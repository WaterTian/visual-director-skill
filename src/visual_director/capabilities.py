from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Any


def _constraint_failures(
    width: int, height: int, constraints: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    multiple = constraints["edge_multiple"]
    if width % multiple or height % multiple:
        failures.append(f"both edges must be multiples of {multiple}")
    if max(width, height) > constraints["maximum_edge"]:
        failures.append(f"maximum edge is {constraints['maximum_edge']}px")
    ratio = max(width, height) / min(width, height)
    if ratio > constraints["maximum_ratio"]:
        failures.append(f"long-to-short ratio exceeds {constraints['maximum_ratio']}:1")
    pixels = width * height
    if pixels < constraints["minimum_pixels"]:
        failures.append(f"total pixels are below {constraints['minimum_pixels']}")
    if pixels > constraints["maximum_pixels"]:
        failures.append(f"total pixels exceed {constraints['maximum_pixels']}")
    return failures


def request_capability_blockers(
    request: dict[str, Any], capabilities: dict[str, Any]
) -> list[str]:
    blockers: list[str] = []
    if request["operation"] not in capabilities["operations"]:
        blockers.append(f"provider does not support operation: {request['operation']}")

    output = request["output"]
    provider_output = capabilities["output"]
    if output["format"] not in provider_output["formats"]:
        blockers.append(f"provider does not support output format: {output['format']}")
    if output["transparent_background"] and not provider_output["transparency"]:
        blockers.append("provider does not support transparent output")

    dimension_policy = provider_output["dimension_policy"]
    if dimension_policy == "fixed_presets":
        requested_size = (output["width"], output["height"])
        supported_sizes = {
            (item["width"], item["height"])
            for item in provider_output["supported_sizes"]
        }
        if requested_size not in supported_sizes:
            blockers.append(
                f"provider does not support exact size: {requested_size[0]}x{requested_size[1]}"
            )
    elif dimension_policy == "constrained_exact":
        failures = _constraint_failures(
            output["width"],
            output["height"],
            provider_output["dimension_constraints"],
        )
        blockers.extend(
            f"provider exact-size constraint failed: {failure}" for failure in failures
        )
    elif dimension_policy in {"aspect_only", "unverified"}:
        blockers.append(
            f"provider dimension policy '{dimension_policy}' cannot guarantee exact "
            f"{output['width']}x{output['height']} output"
        )

    input_images = request["input_images"]
    input_capabilities = capabilities["input_images"]
    if input_images and not input_capabilities["supported"]:
        blockers.append("provider does not support input images")
    maximum = input_capabilities["maximum"]
    if maximum is not None and len(input_images) > maximum:
        blockers.append(
            f"provider supports at most {maximum} input images; request has {len(input_images)}"
        )
    return blockers


def suggest_compatible_sizes(
    request: dict[str, Any],
    capabilities: dict[str, Any],
    *,
    limit: int = 3,
) -> list[dict[str, int]]:
    if limit <= 0:
        return []
    provider_output = capabilities["output"]
    if provider_output["dimension_policy"] != "constrained_exact":
        return []
    constraints = provider_output["dimension_constraints"]
    target_width = request["output"]["width"]
    target_height = request["output"]["height"]
    ratio = Fraction(target_width, target_height)
    edge_multiple = constraints["edge_multiple"]
    scale_multiple = 1
    for base_edge in (ratio.numerator, ratio.denominator):
        scale_multiple = scale_multiple * (
            edge_multiple // gcd(base_edge * scale_multiple, edge_multiple)
        )

    maximum_scale = constraints["maximum_edge"] // max(
        ratio.numerator, ratio.denominator
    )
    candidates: list[tuple[float, int, int]] = []
    for scale in range(scale_multiple, maximum_scale + 1, scale_multiple):
        width = ratio.numerator * scale
        height = ratio.denominator * scale
        if _constraint_failures(width, height, constraints):
            continue
        distance = (
            ((width - target_width) / target_width) ** 2
            + ((height - target_height) / target_height) ** 2
        )
        candidates.append((distance, width, height))
    candidates.sort(key=lambda item: (item[0], item[1] * item[2]))
    return [
        {"width": width, "height": height}
        for _, width, height in candidates[:limit]
    ]
