#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


FORBIDDEN_DIRECTORIES = {".venv", "__pycache__", "outputs", "work"}
FORBIDDEN_FILENAMES = {".env"}
FORBIDDEN_SUFFIXES = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}
SECRET_PATTERN = re.compile(rb"sk-[A-Za-z0-9_-]{16,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a built Visual Director Plugin and write deterministic "
            "release checksums."
        )
    )
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checksums", type=Path, required=True)
    return parser.parse_args()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_within(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    temporary.replace(path)


def build_release_manifest(package: Path) -> tuple[dict, str]:
    package = package.resolve()
    plugin_manifest_path = package / ".codex-plugin" / "plugin.json"
    if not plugin_manifest_path.is_file():
        raise ValueError(f"plugin manifest not found: {plugin_manifest_path}")

    plugin_manifest = json.loads(plugin_manifest_path.read_text(encoding="utf-8"))
    if plugin_manifest.get("name") != package.name:
        raise ValueError("plugin name must match the package directory")
    if plugin_manifest.get("author") != {"name": "WaterTian"}:
        raise ValueError("plugin author must be exactly WaterTian")
    developer = plugin_manifest.get("interface", {}).get("developerName")
    if developer != "WaterTian":
        raise ValueError("plugin developerName must be exactly WaterTian")

    files: list[dict] = []
    for path in sorted(package.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in the release package: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(package)
        if any(part in FORBIDDEN_DIRECTORIES for part in relative.parts):
            raise ValueError(f"forbidden directory in release package: {relative}")
        if path.name in FORBIDDEN_FILENAMES or path.name.startswith(".env."):
            raise ValueError(f"forbidden file in release package: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise ValueError(f"raster image in release package: {relative}")

        data = path.read_bytes()
        if b"/Users/" in data:
            raise ValueError(f"machine-specific path in release package: {relative}")
        if b"OPENAI_API_KEY=" in data or SECRET_PATTERN.search(data):
            raise ValueError(f"possible secret in release package: {relative}")
        files.append(
            {
                "path": relative.as_posix(),
                "bytes": len(data),
                "sha256": _sha256(data),
            }
        )

    checksum_text = "".join(
        f"{item['sha256']}  {item['path']}\n" for item in files
    )
    document = {
        "schema_version": "0.1",
        "plugin": {
            "name": plugin_manifest["name"],
            "version": plugin_manifest["version"],
            "author": "WaterTian",
            "developer": "WaterTian",
        },
        "package": {
            "file_count": len(files),
            "total_bytes": sum(item["bytes"] for item in files),
            "tree_sha256": _sha256(checksum_text.encode("utf-8")),
            "tree_hash_definition": "sha256(utf8(sorted '<file_sha256>  <relative_path>\\n'))",
        },
        "files": files,
    }
    return document, checksum_text


def main() -> int:
    args = parse_args()
    package = args.package.resolve()
    output = args.output.resolve()
    checksums = args.checksums.resolve()
    try:
        if output == checksums:
            raise ValueError("manifest and checksum paths must be different")
        if _is_within(package, output) or _is_within(package, checksums):
            raise ValueError("release metadata must be written outside the package")
        if output.exists() or checksums.exists():
            raise FileExistsError("release manifest or checksum output already exists")
        document, checksum_text = build_release_manifest(package)
        manifest_data = (
            json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        _atomic_write(output, manifest_data)
        _atomic_write(checksums, checksum_text.encode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"release manifest failed: {error}", file=sys.stderr)
        return 2

    print(
        f"release manifest: {document['plugin']['name']} "
        f"{document['plugin']['version']} -> {output} "
        f"(tree_sha256={document['package']['tree_sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
