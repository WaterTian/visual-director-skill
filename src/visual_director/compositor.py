from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .asset_qc import file_sha256
from .json_io import canonical_json_sha256


def _project_file(project_root: Path, relative_path: str) -> tuple[Path, str]:
    normalized = relative_path.replace("\\", "/")
    portable = PurePosixPath(normalized)
    if (
        not normalized
        or portable.is_absolute()
        or PureWindowsPath(relative_path).is_absolute()
        or ".." in portable.parts
    ):
        raise ValueError("composition paths must be project-relative and cannot contain '..'")
    root = project_root.resolve()
    resolved = (root / Path(*portable.parts)).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("composition path resolves outside project root")
    return resolved, portable.as_posix()


def _fit_layer(
    image: Image.Image,
    layer: dict[str, Any],
) -> tuple[Image.Image, int, int, bool]:
    box = layer["box"]
    source_width, source_height = image.size
    if layer["fit"] == "native":
        if source_width > box["width"] or source_height > box["height"]:
            raise ValueError("native raster layer does not fit inside its box")
        rendered = image
    else:
        scale = min(box["width"] / source_width, box["height"] / source_height)
        rendered_size = (
            max(1, round(source_width * scale)),
            max(1, round(source_height * scale)),
        )
        rendered = (
            image
            if rendered_size == image.size
            else image.resize(rendered_size, Image.Resampling.LANCZOS)
        )
    x = box["x"] + (box["width"] - rendered.width) // 2
    y = box["y"] + (box["height"] - rendered.height) // 2
    return rendered, x, y, rendered.size != image.size


def compose_exact_canvas(
    plan: dict[str, Any],
    project_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"composition output already exists: {output_path}")
    canvas_spec = plan["canvas"]
    width = canvas_spec["width"]
    height = canvas_spec["height"]
    background = ImageColor.getrgb(canvas_spec["background"])
    alpha = 0 if canvas_spec["transparent_background"] else 255
    canvas = Image.new("RGBA", (width, height), (*background, alpha))

    raster_transforms: list[dict[str, Any]] = []
    for layer in plan["raster_layers"]:
        box = layer["box"]
        if box["x"] + box["width"] > width or box["y"] + box["height"] > height:
            raise ValueError("raster layer box extends beyond the canvas")
        source_path, portable_path = _project_file(
            project_root,
            layer["source_path"],
        )
        if not source_path.is_file():
            raise FileNotFoundError(f"raster source does not exist: {portable_path}")
        actual_sha256 = file_sha256(source_path)
        if actual_sha256 != layer["source_sha256"]:
            raise ValueError(f"raster source hash mismatch: {portable_path}")
        with Image.open(source_path) as source:
            source.load()
            rgba = source.convert("RGBA")
        working = rgba
        source_crop = None
        if layer["trim_transparent"]:
            alpha_box = rgba.getchannel("A").getbbox()
            if alpha_box is None:
                raise ValueError(f"transparent raster source is empty: {portable_path}")
            left, top, right, bottom = alpha_box
            working = rgba.crop(alpha_box)
            source_crop = {
                "x": left,
                "y": top,
                "width": right - left,
                "height": bottom - top,
            }
        rendered, x, y, resampled = _fit_layer(working, layer)
        canvas.alpha_composite(rendered, (x, y))
        raster_transforms.append(
            {
                "source_path": portable_path,
                "source_sha256": actual_sha256,
                "source_type": layer["source_type"],
                "provider": layer["provider"],
                "model": layer["model"],
                "role": layer["role"],
                "trim_transparent": layer["trim_transparent"],
                "fit": layer["fit"],
                "original_size": {"width": rgba.width, "height": rgba.height},
                "source_crop": source_crop,
                "rendered_size": {
                    "width": rendered.width,
                    "height": rendered.height,
                },
                "position": {"x": x, "y": y},
                "resampled": resampled,
            }
        )

    draw = ImageDraw.Draw(canvas)
    rendered_text: list[dict[str, Any]] = []
    for layer in plan["text_layers"]:
        font_path_value = layer["font_path"]
        if font_path_value is None:
            font = ImageFont.load_default(size=layer["font_size"])
            font_name = "pillow-default"
            font_sha256 = None
        else:
            font_path, font_name = _project_file(project_root, font_path_value)
            if not font_path.is_file():
                raise FileNotFoundError(f"font does not exist: {font_name}")
            font = ImageFont.truetype(font_path, layer["font_size"])
            font_sha256 = file_sha256(font_path)
        text_bbox = draw.textbbox(
            (layer["x"], layer["y"]),
            layer["text"],
            font=font,
            anchor=layer["anchor"],
        )
        left, top, right, bottom = text_bbox
        if left < 0 or top < 0 or right > width or bottom > height:
            raise ValueError(f"text layer extends beyond the canvas: {layer['text']}")
        max_width = layer.get("max_width")
        if max_width is not None and right - left > max_width:
            raise ValueError(
                f"text layer does not fit preset width: {layer['text']}"
            )
        draw.text(
            (layer["x"], layer["y"]),
            layer["text"],
            fill=ImageColor.getrgb(layer["fill"]),
            font=font,
            anchor=layer["anchor"],
        )
        rendered_text.append(
            {
                "text": layer["text"],
                "position": {"x": layer["x"], "y": layer["y"]},
                "font_size": layer["font_size"],
                "max_width": max_width,
                "fill": layer["fill"],
                "anchor": layer["anchor"],
                "font": font_name,
                "rendered_bbox": {
                    "x": left,
                    "y": top,
                    "width": right - left,
                    "height": bottom - top,
                },
                "font_sha256": font_sha256,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.composition-tmp")
    try:
        final_image = (
            canvas
            if canvas_spec["transparent_background"]
            else canvas.convert("RGB")
        )
        final_image.save(temporary, format="PNG")
        temporary.replace(output_path)
    finally:
        temporary.unlink(missing_ok=True)

    return {
        "version": "0.1",
        "asset_id": plan["asset_id"],
        "plan_sha256": canonical_json_sha256(plan),
        "raster_transforms": raster_transforms,
        "text_layers": rendered_text,
        "output": {
            "name": output_path.name,
            "sha256": file_sha256(output_path),
            "format": "png",
            "width": width,
            "height": height,
            "has_alpha": canvas_spec["transparent_background"],
            "size_bytes": output_path.stat().st_size,
        },
    }
