#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.capabilities import request_capability_blockers, suggest_compatible_sizes
from visual_director.json_io import load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a GenerationRequest against provider capabilities.")
    parser.add_argument("request", type=Path)
    parser.add_argument("capabilities", type=Path)
    parser.add_argument("--suggest", type=int, default=3)
    return parser.parse_args()


def _load_valid(path: Path, schema_name: str) -> dict:
    document = load_json(path)
    schema = load_json(ROOT / "schemas" / schema_name)
    errors = validate_document(document, schema)
    if errors:
        summary = "; ".join(f"{error.path}: {error.message}" for error in errors[:8])
        raise ValueError(f"{path}: {summary}")
    return document


def main() -> int:
    args = parse_args()
    try:
        request = _load_valid(args.request, "generation-request.schema.json")
        capabilities = _load_valid(
            args.capabilities,
            "provider-capabilities.schema.json",
        )
        blockers = request_capability_blockers(request, capabilities)
        suggestions = (
            suggest_compatible_sizes(request, capabilities, limit=args.suggest)
            if blockers
            else []
        )
    except (OSError, ValueError) as error:
        print(f"capability check failed: {error}", file=sys.stderr)
        return 2

    result = {
        "provider": capabilities["provider"],
        "model": capabilities["model"],
        "compatible": not blockers,
        "blockers": blockers,
        "suggested_sizes": suggestions,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
