#!/usr/bin/env python3
"""Create missing project-governance scaffolding without overwriting files."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from governance_schema import IDENTIFIER, contained_path, read_project_config


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"
IGNORE_RULES = (
    "root/notifications/feishu_config.json",
    "root/notifications/.feishu_notifications.json",
    "root/notifications/.feishu_notifications.tmp",
    "root/notifications/.feishu_notifications.lock",
)


def copy_missing(source: Path, destination: Path, created: list[Path], skipped: list[Path], root: Path) -> None:
    contained_path(root, destination.relative_to(root).as_posix())
    if source.is_symlink() or destination.is_symlink():
        raise ValueError("scaffold symlinks are not supported")
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            copy_missing(child, destination / child.name, created, skipped, root)
        return
    if destination.exists():
        skipped.append(destination)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    created.append(destination)


def append_ignore_rules(root: Path) -> bool:
    """Startup scaffold exception: append only missing fixed rules, preserve every byte."""
    path = contained_path(root, ".gitignore")
    original = path.read_bytes() if path.exists() else b""
    existing = {line.strip() for line in original.decode("utf-8-sig").splitlines()}
    missing = [rule for rule in IGNORE_RULES if rule not in existing]
    if not missing:
        return False
    suffix = (b"\n" if original and not original.endswith(b"\n") else b"")
    suffix += b"\n# Local notification settings, legacy credentials and runtime state\n"
    suffix += ("\n".join(missing) + "\n").encode("utf-8")
    with path.open("ab") as handle:
        handle.write(suffix)
    return True


def _startup_check(root: Path, enabled: bool) -> None:
    if not enabled:
        print("FEISHU: disabled by persisted owner configuration")
        return
    adapter = contained_path(root, "root/notifications/feishu.py", must_exist=True)
    source = SKILL_ROOT / "scripts" / "notifications" / "feishu.py"
    if adapter.read_bytes() != source.read_bytes():
        print("FEISHU: preserved adapter needs migration review; startup check not run")
        return
    try:
        result = subprocess.run(
            [sys.executable, "-B", str(adapter), str(root), "--startup"],
            check=False, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=20, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        parsed = None
        for line in result.stdout.splitlines():
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and candidate.get("notification_status") in {"sent", "skipped", "failed"}:
                    parsed = candidate
                    break
            except json.JSONDecodeError:
                continue
        if result.returncode == 0 and parsed and parsed["notification_status"] == "sent":
            print("FEISHU: sent; startup connectivity confirmed by Feishu business response")
        elif result.returncode == 0 and parsed and parsed["notification_status"] == "skipped" and not parsed.get("owner_dialogue_fallback"):
            print("FEISHU: skipped; no new startup connectivity check was performed")
        else:
            print("FEISHU: not connected; monitor must report in-project and guide configuration or disablement")
    except (OSError, subprocess.TimeoutExpired):
        print("FEISHU: startup check unavailable; monitor must report in-project and guide configuration or disablement")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="existing project root")
    parser.add_argument("--prefix", help="owner-confirmed global task-code project identifier, e.g. QSV5 or TLTK")
    parser.add_argument("--feishu-notifications", choices=("enabled", "disabled"), default=None,
                        help="owner choice; defaults enabled for new projects, preserves existing choice otherwise")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    if not root.exists() or not root.is_dir():
        parser.error("project_root must be an existing directory")
    if args.prefix and not re.fullmatch(IDENTIFIER, args.prefix):
        parser.error("--prefix must start with an ASCII letter, followed by letters, digits or underscores")

    created: list[Path] = []
    skipped: list[Path] = []
    for name in (
        "ai_workspace", "assistant_workspace", "work_logs", "draft", "plan/interfaces",
        "project_demo", "project_final", "raw_data", "common_data", "common_artifacts",
    ):
        target = contained_path(root, name)
        if not target.exists():
            target.mkdir(parents=True)
            created.append(target)
    copy_missing(TEMPLATES / "AGENTS.md", root / "AGENTS.md", created, skipped, root)
    copy_missing(TEMPLATES / "rules", root / "rules", created, skipped, root)
    copy_missing(TEMPLATES / "root", root / "root", created, skipped, root)
    for relative in (
        Path("validate_project_governance.py"), Path("record_engine.py"),
        Path("publish_artifact.py"), Path("notifications") / "feishu.py",
        Path("governance_schema.py"), Path("artifact_support.py"),
    ):
        copy_missing(SKILL_ROOT / "scripts" / relative, root / "root" / relative, created, skipped, root)
    if append_ignore_rules(root):
        print("APPEND .gitignore fixed notification rules (existing bytes preserved)")

    core_rule = root / "rules" / "00-core-governance.md"
    if core_rule in created:
        content = core_rule.read_text(encoding="utf-8")
        if args.prefix:
            content = content.replace("<SET_BY_OWNER>", args.prefix)
        if args.feishu_notifications == "disabled":
            content = re.sub(r"(notifications:\s*\{\s*enabled:\s*)true", r"\g<1>false", content)
        core_rule.write_text(content, encoding="utf-8")
    elif args.feishu_notifications is not None:
        enabled = args.feishu_notifications == "enabled"
        if read_project_config(root).get("notifications_enabled", True) != enabled:
            original = core_rule.read_bytes()
            with core_rule.open("ab") as handle:
                if original and not original.endswith(b"\n"):
                    handle.write(b"\n")
                handle.write(f"\n- notifications-enabled: {str(enabled).lower()}\n".encode("utf-8"))
            print("APPEND owner-confirmed notifications override (existing governance bytes preserved)")
    _startup_check(root, read_project_config(root).get("notifications_enabled", True))
    print(f"project_root={root}")
    print(f"created_or_initialized={len(created)}")
    for path in created:
        print(f"CREATE {path.relative_to(root)}")
    print(f"preserved_existing={len(skipped)}")
    for path in skipped:
        print(f"PRESERVE {path.relative_to(root)}")
    if skipped:
        print("MIGRATION_WARNING existing governance content was preserved; review V2 rules before enabling V2 autonomy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
