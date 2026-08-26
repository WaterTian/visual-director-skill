#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.asset_qc import inspect_asset
from visual_director.case_selector import select_cases
from visual_director.compiler import compile_prompt
from visual_director.compositor import compose_exact_canvas
from visual_director.free_exact import (
    build_composition_plan,
    build_material_request,
    portable_project_path,
    select_composition_preset,
)
from visual_director.generation import build_generation_request
from visual_director.json_io import atomic_write_json, canonical_json_sha256, load_json
from visual_director.manifest import build_asset_manifest
from visual_director.selector import score_templates
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare or resume the no-paid-API exact-canvas pipeline. "
            "Omit --material to prepare a single built-in ImageGen request."
        )
    )
    parser.add_argument("brief", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--material", type=Path)
    parser.add_argument("--authorized-by")
    parser.add_argument(
        "--preset",
        default="left-copy-right-product-hero",
    )
    parser.add_argument(
        "--presets",
        type=Path,
        default=ROOT / "data" / "composition-presets.json",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT / "data" / "templates.json",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "data" / "cases.json",
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=ROOT / "gallery" / "gallery-manifest.json",
    )
    parser.add_argument("--font-path")
    return parser.parse_args()


def _require_valid(document: dict, schema_name: str) -> None:
    schema = load_json(ROOT / "schemas" / schema_name)
    errors = validate_document(document, schema)
    if errors:
        summary = "; ".join(
            f"{error.path}: {error.message}" for error in errors[:8]
        )
        raise ValueError(f"{schema_name} validation failed: {summary}")


def _resolved(project_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def _prepare(
    brief: dict,
    case_selection: dict,
    output_dir: Path,
    project_root: Path,
    *,
    authorized_by: str | None,
) -> dict:
    request_path = output_dir / "material-request.json"
    case_selection_path = output_dir / "case-selection.json"
    material_path = output_dir / f"{brief['asset_id']}-material.png"
    material_relative = portable_project_path(project_root, material_path)
    if request_path.exists():
        existing = load_json(request_path)
        _require_valid(existing, "material-request.schema.json")
        if not authorized_by:
            raise FileExistsError(f"material request already exists: {request_path}")
        if existing["status"] != "awaiting_authorization":
            raise ValueError("material request is already authorized")
        if (
            existing["asset_id"] != brief["asset_id"]
            or existing["candidate"]["relative_path"] != material_relative
        ):
            raise ValueError("existing material request does not match the current run")
    if case_selection_path.exists():
        existing_selection = load_json(case_selection_path)
        _require_valid(existing_selection, "case-selection.schema.json")
        if canonical_json_sha256(existing_selection) != canonical_json_sha256(
            case_selection
        ):
            raise ValueError("existing case selection does not match the current run")
    request = build_material_request(
        brief,
        material_relative,
        authorized_by=authorized_by,
        case_selection=case_selection,
    )
    _require_valid(request, "material-request.schema.json")
    output_dir.mkdir(parents=True, exist_ok=True)
    if not case_selection_path.exists():
        atomic_write_json(case_selection_path, case_selection)
    atomic_write_json(request_path, request)
    return request


def _resume(
    brief: dict,
    template_catalog: dict,
    preset: dict,
    material_path: Path,
    output_dir: Path,
    project_root: Path,
    *,
    font_path: str | None,
) -> tuple[dict, dict]:
    material_request_path = output_dir / "material-request.json"
    material_request = load_json(material_request_path)
    _require_valid(material_request, "material-request.schema.json")
    case_selection = load_json(output_dir / "case-selection.json")
    _require_valid(case_selection, "case-selection.schema.json")
    if material_request["asset_id"] != brief["asset_id"]:
        raise ValueError("material request and brief asset_id do not match")
    if material_request["status"] != "ready":
        raise ValueError("material request is not authorized")
    if material_request["case_selection_sha256"] != canonical_json_sha256(
        case_selection
    ):
        raise ValueError("material request and case selection do not match")
    if material_request["case_ids"] != [
        case["id"] for case in case_selection["cases"]
    ]:
        raise ValueError("material request case IDs do not match case selection")
    actual_relative = portable_project_path(project_root, material_path)
    expected_relative = material_request["candidate"]["relative_path"]
    if actual_relative != expected_relative:
        raise ValueError(
            f"material path does not match request: expected {expected_relative}"
        )

    output_names = [
        f"{brief['asset_id']}-exact.png",
        "composition-plan.json",
        "composition-record.json",
        "compiled-prompt.json",
        "generation-request.json",
        "qc-report.json",
        "asset-manifest.json",
    ]
    existing = [name for name in output_names if (output_dir / name).exists()]
    if existing:
        raise FileExistsError(
            "pipeline outputs already exist: " + ", ".join(existing)
        )

    plan = build_composition_plan(
        brief,
        preset,
        material_path,
        project_root,
        font_path=font_path,
    )
    _require_valid(plan, "composition-plan.schema.json")
    selection = score_templates(brief, template_catalog)[0]
    templates = {item["id"]: item for item in template_catalog["templates"]}
    if selection["id"] != case_selection["template"]["id"]:
        raise ValueError("case selection and selected template do not match")
    compiled = compile_prompt(
        brief,
        templates[selection["id"]],
        selection,
        case_selection,
    )
    _require_valid(compiled, "compiled-prompt.schema.json")
    generation_request = build_generation_request(brief, compiled)
    _require_valid(generation_request, "generation-request.schema.json")
    final_path = output_dir / f"{brief['asset_id']}-exact.png"
    composition_record = compose_exact_canvas(plan, project_root, final_path)
    _require_valid(composition_record, "composition-record.schema.json")
    qc_report, metadata = inspect_asset(final_path, brief)
    _require_valid(qc_report, "qc-report.schema.json")
    manifest = build_asset_manifest(
        brief,
        compiled,
        generation_request,
        qc_report,
        metadata,
        composition_record=composition_record,
    )
    _require_valid(manifest, "asset-manifest.schema.json")

    outputs = {
        "composition-plan.json": plan,
        "composition-record.json": composition_record,
        "compiled-prompt.json": compiled,
        "generation-request.json": generation_request,
        "qc-report.json": qc_report,
        "asset-manifest.json": manifest,
    }
    for filename, document in outputs.items():
        destination = output_dir / filename
        atomic_write_json(destination, document)
    return qc_report, manifest


def main() -> int:
    args = parse_args()
    try:
        project_root = args.project_root.resolve()
        output_dir = _resolved(project_root, args.output_dir).resolve()
        portable_project_path(project_root, output_dir)
        brief = load_json(args.brief)
        preset_catalog = load_json(args.presets)
        template_catalog = load_json(args.catalog)
        case_catalog = load_json(args.cases)
        image_manifest = load_json(args.images) if args.images.is_file() else None
        _require_valid(brief, "visual-brief.schema.json")
        _require_valid(
            preset_catalog,
            "composition-preset-catalog.schema.json",
        )
        _require_valid(template_catalog, "template-catalog.schema.json")
        _require_valid(case_catalog, "case-catalog.schema.json")
        if image_manifest is not None:
            _require_valid(image_manifest, "gallery-manifest.schema.json")
        preset = select_composition_preset(brief, preset_catalog, args.preset)

        if args.material is None:
            template_selection = score_templates(brief, template_catalog)[0]
            templates = {
                item["id"]: item for item in template_catalog["templates"]
            }
            case_selection = select_cases(
                brief,
                templates[template_selection["id"]],
                case_catalog,
                image_manifest=image_manifest,
            )
            _require_valid(case_selection, "case-selection.schema.json")
            material_request = _prepare(
                brief,
                case_selection,
                output_dir,
                project_root,
                authorized_by=args.authorized_by,
            )
            print(
                f"pipeline {material_request['status']}: generate one transparent "
                f"material at {material_request['candidate']['relative_path']}"
            )
            return 0

        material_path = _resolved(project_root, args.material).resolve()
        qc_report, manifest = _resume(
            brief,
            template_catalog,
            preset,
            material_path,
            output_dir,
            project_root,
            font_path=args.font_path,
        )
    except (OSError, ValueError) as error:
        print(f"free exact pipeline failed: {error}", file=sys.stderr)
        return 2

    print(
        f"pipeline {qc_report['overall_status']}: {brief['asset_id']} -> "
        f"{output_dir} (manifest={manifest['status']})"
    )
    return 1 if qc_report["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
