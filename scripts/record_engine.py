#!/usr/bin/env python3
"""Deterministically validate and append a V2 governance event to work_logs/."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TASK_CODE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*_\d{2}-\d{2}-\d{3}-\d{4}$")
TRANSITIONS = {
    "planned": {"dispatched", "cancelled"}, "dispatched": {"running", "paused", "cancelled"},
    "running": {"submitted", "paused", "failed"}, "submitted": {"audited", "running", "failed"},
    "audited": {"accepted", "running", "failed"}, "accepted": {"integrated", "closed"},
    "paused": {"running", "cancelled"}, "failed": {"running", "cancelled"},
}
REQUIRED = ("record_type", "task_code", "task_name", "responsible_role", "status", "event_description")


def fail(message: str) -> None:
    raise ValueError(message)


def validate(root: Path, event: dict) -> None:
    for field in REQUIRED:
        if not event.get(field):
            fail(f"missing required event field: {field}")
    if not TASK_CODE.fullmatch(str(event["task_code"])) and event["record_type"] != "level1_plan":
        fail("invalid concrete task_code")
    previous = event.get("previous_status")
    if previous and event["status"] not in TRANSITIONS.get(previous, set()):
        fail(f"illegal state transition: {previous} -> {event['status']}")
    for artifact in event.get("artifact_references", []):
        target = root / artifact["kind"] / artifact["artifact_id"] / artifact["version"] / "manifest.yaml"
        if not target.is_file():
            fail(f"missing artifact manifest: {target.relative_to(root)}")
    for dependency in event.get("depends_on", []):
        if not any(root.joinpath("work_logs").glob(f"*_{dependency}.md")):
            fail(f"missing dependency record for {dependency}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--event", type=Path, required=True, help="JSON event payload")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    event = json.loads(args.event.read_text(encoding="utf-8"))
    try:
        validate(root, event)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"REJECTED: {exc}")
        return 2
    timestamp = datetime.now(timezone.utc).isoformat()
    event.setdefault("event_date", timestamp[:10])
    event.setdefault("created_at", timestamp)
    filename = f"{event['record_type']}_{event['task_code']}.md"
    destination = root / "work_logs" / filename
    if destination.exists() and event["record_type"] != "level2_results_mid":
        print(f"REJECTED: append-only record already exists: work_logs/{filename}")
        return 2
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in event.items()) + "\n---\n\n"
    document += f"# {event['record_type']}｜{event['task_name']}\n\n{event['event_description']}\n"
    if args.dry_run:
        print(f"VALID {filename}")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if destination.exists() else "x"
    with destination.open(mode, encoding="utf-8") as handle:
        if mode == "a":
            handle.write("\n---\n\n")
        handle.write(document)
    print(f"RECORDED work_logs/{filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
