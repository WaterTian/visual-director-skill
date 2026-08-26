#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visual_director.handoff import prepare_generation_handoff
from visual_director.json_io import atomic_write_json, load_json
from visual_director.validation import validate_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare an authorization-gated external generation handoff.")
    parser.add_argument("request", type=Path)
    parser.add_argument("--candidate", required=True, help="Project-relative candidate path")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--authorized-by", help="Record the current explicit single-candidate authorization")
    parser.add_argument("--capabilities", type=Path, help="ProviderCapabilities JSON used for preflight")
    parser.add_argument(
        "--accept-unverified-dimensions",
        action="store_true",
        help="Allow only an unverified-dimension blocker for one explicit smoke candidate",
    )
    parser.add_argument(
        "--exception-reason",
        help="Required audit reason when --accept-unverified-dimensions is used",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.accept_unverified_dimensions and not args.exception_reason:
            raise ValueError(
                "--exception-reason is required with --accept-unverified-dimensions"
            )
        if args.exception_reason and not args.accept_unverified_dimensions:
            raise ValueError(
                "--exception-reason requires --accept-unverified-dimensions"
            )
        request = load_json(args.request)
        request_schema = load_json(ROOT / "schemas" / "generation-request.schema.json")
        request_errors = validate_document(request, request_schema)
        if request_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in request_errors[:8])
            raise ValueError(summary)
        capabilities = load_json(args.capabilities) if args.capabilities else None
        if capabilities is not None:
            capabilities_schema = load_json(
                ROOT / "schemas" / "provider-capabilities.schema.json"
            )
            capabilities_errors = validate_document(capabilities, capabilities_schema)
            if capabilities_errors:
                summary = "; ".join(
                    f"{error.path}: {error.message}"
                    for error in capabilities_errors[:8]
                )
                raise ValueError(summary)
        handoff = prepare_generation_handoff(
            request,
            args.candidate,
            authorized_by=args.authorized_by,
            capabilities=capabilities,
            unverified_dimension_exception=(
                args.exception_reason
                if args.accept_unverified_dimensions
                else None
            ),
        )
        handoff_schema = load_json(ROOT / "schemas" / "generation-handoff.schema.json")
        handoff_errors = validate_document(handoff, handoff_schema)
        if handoff_errors:
            summary = "; ".join(f"{error.path}: {error.message}" for error in handoff_errors[:8])
            raise ValueError(summary)
        atomic_write_json(args.output, handoff)
    except (OSError, ValueError) as error:
        print(f"handoff preparation failed: {error}", file=sys.stderr)
        return 2
    print(f"handoff {handoff['status']}: {handoff['handoff_id']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
