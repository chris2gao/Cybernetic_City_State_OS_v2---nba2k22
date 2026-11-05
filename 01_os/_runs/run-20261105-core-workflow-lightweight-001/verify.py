"""Run the actual regression suites with a private pytest temporary root."""
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


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="core-workflow-lightweight-") as root:
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--basetemp", str(Path(root) / "pytest"), *SUITES],
            check=False,
        )
    raise SystemExit(result.returncode)
