#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.handoff import record_generation_result
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a completed external generation without provider-specific response fields.")
    parser.add_argument("handoff", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        handoff = load_json(args.handoff)
        schema = load_json(ROOT / "schemas" / "generation-handoff.schema.json")
        input_errors = validate_document(handoff, schema)
        if input_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in input_errors[:8])
            raise ValueError(summary)
        completed = record_generation_result(
            handoff,
            args.candidate,
            provider=args.provider,
            model=args.model,
            project_root=args.project_root,
        )
        output_errors = validate_document(completed, schema)
        if output_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in output_errors[:8])
            raise ValueError(summary)
        atomic_write_json(args.output, completed)
    except (OSError, ValueError) as error:
        print(f"generation result recording failed: {error}", file=sys.stderr)
        return 2
    print(f"generation completed: {completed['handoff_id']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
