from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from PIL import Image

from .asset_qc import file_sha256
from .json_io import canonical_json_sha256


def _portable_path_value(value: str) -> str:
    normalized = value.replace("\\", "/")
    portable = PurePosixPath(normalized)
    if (
        not normalized
        or portable.is_absolute()
        or PureWindowsPath(value).is_absolute()
        or ".." in portable.parts
    ):
        raise ValueError("material candidate path must be project-relative")
    return portable.as_posix()


def portable_project_path(project_root: Path, path: Path) -> str:
    root = project_root.resolve()
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("material path must be inside project root")
    relative = resolved.relative_to(root).as_posix()
    portable = PurePosixPath(relative)
    if (
        not relative
        or portable.is_absolute()
        or PureWindowsPath(relative).is_absolute()
        or ".." in portable.parts
    ):
        raise ValueError("material path must be a portable project-relative path")
    return relative


def select_composition_preset(
    brief: dict[str, Any],
    catalog: dict[str, Any],
    preset_id: str,
) -> dict[str, Any]:
    preset = next(
        (item for item in catalog["presets"] if item["id"] == preset_id),
        None,
    )
    if preset is None:
        raise ValueError(f"unknown composition preset: {preset_id}")
    deliverable = brief["deliverable"]
    if deliverable["type"] not in preset["deliverable_types"]:
        raise ValueError(
            f"preset {preset_id} does not support deliverable type "
            f"{deliverable['type']}"
        )
    if deliverable["format"] != preset["canvas"]["format"]:
        raise ValueError(
            f"preset {preset_id} requires {preset['canvas']['format']} output"
        )
    requested_transparency = deliverable.get("transparent_background", False)
    if requested_transparency != preset["canvas"]["transparent_background"]:
        raise ValueError(
            f"preset {preset_id} requires transparent_background="
            f"{str(preset['canvas']['transparent_background']).lower()}"
        )
    ratio = deliverable["width"] / deliverable["height"]
    ratio_limits = preset["aspect_ratio"]
    if not ratio_limits["minimum"] <= ratio <= ratio_limits["maximum"]:
        raise ValueError(
            f"preset {preset_id} requires aspect ratio between "
            f"{ratio_limits['minimum']} and {ratio_limits['maximum']}"
        )
    exact_text = brief["content"].get("exact_text", [])
    text_limits = preset["exact_text"]
    if not text_limits["minimum"] <= len(exact_text) <= text_limits["maximum"]:
        raise ValueError(
            f"preset {preset_id} requires between {text_limits['minimum']} and "
            f"{text_limits['maximum']} exact text strings"
        )
    if len(preset["text_slots"]) < len(exact_text):
        raise ValueError(f"preset {preset_id} does not have enough text slots")
    return preset


def build_material_prompt(
    brief: dict[str, Any],
    case_selection: dict[str, Any] | None = None,
) -> str:
    content = brief["content"]
    art = brief["art_direction"]
    composition = brief["composition"]
    brand_rules = brief.get("brand", {}).get("rules", [])
    lines = [
        "Use case: product-mockup",
        "Asset type: isolated visual material for later exact-canvas composition",
        "Primary request: create the isolated subject for later exact-canvas composition",
        f"Subject: {content['subject']}",
        f"Style/medium: {art['style']}",
        f"Composition/framing: full subject visible with generous transparent margin; viewpoint: {composition['viewpoint']}",
        f"Lighting/mood: {art['lighting']}",
        f"Color palette: {'; '.join(art['palette'])}",
        f"Materials/textures: {'; '.join(art['materials'])}",
        "Background: genuinely transparent; preserve antialiased edges and natural shadow transparency",
        "Text: none; do not render any headline, label, logo, or placeholder copy",
        f"Must include: {'; '.join(content['must_include'])}",
        f"Constraints: {'; '.join(brand_rules) if brand_rules else 'none'}",
        f"Avoid: {'; '.join(content['must_avoid'])}",
        "Output only the isolated visual material, not the finished layout.",
    ]
    if case_selection is not None:
        material_prefixes = ("camera:", "lighting:", "material:", "style:")
        references = []
        for case in case_selection["cases"]:
            cues = [
                cue
                for cue in case["structure_cues"]
                if cue.startswith(material_prefixes)
            ]
            if cues:
                references.append(f"case {case['id']} [{', '.join(cues)}]")
        if references:
            lines.insert(
                3,
                "Structural references for the isolated material (generic cues only): "
                + "; ".join(references),
            )
            lines.insert(
                4,
                "Reference isolation: do not transfer case subjects, named people, "
                "product identity, brand names, logos, visible copy, or watermarks.",
            )
    return "\n".join(lines)


def build_material_request(
    brief: dict[str, Any],
    candidate_relative_path: str,
    *,
    authorized_by: str | None = None,
    case_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_relative_path = _portable_path_value(candidate_relative_path)
    prompt = build_material_prompt(brief, case_selection)
    prompt_sha256 = canonical_json_sha256(prompt)
    authorized = bool(authorized_by)
    recorded_at = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if authorized
        else None
    )
    return {
        "version": "0.1",
        "request_id": f"{brief['asset_id']}-material-{prompt_sha256[:12]}",
        "asset_id": brief["asset_id"],
        "status": "ready" if authorized else "awaiting_authorization",
        "authorization": {
            "required": True,
            "state": "authorized" if authorized else "pending",
            "scope": "single_material",
            "authorized_by": authorized_by,
            "recorded_at": recorded_at,
        },
        "provider_policy": {
            "provider": "codex-built-in-imagegen",
            "no_paid_api": True,
        },
        "prompt": prompt,
        "prompt_sha256": prompt_sha256,
        "case_selection_sha256": (
            canonical_json_sha256(case_selection)
            if case_selection is not None
            else None
        ),
        "case_ids": (
            [case["id"] for case in case_selection["cases"]]
            if case_selection is not None
            else []
        ),
        "requirements": {
            "role": "isolated_visual_material",
            "transparent_background": True,
            "no_text": True,
            "preserve_original": True,
        },
        "candidate": {"relative_path": candidate_relative_path},
    }


def inspect_material(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"material does not exist: {path}")
    with Image.open(path) as image:
        image.load()
        has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        if not has_alpha:
            raise ValueError("material must have a real alpha channel")
        alpha = image.convert("RGBA").getchannel("A")
        minimum_alpha, maximum_alpha = alpha.getextrema()
        if minimum_alpha == 255:
            raise ValueError("material alpha channel contains no transparency")
        if maximum_alpha == 0 or alpha.getbbox() is None:
            raise ValueError("material contains no visible pixels")
        width, height = image.size
    return {
        "sha256": file_sha256(path),
        "width": width,
        "height": height,
        "has_alpha": True,
    }


def build_composition_plan(
    brief: dict[str, Any],
    preset: dict[str, Any],
    material_path: Path,
    project_root: Path,
    *,
    provider: str = "codex-built-in-imagegen",
    model: str | None = None,
    font_path: str | None = None,
) -> dict[str, Any]:
    material = inspect_material(material_path)
    relative_material = portable_project_path(project_root, material_path)
    deliverable = brief["deliverable"]
    width = deliverable["width"]
    height = deliverable["height"]
    box = preset["raster_box"]
    raster_box = {
        "x": round(width * box["x"]),
        "y": round(height * box["y"]),
        "width": round(width * box["width"]),
        "height": round(height * box["height"]),
    }
    text_layers = []
    for text, slot in zip(
        brief["content"].get("exact_text", []),
        preset["text_slots"][: len(brief["content"].get("exact_text", []))],
        strict=True,
    ):
        font_size = round(height * slot["font_size"])
        font_size = max(
            slot["minimum_font_size"],
            min(slot["maximum_font_size"], font_size),
        )
        text_layers.append(
            {
                "text": text,
                "x": round(width * slot["x"]),
                "y": round(height * slot["y"]),
                "font_size": font_size,
                "max_width": round(width * slot["max_width"]),
                "fill": slot["fill"],
                "anchor": slot["anchor"],
                "font_path": font_path,
            }
        )
    return {
        "version": "0.1",
        "asset_id": brief["asset_id"],
        "canvas": {
            "width": width,
            "height": height,
            "format": "png",
            "transparent_background": preset["canvas"]["transparent_background"],
            "background": preset["canvas"]["background"],
        },
        "raster_layers": [
            {
                "source_path": relative_material,
                "source_sha256": material["sha256"],
                "source_type": "generated",
                "provider": provider,
                "model": model,
                "role": "isolated visual material",
                "trim_transparent": True,
                "fit": "contain",
                "box": raster_box,
            }
        ],
        "text_layers": text_layers,
    }
