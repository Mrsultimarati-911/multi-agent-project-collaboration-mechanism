#!/usr/bin/env python3
"""Create missing project-governance scaffolding without overwriting files."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"


def copy_missing(source: Path, destination: Path, created: list[Path], skipped: list[Path]) -> None:
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            copy_missing(child, destination / child.name, created, skipped)
        return
    if destination.exists():
        skipped.append(destination)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    created.append(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="existing project root")
    parser.add_argument("--prefix", help="owner-confirmed global task-code project identifier, e.g. QSV5 or TLTK")
    parser.add_argument("--feishu-notifications", choices=("enabled", "disabled"), default="enabled")
    args = parser.parse_args()
    root = args.project_root.resolve()
    if not root.exists() or not root.is_dir():
        parser.error("project_root must be an existing directory")
    if args.prefix and not args.prefix.replace("_", "").isalnum():
        parser.error("--prefix may contain only letters, digits, and underscores")

    created: list[Path] = []
    skipped: list[Path] = []
    for name in (
        "ai_workspace", "assistant_workspace", "work_logs", "draft", "plan/interfaces",
        "project_demo", "project_final", "raw_data", "common_data", "common_artifacts",
    ):
        target = root / name
        if not target.exists():
            target.mkdir(parents=True)
            created.append(target)
    copy_missing(TEMPLATES / "AGENTS.md", root / "AGENTS.md", created, skipped)
    copy_missing(TEMPLATES / "rules", root / "rules", created, skipped)
    copy_missing(TEMPLATES / "root", root / "root", created, skipped)
    for relative in (
        Path("validate_project_governance.py"), Path("record_engine.py"),
        Path("publish_artifact.py"), Path("notifications") / "feishu.py",
    ):
        copy_missing(SKILL_ROOT / "scripts" / relative, root / "root" / relative, created, skipped)
    gitignore = root / ".gitignore"
    ignored = "root/notifications/feishu_config.json\nroot/notifications/.feishu_notifications.json\n"
    old_ignore = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if "root/notifications/feishu_config.json" not in old_ignore:
        gitignore.write_text(old_ignore.rstrip() + "\n\n# Local Feishu credentials and notification state\n" + ignored, encoding="utf-8")
        created.append(gitignore) if not old_ignore else skipped.append(gitignore)

    core_rule = root / "rules" / "00-core-governance.md"
    if args.prefix and core_rule in created and "<SET_BY_OWNER>" in core_rule.read_text(encoding="utf-8"):
        core_rule.write_text(
            core_rule.read_text(encoding="utf-8").replace("<SET_BY_OWNER>", args.prefix),
            encoding="utf-8",
        )
    if args.feishu_notifications == "disabled":
        print("FEISHU: disabled by monitor/owner initialization choice")
    elif (root / "root" / "notifications" / "feishu_config.json").is_file():
        result = subprocess.run([sys.executable, str(root / "root" / "notifications" / "feishu.py"), str(root), "--startup"], check=False)
        print(f"FEISHU_STARTUP_CHECK_EXIT={result.returncode}")
    else:
        print("FEISHU: config missing; monitor must report not connected and offer configuration or disablement")
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
