"""Resolve domain research and invoke the pinned Core static tool."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


PROFILE = Path(__file__).with_name("profile.json")
MAX_RAW_BYTES = 8 * 1024 * 1024


def git_blob(root, commit, path):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected a full Git commit SHA")
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", f"{commit}:{path}"],
        check=False, capture_output=True, timeout=15,
    )
    if result.returncode:
        raise FileNotFoundError(f"Missing pinned source {commit}:{path}")
    return result.stdout


def load_catalog(root, profile):
    source = profile["native_research"]
    def load(name):
        return json.loads(git_blob(root, source["commit"], source["directory"] + "/" + source[name]))
    registry = load("action_catalog")
    effects = load("effect_evidence")
    bindings = load("binding_catalog")
    readers = load("read_catalog")
    build = profile["target"]["sha256"]
    if any(document["game_build_sha256"] != build for document in (registry, effects, bindings)):
        raise ValueError("Catalog and exact-example evidence must bind the domain build")
    actions = {}
    for action in registry["actions"]:
        identifier = action["action_id"]
        if identifier in actions:
            raise ValueError(f"Duplicate action ID {identifier}")
        observed = effects["actions"].get(identifier)
        status = (observed or {}).get("status", "")
        level = "Pending"
        if status.startswith("REAL_NATIVE_EFFECT_VERIFIED_"):
            level = "LiveEffectVerified"
        elif status == "REAL_BOUND_SUBSET_READ":
            level = "LiveSubsetRead"
        elif status == "REJECTED_BY_GAME":
            level = "ObservedRejection"
        elif action["capability"] in {"CALL_LOGIC_RECOVERED", "PRIOR_LIVE_SUCCESS"}:
            level = "StaticRecovered"
        actions[identifier] = {
            "evidence_level": level,
            "source_capability": action["capability"],
            "historical_example": observed,
            "runtime_handler": action.get("runtime_handler"),
            "domain_route": profile["native_executor_candidate"],
            "current_execution": "NOT_RUN",
        }
    return {"status": "DOMAIN_CATALOG_RESOLVED", "source": source, "game_build_sha256": build,
            "binding_count": len(bindings["bindings"]), "reader_count": len(readers["datasets"]),
            "actions": actions, "authority_effect": "none"}


def verify_static_receipt(evidence_dir, profile):
    directory = Path(evidence_dir)
    receipt_bytes = (directory / "receipt.json").read_bytes()
    binding = json.loads((directory / "domain_invocation.json").read_bytes())
    if (binding.get("core_commit") != profile["core"]["commit"]
            or binding.get("operation") != "invoke"
            or binding.get("receipt_sha256") != hashlib.sha256(receipt_bytes).hexdigest()):
        raise ValueError("Receipt does not match the recorded Core invocation")
    report = json.loads(receipt_bytes)
    if (report.get("schema_version") != "citystate.rea.receipt.v1"
            or report.get("status") != "VERIFIED_TOOL_CALL"
            or type(report.get("exit_code")) is not int or report["exit_code"] != 0
            or report.get("evidence_scope") != "local_tool_only"
            or report.get("authority_effect") != "none"
            or report.get("command") != profile["core"]["static_operation"]
            or report.get("observed_version") != profile["core"]["expected_rea_version"]
            or report.get("parameters") != {"length": str(profile["core"]["read_window_bytes"])}
            or report.get("source", {}).get("sha256") != profile["target"]["sha256"]
            or report.get("output") != "result.stdout"):
        raise ValueError("Receipt does not bind the domain build, operation, version and static evidence")
    matches = [item for item in report["raw_files"] if item["path"] == "result.stdout"]
    raw_file = directory / "result.stdout"
    if len(matches) != 1 or not raw_file.is_file() or raw_file.stat().st_size > MAX_RAW_BYTES:
        raise ValueError("Missing or oversized raw evidence")
    raw = raw_file.read_bytes()
    if len(raw) != matches[0]["size_bytes"] or hashlib.sha256(raw).hexdigest() != matches[0]["sha256"]:
        raise ValueError("Raw output changed after receipt")
    envelope = json.loads(raw)
    if envelope.get("ok") is not True or not isinstance(envelope.get("data"), dict):
        raise ValueError("Raw static evidence is missing")
    return {"status": "DOMAIN_STATIC_RECEIPT_VERIFIED", "source": report["source"],
            "core_commit": profile["core"]["commit"], "raw_sha256": matches[0]["sha256"],
            "current_game_effect": "NOT_RUN", "authority_effect": "none"}


def call_core(root, profile, evidence_dir, operation, artifact=None):
    if Path(evidence_dir).exists():
        raise ValueError("Select a new evidence directory")
    core = profile["core"]
    try:
        program = git_blob(root, core["commit"], core["adapter_path"])
    except FileNotFoundError as exc:
        raise FileNotFoundError("Core tool unavailable. Supply a Core checkout containing the pinned candidate.") from exc
    argv = [operation, "--evidence-dir", str(Path(evidence_dir).resolve()),
            "--expected-version", core["expected_rea_version"]]
    if operation == "invoke":
        argv.extend(["--command", core["static_operation"], "--artifact", str(Path(artifact).resolve()),
                     "--expected-sha256", profile["target"]["sha256"],
                     "--option", "length=" + str(core["read_window_bytes"])])
    with tempfile.TemporaryDirectory(prefix="nba-rea-core-") as folder:
        adapter = Path(folder) / "adapter.py"
        adapter.write_bytes(program)
        completed = subprocess.run([sys.executable, "-B", str(adapter), *argv],
                                   capture_output=True, timeout=45, check=False)
    receipt = Path(evidence_dir) / "receipt.json"
    if not receipt.is_file():
        raise ValueError(f"Core adapter exited {completed.returncode} before producing a receipt")
    binding = {"core_commit": core["commit"], "operation": operation,
               "adapter_sha256": hashlib.sha256(program).hexdigest(),
               "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
    with (Path(evidence_dir) / "domain_invocation.json").open("x", encoding="utf-8") as stream:
        json.dump(binding, stream, indent=2)
    if completed.returncode == 0 and operation == "invoke":
        return verify_static_receipt(evidence_dir, profile), 0
    return json.loads(receipt.read_text(encoding="utf-8")), completed.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["catalog", "probe", "inspect", "verify-receipt"])
    parser.add_argument("--nba-root", type=Path)
    parser.add_argument("--core-root", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--action")
    args = parser.parse_args()
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    try:
        code = 0
        if args.operation == "catalog":
            if args.nba_root is None:
                parser.error("catalog requires --nba-root")
            result = load_catalog(args.nba_root, profile)
            if args.action:
                result["actions"] = {args.action: result["actions"][args.action]}
            else:
                result["action_count"] = len(result["actions"])
                result["actions"] = {key: value["evidence_level"] for key, value in result["actions"].items()}
        elif args.operation == "verify-receipt":
            if args.evidence_dir is None:
                parser.error("verify-receipt requires --evidence-dir")
            result = verify_static_receipt(args.evidence_dir, profile)
        else:
            if args.core_root is None or args.evidence_dir is None:
                parser.error("probe and inspect require --core-root and --evidence-dir")
            if args.operation == "inspect" and args.artifact is None:
                parser.error("inspect requires --artifact")
            result, code = call_core(args.core_root, profile, args.evidence_dir,
                                     "invoke" if args.operation == "inspect" else "probe", args.artifact)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        status = "SOURCE_UNAVAILABLE" if isinstance(exc, FileNotFoundError) else "DOMAIN_REQUEST_FAILED"
        result, code = {"status": status, "message": str(exc), "authority_effect": "none"}, 3
    print(json.dumps(result, ensure_ascii=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
