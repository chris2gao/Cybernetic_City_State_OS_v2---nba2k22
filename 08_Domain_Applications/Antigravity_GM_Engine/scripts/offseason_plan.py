"""External bidding simulation; no game attachment, capture, approval or execution."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.offseason import plan
from gm_core.offseason_io import read_json, save_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Explicitly labelled synthetic frozen snapshot")
    parser.add_argument("--output", required=True, help="Parent directory below _exports")
    args = parser.parse_args()
    try:
        data = read_json(args.input)
        artifacts = plan(data)
        directory, write_status = save_run(ROOT, args.output, data, artifacts)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc),
                          "executable_operation_ready": False}, ensure_ascii=False))
        return 2
    run = artifacts["offseason_run.json"]
    print(json.dumps({"status": run["status"], "output": str(directory),
                      "write_status": write_status, "executable_operation_ready": False}, ensure_ascii=False))
    return 2 if run["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
