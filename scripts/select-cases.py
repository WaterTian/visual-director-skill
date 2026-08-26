#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_selector import select_cases
from visual_director.json_io import atomic_write_json, load_json
from visual_director.selector import score_templates
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select up to three traceable case references for a Visual Brief."
    )
    parser.add_argument("brief", type=Path)
    parser.add_argument("--templates", type=Path, default=ROOT / "data" / "templates.json")
    parser.add_argument("--cases", type=Path, default=ROOT / "data" / "cases.json")
    parser.add_argument("--images", type=Path, default=ROOT / "gallery" / "gallery-manifest.json")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _require_valid(document: dict, schema_name: str) -> None:
    schema = load_json(ROOT / "schemas" / schema_name)
    errors = validate_document(document, schema)
    if errors:
        summary = "; ".join(f"{error.path}: {error.message}" for error in errors[:8])
        raise ValueError(f"{schema_name} validation failed: {summary}")


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        templates = load_json(args.templates)
        cases = load_json(args.cases)
        images = load_json(args.images) if args.images.is_file() else None
        _require_valid(brief, "visual-brief.schema.json")
        _require_valid(templates, "template-catalog.schema.json")
        _require_valid(cases, "case-catalog.schema.json")
        if images is not None:
            _require_valid(images, "gallery-manifest.schema.json")
        template_selection = score_templates(brief, templates)[0]
        template_by_id = {item["id"]: item for item in templates["templates"]}
        selection = select_cases(
            brief,
            template_by_id[template_selection["id"]],
            cases,
            top=args.top,
            image_manifest=images,
        )
        _require_valid(selection, "case-selection.schema.json")
    except (OSError, ValueError) as error:
        print(f"case selection failed: {error}", file=sys.stderr)
        return 2
    if args.output:
        atomic_write_json(args.output, selection)
        print(f"selected {len(selection['cases'])} cases to {args.output}")
    else:
        print(json.dumps(selection, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
