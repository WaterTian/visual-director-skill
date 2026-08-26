#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import atomic_write_json, load_json
from visual_director.promotion import promote_asset
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote an approved qc_passed candidate to a formal asset path.")
    parser.add_argument("candidate", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("qc_report", type=Path)
    parser.add_argument("approval", type=Path)
    parser.add_argument("--manifest-output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow replacement of an existing destination")
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
        if args.manifest_output.exists() and not args.overwrite:
            raise FileExistsError(f"manifest output already exists: {args.manifest_output}")
        manifest = _load_valid(args.manifest, "asset-manifest.schema.json")
        qc_report = _load_valid(args.qc_report, "qc-report.schema.json")
        approval = _load_valid(args.approval, "approval.schema.json")
        landed = promote_asset(
            args.candidate,
            args.destination,
            manifest,
            qc_report,
            approval,
            overwrite=args.overwrite,
        )
        schema = load_json(ROOT / "schemas" / "asset-manifest.schema.json")
        output_errors = validate_document(landed, schema)
        if output_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in output_errors[:8])
            raise ValueError(f"landed manifest invalid: {summary}")
        atomic_write_json(args.manifest_output, landed)
    except (OSError, ValueError) as error:
        print(f"promotion failed: {error}", file=sys.stderr)
        return 2
    print(f"promoted {landed['asset_id']}: {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
