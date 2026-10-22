"""Local immutable offseason simulation artifacts; no approval/execution APIs."""
import json
from pathlib import Path

from .offseason import FILES, identifier, integer, season


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _no_float(value):
    raise ValueError("Use integer dollars and integer scores, not floats/nonfinite values")


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("Snapshot exceeds the 20 MiB input limit")
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_pairs,
                      parse_float=_no_float, parse_constant=_no_float)


def local_output(root, output):
    exports = (Path(root) / "_exports").resolve()
    path = (Path(root) / output).resolve()
    if path == exports or not path.is_relative_to(exports):
        raise ValueError("Offseason output must be inside a child of _exports")
    return path


def artifact_directory(root, output, data):
    base = local_output(root, output)
    save_id = identifier(data["save_id"], "save_id")
    run_id = identifier(data["offseason_run_id"], "offseason_run_id")
    season(data["completed_season"])
    integer(data["proposal_version"], "proposal_version", 1)
    directory = base / save_id / data["completed_season"] / run_id / f"v{data['proposal_version']}"
    resolved = directory.resolve()
    if not resolved.is_relative_to(base):
        raise ValueError("Run directory leaves output root")
    return resolved


def save_run(root, output, data, artifacts):
    directory = artifact_directory(root, output, data)
    if directory.exists():
        try:
            old = read_run(directory)
            original = read_json(directory / "frozen_input.json")
        except (OSError, ValueError, KeyError) as exc:
            raise ValueError("OUTPUT_INCOMPLETE: preserve evidence and use a new run/version") from exc
        if original != data or old != artifacts:
            raise ValueError("RUN_VERSION_CONFLICT: cannot overwrite frozen input or proposals")
        return directory, "NO_WRITE_NEEDED"
    # Exclusive creation prevents two invocations from writing the same version.
    directory.mkdir(parents=True, exist_ok=False)
    for filename, content in {"frozen_input.json": data, **artifacts}.items():
        if filename not in (*FILES, "frozen_input.json"):
            raise ValueError("Unexpected artifact name")
        payload = content if filename.endswith(".md") else json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        (directory / filename).write_text(payload, encoding="utf-8")
    # Written last. An interrupted run is never mistaken for a completed one.
    (directory / "COMPLETE").write_text("OFFLINE_ARTIFACTS_ONLY\n", encoding="utf-8")
    return directory, "WRITTEN"


def read_run(directory):
    directory = Path(directory)
    if (directory / "COMPLETE").read_text(encoding="utf-8") != "OFFLINE_ARTIFACTS_ONLY\n":
        raise ValueError("Incomplete run")
    return {name: (directory / name).read_text(encoding="utf-8") if name.endswith(".md")
            else read_json(directory / name) for name in FILES}
