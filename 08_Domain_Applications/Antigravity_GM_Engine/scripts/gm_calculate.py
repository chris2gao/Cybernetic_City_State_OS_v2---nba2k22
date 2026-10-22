"""Run a named deterministic calculation from an explicit JSON request."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from gm_core import calculations
from gm_core.data_reader import load_json
from gm_core.history import StateStore, write_json

OPERATIONS = {name: getattr(calculations, name) for name in
              ("difference", "observed_sum", "distribution", "win_percentage", "efficiency",
               "field_changes", "roster_changes", "draft_year", "salary_exchange", "draft_pick_window")}


def calculate(request):
    if not request.get("source_batch_id") or not request.get("career_id"):
        raise ValueError("Calculation requests require career_id and source_batch_id")
    operation = request.get("operation")
    if operation not in OPERATIONS or not isinstance(request.get("inputs"), dict):
        raise ValueError("Unknown calculation or invalid inputs")
    output = OPERATIONS[operation](**request["inputs"])
    if isinstance(output, dict) and "availability" not in output and operation in ("field_changes", "salary_exchange"):
        output = calculations.result(output)
    return {"schema_version": 1, "career_id": request["career_id"],
            "source_batch_id": request["source_batch_id"], "operation": operation,
            "calculation_version": calculations.VERSION, "input_provenance": "CALLER_PROVIDED_REQUEST",
            "result": output, "execution_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    response = calculate(load_json(args.request))
    if args.output:
        StateStore(ROOT, args.output.parent)
        write_json(args.output, response)
    else:
        print(json.dumps(response, ensure_ascii=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
