"""Shared artifact paths, hashes and accepted-delivery provenance (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from governance_schema import contained_path, load_history, ref_event, replay_history, require_evidence

KINDS = frozenset({"common_data", "common_artifacts"})
ARTIFACT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VERSION = re.compile(r"^v\d{4,}$")
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe_component(value: object, *, version: bool = False) -> str:
    pattern = VERSION if version else ARTIFACT_ID
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError("invalid artifact version" if version else "invalid artifact identifier/name")
    if value.endswith(".") or value.split(".")[0].upper() in RESERVED_NAMES:
        raise ValueError("unsafe artifact path component")
    return value


def safe_payload_name(value: object) -> str:
    """Keep human/Unicode filenames while rejecting path components and manifests."""
    if not isinstance(value, str) or not value or value in {".", ".."}:
        raise ValueError("invalid artifact payload name")
    if any(c in value for c in '/\\:<>"|?*') or any(ord(c) < 32 for c in value):
        raise ValueError("unsafe artifact payload name")
    if value.endswith((".", " ")) or value.split(".")[0].upper() in RESERVED_NAMES:
        raise ValueError("unsafe artifact payload name")
    if value.lower() in {"manifest.json", "manifest.yaml"}:
        raise ValueError("artifact payload name conflicts with manifest")
    return value


def reject_links(path: Path, root: Path, *, recursive: bool = False) -> None:
    """Reject symlinks/junctions, including parents, before following content."""
    path, root = Path(path).absolute(), Path(root).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path escapes project root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise ValueError("symlink or junction is not allowed in artifact paths")
    if recursive and path.is_dir():
        for child in path.iterdir():
            reject_links(child, root, recursive=True)


def project_path(root: Path, value: str | Path, *, must_exist: bool = True) -> Path:
    root, candidate = Path(root).resolve(), Path(value)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("source escapes project root") from exc
    reject_links(root / candidate, root)
    return contained_path(root, candidate.as_posix(), must_exist=must_exist)


def hash_artifact(path: Path) -> str:
    """File SHA-256; directories use a deterministic framed tree-v1 digest."""
    path = Path(path)
    reject_links(path, path.parent, recursive=True)
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    elif path.is_dir():
        digest.update(b"macm-tree-v1\0")
        for child in sorted(path.rglob("*"), key=lambda p: p.relative_to(path).as_posix()):
            name = child.relative_to(path).as_posix().encode("utf-8")
            digest.update(b"D" if child.is_dir() else b"F")
            digest.update(len(name).to_bytes(8, "big"))
            digest.update(name)
            if child.is_file():
                digest.update(child.stat().st_size.to_bytes(8, "big"))
                with child.open("rb") as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(block)
            elif not child.is_dir():
                raise ValueError("unsupported special file in artifact")
    else:
        raise ValueError("artifact content must be a regular file or directory")
    return digest.hexdigest()


def _legacy_hash(path: Path) -> str:
    """Read-only compatibility with the first V2 publisher's JSON manifest.yaml."""
    reject_links(path, path.parent, recursive=True)
    digest = hashlib.sha256()
    paths, base = ([path], path.parent) if path.is_file() else (sorted(p for p in path.rglob("*") if p.is_file()), path)
    for child in paths:
        digest.update(child.relative_to(base).as_posix().encode())
        with child.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def _within(path: Path, scope: Path) -> bool:
    return path == scope or scope in path.parents


def validate_provenance(root: Path, *, producer_task: str, producer_employee: str,
                        producer_assistant: str, audit_reference: str,
                        source: str | Path | None, events: list[dict] | None = None,
                        require_source: bool = False) -> tuple[Path, dict, dict]:
    """Require a real, accepted audit for this task and its delivery scope."""
    root = Path(root).resolve()
    if events is None:
        events, _ = load_history(root)
    # A valid content hash chain does not by itself prove legal governance transitions.
    # Suppress artifact recursion while replaying structural authority/state semantics.
    replay_history(root, events, check_artifacts=False)
    audit = ref_event(events, audit_reference, kinds={"level2_results_mid", "level2_results"}, task_code=producer_task)
    if audit.get("record_type") == "level2_results":
        if audit.get("execution_status") not in {"accepted", "integrated", "closed"}:
            raise ValueError("artifact result is not accepted")
        audit = ref_event(events, audit.get("assistant_audit_reference", ""), kinds={"level2_results_mid"}, task_code=producer_task)
    if audit.get("execution_status") != "audited" or audit.get("assistant_audit_status") != "accepted":
        raise ValueError("artifact requires an accepted assistant audit")
    if require_source:
        task_events = [e for e in events if e.get("task_code") == producer_task]
        if not task_events or task_events[-1].get("execution_status") not in {"audited", "accepted", "integrated", "closed"}:
            raise ValueError("producer task is no longer in an accepted publishable state")
        audits = [e for e in task_events if e.get("record_type") == "level2_results_mid" and e.get("execution_status") == "audited"]
        if not audits or audits[-1].get("event_id") != audit.get("event_id"):
            raise ValueError("artifact publication requires the latest accepted audit")
    plan = ref_event(events, audit.get("level2_plan_reference", ""), kinds={"level2_plan"}, task_code=producer_task)
    if plan.get("responsible_employee") != producer_employee or plan.get("responsible_assistant") != producer_assistant:
        raise ValueError("artifact producer does not match the approved task plan")
    if audit.get("responsible_assistant", producer_assistant) != producer_assistant:
        raise ValueError("artifact audit assistant does not match producer assistant")
    if not audit.get("employee_delivery_reference"):
        raise ValueError("accepted audit has no scoped employee delivery")
    delivery = project_path(root, audit["employee_delivery_reference"], must_exist=require_source)
    source_path = project_path(root, source if source is not None else delivery, must_exist=require_source)
    if source_path != delivery:
        raise ValueError("source must exactly match the accepted audit delivery scope")
    scopes = [plan.get("workspace", ""), *plan.get("allowed_reads", []), *plan.get("allowed_writes", [])]
    allowed_roots = {"ai_workspace", "assistant_workspace", "common_data", "common_artifacts", "project_demo"}
    authorized = False
    for scope in scopes:
        if not isinstance(scope, str) or not scope or any(token in scope for token in ("*", "?", "[")):
            continue
        scope_path = project_path(root, scope, must_exist=False)
        parts = scope_path.relative_to(root).parts
        if parts and parts[0] in allowed_roots and _within(source_path, scope_path):
            authorized = True
            break
    if not authorized:
        raise ValueError("source is outside the approved task workspace/artifact scope")
    reject_links(source_path, root, recursive=require_source)
    audit_hash = audit.get("employee_delivery_hash")
    if not isinstance(audit_hash, dict) or audit_hash.get("algorithm") != "sha256" or audit_hash.get("mode") not in {"file", "tree-v1"} or not re.fullmatch(r"[0-9a-f]{64}", str(audit_hash.get("value", ""))):
        raise ValueError("accepted audit is missing its validated delivery hash snapshot")
    if require_source and (hash_artifact(source_path) != audit_hash["value"] or audit_hash["mode"] != ("file" if source_path.is_file() else "tree-v1")):
        raise ValueError("source no longer matches the accepted audit hash snapshot")
    return source_path, audit, plan


def validate_publication_authority(root: Path, kind: str, plan: dict, events: list[dict]) -> None:
    """Dispatch approval alone does not grant shared-layer publication authority."""
    stage = ref_event(events, plan["level1_plan_reference"], kinds={"level1_plan"})
    if stage.get("authority_envelope", {}).get("publish_permissions", {}).get(kind) is True:
        return
    evidence = plan.get("owner_publication_approval_evidence")
    if not evidence:
        raise ValueError("publication exceeds the approved Authority Envelope and lacks owner publication approval")
    require_evidence(root, evidence)


def validate_manifest(root: Path, manifest_path: str | Path, events: list[dict] | None = None) -> dict:
    root = Path(root).resolve()
    if events is None:
        events, _ = load_history(root)
    manifest_path = project_path(root, manifest_path)
    relative = manifest_path.relative_to(root)
    if len(relative.parts) != 4 or relative.parts[0] not in KINDS or relative.name not in {"manifest.json", "manifest.yaml"}:
        raise ValueError("manifest must be in a versioned shared artifact directory")
    kind, artifact_id, version, _ = relative.parts
    safe_component(artifact_id)
    safe_component(version, version=True)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("artifact manifest must contain JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("artifact manifest must be an object")
    required = {"artifact_id", "name", "artifact_type", "version", "status", "producer_task", "producer_employee", "producer_assistant", "assistant_audit_reference", "created_at", "content_hash"}
    if any(not manifest.get(field) for field in required):
        raise ValueError("artifact manifest is missing required provenance fields")
    if (manifest["artifact_type"], manifest["artifact_id"], manifest["version"]) != (kind, artifact_id, version):
        raise ValueError("manifest identity does not match artifact directory")
    if manifest["status"] != "published":
        raise ValueError("artifact is not published")
    name = safe_payload_name(manifest["name"])
    payload = project_path(root, manifest_path.parent / name)
    reject_links(payload, root, recursive=True)
    if any(p.name not in {name, "manifest.json", "manifest.yaml"} for p in manifest_path.parent.iterdir()):
        raise ValueError("artifact version contains unmanifested content")
    content_hash = manifest["content_hash"]
    if not isinstance(content_hash, dict) or content_hash.get("algorithm") != "sha256":
        raise ValueError("unsupported artifact hash algorithm")
    mode = content_hash.get("mode")
    if mode is None and manifest_path.name == "manifest.yaml":
        actual = _legacy_hash(payload)
    else:
        if mode != ("file" if payload.is_file() else "tree-v1"):
            raise ValueError("artifact hash mode does not match payload")
        actual = hash_artifact(payload)
    if not isinstance(content_hash.get("value"), str) or content_hash["value"] != actual:
        raise ValueError("artifact SHA-256 mismatch")
    if manifest_path.name == "manifest.json" and not manifest.get("source_path"):
        raise ValueError("artifact manifest is missing source_path")
    source, audit, plan = validate_provenance(root, producer_task=manifest["producer_task"],
        producer_employee=manifest["producer_employee"], producer_assistant=manifest["producer_assistant"],
        audit_reference=manifest["assistant_audit_reference"], source=manifest.get("source_path"), events=events)
    validate_publication_authority(root, kind, plan, events)
    if source.name != name:
        raise ValueError("manifest content name does not match accepted source")
    if hash_artifact(payload) != audit["employee_delivery_hash"]["value"] or audit["employee_delivery_hash"]["mode"] != ("file" if payload.is_file() else "tree-v1"):
        raise ValueError("published payload does not match the accepted audit hash snapshot")
    return manifest


def validate_artifact_reference(root: Path, ref: dict, events: list[dict] | None = None) -> dict:
    if not isinstance(ref, dict) or ref.get("kind") not in KINDS:
        raise ValueError("artifact reference requires common_data/common_artifacts kind")
    artifact_id = safe_component(ref.get("artifact_id"))
    version = safe_component(ref.get("version"), version=True)
    directory = project_path(root, Path(ref["kind"]) / artifact_id / version)
    manifest = directory / "manifest.json"
    if not manifest.exists():
        manifest = directory / "manifest.yaml"
    return validate_manifest(root, manifest, events=events)
