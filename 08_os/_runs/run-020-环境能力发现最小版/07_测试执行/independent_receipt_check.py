from __future__ import annotations

import json
from pathlib import Path
import sys
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


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[2] != "--schema-exit":
        print(json.dumps({"status": "error", "code": "usage"}))
        return 2
    try:
        schema_exit = int(argv[3])
    except ValueError:
        print(json.dumps({"status": "error", "code": "schema_exit"}))
        return 2
    if schema_exit not in {0, 1}:
        print(json.dumps({"status": "error", "code": "schema_exit"}))
        return 2
    try:
        receipt = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "code": exc.__class__.__name__}))
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
        print(json.dumps({"status": "error", "code": "schema_only_disagreement"}, sort_keys=True))
        return 1
    print(json.dumps({"classification": classification, "checker_errors": errors}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
