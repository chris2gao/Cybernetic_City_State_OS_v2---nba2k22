from __future__ import annotations

import json
from pathlib import Path

import pytest

from target import inspect_schema_refs as subject


def write_schema(tmp_path: Path, payload: object, suffix: str = ".json") -> Path:
    path = tmp_path / f"schema{suffix}"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def assert_policy_error(
    tmp_path: Path,
    payload: object,
    code: str,
    location: str,
) -> subject.SchemaPolicyError:
    path = write_schema(tmp_path, payload)
    with pytest.raises(subject.SchemaPolicyError) as caught:
        subject.inspect_schema(path)
    assert caught.value.code == code
    assert caught.value.location == location
    assert caught.value.detail
    return caught.value


def test_fragment_only_refs_and_schema_dialect_are_allowed(tmp_path: Path) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": {"value": {"type": "integer"}},
        "$ref": "#/$defs/value",
        "items": {
            "$dynamicRef": "#node",
            "$recursiveRef": "#",
        },
    }
    subject.inspect_schema(write_schema(tmp_path, schema))


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("$ref", "https://example.invalid/schema.json"),
        ("$dynamicRef", "http://example.invalid/node"),
        ("$recursiveRef", "other.json#node"),
        ("$ref", "/absolute/schema.json"),
    ],
)
def test_external_references_are_rejected(
    tmp_path: Path,
    keyword: str,
    value: str,
) -> None:
    error = assert_policy_error(
        tmp_path,
        {keyword: value},
        "CJV-R01-EXTERNAL-REFERENCE",
        f'$["{keyword}"]',
    )
    assert "fragment-only" in error.detail


@pytest.mark.parametrize("keyword", ["$ref", "$dynamicRef", "$recursiveRef"])
def test_reference_keywords_must_be_strings(
    tmp_path: Path,
    keyword: str,
) -> None:
    error = assert_policy_error(
        tmp_path,
        {keyword: 7},
        "CJV-R01-REFERENCE-TYPE",
        f'$["{keyword}"]',
    )
    assert "must be a string" in error.detail


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("$id", "https://example.invalid/schema"),
        ("id", "http://example.invalid/legacy"),
        ("$id", "HTTPS://example.invalid/schema"),
    ],
)
def test_remote_identifiers_are_rejected(
    tmp_path: Path,
    keyword: str,
    value: str,
) -> None:
    error = assert_policy_error(
        tmp_path,
        {keyword: value},
        "CJV-R01-REMOTE-IDENTIFIER",
        f'$["{keyword}"]',
    )
    assert "HTTP(S)" in error.detail


def test_nested_location_is_stable(tmp_path: Path) -> None:
    error = assert_policy_error(
        tmp_path,
        {"allOf": [{"properties": {"value": {"$ref": "other.json"}}}]},
        "CJV-R01-EXTERNAL-REFERENCE",
        '$["allOf"][0]["properties"]["value"]["$ref"]',
    )
    assert '"other.json"' in error.detail


def test_non_json_suffix_is_rejected(tmp_path: Path) -> None:
    path = write_schema(tmp_path, {}, suffix=".yaml")
    with pytest.raises(subject.SchemaPolicyError) as caught:
        subject.inspect_schema(path)
    assert caught.value.code == "CJV-R01-JSON-SUFFIX"
    assert caught.value.location == "$"


def test_uppercase_json_suffix_is_allowed(tmp_path: Path) -> None:
    subject.inspect_schema(write_schema(tmp_path, {}, suffix=".JSON"))


def test_damaged_json_is_rejected_with_stable_location(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('{"type":', encoding="utf-8")
    with pytest.raises(subject.SchemaPolicyError) as caught:
        subject.inspect_schema(path)
    assert caught.value.code == "CJV-R01-STRICT-JSON"
    assert caught.value.location == "$"
    assert "line 1" in caught.value.detail
    assert "column" in caught.value.detail


def test_unreadable_schema_is_rejected(tmp_path: Path) -> None:
    path = write_schema(tmp_path, {})
    path.chmod(0)
    try:
        with pytest.raises(subject.SchemaPolicyError) as caught:
            subject.inspect_schema(path)
    finally:
        path.chmod(0o600)
    assert caught.value.code == "CJV-R01-SCHEMA-READ"
    assert caught.value.location == "$"
    assert "PermissionError" in caught.value.detail


def test_main_usage_failure_is_short_and_stable(capsys: pytest.CaptureFixture[str]) -> None:
    assert subject.main(["inspect_schema_refs.py"]) == 65
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        "schema reference policy: FAIL [CJV-R01-USAGE] "
        "expected one schema path\n"
    )


def test_main_policy_failure_reports_code_and_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = write_schema(tmp_path, {"$ref": "remote.json"})
    assert subject.main(["inspect_schema_refs.py", str(path)]) == 65
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "[CJV-R01-EXTERNAL-REFERENCE]" in captured.err
    assert 'at $["$ref"]:' in captured.err


def test_main_success_is_short_and_stable(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = write_schema(tmp_path, {"$ref": "#"})
    assert subject.main(["inspect_schema_refs.py", str(path)]) == 0
    captured = capsys.readouterr()
    assert captured.out == "schema reference policy: PASS\n"
    assert captured.err == ""
