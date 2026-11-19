"""Explicit, bounded access to selected static commands of a locally installed REA."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


STATIC_COMMANDS = {
    "inspect-go-binary": {"architecture"},
    "inspect-byte-entropy": {"block-size", "offset", "length"},
}
MAX_INPUT = 512 * 1024 * 1024
MAX_OUTPUT = 8 * 1024 * 1024


class AdapterError(Exception):
    def __init__(self, status, message, **details):
        super().__init__(message)
        self.status = status
        self.details = details


def launcher(explicit=None):
    if explicit is None:
        command = shutil.which("rea")
        if os.name == "nt":
            command = shutil.which("rea.cmd") or command
        if command is None:
            raise AdapterError("NOT_INSTALLED", "REA launcher is absent from PATH")
        path = Path(command).resolve()
        if path.suffix.lower() in {".cmd", ".ps1", ".bat"}:
            path = path.parent / "node_modules/rea-agents/scripts/rea.mjs"
    else:
        path = Path(explicit).resolve()
    if not path.is_file():
        raise AdapterError("NOT_INSTALLED", "REA launcher does not resolve to a local file")
    if path.suffix.lower() in {".cmd", ".ps1", ".bat"}:
        raise AdapterError("INVALID_REQUEST", "Pass the installed .mjs entry or native executable")
    if path.suffix.lower() == ".mjs":
        node = shutil.which("node")
        if node is None:
            raise AdapterError("BACKEND_UNAVAILABLE", "Node is required for the installed REA entry")
        return [node, str(path)]
    return [str(path)]


def fingerprint(path, deadline, max_bytes=MAX_INPUT):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                raise AdapterError("INPUT_LIMIT", "Artifact exceeds the byte budget")
            if time.monotonic() >= deadline:
                raise AdapterError("TIMEOUT", "Artifact fingerprint exceeded deadline")
            digest.update(chunk)
    return {"size_bytes": size, "sha256": digest.hexdigest()}


def run_child(prefix, args, directory, label, deadline, max_output):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise AdapterError("TIMEOUT", "Deadline reached before tool start")
    stdout = directory / (label + ".stdout")
    stderr = directory / (label + ".stderr")
    with stdout.open("xb") as out, stderr.open("xb") as err:
        with subprocess.Popen([*prefix, *args], cwd=directory, stdout=out, stderr=err,
                              stdin=subprocess.DEVNULL, shell=False) as child:
            while child.poll() is None:
                if stdout.stat().st_size + stderr.stat().st_size > max_output:
                    child.kill()
                    raise AdapterError("OUTPUT_LIMIT", "Tool output exceeds budget", stdout=stdout.name, stderr=stderr.name)
                if time.monotonic() >= deadline:
                    child.kill()
                    raise AdapterError("TIMEOUT", "Tool deadline exceeded", stdout=stdout.name, stderr=stderr.name)
                time.sleep(0.02)
            code = child.returncode
    if stdout.stat().st_size + stderr.stat().st_size > max_output:
        raise AdapterError("OUTPUT_LIMIT", "Tool output exceeds budget", exit_code=code, stdout=stdout.name, stderr=stderr.name)
    return code, stdout.read_bytes()


def read_json(raw):
    try:
        result = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise AdapterError("INVALID_TOOL_OUTPUT", "REA did not return valid JSON") from exc
    if not isinstance(result, dict):
        raise AdapterError("INVALID_TOOL_OUTPUT", "REA result must be an object")
    return result


def read_result(code, raw):
    try:
        result = read_json(raw)
    except AdapterError:
        if code:
            raise AdapterError("TOOL_FAILED", "REA returned a nonzero exit without structured diagnostics", exit_code=code)
        raise
    if code != 0 or result.get("ok") is False:
        error = result.get("error", result)
        tool_code = str(error.get("code", "UNKNOWN")) if isinstance(error, dict) else "UNKNOWN"
        hint = tool_code.lower()
        status = "TOOL_FAILED"
        if hint in {"validation_error", "invalid_argument", "invalid_arguments", "invalid_request"}:
            status = "INVALID_REQUEST"
        elif "permission" in hint or "access_denied" in hint:
            status = "PERMISSION_DENIED"
        elif any(token in hint for token in ("backend", "provider_unavailable", "not_configured", "executable_missing")):
            status = "BACKEND_UNAVAILABLE"
        elif "timeout" in hint or "deadline" in hint:
            status = "TIMEOUT"
        details = {}
        if isinstance(error, dict):
            if isinstance(error.get("message"), str):
                details["tool_message"] = error["message"][:1024]
            fields = error.get("fieldErrors", [])
            if isinstance(fields, list):
                details["field_errors"] = [
                    {key: str(row[key])[:512] for key in ("path", "code", "message")
                     if key in row}
                    for row in fields[:16] if isinstance(row, dict)
                ]
        raise AdapterError(status, "REA returned a failure", exit_code=code,
                           tool_code=tool_code, **details)
    if result.get("ok") is not True or "data" not in result:
        raise AdapterError("INVALID_TOOL_OUTPUT", "REA success envelope is missing", exit_code=code)
    return result["data"]


def command_options(command, values):
    if command not in STATIC_COMMANDS:
        raise AdapterError("INVALID_REQUEST", "Only explicitly supported static operations may run")
    options = {}
    for value in values:
        key, separator, arg = value.partition("=")
        if not separator or key in options or key not in STATIC_COMMANDS[command]:
            raise AdapterError("INVALID_REQUEST", "Unknown, duplicate or malformed operation option",
                               option=key, allowed_options=sorted(STATIC_COMMANDS[command]))
        if key == "architecture":
            if arg not in {"x86", "x86_64", "arm", "arm64"}:
                raise AdapterError("INVALID_REQUEST", "Unsupported architecture",
                                   option=key, received=arg, allowed_values=["x86", "x86_64", "arm", "arm64"])
        elif not re.fullmatch(r"[0-9]{1,10}", arg) or int(arg) > MAX_INPUT:
            raise AdapterError("INVALID_REQUEST", "Numeric option outside adapter byte budget",
                               option=key, received=arg, minimum=0, maximum=MAX_INPUT)
        elif key == "block-size" and (not 256 <= int(arg) <= 65536 or int(arg) & (int(arg) - 1)):
            raise AdapterError("INVALID_REQUEST", "Block size must be a power of two from 256 to 65536",
                               option=key, received=arg, minimum=256, maximum=65536)
        elif key == "length" and int(arg) == 0:
            raise AdapterError("INVALID_REQUEST", "Length must be positive",
                               option=key, received=arg, minimum=1, maximum=MAX_INPUT)
        options[key] = arg
    return options


def artifact(path):
    target = Path(path).resolve(strict=True)
    if not target.is_file() or target.stat().st_size > MAX_INPUT:
        raise AdapterError("INPUT_LIMIT", "Select a regular bounded binary file")
    with target.open("rb") as stream:
        header = stream.read(4)
    if not (header.startswith(b"MZ") or header in {
        b"\x7fELF", b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe",
        b"\xbe\xba\xfe\xca", b"\xca\xfe\xba\xbf", b"\xbf\xba\xfe\xca",
    }):
        raise AdapterError("INVALID_REQUEST", "Select a PE, ELF or Mach-O binary")
    return target


def execute(args):
    directory = args.evidence_dir.resolve()
    directory.mkdir()
    result = {"schema_version": "citystate.rea.receipt.v1", "operation": args.operation,
              "authority_effect": "none", "evidence_scope": "local_tool_only", "automatic_replay": False}
    deadline = time.monotonic() + args.timeout
    try:
        options = command_options(args.command, args.option) if args.operation == "invoke" else {}
        prefix = launcher(args.launcher)
        code, version_raw = run_child(prefix, ["--version"], directory, "version", deadline, args.max_output)
        version = version_raw.decode("utf-8", errors="replace").strip()
        if code != 0 or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?", version):
            raise AdapterError("VERSION_UNREADABLE", "REA version probe failed", exit_code=code)
        result["observed_version"] = version
        if args.expected_version and version != args.expected_version:
            raise AdapterError("VERSION_MISMATCH", "Installed version differs from selected version",
                               expected_version=args.expected_version)
        if args.operation == "probe":
            code, raw = run_child(prefix, ["capabilities", "--format", "json", "--full-output"],
                                  directory, "capabilities", deadline, args.max_output)
            data = read_result(code, raw)
            if not isinstance(data, dict) or not isinstance(data.get("analysis_provider_candidates"), list):
                raise AdapterError("INVALID_TOOL_OUTPUT", "Capability inventory is missing")
            result["providers"] = [
                {"id": item["provider"]["id"], "status": item["availability"]["status"],
                 "code": item["availability"].get("code")}
                for item in data["analysis_provider_candidates"]
            ]
            result["catalog"] = data.get("server_identity", {}).get("catalog", {})
            result["tools"] = {}
            for name in STATIC_COMMANDS:
                schema = get_schema(prefix, name, directory, deadline, args.max_output)
                result["tools"][name] = {"status": "AVAILABLE_UNVERIFIED", "schema_sha256": schema}
            result.update(status="AVAILABLE_UNVERIFIED", exit_code=0)
        else:
            target = artifact(args.artifact)
            source = fingerprint(target, deadline)
            result.update(command=args.command, source=source, parameters=options)
            if args.expected_sha256 and source["sha256"] != args.expected_sha256:
                raise AdapterError("SOURCE_MISMATCH", "Selected binary differs from requested SHA256")
            result["schema_sha256"] = get_schema(prefix, args.command, directory, deadline, args.max_output, options)
            argv = [args.command, str(target)]
            for key, value in options.items():
                argv.extend(["--" + key, value])
            code, raw = run_child(prefix, [*argv, "--format", "json", "--full-output"],
                                  directory, "result", deadline, args.max_output)
            result["exit_code"] = code
            data = read_result(code, raw)
            if not isinstance(data, dict):
                raise AdapterError("INVALID_TOOL_OUTPUT", "Static result must contain an Evidence object")
            if fingerprint(target, deadline) != source:
                raise AdapterError("SOURCE_CHANGED", "Binary changed during inspection")
            result.update(status="VERIFIED_TOOL_CALL", output="result.stdout")
    except AdapterError as exc:
        result.update(status=exc.status, message=str(exc), **exc.details)
    except PermissionError:
        result.update(status="PERMISSION_DENIED", message="Host denied a file or process operation")
    except FileNotFoundError:
        result.update(status="SOURCE_OR_TOOL_MISSING", message="Selected artifact or launcher is absent")
    except (OSError, KeyError, TypeError) as exc:
        result.update(status="LOCAL_OR_PROTOCOL_FAILURE", error_type=type(exc).__name__)
    result["raw_files"] = [
        {"path": path.name, **fingerprint(path, float("inf"), max_bytes=args.max_output)}
        for path in sorted(directory.iterdir()) if path.stat().st_size <= args.max_output
    ]
    (directory / "receipt.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def get_schema(prefix, command, directory, deadline, max_output, options=()):
    code, raw = run_child(prefix, [command, "--schema", "--format", "json"],
                          directory, command + "-schema", deadline, max_output)
    schema = read_json(raw)
    if code != 0 or "path" not in schema.get("args", {}).get("properties", {}):
        raise AdapterError("SCHEMA_UNAVAILABLE", "Installed REA does not expose the selected static tool schema", exit_code=code)
    available = schema.get("options", {}).get("properties", {})
    schema_keys = {"block-size": "blockSize"}
    if any(schema_keys.get(key, key) not in available for key in options):
        raise AdapterError("SCHEMA_UNAVAILABLE", "Installed REA schema lacks a requested option",
                           requested_options=list(options), available_options=sorted(available))
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["probe", "invoke"])
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--launcher")
    parser.add_argument("--expected-version")
    parser.add_argument("--command", choices=sorted(STATIC_COMMANDS))
    parser.add_argument("--artifact")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--option", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-output", type=int, default=MAX_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 120 or not 1024 <= args.max_output <= MAX_OUTPUT:
        parser.error(f"--timeout must be 1..120 seconds; --max-output must be 1024..{MAX_OUTPUT} bytes")
    if args.operation == "invoke" and not all([args.command, args.artifact, args.expected_version]):
        parser.error("invoke requires command, artifact and expected version")
    if args.expected_sha256 and not re.fullmatch(r"[0-9a-f]{64}", args.expected_sha256):
        parser.error("Expected SHA256 must be a 64-character lowercase digest")
    try:
        result = execute(args)
    except OSError as exc:
        parser.error(f"Cannot create new evidence directory: {type(exc).__name__}")
    print(json.dumps(result))
    return 0 if result["status"] in {"AVAILABLE_UNVERIFIED", "VERIFIED_TOOL_CALL"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
