from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from PIL import Image

from visual_director.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]


class PublicGalleryTests(unittest.TestCase):
    def test_manifest_covers_only_approved_first_party_assets(self) -> None:
        manifest = json.loads((ROOT / "gallery" / "gallery-manifest.json").read_text())
        schema = json.loads((ROOT / "schemas" / "gallery-manifest.schema.json").read_text())
        cases = json.loads((ROOT / "data" / "cases.json").read_text())
        self.assertEqual([], validate_document(manifest, schema))
        self.assertTrue(manifest["policy"]["first_party_only"])
        self.assertFalse(manifest["policy"]["paid_api"])

        assets = manifest["assets"]
        self.assertEqual(7, len(assets))
        self.assertEqual(
            {asset["image_path"] for asset in assets},
            {path.relative_to(ROOT).as_posix() for path in (ROOT / "gallery" / "images").glob("*.png")},
        )
        case_by_id = {item["id"]: item for item in cases["cases"]}
        self.assertEqual(set(case_by_id), {asset["case_id"] for asset in assets})

        for asset in assets:
            self.assertEqual("approved_public_gallery", asset["status"])
            self.assertFalse(asset["paid_api"])
            self.assertTrue(asset["first_party"])
            image_path = ROOT / asset["image_path"]
            prompt_path = ROOT / asset["prompt_path"]
            self.assertTrue(image_path.is_file())
            self.assertTrue(prompt_path.is_file())
            image_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
            prompt_hash = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
            self.assertEqual(asset["image_sha256"], image_hash)
            self.assertEqual(asset["prompt_sha256"], prompt_hash)
            case = case_by_id[asset["case_id"]]
            self.assertEqual(asset["image_path"], case["image"]["path"])
            self.assertEqual(asset["prompt_path"], case["prompt_path"])
            self.assertEqual(prompt_hash, case["prompt_sha256"])
            with Image.open(image_path) as image:
                self.assertEqual("PNG", image.format)
                self.assertEqual("RGB", image.mode)
                self.assertEqual((asset["width"], asset["height"]), image.size)


if __name__ == "__main__":
    unittest.main()
