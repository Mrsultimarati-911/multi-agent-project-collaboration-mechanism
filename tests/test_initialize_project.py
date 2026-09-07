"""Initialize/migrate without overwriting project content or sending real notifications."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import initialize_project
from governance_schema import read_project_config


class InitializeProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = io.StringIO()
        self.network = patch.object(initialize_project.subprocess, "run")
        self.run = self.network.start()
        self.addCleanup(self.network.stop)
        self.run.return_value = subprocess.CompletedProcess([], 1, '{"notification_status":"failed","owner_dialogue_fallback":true}\n', "")

    def initialize(self, *args):
        with contextlib.redirect_stdout(self.output):
            return initialize_project.main([str(self.root), "--prefix", "TEST", *args])

    def test_empty_v2_project(self):
        self.assertEqual(self.initialize("--feishu-notifications", "disabled"), 0)
        for path in ("common_data", "common_artifacts", "assistant_workspace", "plan/interfaces", "root", "rules", "work_logs", "ai_workspace"):
            self.assertTrue((self.root / path).is_dir(), path)
        for path in ("root/governance_schema.py", "root/artifact_support.py", "root/record_engine.py", "root/notifications/feishu.py"):
            self.assertTrue((self.root / path).is_file(), path)
        self.assertEqual(read_project_config(self.root)["governance_version"], 2)
        self.assertIn("TEST", read_project_config(self.root)["identifiers"])
        self.run.assert_not_called()

    def test_disabled_persisted_and_repeat_does_not_enable(self):
        self.initialize("--feishu-notifications", "disabled")
        self.assertFalse(read_project_config(self.root)["notifications_enabled"])
        core = (self.root / "rules/00-core-governance.md").read_bytes()
        self.initialize()
        self.assertFalse(read_project_config(self.root)["notifications_enabled"])
        self.assertEqual((self.root / "rules/00-core-governance.md").read_bytes(), core)
        self.run.assert_not_called()

    def test_repeat_initialization_is_idempotent(self):
        self.initialize("--feishu-notifications", "disabled")
        before = {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.initialize("--feishu-notifications", "disabled")
        after = {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_existing_files_and_scripts_preserved(self):
        paths = {"AGENTS.md": b"owner customized AGENTS\n", "root/record_engine.py": b"# owner script\n", "root/notifications/feishu.py": b"# legacy adapter\n"}
        for name, content in paths.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.initialize()
        for name, content in paths.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        self.assertIn("MIGRATION_WARNING", self.output.getvalue())
        self.assertIn("preserved adapter needs migration review", self.output.getvalue())
        self.run.assert_not_called()

    def test_v1_project_only_adds_missing_content(self):
        paths = {"rules/00-core-governance.md": b"- governance-version: 1\n- project-code-prefix: OLD\n", "work_logs/old.md": b"legacy immutable history\n", "AGENTS.md": b"custom routing\n"}
        for name, content in paths.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.initialize()
        for name, content in paths.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        self.assertEqual(read_project_config(self.root)["governance_version"], 1)
        self.assertTrue((self.root / "common_artifacts").is_dir())
        self.assertIn("MIGRATION_WARNING", self.output.getvalue())

    def test_explicit_existing_choice_appends_only(self):
        self.initialize()
        core = self.root / "rules/00-core-governance.md"
        before = core.read_bytes()
        self.initialize("--feishu-notifications", "disabled")
        after = core.read_bytes()
        self.assertTrue(after.startswith(before))
        self.assertIn(b"notifications-enabled: false", after[len(before):])
        self.assertFalse(read_project_config(self.root)["notifications_enabled"])
        self.initialize("--feishu-notifications", "enabled")
        self.assertTrue(core.read_bytes().startswith(after))
        self.assertTrue(read_project_config(self.root)["notifications_enabled"])

    def test_gitignore_appends_each_missing_rule_and_preserves_bytes(self):
        original = b"# custom\r\n*.tmp\r\nroot/notifications/feishu_config.json"
        path = self.root / ".gitignore"
        path.write_bytes(original)
        self.initialize("--feishu-notifications", "disabled")
        new = path.read_bytes()
        self.assertTrue(new.startswith(original))
        for rule in initialize_project.IGNORE_RULES:
            self.assertEqual(new.decode().splitlines().count(rule), 1)
        self.initialize()
        self.assertEqual(path.read_bytes(), new)

    def test_new_project_defaults_enabled_and_failed_startup_nonblocking(self):
        self.assertEqual(self.initialize(), 0)
        self.assertTrue(read_project_config(self.root)["notifications_enabled"])
        self.run.assert_called_once()
        self.assertIn("not connected", self.output.getvalue())
        self.assertNotIn("connectivity confirmed", self.output.getvalue())

    def test_startup_success_requires_explicit_business_result(self):
        self.run.return_value = subprocess.CompletedProcess([], 0, '{"notification_status":"sent"}\n', "")
        self.initialize()
        self.assertIn("connectivity confirmed by Feishu business response", self.output.getvalue())

    def test_process_exit_zero_alone_never_claims_connected(self):
        self.run.return_value = subprocess.CompletedProcess([], 0, 'WARNING: fake transport success\n', "")
        self.initialize()
        self.assertIn("not connected", self.output.getvalue())
        self.assertNotIn("connectivity confirmed", self.output.getvalue())

    def test_startup_timeout_nonblocking_and_no_exception_leak(self):
        self.run.side_effect = subprocess.TimeoutExpired("secret-webhook-marker", 20)
        self.assertEqual(self.initialize(), 0)
        self.assertIn("startup check unavailable", self.output.getvalue())
        self.assertNotIn("secret-webhook-marker", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
