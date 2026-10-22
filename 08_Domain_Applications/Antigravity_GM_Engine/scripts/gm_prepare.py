"""Explicit offline preparation/simulation; never starts a model or game action."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from gm_core.data_reader import DataReader, identifier
from gm_core.history import StateStore, previous_run
from gm_core.reports import prepare_run, markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--save-id", type=identifier, required=True)
    parser.add_argument("--run-id", type=identifier, required=True)
    parser.add_argument("--mode", choices=("simulation", "analysis"), required=True)
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--previous-run", type=Path)
    parser.add_argument("--completed-drafts", type=int, help="Only the player's explicitly confirmed completed-draft count")
    args = parser.parse_args()
    if args.completed_drafts is not None and args.completed_drafts < 0:
        parser.error("Completed draft count cannot be negative")
    data = DataReader(args.project_root).read(args.save_id)
    previous = previous_run(data, args.previous_run)
    run = prepare_run(data, args.run_id, args.mode, previous, args.completed_drafts)
    destination = StateStore(args.project_root, args.state_root).save_run(run, markdown(run))
    print(f"{run['status']}: {run['teams_reviewed']} teams; {run['readiness']}; no formal decisions or game actions")
    print(f"Data updated: {data.source.data_updated_at}; uploaded: {data.source.uploaded_at}")
    print(f"Output: {destination}")


if __name__ == "__main__":
    main()
