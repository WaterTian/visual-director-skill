from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectMetadataTests(unittest.TestCase):
    def test_project_has_exactly_one_author(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual([{"name": "WaterTian"}], pyproject["project"]["authors"])
        self.assertIn(
            "Copyright (c) 2026 WaterTian",
            (ROOT / "LICENSE").read_text(encoding="utf-8"),
        )

        manifest = json.loads(
            (ROOT / "packages" / "visual-director" / ".codex-plugin" / "plugin.json").read_text()
        )
        self.assertEqual({"name": "WaterTian"}, manifest["author"])
        self.assertEqual("WaterTian", manifest["interface"]["developerName"])

    def test_repo_marketplace_points_to_rebuildable_plugin_path(self) -> None:
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        self.assertEqual("visual-director", marketplace["name"])
        self.assertEqual(1, len(marketplace["plugins"]))
        entry = marketplace["plugins"][0]
        self.assertEqual("visual-director", entry["name"])
        self.assertEqual(
            {"source": "local", "path": "./plugins/visual-director"},
            entry["source"],
        )
        self.assertEqual("AVAILABLE", entry["policy"]["installation"])
        self.assertEqual("ON_INSTALL", entry["policy"]["authentication"])


if __name__ == "__main__":
    unittest.main()
