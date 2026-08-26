from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.free_exact import (
    build_composition_plan,
    build_material_request,
    select_composition_preset,
)
from visual_director.validation import validate_document


class FreeExactPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.brief = json.loads(
            (ROOT / "tests" / "fixtures" / "hero-brief.json").read_text()
        )
        cls.catalog = json.loads(
            (ROOT / "data" / "composition-presets.json").read_text()
        )
        cls.preset = select_composition_preset(
            cls.brief,
            cls.catalog,
            "left-copy-right-product-hero",
        )

    def _material(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            (130, 70, 470, 540),
            radius=50,
            fill=(236, 236, 230, 255),
            outline=(75, 75, 72, 255),
            width=8,
        )
        image.save(path)

    def test_checked_in_preset_catalog_is_valid(self) -> None:
        schema = json.loads(
            (
                ROOT
                / "schemas"
                / "composition-preset-catalog.schema.json"
            ).read_text()
        )
        self.assertEqual([], validate_document(self.catalog, schema))

    def test_hero_preset_compiles_the_verified_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            material = project_root / "materials" / "product.png"
            self._material(material)
            plan = build_composition_plan(
                self.brief,
                self.preset,
                material,
                project_root,
            )
        schema = json.loads(
            (ROOT / "schemas" / "composition-plan.schema.json").read_text()
        )
        self.assertEqual([], validate_document(plan, schema))
        self.assertEqual(
            {"x": 780, "y": 80, "width": 720, "height": 740},
            plan["raster_layers"][0]["box"],
        )
        self.assertEqual(
            [118, 42],
            [item["font_size"] for item in plan["text_layers"]],
        )
        self.assertEqual(
            [576, 576],
            [item["max_width"] for item in plan["text_layers"]],
        )
        self.assertEqual(
            ["AURORA", "Small form. Clear presence."],
            [item["text"] for item in plan["text_layers"]],
        )

    def test_preset_and_material_rejections_are_explicit(self) -> None:
        poster = copy.deepcopy(self.brief)
        poster["deliverable"]["type"] = "poster"
        with self.assertRaisesRegex(ValueError, "does not support"):
            select_composition_preset(
                poster,
                self.catalog,
                "left-copy-right-product-hero",
            )

        square = copy.deepcopy(self.brief)
        square["deliverable"]["width"] = 900
        with self.assertRaisesRegex(ValueError, "aspect ratio"):
            select_composition_preset(
                square,
                self.catalog,
                "left-copy-right-product-hero",
            )

        transparent = copy.deepcopy(self.brief)
        transparent["deliverable"]["transparent_background"] = True
        with self.assertRaisesRegex(ValueError, "transparent_background"):
            select_composition_preset(
                transparent,
                self.catalog,
                "left-copy-right-product-hero",
            )

        too_much_text = copy.deepcopy(self.brief)
        too_much_text["content"]["exact_text"].append("Third line")
        with self.assertRaisesRegex(ValueError, "exact text"):
            select_composition_preset(
                too_much_text,
                self.catalog,
                "left-copy-right-product-hero",
            )

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            opaque = project_root / "opaque.png"
            Image.new("RGB", (600, 600), (255, 255, 255)).save(opaque)
            with self.assertRaisesRegex(ValueError, "alpha channel"):
                build_composition_plan(
                    self.brief,
                    self.preset,
                    opaque,
                    project_root,
                )

    def test_material_request_is_no_paid_api_and_authorization_gated(self) -> None:
        pending = build_material_request(
            self.brief,
            "outputs/run/aurora-launch-hero-material.png",
        )
        ready = build_material_request(
            self.brief,
            "outputs/run/aurora-launch-hero-material.png",
            authorized_by="current-user-request",
        )
        schema = json.loads(
            (ROOT / "schemas" / "material-request.schema.json").read_text()
        )
        self.assertEqual([], validate_document(pending, schema))
        self.assertEqual([], validate_document(ready, schema))
        self.assertEqual("awaiting_authorization", pending["status"])
        self.assertEqual("ready", ready["status"])
        self.assertTrue(ready["provider_policy"]["no_paid_api"])
        self.assertNotIn("AURORA", ready["prompt"])
        self.assertIn("Text: none", ready["prompt"])
        text_in_goal = copy.deepcopy(self.brief)
        text_in_goal["goal"] = "Launch AURORA with an exact headline treatment."
        isolated = build_material_request(
            text_in_goal,
            "outputs/run/aurora-launch-hero-material.png",
        )
        self.assertNotIn("AURORA", isolated["prompt"])
        with self.assertRaisesRegex(ValueError, "project-relative"):
            build_material_request(self.brief, "../outside.png")

    def test_plan_cli_has_success_and_rejection_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            material = project_root / "materials" / "product.png"
            self._material(material)
            output = project_root / "composition-plan.json"
            command = [
                sys.executable,
                str(ROOT / "scripts" / "build-composition-plan.py"),
                str(ROOT / "tests" / "fixtures" / "hero-brief.json"),
                "materials/product.png",
                "--output",
                str(output),
                "--project-root",
                str(project_root),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(output.is_file())

            repeated = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, repeated.returncode)
            self.assertIn("already exists", repeated.stderr)

    def test_staged_pipeline_prepares_resumes_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            output_dir = project_root / "outputs" / "hero-run"
            base = [
                sys.executable,
                str(ROOT / "scripts" / "run-free-exact-pipeline.py"),
                str(ROOT / "tests" / "fixtures" / "hero-brief.json"),
                "--output-dir",
                "outputs/hero-run",
                "--project-root",
                str(project_root),
            ]
            prepared = subprocess.run(
                [*base, "--authorized-by", "current-user-request"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, prepared.returncode, prepared.stderr)
            self.assertIn("pipeline ready", prepared.stdout)
            request = json.loads(
                (output_dir / "material-request.json").read_text()
            )
            case_selection = json.loads(
                (output_dir / "case-selection.json").read_text()
            )
            self.assertEqual([1, 2, 3], request["case_ids"])
            self.assertEqual(
                request["case_ids"],
                [item["id"] for item in case_selection["cases"]],
            )
            self.assertEqual(64, len(request["case_selection_sha256"]))
            self.assertIn("case 1", request["prompt"])
            self.assertIn("Reference isolation", request["prompt"])
            material = project_root / request["candidate"]["relative_path"]
            self._material(material)

            resumed = subprocess.run(
                [*base, "--material", request["candidate"]["relative_path"]],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, resumed.returncode, resumed.stderr)
            self.assertIn("review_required", resumed.stdout)
            final = output_dir / "aurora-launch-hero-exact.png"
            with Image.open(final) as image:
                self.assertEqual((1600, 900), image.size)
            manifest = json.loads(
                (output_dir / "asset-manifest.json").read_text()
            )
            self.assertEqual(
                "exact_canvas_composition",
                manifest["derivation"]["method"],
            )
            self.assertEqual(
                "codex-built-in-imagegen",
                manifest["derivation"]["sources"][0]["provider"],
            )

            repeated = subprocess.run(
                [*base, "--material", request["candidate"]["relative_path"]],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, repeated.returncode)
            self.assertIn("already exist", repeated.stderr)

    def test_pipeline_rejects_case_selection_changed_after_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            output_dir = project_root / "outputs" / "hero-run"
            base = [
                sys.executable,
                str(ROOT / "scripts" / "run-free-exact-pipeline.py"),
                str(ROOT / "tests" / "fixtures" / "hero-brief.json"),
                "--output-dir",
                "outputs/hero-run",
                "--project-root",
                str(project_root),
            ]
            prepared = subprocess.run(
                [*base, "--authorized-by", "current-user-request"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, prepared.returncode, prepared.stderr)
            request = json.loads((output_dir / "material-request.json").read_text())
            selection_path = output_dir / "case-selection.json"
            selection = json.loads(selection_path.read_text())
            selection["cases"][0]["reasons"].append("tampered after authorization")
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            material = project_root / request["candidate"]["relative_path"]
            self._material(material)
            refused = subprocess.run(
                [*base, "--material", request["candidate"]["relative_path"]],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, refused.returncode)
            self.assertIn("case selection do not match", refused.stderr)

    def test_pipeline_refuses_unapproved_material_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            base = [
                sys.executable,
                str(ROOT / "scripts" / "run-free-exact-pipeline.py"),
                str(ROOT / "tests" / "fixtures" / "hero-brief.json"),
                "--output-dir",
                "outputs/hero-run",
                "--project-root",
                str(project_root),
            ]
            prepared = subprocess.run(
                base,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, prepared.returncode, prepared.stderr)
            request_path = (
                project_root / "outputs" / "hero-run" / "material-request.json"
            )
            request = json.loads(request_path.read_text())
            material = project_root / request["candidate"]["relative_path"]
            self._material(material)
            refused = subprocess.run(
                [*base, "--material", request["candidate"]["relative_path"]],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, refused.returncode)
            self.assertIn("not authorized", refused.stderr)

            authorized = subprocess.run(
                [*base, "--authorized-by", "current-user-request"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, authorized.returncode, authorized.stderr)
            self.assertIn("pipeline ready", authorized.stdout)
            resumed = subprocess.run(
                [*base, "--material", request["candidate"]["relative_path"]],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, resumed.returncode, resumed.stderr)


if __name__ == "__main__":
    unittest.main()
