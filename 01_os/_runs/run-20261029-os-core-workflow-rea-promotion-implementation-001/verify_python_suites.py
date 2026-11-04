"""Run the candidate's independent pytest suites with isolated temporary roots."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile


SUITES = {
    "workflow": "01_os/06_execution/workflow/minimum_operational_loop",
    "prms": "01_os/06_execution/boot/context_management/prms/tests",
    "task_loop": "01_os/06_execution/task_orchestration/big_task",
    "project_context": "01_os/06_execution/task_discipline/project_context",
    "rea": "01_os/06_execution/tools/rea",
}


def check_suite(name, target, temp_root):
    args = [sys.executable, "-B", "-X", "utf8", "-m", "pytest", target,
            "-q", "-p", "no:cacheprovider", "--basetemp", str(temp_root / name)]
    return subprocess.run(args, capture_output=True, check=False)


def main():
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="workflow-rea-suites-") as directory:
        with ThreadPoolExecutor(max_workers=3) as workers:
            futures = {name: workers.submit(check_suite, name, target, Path(directory))
                       for name, target in SUITES.items()}
            for name, future in futures.items():
                result = future.result()
                print(f"{name} exit_code={result.returncode}", flush=True)
                sys.stdout.buffer.write(result.stdout)
                sys.stdout.buffer.flush()
                sys.stderr.buffer.write(result.stderr)
                sys.stderr.buffer.flush()
                outcomes.append(result.returncode)
    return int(any(outcomes))


if __name__ == "__main__":
    raise SystemExit(main())
