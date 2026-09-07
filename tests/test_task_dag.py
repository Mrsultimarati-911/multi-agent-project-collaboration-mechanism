import json
import tempfile
import unittest
from pathlib import Path
from tests.helpers import initialize, make_stage, make_task, advance, accepted_task, TASK, reference
from governance_schema import validate_dag, validate_interface
from validate_project_governance import validate_project


class TaskDagTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = initialize(Path(self.tmp.name)/'project')

    def test_valid_graph(self):
        validate_dag({'A': [], 'B': ['A'], 'C': ['B']})

    def test_missing_dependency(self):
        with self.assertRaisesRegex(ValueError, 'missing dependency'):
            make_task(self.root, depends_on=['DEMO_00-00-009-0000'])

    def test_self_dependency(self):
        with self.assertRaisesRegex(ValueError, 'self dependency'):
            make_task(self.root, depends_on=[TASK])

    def test_cycle(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            validate_dag({'A': ['B'], 'B': ['A']})

    def test_stage_cycle(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            make_stage(self.root, workstreams={'A': {'owner':'assistant_00','depends_on':['B']},
                'B': {'owner':'assistant_00','depends_on':['A']}})

    def test_stage_owner_must_be_declared(self):
        with self.assertRaisesRegex(ValueError, 'owner'):
            make_stage(self.root, workstreams={'A': {'owner':'assistant_01','depends_on':[]}})

    def test_dependency_planned_does_not_allow_dispatch(self):
        make_task(self.root)
        dependent = make_task(self.root, 'DEMO_00-00-001-0000', depends_on=[TASK])
        with self.assertRaisesRegex(ValueError, 'required state'):
            advance(self.root, dependent, 'dispatched')

    def test_accepted_dependency_allows_dispatch(self):
        accepted_task(self.root)
        dependent = make_task(self.root, 'DEMO_00-00-001-0000', depends_on=[TASK])
        advance(self.root, dependent, 'dispatched')
        self.assertEqual(validate_project(self.root)[0], [])

    def test_stricter_dependency_state_enforced(self):
        accepted_task(self.root)
        dependent = make_task(self.root, 'DEMO_00-00-001-0000', depends_on=[TASK],
            required_dependency_status={TASK:'integrated'})
        with self.assertRaisesRegex(ValueError, 'required state'):
            advance(self.root, dependent, 'dispatched')

    def test_dependency_requirement_cannot_be_downgraded_to_planned(self):
        make_task(self.root)
        with self.assertRaisesRegex(ValueError, 'required dependency state'):
            make_task(self.root, 'DEMO_00-00-001-0000', depends_on=[TASK],
                required_dependency_status={TASK:'planned'})

    def test_interface_fields_owner_and_containment(self):
        path = self.root/'plan/interfaces/CONTRACT.json'
        data = {'interface_id':'CONTRACT','version':1,'owner_assistant':'assistant_00','consumers':['assistant_00']}
        path.write_text(json.dumps(data), encoding='utf-8')
        make_task(self.root, interface_references=['plan/interfaces/CONTRACT.json'])
        self.assertEqual(validate_project(self.root)[0], [])
        for change in ({'version':0}, {'owner_assistant':'assistant_09'}, {'consumers':'assistant_00'}):
            with self.subTest(change=change):
                path.write_text(json.dumps({**data, **change}), encoding='utf-8')
                with self.assertRaises(ValueError):
                    validate_interface(self.root, 'plan/interfaces/CONTRACT.json', ['assistant_00'])
        with self.assertRaises(ValueError):
            validate_interface(self.root, '../CONTRACT.json')

    def test_missing_interface(self):
        with self.assertRaisesRegex(ValueError, 'missing referenced'):
            make_task(self.root, interface_references=['plan/interfaces/MISSING.json'])

    def test_envelope_scope_and_r3_rejected(self):
        with self.assertRaisesRegex(ValueError, 'scope exceeds'):
            make_task(self.root, allowed_reads=['rules'])
        with self.assertRaisesRegex(ValueError, 'owner explicit'):
            make_task(self.root, risk_level='R3')

    def test_explicit_owner_dispatch_remains_supported(self):
        plan = make_task(self.root, dispatch_authority='owner-approved',
            owner_dispatch_approval_evidence='rules/owner-approval.md', risk_level='R3')
        self.assertEqual(plan['dispatch_authority'], 'owner-approved')
        self.assertEqual(validate_project(self.root)[0], [])


if __name__ == '__main__':
    unittest.main()
