#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.compositor import compose_exact_canvas
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compose generated layers onto an explicitly exact PNG canvas."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--record-output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
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
        plan = load_json(args.plan)
        _require_valid(plan, "composition-plan.schema.json")
        record = compose_exact_canvas(
            plan,
            args.project_root,
            args.output,
        )
        _require_valid(record, "composition-record.schema.json")
        atomic_write_json(args.record_output, record)
    except (OSError, ValueError) as error:
        print(f"composition failed: {error}", file=sys.stderr)
        return 2
    print(
        f"composed exact canvas {record['output']['width']}x"
        f"{record['output']['height']} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
