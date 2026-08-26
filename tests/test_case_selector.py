from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_selector import select_cases
from visual_director.selector import score_templates
from visual_director.validation import validate_document


class CaseSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.templates = json.loads((ROOT / "data" / "templates.json").read_text())
        cls.template_by_id = {item["id"]: item for item in cls.templates["templates"]}
        cls.cases = json.loads((ROOT / "data" / "cases.json").read_text())
        cls.images = json.loads((ROOT / "gallery" / "gallery-manifest.json").read_text())
        cls.schema = json.loads((ROOT / "schemas" / "case-selection.schema.json").read_text())

    def _select(self, filename: str) -> dict:
        brief = json.loads((ROOT / "tests" / "fixtures" / filename).read_text())
        template_result = score_templates(brief, self.templates)[0]
        return select_cases(
            brief,
            self.template_by_id[template_result["id"]],
            self.cases,
            image_manifest=self.images,
        )

    def test_ranking_is_stable_for_supported_briefs(self) -> None:
        expected = {
            "character-edit-brief.json": [2, 3, 4],
            "exploded-product-diagram-brief.json": [5, 1, 4],
            "fashion-lookbook-brief.json": [4, 3, 7],
            "hero-brief.json": [1, 2, 4],
            "product-brief.json": [1, 3, 4],
            "product-background-edit-brief.json": [1, 3, 2],
            "quiet-editorial-portrait-brief.json": [6, 3, 7],
            "realistic-motion-editorial-brief.json": [7, 3, 4],
        }
        for filename, ids in expected.items():
            with self.subTest(filename=filename):
                result = self._select(filename)
                self.assertEqual([], validate_document(result, self.schema))
                self.assertEqual(ids, [item["id"] for item in result["cases"]])
                self.assertEqual(result, self._select(filename))

    def test_output_is_first_party_traceable_and_excludes_selection_text(self) -> None:
        result = self._select("hero-brief.json")
        self.assertEqual("first-party", result["source"]["kind"])
        self.assertEqual("local_text_and_metadata", result["policy"]["selection_basis"])
        self.assertTrue(result["policy"]["visual_review_required"])
        self.assertFalse(result["policy"]["prompt_text_included"])
        serialized = json.dumps(result, ensure_ascii=False)
        prompt_hashes: set[str] = set()
        image_hashes: set[str] = set()
        for item in result["cases"]:
            source = self._case_by_id(item["id"])
            self.assertNotIn(source["selection_text"], serialized)
            self.assertEqual(item["score"], sum(item["score_breakdown"].values()))
            self.assertTrue(item["structure_cues"])
            self.assertTrue(item["image"]["manifest_verified"])
            self.assertTrue((ROOT / item["image"]["path"]).is_file())
            prompt_hashes.add(item["prompt_sha256"])
            image_hashes.add(item["image"]["sha256"])
        self.assertEqual(3, len(prompt_hashes))
        self.assertEqual(3, len(image_hashes))

    def test_cli_writes_valid_selection_and_rejects_invalid_brief(self) -> None:
        script = ROOT / "scripts" / "select-cases.py"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "case-selection.json"
            success = subprocess.run(
                [sys.executable, str(script), str(ROOT / "tests" / "fixtures" / "hero-brief.json"), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, success.returncode, success.stderr)
            self.assertEqual([], validate_document(json.loads(output.read_text()), self.schema))
        failure = subprocess.run(
            [sys.executable, str(script), str(ROOT / "tests" / "fixtures" / "invalid" / "missing-width.json")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(2, failure.returncode)
        self.assertIn("case selection failed", failure.stderr)

    def _case_by_id(self, case_id: int) -> dict:
        return next(item for item in self.cases["cases"] if item["id"] == case_id)


if __name__ == "__main__":
    unittest.main()
