import json
import re
import tempfile
import unittest
from pathlib import Path

from tests.helpers import REPO, STAGE, TASK, initialize, make_stage, make_task, advance, accepted_task, base, reference
from record_engine import append_event, RESERVED
from governance_schema import RECORD_PATTERNS, load_history, current_state
from validate_project_governance import validate_project

SCOPE = 'DEMO_00-00-###-####'


def template(name):
    text = (REPO/'assets/templates/root/templates'/name).read_text(encoding='utf-8')
    return json.loads(re.search(r'```json\s*\n(.*?)\n```', text, re.S).group(1))


def active_stage(root):
    events, _ = load_history(root)
    stage = next((e for e in events if e['record_type'] == 'level1_plan'), None) or make_stage(root)
    return append_event(root, base('level1_warning', SCOPE, 'active',
        level1_plan_reference=reference(stage), recovery_owner='assistant_00',
        recovery_plan='Read existing inputs', resumption_condition='Inputs present',
        affected_scope=['MAIN']))


class SchemaConsistencyTests(unittest.TestCase):
    def run_template(self, name):
        payload = template(name)
        kind = payload['record_type']
        self.assertFalse(RESERVED.intersection(payload), name)
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            delivery = root/'ai_workspace'/TASK/'delivery.txt'
            delivery.parent.mkdir(parents=True)
            delivery.write_text('Reviewed fixture delivery', encoding='utf-8')
            (root/'rules/owner-acceptance.md').write_text('Owner accepted fixture stage', encoding='utf-8')
            if kind != 'level1_plan':
                make_stage(root)
            if kind == 'level1_error':
                active_stage(root)
            if kind in {'level2_results_mid','level2_warning','level2_error','level2_results'}:
                plan = make_task(root)
                advance(root, plan, 'dispatched')
                advance(root, plan, 'running')
                if kind == 'level2_results':
                    advance(root, plan, 'submitted')
                    advance(root, plan, 'audited', audit='accepted')
            if kind in {'level2_summary','level1_results'}:
                accepted_task(root)
                if kind == 'level1_results':
                    append_event(root, template('LEVEL1_SUMMARY.md'))
                else:
                    events, _ = load_history(root)
                    result = next(e for e in events if e['record_type'] == 'level2_results')
                    payload['assistant_audit_reference'] = result['assistant_audit_reference']
            # These fixture evidence files are populated from explicit template refs.
            if 'direct_error_evidence' in payload:
                p = root/payload['direct_error_evidence']
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('Observed fixture failure', encoding='utf-8')
            event = append_event(root, payload)
            self.assertEqual(event['record_type'], kind)
            errors, _ = validate_project(root)
            self.assertEqual(errors, [], name)
            history, _ = load_history(root)
            self.assertEqual(history[-1]['event_id'], event['event_id'])

    def test_all_11_record_types_in_both_languages_roundtrip(self):
        names = sorted((REPO/'assets/templates/root/templates').glob('LEVEL*.md'))
        self.assertEqual(len(names), 22)
        self.assertEqual({template(p.name)['record_type'] for p in names}, set(RECORD_PATTERNS))
        for path in names:
            with self.subTest(template=path.name):
                self.run_template(path.name)

    def test_shared_schema_copied_to_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            self.assertEqual((root/'root/governance_schema.py').read_bytes(),
                             (REPO/'scripts/governance_schema.py').read_bytes())

    def test_stage_summary_cannot_bypass_owner_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            make_stage(root)
            active_stage(root)
            payload = template('LEVEL1_SUMMARY.md')
            payload['requested_status'] = 'accepted'
            with self.assertRaisesRegex(ValueError, 'owner-accepted'):
                append_event(root, payload)

    def test_null_timestamp_is_not_valid_required_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            plan = make_task(root)
            with self.assertRaisesRegex(ValueError, 'ISO timestamp'):
                advance(root, plan, 'dispatched', submission_timestamp=None)

    def test_assistant_scope_identity_matches_submitter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            stage = make_stage(root)
            with self.assertRaisesRegex(ValueError, 'scope task code'):
                append_event(root, base('level1_warning', 'DEMO_00-01-###-####', 'active',
                    level1_plan_reference=reference(stage), recovery_owner='assistant_00',
                    recovery_plan='Read inputs', affected_scope=['MAIN']))


if __name__ == '__main__':
    unittest.main()
