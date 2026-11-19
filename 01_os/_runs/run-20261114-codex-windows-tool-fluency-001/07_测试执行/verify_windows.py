"""Run-scoped Windows replay. No game process, save, domain import or live tool."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = "953b3e34d5432b93f05cdff7215da49fe7f87833"
ADAPTER = "01_os/06_execution/tools/rea/adapter.py"
CASES = ("discovery", "shell", "git", "history", "reuse", "diagnostics", "static")
sys.path.insert(0, str(ROOT / "01_os/06_execution/boot/context_management/prms"))
from source import GitSource


def run(argv, cwd=ROOT, timeout=30):
    return subprocess.run([str(arg) for arg in argv], cwd=cwd, capture_output=True,
                          timeout=timeout, check=True)


def load_adapter(mode):
    if mode == "baseline":
        raw = run(["git", "show", f"{BASE}:{ADAPTER}"]).stdout
    else:
        raw = (ROOT / ADAPTER).read_bytes()
    module = types.ModuleType("replay_adapter_" + mode)
    exec(compile(raw, ADAPTER, "exec"), module.__dict__)
    return module


def ps_case(case, workspace):
    pwsh = shutil.which("pwsh.exe")
    assert pwsh, "PowerShell 7 executable required"
    result = run([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive",
                  "-File", HERE / "shell_cases.ps1", "-Python", sys.executable,
                  "-Workspace", workspace, "-Case", case])
    return json.loads(result.stdout.decode("utf-8-sig"))


def perform(case, mode, workspace):
    if case == "discovery":
        paths = run(["rg", "--files", "01_os/04_skills_and_tools",
                     "01_os/06_execution/tools/rea", "-g", "*.md", "-g", "*.py"])
        names = paths.stdout.decode("utf-8").replace("\\", "/").splitlines()
        assert ADAPTER in names
        return {"bounded_path_count": len(names), "adapter_entry_found": True,
                "search_roots": ["01_os/04_skills_and_tools", "01_os/06_execution/tools/rea"]}
    if case == "shell":
        probe = ps_case("probe", workspace)
        assert probe["edition"] == "Core" and probe["version"].startswith("7.")
        assert probe["no_profile"] and probe["non_interactive"]
        return probe
    if case == "git":
        return {name: run(["git", *arguments]).stdout.decode("utf-8").strip()
                for name, arguments in {
                    "head": ["rev-parse", "HEAD"],
                    "branch": ["branch", "--show-current"],
                    "status": ["status", "-sb"],
                    "diff": ["diff", "--stat"],
                }.items()}
    if case == "history":
        source = GitSource(ROOT, BASE, "chris2gao/Cybernetic_City_State_OS_v2---core")
        raw, proof = source.read(ADAPTER)
        return {"blob": proof["blob"], "sha256": proof["sha256"], "bytes": len(raw)}
    if case == "reuse":
        # Execute the existing historical processor, without another source script.
        options = load_adapter("baseline").command_options(
            "inspect-byte-entropy", ["length=4096", "block-size=256"])
        echo = ps_case("arguments", workspace)
        assert echo["echo"] == [echo["expected_payload"], str(workspace), ""], json.dumps(echo, ensure_ascii=True)
        assert echo["native_exit"] == 7 and echo["warning_exit"] == 0
        assert echo["warning_stdout"] == "ok" and "fixture warning" in echo["warning_stderr"]
        assert "fixture native failure" in echo["failure_stderr"]
        assert echo["powershell_error_id"] and echo["cmd_exit"] == 0
        return {"options": options, "argv_equal": True, "native_exit": 7,
                "warning_exit": 0, "powershell_failure_caught": True,
                "cmd_version": echo["cmd_version"], "temporary_source_scripts": 0}
    if case == "diagnostics":
        module = load_adapter(mode)
        historical = json.loads((HERE / "ge01_cases.json").read_text(encoding="utf-8"))
        try:
            module.read_result(1, json.dumps(historical["validation_error"]).encode())
        except module.AdapterError as exc:
            parameter = {"status": exc.status, **exc.details}
        else:
            raise AssertionError("Parameter failure accepted")
        expected = {"id": 123, "day": 20211115, "home": 1, "away": 28}
        observed = dict(expected, away=27)
        differences = [{"field": key, "expected": value, "observed": observed.get(key)}
                       for key, value in expected.items() if observed.get(key) != value]
        assert differences == [{"field": "away", "expected": 28, "observed": 27}]
        assert historical["fixture_error"]["observed_row_values"] == "NOT_RECORDED"
        return {"parameter_error": parameter, "synthetic_fixture_difference": differences,
                "historical_fixture_stage": "PRE_DISPATCH_PRECONDITION_FAILED",
                "historical_field_values": "NOT_RECORDED",
                "external_unknown_policy": "retain_original_unknown_no_automatic_replay"}
    if case == "static":
        module = load_adapter(mode)
        args = argparse.Namespace(operation="invoke", evidence_dir=workspace / "rea",
                                  launcher=None, expected_version="6.8.0",
                                  command="inspect-byte-entropy", artifact=shutil.which("git.exe"),
                                  expected_sha256=None, option=["length=4096"], timeout=30,
                                  max_output=module.MAX_OUTPUT)
        receipt = module.execute(args)
        assert receipt["status"] == "VERIFIED_TOOL_CALL", receipt
        output = json.loads((args.evidence_dir / "result.stdout").read_bytes())
        evidence = output["data"]
        # Evidence IDs can differ per invocation. Compare the actual entropy data.
        return {"source": receipt["source"], "parameters": receipt["parameters"],
                "predicate_type": evidence.get("predicate_type"),
                "normalized_result": evidence.get("normalized_result"),
                "raw_result": evidence.get("raw_result"),
                "automatic_replay": receipt["automatic_replay"],
                "version": receipt["observed_version"]}
    raise AssertionError(case)


def verify():
    assert os.name == "nt", "This acceptance replay requires actual Windows"
    registry = (ROOT / "01_os/05_registry/skills_and_tools_v1.yml").read_text(encoding="utf-8")
    assert "01_os/04_skills_and_tools/windows/README.md" in registry
    assert "windows/README.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="Core 工具 对照 ") as temp:
        parent = Path(temp)
        results = {}
        for mode in ("baseline", "candidate"):
            workspace = parent / mode
            workspace.mkdir()
            start = time.perf_counter()
            results[mode] = {}
            for case in CASES:
                if case == "git":
                    continue
                directory = workspace / case
                directory.mkdir()
                results[mode][case] = perform(case, mode, directory)
            results[mode]["elapsed_seconds"] = time.perf_counter() - start
        before, after = results["baseline"], results["candidate"]
        assert before["history"] == after["history"]
        assert before["reuse"] == after["reuse"]
        assert before["static"] == after["static"]
        assert after["static"]["normalized_result"] is not None
        assert before["diagnostics"]["parameter_error"]["status"] == "TOOL_FAILED"
        error = after["diagnostics"]["parameter_error"]
        assert error["status"] == "INVALID_REQUEST"
        assert "60000" in error["field_errors"][0]["message"]
        block = run([sys.executable, "-B", ROOT / ADAPTER, "invoke",
                     "--evidence-dir", parent / "real-block-size",
                     "--expected-version", "6.8.0", "--command", "inspect-byte-entropy",
                     "--artifact", shutil.which("git.exe"), "--option", "length=4096",
                     "--option", "block-size=256"])
        block_receipt = json.loads(block.stdout)
        assert block_receipt["status"] == "VERIFIED_TOOL_CALL"
        assert block_receipt["parameters"]["block-size"] == "256"
        print(json.dumps({"status": "success", "history_and_business_outputs_equal": True,
                          "diagnostic_root_cause_preserved": True,
                          "real_cli_block_size_verified": True,
                          "baseline_seconds": before["elapsed_seconds"],
                          "candidate_seconds": after["elapsed_seconds"],
                          "shell": after["shell"]}, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "candidate"))
    parser.add_argument("--cases", nargs="+", choices=CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode is None:
        verify()
        return
    if args.output is None or not args.cases:
        parser.error("measurement requires --cases and --output")
    start = time.perf_counter()
    first_business_seconds = None
    with tempfile.TemporaryDirectory(prefix="Core 工具 对照 ") as temp:
        rows = {}
        for case in args.cases:
            directory = Path(temp) / case
            directory.mkdir()
            tick = time.perf_counter()
            rows[case] = {"result": perform(case, args.mode, directory),
                          "seconds": time.perf_counter() - tick}
            if case in {"reuse", "static"} and first_business_seconds is None:
                first_business_seconds = time.perf_counter() - start
    result = {"mode": args.mode, "cases": rows, "elapsed_seconds": time.perf_counter() - start,
              "first_business_seconds": first_business_seconds}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"mode": args.mode, "cases": args.cases,
                      "seconds": result["elapsed_seconds"], "output": args.output.name}))


if __name__ == "__main__":
    main()
