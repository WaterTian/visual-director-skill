#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_search import search_cases
from visual_director.json_io import load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search the reviewed first-party Visual Director example catalog.")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "cases.json")
    parser.add_argument("--category")
    parser.add_argument("--style", action="append", default=[])
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--id", type=int, action="append", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--full-prompt", action="store_true", help="Include the local prompt document path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        catalog = load_json(args.catalog)
        schema = load_json(ROOT / "schemas" / "case-catalog.schema.json")
    except (OSError, ValueError) as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2
    errors = validate_document(catalog, schema)
    if errors:
        for error in errors[:10]:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1
    results = search_cases(
        catalog,
        query=args.query,
        category=args.category,
        styles=args.style,
        scenes=args.scene,
        case_ids=args.id,
        limit=args.limit,
        include_prompt=args.full_prompt,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
