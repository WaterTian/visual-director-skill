from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


def apply_visual_review(report: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    if report["asset_id"] != review["asset_id"]:
        raise ValueError(
            f"asset_id mismatch: report={report['asset_id']} review={review['asset_id']}"
        )
    decisions: dict[str, dict[str, str]] = {}
    for decision in review["checks"]:
        requirement = decision["requirement"]
        if requirement in decisions:
            raise ValueError(f"duplicate visual review requirement: {requirement}")
        decisions[requirement] = decision

    result = deepcopy(report)
    known_requirements = {item["requirement"] for item in result["visual_checks"]}
    unknown = sorted(set(decisions) - known_requirements)
    if unknown:
        raise ValueError(f"review contains unknown requirements: {', '.join(unknown)}")

    for item in result["visual_checks"]:
        decision = decisions.get(item["requirement"])
        if decision:
            item["status"] = decision["status"]
            item["evidence"] = decision["evidence"]

    automatic_failures = [
        item["id"] for item in result["automatic_checks"] if item["status"] == "fail"
    ]
    visual_failures = [
        item["requirement"] for item in result["visual_checks"] if item["status"] == "fail"
    ]
    pending = [
        item["requirement"]
        for item in result["visual_checks"]
        if item["status"] == "not_reviewed"
    ]
    if automatic_failures or visual_failures:
        result["overall_status"] = "fail"
        result["blockers"] = [
            *(f"automatic check failed: {item}" for item in automatic_failures),
            *(f"visual check failed: {item}" for item in visual_failures),
        ]
    elif pending:
        result["overall_status"] = "review_required"
        result["blockers"] = [f"visual check pending: {item}" for item in pending]
    else:
        result["overall_status"] = "pass"
        result["blockers"] = []
    result["review"] = {
        "reviewer": review["reviewer"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return result

