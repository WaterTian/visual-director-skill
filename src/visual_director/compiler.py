from __future__ import annotations

import hashlib
from typing import Any

from .json_io import canonical_json_sha256


def _quoted(values: list[str]) -> str:
    return "; ".join(f'"{value}"' for value in values) if values else "None"


def _joined(values: list[str]) -> str:
    return "; ".join(values) if values else "None"


def compile_prompt(
    brief: dict[str, Any],
    template: dict[str, Any],
    selection: dict[str, Any],
    case_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    deliverable = brief["deliverable"]
    content = brief["content"]
    art = brief["art_direction"]
    composition = brief["composition"]
    transparent = bool(deliverable.get("transparent_background", False))
    prompt_lines = [
        f"Template direction: {template['title']['en']} ({template['id']})",
        f"Asset intent: {brief['goal']}",
        f"Audience: {brief.get('audience', 'Not specified')}",
        f"Deliverable: {deliverable['type']}; {deliverable['width']}x{deliverable['height']} {deliverable['format'].upper()}; transparent background: {'yes' if transparent else 'no'}",
        f"Subject: {content['subject']}",
        f"Composition: {composition['layout']}; viewpoint: {composition['viewpoint']}; focal hierarchy: {_joined(composition['focal_hierarchy'])}",
        f"Art direction: {art['style']}; palette: {_joined(art['palette'])}; lighting: {art['lighting']}; materials: {_joined(art['materials'])}",
        f"Text (verbatim): {_quoted(content.get('exact_text', []))}",
        f"Must include: {_joined(content['must_include'])}",
        f"Avoid: {_joined(content['must_avoid'])}",
        f"Template guidance: {_joined(template['guidance']['en'])}",
        "Output one finished asset, not a moodboard or process sheet, unless the brief explicitly requests one.",
    ]
    case_references: list[dict[str, Any]] = []
    assumptions: list[str] = []
    sources = [
        {
            "type": "template-catalog",
            "path": template["provenance"]["path"],
            "version": template["provenance"]["version"],
        }
    ]
    case_selection_sha256: str | None = None
    if case_selection is not None:
        if case_selection["asset_id"] != brief["asset_id"]:
            raise ValueError("case selection and brief asset_id do not match")
        if case_selection["template"]["id"] != template["id"]:
            raise ValueError("case selection and selected template do not match")
        case_selection_sha256 = canonical_json_sha256(case_selection)
        cue_lines: list[str] = []
        for case in case_selection["cases"]:
            cues = list(case["structure_cues"])
            cue_lines.append(f"case {case['id']} [{', '.join(cues)}]")
            case_references.append(
                {
                    "id": case["id"],
                    "title": case["title"],
                    "score": case["score"],
                    "prompt_sha256": case["prompt_sha256"],
                    "image_path": case["image"]["path"],
                    "image_sha256": case["image"]["sha256"],
                    "structure_cues": cues,
                }
            )
        if deliverable["type"] == "edit":
            prompt_lines.insert(
                1,
                "Case references are audit-only for this edit: "
                + ", ".join(f"case {case['id']}" for case in case_selection["cases"])
                + ".",
            )
            prompt_lines.insert(
                2,
                "Edit isolation: the supplied edit target is the sole visual authority; "
                "do not apply case composition, camera, subject, product identity, brand, "
                "logo, visible copy, or watermark content.",
            )
        else:
            prompt_lines.insert(
                1,
                "Structural references (generic cues only): " + "; ".join(cue_lines),
            )
            prompt_lines.insert(
                2,
                "Reference isolation: use only generic composition, camera, lighting, "
                "material, typography, and style cues; do not transfer case subjects, "
                "named people, product identity, brand names, logos, visible copy, or watermarks.",
            )
        assumptions.append(
            "Example ranking uses reviewed first-party metadata, not image embeddings; "
            "visually inspect the selected examples before generation."
        )
        if deliverable["type"] == "edit":
            assumptions.append(
                "Case cues are audit-only for this edit; the supplied edit target remains "
                "the sole visual authority."
            )
        sources.append(
            {
                "type": "first-party-example-catalog",
                "path": case_selection["source"]["catalog_path"],
                "version": case_selection["source"]["version"],
            }
        )
    if brief.get("brand"):
        brand = brief["brand"]
        prompt_lines.insert(
            8,
            f"Brand constraints: profile {brand.get('profile', 'unspecified')}; rules: {_joined(brand.get('rules', []))}",
        )
    if brief.get("references"):
        reference_lines = [
            f"{item['uri']} [{item['role']}]: {item.get('notes', 'no additional notes')}"
            for item in brief["references"]
        ]
        prompt_lines.insert(5, f"References: {_joined(reference_lines)}")

    prompt = "\n".join(prompt_lines)
    return {
        "version": "0.1",
        "asset_id": brief["asset_id"],
        "template": {
            "id": selection["id"],
            "title": selection["title"],
            "score": selection["score"],
            "score_breakdown": selection["score_breakdown"],
        },
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "case_selection_sha256": case_selection_sha256,
        "case_references": case_references,
        "hard_constraints": {
            "width": deliverable["width"],
            "height": deliverable["height"],
            "format": deliverable["format"],
            "transparent_background": transparent,
            "exact_text": list(content.get("exact_text", [])),
            "must_include": list(content["must_include"]),
            "must_avoid": list(content["must_avoid"]),
        },
        "assumptions": assumptions,
        "conflicts": [],
        "sources": sources,
    }
