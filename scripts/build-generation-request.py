#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.generation import build_generation_request
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a provider-neutral GenerationRequest.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("compiled_prompt", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        compiled = load_json(args.compiled_prompt)
        request = build_generation_request(brief, compiled)
        schema = load_json(ROOT / "schemas" / "generation-request.schema.json")
        errors = validate_document(request, schema)
    except (OSError, ValueError) as error:
        print(f"request build failed: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1
    if args.output:
        atomic_write_json(args.output, request)
        print(f"built request {request['request_id']} at {args.output}")
    else:
        print(json.dumps(request, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

