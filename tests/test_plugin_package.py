from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginPackageTests(unittest.TestCase):
    def test_clean_plugin_build_has_only_first_party_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "visual-director"
            command = [sys.executable, str(ROOT / "scripts" / "build-plugin-package.py"), "--output", str(output)]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual({".codex-plugin", "LICENSE", "runtime", "skills"}, {path.name for path in output.iterdir()})
            manifest = json.loads((output / ".codex-plugin" / "plugin.json").read_text())
            self.assertEqual("WaterTian", manifest["author"]["name"])
            self.assertEqual("WaterTian", manifest["interface"]["developerName"])
            self.assertTrue((output / "skills" / "visual-director" / "SKILL.md").is_file())
            self.assertTrue((output / "runtime" / "scripts" / "select-cases.py").is_file())
            self.assertTrue((output / "runtime" / "scripts" / "run-free-exact-pipeline.py").is_file())
            self.assertTrue((output / "runtime" / "schemas" / "gallery-manifest.schema.json").is_file())
            case_catalog = json.loads((output / "runtime" / "data" / "cases.json").read_text())
            self.assertEqual(13, len(case_catalog["cases"]))
            self.assertTrue(all(item["status"] == "approved_public_gallery" for item in case_catalog["cases"]))
            provider_names = {path.name for path in (output / "runtime" / "config" / "providers").glob("*.json")}
            self.assertEqual({"codex-built-in-imagegen.json", "mock.json"}, provider_names)
            forbidden_directories = {".venv", "__pycache__", "outputs", "work"}
            self.assertFalse(any(path.is_dir() and path.name in forbidden_directories for path in output.rglob("*")))
            for path in output.rglob("*"):
                self.assertNotIn(path.suffix.lower(), {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"})
                if path.is_file() and path.suffix in {".json", ".md", ".py", ".toml"}:
                    self.assertNotIn(str(ROOT), path.read_text(encoding="utf-8"))
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(2, second.returncode)
            self.assertIn("already exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
