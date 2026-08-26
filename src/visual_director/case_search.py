from __future__ import annotations

from typing import Any


def _haystack(record: dict[str, Any]) -> str:
    return " ".join(
        [
            record["title"],
            record["category"],
            *record["styles"],
            *record["scenes"],
            record["selection_text"],
        ]
    ).casefold()


def search_cases(
    catalog: dict[str, Any],
    *,
    query: str = "",
    category: str | None = None,
    styles: list[str] | None = None,
    scenes: list[str] | None = None,
    case_ids: list[int] | None = None,
    limit: int = 10,
    include_prompt: bool = False,
) -> list[dict[str, Any]]:
    query_text = query.strip().casefold()
    required_styles = {item.casefold() for item in (styles or [])}
    required_scenes = {item.casefold() for item in (scenes or [])}
    required_ids = set(case_ids or [])
    category_text = category.casefold() if category else None
    ranked: list[tuple[int, int, dict[str, Any]]] = []

    for record in catalog["cases"]:
        if required_ids and record["id"] not in required_ids:
            continue
        if category_text and record["category"].casefold() != category_text:
            continue
        record_styles = {item.casefold() for item in record["styles"]}
        record_scenes = {item.casefold() for item in record["scenes"]}
        if required_styles and not required_styles.issubset(record_styles):
            continue
        if required_scenes and not required_scenes.issubset(record_scenes):
            continue

        score = 0
        if query_text:
            title = record["title"].casefold()
            prompt = record["selection_text"].casefold()
            if query_text == title:
                score += 100
            elif query_text in title:
                score += 60
            if query_text in prompt:
                score += 30
            if query_text not in _haystack(record):
                continue
        output = {
            "id": record["id"],
            "title": record["title"],
            "category": record["category"],
            "styles": record["styles"],
            "scenes": record["scenes"],
            "selection_text": record["selection_text"],
            "prompt_sha256": record["prompt_sha256"],
            "image_path": record["image"]["path"],
            "prompt_path": record["prompt_path"],
            "status": record["status"],
        }
        if include_prompt:
            output["prompt_path"] = record["prompt_path"]
        ranked.append((score, record["id"], output))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in ranked[: max(1, limit)]]
