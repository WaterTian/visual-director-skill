from __future__ import annotations

import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from .asset_qc import file_sha256
from .json_io import canonical_json_sha256


def reconcile_manifest_qc(
    manifest: dict[str, Any], qc_report: dict[str, Any]
) -> dict[str, Any]:
    if manifest["asset_id"] != qc_report["asset_id"]:
        raise ValueError("manifest and QC asset_id do not match")
    if manifest["file"]["sha256"] != qc_report["candidate_sha256"]:
        raise ValueError("manifest and QC candidate hashes do not match")
    if manifest["status"] in {"approved", "landed"}:
        raise ValueError(f"cannot reconcile QC after manifest is {manifest['status']}")

    result = deepcopy(manifest)
    status_map = {"fail": "qc_failed", "review_required": "candidate", "pass": "qc_passed"}
    result["status"] = status_map[qc_report["overall_status"]]
    result["qc"] = {
        "overall_status": qc_report["overall_status"],
        "report_sha256": canonical_json_sha256(qc_report),
    }
    return result


def _atomic_copy(source: Path, destination: Path, *, overwrite: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        if file_sha256(temporary) != file_sha256(source):
            raise OSError("copied asset hash mismatch")
        if overwrite:
            temporary.replace(destination)
        else:
            os.link(temporary, destination)
            temporary.unlink()
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def promote_asset(
    candidate_path: Path,
    destination: Path,
    manifest: dict[str, Any],
    qc_report: dict[str, Any],
    approval: dict[str, Any],
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    if manifest["status"] != "qc_passed":
        raise ValueError(f"manifest must be qc_passed, got {manifest['status']}")
    if qc_report["overall_status"] != "pass":
        raise ValueError("QC report must pass before promotion")
    if canonical_json_sha256(qc_report) != manifest["qc"]["report_sha256"]:
        raise ValueError("QC report hash does not match manifest")
    if approval["asset_id"] != manifest["asset_id"]:
        raise ValueError("approval and manifest asset_id do not match")
    if approval["decision"] != "approve":
        raise ValueError("approval decision must be approve")
    if not candidate_path.is_file():
        raise FileNotFoundError(f"candidate does not exist: {candidate_path}")
    if file_sha256(candidate_path) != manifest["file"]["sha256"]:
        raise ValueError("candidate file hash does not match manifest")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"destination already exists: {destination}")

    _atomic_copy(candidate_path, destination, overwrite=overwrite)
    result = deepcopy(manifest)
    result["status"] = "landed"
    result["file"]["name"] = destination.name
    result["approvals"].append(
        {
            "reviewer": approval["reviewer"],
            "decision": approval["decision"],
            "recorded_at": approval["recorded_at"],
            "exceptions": approval["exceptions"],
        }
    )
    return result
