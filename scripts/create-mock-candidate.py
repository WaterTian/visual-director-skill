#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.json_io import load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a deterministic metadata-only mock candidate.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    brief = load_json(args.brief)
    schema = load_json(ROOT / "schemas" / "visual-brief.schema.json")
    errors = validate_document(brief, schema)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1

    deliverable = brief["deliverable"]
    transparent = bool(deliverable.get("transparent_background", False))
    mode = "RGBA" if transparent else "RGB"
    background = (235, 238, 242, 0) if transparent else (235, 238, 242)
    image = Image.new(mode, (deliverable["width"], deliverable["height"]), background)
    draw = ImageDraw.Draw(image)
    line_color = (75, 85, 99, 255) if transparent else (75, 85, 99)
    draw.line((0, 0, deliverable["width"], deliverable["height"]), fill=line_color, width=3)
    draw.line((deliverable["width"], 0, 0, deliverable["height"]), fill=line_color, width=3)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_format = "JPEG" if deliverable["format"] == "jpeg" else deliverable["format"].upper()
    if save_format == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")
    image.save(args.output, format=save_format)
    print(f"created metadata-only mock candidate at {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

