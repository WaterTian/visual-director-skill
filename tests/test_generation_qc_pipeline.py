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

from visual_director.asset_qc import inspect_asset
from visual_director.compiler import compile_prompt
from visual_director.generation import build_generation_request
from visual_director.manifest import build_asset_manifest
from visual_director.selector import score_templates
from visual_director.validation import validate_document
from visual_director.visual_review import apply_visual_review


class GenerationQCPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "data" / "templates.json").read_text())
        cls.templates = {item["id"]: item for item in cls.catalog["templates"]}

    def _compile(self, brief: dict) -> tuple[dict, dict]:
        selection = score_templates(brief, self.catalog)[0]
        compiled = compile_prompt(brief, self.templates[selection["id"]], selection)
        return compiled, build_generation_request(brief, compiled)

    def test_generation_request_is_provider_neutral_and_edit_safe(self) -> None:
        brief = json.loads(
            (ROOT / "tests" / "fixtures" / "character-edit-brief.json").read_text()
        )
        _, request = self._compile(brief)
        schema = json.loads((ROOT / "schemas" / "generation-request.schema.json").read_text())
        self.assertEqual([], validate_document(request, schema))
        self.assertEqual("edit", request["operation"])
        self.assertIsNone(request["provider"]["name"])
        self.assertIsNone(request["provider"]["model"])
        self.assertEqual("identity", request["input_images"][0]["role"])
        self.assertTrue(any("Preserve face" in item for item in request["invariants"]))

    def test_file_qc_passes_metadata_and_requires_visual_review(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            Image.new("RGB", (1600, 900), (240, 240, 240)).save(candidate)
            report, metadata = inspect_asset(candidate, brief)
        schema = json.loads((ROOT / "schemas" / "qc-report.schema.json").read_text())
        self.assertEqual([], validate_document(report, schema))
        self.assertEqual("review_required", report["overall_status"])
        self.assertTrue(all(item["status"] == "pass" for item in report["automatic_checks"]))
        self.assertEqual(1600, metadata["width"])
        self.assertIn(
            'exact text: "AURORA"',
            {item["requirement"] for item in report["visual_checks"]},
        )

    def test_file_qc_rejects_wrong_dimensions(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            Image.new("RGB", (800, 800), (240, 240, 240)).save(candidate)
            report, _ = inspect_asset(candidate, brief)
        self.assertEqual("fail", report["overall_status"])
        failed = {item["id"] for item in report["automatic_checks"] if item["status"] == "fail"}
        self.assertIn("dimensions", failed)
        self.assertIn("aspect-ratio", failed)

    def test_manifest_is_traceable_and_not_approved(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        compiled, request = self._compile(brief)
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            Image.new("RGB", (1600, 900), (240, 240, 240)).save(candidate)
            report, metadata = inspect_asset(candidate, brief)
        manifest = build_asset_manifest(brief, compiled, request, report, metadata)
        schema = json.loads((ROOT / "schemas" / "asset-manifest.schema.json").read_text())
        self.assertEqual([], validate_document(manifest, schema))
        self.assertEqual("candidate", manifest["status"])
        self.assertEqual([], manifest["approvals"])
        self.assertEqual("direct", manifest["derivation"]["method"])

    def test_complete_visual_review_can_reach_qc_passed(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        compiled, request = self._compile(brief)
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            Image.new("RGB", (1600, 900), (240, 240, 240)).save(candidate)
            report, metadata = inspect_asset(candidate, brief)
        review = {
            "version": "0.1",
            "asset_id": brief["asset_id"],
            "reviewer": "fixture-reviewer",
            "checks": [
                {
                    "requirement": item["requirement"],
                    "status": "pass",
                    "evidence": "fixture evidence",
                }
                for item in report["visual_checks"]
            ],
        }
        review_schema = json.loads((ROOT / "schemas" / "visual-review.schema.json").read_text())
        self.assertEqual([], validate_document(review, review_schema))
        reviewed_report = apply_visual_review(report, review)
        self.assertEqual("pass", reviewed_report["overall_status"])
        manifest = build_asset_manifest(brief, compiled, request, reviewed_report, metadata)
        self.assertEqual("qc_passed", manifest["status"])

    def test_visual_failure_blocks_asset(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            Image.new("RGB", (1600, 900), (240, 240, 240)).save(candidate)
            report, _ = inspect_asset(candidate, brief)
        first = report["visual_checks"][0]["requirement"]
        reviewed = apply_visual_review(
            report,
            {
                "version": "0.1",
                "asset_id": brief["asset_id"],
                "reviewer": "fixture-reviewer",
                "checks": [
                    {"requirement": first, "status": "fail", "evidence": "required item missing"}
                ],
            },
        )
        self.assertEqual("fail", reviewed["overall_status"])
        self.assertTrue(any(first in blocker for blocker in reviewed["blockers"]))

    def test_cli_dry_run_writes_all_contracts(self) -> None:
        brief_path = ROOT / "tests" / "fixtures" / "hero-brief.json"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.png"
            output_dir = root / "run"
            Image.new("RGB", (1600, 900), (240, 240, 240)).save(candidate)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run-dry-pipeline.py"),
                    str(brief_path),
                    str(candidate),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("review_required", result.stdout)
            self.assertEqual(
                {
                    "asset-manifest.json",
                    "case-selection.json",
                    "compiled-prompt.json",
                    "generation-request.json",
                    "qc-report.json",
                },
                {path.name for path in output_dir.iterdir()},
            )


if __name__ == "__main__":
    unittest.main()
