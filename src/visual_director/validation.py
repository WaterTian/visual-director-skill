from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


@dataclass(frozen=True)
class FieldError:
    path: str
    message: str
    rule: str


def _required_property(error: ValidationError) -> str | None:
    if error.validator != "required":
        return None
    if not isinstance(error.validator_value, list):
        return None
    instance = error.instance if isinstance(error.instance, dict) else {}
    return next((name for name in error.validator_value if name not in instance), None)


def _json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif str(part).isidentifier():
            result += f".{part}"
        else:
            escaped = str(part).replace("'", "\\'")
            result += f"['{escaped}']"
    return result


def validate_document(document: Any, schema: dict[str, Any]) -> list[FieldError]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[FieldError] = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path)):
        path = list(error.absolute_path)
        missing = _required_property(error)
        if missing is not None:
            path.append(missing)
        errors.append(
            FieldError(
                path=_json_path(path),
                message=error.message,
                rule=str(error.validator),
            )
        )
    return errors
