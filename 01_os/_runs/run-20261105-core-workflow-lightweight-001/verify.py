"""Run the actual regression suites with a private pytest temporary root."""
from concurrent.futures import ThreadPoolExecutor
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


def run_suite(suite, temp_root):
    return subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--basetemp", str(temp_root / Path(suite).name), suite],
        capture_output=True, check=False,
    )


def main():
    exit_codes = []
    with tempfile.TemporaryDirectory(prefix="core-workflow-lightweight-") as root:
        with ThreadPoolExecutor(max_workers=3) as pool:
            runs = {suite: pool.submit(run_suite, suite, Path(root)) for suite in SUITES}
            for suite, future in runs.items():
                result = future.result()
                print(f"{suite}: exit_code={result.returncode}", flush=True)
                sys.stdout.buffer.write(result.stdout)
                sys.stdout.buffer.flush()
                sys.stderr.buffer.write(result.stderr)
                sys.stderr.buffer.flush()
                exit_codes.append(result.returncode)
    return int(any(exit_codes))


if __name__ == "__main__":
    raise SystemExit(main())
