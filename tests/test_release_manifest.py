from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseManifestTests(unittest.TestCase):
    def test_release_manifest_is_deterministic_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "visual-director"
            built = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build-plugin-package.py"),
                    "--output",
                    str(package),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            self.assertFalse(
                (package / "runtime" / "scripts" / "build-release-manifest.py").exists()
            )

            outputs = []
            for index in range(2):
                manifest = root / f"release-{index}.json"
                checksums = root / f"release-{index}.sha256"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "build-release-manifest.py"),
                        str(package),
                        "--output",
                        str(manifest),
                        "--checksums",
                        str(checksums),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                outputs.append((manifest.read_bytes(), checksums.read_bytes()))

            self.assertEqual(outputs[0], outputs[1])
            document = json.loads(outputs[0][0])
            checksum_bytes = outputs[0][1]
            self.assertEqual("visual-director", document["plugin"]["name"])
            self.assertEqual("0.4.0", document["plugin"]["version"])
            self.assertEqual("WaterTian", document["plugin"]["author"])
            self.assertEqual("WaterTian", document["plugin"]["developer"])
            self.assertGreater(document["package"]["file_count"], 50)
            self.assertEqual(
                hashlib.sha256(checksum_bytes).hexdigest(),
                document["package"]["tree_sha256"],
            )

            repeated = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build-release-manifest.py"),
                    str(package),
                    "--output",
                    str(root / "release-0.json"),
                    "--checksums",
                    str(root / "release-0.sha256"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, repeated.returncode)
            self.assertIn("already exists", repeated.stderr)


if __name__ == "__main__":
    unittest.main()
