from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_selector import select_cases
from visual_director.compiler import compile_prompt
from visual_director.selector import score_templates
from visual_director.validation import validate_document


class SelectorCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "data" / "templates.json").read_text())
        cls.templates = {item["id"]: item for item in cls.catalog["templates"]}
        cls.cases = json.loads((ROOT / "data" / "cases.json").read_text())
        cls.images = json.loads((ROOT / "gallery" / "gallery-manifest.json").read_text())
        cls.compiled_schema = json.loads((ROOT / "schemas" / "compiled-prompt.schema.json").read_text())

    def test_top_selection_is_stable_for_supported_fixtures(self) -> None:
        expected = {
            "character-edit-brief.json": "character-design-sheet",
            "fashion-lookbook-brief.json": "realistic-fashion-lookbook",
            "hero-brief.json": "product-commerce-visual",
            "product-brief.json": "product-commerce-visual",
            "product-background-edit-brief.json": "product-commerce-visual",
        }
        for filename, template_id in expected.items():
            with self.subTest(filename=filename):
                brief = json.loads((ROOT / "tests" / "fixtures" / filename).read_text())
                results = score_templates(brief, self.catalog)
                self.assertEqual(template_id, results[0]["id"])
                self.assertEqual(results, score_templates(brief, self.catalog))
                self.assertEqual(results[0]["score"], sum(results[0]["score_breakdown"].values()))

    def test_compiler_preserves_hard_constraints(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        selection = score_templates(brief, self.catalog)[0]
        case_selection = select_cases(
            brief,
            self.templates[selection["id"]],
            self.cases,
            image_manifest=self.images,
        )
        compiled = compile_prompt(brief, self.templates[selection["id"]], selection, case_selection)
        self.assertEqual([], validate_document(compiled, self.compiled_schema))
        for value in brief["content"].get("exact_text", []):
            self.assertIn(f'"{value}"', compiled["prompt"])
        for value in brief["content"]["must_include"] + brief["content"]["must_avoid"]:
            self.assertIn(value, compiled["prompt"])
        self.assertEqual(brief["deliverable"]["width"], compiled["hard_constraints"]["width"])
        self.assertEqual(3, len(compiled["case_references"]))
        self.assertIn("Reference isolation", compiled["prompt"])
        self.assertIn("case 1", compiled["prompt"])
        self.assertNotIn(case_selection["cases"][0]["title"], compiled["prompt"])
        source = next(item for item in self.cases["cases"] if item["id"] == case_selection["cases"][0]["id"])
        self.assertNotIn(source["selection_text"], compiled["prompt"])
        self.assertEqual("first-party-example-catalog", compiled["sources"][1]["type"])

    def test_product_edit_keeps_input_as_visual_authority(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "product-background-edit-brief.json").read_text())
        result = score_templates(brief, self.catalog)[0]
        case_selection = select_cases(brief, self.templates[result["id"]], self.cases, image_manifest=self.images)
        compiled = compile_prompt(brief, self.templates[result["id"]], result, case_selection)
        self.assertIn("audit-only for this edit", compiled["prompt"])
        self.assertIn("sole visual authority", compiled["prompt"])
        self.assertNotIn("Structural references (generic cues only)", compiled["prompt"])


if __name__ == "__main__":
    unittest.main()
