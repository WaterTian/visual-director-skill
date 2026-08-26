from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from .json_io import canonical_json_sha256
from .selector import SCENE_ALIASES, STYLE_ALIASES

TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]{2,}", re.IGNORECASE)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "create",
    "for",
    "from",
    "generate",
    "image",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "one",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "without",
    "only",
    "keep",
}

PREFERRED_STYLE_BY_DELIVERABLE = {
    "brand": "brand",
    "character": "character",
    "edit": "character",
    "hero": "product",
    "illustration": "illustration",
    "infographic": "infographic",
    "poster": "poster",
    "product": "product",
    "ui": "ui",
}

PREFERRED_STYLE_BY_CATEGORY = {
    "Brand & Logos": "brand",
    "Characters & People": "character",
    "Charts & Infographics": "infographic",
    "Illustration & Art": "illustration",
    "Posters & Typography": "poster",
    "Products & E-commerce": "product",
    "UI & Interfaces": "ui",
}

EXAMPLE_PRIORITY_BAND = 10

CUE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("layout:negative-space", ("negative space", "copy space", "empty space")),
    ("layout:centered-subject", ("centered", "centred", "in the center")),
    ("layout:right-weighted", ("right third", "on the right", "right side")),
    ("layout:left-weighted", ("left third", "on the left", "left side")),
    ("layout:grid", ("grid layout", "2x2 grid", "3x3 grid", "six-panel", "panels")),
    (
        "layout:modular",
        (
            "module",
            "modular",
            "information hierarchy",
            "stage 1",
            "stage 2",
            "technical breakdown",
            "development board",
            "concept board",
            "process board",
            "blueprint dimensions",
            "illustration sheet",
            "technical views",
            "surrounded by technical",
        ),
    ),
    ("layout:split", ("split-screen", "split screen", "two-column", "two column")),
    ("layout:layered-depth", ("foreground", "midground", "background")),
    ("camera:three-quarter", ("three-quarter", "three quarter", "3/4 view")),
    ("camera:eye-level", ("eye-level", "eye level")),
    ("camera:top-down", ("top-down", "top down", "overhead view")),
    ("camera:close-up", ("close-up", "close up", "macro shot")),
    ("camera:wide-angle", ("wide-angle", "wide angle")),
    ("camera:isometric", ("isometric",)),
    ("camera:straight-on", ("straight-on", "straight on", "front view")),
    ("lighting:soft-studio", ("soft studio", "studio lighting", "softbox")),
    ("lighting:soft-daylight", ("soft daylight", "natural daylight", "window light")),
    ("lighting:rim-light", ("rim light", "edge light")),
    ("lighting:backlight", ("backlight", "backlit")),
    ("lighting:high-contrast", ("high contrast", "high-contrast", "dramatic lighting")),
    ("lighting:graphic-glow", ("glowing", "neon glow", "graphic glow")),
    ("material:matte", ("matte",)),
    ("material:metal", ("metal", "aluminum", "aluminium", "steel")),
    ("material:glass", ("glass", "transparent crystal")),
    ("material:paper", ("paper texture", "printed paper", "paper background")),
    ("material:fabric", ("fabric", "woven", "textile")),
    ("material:wood", ("wood", "wooden")),
    ("material:plastic", ("plastic", "polymer")),
    ("type:headline-led", ("dominant headline", "large headline", "bold headline")),
    ("type:minimal-copy", ("minimal typography", "minimal text", "minimal copy")),
    ("type:readable-labels", ("readable text", "clear labels", "bilingual labels")),
)


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.casefold().replace("-", " "))
        if token not in STOPWORDS and len(token) > 1 and not token.isdigit()
    ]


def _brief_text(brief: dict[str, Any]) -> str:
    content = brief["content"]
    art = brief["art_direction"]
    composition = brief["composition"]
    brand = brief.get("brand") or {}
    values = [
        brief["deliverable"]["type"],
        brief["goal"],
        brief.get("audience", ""),
        content["subject"],
        *content["must_include"],
        art["style"],
        *art["palette"],
        art["lighting"],
        *art["materials"],
        composition["layout"],
        composition["viewpoint"],
        *composition["focal_hierarchy"],
        *brand.get("rules", []),
    ]
    return " ".join(str(value) for value in values)


def _case_text(record: dict[str, Any]) -> str:
    return " ".join(
        [
            record["title"],
            record["category"],
            *record["styles"],
            *record["scenes"],
            record["selection_text"],
        ]
    )


def _desired_labels(request: str, aliases: dict[str, tuple[str, ...]]) -> set[str]:
    lowered = request.casefold()
    return {
        label
        for label, terms in aliases.items()
        if any(term.casefold() in lowered for term in terms)
    }


def _label_match_count(labels: list[str], desired: set[str]) -> int:
    normalized = {label.casefold().rstrip("s") for label in labels}
    return sum(
        1
        for target in desired
        if target.casefold().rstrip("s") in normalized
    )


def _adoptable_structure_cues(
    record: dict[str, Any],
    desired_cues: set[str],
    desired_styles: set[str],
) -> list[str]:
    cues = [
        cue for cue in _generic_cues(record["selection_text"]) if cue in desired_cues
    ]
    for style in record["styles"]:
        slug = re.sub(r"[^a-z0-9]+", "-", style.casefold()).strip("-")
        if slug and slug in desired_styles:
            cues.append(f"style:{slug}")
    return (list(dict.fromkeys(cues)) or ["style:general-reference"])[:10]


def _generic_cues(text: str) -> list[str]:
    lowered = text.casefold()
    return [
        cue
        for cue, patterns in CUE_PATTERNS
        if any(pattern in lowered for pattern in patterns)
    ]


def _layout_is_compatible(
    deliverable_type: str,
    desired_cues: set[str],
    record_cues: set[str],
) -> bool:
    single_asset_types = {"hero", "product"}
    multi_panel_cues = {"layout:grid", "layout:modular", "layout:split"}
    if deliverable_type not in single_asset_types:
        return True
    requested_multi_panel = bool(desired_cues.intersection(multi_panel_cues))
    return requested_multi_panel or not record_cues.intersection(multi_panel_cues)


def _bm25_scores(query: list[str], documents: list[list[str]]) -> tuple[list[float], dict[str, float]]:
    if not query:
        return [0.0] * len(documents), {}
    document_counts = [Counter(document) for document in documents]
    average_length = sum(len(document) for document in documents) / max(1, len(documents))
    document_frequency = Counter(
        token for document in documents for token in set(document) if token in query
    )
    idf = {
        token: math.log(1 + (len(documents) - count + 0.5) / (count + 0.5))
        for token, count in document_frequency.items()
    }
    k1 = 1.5
    b = 0.75
    scores: list[float] = []
    for document, counts in zip(documents, document_counts):
        score = 0.0
        length_factor = 1 - b + b * len(document) / max(1.0, average_length)
        for token in set(query):
            frequency = counts.get(token, 0)
            if not frequency:
                continue
            score += idf.get(token, 0.0) * (
                frequency * (k1 + 1) / (frequency + k1 * length_factor)
            )
        scores.append(score)
    return scores, idf


def select_cases(
    brief: dict[str, Any],
    template: dict[str, Any],
    case_catalog: dict[str, Any],
    *,
    top: int = 3,
    image_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    top = max(1, min(3, top))
    records = case_catalog["cases"]
    request_text = _brief_text(brief)
    query_tokens = _tokens(request_text)
    desired_cues = set(_generic_cues(request_text))
    document_tokens = [_tokens(_case_text(record)) for record in records]
    bm25, idf = _bm25_scores(query_tokens, document_tokens)
    maximum_bm25 = max(bm25, default=0.0)
    desired_styles = _desired_labels(request_text, STYLE_ALIASES)
    desired_scenes = _desired_labels(request_text, SCENE_ALIASES)
    preferred_style = (
        PREFERRED_STYLE_BY_CATEGORY.get(template["category"])
        if brief["deliverable"]["type"] == "edit"
        else PREFERRED_STYLE_BY_DELIVERABLE.get(brief["deliverable"]["type"])
    )
    example_ids = set(template["example_cases"])
    query_set = set(query_tokens)
    image_by_case = {
        item["case_id"]: item for item in (image_manifest or {}).get("assets", [])
    }

    ranked: list[dict[str, Any]] = []
    for record, lexical_raw, tokens in zip(records, bm25, document_tokens):
        category_score = 35 if record["category"] == template["category"] else 0
        example_score = 5 if record["id"] in example_ids else 0
        style_score = min(10, 5 * _label_match_count(record["styles"], desired_styles))
        scene_score = min(5, 3 * _label_match_count(record["scenes"], desired_scenes))
        deliverable_style_score = (
            5
            if preferred_style
            and preferred_style in {label.casefold() for label in record["styles"]}
            else 0
        )
        record_cues = set(_generic_cues(record["selection_text"]))
        if not _layout_is_compatible(
            (
                "product"
                if brief["deliverable"]["type"] == "edit"
                and template["category"] == "Products & E-commerce"
                else brief["deliverable"]["type"]
            ),
            desired_cues,
            record_cues,
        ):
            continue
        structure_score = (
            int(round(20 * len(desired_cues.intersection(record_cues)) / len(desired_cues)))
            if desired_cues
            else 0
        )
        lexical_score = (
            int(round(20 * lexical_raw / maximum_bm25)) if maximum_bm25 > 0 else 0
        )
        breakdown = {
            "category": category_score,
            "template_example": example_score,
            "style": style_score,
            "scene": scene_score,
            "deliverable_style": deliverable_style_score,
            "structure": structure_score,
            "lexical": lexical_score,
        }
        matched = sorted(
            query_set.intersection(tokens),
            key=lambda token: (-idf.get(token, 0.0), token),
        )[:8]
        reasons: list[str] = []
        if category_score:
            reasons.append(f"category matches {template['category']}")
        if example_score:
            reasons.append(f"listed by template {template['id']}")
        if style_score:
            reasons.append("style metadata matches the brief")
        if scene_score:
            reasons.append("scene metadata matches the brief")
        if deliverable_style_score:
            reasons.append("style matches the deliverable type")
        if structure_score:
            reasons.append("generic composition or rendering cues match the brief")
        if lexical_score:
            reasons.append("Prompt text shares decision-relevant terms with the brief")
        image_record = image_by_case.get(record["id"])
        ranked.append(
            {
                "id": record["id"],
                "title": record["title"],
                "category": record["category"],
                "score": sum(breakdown.values()),
                "score_breakdown": breakdown,
                "reasons": reasons or ["fallback candidate after deterministic ranking"],
                "matched_terms": matched,
                "structure_cues": _adoptable_structure_cues(
                    record,
                    desired_cues,
                    desired_styles,
                ),
                "prompt_sha256": record["prompt_sha256"],
                "image": {
                    "path": record["image"]["path"],
                    "manifest_verified": image_record is not None,
                    "sha256": image_record["image_sha256"] if image_record else None,
                    "width": image_record["width"] if image_record else None,
                    "height": image_record["height"] if image_record else None,
                },
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    template_examples = [item for item in ranked if item["id"] in example_ids]
    if template_examples and ranked:
        strongest_example = template_examples[0]
        strongest_score = ranked[0]["score"]
        if strongest_example["score"] >= strongest_score - EXAMPLE_PRIORITY_BAND:
            ranked.remove(strongest_example)
            ranked.insert(0, strongest_example)
    selected: list[dict[str, Any]] = []
    seen_prompts: set[str] = set()
    seen_images: set[str] = set()
    for item in ranked:
        image_hash = item["image"]["sha256"]
        if item["prompt_sha256"] in seen_prompts or (image_hash and image_hash in seen_images):
            continue
        selected.append(item)
        seen_prompts.add(item["prompt_sha256"])
        if image_hash:
            seen_images.add(image_hash)
        if len(selected) == top:
            break
    if len(selected) < top:
        selected_ids = {item["id"] for item in selected}
        selected.extend(item for item in ranked if item["id"] not in selected_ids)
        selected = selected[:top]

    source = case_catalog["source"]
    request_sha256 = canonical_json_sha256(
        {
            "brief": brief,
            "template_id": template["id"],
            "case_catalog_version": source["version"],
        }
    )
    return {
        "version": "0.1",
        "asset_id": brief["asset_id"],
        "request_sha256": request_sha256,
        "template": {
            "id": template["id"],
            "category": template["category"],
        },
        "policy": {
            "selection_basis": "local_text_and_metadata",
            "max_cases": top,
            "prompt_text_included": False,
            "adoption": "generic_structure_cues_only",
            "visual_review_required": True,
            "forbidden_transfers": [
                "brand names",
                "case subjects or named people",
                "logos",
                "visible copy",
                "watermarks",
                "product identity",
            ],
        },
        "source": {
            "kind": source["kind"],
            "version": source["version"],
            "catalog_path": source["catalog_path"],
            "catalog_sha256": canonical_json_sha256(case_catalog),
            "image_manifest_used": bool(image_by_case),
        },
        "cases": selected,
    }
