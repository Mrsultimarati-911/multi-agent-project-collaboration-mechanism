#!/usr/bin/env python3
"""Feishu notification-only adapter. Credentials are environment-only; output is redacted."""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governance_schema import contained_path, read_project_config

EVENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:#-]{0,199}$")
STATES = {"pending", "sent", "failed", "resolved"}


def generate_signature(timestamp: str, secret: str) -> str:
    """Official custom-bot HMAC: key timestamp + newline + secret, empty message.

    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    """
    key = f"{timestamp}\n{secret}".encode("utf-8")
    return base64.b64encode(hmac.new(key, b"", hashlib.sha256).digest()).decode("ascii")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _post(webhook: str, payload: dict) -> bool:
    request = urllib.request.Request(
        webhook, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST",
    )
    with urllib.request.build_opener(_NoRedirect()).open(request, timeout=10) as response:
        if not 200 <= response.status < 300:
            return False
        body = json.loads(response.read(65537).decode("utf-8"))
    if not isinstance(body, dict):
        return False
    codes = [body[key] for key in ("code", "StatusCode") if key in body]
    return bool(codes) and all(type(code) is int and code == 0 for code in codes)


def _result(status: str, reason: str, *, fallback: bool = False) -> dict:
    result = {"notification_status": status, "reason": reason, "owner_dialogue_fallback": fallback}
    print(json.dumps(result, ensure_ascii=False))
    if fallback:
        print("WARNING: 飞书通知未确认送达；请在当前项目负责人对话报告，并指导配置或关闭通知。")
    return result


def _runtime_path(root: Path, filename: str) -> Path:
    directory = contained_path(root, "root/notifications")
    directory.mkdir(parents=True, exist_ok=True)
    path = contained_path(root, f"root/notifications/{filename}")
    if (directory / filename).is_symlink():
        raise ValueError("notification runtime symlink rejected")
    return path


def _read_state(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("invalid notification state")
    state = {}
    for key, value in raw.items():
        if isinstance(value, str) and value in STATES:
            state[hashlib.sha256(key.encode("utf-8")).hexdigest()] = {"status": value, "attempts": 1}
        elif (re.fullmatch(r"[a-f0-9]{64}", key) and isinstance(value, dict)
              and value.get("status") in STATES and type(value.get("attempts")) is int):
            state[key] = {"status": value["status"], "attempts": value["attempts"]}
        else:
            raise ValueError("invalid notification state")
    return state


def _save_state(root: Path, path: Path, state: dict) -> None:
    temp = _runtime_path(root, ".feishu_notifications.tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def _payload(root: Path, event: dict, startup: bool, config: dict) -> dict:
    if startup:
        identifiers = config.get("identifiers") or []
        project = config.get("current_identifier") or (identifiers[-1] if isinstance(identifiers, list) and identifiers else root.name)
        text = f"【Multi-Agent Project】\n\n{project}_项目已启动飞书监控。"
    else:
        fields = (
            ("项目", event.get("project", root.name)), ("阶段", event.get("stage", "")),
            ("任务", event.get("task_code", "")), ("状态", event.get("requested_status", event.get("status", "paused"))),
            ("问题", event.get("question", event.get("event_description", ""))),
            ("影响", event.get("impact", "")), ("可选方案", event.get("options", "需要负责人提供外部信息。")),
            ("推荐方案", event.get("recommendation", "")), ("记录", event.get("record_reference", "")),
        )
        text = "【Multi-Agent Project · Owner Action Required】\n\n" + "\n\n".join(f"{key}：\n{value}" for key, value in fields)
        text += "\n\n请进入项目对话处理；此通知不能作为审批。"
    for key in ("FEISHU_WEBHOOK_URL", "FEISHU_WEBHOOK_SECRET"):
        value = os.environ.get(key)
        if value:
            text = text.replace(value, "[REDACTED]")
    return {"msg_type": "text", "content": {"text": text}}


def notify(project_root: Path, event: dict | None = None, *, startup: bool = False,
           resolve_event_id: str | None = None) -> dict:
    """Send once per event; explicit material updates may retry unresolved events.

    No raw response, exception, credential or payload is printed or persisted.
    """
    root = Path(project_root).resolve()
    event = event or {}
    if not isinstance(event, dict):
        return _result("failed", "invalid_event", fallback=True)
    if not startup and resolve_event_id is None and event.get("owner_intervention_required") is not True:
        return _result("skipped", "owner_intervention_not_required")
    event_id = resolve_event_id or ("project-startup" if startup else event.get("event_id"))
    if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
        return _result("failed", "invalid_event_id", fallback=True)
    if "material_update" in event and type(event["material_update"]) is not bool:
        return _result("failed", "invalid_material_update", fallback=True)
    lock = None
    locked = False
    try:
        config = read_project_config(root)
        if resolve_event_id is None:
            if not config.get("notifications_enabled", True):
                return _result("skipped", "disabled")
            optional = contained_path(root, "root/notifications/feishu_config.json")
            if optional.exists():
                settings = json.loads(optional.read_text(encoding="utf-8"))
                if not isinstance(settings, dict) or set(settings) - {"enabled"}:
                    return _result("failed", "legacy_or_invalid_config_use_environment", fallback=True)
                if type(settings.get("enabled", True)) is not bool:
                    return _result("failed", "invalid_enabled_setting", fallback=True)
                if not settings.get("enabled", True):
                    return _result("skipped", "disabled")
        state_path = _runtime_path(root, ".feishu_notifications.json")
        lock = _runtime_path(root, ".feishu_notifications.lock")
        try:
            with lock.open("x", encoding="utf-8"):
                pass
            locked = True
        except FileExistsError:
            return _result("failed", "state_busy_or_recovery_required", fallback=True)
        state = _read_state(state_path)
        key = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
        existing = state.get(key)
        if resolve_event_id is not None:
            if existing is None:
                return _result("failed", "unknown_event", fallback=True)
            state[key]["status"] = "resolved"
            _save_state(root, state_path, state)
            return _result("resolved", "resolved_in_project")
        if existing:
            if existing["status"] == "resolved":
                return _result("skipped", "resolved_event_requires_new_id")
            if not event.get("material_update", False):
                return _result("skipped", "duplicate_unresolved_event", fallback=existing["status"] in {"failed", "pending"})
        state[key] = {"status": "pending", "attempts": (existing or {}).get("attempts", 0) + 1}
        _save_state(root, state_path, state)
        webhook = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
        try:
            parts = urlsplit(webhook)
            valid_url = (parts.scheme == "https" and parts.hostname in {"open.feishu.cn", "open.larksuite.com"}
                         and parts.username is None and parts.password is None and parts.port in {None, 443}
                         and parts.path.startswith("/open-apis/bot/v2/hook/") and not parts.query and not parts.fragment)
        except ValueError:
            valid_url = False
        sent = False
        reason = "missing_environment" if not webhook else "invalid_webhook_environment"
        if valid_url:
            payload = _payload(root, event, startup, config)
            secret = os.environ.get("FEISHU_WEBHOOK_SECRET", "")
            if secret:
                timestamp = str(int(time.time()))
                payload.update(timestamp=timestamp, sign=generate_signature(timestamp, secret))
            try:
                sent = _post(webhook, payload)
                reason = "business_success" if sent else "http_or_business_failure"
            except Exception:
                reason = "transport_or_response_failure"
        state[key]["status"] = "sent" if sent else "failed"
        _save_state(root, state_path, state)
        return _result("sent" if sent else "failed", reason, fallback=not sent)
    except Exception:
        return _result("failed", "configuration_or_state_failure", fallback=True)
    finally:
        if locked and lock is not None:
            try:
                lock.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event", help="project-relative governance event JSON")
    group.add_argument("--startup", action="store_true")
    group.add_argument("--resolve", metavar="EVENT_ID", help="mark resolved after an in-project owner decision")
    parser.add_argument("--material-update", action="store_true", help="retry after a material event/configuration change")
    args = parser.parse_args(argv)
    event = None
    if args.event:
        try:
            event = json.loads(contained_path(args.project_root, args.event, must_exist=True).read_text(encoding="utf-8"))
        except Exception:
            _result("failed", "invalid_event_file", fallback=True)
            return 1
    if args.material_update:
        event = {**(event or {}), "material_update": True}
    result = notify(args.project_root, event, startup=args.startup, resolve_event_id=args.resolve)
    return 1 if result["notification_status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
