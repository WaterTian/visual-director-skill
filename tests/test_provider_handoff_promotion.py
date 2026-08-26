from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.asset_qc import file_sha256, inspect_asset
from visual_director.compiler import compile_prompt
from visual_director.generation import build_generation_request
from visual_director.handoff import prepare_generation_handoff, record_generation_result
from visual_director.manifest import build_asset_manifest
from visual_director.promotion import promote_asset, reconcile_manifest_qc
from visual_director.selector import score_templates
from visual_director.validation import validate_document
from visual_director.visual_review import apply_visual_review


class ProviderHandoffPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.brief = json.loads(
            (ROOT / "tests" / "fixtures" / "hero-brief.json").read_text()
        )
        cls.catalog = json.loads((ROOT / "data" / "templates.json").read_text())
        selection = score_templates(cls.brief, cls.catalog)[0]
        template = next(item for item in cls.catalog["templates"] if item["id"] == selection["id"])
        cls.compiled = compile_prompt(cls.brief, template, selection)
        cls.request = build_generation_request(cls.brief, cls.compiled)
        cls.mock_capabilities = json.loads(
            (ROOT / "config" / "providers" / "mock.json").read_text()
        )

    def _write_request(self, root: Path) -> Path:
        path = root / "request.json"
        path.write_text(json.dumps(self.request), encoding="utf-8")
        return path

    def _reviewed_state(self, root: Path) -> tuple[Path, dict, dict]:
        candidate = root / "candidate.png"
        Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
        report, metadata = inspect_asset(candidate, self.brief)
        review = {
            "version": "0.1",
            "asset_id": self.brief["asset_id"],
            "reviewer": "fixture-reviewer",
            "checks": [
                {
                    "requirement": item["requirement"],
                    "status": "pass",
                    "evidence": "fixture-only visual evidence",
                }
                for item in report["visual_checks"]
            ],
        }
        reviewed = apply_visual_review(report, review)
        manifest = build_asset_manifest(
            self.brief,
            self.compiled,
            self.request,
            report,
            metadata,
        )
        return candidate, reviewed, reconcile_manifest_qc(manifest, reviewed)

    def _approval(self, decision: str = "approve") -> dict:
        return {
            "version": "0.1",
            "asset_id": self.brief["asset_id"],
            "reviewer": "fixture-approver",
            "decision": decision,
            "recorded_at": "2026-08-25T12:00:00Z",
            "exceptions": [],
        }

    def test_provider_cli_normalizes_success_failure_and_timeout(self) -> None:
        attempt_schema = json.loads(
            (ROOT / "schemas" / "provider-attempt.schema.json").read_text()
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = self._write_request(root)
            cases = [
                ("success", "0.0", "5", 0, "succeeded"),
                ("fail", "0.0", "5", 2, "failed"),
                ("sleep", "1.0", "0.1", 3, "timed_out"),
            ]
            for mode, delay, timeout, exit_code, status in cases:
                with self.subTest(mode=mode):
                    candidate = root / f"{mode}.png"
                    attempt_path = root / f"{mode}-attempt.json"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "run-provider.py"),
                            str(request_path),
                            str(candidate),
                            "--attempt-output",
                            str(attempt_path),
                            "--mock-mode",
                            mode,
                            "--mock-delay",
                            delay,
                            "--timeout-seconds",
                            timeout,
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(exit_code, result.returncode, result.stderr)
                    attempt = json.loads(attempt_path.read_text())
                    self.assertEqual([], validate_document(attempt, attempt_schema))
                    self.assertEqual(status, attempt["status"])
                    self.assertEqual(status == "succeeded", candidate.exists())

    def test_handoff_is_pending_by_default_and_project_relative(self) -> None:
        handoff = prepare_generation_handoff(
            self.request,
            "outputs/candidates/hero.png",
        )
        schema = json.loads(
            (ROOT / "schemas" / "generation-handoff.schema.json").read_text()
        )
        self.assertEqual([], validate_document(handoff, schema))
        self.assertEqual("awaiting_authorization", handoff["status"])
        self.assertEqual("pending", handoff["authorization"]["state"])
        self.assertTrue(handoff["candidate"]["preserve_original"])

    def test_handoff_rejects_absolute_and_parent_paths(self) -> None:
        for path in ["/tmp/candidate.png", "../candidate.png", "C:\\temp\\candidate.png"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                prepare_generation_handoff(self.request, path)

    def test_authorized_handoff_records_external_result_without_provider_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "hero.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            handoff = prepare_generation_handoff(
                self.request,
                "outputs/candidates/hero.png",
                authorized_by="fixture-user",
                capabilities=self.mock_capabilities,
            )
            completed = record_generation_result(
                handoff,
                candidate,
                provider="fixture-provider",
                model="fixture-model",
            )
        schema = json.loads(
            (ROOT / "schemas" / "generation-handoff.schema.json").read_text()
        )
        self.assertEqual([], validate_document(completed, schema))
        self.assertEqual("completed", completed["status"])
        self.assertEqual("fixture-provider", completed["result"]["provider"])

    def test_manifest_links_normalized_generation_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "hero.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            handoff = prepare_generation_handoff(
                self.request,
                "outputs/candidates/hero.png",
                authorized_by="fixture-user",
                capabilities=self.mock_capabilities,
            )
            completed = record_generation_result(
                handoff,
                candidate,
                provider="fixture-provider",
                model="fixture-model",
            )
            report, metadata = inspect_asset(candidate, self.brief)
            manifest = build_asset_manifest(
                self.brief,
                self.compiled,
                self.request,
                report,
                metadata,
                completed,
            )
        schema = json.loads(
            (ROOT / "schemas" / "asset-manifest.schema.json").read_text()
        )
        self.assertEqual([], validate_document(manifest, schema))
        self.assertEqual("fixture-provider", manifest["generation"]["provider"])
        self.assertIsNotNone(manifest["generation"]["record_sha256"])

    def test_edit_result_hashes_its_input_and_manifest_links_source(self) -> None:
        request = json.loads(json.dumps(self.request))
        request["operation"] = "edit"
        request["input_images"] = [
            {
                "uri": "references/source.png",
                "role": "identity",
                "notes": "fixture edit target",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references" / "source.png"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (320, 240), (20, 30, 40)).save(source)
            expected_source_hash = file_sha256(source)
            candidate = root / "hero.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            handoff = prepare_generation_handoff(
                request,
                "outputs/candidates/hero.png",
                authorized_by="fixture-user",
                capabilities=self.mock_capabilities,
            )
            completed = record_generation_result(
                handoff,
                candidate,
                provider="fixture-provider",
                project_root=root,
            )
            report, metadata = inspect_asset(candidate, self.brief)
            manifest = build_asset_manifest(
                self.brief,
                self.compiled,
                request,
                report,
                metadata,
                completed,
            )
        self.assertEqual(expected_source_hash, completed["result"]["inputs"][0]["sha256"])
        self.assertEqual("references/source.png", manifest["derivation"]["sources"][0]["path"])
        self.assertEqual("reference", manifest["derivation"]["sources"][0]["source_type"])

    def test_manifest_rejects_generation_record_for_a_different_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "hero.png"
            inspected = root / "other.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(generated)
            Image.new("RGB", (1600, 900), (20, 30, 40)).save(inspected)
            handoff = prepare_generation_handoff(
                self.request,
                "outputs/candidates/hero.png",
                authorized_by="fixture-user",
                capabilities=self.mock_capabilities,
            )
            completed = record_generation_result(
                handoff,
                generated,
                provider="fixture-provider",
            )
            report, metadata = inspect_asset(inspected, self.brief)
            with self.assertRaisesRegex(ValueError, "inspected file"):
                build_asset_manifest(
                    self.brief,
                    self.compiled,
                    self.request,
                    report,
                    metadata,
                    completed,
                )

    def test_pending_handoff_cannot_record_a_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "hero.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            handoff = prepare_generation_handoff(
                self.request,
                "outputs/candidates/hero.png",
            )
            with self.assertRaisesRegex(ValueError, "ready"):
                record_generation_result(
                    handoff,
                    candidate,
                    provider="fixture-provider",
                )

    def test_handoff_clis_cover_ready_completed_and_invalid_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = self._write_request(root)
            ready_path = root / "ready.json"
            prepare = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare-generation-handoff.py"),
                    str(request_path),
                    "--candidate",
                    "outputs/candidates/hero.png",
                    "--authorized-by",
                    "fixture-user",
                    "--capabilities",
                    str(ROOT / "config" / "providers" / "mock.json"),
                    "--output",
                    str(ready_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, prepare.returncode, prepare.stderr)
            candidate = root / "hero.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            completed_path = root / "completed.json"
            record = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record-generation-result.py"),
                    str(ready_path),
                    str(candidate),
                    "--provider",
                    "fixture-provider",
                    "--output",
                    str(completed_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, record.returncode, record.stderr)
            self.assertEqual("completed", json.loads(completed_path.read_text())["status"])

            invalid = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare-generation-handoff.py"),
                    str(request_path),
                    "--candidate",
                    "../outside.png",
                    "--output",
                    str(root / "invalid.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, invalid.returncode)
            self.assertIn("project-relative", invalid.stderr)

    def test_promotion_requires_qc_pass_and_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.png"
            Image.new("RGB", (1600, 900), (235, 238, 242)).save(candidate)
            report, metadata = inspect_asset(candidate, self.brief)
            manifest = build_asset_manifest(
                self.brief,
                self.compiled,
                self.request,
                report,
                metadata,
            )
            with self.assertRaisesRegex(ValueError, "qc_passed"):
                promote_asset(
                    candidate,
                    root / "formal.png",
                    manifest,
                    report,
                    self._approval(),
                )

    def test_promotion_copies_without_removing_candidate_and_records_approval(self) -> None:
        manifest_schema = json.loads(
            (ROOT / "schemas" / "asset-manifest.schema.json").read_text()
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, report, manifest = self._reviewed_state(root)
            destination = root / "formal" / "hero.png"
            landed = promote_asset(
                candidate,
                destination,
                manifest,
                report,
                self._approval(),
            )
            self.assertEqual([], validate_document(landed, manifest_schema))
            self.assertEqual("landed", landed["status"])
            self.assertTrue(candidate.exists())
            self.assertTrue(destination.exists())
            self.assertEqual(file_sha256(candidate), file_sha256(destination))
            self.assertEqual("fixture-approver", landed["approvals"][0]["reviewer"])

    def test_promotion_refuses_existing_destination_and_bad_candidate_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, report, manifest = self._reviewed_state(root)
            destination = root / "formal.png"
            Image.new("RGB", (10, 10), (0, 0, 0)).save(destination)
            with self.assertRaises(FileExistsError):
                promote_asset(
                    candidate,
                    destination,
                    manifest,
                    report,
                    self._approval(),
                )
            candidate.write_bytes(b"changed after QC")
            with self.assertRaisesRegex(ValueError, "hash"):
                promote_asset(
                    candidate,
                    root / "other.png",
                    manifest,
                    report,
                    self._approval(),
                )

    def test_promotion_cli_has_success_and_no_overwrite_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, report, manifest = self._reviewed_state(root)
            manifest_path = root / "manifest.json"
            report_path = root / "qc.json"
            approval_path = root / "approval.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report_path.write_text(json.dumps(report), encoding="utf-8")
            approval_path.write_text(json.dumps(self._approval()), encoding="utf-8")
            destination = root / "formal" / "hero.png"
            output_manifest = root / "formal" / "hero.manifest.json"
            command = [
                sys.executable,
                str(ROOT / "scripts" / "promote-asset.py"),
                str(candidate),
                str(destination),
                str(manifest_path),
                str(report_path),
                str(approval_path),
                "--manifest-output",
                str(output_manifest),
            ]
            first = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, first.returncode, first.stderr)
            landed = json.loads(output_manifest.read_text())
            self.assertEqual("landed", landed["status"])
            second = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, second.returncode)
            self.assertIn("already exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
