from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.validation import validate_document


class VisualBriefValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "visual-brief.schema.json").read_text())

    def test_twenty_valid_fixtures(self) -> None:
        valid_paths = sorted((ROOT / "tests" / "fixtures").glob("*.json"))
        self.assertEqual(20, len(valid_paths))
        for path in valid_paths:
            with self.subTest(path=path.name):
                document = json.loads(path.read_text())
                self.assertEqual([], validate_document(document, self.schema))
                self.assertTrue(document["content"]["must_include"])
                self.assertTrue(document["content"]["must_avoid"])

    def test_invalid_fixtures_report_field_paths(self) -> None:
        expected_paths = {
            "missing-width.json": "$.deliverable.width",
            "empty-exact-text.json": "$.content.exact_text[0]",
            "bad-format.json": "$.deliverable.format",
        }
        for filename, expected_path in expected_paths.items():
            with self.subTest(filename=filename):
                document = json.loads(
                    (ROOT / "tests" / "fixtures" / "invalid" / filename).read_text()
                )
                errors = validate_document(document, self.schema)
                self.assertTrue(errors)
                self.assertIn(expected_path, {error.path for error in errors})

    def test_transparent_jpeg_is_rejected_before_generation(self) -> None:
        document = json.loads(
            (ROOT / "tests" / "fixtures" / "hero-brief.json").read_text()
        )
        document["deliverable"]["format"] = "jpeg"
        document["deliverable"]["transparent_background"] = True
        errors = validate_document(document, self.schema)
        self.assertIn("$.deliverable.format", {error.path for error in errors})


if __name__ == "__main__":
    unittest.main()
