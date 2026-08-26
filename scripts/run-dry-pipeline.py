#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.case_selector import select_cases
from visual_director.asset_qc import inspect_asset
from visual_director.compiler import compile_prompt
from visual_director.generation import build_generation_request
from visual_director.json_io import atomic_write_json, load_json
from visual_director.manifest import build_asset_manifest
from visual_director.selector import score_templates
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Visual Director pipeline without image generation.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "templates.json")
    parser.add_argument("--cases", type=Path, default=ROOT / "data" / "cases.json")
    parser.add_argument("--images", type=Path, default=ROOT / "gallery" / "gallery-manifest.json")
    parser.add_argument("--generation-record", type=Path)
    parser.add_argument("--composition-record", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
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
        brief = load_json(args.brief)
        catalog = load_json(args.catalog)
        cases = load_json(args.cases)
        images = load_json(args.images) if args.images.is_file() else None
        _require_valid(brief, "visual-brief.schema.json")
        _require_valid(catalog, "template-catalog.schema.json")
        _require_valid(cases, "case-catalog.schema.json")
        if images is not None:
            _require_valid(images, "gallery-manifest.schema.json")

        selection = score_templates(brief, catalog)[0]
        templates = {template["id"]: template for template in catalog["templates"]}
        case_selection = select_cases(
            brief,
            templates[selection["id"]],
            cases,
            image_manifest=images,
        )
        _require_valid(case_selection, "case-selection.schema.json")
        compiled = compile_prompt(
            brief,
            templates[selection["id"]],
            selection,
            case_selection,
        )
        _require_valid(compiled, "compiled-prompt.schema.json")

        request = build_generation_request(brief, compiled)
        _require_valid(request, "generation-request.schema.json")

        report, file_metadata = inspect_asset(args.candidate, brief)
        _require_valid(report, "qc-report.schema.json")

        generation_record = None
        if args.generation_record:
            generation_record = load_json(args.generation_record)
            if generation_record.get("status") == "completed":
                _require_valid(generation_record, "generation-handoff.schema.json")
            else:
                _require_valid(generation_record, "provider-attempt.schema.json")

        composition_record = None
        if args.composition_record:
            composition_record = load_json(args.composition_record)
            _require_valid(composition_record, "composition-record.schema.json")

        manifest = build_asset_manifest(
            brief,
            compiled,
            request,
            report,
            file_metadata,
            generation_record,
            composition_record,
        )
        _require_valid(manifest, "asset-manifest.schema.json")
    except (OSError, ValueError) as error:
        print(f"dry-run failed: {error}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "case-selection.json": case_selection,
        "compiled-prompt.json": compiled,
        "generation-request.json": request,
        "qc-report.json": report,
        "asset-manifest.json": manifest,
    }
    for filename, document in outputs.items():
        atomic_write_json(args.output_dir / filename, document)
    print(
        f"dry-run {report['overall_status']}: {brief['asset_id']} -> {args.output_dir} "
        f"(template={selection['id']})"
    )
    return 1 if report["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
