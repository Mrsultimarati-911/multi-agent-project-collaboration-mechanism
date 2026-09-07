from __future__ import annotations

import hashlib
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import TASK, accepted_task, advance, base, initialize, make_stage, make_task, reference
from artifact_support import hash_artifact, validate_artifact_reference, validate_manifest
from publish_artifact import publish
from governance_schema import EVENT_SEPARATOR, event_digest, load_history
from record_engine import append_event


class ArtifactPublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = initialize(Path(self.tmp.name) / "project")
        self.audit = accepted_task(self.root)
        self.source = self.root / "ai_workspace" / TASK / "delivery.txt"

    def publish(self, **changes):
        args = dict(kind="common_data", artifact_id="dataset", version="v0001",
                    source=self.source, producer_task=TASK, producer_employee="employee_00",
                    producer_assistant="assistant_00", audit_reference=self.audit)
        args.update(changes)
        return publish(self.root, **args)

    def test_workspace_publish_manifest_and_actual_sha256(self):
        version = self.publish()
        manifest = validate_manifest(self.root, version / "manifest.json")
        self.assertFalse((version / "manifest.yaml").exists())
        self.assertEqual((version / "delivery.txt").read_bytes(), self.source.read_bytes())
        self.assertEqual(manifest["content_hash"]["value"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(manifest["producer_task"], TASK)
        self.assertEqual(manifest["assistant_audit_reference"], self.audit)
        self.assertEqual(validate_artifact_reference(self.root, {"kind": "common_data", "artifact_id": "dataset", "version": "v0001"}), manifest)

    def test_immutable_version_cannot_overwrite(self):
        version = self.publish()
        original = (version / "manifest.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.publish()
        self.assertEqual((version / "manifest.json").read_bytes(), original)
        self.assertFalse((version.parent / ".v0001.publish.lock").exists())

    def test_identifier_traversal_rejected(self):
        for artifact_id in ("../outside", "x/../../outside", "x\\..\\outside", "/outside", "C:\\outside", "..", "NUL", "folder."):
            with self.subTest(artifact_id=artifact_id), self.assertRaises(ValueError):
                self.publish(artifact_id=artifact_id)
        self.assertFalse((self.root.parent / "outside").exists())

    def test_version_traversal_and_latest_rejected(self):
        for version in ("v../escape", "../v0001", "v0001/other", "v0001\\other", "latest", "v1"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.publish(version=version)
        with self.assertRaises(ValueError):
            validate_artifact_reference(self.root, {"kind": "common_data", "artifact_id": "dataset", "version": "latest"})

    def test_external_source_rejected(self):
        outside = self.root.parent / "outside.txt"
        outside.write_text("outside project", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.publish(source=outside)

    def test_unaudited_sibling_source_rejected(self):
        sibling = self.source.with_name("not-audited.txt")
        sibling.write_text("different task output", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "audit delivery scope"):
            self.publish(source=sibling)

    def test_source_changed_after_accepted_audit_rejected(self):
        self.source.write_text("changed after audit", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "audit.*hash|audit.*snapshot"):
            self.publish()

    def directory_delivery(self):
        plan = make_task(self.root, "DEMO_00-00-001-0000")
        for state in ("dispatched", "running"):
            advance(self.root, plan, state)
        source = self.root / plan["workspace"] / "数据 目录"
        source.mkdir()
        (source / "结果.csv").write_text("value\n1\n", encoding="utf-8")
        (source / "empty").mkdir()
        delivery = source.relative_to(self.root).as_posix()
        advance(self.root, plan, "submitted", employee_delivery_reference=delivery)
        audit = advance(self.root, plan, "audited", audit="accepted", employee_delivery_reference=delivery)
        return source, dict(producer_task=plan["task_code"], producer_employee=plan["responsible_employee"],
                           producer_assistant=plan["responsible_assistant"], audit_reference=reference(audit))

    def test_directory_publication_keeps_unicode_names(self):
        source, args = self.directory_delivery()
        version = self.publish(source=source, artifact_id="bundle", **args)
        manifest = validate_manifest(self.root, version / "manifest.json")
        self.assertEqual(manifest["name"], source.name)
        self.assertEqual(manifest["content_hash"]["mode"], "tree-v1")
        self.assertEqual(hash_artifact(version / source.name), hash_artifact(source))

    def test_directory_audit_does_not_implicitly_approve_sliced_publication(self):
        source, args = self.directory_delivery()
        with self.assertRaisesRegex(ValueError, "exactly match"):
            self.publish(source=source / "结果.csv", **args)

    def test_envelope_publication_permission_enforced(self):
        root = initialize(Path(self.tmp.name) / "no-publication")
        history, _ = load_history(self.root)
        envelope = copy.deepcopy(history[0]["authority_envelope"])
        envelope["publish_permissions"]["common_data"] = False
        make_stage(root, authority_envelope=envelope)
        audit = accepted_task(root)
        with self.assertRaisesRegex(ValueError, "Authority Envelope"):
            publish(root, kind="common_data", artifact_id="dataset", version="v0001",
                    source=root / "ai_workspace" / TASK / "delivery.txt", producer_task=TASK,
                    producer_employee="employee_00", producer_assistant="assistant_00", audit_reference=audit)

    def owner_dispatch_without_envelope_publish(self, *, publication_evidence=False):
        root = initialize(Path(self.tmp.name) / "owner-dispatch-no-publication")
        history, _ = load_history(self.root)
        envelope = copy.deepcopy(history[0]["authority_envelope"])
        envelope["publish_permissions"]["common_data"] = False
        make_stage(root, authority_envelope=envelope)
        changes = dict(dispatch_authority="owner-approved", owner_dispatch_approval_evidence="rules/owner-approval.md")
        if publication_evidence:
            (root / "rules/publication-approval.md").write_text("Owner explicitly permits this task to publish common_data.\n", encoding="utf-8")
            changes["owner_publication_approval_evidence"] = "rules/publication-approval.md"
        plan = make_task(root, **changes)
        for state in ("dispatched", "running", "submitted"):
            advance(root, plan, state)
        audit = advance(root, plan, "audited", audit="accepted")
        append_event(root, base("level2_results", TASK, "accepted", level2_plan_reference=reference(plan),
            level2_results_mid_reference=reference(audit), assistant_audit_reference=reference(audit), assistant_audit_status="accepted"))
        return root, audit

    def test_owner_dispatch_does_not_imply_publication_authority(self):
        root, audit = self.owner_dispatch_without_envelope_publish()
        with self.assertRaisesRegex(ValueError, "publication.*Authority Envelope"):
            publish(root, kind="common_data", artifact_id="dataset", version="v0001",
                    source=root / "ai_workspace" / TASK / "delivery.txt", producer_task=TASK,
                    producer_employee="employee_00", producer_assistant="assistant_00", audit_reference=reference(audit))
        self.assertFalse((root / "common_data/dataset/v0001").exists())

    def test_explicit_owner_publication_evidence_authorizes_exception(self):
        root, audit = self.owner_dispatch_without_envelope_publish(publication_evidence=True)
        path = publish(root, kind="common_data", artifact_id="dataset", version="v0001",
                       source=root / "ai_workspace" / TASK / "delivery.txt", producer_task=TASK,
                       producer_employee="employee_00", producer_assistant="assistant_00", audit_reference=reference(audit))
        validate_manifest(root, path / "manifest.json")

    def test_semantically_invalid_but_rehashed_history_cannot_publish_or_validate(self):
        version = self.publish()
        history, _ = load_history(self.root)
        audit = next(event for event in history if event["execution_status"] == "audited")
        audit["actual_previous_status"] = "running"  # Actual authoritative previous state is submitted.
        previous = None
        by_path = {}
        for event in history:
            value = {key: item for key, item in event.items() if not key.startswith("_")}
            value["previous_event_hash"] = previous
            value["event_hash"] = event_digest(value)
            previous = value["event_hash"]
            text = "---\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n---\n"
            text += f"\n# {value['record_type']}｜{value['task_name']}\n\n{value['event_description']}\n"
            by_path.setdefault(event["_path"], []).append(text)
        for path, blocks in by_path.items():
            (self.root / path).write_text(EVENT_SEPARATOR.join(blocks), encoding="utf-8")
        self.assertEqual(len(load_history(self.root)[0]), len(history))  # All hashes remain internally consistent.
        with self.assertRaisesRegex(ValueError, "previous state"):
            self.publish(version="v0002")
        with self.assertRaisesRegex(ValueError, "previous state"):
            validate_manifest(self.root, version / "manifest.json")

    def test_source_mutation_between_provenance_check_and_copy_is_rejected(self):
        changed = False
        def change_before_hash(path):
            nonlocal changed
            if not changed:
                self.source.write_text("changed after provenance validation", encoding="utf-8")
                changed = True
            return hash_artifact(path)
        with patch("publish_artifact.hash_artifact", side_effect=change_before_hash):
            with self.assertRaisesRegex(ValueError, "audit snapshot"):
                self.publish()
        self.assertFalse((self.root / "common_data/dataset/v0001").exists())

    def test_old_accepted_audit_cannot_publish_after_rework(self):
        plan = make_task(self.root, "DEMO_00-00-001-0000")
        for state in ("dispatched", "running", "submitted"):
            advance(self.root, plan, state)
        old = advance(self.root, plan, "audited", audit="accepted")
        args = dict(producer_task=plan["task_code"], producer_employee=plan["responsible_employee"],
                    audit_reference=reference(old), source=self.root / plan["workspace"] / "delivery.txt")
        advance(self.root, plan, "running", attempt=2)
        with self.assertRaisesRegex(ValueError, "publishable state"):
            self.publish(**args)
        advance(self.root, plan, "submitted", attempt=2)
        advance(self.root, plan, "audited", attempt=2, audit="accepted")
        with self.assertRaisesRegex(ValueError, "latest accepted audit"):
            self.publish(**args)

    def test_published_provenance_survives_workspace_cleanup(self):
        version = self.publish()
        self.source.unlink()
        self.assertEqual(validate_manifest(self.root, version / "manifest.json")["producer_task"], TASK)

    def test_rehashed_tampering_cannot_reuse_accepted_audit(self):
        version = self.publish()
        payload = version / "delivery.txt"
        payload.write_text("new unauthorized output", encoding="utf-8")
        path = version / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["content_hash"]["value"] = hash_artifact(payload)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "audit hash snapshot"):
            validate_manifest(self.root, path)

    def test_platform_independent_symlink_guard(self):
        real_is_symlink = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda path: path == self.source or real_is_symlink(path)):
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.publish()

    def test_missing_or_wrong_producer_audit_rejected(self):
        with self.assertRaises(ValueError):
            self.publish(audit_reference="work_logs/nonexistent.md")
        with self.assertRaisesRegex(ValueError, "producer"):
            self.publish(producer_employee="employee_01")
        with self.assertRaises(ValueError):
            self.publish(producer_task="DEMO_00-00-001-0000")

    def test_hash_tamper_rejected(self):
        version = self.publish()
        (version / "delivery.txt").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            validate_manifest(self.root, version / "manifest.json")

    def test_manifest_audit_tamper_rejected(self):
        version = self.publish()
        path = version / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["assistant_audit_reference"] = "work_logs/missing.md"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            validate_manifest(self.root, path)

    def test_unmanifested_payload_rejected(self):
        version = self.publish()
        (version / "extra.txt").write_text("untracked payload", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unmanifested"):
            validate_manifest(self.root, version / "manifest.json")

    def test_legacy_json_manifest_compatibility(self):
        version = self.publish()
        path = version / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["content_hash"].pop("mode")
        manifest["content_hash"]["value"] = hashlib.sha256(b"delivery.txt" + self.source.read_bytes()).hexdigest()
        manifest.pop("source_path")
        path.unlink()
        (version / "manifest.yaml").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(validate_artifact_reference(self.root, {"kind": "common_data", "artifact_id": "dataset", "version": "v0001"})["producer_task"], TASK)

    def test_failed_copy_leaves_no_published_version(self):
        with patch("publish_artifact.shutil.copy2", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                self.publish()
        parent = self.root / "common_data/dataset"
        self.assertEqual(list(parent.iterdir()), [])

    def test_directory_hash_tracks_names_empty_directories_and_content(self):
        directory = self.root / "ai_workspace/tree"
        directory.mkdir()
        (directory / "a.txt").write_text("one", encoding="utf-8")
        first = hash_artifact(directory)
        copy = self.root / "ai_workspace/tree-copy"
        shutil.copytree(directory, copy)
        self.assertEqual(hash_artifact(copy), first)
        (copy / "empty").mkdir()
        self.assertNotEqual(hash_artifact(copy), first)
        (copy / "empty").rmdir()
        (copy / "a.txt").rename(copy / "b.txt")
        self.assertNotEqual(hash_artifact(copy), first)

    def test_source_symlink_rejected(self):
        outside = self.root.parent / "outside.txt"
        outside.write_text("must not publish", encoding="utf-8")
        link = self.source.with_name("link.txt")
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink unavailable on host: {exc}")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.publish(source=link)

    def test_nested_symlink_rejected(self):
        directory, args = self.directory_delivery()
        outside = self.root.parent / "outside.txt"
        outside.write_text("must not publish", encoding="utf-8")
        try:
            (directory / "link.txt").symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink unavailable on host: {exc}")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.publish(source=directory, **args)


if __name__ == "__main__":
    unittest.main()
