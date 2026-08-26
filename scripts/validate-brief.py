#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Visual Brief JSON files.")
    parser.add_argument("briefs", nargs="+", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=ROOT / "schemas" / "visual-brief.schema.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema = load_json(args.schema)
    except (OSError, ValueError) as error:
        print(f"schema error: {error}", file=sys.stderr)
        return 2

    failed = False
    for brief_path in args.briefs:
        try:
            brief = load_json(brief_path)
            errors = validate_document(brief, schema)
        except (OSError, ValueError) as error:
            print(f"FAIL {brief_path}: {error}")
            failed = True
            continue

        if not errors:
            print(f"PASS {brief_path}")
            continue

        failed = True
        print(f"FAIL {brief_path}")
        for error in errors:
            print(f"  {error.path}: {error.message} [{error.rule}]")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

