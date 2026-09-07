import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.helpers import REPO, TASK, initialize, accepted_task, make_task, advance, reference, base
from record_engine import append_event
from publish_artifact import publish
from validate_project_governance import validate_project


class EndToEndTests(unittest.TestCase):
    def test_happy_path_then_reject_bypass_using_installed_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            audit_ref = accepted_task(root)
            publish(root, kind='common_data', artifact_id='fixture-data', version='v0001',
                source='ai_workspace/'+TASK+'/delivery.txt', producer_task=TASK,
                producer_employee='employee_00', producer_assistant='assistant_00',
                audit_reference=audit_ref)
            downstream = make_task(root, 'DEMO_00-00-001-0000', depends_on=[TASK],
                consumes=[{'kind':'common_data','artifact_id':'fixture-data','version':'v0001'}],
                allowed_reads=['common_data/fixture-data/v0001'])
            advance(root, downstream, 'dispatched')
            advance(root, downstream, 'running')
            result = subprocess.run([sys.executable, '-B', str(root/'root/validate_project_governance.py'), str(root)],
                capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn('RESULT: PASS', result.stdout)
            payload = base('level2_results', downstream['task_code'], 'accepted',
                level2_plan_reference=reference(downstream), level2_results_mid_reference=audit_ref,
                assistant_audit_reference=audit_ref, assistant_audit_status='accepted')
            event_path = root/'root/invalid_event.json'
            event_path.write_text(json.dumps(payload), encoding='utf-8')
            rejected = subprocess.run([sys.executable, '-B', str(root/'root/record_engine.py'), str(root),
                '--event', str(event_path)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(rejected.returncode, 2, rejected.stdout+rejected.stderr)
            self.assertIn('REJECTED', rejected.stdout)
            self.assertIn('running -> accepted', rejected.stdout)
            self.assertEqual(validate_project(root)[0], [])

    def test_accepted_history_and_artifact_survive_source_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            audit_ref = accepted_task(root)
            source = 'ai_workspace/'+TASK+'/delivery.txt'
            publish(root, kind='common_data', artifact_id='stable-data', version='v0001',
                source=source, producer_task=TASK, producer_employee='employee_00',
                producer_assistant='assistant_00', audit_reference=audit_ref)
            (root/source).unlink()
            self.assertEqual(validate_project(root)[0], [])
            make_task(root, 'DEMO_00-00-001-0000', consumes=[{
                'kind':'common_data','artifact_id':'stable-data','version':'v0001'}])
            self.assertEqual(validate_project(root)[0], [])

    def test_human_block_cannot_resume_without_owner_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            plan = make_task(root)
            advance(root, plan, 'dispatched')
            advance(root, plan, 'running')
            append_event(root, base('level2_error', TASK, 'paused',
                level2_plan_reference=reference(plan), direct_error_evidence='rules/owner-approval.md',
                owner_intervention_required=True, paused_scope=[TASK]))
            with self.assertRaises(ValueError):
                advance(root, plan, 'running')
            append_event(root, base('level2_warning', TASK, 'paused',
                level2_plan_reference=reference(plan), recovery_owner='assistant_00',
                recovery_plan='Waiting for owner', resumption_condition='Owner permission'))
            with self.assertRaises(ValueError):
                advance(root, plan, 'running')
            (root/'rules/owner-resolution.md').write_text('Owner supplied permission in fixture', encoding='utf-8')
            advance(root, plan, 'running', owner_resolution_reference='rules/owner-resolution.md')
            self.assertEqual(validate_project(root)[0], [])


if __name__ == '__main__':
    unittest.main()
