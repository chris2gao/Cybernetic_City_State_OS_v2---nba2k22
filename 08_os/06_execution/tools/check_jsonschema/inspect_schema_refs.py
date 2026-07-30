from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlsplit


REFERENCE_KEYWORDS = frozenset({"$ref", "$dynamicRef", "$recursiveRef"})
IDENTIFIER_KEYWORDS = frozenset({"$id", "id"})
HTTP_SCHEMES = frozenset({"http", "https"})
EXIT_POLICY_FAILURE = 65


class SchemaPolicyError(ValueError):
    def __init__(self, code: str, location: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.location = location
        self.detail = detail


def _child_location(location: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{location}[{key}]"
    return f"{location}[{json.dumps(key, ensure_ascii=False)}]"


def _walk(value: Any, location: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = _child_location(location, key)
            if key in REFERENCE_KEYWORDS:
                if not isinstance(child, str):
                    raise SchemaPolicyError(
                        "CJV-R01-REFERENCE-TYPE",
                        child_location,
                        f"{key} must be a string",
                    )
                if not child.startswith("#"):
                    raise SchemaPolicyError(
                        "CJV-R01-EXTERNAL-REFERENCE",
                        child_location,
                        f"{key} must be fragment-only; got {json.dumps(child)}",
                    )
            elif key in IDENTIFIER_KEYWORDS and isinstance(child, str):
                scheme = urlsplit(child).scheme.lower()
                if scheme in HTTP_SCHEMES:
                    raise SchemaPolicyError(
                        "CJV-R01-REMOTE-IDENTIFIER",
                        child_location,
                        f"{key} must not use HTTP(S); got {json.dumps(child)}",
                    )
            _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk(child, _child_location(location, index))


def inspect_schema(path: Path) -> None:
    if path.suffix.lower() != ".json":
        raise SchemaPolicyError(
            "CJV-R01-JSON-SUFFIX",
            "$",
            "canonical schema must use the .json suffix",
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SchemaPolicyError(
            "CJV-R01-SCHEMA-READ",
            "$",
            f"schema could not be read: {exc.__class__.__name__}",
        ) from exc
    try:
        schema = json.loads(text)
    except (UnicodeError, json.JSONDecodeError) as exc:
        detail = f"strict JSON parse failed: {exc.__class__.__name__}"
        if isinstance(exc, json.JSONDecodeError):
            detail += f" at line {exc.lineno} column {exc.colno}"
        raise SchemaPolicyError(
            "CJV-R01-STRICT-JSON",
            "$",
            detail,
        ) from exc
    _walk(schema)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "schema reference policy: FAIL [CJV-R01-USAGE] expected one schema path",
            file=sys.stderr,
        )
        return EXIT_POLICY_FAILURE
    try:
        inspect_schema(Path(argv[1]))
    except SchemaPolicyError as exc:
        print(
            f"schema reference policy: FAIL [{exc.code}] "
            f"at {exc.location}: {exc.detail}",
            file=sys.stderr,
        )
        return EXIT_POLICY_FAILURE
    print("schema reference policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
