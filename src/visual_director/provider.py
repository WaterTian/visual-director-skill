from __future__ import annotations

import multiprocessing
import queue
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from PIL import Image

from .asset_qc import file_sha256
from .capabilities import request_capability_blockers
from .json_io import canonical_json_sha256


class ProviderAdapter(Protocol):
    name: str
    model: str | None
    capabilities: dict[str, Any]

    def generate(self, request: dict[str, Any], candidate_path: Path) -> None:
        """Write one complete candidate atomically or raise an exception."""


class MockProviderAdapter:
    name = "mock"
    model = "solid-fixture-v1"
    capabilities = {
        "version": "0.1",
        "provider": "mock",
        "model": "solid-fixture-v1",
        "operations": ["create", "edit"],
        "output": {
            "formats": ["png", "jpeg", "webp"],
            "transparency": True,
            "dimension_policy": "exact",
            "supported_sizes": [],
            "dimension_constraints": None,
        },
        "input_images": {"supported": True, "maximum": None},
        "evidence": ["Deterministic local adapter implementation"],
    }

    def __init__(self, mode: str = "success", delay_seconds: float = 0.0) -> None:
        if mode not in {"success", "fail", "sleep"}:
            raise ValueError(f"unsupported mock mode: {mode}")
        self.mode = mode
        self.delay_seconds = delay_seconds

    def generate(self, request: dict[str, Any], candidate_path: Path) -> None:
        if self.mode == "fail":
            raise RuntimeError("mock provider failure")
        if self.mode == "sleep":
            time.sleep(self.delay_seconds)
            return

        output = request["output"]
        transparent = output["transparent_background"]
        image = Image.new(
            "RGBA" if transparent else "RGB",
            (output["width"], output["height"]),
            (236, 239, 244, 0) if transparent else (236, 239, 244),
        )
        format_name = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}[output["format"]]
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = candidate_path.with_name(f".{candidate_path.name}.provider-tmp")
        try:
            image.save(temporary, format=format_name)
            temporary.replace(candidate_path)
        finally:
            temporary.unlink(missing_ok=True)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _provider_worker(
    adapter: ProviderAdapter,
    request: dict[str, Any],
    candidate_path: Path,
    result_queue: Any,
) -> None:
    try:
        adapter.generate(request, candidate_path)
    except Exception as error:  # pragma: no cover - exercised across a process boundary
        result_queue.put({"ok": False, "message": str(error) or error.__class__.__name__})
    else:
        result_queue.put({"ok": True})


def execute_provider(
    adapter: ProviderAdapter,
    request: dict[str, Any],
    candidate_path: Path,
    *,
    timeout_seconds: float,
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    blockers = request_capability_blockers(request, adapter.capabilities)
    if blockers:
        raise ValueError("provider capability preflight failed: " + "; ".join(blockers))
    if candidate_path.exists():
        raise FileExistsError(f"candidate already exists: {candidate_path}")

    started_at = _utc_now()
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_provider_worker,
        args=(adapter, request, candidate_path, result_queue),
        daemon=False,
    )
    process.start()
    process.join(timeout_seconds)

    error: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    if process.is_alive():
        process.terminate()
        process.join(2)
        if process.is_alive():
            process.kill()
            process.join()
        candidate_path.unlink(missing_ok=True)
        status = "timed_out"
        error = {
            "code": "provider_timeout",
            "message": f"provider exceeded {timeout_seconds:g} seconds",
            "retryable": True,
        }
    else:
        try:
            result = result_queue.get(timeout=1)
        except queue.Empty:
            result = {
                "ok": False,
                "message": f"provider process exited without a result (exit={process.exitcode})",
            }
        if result["ok"] and candidate_path.is_file():
            status = "succeeded"
            candidate = {
                "name": candidate_path.name,
                "sha256": file_sha256(candidate_path),
                "size_bytes": candidate_path.stat().st_size,
            }
        else:
            candidate_path.unlink(missing_ok=True)
            status = "failed"
            error = {
                "code": "provider_failed",
                "message": result.get("message", "provider did not create a candidate"),
                "retryable": False,
            }
    result_queue.close()
    result_queue.join_thread()

    return {
        "version": "0.1",
        "attempt_id": f"{request['request_id']}-{canonical_json_sha256(started_at)[:12]}",
        "asset_id": request["asset_id"],
        "request_sha256": canonical_json_sha256(request),
        "adapter": {"name": adapter.name, "model": adapter.model},
        "status": status,
        "started_at": started_at,
        "finished_at": _utc_now(),
        "timeout_seconds": timeout_seconds,
        "candidate": candidate,
        "error": error,
    }
