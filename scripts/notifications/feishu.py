#!/usr/bin/env python3
"""Send a deduplicated Feishu owner-escalation decision package from environment credentials."""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--event", type=Path, required=True, help="JSON with owner_intervention_required=true")
    args = parser.parse_args()
    event = json.loads(args.event.read_text(encoding="utf-8"))
    if not event.get("owner_intervention_required"):
        print("SKIP: owner intervention is not required")
        return 0
    root = args.project_root.resolve()
    state_path = root / "root" / "notifications" / ".feishu_notifications.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    event_id = event.get("event_id") or f"{event.get('record_type')}:{event.get('task_code')}"
    if state.get(event_id) == "sent" and not event.get("material_update"):
        print("SKIP: duplicate unresolved escalation")
        return 0
    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook:
        print("WARNING: FEISHU_WEBHOOK_URL is not configured; notification not sent")
        return 0
    fields = [
        ("项目", event.get("project", "")), ("阶段", event.get("stage", "")), ("任务", event.get("task_code", "")),
        ("状态", event.get("status", "paused")), ("问题", event.get("question", event.get("event_description", ""))),
        ("影响", event.get("impact", "")), ("可选方案", event.get("options", "尚无法形成可靠备选，需要负责人提供外部信息。")),
        ("推荐方案", event.get("recommendation", "")), ("记录", event.get("record_reference", "")),
    ]
    content = "【Multi-Agent Project · Owner Action Required】\n\n" + "\n\n".join(f"{key}：\n{value}" for key, value in fields) + "\n\n请进入项目对话处理。"
    body = json.dumps({"msg_type": "text", "content": {"text": content}}, ensure_ascii=False).encode("utf-8")
    try:
        request = urllib.request.Request(webhook, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError(f"HTTP {response.status}")
    except Exception as exc:
        print(f"WARNING: Feishu notification failed; owner must be told in-project: {exc}")
        return 0
    state[event_id] = "sent"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SENT event_id={event_id} at {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
