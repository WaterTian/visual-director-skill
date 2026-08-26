from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .asset_qc import file_sha256
from .capabilities import request_capability_blockers
from .json_io import canonical_json_sha256


def _portable_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        Path(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or path.is_absolute()
        or ".." in path.parts
    ):
        raise ValueError("candidate path must be project-relative and cannot contain '..'")
    if not normalized or normalized in {".", "./"}:
        raise ValueError("candidate path must name a file")
    return path.as_posix()


def prepare_generation_handoff(
    request: dict[str, Any],
    candidate_path: str,
    *,
    authorized_by: str | None = None,
    capabilities: dict[str, Any] | None = None,
    unverified_dimension_exception: str | None = None,
) -> dict[str, Any]:
    relative_path = _portable_relative_path(candidate_path)
    authorized = bool(authorized_by)
    if authorized and capabilities is None:
        raise ValueError("authorized handoff requires provider capabilities preflight")
    blockers = request_capability_blockers(request, capabilities) if capabilities else []
    if unverified_dimension_exception and not authorized:
        raise ValueError("capability exception requires an authorized handoff")
    if authorized and blockers:
        overridable_prefix = "provider dimension policy 'unverified' cannot guarantee exact "
        non_overridable = [
            blocker for blocker in blockers if not blocker.startswith(overridable_prefix)
        ]
        if non_overridable or not unverified_dimension_exception:
            raise ValueError("provider capability preflight failed: " + "; ".join(blockers))
    exception_reason = (
        unverified_dimension_exception.strip()
        if unverified_dimension_exception
        else None
    )
    if unverified_dimension_exception and not exception_reason:
        raise ValueError("capability exception reason must not be empty")
    recorded_at = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if authorized
        else None
    )
    return {
        "version": "0.1",
        "handoff_id": f"{request['request_id']}-handoff",
        "asset_id": request["asset_id"],
        "request_sha256": canonical_json_sha256(request),
        "status": "ready" if authorized else "awaiting_authorization",
        "authorization": {
            "required": True,
            "state": "authorized" if authorized else "pending",
            "scope": "single_candidate",
            "authorized_by": authorized_by,
            "recorded_at": recorded_at,
        },
        "operation": request["operation"],
        "prompt": request["prompt"],
        "output": request["output"],
        "input_images": request["input_images"],
        "invariants": request["invariants"],
        "candidate": {
            "relative_path": relative_path,
            "preserve_original": True,
        },
        "result": None,
        "capabilities_sha256": (
            canonical_json_sha256(capabilities) if capabilities is not None else None
        ),
        "capability_blockers": blockers,
        "capability_exception_reason": exception_reason,
    }


def record_generation_result(
    handoff: dict[str, Any],
    candidate_path: Path,
    *,
    provider: str,
    model: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    if handoff["status"] != "ready":
        raise ValueError(f"handoff must be ready, got {handoff['status']}")
    if handoff["authorization"]["state"] != "authorized":
        raise ValueError("handoff is not authorized")
    if not provider.strip():
        raise ValueError("provider must not be empty")
    if not candidate_path.is_file():
        raise FileNotFoundError(f"candidate does not exist: {candidate_path}")
    expected_name = PurePosixPath(handoff["candidate"]["relative_path"]).name
    if candidate_path.name != expected_name:
        raise ValueError(
            f"candidate filename does not match handoff: expected {expected_name}, got {candidate_path.name}"
        )

    input_records: list[dict[str, Any]] = []
    if handoff["input_images"]:
        if project_root is None:
            raise ValueError("project_root is required to hash generation input images")
        root = project_root.resolve()
        for item in handoff["input_images"]:
            relative = _portable_relative_path(item["uri"])
            source = (root / relative).resolve()
            if source != root and root not in source.parents:
                raise ValueError("generation input image must be inside project_root")
            if not source.is_file():
                raise FileNotFoundError(f"generation input image does not exist: {source}")
            input_records.append(
                {
                    "uri": relative,
                    "role": item["role"],
                    "sha256": file_sha256(source),
                    "size_bytes": source.stat().st_size,
                }
            )

    result = deepcopy(handoff)
    result["status"] = "completed"
    result["result"] = {
        "provider": provider.strip(),
        "model": model,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "name": candidate_path.name,
        "sha256": file_sha256(candidate_path),
        "size_bytes": candidate_path.stat().st_size,
        "inputs": input_records,
    }
    return result
