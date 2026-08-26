#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import atomic_write_json, load_json
from visual_director.provider import MockProviderAdapter, execute_provider
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one normalized provider attempt.")
    parser.add_argument("request", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--attempt-output", type=Path, required=True)
    parser.add_argument("--adapter", choices=["mock"], default="mock")
    parser.add_argument("--mock-mode", choices=["success", "fail", "sleep"], default="success")
    parser.add_argument("--mock-delay", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
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
        request = load_json(args.request)
        _require_valid(request, "generation-request.schema.json")
        adapter = MockProviderAdapter(args.mock_mode, args.mock_delay)
        attempt = execute_provider(
            adapter,
            request,
            args.candidate,
            timeout_seconds=args.timeout_seconds,
        )
        _require_valid(attempt, "provider-attempt.schema.json")
        atomic_write_json(args.attempt_output, attempt)
    except (OSError, ValueError) as error:
        print(f"provider run failed: {error}", file=sys.stderr)
        return 2

    print(f"provider {attempt['status']}: {attempt['attempt_id']} -> {args.attempt_output}")
    return {"succeeded": 0, "failed": 2, "timed_out": 3}[attempt["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
