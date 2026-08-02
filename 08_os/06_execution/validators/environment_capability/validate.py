from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "receipt_id",
    "task_id",
    "measured_at",
    "environment_class",
    "model_availability",
    "toolchain",
    "publication_transport",
    "boundaries",
    "runtime_limits",
    "invalidation_events",
}
CATEGORY_KEYS = {
    "environment_class",
    "model_availability",
    "toolchain",
    "publication_transport",
    "boundaries",
    "runtime_limits",
}
POSIX_PERSONAL_OR_SYSTEM_ROOTS = frozenset({"home", "users", "mnt", "etc", "opt", "root", "var"})
ENVIRONMENT_HOME_MARKERS = ("%userprofile%", "$env:userprofile", "$home", "${home}")
KNOWN_MEASURED_AT = "2000-01-01T00:00:00Z"
KNOWN_SAFE_STRING = "known-difference-placeholder"


def personal_path_shape_codes(text: str) -> list[str]:
    """Derive path findings from shape categories, independently of schema regexes."""
    lowered = text.lower()
    findings: list[str] = []
    for index in range(max(0, len(text) - 2)):
        if text[index].isalpha() and text[index + 1] == ":" and text[index + 2] in {"\\", "/"}:
            findings.append("drive_root")
            break
    unc_start = text.find("\\\\")
    if unc_start >= 0:
        remainder = text[unc_start + 2 :]
        if remainder and any(separator in remainder for separator in {"\\", "/"}):
            findings.append("unc_root")
    for root_name in POSIX_PERSONAL_OR_SYSTEM_ROOTS:
        if f"/{root_name}/" in lowered:
            findings.append("posix_personal_or_system_root")
            break
    if "~/" in lowered or "~\\" in lowered:
        findings.append("home_shorthand")
    for marker in ENVIRONMENT_HOME_MARKERS:
        marker_index = lowered.find(marker)
        if marker_index >= 0:
            suffix_index = marker_index + len(marker)
            if suffix_index < len(lowered) and lowered[suffix_index] in {"\\", "/"}:
                findings.append("environment_home_expansion")
                break
    return findings


def walk_strings(value: Any) -> list[str]:
    findings: list[str] = []
    if isinstance(value, str):
        findings.extend(personal_path_shape_codes(value))
    elif isinstance(value, list):
        for item in value:
            findings.extend(walk_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            findings.extend(walk_strings(item))
    return findings


def validate(receipt: dict[str, Any]) -> list[str]:
    """Run the checker contract without importing schema definitions or regexes."""
    errors: list[str] = []
    if set(receipt) != REQUIRED_TOP_LEVEL:
        errors.append("top_level_contract")
    if receipt.get("schema_version") != "citystate.environment_capability_receipt.v1":
        errors.append("schema_version")
    for category_name in CATEGORY_KEYS:
        category = receipt.get(category_name)
        if not isinstance(category, dict) or set(category) != {"observations"}:
            errors.append(f"{category_name}.shape")
            continue
        observations = category.get("observations")
        if not isinstance(observations, list) or not observations:
            errors.append(f"{category_name}.observations")
            continue
        ids: set[str] = set()
        for observation in observations:
            if not isinstance(observation, dict):
                errors.append(f"{category_name}.observation_type")
                continue
            observation_id = observation.get("id")
            if not isinstance(observation_id, str) or observation_id in ids:
                errors.append(f"{category_name}.observation_id")
            else:
                ids.add(observation_id)
            if not isinstance(observation.get("measurement_source"), dict):
                errors.append(f"{category_name}.measurement_source")
            status = observation.get("status")
            if status == "observed":
                if "value" not in observation or observation.get("value") is None or "reason" in observation:
                    errors.append(f"{category_name}.observed_state")
            elif status == "not_observable":
                if "reason" not in observation or "value" in observation:
                    errors.append(f"{category_name}.not_observable_state")
            else:
                errors.append(f"{category_name}.status")
    invalidation_events = receipt.get("invalidation_events")
    if not isinstance(invalidation_events, list) or not invalidation_events:
        errors.append("invalidation_events")
    else:
        for event in invalidation_events:
            if not isinstance(event, dict) or event.get("required_action") != "remeasure_before_use":
                errors.append("invalidation_event_contract")
    errors.extend(walk_strings(receipt))
    return sorted(set(errors))


def _default_paths() -> tuple[Path, Path]:
    repo = Path(__file__).resolve().parents[4]
    return (
        repo / "08_os/03_mechanisms/environment_capability/实现/环境能力receipt_schema_v1.yml",
        repo / "08_os/06_execution/tools/check_jsonschema/invoke.ps1",
    )


def _schema_run(receipt_path: Path, schema_path: Path, wrapper_path: Path) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="environment-capability-schema-") as temp_name:
        schema_copy = Path(temp_name) / "schema.json"
        shutil.copyfile(schema_path, schema_copy)
        process = subprocess.run(
            [
                "pwsh", "-NoProfile", "-File", str(wrapper_path),
                "-SchemaPath", str(schema_copy), "-InstancePath", str(receipt_path),
            ],
            capture_output=True,
            check=False,
        )
    output_digest = hashlib.sha256(process.stdout + process.stderr).hexdigest()
    return process.returncode, output_digest


def _replace_empty_safe_value(value: Any) -> tuple[Any, int]:
    if value == "":
        return KNOWN_SAFE_STRING, 1
    if isinstance(value, list):
        replaced: list[Any] = []
        changes = 0
        for item in value:
            new_item, item_changes = _replace_empty_safe_value(item)
            replaced.append(new_item)
            changes += item_changes
        return replaced, changes
    if isinstance(value, dict):
        replaced_dict: dict[str, Any] = {}
        changes = 0
        for key, item in value.items():
            new_item, item_changes = _replace_empty_safe_value(item)
            replaced_dict[key] = new_item
            changes += item_changes
        return replaced_dict, changes
    return value, 0


def _repair_empty_safe_strings(receipt: dict[str, Any]) -> int:
    changes = 0
    for category_name in CATEGORY_KEYS:
        category = receipt.get(category_name)
        if not isinstance(category, dict):
            continue
        observations = category.get("observations")
        if not isinstance(observations, list):
            continue
        for observation in observations:
            if not isinstance(observation, dict):
                continue
            if "value" in observation:
                observation["value"], item_changes = _replace_empty_safe_value(observation["value"])
                changes += item_changes
            if observation.get("reason") == "":
                observation["reason"] = KNOWN_SAFE_STRING
                changes += 1
            limitations = observation.get("limitations")
            if isinstance(limitations, list):
                for index, item in enumerate(limitations):
                    if item == "":
                        limitations[index] = KNOWN_SAFE_STRING
                        changes += 1
            source = observation.get("measurement_source")
            if isinstance(source, dict):
                for field in ("probe", "result"):
                    if source.get(field) == "":
                        source[field] = KNOWN_SAFE_STRING
                        changes += 1
    events = receipt.get("invalidation_events")
    if isinstance(events, list):
        for event in events:
            if isinstance(event, dict) and event.get("trigger") == "":
                event["trigger"] = KNOWN_SAFE_STRING
                changes += 1
    return changes


def _write_and_check(candidate: dict[str, Any], directory: Path, name: str, schema: Path, wrapper: Path) -> int:
    candidate_path = directory / name
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
    exit_code, _ = _schema_run(candidate_path, schema, wrapper)
    return exit_code


def _known_schema_only_differences(
    receipt: dict[str, Any], schema_path: Path, wrapper_path: Path
) -> list[str] | None:
    measured_candidate = copy.deepcopy(receipt)
    measured_changed = isinstance(measured_candidate.get("measured_at"), str)
    if measured_changed:
        measured_candidate["measured_at"] = KNOWN_MEASURED_AT
    empty_candidate = copy.deepcopy(receipt)
    empty_changes = _repair_empty_safe_strings(empty_candidate)

    with tempfile.TemporaryDirectory(prefix="environment-capability-validator-") as temp_name:
        temp_dir = Path(temp_name)
        if measured_changed and _write_and_check(
            measured_candidate, temp_dir, "measured_at.json", schema_path, wrapper_path
        ) == 0:
            return ["measured_at_format"]
        if empty_changes and _write_and_check(
            empty_candidate, temp_dir, "safe_string.json", schema_path, wrapper_path
        ) == 0:
            return ["safe_string_min_length"]
        if measured_changed and empty_changes:
            combined_candidate = copy.deepcopy(measured_candidate)
            _repair_empty_safe_strings(combined_candidate)
            if _write_and_check(
                combined_candidate, temp_dir, "combined.json", schema_path, wrapper_path
            ) == 0:
                return ["measured_at_format", "safe_string_min_length"]
    return None


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def main(argv: list[str]) -> int:
    default_schema, default_wrapper = _default_paths()
    parser = argparse.ArgumentParser(description="Validate one environment capability receipt.")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--schema", type=Path, default=default_schema)
    parser.add_argument("--wrapper", type=Path, default=default_wrapper)
    args = parser.parse_args(argv[1:])
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _emit({"status": "error", "code": exc.__class__.__name__})
        return 2
    if not isinstance(receipt, dict):
        _emit({"status": "error", "code": "receipt_type"})
        return 2
    if not args.schema.is_file() or not args.wrapper.is_file() or shutil.which("pwsh") is None:
        _emit({"status": "error", "code": "validator_dependency"})
        return 2

    schema_exit, schema_output_sha256 = _schema_run(args.receipt, args.schema, args.wrapper)
    if schema_exit not in {0, 1}:
        _emit({
            "status": "error", "code": "schema_validator_failure",
            "schema_exit": schema_exit, "schema_output_sha256": schema_output_sha256,
        })
        return 2

    errors = validate(receipt)
    schema_rejects = schema_exit == 1
    checker_rejects = bool(errors)
    if schema_rejects and checker_rejects:
        classification = "agreed_reject"
    elif not schema_rejects and checker_rejects:
        classification = "checker_only"
    elif not schema_rejects and not checker_rejects:
        classification = "pass"
    else:
        known_differences = _known_schema_only_differences(receipt, args.schema, args.wrapper)
        if known_differences is not None:
            _emit({
                "status": "error", "code": "schema_only_known_difference",
                "known_differences": known_differences, "checker_errors": errors, "schema_exit": schema_exit,
            })
            return 1
        _emit({
            "status": "error", "code": "schema_only_unexplained_disagreement",
            "checker_errors": errors, "schema_exit": schema_exit,
        })
        return 1

    _emit({"classification": classification, "checker_errors": errors, "schema_exit": schema_exit})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
