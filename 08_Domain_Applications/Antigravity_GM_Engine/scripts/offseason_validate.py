"""Offline proposal replay; never certifies live freshness, approval or game writes."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.offseason import validate_proposal
from gm_core.offseason_io import local_output, read_json, read_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-dir", required=True, help="Local run version directory inside _exports")
    parser.add_argument("--current-context", help="Independent context declaration; not a live game observation")
    args = parser.parse_args()
    try:
        directory = local_output(ROOT, args.plan_dir)
        frozen = read_json(directory / "frozen_input.json")
        result = validate_proposal(frozen, read_run(directory),
                                   read_json(args.current_context) if args.current_context else None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"status": "BLOCKED", "errors": [str(exc)], "executable_operation_ready": False}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "SIMULATION_CONSISTENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
