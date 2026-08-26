#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_selector import select_cases
from visual_director.compiler import compile_prompt
from visual_director.json_io import atomic_write_json, load_json
from visual_director.selector import score_templates
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a Visual Brief into a provider-neutral prompt.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "templates.json")
    parser.add_argument("--cases", type=Path, default=ROOT / "data" / "cases.json")
    parser.add_argument("--images", type=Path, default=ROOT / "gallery" / "gallery-manifest.json")
    parser.add_argument("--top-cases", type=int, default=3)
    parser.add_argument("--case-selection-output", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        catalog = load_json(args.catalog)
        cases = load_json(args.cases)
        images = load_json(args.images) if args.images.is_file() else None
        brief_schema = load_json(ROOT / "schemas" / "visual-brief.schema.json")
        catalog_schema = load_json(ROOT / "schemas" / "template-catalog.schema.json")
        case_catalog_schema = load_json(ROOT / "schemas" / "case-catalog.schema.json")
        image_schema = load_json(ROOT / "schemas" / "gallery-manifest.schema.json")
        case_selection_schema = load_json(ROOT / "schemas" / "case-selection.schema.json")
        compiled_schema = load_json(ROOT / "schemas" / "compiled-prompt.schema.json")
    except (OSError, ValueError) as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2

    errors = (
        validate_document(brief, brief_schema)
        + validate_document(catalog, catalog_schema)
        + validate_document(cases, case_catalog_schema)
    )
    if images is not None:
        errors += validate_document(images, image_schema)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1

    selection = score_templates(brief, catalog)[0]
    templates = {template["id"]: template for template in catalog["templates"]}
    case_selection = select_cases(
        brief,
        templates[selection["id"]],
        cases,
        top=args.top_cases,
        image_manifest=images,
    )
    case_errors = validate_document(case_selection, case_selection_schema)
    if case_errors:
        for error in case_errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1
    compiled = compile_prompt(
        brief,
        templates[selection["id"]],
        selection,
        case_selection,
    )
    compiled_errors = validate_document(compiled, compiled_schema)
    if compiled_errors:
        for error in compiled_errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1

    if args.output:
        atomic_write_json(args.output, compiled)
        print(f"compiled {brief['asset_id']} to {args.output}")
    else:
        print(json.dumps(compiled, ensure_ascii=False, indent=2))
    if args.case_selection_output:
        atomic_write_json(args.case_selection_output, case_selection)
        print(f"case selection written to {args.case_selection_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
