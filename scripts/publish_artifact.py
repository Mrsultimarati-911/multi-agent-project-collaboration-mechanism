#!/usr/bin/env python3
"""Publish an audited file or directory as an immutable shared V2 artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        paths = [path]
        root = path.parent
    else:
        paths = sorted(item for item in path.rglob("*") if item.is_file())
        root = path
    for item in paths:
        digest.update(item.relative_to(root).as_posix().encode())
        with item.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--kind", choices=("common_data", "common_artifacts"), required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--version", required=True, help="immutable version such as v0001")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--producer-task", required=True)
    parser.add_argument("--producer-employee", required=True)
    parser.add_argument("--producer-assistant", required=True)
    parser.add_argument("--audit-reference", required=True)
    parser.add_argument("--schema-or-interface", default="")
    args = parser.parse_args()
    root, source = args.project_root.resolve(), args.source.resolve()
    if not source.exists():
        parser.error(f"source does not exist: {source}")
    if not args.version.startswith("v"):
        parser.error("--version must begin with v, for example v0001")
    destination = root / args.kind / args.artifact_id / args.version
    if destination.exists():
        parser.error(f"immutable version already exists: {destination}")
    destination.mkdir(parents=True)
    payload = destination / source.name
    if source.is_dir():
        shutil.copytree(source, payload)
    else:
        shutil.copy2(source, payload)
    manifest = {
        "artifact_id": args.artifact_id, "name": source.name,
        "artifact_type": args.kind, "version": args.version, "status": "published",
        "producer_task": args.producer_task, "producer_employee": args.producer_employee,
        "producer_assistant": args.producer_assistant,
        "assistant_audit_reference": args.audit_reference,
        "created_at": datetime.now(timezone.utc).isoformat(), "sources": [],
        "content_hash": {"algorithm": "sha256", "value": sha256(payload)},
        "schema_or_interface": args.schema_or_interface or None, "replaces": None, "notes": None,
    }
    (destination / "manifest.yaml").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PUBLISHED {destination.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
