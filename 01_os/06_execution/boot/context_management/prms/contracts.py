"""Versioned record validation shared by writers and recovery consumers."""
from datetime import datetime, timezone
import json
from functools import lru_cache
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

from source import PRMSError

KINDS = frozenset({"HUMAN_DECISION", "OBSERVATION", "MODEL_INFERENCE", "EXECUTION_REQUEST",
                   "EXTERNAL_RESULT", "CORRECTION", "REVIEW"})


@lru_cache(maxsize=4)
def record_validator(kind):
    path = Path(__file__).resolve().parents[4] / "03_mechanisms/context_management/prms/record_schemas_v1.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator({"$ref": "#/$defs/" + kind, "$defs": schema["$defs"]}, format_checker=FormatChecker())


def validate_record(kind, value):
    problems = sorted(record_validator(kind).iter_errors(value), key=lambda e: str(list(e.path)))
    if problems:
        raise PRMSError("REJECTED", f"{kind} schema: {problems[0].message}")
    return value


def require_mapping(value, name):
    if not isinstance(value, dict):
        raise PRMSError("REJECTED", name + " must be an object")
    return value


def positive_version(value, name, allow_zero=False):
    if type(value) is not int or value < (0 if allow_zero else 1):
        raise PRMSError("REJECTED", name + " must be an integer state version")


def validate_source_ref(ref):
    require_mapping(ref, "source_ref")
    for key in ("repository", "commit", "path"):
        if not isinstance(ref.get(key), str) or not ref[key]:
            raise PRMSError("SOURCE_MISSING", "source " + key)
    if not re.fullmatch(r"[0-9a-f]{40}", ref["commit"]):
        raise PRMSError("SOURCE_MISSING", "source commit is not immutable")
    if "blob" in ref and not re.fullmatch(r"[0-9a-f]{40}", ref["blob"]):
        raise PRMSError("SOURCE_MISSING", "invalid source blob")
    return ref


def normalize_event(event):
    require_mapping(event, "event")
    if event.get("kind") not in KINDS:
        raise PRMSError("REJECTED", "event evidence kind")
    if not isinstance(event.get("source_refs"), list) or not event["source_refs"]:
        raise PRMSError("SOURCE_MISSING", "event provenance required")
    for ref in event["source_refs"]:
        validate_source_ref(ref)
    if event["kind"] == "CORRECTION" and not event.get("corrects_event_id"):
        raise PRMSError("REJECTED", "correction must identify the retained original event")
    normalized = dict(event)
    normalized.update(schema_version="prms.event.v1",
                      recorded_at=datetime.now(timezone.utc).isoformat(),
                      observed_at=event.get("observed_at", "UNKNOWN"),
                      source_verification="REFERENCED_NOT_INDEPENDENTLY_VERIFIED")
    return validate_record("event", normalized)


def validate_current(current, role_id):
    require_mapping(current, "CURRENT")
    if current.get("role_id") != role_id or current.get("status") != "PUBLISHED_CURRENT":
        raise PRMSError("REJECTED", "CURRENT identity or status invalid")
    positive_version(current.get("state_version"), "state_version")
    positive_version(current.get("owner_epoch"), "owner_epoch")
    if not current.get("operation_id"):
        raise PRMSError("REJECTED", "CURRENT operation missing")
    return validate_record("current", current)
