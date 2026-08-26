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

from visual_director.asset_qc import file_sha256
from visual_director.asset_qc import inspect_asset
from visual_director.compiler import compile_prompt
from visual_director.compositor import compose_exact_canvas
from visual_director.generation import build_generation_request
from visual_director.manifest import build_asset_manifest
from visual_director.selector import score_templates
from visual_director.validation import validate_document


class ExactCanvasCompositorTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict]:
        source = root / "inputs" / "product.png"
        source.parent.mkdir(parents=True)
        image = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            (80, 50, 320, 350),
            radius=36,
            fill=(232, 232, 226, 255),
            outline=(70, 70, 68, 255),
            width=6,
        )
        image.save(source)
        plan = {
            "version": "0.1",
            "asset_id": "aurora-launch-hero",
            "canvas": {
                "width": 1600,
                "height": 900,
                "format": "png",
                "transparent_background": False,
                "background": "#F5F2EA",
            },
            "raster_layers": [
                {
                    "source_path": "inputs/product.png",
                    "source_sha256": file_sha256(source),
                    "source_type": "generated",
                    "provider": "mock",
                    "model": "fixture-v1",
                    "role": "generated product material",
                    "trim_transparent": True,
                    "fit": "contain",
                    "box": {"x": 900, "y": 120, "width": 560, "height": 660},
                }
            ],
            "text_layers": [
                {
                    "text": "AURORA",
                    "x": 140,
                    "y": 320,
                    "font_size": 94,
                    "max_width": 620,
                    "fill": "#242422",
                    "anchor": "lt",
                    "font_path": None,
                },
                {
                    "text": "Small form. Clear presence.",
                    "x": 145,
                    "y": 450,
                    "font_size": 38,
                    "max_width": 620,
                    "fill": "#585650",
                    "anchor": "lt",
                    "font_path": None,
                },
            ],
        }
        return source, plan

    def test_composition_is_exact_traceable_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            source, plan = self._fixture(project_root)
            source_sha256 = file_sha256(source)
            output = project_root / "outputs" / "hero.png"
            record = compose_exact_canvas(plan, project_root, output)

            with Image.open(output) as image:
                self.assertEqual((1600, 900), image.size)
                self.assertEqual("RGB", image.mode)
            self.assertEqual(source_sha256, file_sha256(source))
            self.assertEqual(1, len(record["raster_transforms"]))
            self.assertTrue(record["raster_transforms"][0]["resampled"])
            self.assertEqual(
                {"x": 80, "y": 50, "width": 241, "height": 301},
                record["raster_transforms"][0]["source_crop"],
            )
            self.assertEqual(
                ["AURORA", "Small form. Clear presence."],
                [item["text"] for item in record["text_layers"]],
            )
            schema = json.loads(
                (ROOT / "schemas" / "composition-record.schema.json").read_text()
            )
            self.assertEqual([], validate_document(record, schema))

    def test_composition_rejects_hash_mismatch_path_escape_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            _, plan = self._fixture(project_root)
            output = project_root / "outputs" / "hero.png"

            bad_hash = copy.deepcopy(plan)
            bad_hash["raster_layers"][0]["source_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                compose_exact_canvas(bad_hash, project_root, output)

            escaped = copy.deepcopy(plan)
            escaped["raster_layers"][0]["source_path"] = "../product.png"
            with self.assertRaisesRegex(ValueError, "project-relative"):
                compose_exact_canvas(escaped, project_root, output)

            compose_exact_canvas(plan, project_root, output)
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                compose_exact_canvas(plan, project_root, output)

    def test_composition_rejects_text_that_overflows_its_preset_slot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            _, plan = self._fixture(project_root)
            plan["text_layers"][0]["max_width"] = 10
            with self.assertRaisesRegex(ValueError, "does not fit"):
                compose_exact_canvas(
                    plan,
                    project_root,
                    project_root / "outputs" / "hero.png",
                )

    def test_manifest_links_composition_record_and_generated_source(self) -> None:
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        catalog = json.loads((ROOT / "data" / "templates.json").read_text())
        selection = score_templates(brief, catalog)[0]
        template = next(
            item for item in catalog["templates"] if item["id"] == selection["id"]
        )
        compiled = compile_prompt(brief, template, selection)
        request = build_generation_request(brief, compiled)
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            _, plan = self._fixture(project_root)
            output = project_root / "outputs" / "hero.png"
            composition_record = compose_exact_canvas(plan, project_root, output)
            report, metadata = inspect_asset(output, brief)
            manifest = build_asset_manifest(
                brief,
                compiled,
                request,
                report,
                metadata,
                composition_record=composition_record,
            )
        schema = json.loads(
            (ROOT / "schemas" / "asset-manifest.schema.json").read_text()
        )
        self.assertEqual([], validate_document(manifest, schema))
        self.assertEqual("exact_canvas_composition", manifest["derivation"]["method"])
        self.assertEqual("mock", manifest["derivation"]["sources"][0]["provider"])

    def test_cli_covers_success_and_invalid_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            _, plan = self._fixture(project_root)
            plan_path = project_root / "composition-plan.json"
            plan_path.write_text(json.dumps(plan))
            output = project_root / "outputs" / "hero.png"
            record = project_root / "outputs" / "composition-record.json"
            command = [
                sys.executable,
                str(ROOT / "scripts" / "compose-exact-canvas.py"),
                str(plan_path),
                str(output),
                "--record-output",
                str(record),
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
            self.assertIn("1600x900", result.stdout)
            self.assertTrue(record.is_file())

            invalid_path = project_root / "invalid-plan.json"
            invalid_path.write_text("{}")
            invalid = subprocess.run(
                [
                    *command[:2],
                    str(invalid_path),
                    str(project_root / "outputs" / "invalid.png"),
                    *command[4:],
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, invalid.returncode)
            self.assertIn("composition failed", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
