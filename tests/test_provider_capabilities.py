from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.capabilities import request_capability_blockers
from visual_director.compiler import compile_prompt
from visual_director.generation import build_generation_request
from visual_director.handoff import prepare_generation_handoff
from visual_director.selector import score_templates
from visual_director.validation import validate_document


class ProviderCapabilitiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "provider-capabilities.schema.json").read_text())
        brief = json.loads((ROOT / "tests" / "fixtures" / "hero-brief.json").read_text())
        catalog = json.loads((ROOT / "data" / "templates.json").read_text())
        selection = score_templates(brief, catalog)[0]
        template = next(item for item in catalog["templates"] if item["id"] == selection["id"])
        cls.request = build_generation_request(brief, compile_prompt(brief, template, selection))

    def test_checked_in_provider_capabilities_are_valid(self) -> None:
        paths = sorted((ROOT / "config" / "providers").glob("*.json"))
        self.assertEqual(2, len(paths))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual([], validate_document(json.loads(path.read_text()), self.schema))

    def test_capability_check_cli_reports_blocked_and_compatible_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            request_path = temporary / "request.json"
            request_path.write_text(json.dumps(self.request))
            script = str(ROOT / "scripts" / "check-provider-capabilities.py")
            blocked = subprocess.run(
                [sys.executable, script, str(request_path), str(ROOT / "config" / "providers" / "codex-built-in-imagegen.json")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, blocked.returncode, blocked.stderr)
            self.assertFalse(json.loads(blocked.stdout)["compatible"])
            compatible = subprocess.run(
                [sys.executable, script, str(request_path), str(ROOT / "config" / "providers" / "mock.json")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, compatible.returncode, compatible.stderr)
            self.assertTrue(json.loads(compatible.stdout)["compatible"])
            request_path.write_text("{}")
            invalid = subprocess.run(
                [sys.executable, script, str(request_path), str(ROOT / "config" / "providers" / "mock.json")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, invalid.returncode)
            self.assertIn("capability check failed", invalid.stderr)

    def test_exact_mock_provider_passes_preflight(self) -> None:
        capabilities = json.loads((ROOT / "config" / "providers" / "mock.json").read_text())
        self.assertEqual([], request_capability_blockers(self.request, capabilities))

    def test_unverified_dimensions_block_authorized_handoff(self) -> None:
        capabilities = json.loads((ROOT / "config" / "providers" / "codex-built-in-imagegen.json").read_text())
        blockers = request_capability_blockers(self.request, capabilities)
        self.assertTrue(any("cannot guarantee exact 1600x900" in item for item in blockers))
        with self.assertRaisesRegex(ValueError, "capability preflight"):
            prepare_generation_handoff(self.request, "outputs/candidates/hero.png", authorized_by="fixture-user", capabilities=capabilities)
        experimental = prepare_generation_handoff(
            self.request,
            "outputs/candidates/hero.png",
            authorized_by="fixture-user",
            capabilities=capabilities,
            unverified_dimension_exception="single built-in smoke candidate; actual dimensions must pass QC",
        )
        self.assertEqual("ready", experimental["status"])
        self.assertEqual(1, len(experimental["capability_blockers"]))

    def test_authorized_handoff_requires_a_capability_record(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires provider capabilities"):
            prepare_generation_handoff(self.request, "outputs/candidates/hero.png", authorized_by="fixture-user")

    def test_unverified_dimension_exception_cli_requires_reason(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.json"
            request_path.write_text(json.dumps(self.request), encoding="utf-8")
            base = [
                sys.executable,
                str(ROOT / "scripts" / "prepare-generation-handoff.py"),
                str(request_path),
                "--candidate", "outputs/candidates/hero.png",
                "--authorized-by", "fixture-user",
                "--capabilities", str(ROOT / "config" / "providers" / "codex-built-in-imagegen.json"),
                "--accept-unverified-dimensions",
            ]
            missing = subprocess.run([*base, "--output", str(root / "missing.json")], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(2, missing.returncode)
            self.assertIn("--exception-reason is required", missing.stderr)
            output = root / "ready.json"
            accepted = subprocess.run(
                [*base, "--exception-reason", "fixture smoke candidate; actual dimensions require QC", "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, accepted.returncode, accepted.stderr)
            handoff = json.loads(output.read_text())
            schema = json.loads((ROOT / "schemas" / "generation-handoff.schema.json").read_text())
            self.assertEqual([], validate_document(handoff, schema))


if __name__ == "__main__":
    unittest.main()
