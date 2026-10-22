"""Isolated proposed state. v1 cannot approve or execute a decision."""
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path
import os
import tempfile

from .data_reader import identifier, load_json, timestamp


def compare_context(data, previous):
    source = previous["source"]
    if previous["career_id"] != data.source.career_id:
        raise ValueError("Previous run belongs to another career")
    if source.get('game_date') is None or data.source.game_date is None:
        raise ValueError('Game date is unconfirmed; cannot establish game-time continuity with a previous run')
    if date.fromisoformat(source["game_date"]) > date.fromisoformat(data.source.game_date):
        raise ValueError("Previous run is in a future game date; select a branch after rollback")
    if timestamp(source["data_updated_at"]) > timestamp(data.source.data_updated_at):
        raise ValueError("Previous run is from a later capture")
    return source["batch_id"] != data.source.batch_id


def previous_run(data, path=None):
    if not path:
        return None
    previous = load_json(path)
    compare_context(data, previous)
    return previous


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


class StateStore:
    def __init__(self, project_root, state_root=None):
        project = Path(project_root).resolve()
        self.root = Path(state_root or project / "gm_state").resolve()
        if self.root.is_relative_to(project) and not any(
            self.root.is_relative_to(project / allowed) for allowed in ("gm_state", "_exports")
        ):
            raise ValueError("GM output must be isolated from source, published facts and databases")

    def save_run(self, run, markdown):
        career, run_id = identifier(run["career_id"]), identifier(run["gm_run_id"])
        if run["status"] not in ("SIMULATION", "ANALYSIS_ONLY") or run["decisions"]:
            raise ValueError("Preparation stores analysis only, never formal decisions")
        parent = self.root / "careers" / career / "runs"
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / run_id
        if destination.exists():
            raise FileExistsError("Run already exists; use a distinct run ID")
        with tempfile.TemporaryDirectory(prefix=".gm_run_", dir=parent) as temporary:
            staged = Path(temporary) / "run"
            staged.mkdir()
            write_json(staged / "run.json", run)
            (staged / "REPORT.md").write_text(markdown, encoding="utf-8")
            for abbreviation, team in run["team_reviews"].items():
                identifier(abbreviation)
                write_json(staged / "teams" / f"{abbreviation}.json", team)
            os.replace(staged, destination)
        return destination

    def save_pending(self, proposal, verdict):
        if not verdict["valid"] or proposal.get("status", "PROPOSED") != "PROPOSED":
            raise ValueError("Only structurally valid unapproved proposals can be stored")
        destination = self.root / "careers" / identifier(proposal["career_id"]) / "proposals" / (
            f"{identifier(proposal['decision_id'])}_v{proposal['version']}.json")
        if destination.exists():
            raise FileExistsError("Proposal version is immutable")
        write_json(destination, {"proposal": dict(proposal, status="PROPOSED"),
                                 "validation": verdict, "approval_status": "NOT_GRANTED"})
        return destination
