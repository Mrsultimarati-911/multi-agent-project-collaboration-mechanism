import tempfile
import unittest
from pathlib import Path
from tests.helpers import initialize, accepted_task, make_stage, make_task
from governance_schema import read_project_config
from validate_project_governance import validate_project


class IdentifierAliasTests(unittest.TestCase):
    def test_append_rename_preserves_history_and_accepts_new_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            accepted_task(root)
            before = {p.name:p.read_bytes() for p in (root/'work_logs').glob('*.md')}
            with (root/'rules/00-core-governance.md').open('a', encoding='utf-8') as handle:
                handle.write('\n- current-project-identifier: RENAMED\n- project-identifier-aliases: ["DEMO", "RENAMED"]\n')
            config = read_project_config(root)
            self.assertEqual(config['identifiers'], {'DEMO','RENAMED'})
            make_stage(root, task_code='RENAMED_01-##-###-####')
            make_task(root, 'RENAMED_01-00-001-0000')
            self.assertEqual(validate_project(root)[0], [])
            self.assertEqual(before, {name:(root/'work_logs'/name).read_bytes() for name in before})
            with self.assertRaisesRegex(ValueError, 'unrecognized'):
                make_stage(root, task_code='UNAPPROVED_02-##-###-####')

    def test_yaml_block_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            with (root/'rules/00-core-governance.md').open('a', encoding='utf-8') as handle:
                handle.write('\nproject-identifier-aliases:\n  - OLD\n  - NEW\n')
            self.assertTrue({'OLD','NEW'} <= read_project_config(root)['identifiers'])


if __name__ == '__main__':
    unittest.main()
