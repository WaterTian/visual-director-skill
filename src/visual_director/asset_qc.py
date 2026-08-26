from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

FORMAT_MAP = {"JPG": "jpeg", "JPEG": "jpeg", "PNG": "png", "WEBP": "webp"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check(check_id: str, passed: bool, evidence: str) -> dict[str, str]:
    return {"id": check_id, "status": "pass" if passed else "fail", "evidence": evidence}


def inspect_asset(path: Path, brief: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        with Image.open(path) as image:
            image.load()
            detected_format = FORMAT_MAP.get(str(image.format).upper(), str(image.format).lower())
            width, height = image.size
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"candidate is not a readable supported image: {error}") from error

    size_bytes = path.stat().st_size
    sha256 = file_sha256(path)
    expected = brief["deliverable"]
    expected_alpha = bool(expected.get("transparent_background", False))
    actual_ratio = width / height
    expected_ratio = expected["width"] / expected["height"]
    automatic_checks = [
        _check("file-readable", True, f"opened {detected_format} image successfully"),
        _check(
            "format",
            detected_format == expected["format"],
            f"expected {expected['format']}; detected {detected_format}",
        ),
        _check(
            "dimensions",
            (width, height) == (expected["width"], expected["height"]),
            f"expected {expected['width']}x{expected['height']}; detected {width}x{height}",
        ),
        _check(
            "aspect-ratio",
            abs(actual_ratio - expected_ratio) <= 0.001,
            f"expected {expected_ratio:.6f}; detected {actual_ratio:.6f}",
        ),
        _check(
            "alpha-channel",
            has_alpha == expected_alpha,
            f"expected alpha={str(expected_alpha).lower()}; detected alpha={str(has_alpha).lower()}",
        ),
    ]
    visual_requirements = [
        *(f'exact text: "{item}"' for item in brief["content"]["exact_text"]),
        *(f"must include: {item}" for item in brief["content"]["must_include"]),
        *(f"must avoid: {item}" for item in brief["content"]["must_avoid"]),
        *brief["qa"]["visual_checks"],
    ]
    visual_checks = [
        {"requirement": requirement, "status": "not_reviewed", "evidence": ""}
        for requirement in dict.fromkeys(visual_requirements)
    ]
    failed_ids = [item["id"] for item in automatic_checks if item["status"] == "fail"]
    if failed_ids:
        overall_status = "fail"
        blockers = [f"automatic check failed: {check_id}" for check_id in failed_ids]
    elif visual_checks:
        overall_status = "review_required"
        blockers = ["visual review pending"]
    else:
        overall_status = "pass"
        blockers = []
    file_record = {
        "name": path.name,
        "format": detected_format,
        "width": width,
        "height": height,
        "has_alpha": has_alpha,
        "size_bytes": size_bytes,
    }
    report = {
        "version": "0.1",
        "asset_id": brief["asset_id"],
        "candidate_sha256": sha256,
        "overall_status": overall_status,
        "file": file_record,
        "automatic_checks": automatic_checks,
        "visual_checks": visual_checks,
        "review": None,
        "blockers": blockers,
    }
    metadata = {**file_record, "sha256": sha256}
    return report, metadata
