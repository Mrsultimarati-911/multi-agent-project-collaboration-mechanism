"""Regression cases reproduced during the independent governance review."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.helpers import (TASK, accepted_task, advance, base, initialize, make_stage,
                           make_task, reference)
from governance_schema import load_history
from record_engine import append_event
from validate_project_governance import validate_project


class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = initialize(Path(self.tmp.name) / "project")
        (self.root / "rules/owner-integration-approval.md").write_text(
            "Test fixture: the owner explicitly approves the requested integration target.\n",
            encoding="utf-8")

    def submitted(self):
        plan = make_task(self.root)
        for state in ("dispatched", "running", "submitted"):
            advance(self.root, plan, state)
        return plan

    def accepted(self, code=TASK):
        accepted_task(self.root, code)
        return next(e for e in load_history(self.root)[0]
                    if e["record_type"] == "level2_plan" and e["task_code"] == code)

    def envelope(self, **changes):
        value = {
            "auto_dispatch": True, "max_module_assistants": 0,
            "max_parallel_employees_per_assistant": 5,
            "allowed_task_types": ["data_processing", "testing"],
            "allowed_reads": ["raw_data", "common_data", "common_artifacts", "ai_workspace"],
            "allowed_writes": ["ai_workspace"],
            "publish_permissions": {"common_data": True, "common_artifacts": True},
            "integration_permissions": {"assistant_workspace": True, "project_demo": True, "project_final": False},
        }
        value.update(changes)
        return value

    def module_stage(self):
        return make_stage(self.root, participating_assistants=["assistant_00", "assistant_01"],
            workstreams={"MAIN": {"owner": "assistant_00", "depends_on": []},
                         "MODULE": {"owner": "assistant_01", "depends_on": []}},
            authority_envelope=self.envelope(max_module_assistants=1))

    def test_bare_audit_reference_is_pinned_before_later_ledger_entries(self):
        plan = self.submitted()
        audit = advance(self.root, plan, "audited", audit="accepted")
        result = append_event(self.root, base("level2_results", TASK, "accepted",
            level2_plan_reference=plan["_path"], level2_results_mid_reference=audit["_path"],
            assistant_audit_reference=audit["_path"], assistant_audit_status="accepted"))
        self.assertEqual(result["assistant_audit_reference"], reference(audit))
        self.assertEqual(result["level2_results_mid_reference"], reference(audit))
        self.assertEqual(result["level2_plan_reference"], reference(plan))
        advance(self.root, plan, "integrated", integration_target="project_demo/module")
        summary = append_event(self.root, base("level2_summary", TASK, "integrated",
            assistant_audit_reference=result["assistant_audit_reference"],
            level2_results_reference=result["_path"]))
        self.assertEqual(summary["assistant_audit_reference"], reference(audit))
        self.assertEqual(summary["level2_results_reference"], reference(result))
        self.assertEqual(validate_project(self.root)[0], [])

    def test_audit_cannot_change_submitted_attempt(self):
        plan = self.submitted()
        with self.assertRaisesRegex(ValueError, "attempt/delivery must match"):
            advance(self.root, plan, "audited", attempt=99, audit="accepted")

    def test_audit_cannot_switch_to_unsubmitted_delivery(self):
        plan = self.submitted()
        other = self.root / plan["workspace"] / "unsubmitted.txt"
        other.write_text("different scoped delivery", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "attempt/delivery must match"):
            advance(self.root, plan, "audited", audit="accepted",
                    employee_delivery_reference=other.relative_to(self.root).as_posix())

    def test_accepted_audit_rejects_bytes_changed_after_submission(self):
        plan = self.submitted()
        (self.root / plan["workspace"] / "delivery.txt").write_text("edited after submission", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed after submission"):
            advance(self.root, plan, "audited", audit="accepted")

    def test_integration_requires_target(self):
        plan = self.accepted()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "integrated")

    def test_integration_denied_by_envelope_needs_explicit_owner_evidence(self):
        make_stage(self.root, authority_envelope=self.envelope(integration_permissions={
            "assistant_workspace": False, "project_demo": False, "project_final": False}))
        plan = self.accepted()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "integrated", integration_target="project_demo/module")
        advance(self.root, plan, "integrated", integration_target="project_demo/module",
                owner_integration_approval_evidence="rules/owner-integration-approval.md")
        self.assertEqual(validate_project(self.root)[0], [])

    def test_project_final_always_requires_owner_even_if_envelope_says_yes(self):
        make_stage(self.root, authority_envelope=self.envelope(integration_permissions={
            "assistant_workspace": True, "project_demo": True, "project_final": True}))
        plan = self.accepted()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "integrated", integration_target="project_final/release")
        advance(self.root, plan, "integrated", integration_target="project_final/release",
                owner_integration_approval_evidence="rules/owner-integration-approval.md")
        self.assertEqual(validate_project(self.root)[0], [])

    def test_module_assistant_cannot_integrate_project_demo(self):
        self.module_stage()
        plan = self.accepted("DEMO_00-01-001-0000")
        with self.assertRaisesRegex(ValueError, "only coordinator"):
            advance(self.root, plan, "integrated", integration_target="project_demo/module",
                    owner_integration_approval_evidence="rules/owner-integration-approval.md")

    def test_module_integration_stays_in_own_assistant_workspace(self):
        self.module_stage()
        plan = self.accepted("DEMO_00-01-001-0000")
        with self.assertRaisesRegex(ValueError, "role scope"):
            advance(self.root, plan, "integrated", integration_target="assistant_workspace/assistant_00/module")
        advance(self.root, plan, "integrated", integration_target="assistant_workspace/assistant_01/module")
        self.assertEqual(validate_project(self.root)[0], [])


if __name__ == "__main__":
    unittest.main()
