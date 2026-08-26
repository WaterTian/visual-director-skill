#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SOURCE = ROOT / "packages" / "visual-director"
SKILL_SOURCE = ROOT / ".agents" / "skills" / "visual-director"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a clean, portable Visual Director Codex Plugin directory.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "plugins" / "visual-director",
        help="New output directory; must not already exist",
    )
    return parser.parse_args()


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build_plugin(output: Path) -> None:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    if output == ROOT or ROOT in output.parents and output.name in {"src", "scripts", "schemas"}:
        raise ValueError(f"unsafe output path: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".visual-director-plugin-", dir=output.parent))
    try:
        _copy_file(
            PLUGIN_SOURCE / ".codex-plugin" / "plugin.json",
            temporary / ".codex-plugin" / "plugin.json",
        )
        _copy_file(ROOT / "LICENSE", temporary / "LICENSE")
        shutil.copytree(SKILL_SOURCE, temporary / "skills" / "visual-director")

        runtime = temporary / "runtime"
        for name in ("pyproject.toml", "uv.lock"):
            _copy_file(ROOT / name, runtime / name)
        shutil.copytree(ROOT / "src", runtime / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ROOT / "schemas", runtime / "schemas")
        shutil.copytree(ROOT / "templates", runtime / "templates")
        _copy_file(ROOT / "data" / "templates.json", runtime / "data" / "templates.json")
        _copy_file(ROOT / "data" / "cases.json", runtime / "data" / "cases.json")
        _copy_file(
            ROOT / "data" / "composition-presets.json",
            runtime / "data" / "composition-presets.json",
        )
        shutil.copytree(ROOT / "config" / "providers", runtime / "config" / "providers")
        _copy_file(
            ROOT / "tests" / "fixtures" / "hero-brief.json",
            runtime / "examples" / "hero-brief.json",
        )
        runtime_scripts = runtime / "scripts"
        excluded_scripts = {Path(__file__).name, "build-release-manifest.py"}
        for script in sorted((ROOT / "scripts").glob("*.py")):
            if script.name not in excluded_scripts:
                _copy_file(script, runtime_scripts / script.name)
        temporary.replace(output)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> int:
    args = parse_args()
    try:
        build_plugin(args.output)
    except (OSError, ValueError) as error:
        print(f"plugin build failed: {error}", file=sys.stderr)
        return 2
    print(f"built plugin: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
