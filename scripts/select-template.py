#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import load_json
from visual_director.selector import score_templates
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select explainable Visual Director templates.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "templates.json")
    parser.add_argument("--top", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        brief_schema = load_json(ROOT / "schemas" / "visual-brief.schema.json")
        catalog = load_json(args.catalog)
        catalog_schema = load_json(ROOT / "schemas" / "template-catalog.schema.json")
    except (OSError, ValueError) as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2
    errors = validate_document(brief, brief_schema) + validate_document(catalog, catalog_schema)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1
    results = score_templates(brief, catalog)[: max(1, args.top)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

