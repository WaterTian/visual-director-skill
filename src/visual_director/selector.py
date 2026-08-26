from __future__ import annotations

from typing import Any

CATEGORY_BY_DELIVERABLE = {
    "product": "Products & E-commerce",
    "hero": "Products & E-commerce",
    "poster": "Posters & Typography",
    "infographic": "Charts & Infographics",
    "ui": "UI & Interfaces",
    "brand": "Brand & Logos",
    "illustration": "Illustration & Art",
    "character": "Characters & People",
    "edit": "Characters & People",
    "scene": "Scenes & Storytelling",
    "other": "Other Use Cases",
}

PREFERRED_TEMPLATE_BY_DELIVERABLE = {
    "product": "product-commerce-visual",
    "hero": "product-commerce-visual",
    "poster": "poster-layout-system",
    "infographic": "infographic-engine",
    "ui": "ui-screenshot-system",
    "brand": "brand-identity-package",
    "illustration": "illustration-art-style",
    "character": "character-design-sheet",
    "edit": "character-design-sheet",
    "scene": "scene-storytelling",
    "other": "concept-product-breakdown",
}

EDIT_ROUTES = (
    (
        "Products & E-commerce",
        "product-commerce-visual",
        ("product", "device", "packaging", "merchandise", "appliance", "商品", "产品", "设备", "包装"),
    ),
    (
        "Characters & People",
        "character-design-sheet",
        ("character", "person", "face", "identity", "outfit", "coat", "satchel", "人物", "人脸", "身份", "服装"),
    ),
    (
        "UI & Interfaces",
        "ui-screenshot-system",
        ("interface", "screen", "dashboard", "mobile app", "website", "界面", "屏幕"),
    ),
    (
        "Posters & Typography",
        "poster-layout-system",
        ("poster", "typography", "headline", "海报", "字体", "标题"),
    ),
    (
        "Scenes & Storytelling",
        "scene-storytelling",
        ("landscape", "weather", "environment", "scene", "风景", "天气", "场景"),
    ),
)

STYLE_ALIASES = {
    "3d": ("3d", "render", "toy", "collectible"),
    "brand": ("brand", "identity", "logo", "campaign"),
    "character": ("character", "identity", "pose", "outfit"),
    "fashion": ("fashion", "lookbook", "wardrobe", "clothing", "outfit"),
    "charts": ("chart", "diagram", "flow", "technical"),
    "classical": ("classical", "history", "dynasty", "scroll"),
    "illustration": ("illustration", "watercolor", "paint", "drawing"),
    "infographic": ("infographic", "diagram", "flow", "module"),
    "photography": ("photo", "photography", "photorealistic", "studio"),
    "poster": ("poster", "typography", "headline", "event"),
    "product": ("product", "catalog", "commerce", "packaging"),
    "realistic": ("realistic", "photorealistic", "photo", "material"),
    "ui": ("ui", "interface", "screen", "mobile", "dashboard"),
}

SCENE_ALIASES = {
    "commerce": ("shop", "commerce", "catalog", "product", "customer", "launch"),
    "creative": ("creative", "concept", "abstract"),
    "education": ("learn", "education", "explain", "technician", "student"),
    "fashion": ("fashion", "clothing", "outfit"),
    "food": ("food", "coffee", "cafe", "market"),
    "history": ("history", "dynasty", "ancient"),
    "social": ("social", "community", "feed", "campaign"),
    "story": ("story", "narrative", "quest", "scene"),
    "tech": ("tech", "technical", "developer", "device", "data"),
    "travel": ("travel", "city", "map", "street"),
}


def _request_text(brief: dict[str, Any]) -> str:
    content = brief["content"]
    art = brief["art_direction"]
    composition = brief["composition"]
    values = [
        brief["deliverable"]["type"],
        brief["goal"],
        brief.get("audience", ""),
        content["subject"],
        *content.get("exact_text", []),
        *content["must_include"],
        *content["must_avoid"],
        art["style"],
        *art["palette"],
        art["lighting"],
        *art["materials"],
        composition["layout"],
        composition["viewpoint"],
        *composition["focal_hierarchy"],
    ]
    return " ".join(str(value).lower() for value in values)


def _metadata_text(template: dict[str, Any]) -> str:
    values = [
        template["id"],
        template["title"]["en"],
        template["title"]["zh"],
        template["category"],
        *template["styles"],
        *template["scenes"],
        *template["tags"],
        template["use_when"]["en"],
        template["use_when"]["zh"],
        *template["guidance"]["en"],
        *template["guidance"]["zh"],
        *template["pitfalls"]["en"],
        *template["pitfalls"]["zh"],
    ]
    return " ".join(str(value).lower() for value in values)


def _target_route(deliverable_type: str, request: str) -> tuple[str, str | None]:
    if deliverable_type == "edit":
        for category, template_id, terms in EDIT_ROUTES:
            if any(term in request for term in terms):
                return category, template_id
    return (
        CATEGORY_BY_DELIVERABLE.get(deliverable_type, "Other Use Cases"),
        PREFERRED_TEMPLATE_BY_DELIVERABLE.get(deliverable_type),
    )


def _alias_match_score(request: str, labels: list[str], aliases: dict[str, tuple[str, ...]], maximum: int) -> int:
    matched = 0
    for label in labels:
        terms = aliases.get(label.lower(), (label.lower(),))
        if any(term in request for term in terms):
            matched += 1
    return min(maximum, matched * maximum) if matched else 0


def score_templates(brief: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    deliverable_type = brief["deliverable"]["type"]
    request = _request_text(brief)
    target_category, preferred_id = _target_route(deliverable_type, request)
    has_exact_text = bool(brief["content"].get("exact_text"))
    has_references = bool(brief.get("references"))

    results: list[dict[str, Any]] = []
    for template in catalog["templates"]:
        metadata = _metadata_text(template)
        category_score = 55 if template["category"] == target_category else 0
        style_score = _alias_match_score(request, template["styles"] + template["tags"], STYLE_ALIASES, 20)
        scene_score = _alias_match_score(request, template["scenes"], SCENE_ALIASES, 10)
        constraint_score = 0
        reasons: list[str] = []
        if category_score:
            reasons.append(f"category matches {target_category}")
        if style_score:
            reasons.append("style/tag language matches the brief")
        if scene_score:
            reasons.append("scene language matches the brief")
        if template["id"] == preferred_id:
            constraint_score += 8
            reasons.append(f"preferred template for deliverable type {deliverable_type}")
        text_terms = ("text", "label", "copy", "typography", "文字", "标签", "文案", "字体")
        if has_exact_text and any(term in metadata for term in text_terms):
            constraint_score += 4
            reasons.append("template addresses exact text or labels")
        reference_terms = ("reference", "identity", "preserve", "参考", "身份", "保持")
        if has_references and any(term in metadata for term in reference_terms):
            constraint_score += 3
            reasons.append("template addresses reference preservation")
        constraint_score = min(15, constraint_score)
        breakdown = {
            "category": category_score,
            "style": style_score,
            "scene": scene_score,
            "constraint": constraint_score,
        }
        results.append(
            {
                "id": template["id"],
                "title": template["title"]["en"],
                "score": sum(breakdown.values()),
                "score_breakdown": breakdown,
                "reasons": reasons or ["fallback candidate with no direct match"],
            }
        )
    return sorted(results, key=lambda item: (-item["score"], item["id"]))
