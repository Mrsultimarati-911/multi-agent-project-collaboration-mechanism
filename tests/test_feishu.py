"""Notification regression tests: no test sends a real network request."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from notifications import feishu


class FeishuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "rules").mkdir()
        (self.root / "rules/00-core-governance.md").write_text(
            "- governance-version: 2\n- project-code-prefix: TEST\n"
            "- original-project-identifier: TEST\n- current-project-identifier: TEST\n"
            "- notifications: { enabled: true }\n", encoding="utf-8")
        self.url = "https://open.feishu.cn/open-apis/bot/v2/hook/unit-test-only"
        self.secret = "unit-test-secret"
        self.environment = patch.dict(os.environ, {"FEISHU_WEBHOOK_URL": self.url, "FEISHU_WEBHOOK_SECRET": self.secret}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.opener_patch = patch.object(feishu.urllib.request, "build_opener")
        self.build_opener = self.opener_patch.start()
        self.addCleanup(self.opener_patch.stop)
        self.response = MagicMock()
        self.response.status = 200
        self.response.read.return_value = b'{"code":0,"msg":"success"}'
        self.build_opener.return_value.open.return_value.__enter__.return_value = self.response
        self.event = {"event_id": "TEST:permission-1", "owner_intervention_required": True, "question": "Need permission"}
        self.output = io.StringIO()

    def notify(self, event=None, **kwargs):
        with contextlib.redirect_stdout(self.output):
            return feishu.notify(self.root, self.event if event is None else event, **kwargs)

    def state(self):
        path = self.root / "root/notifications/.feishu_notifications.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return data[hashlib.sha256(self.event["event_id"].encode()).hexdigest()]

    def test_no_intervention_never_sends(self):
        self.assertEqual(self.notify({"owner_intervention_required": False})["notification_status"], "skipped")
        self.build_opener.assert_not_called()

    def test_known_signature_vector(self):
        self.assertEqual(feishu.generate_signature("1700000000", self.secret), "wjfRqjvrFW1O9p5NWa2DHJCyt/9bB36ZHkDxu0POpJw=")

    def test_env_credentials_and_success(self):
        with patch.object(feishu.time, "time", return_value=1700000000):
            self.assertEqual(self.notify()["notification_status"], "sent")
        request = self.build_opener.return_value.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, self.url)
        self.assertEqual(payload["sign"], "wjfRqjvrFW1O9p5NWa2DHJCyt/9bB36ZHkDxu0POpJw=")
        self.assertEqual(self.state()["status"], "sent")
        self.assertNotIn(self.secret, self.output.getvalue())
        self.assertNotIn(self.url, self.output.getvalue())

    def test_business_failure_at_http_200(self):
        self.response.read.return_value = b'{"code":19024,"msg":"bad signature"}'
        result = self.notify()
        self.assertEqual(result["notification_status"], "failed")
        self.assertTrue(result["owner_dialogue_fallback"])
        self.assertEqual(self.state()["status"], "failed")

    def test_missing_or_boolean_business_code_is_not_success(self):
        for body in (b'{}', b'{"code":false}', b'{"code":"0"}', b'not-json', b'{"code":0,"StatusCode":1}'):
            with self.subTest(body=body):
                self.response.read.return_value = body
                result = self.notify({**self.event, "material_update": True})
                self.assertEqual(result["notification_status"], "failed")

    def test_legacy_business_success(self):
        self.response.read.return_value = b'{"StatusCode":0}'
        self.assertEqual(self.notify()["notification_status"], "sent")

    def test_pending_is_persisted_before_network(self):
        def inspect(*args, **kwargs):
            self.assertEqual(self.state()["status"], "pending")
            context = MagicMock()
            context.__enter__.return_value = self.response
            return context
        self.build_opener.return_value.open.side_effect = inspect
        self.assertEqual(self.notify()["notification_status"], "sent")

    def test_duplicate_skips_and_material_update_resends(self):
        self.notify()
        self.assertEqual(self.notify()["notification_status"], "skipped")
        self.assertEqual(self.build_opener.return_value.open.call_count, 1)
        self.assertEqual(self.notify({**self.event, "material_update": True})["notification_status"], "sent")
        self.assertEqual(self.build_opener.return_value.open.call_count, 2)
        self.assertEqual(self.state()["attempts"], 2)

    def test_failed_event_deduplicates_with_owner_fallback(self):
        self.response.read.return_value = b'{"code":1}'
        self.notify()
        result = self.notify()
        self.assertEqual(result["notification_status"], "skipped")
        self.assertTrue(result["owner_dialogue_fallback"])
        self.assertEqual(self.build_opener.return_value.open.call_count, 1)

    def test_resolve_stops_same_event(self):
        self.notify()
        self.assertEqual(self.notify(resolve_event_id=self.event["event_id"])["notification_status"], "resolved")
        self.assertEqual(self.state()["status"], "resolved")
        self.assertEqual(self.notify({**self.event, "material_update": True})["notification_status"], "skipped")
        self.assertEqual(self.build_opener.return_value.open.call_count, 1)

    def test_missing_environment_warns_without_crash(self):
        with patch.dict(os.environ, {}, clear=True):
            result = self.notify()
        self.assertEqual(result["notification_status"], "failed")
        self.assertIn("WARNING", self.output.getvalue())
        self.assertEqual(self.state()["status"], "failed")
        self.build_opener.assert_not_called()

    def test_old_json_credentials_are_never_used_or_echoed(self):
        directory = self.root / "root/notifications"
        directory.mkdir(parents=True)
        (directory / "feishu_config.json").write_text(json.dumps({"webhook_url": self.url, "webhook_secret": self.secret}), encoding="utf-8")
        self.assertEqual(self.notify()["notification_status"], "failed")
        self.build_opener.assert_not_called()
        self.assertNotIn(self.url, self.output.getvalue())
        self.assertNotIn(self.secret, self.output.getvalue())

    def test_enabled_only_optional_config(self):
        directory = self.root / "root/notifications"
        directory.mkdir(parents=True)
        (directory / "feishu_config.json").write_text('{"enabled":false}', encoding="utf-8")
        self.assertEqual(self.notify()["notification_status"], "skipped")
        self.build_opener.assert_not_called()

    def test_core_disabled_takes_precedence(self):
        with (self.root / "rules/00-core-governance.md").open("a", encoding="utf-8") as handle:
            handle.write("- notifications-enabled: false\n")
        self.assertEqual(self.notify()["notification_status"], "skipped")
        self.build_opener.assert_not_called()

    def test_exception_and_payload_do_not_leak(self):
        self.build_opener.return_value.open.side_effect = OSError(self.url + self.secret)
        result = self.notify({**self.event, "question": self.url + self.secret})
        self.assertEqual(result["notification_status"], "failed")
        disk = (self.root / "root/notifications/.feishu_notifications.json").read_text(encoding="utf-8")
        for value in (self.url, self.secret, self.event["event_id"], "Need permission"):
            self.assertNotIn(value, disk)
            self.assertNotIn(value, self.output.getvalue())
        sent = json.loads(self.build_opener.return_value.open.call_args.args[0].data)
        self.assertNotIn(self.secret, sent["content"]["text"])
        self.assertNotIn(self.url, sent["content"]["text"])

    def test_notification_directory_symlink_escape_rejected(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        (self.root / "root").mkdir()
        try:
            (self.root / "root/notifications").symlink_to(outside.name, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        self.assertEqual(self.notify()["notification_status"], "failed")
        self.assertEqual(list(Path(outside.name).iterdir()), [])
        self.build_opener.assert_not_called()

    def test_runtime_state_symlink_guard_without_os_symlink_privilege(self):
        # Exercise the explicit state-file guard on hosts without symlink privileges.
        with patch.object(feishu.Path, "is_symlink", lambda path: path.name == ".feishu_notifications.json"):
            self.assertEqual(self.notify()["notification_status"], "failed")
        self.build_opener.assert_not_called()
        self.assertFalse((self.root / "root/notifications/.feishu_notifications.json").exists())

    def test_startup_business_success_and_dedup(self):
        self.assertEqual(self.notify({}, startup=True)["notification_status"], "sent")
        payload = json.loads(self.build_opener.return_value.open.call_args.args[0].data)
        self.assertIn("TEST_项目已启动飞书监控", payload["content"]["text"])
        self.assertEqual(self.notify({}, startup=True)["notification_status"], "skipped")


if __name__ == "__main__":
    unittest.main()
