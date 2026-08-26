from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .json_io import canonical_json_sha256


def build_asset_manifest(
    brief: dict[str, Any],
    compiled: dict[str, Any],
    request: dict[str, Any],
    qc_report: dict[str, Any],
    file_metadata: dict[str, Any],
    generation_record: dict[str, Any] | None = None,
    composition_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status_map = {"fail": "qc_failed", "review_required": "candidate", "pass": "qc_passed"}
    recorded_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    provider = request["provider"]["name"]
    model = request["provider"]["model"]
    record_sha256 = None
    if generation_record is not None:
        if generation_record.get("asset_id") != brief["asset_id"]:
            raise ValueError("generation_record and brief asset_id do not match")
        if generation_record.get("request_sha256") != canonical_json_sha256(request):
            raise ValueError("generation_record request hash does not match GenerationRequest")
        if generation_record.get("status") == "completed" and generation_record.get("result"):
            provider = generation_record["result"]["provider"]
            model = generation_record["result"]["model"]
            recorded_at = generation_record["result"]["recorded_at"]
            generation_candidate_sha256 = generation_record["result"]["sha256"]
        elif generation_record.get("status") == "succeeded" and generation_record.get("adapter"):
            provider = generation_record["adapter"]["name"]
            model = generation_record["adapter"]["model"]
            recorded_at = generation_record["finished_at"]
            generation_candidate_sha256 = generation_record["candidate"]["sha256"]
        else:
            raise ValueError("generation_record must describe a completed or succeeded generation")
        if generation_candidate_sha256 != file_metadata["sha256"]:
            raise ValueError("generation_record candidate hash does not match inspected file")
        record_sha256 = canonical_json_sha256(generation_record)
    derivation = {
        "method": "direct",
        "record_sha256": None,
        "sources": [],
    }
    if (
        generation_record is not None
        and generation_record.get("status") == "completed"
        and generation_record.get("result", {}).get("inputs")
    ):
        derivation["sources"] = [
            {
                "path": item["uri"],
                "sha256": item["sha256"],
                "source_type": "reference",
                "provider": None,
                "model": None,
                "role": item["role"],
                "resampled": False,
            }
            for item in generation_record["result"]["inputs"]
        ]
    if composition_record is not None:
        if composition_record.get("asset_id") != brief["asset_id"]:
            raise ValueError("composition_record and brief asset_id do not match")
        output = composition_record.get("output", {})
        if output.get("sha256") != file_metadata["sha256"]:
            raise ValueError("composition_record output hash does not match inspected file")
        derivation = {
            "method": "exact_canvas_composition",
            "record_sha256": canonical_json_sha256(composition_record),
            "sources": [
                {
                    "path": item["source_path"],
                    "sha256": item["source_sha256"],
                    "source_type": item["source_type"],
                    "provider": item["provider"],
                    "model": item["model"],
                    "role": item["role"],
                    "resampled": item["resampled"],
                }
                for item in composition_record["raster_transforms"]
            ],
        }
    return {
        "version": "0.1",
        "asset_id": brief["asset_id"],
        "status": status_map[qc_report["overall_status"]],
        "file": {
            "name": file_metadata["name"],
            "sha256": file_metadata["sha256"],
            "format": file_metadata["format"],
            "width": file_metadata["width"],
            "height": file_metadata["height"],
            "has_alpha": file_metadata["has_alpha"],
            "size_bytes": file_metadata["size_bytes"],
        },
        "brief_sha256": canonical_json_sha256(brief),
        "compiled_prompt_sha256": canonical_json_sha256(compiled),
        "generation_request_sha256": canonical_json_sha256(request),
        "template": {
            "id": compiled["template"]["id"],
            "score": compiled["template"]["score"],
        },
        "source_revisions": [
            {"path": source["path"], "version": source["version"]}
            for source in compiled["sources"]
        ],
        "generation": {
            "provider": provider,
            "model": model,
            "recorded_at": recorded_at,
            "record_sha256": record_sha256,
        },
        "derivation": derivation,
        "qc": {
            "overall_status": qc_report["overall_status"],
            "report_sha256": canonical_json_sha256(qc_report),
        },
        "approvals": [],
    }
