"""Foreground, exact-candidate verification with complete logs and a replay gate.

This is not a sandbox or an attestation service. See the canonical contract.
Exit 0: every required check completed as expected; 1: check mismatch;
3: input, source, execution or evidence error. An interrupted run has no verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packet_input"))
from task_packet_input import load_yaml_text, normalize_packet

PLAN_VERSION = "citystate.verification_plan.v1"
RECORD_VERSION = "citystate.verification_attempt.v1"
RUNNER = "01_os/06_execution/task_discipline/managed_verification/managed_verify.py"


class VerificationError(Exception):
    """A non-successful input, source or evidence boundary."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise VerificationError(f"regular_file_required:{path.name}")
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"duplicate_json_key:{key}")
        result[key] = value
    return result


def reject_constant(value):
    raise VerificationError(f"nonfinite_json_number:{value}")


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise VerificationError("nonfinite_json_number")
    return number


def same_json(left, right):
    """JSON equality without Python's True == 1 / False == 0 coercion."""
    options = {"sort_keys": True, "separators": (",", ":"), "allow_nan": False}
    return json.dumps(left, **options) == json.dumps(right, **options)


def decode_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant, parse_float=finite_float)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise VerificationError("invalid_utf8_json") from exc


def read_record(path: Path):
    file_digest(path)
    return decode_json(path.read_bytes())


def exact_keys(value, keys, where):
    if type(value) is not dict or set(value) != set(keys):
        raise VerificationError(f"invalid_fields:{where}")


def validate_plan(plan, *, diagnostic=False):
    exact_keys(plan, {"schema_version", "checks"} if diagnostic else {"schema_version", "task_packet", "checks"}, "plan")
    if plan["schema_version"] != PLAN_VERSION:
        raise VerificationError("unsupported_plan_version")
    if not diagnostic and (type(plan["task_packet"]) is not str or not plan["task_packet"]):
        raise VerificationError("task_packet_path_required")
    if type(plan["checks"]) is not list or not plan["checks"]:
        raise VerificationError("nonempty_checks_required")
    ids = set()
    for check in plan["checks"]:
        exact_keys(check, {"id", "argv", "timeout_seconds", "expected_exit_code"}, "check")
        name = check["id"]
        if type(name) is not str or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
            raise VerificationError("invalid_check_id")
        if name in ids:
            raise VerificationError("duplicate_check_id")
        ids.add(name)
        argv = check["argv"]
        if type(argv) is not list or not argv or any(
            type(arg) is not str or not arg or "\0" in arg for arg in argv
        ):
            raise VerificationError("invalid_argv")
        for field, low, high in [("timeout_seconds", 1, 3600), ("expected_exit_code", 0, 255)]:
            if type(check[field]) is not int or not low <= check[field] <= high:
                raise VerificationError(f"invalid_{field}")
    return plan


def git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(["git", "--no-optional-locks", "-c", "core.untrackedCache=false", "-c", "core.fsmonitor=false", *args], cwd=repo,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError("git_unavailable_or_timeout") from exc
    # Warnings about unreadable files are not clean-source evidence either.
    if result.returncode != 0 or result.stderr:
        raise VerificationError(f"git_source_error:{args[0]}:exit={result.returncode}")
    return result.stdout


def tracked_blob(repo: Path, candidate: str, path: str) -> bytes:
    if type(path) is not str or not path or "\\" in path or ":" in path:
        raise VerificationError("invalid_source_path")
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or any(p in (".", "..") for p in path.split("/")) or "//" in path:
        raise VerificationError("invalid_source_path")
    entries = git(repo, "ls-tree", "-z", candidate, "--", path).split(b"\0")
    entries = [e for e in entries if e]
    if len(entries) != 1:
        raise VerificationError("source_path_absent_or_ambiguous")
    metadata, actual = entries[0].split(b"\t", 1)
    mode, kind, oid = metadata.split()
    if mode not in (b"100644", b"100755") or kind != b"blob" or actual.decode("utf-8") != path:
        raise VerificationError("source_regular_blob_required")
    return git(repo, "cat-file", "blob", oid.decode("ascii"))


def candidate_id(repo: Path, candidate: str):
    if type(candidate) is not str or not re.fullmatch(r"[0-9a-f]{40}", candidate):
        raise VerificationError("exact_40_character_candidate_required")
    if git(repo, "cat-file", "-t", candidate).strip() != b"commit":
        raise VerificationError("candidate_commit_required")


def source_state(repo: Path, candidate: str):
    head = git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    if head != candidate:
        raise VerificationError("candidate_head_mismatch")
    if Path(git(repo, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve() != repo:
        raise VerificationError("repository_root_required")
    flags = git(repo, "ls-files", "-v", "-z").split(b"\0")
    if any(e and (e[:1].islower() or e[:1] == b"S") for e in flags):
        raise VerificationError("hidden_index_entries_unsupported")
    if any(e.startswith(b"160000 ") for e in git(repo, "ls-files", "--stage", "-z").split(b"\0")):
        raise VerificationError("submodules_unsupported")
    if git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=none"):
        raise VerificationError("source_not_clean")
    return {"head": head, "tree": git(repo, "rev-parse", "HEAD^{tree}").decode("ascii").strip(), "clean": True}


def observe_source(repo: Path, candidate: str):
    try:
        return {"state": source_state(repo, candidate), "error": None}
    except VerificationError as exc:
        return {"state": None, "error": str(exc)}


def validate_observation(observation, expected_state):
    exact_keys(observation, {"state", "error"}, "source_observation")
    if observation["error"] is None:
        if not same_json(observation["state"], expected_state):
            raise VerificationError("invalid_source_state")
    elif type(observation["error"]) is not str or not observation["error"] or observation["state"] is not None:
        raise VerificationError("invalid_source_error")


def write_record(path: Path, value, final=False):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    pending = path.with_suffix(".pending") if final else path
    with pending.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if final:
        # The directory is exclusively owned by this invocation. Never overwrite.
        if path.exists():
            raise VerificationError("final_record_already_exists")
        pending.rename(path)


def resolved_argv(check):
    argv = list(check["argv"])
    if argv[0] == "@python":
        argv[0] = sys.executable
    return argv


def terminate_tree(proc):
    """Timeout is always an error, even if tree termination seems successful."""
    try:
        if os.name == "nt":
            cleanup = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15,
                                     creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            outcome = "tree_termination_requested" if cleanup.returncode == 0 else "tree_termination_uncertain"
        else:
            os.killpg(proc.pid, signal.SIGKILL)
            outcome = "process_group_termination_requested"
        proc.wait(timeout=15)
        return outcome
    except (OSError, subprocess.TimeoutExpired):
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                pass
        return "termination_uncertain"


def run_check(check, index: int, repo: Path, attempt: Path):
    prefix = f"{index:03d}"
    argv = resolved_argv(check)
    write_record(attempt / f"{prefix}.started.json", {"id": check["id"], "argv": argv, "started_ns": time.time_ns()})
    outcome, exit_code, termination = "error", None, "not_needed"
    proc = None
    error = None
    begin = time.monotonic()
    with (attempt / f"{prefix}.stdout.bin").open("xb") as stdout, (attempt / f"{prefix}.stderr.bin").open("xb") as stderr:
        try:
            options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
            proc = subprocess.Popen(argv, cwd=repo, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, **options)
            exit_code = proc.wait(timeout=check["timeout_seconds"])
            outcome = "success" if exit_code == check["expected_exit_code"] else "failure"
        except subprocess.TimeoutExpired:
            error = "timeout"
            termination = terminate_tree(proc)
            exit_code = proc.poll()
        except OSError as exc:
            error = f"spawn_or_wait_error:{exc.__class__.__name__}"
        except BaseException:
            if proc is not None and proc.poll() is None:
                terminate_tree(proc)
            raise  # No final record; inspection rejects interrupted attempts.
        finally:
            stdout.flush()
            stderr.flush()
            os.fsync(stdout.fileno())
            os.fsync(stderr.fileno())
    result = {"id": check["id"], "status": outcome, "exit_code": exit_code,
              "error": error, "termination": termination, "finished_ns": time.time_ns(),
              "elapsed_seconds": time.monotonic() - begin,
              "stdout_sha256": file_digest(attempt / f"{prefix}.stdout.bin"),
              "stderr_sha256": file_digest(attempt / f"{prefix}.stderr.bin")}
    write_record(attempt / f"{prefix}.finished.json", result)
    return result


def expected_input(repo: Path, candidate: str, plan_path: str):
    candidate_id(repo, candidate)
    plan_bytes = tracked_blob(repo, candidate, plan_path)
    plan = validate_plan(decode_json(plan_bytes))
    runner_bytes = tracked_blob(repo, candidate, RUNNER)
    packet_bytes = tracked_blob(repo, candidate, plan["task_packet"])
    loaded = normalize_packet(load_yaml_text(packet_bytes.decode("utf-8")))
    packet = loaded.body
    if loaded.source_format != "wrapped_v1":
        raise VerificationError("managed_route_requires_canonical_packet")
    if packet.get("verification_plan") != plan_path:
        raise VerificationError("packet_plan_binding_mismatch")
    if packet["required_tests"] != [check["id"] for check in plan["checks"]]:
        raise VerificationError("required_checks_coverage_mismatch")
    git(repo, "merge-base", "--is-ancestor", packet["exact_base_sha"], candidate)
    paths = git(repo, "diff", "--name-only", "--no-renames", "-z", packet["exact_base_sha"], candidate, "--").decode("utf-8").split("\0")
    paths = sorted(p for p in paths if p)
    def allowed(path):
        return any(path == rule or (rule.endswith("/**") and path.startswith(rule[:-3] + "/"))
                   for rule in packet["allowed_changed_paths"])
    if any(not allowed(path) for path in paths):
        raise VerificationError("candidate_outside_packet_allowlist")
    return {"schema_version": RECORD_VERSION, "candidate": candidate, "plan_path": plan_path,
            "plan_sha256": digest(plan_bytes), "runner_blob_sha256": digest(runner_bytes), "plan": plan,
            "task_id": packet["task_id"], "task_packet_sha256": digest(packet_bytes),
            "source_base": packet["exact_base_sha"], "changed_paths": paths}


def execute(repo: Path, candidate: str, plan_path: str, attempt: Path):
    repo = repo.resolve()
    binding = expected_input(repo, candidate, plan_path)
    before = source_state(repo, candidate)
    if Path(__file__).resolve() != (repo / RUNNER).resolve():
        raise VerificationError("entry_must_execute_from_candidate_worktree")
    attempt = attempt.resolve()
    if attempt == repo or repo in attempt.parents:
        raise VerificationError("attempt_must_be_outside_source")
    attempt.mkdir()  # Parent must exist; exclusive directory, no overwrite/reuse.
    write_record(attempt / "input.json", {**binding, "source_before": before,
                 "runtime": {"python": sys.version, "platform": platform.platform(),
                             "executable": sys.executable, "runner_file_sha256": file_digest(Path(__file__))}})
    stopped = False
    statuses = []
    for index, check in enumerate(binding["plan"]["checks"], 1):
        if stopped:
            statuses.append({"id": check["id"], "status": "not_run"})
            continue
        result = run_check(check, index, repo, attempt)
        observation = observe_source(repo, candidate)
        write_record(attempt / f"{index:03d}.source.json", observation)
        effective_status = "error" if observation["error"] is not None else result["status"]
        statuses.append({"id": check["id"], "status": effective_status})
        stopped = effective_status != "success"
    after = observe_source(repo, candidate)
    write_record(attempt / "source_after.json", after)
    status = derive_status(statuses, after)
    write_record(attempt / "result.json", {"schema_version": RECORD_VERSION,
                 "candidate": candidate, "plan_sha256": binding["plan_sha256"],
                 "checks": statuses, "status": status, "authority_effect": "none"}, final=True)
    # Do not return success from an unchecked self-reported summary.
    return inspect(repo, candidate, plan_path, attempt)


def derive_status(statuses, after):
    if after["error"] is not None or any(item["status"] == "error" for item in statuses):
        return "error"
    if all(item["status"] == "success" for item in statuses):
        return "success"
    if any(item["status"] == "failure" for item in statuses):
        return "failure"
    return "error"


def inspect(repo: Path, candidate: str, plan_path: str, attempt: Path):
    binding = expected_input(repo.resolve(), candidate, plan_path)
    inputs = read_record(attempt / "input.json")
    exact_keys(inputs, set(binding) | {"source_before", "runtime"}, "input")
    if any(not same_json(inputs[k], v) for k, v in binding.items()):
        raise VerificationError("input_binding_mismatch")
    tree = git(repo, "rev-parse", f"{candidate}^{{tree}}").decode("ascii").strip()
    expected_state = {"head": candidate, "tree": tree, "clean": True}
    if not same_json(inputs["source_before"], expected_state):
        raise VerificationError("invalid_source_before")
    exact_keys(inputs["runtime"], {"python", "platform", "executable", "runner_file_sha256"}, "runtime")
    if any(type(v) is not str or not v for v in inputs["runtime"].values()):
        raise VerificationError("invalid_runtime")
    if not re.fullmatch(r"[0-9a-f]{64}", inputs["runtime"]["runner_file_sha256"]):
        raise VerificationError("invalid_runtime_runner_digest")
    after = read_record(attempt / "source_after.json")
    validate_observation(after, expected_state)
    statuses, stopped = [], False
    expected_files = {"input.json", "source_after.json", "result.json"}
    for index, check in enumerate(binding["plan"]["checks"], 1):
        prefix = f"{index:03d}"
        if stopped:
            statuses.append({"id": check["id"], "status": "not_run"})
            continue
        expected_files.update(f"{prefix}.{suffix}" for suffix in ("started.json", "finished.json", "source.json", "stdout.bin", "stderr.bin"))
        start = read_record(attempt / f"{prefix}.started.json")
        exact_keys(start, {"id", "argv", "started_ns"}, "started")
        argv = list(check["argv"])
        if argv[0] == "@python":
            argv[0] = inputs["runtime"]["executable"]
        if start["id"] != check["id"] or start["argv"] != argv or type(start["started_ns"]) is not int:
            raise VerificationError("invalid_start_record")
        end = read_record(attempt / f"{prefix}.finished.json")
        exact_keys(end, {"id", "status", "exit_code", "error", "termination", "finished_ns", "elapsed_seconds", "stdout_sha256", "stderr_sha256"}, "finished")
        if end["id"] != check["id"] or type(end["finished_ns"]) is not int or end["finished_ns"] < start["started_ns"]:
            raise VerificationError("invalid_finish_record")
        if type(end["elapsed_seconds"]) not in (float, int) or end["elapsed_seconds"] < 0:
            raise VerificationError("invalid_elapsed_seconds")
        if end["exit_code"] is not None and type(end["exit_code"]) is not int:
            raise VerificationError("invalid_raw_exit_code")
        for stream in ("stdout", "stderr"):
            if end[f"{stream}_sha256"] != file_digest(attempt / f"{prefix}.{stream}.bin"):
                raise VerificationError("log_digest_mismatch")
        if end["error"] is None:
            if type(end["exit_code"]) is not int or end["termination"] != "not_needed":
                raise VerificationError("invalid_completed_process")
            status = "success" if end["exit_code"] == check["expected_exit_code"] else "failure"
        elif end["error"] == "timeout":
            if end["termination"] not in ("tree_termination_requested", "tree_termination_uncertain", "process_group_termination_requested", "termination_uncertain"):
                raise VerificationError("invalid_timeout_record")
            status = "error"
        elif type(end["error"]) is str and end["error"].startswith("spawn_or_wait_error:"):
            if end["termination"] != "not_needed":
                raise VerificationError("invalid_spawn_record")
            status = "error"
        else:
            raise VerificationError("invalid_process_error")
        if status != end["status"]:
            raise VerificationError("process_status_mismatch")
        observation = read_record(attempt / f"{prefix}.source.json")
        validate_observation(observation, expected_state)
        if observation["error"] is not None:
            status = "error"
        statuses.append({"id": check["id"], "status": status})
        stopped = status != "success"
    if {p.name for p in attempt.iterdir()} != expected_files:
        raise VerificationError("unexpected_or_missing_attempt_files")
    status = derive_status(statuses, after)
    expected_result = {"schema_version": RECORD_VERSION, "candidate": candidate,
                       "plan_sha256": binding["plan_sha256"], "checks": statuses,
                       "status": status, "authority_effect": "none"}
    if not same_json(read_record(attempt / "result.json"), expected_result):
        raise VerificationError("result_derivation_mismatch")
    return expected_result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=["run", "inspect"])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--plan", required=True, help="candidate-tracked repository-relative JSON path")
    parser.add_argument("--attempt", required=True, help="external directory, new for every run")
    args = parser.parse_args(argv)
    try:
        operation = execute if args.action == "run" else inspect
        result = operation(Path(args.repo_root).resolve(), args.candidate, args.plan, Path(args.attempt).absolute())
        print(json.dumps(result, ensure_ascii=False))
        return {"success": 0, "failure": 1, "error": 3}[result["status"]]
    except (VerificationError, OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(json.dumps({"status": "error", "error": str(exc), "authority_effect": "none"}, ensure_ascii=False))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
