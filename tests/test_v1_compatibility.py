import tempfile
import unittest
from pathlib import Path
from tests.helpers import initialize
from governance_schema import V1_DIRS
from validate_project_governance import validate_project


class V1CompatibilityTests(unittest.TestCase):
    def test_legacy_read_only_without_v2_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in V1_DIRS:
                (root/name).mkdir(parents=True, exist_ok=True)
            (root/'AGENTS.md').write_text('# Legacy routing\n', encoding='utf-8')
            (root/'rules/00-core-governance.md').write_text('- governance-version: 1\n- project-code-prefix: OLD\n', encoding='utf-8')
            for name in ('01-role-and-filesystem.md','02-work-log-governance.md'):
                (root/'rules'/name).write_text('# Legacy rules\n', encoding='utf-8')
            log = root/'work_logs/level1_plan_OLD_00-##-###-####.md'
            log.write_text('---\nrecord_type: level1_plan\nstatus: approved-active\n---\nLegacy narrative\n', encoding='utf-8')
            before = log.read_bytes()
            errors, warnings = validate_project(root)
            self.assertEqual(errors, [])
            self.assertTrue(any('V1 compatibility' in w for w in warnings))
            self.assertTrue(any('common_data' in w for w in warnings))
            self.assertEqual(log.read_bytes(), before)

    def test_v2_missing_feature_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = initialize(Path(tmp)/'project')
            (root/'common_data').rmdir()
            errors, _ = validate_project(root)
            self.assertTrue(any('common_data' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
