"""Run the actual regression suites with a private pytest temporary root."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
import tempfile


SUITES = [
    "01_os/06_execution/workflow",
    "01_os/06_execution/task_orchestration",
    "01_os/06_execution/task_discipline",
    "01_os/03_mechanisms/stage_collaborative_deliberation/实现",
    "01_os/06_execution/boot/mechanism_activation",
    "01_os/06_execution/tools/rea",
]
ACTIVATION = "01_os/06_execution/boot/mechanism_activation"
PUBLICATION = "01_os/06_execution/workflow/publication_gate/test_publication_gate.py"
PYTEST = [sys.executable, "-B", "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider"]


def test_jobs():
    collected = subprocess.run([*PYTEST, "--collect-only", PUBLICATION],
                               capture_output=True, check=True, encoding="utf-8")
    tests = [line for line in collected.stdout.splitlines() if line.startswith(PUBLICATION + "::")]
    if not tests or len(tests) != len(set(tests)):
        raise RuntimeError("publication regression collection is empty or contains duplicates")
    jobs = {}
    for suite in SUITES:
        if suite == ACTIVATION:
            jobs[suite] = (["."], suite)
        elif suite.endswith("/workflow"):
            jobs[suite] = ([suite, "--ignore", PUBLICATION], None)
        else:
            jobs[suite] = ([suite], None)
    for shard in range(4):
        jobs[f"publication_gate/shard-{shard + 1}"] = (tests[shard::4], None)
    return jobs


def run_suite(name, args, cwd, temp_root):
    return subprocess.run(
        [*PYTEST, "--basetemp", str(temp_root / Path(name).name), *args],
        cwd=cwd, capture_output=True, check=False,
    )


def main():
    exit_codes = []
    with tempfile.TemporaryDirectory(prefix="core-workflow-lightweight-") as root:
        with ThreadPoolExecutor(max_workers=4) as pool:
            runs = {pool.submit(run_suite, name, args, cwd, Path(root)): name
                    for name, (args, cwd) in test_jobs().items()}
            for future in as_completed(runs):
                result = future.result()
                print(f"{runs[future]}: exit_code={result.returncode}", flush=True)
                sys.stdout.buffer.write(result.stdout)
                sys.stdout.buffer.flush()
                sys.stderr.buffer.write(result.stderr)
                sys.stderr.buffer.flush()
                exit_codes.append(result.returncode)
    return int(any(exit_codes))


if __name__ == "__main__":
    raise SystemExit(main())
