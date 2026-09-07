"""Independent tests for authoritative append-only record transitions."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from helpers import REPO, STAGE, TASK, advance, base, initialize, make_stage, make_task, reference
from governance_schema import current_state, load_history, replay_history
from record_engine import append_event, main


class RecordEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = initialize(Path(self.temp.name))

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in (self.root / "work_logs").glob("*.md")}

    def running_task(self):
        plan = make_task(self.root)
        advance(self.root, plan, "dispatched")
        return plan, advance(self.root, plan, "running")

    def final_payload(self, plan, audit, **changes):
        event = base("level2_results", plan["task_code"], "accepted", plan["responsible_assistant"],
                     level2_plan_reference=reference(plan), level2_results_mid_reference=reference(audit),
                     assistant_audit_reference=reference(audit), assistant_audit_status="accepted")
        event.update(changes)
        return event

    def reject(self, payload):
        before = self.snapshot()
        with self.assertRaises(ValueError):
            append_event(self.root, payload)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / "root/.record_engine.lock").exists())

    def test_full_transition_chain_and_engine_owned_previous_state(self):
        plan = make_task(self.root)
        previous = "planned"
        for state in ("dispatched", "running", "submitted", "audited"):
            event = advance(self.root, plan, state, audit="accepted" if state == "audited" else "not_requested")
            self.assertEqual(event["actual_previous_status"], previous)
            previous = state
        accepted = append_event(self.root, self.final_payload(plan, event))
        self.assertEqual(accepted["actual_previous_status"], "audited")
        history, warnings = load_history(self.root)
        self.assertFalse(warnings)
        self.assertEqual(current_state(history, TASK), "accepted")
        self.assertEqual([e["execution_status"] for e in history if e["task_code"] == TASK],
                         ["planned", "dispatched", "running", "submitted", "audited", "accepted"])
        replay_history(self.root, history)

    def test_new_process_recovers_state_from_markdown(self):
        plan, running = self.running_task()
        data = base("level2_results_mid", TASK, "submitted", level2_plan_reference=reference(plan),
                    attempt_number=1, employee_delivery_reference=plan["workspace"] + "/delivery.txt",
                    assistant_audit_status="pending", expected_previous_status="running")
        payload = self.root / "root/event.json"
        payload.write_text(json.dumps(data), encoding="utf-8")
        command = [sys.executable, "-B", str(REPO / "scripts/record_engine.py"), str(self.root), "--event", "root/event.json"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        history, _ = load_history(self.root)
        self.assertEqual(current_state(history, TASK), "submitted")
        self.assertEqual(history[-1]["actual_previous_status"], "running")
        self.assertEqual(history[-1]["previous_event_hash"], running["event_hash"])

    def test_running_to_accepted_without_previous_assertion_rejected(self):
        plan, running = self.running_task()
        self.reject(self.final_payload(plan, running))

    def test_forged_expected_previous_state_cannot_authorize_transition(self):
        plan, running = self.running_task()
        self.reject(self.final_payload(plan, running, expected_previous_status="audited"))

    def test_legacy_previous_status_cannot_authorize_transition(self):
        plan, running = self.running_task()
        self.reject(self.final_payload(plan, running, previous_status="audited"))

    def test_caller_cannot_set_actual_previous_state(self):
        plan, running = self.running_task()
        self.reject(self.final_payload(plan, running, actual_previous_status="audited"))

    def test_rejected_assistant_audit_cannot_be_finalized(self):
        plan, _ = self.running_task()
        advance(self.root, plan, "submitted")
        rejected = advance(self.root, plan, "audited", audit="rejected")
        self.reject(self.final_payload(plan, rejected))

    def test_same_named_empty_audit_file_is_not_authoritative_audit(self):
        plan, _ = self.running_task()
        advance(self.root, plan, "submitted")
        audit = advance(self.root, plan, "audited", audit="accepted")
        fake = "rules/assistant_audit_accepted.md"
        (self.root / fake).write_text("", encoding="utf-8")
        self.reject(self.final_payload(plan, audit, assistant_audit_reference=fake))

    def test_empty_owner_approval_file_cannot_grant_stage_authority(self):
        (self.root / "rules/owner-approval.md").write_text(" \n\t", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            make_stage(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_audited_delivery_cannot_change_before_finalization(self):
        plan, _ = self.running_task()
        advance(self.root, plan, "submitted")
        audit = advance(self.root, plan, "audited", audit="accepted")
        (self.root / audit["employee_delivery_reference"]).write_text("changed after acceptance\n", encoding="utf-8")
        self.reject(self.final_payload(plan, audit))

    def test_two_rework_attempts_preserve_all_previous_events(self):
        plan, _ = self.running_task()
        for attempt in (1, 2):
            advance(self.root, plan, "submitted", attempt=attempt)
            advance(self.root, plan, "audited", attempt=attempt, audit="rejected")
            before = self.snapshot()
            advance(self.root, plan, "running", attempt=attempt + 1)
            after = self.snapshot()
            for path, content in before.items():
                self.assertTrue(after[path].startswith(content))
        advance(self.root, plan, "submitted", attempt=3)
        audit = advance(self.root, plan, "audited", attempt=3, audit="accepted")
        append_event(self.root, self.final_payload(plan, audit))
        history, _ = load_history(self.root)
        audits = [e for e in history if e["task_code"] == TASK and e["execution_status"] == "audited"]
        self.assertEqual([e["assistant_audit_status"] for e in audits], ["rejected", "rejected", "accepted"])
        self.assertEqual([e["attempt_number"] for e in audits], [1, 2, 3])
        self.assertEqual(current_state(history, TASK), "accepted")
        replay_history(self.root, history)

    def test_attempt_counter_cannot_go_backwards(self):
        plan, _ = self.running_task()
        advance(self.root, plan, "submitted", attempt=2)
        before = self.snapshot()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "audited", attempt=1, audit="accepted")
        self.assertEqual(self.snapshot(), before)

    def test_frozen_plan_cannot_be_rewritten(self):
        make_task(self.root)
        before = self.snapshot()
        with self.assertRaises(ValueError):
            make_task(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_hash_tampering_rejected_by_history_and_next_append(self):
        plan, running = self.running_task()
        path = self.root / running["_path"]
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('"task_name": "测试任务"', '"task_name": "被修改的测试任务"'), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_history(self.root)
        before = self.snapshot()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "submitted")
        self.assertEqual(self.snapshot(), before)

    def test_narrative_tampering_rejected(self):
        _, running = self.running_task()
        with (self.root / running["_path"]).open("a", encoding="utf-8") as handle:
            handle.write("unauthorized narrative\n")
        with self.assertRaises(ValueError):
            load_history(self.root)

    def test_front_matter_hash_tamper_rejected_with_unchanged_narrative(self):
        _, running = self.running_task()
        path = self.root / running["_path"]
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(running["event_hash"], "0" * 64, 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hash"):
            load_history(self.root)

    def test_deleted_historical_event_breaks_hash_chain(self):
        plan, _ = self.running_task()
        # Temporary fixture simulates an external writer deleting a historical event.
        (self.root / plan["_path"]).unlink()
        with self.assertRaises(ValueError):
            load_history(self.root)

    def test_record_type_and_task_scope_binding(self):
        for kind, code in (("level1_plan", TASK), ("level2_plan", STAGE), ("../escape", TASK), ("arbitrary_record", TASK)):
            with self.subTest(kind=kind, code=code):
                self.reject(base(kind, code, "planned"))

    def test_task_identity_path_injection_rejected(self):
        for task_code in ("../escape", "/tmp/escape", r"C:\outside", "DEMO_00-00-000-0000/../../escape"):
            with self.subTest(task_code=task_code):
                self.reject(base("level2_plan", task_code, "planned"))

    def test_delivery_path_escape_rejected(self):
        plan, _ = self.running_task()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            advance(self.root, plan, "submitted", employee_delivery_reference="../outside.txt")
        self.assertEqual(self.snapshot(), before)

    def test_cli_event_path_escape_rejected(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([str(self.root), "--event", "../outside.json"])
        self.assertNotEqual(code, 0)
        self.assertIn("REJECTED", output.getvalue())
        self.assertEqual(self.snapshot(), {})

    def test_dry_run_does_not_append_history(self):
        plan, running = self.running_task()
        before = self.snapshot()
        payload = base("level2_results_mid", TASK, "submitted", level2_plan_reference=reference(plan),
                       attempt_number=1, employee_delivery_reference=plan["workspace"] + "/delivery.txt", assistant_audit_status="pending")
        proposed = append_event(self.root, payload, dry_run=True)
        self.assertEqual(proposed["actual_previous_status"], "running")
        self.assertEqual(proposed["previous_event_hash"], running["event_hash"])
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
