#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.asset_qc import inspect_asset
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic file QC for a candidate image.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brief = load_json(args.brief)
        report, _ = inspect_asset(args.candidate, brief)
        schema = load_json(ROOT / "schemas" / "qc-report.schema.json")
        errors = validate_document(report, schema)
    except (OSError, ValueError) as error:
        print(f"inspection failed: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 2
    if args.output:
        atomic_write_json(args.output, report)
        print(f"QC {report['overall_status']}: {args.output}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

