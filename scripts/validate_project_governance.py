#!/usr/bin/env python3
"""Read-only structural validator for a governed multi-agent project."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_DIRS = ("root", "rules", "ai_workspace", "work_logs", "draft", "plan", "project_demo", "project_final", "raw_data")
TASK_CODE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*_\d{2}-\d{2}-\d{3}-\d{4}$")
LEVEL1_PLAN_CODE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*_\d{2}-##-###-####$")
LEVEL1_ASSISTANT_CODE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*_\d{2}-\d{2}-###-####$")
LOG_NAME = re.compile(r"^(level[12]_(?:results_mid|results|plan|summary|warning|error))_(.+)\.md$")
REQUIRED_LOG_FIELDS = ("record_type:", "task_code:", "task_name:", "responsible_role:", "event_date:", "status:")
REQUIRED_TASK_FIELDS = ("task_code:", "task_name:", "dispatch_status:", "responsible_employee:", "allowed_reads:", "allowed_writes:")
REQUIRED_LEVEL1_PLAN_FIELDS = (
    "project_identifier:", "accountable_assistant:", "owner_approval_date:",
    "owner_approval_evidence:", "plan_status:", "frozen_at:", "frozen_by:",
)
REQUIRED_LEVEL2_PLAN_FIELDS = (
    "responsible_assistant:", "responsible_employee:", "level1_plan_reference:",
    "owner_dispatch_approval_date:", "owner_dispatch_approval_evidence:",
    "employee_model:", "employee_reasoning:", "workspace:", "plan_status:",
)
REQUIRED_FIELDS_BY_RECORD_TYPE = {
    "level2_results_mid": ("level2_plan_reference:", "attempt_number:", "submission_timestamp:", "employee_delivery_reference:", "assistant_audit_status:"),
    "level2_results": ("level2_plan_reference:", "level2_results_mid_reference:", "assistant_audit_reference:", "assistant_audit_status:", "final_completion_timestamp:"),
    "level2_summary": ("assistant_audit_reference:", "level2_results_reference:"),
    "level2_warning": ("level2_plan_reference:", "interruption_detected_at:", "recovery_owner:", "recovery_plan:", "resumption_condition:"),
    "level2_error": ("level2_plan_reference:", "interruption_detected_at:", "direct_error_evidence:", "owner_intervention_required:", "paused_scope:"),
    "level1_warning": ("level1_plan_reference:", "interruption_detected_at:", "recovery_owner:", "recovery_plan:", "affected_scope:"),
    "level1_error": ("level1_plan_reference:", "interruption_detected_at:", "direct_error_evidence:", "owner_decision_required:", "all_paused_employees:"),
    "level1_summary": ("level1_plan_reference:", "participating_assistant:", "completion_assessment:", "audit_evidence:", "exception_references:"),
    "level1_results": ("level1_plan_reference:", "source_level1_summaries:", "source_level2_results:", "owner_acceptance_reference:", "reusable_outputs:"),
}


def text_has_all(path: Path, fields: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return [field for field in fields if field not in text]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not (root / "AGENTS.md").is_file():
        errors.append("missing AGENTS.md")
    for directory in REQUIRED_DIRS:
        if not (root / directory).is_dir():
            errors.append(f"missing directory: {directory}/")
    for filename in ("00-core-governance.md", "01-role-and-filesystem.md", "02-work-log-governance.md"):
        if not (root / "rules" / filename).is_file():
            errors.append(f"missing rule: rules/{filename}")

    project_identifier = None
    core_rule = root / "rules" / "00-core-governance.md"
    if core_rule.is_file():
        match = re.search(r"^\s*-\s*project-code-prefix:\s*`?([^`\s]+)`?\s*$", core_rule.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
        if match and "<" not in match.group(1):
            project_identifier = match.group(1)

    logs = root / "work_logs"
    if logs.is_dir():
        for path in sorted(logs.glob("*.md")):
            match = LOG_NAME.match(path.name)
            if not match:
                warnings.append(f"unrecognized log filename: work_logs/{path.name}")
                continue
            kind, code = match.groups()
            if kind.startswith("level2") and not TASK_CODE.fullmatch(code):
                errors.append(f"invalid level2 task code in {path.name}")
            elif kind.startswith("level2") and project_identifier and not code.startswith(f"{project_identifier}_"):
                errors.append(f"project identifier mismatch in {path.name}: expected {project_identifier}_")
            if kind == "level1_plan":
                if not LEVEL1_PLAN_CODE.fullmatch(code):
                    errors.append(f"invalid level1 aggregate task code in {path.name}")
                elif project_identifier and not code.startswith(f"{project_identifier}_"):
                    errors.append(f"project identifier mismatch in {path.name}: expected {project_identifier}_")
            missing = text_has_all(path, REQUIRED_LOG_FIELDS)
            if missing:
                errors.append(f"missing fields in {path.name}: {', '.join(missing)}")
            if kind == "level1_plan":
                plan_missing = text_has_all(path, REQUIRED_LEVEL1_PLAN_FIELDS)
                if plan_missing:
                    errors.append(f"level1 plan missing contract fields in {path.name}: {', '.join(plan_missing)}")
            if kind == "level2_plan":
                plan_missing = text_has_all(path, REQUIRED_LEVEL2_PLAN_FIELDS)
                if plan_missing:
                    errors.append(f"level2 plan missing contract fields in {path.name}: {', '.join(plan_missing)}")
            if kind == "level2_results" and "assistant_audit_status:" not in path.read_text(encoding="utf-8", errors="replace"):
                errors.append(f"final result lacks assistant_audit_status: {path.name}")
            required = REQUIRED_FIELDS_BY_RECORD_TYPE.get(kind)
            if required:
                record_missing = text_has_all(path, required)
                if record_missing:
                    errors.append(f"record missing required fields in {path.name}: {', '.join(record_missing)}")
            if kind in ("level1_summary", "level1_warning", "level1_error"):
                if not LEVEL1_ASSISTANT_CODE.fullmatch(code):
                    errors.append(f"invalid level1 assistant-scope task code in {path.name}")
            if kind == "level1_results":
                if not LEVEL1_PLAN_CODE.fullmatch(code):
                    errors.append(f"invalid level1 aggregate task code in {path.name}")

    root_templates = root / "root" / "templates"
    if root_templates.is_dir():
        for path in sorted(root_templates.rglob("*TASK*.md")):
            missing = text_has_all(path, REQUIRED_TASK_FIELDS)
            if missing:
                warnings.append(f"template missing task fields in {path.relative_to(root)}: {', '.join(missing)}")

    workspaces = root / "ai_workspace"
    if workspaces.is_dir():
        for path in sorted(workspaces.rglob("TASK_PACKAGE.md")):
            missing = text_has_all(path, REQUIRED_TASK_FIELDS)
            if missing:
                errors.append(f"task package missing fields in {path.relative_to(root)}: {', '.join(missing)}")
            text = path.read_text(encoding="utf-8", errors="replace")
            code_line = next((line for line in text.splitlines() if "task_code:" in line), "")
            candidate = code_line.split("task_code:", 1)[-1].strip().strip("`")
            if candidate and "<" not in candidate and not TASK_CODE.fullmatch(candidate):
                errors.append(f"invalid task code in {path.relative_to(root)}")
            elif candidate and "<" not in candidate and project_identifier and not candidate.startswith(f"{project_identifier}_"):
                errors.append(f"project identifier mismatch in {path.relative_to(root)}: expected {project_identifier}_")

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    print(f"RESULT: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors, {len(warnings)} warnings)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
