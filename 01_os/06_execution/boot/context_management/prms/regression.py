"""Run the existing working-set regression without pytest's shared temp root."""
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[5]
    with tempfile.TemporaryDirectory(prefix="prms-working-set-regression-") as temp:
        return subprocess.run([sys.executable, "-B", "-m", "pytest",
            "01_os/06_execution/boot/context_management/working_set/test_working_set.py",
            "-q", "-p", "no:cacheprovider", "--basetemp", str(Path(temp) / "pytest")], cwd=root).returncode


if __name__ == "__main__":
    sys.exit(main())
