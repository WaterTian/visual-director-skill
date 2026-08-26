#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.free_exact import (
    build_composition_plan,
    select_composition_preset,
)
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a Visual Brief and transparent material into a CompositionPlan."
    )
    parser.add_argument("brief", type=Path)
    parser.add_argument("material", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--presets",
        type=Path,
        default=ROOT / "data" / "composition-presets.json",
    )
    parser.add_argument(
        "--preset",
        default="left-copy-right-product-hero",
    )
    parser.add_argument("--provider", default="codex-built-in-imagegen")
    parser.add_argument("--model")
    parser.add_argument("--font-path")
    return parser.parse_args()


def _require_valid(document: dict, schema_name: str) -> None:
    schema = load_json(ROOT / "schemas" / schema_name)
    errors = validate_document(document, schema)
    if errors:
        summary = "; ".join(
            f"{error.path}: {error.message}" for error in errors[:8]
        )
        raise ValueError(f"{schema_name} validation failed: {summary}")


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        catalog = load_json(args.presets)
        _require_valid(brief, "visual-brief.schema.json")
        _require_valid(catalog, "composition-preset-catalog.schema.json")
        preset = select_composition_preset(brief, catalog, args.preset)
        material = (
            args.material
            if args.material.is_absolute()
            else args.project_root / args.material
        )
        plan = build_composition_plan(
            brief,
            preset,
            material,
            args.project_root,
            provider=args.provider,
            model=args.model,
            font_path=args.font_path,
        )
        _require_valid(plan, "composition-plan.schema.json")
        if args.output.exists():
            raise FileExistsError(f"output already exists: {args.output}")
        atomic_write_json(args.output, plan)
    except (OSError, ValueError) as error:
        print(f"composition plan build failed: {error}", file=sys.stderr)
        return 2
    print(f"built composition plan {plan['asset_id']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
