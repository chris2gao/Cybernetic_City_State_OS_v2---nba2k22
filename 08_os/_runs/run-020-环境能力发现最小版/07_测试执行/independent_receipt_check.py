from __future__ import annotations

import json
from pathlib import Path
import re
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
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]"),
    re.compile(r"/(?:home|Users|mnt)/"),
    re.compile(r"\\\\[^\\/\s]+[\\/]"),
)


def walk_strings(value: Any) -> list[str]:
    findings: list[str] = []
    if isinstance(value, str):
        if any(pattern.search(value) for pattern in ABSOLUTE_PATH_PATTERNS):
            findings.append("absolute_path_shape")
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
                if "value" not in observation or "reason" in observation:
                    errors.append(f"{category_name}.observed_state")
            elif status == "not_observable":
                if "reason" not in observation or "value" in observation:
                    errors.append(f"{category_name}.not_observable_state")
            else:
                errors.append(f"{category_name}.status")
    errors.extend(walk_strings(receipt))
    return sorted(set(errors))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"status": "error", "code": "usage"}))
        return 2
    try:
        receipt = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "code": exc.__class__.__name__}))
        return 2
    errors = validate(receipt)
    print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
