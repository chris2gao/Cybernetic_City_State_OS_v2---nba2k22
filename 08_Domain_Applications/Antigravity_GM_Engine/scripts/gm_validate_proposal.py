"""Validate a pending proposal; no approval or execution command is available."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from gm_core.data_reader import DataReader, load_json, identifier
from gm_core.decisions import validate_proposal
from gm_core.history import StateStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--save-id", type=identifier, required=True)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--run", type=Path, help="Calculation references from the selected prepared run")
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--save-pending", action="store_true")
    args = parser.parse_args()
    data = DataReader(args.project_root).read(args.save_id)
    references = {}
    if args.run:
        run = load_json(args.run)
        if run.get("career_id") != data.source.career_id or run.get("source", {}).get("batch_id") != data.source.batch_id:
            parser.error("Calculation run belongs to another source")
        if run.get("policy", {}).get("policy_id") != data.policy["policy_id"] or run.get("policy", {}).get("gm_policy_id") != data.gm_policy["policy_id"]:
            parser.error("Calculation run uses another gameplay/operating policy")
        references = run["calculations"]
    proposal = load_json(args.proposal)
    verdict = validate_proposal(proposal, data, references)
    if args.save_pending and verdict["valid"]:
        verdict["saved_to"] = str(StateStore(args.project_root, args.state_root).save_pending(proposal, verdict))
    print(json.dumps(verdict, ensure_ascii=True, indent=2))
    return 0 if verdict["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
