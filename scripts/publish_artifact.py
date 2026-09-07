#!/usr/bin/env python3
"""Publish an accepted scoped delivery as an immutable shared V2 artifact."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


from artifact_support import (KINDS, hash_artifact, project_path, reject_links,
                              safe_component, safe_payload_name, validate_provenance,
                              validate_publication_authority)
from governance_schema import load_history


def publish(root: Path, *, kind: str, artifact_id: str, version: str,
            source: str | Path, producer_task: str, producer_employee: str,
            producer_assistant: str, audit_reference: str,
            schema_or_interface: str = "") -> Path:
    root = Path(root).resolve()
    if kind not in KINDS:
        raise ValueError("invalid shared artifact kind")
    safe_component(artifact_id)
    safe_component(version, version=True)
    events, _ = load_history(root)
    source, audit, plan = validate_provenance(root, producer_task=producer_task,
        producer_employee=producer_employee, producer_assistant=producer_assistant,
        audit_reference=audit_reference, source=source, events=events, require_source=True)
    safe_payload_name(source.name)
    validate_publication_authority(root, kind, plan, events)
    destination = project_path(root, Path(kind) / artifact_id / version, must_exist=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    reject_links(destination.parent, root)
    lock = destination.parent / f".{version}.publish.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise ValueError("artifact version has an active publication lock") from exc
    staging = None
    try:
        handle.close()
        if destination.exists():
            raise ValueError("immutable artifact version already exists")
        staging = Path(tempfile.mkdtemp(prefix=f".{version}.", dir=destination.parent))
        payload = staging / source.name
        original_hash = hash_artifact(source)
        audited_hash = audit["employee_delivery_hash"]["value"]
        if original_hash != audited_hash:
            raise ValueError("source changed after accepted audit snapshot validation")
        if source.is_dir():
            shutil.copytree(source, payload, symlinks=True)
        else:
            shutil.copy2(source, payload, follow_symlinks=False)
        reject_links(source, root, recursive=True)
        reject_links(payload, root, recursive=True)
        copied_hash = hash_artifact(payload)
        if copied_hash != audited_hash or original_hash != audited_hash or hash_artifact(source) != audited_hash:
            raise ValueError("source changed while publishing")
        audit_ref = f"{audit['_path']}#{audit['event_id']}"
        manifest = {
            "artifact_id": artifact_id, "name": source.name,
            "artifact_type": kind, "version": version, "status": "published",
            "producer_task": producer_task, "producer_employee": producer_employee,
            "producer_assistant": producer_assistant, "assistant_audit_reference": audit_ref,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_path": source.relative_to(root).as_posix(), "sources": [],
            "content_hash": {"algorithm": "sha256", "mode": "file" if payload.is_file() else "tree-v1", "value": copied_hash},
            "schema_or_interface": schema_or_interface or None,
            "replaces": None, "notes": None,
        }
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        reject_links(destination, root)
        if destination.exists():
            raise ValueError("immutable artifact version already exists")
        staging.rename(destination)
        staging = None
        return destination
    finally:
        if staging is not None and staging.exists():
            # Only remove this invocation's staging directory within the artifact root.
            if staging.parent.resolve() != destination.parent.resolve() or not staging.name.startswith(f".{version}."):
                raise ValueError("refusing to remove unexpected artifact staging path")
            shutil.rmtree(staging)
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--kind", choices=sorted(KINDS), required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--version", required=True, help="exact immutable version, such as v0001")
    parser.add_argument("--source", type=Path, required=True, help="project-relative or contained absolute path")
    parser.add_argument("--producer-task", required=True)
    parser.add_argument("--producer-employee", required=True)
    parser.add_argument("--producer-assistant", required=True)
    parser.add_argument("--audit-reference", required=True)
    parser.add_argument("--schema-or-interface", default="")
    args = parser.parse_args()
    try:
        destination = publish(args.project_root, kind=args.kind, artifact_id=args.artifact_id,
            version=args.version, source=args.source, producer_task=args.producer_task,
            producer_employee=args.producer_employee, producer_assistant=args.producer_assistant,
            audit_reference=args.audit_reference, schema_or_interface=args.schema_or_interface)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"REJECTED: {exc}")
        return 2
    print(f"PUBLISHED {destination.relative_to(args.project_root.resolve()).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
