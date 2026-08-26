from __future__ import annotations

from typing import Any


def build_generation_request(
    brief: dict[str, Any], compiled: dict[str, Any]
) -> dict[str, Any]:
    operation = "edit" if brief["deliverable"]["type"] == "edit" else "create"
    references = [
        {
            "uri": item["uri"],
            "role": item["role"],
            "notes": item.get("notes", ""),
        }
        for item in brief.get("references", [])
    ]
    invariants = list(brief["content"]["must_include"])
    if operation == "edit":
        invariants.extend(
            item.get("notes", "") for item in brief.get("references", []) if item.get("notes")
        )
    invariants.extend(brief.get("brand", {}).get("rules", []))
    invariants = list(dict.fromkeys(item for item in invariants if item))
    hard = compiled["hard_constraints"]
    return {
        "version": "0.1",
        "request_id": f"{brief['asset_id']}-{compiled['prompt_sha256'][:12]}",
        "asset_id": brief["asset_id"],
        "operation": operation,
        "prompt": compiled["prompt"],
        "prompt_sha256": compiled["prompt_sha256"],
        "output": {
            "width": hard["width"],
            "height": hard["height"],
            "format": hard["format"],
            "transparent_background": hard["transparent_background"],
        },
        "input_images": references,
        "invariants": invariants,
        "provider": {"name": None, "model": None},
    }

