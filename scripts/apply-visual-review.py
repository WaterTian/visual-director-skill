#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import atomic_write_json, load_json
from visual_director.promotion import reconcile_manifest_qc
from visual_director.validation import validate_document
from visual_director.visual_review import apply_visual_review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply evidence-backed visual review decisions to a QC report.")
    parser.add_argument("qc_report", type=Path)
    parser.add_argument("review", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if bool(args.manifest) != bool(args.manifest_output):
            raise ValueError("--manifest and --manifest-output must be provided together")
        report = load_json(args.qc_report)
        review = load_json(args.review)
        report_schema = load_json(ROOT / "schemas" / "qc-report.schema.json")
        review_schema = load_json(ROOT / "schemas" / "visual-review.schema.json")
        input_errors = validate_document(report, report_schema) + validate_document(review, review_schema)
        if input_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in input_errors)
            raise ValueError(summary)
        updated = apply_visual_review(report, review)
        output_errors = validate_document(updated, report_schema)
        if output_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in output_errors)
            raise ValueError(summary)
        updated_manifest = None
        if args.manifest:
            manifest = load_json(args.manifest)
            manifest_schema = load_json(ROOT / "schemas" / "asset-manifest.schema.json")
            manifest_errors = validate_document(manifest, manifest_schema)
            if manifest_errors:
                summary = "; ".join(
                    f"{error.path}: {error.message}" for error in manifest_errors
                )
                raise ValueError(summary)
            updated_manifest = reconcile_manifest_qc(manifest, updated)
            updated_manifest_errors = validate_document(updated_manifest, manifest_schema)
            if updated_manifest_errors:
                summary = "; ".join(
                    f"{error.path}: {error.message}" for error in updated_manifest_errors
                )
                raise ValueError(summary)
    except (OSError, ValueError) as error:
        print(f"visual review failed: {error}", file=sys.stderr)
        return 2
    if updated_manifest is not None:
        atomic_write_json(args.manifest_output, updated_manifest)
    if args.output:
        atomic_write_json(args.output, updated)
        print(f"visual review {updated['overall_status']}: {args.output}")
    else:
        print(json.dumps(updated, ensure_ascii=False, indent=2))
    return 1 if updated["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
