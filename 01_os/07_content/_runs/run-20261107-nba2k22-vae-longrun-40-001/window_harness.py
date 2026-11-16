"""Single-window offline controller. Live authority and journals stay in their owning Hosts."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from experiment_round import analyze, digest, fixture, plan

FIXTURE_SCOPE = "SYNTHETIC_FIXTURE_NOT_A_LIVE_ROUND"


class FixturePort:
    """Explicit synthetic port for replay and fault injection only."""

    def __init__(self, plan_data, fault=None):
        self.plan = plan_data
        self.fault = fault
        self.commands = 0
        self.setters = 0

    def preflight(self):
        if self.fault in {"wrong_binding", "lost_focus", "season_boundary", "not_persistent"}:
            raise ValueError(self.fault)

    def apply_exact_batch(self, action):
        if self.fault == "cas":
            return {"status": "CAS_MISMATCH"}
        self.setters += 1
        return {"status": "VERIFIED", "fixture_action_digest": digest(action),
                "observed_value": action["target"]}

    def simulate_once(self):
        self.commands += 1
        if self.fault == "crash":
            raise RuntimeError("simulated process crash after dispatch")
        return "UNKNOWN" if self.fault == "unknown" else "RETURNED"

    def capture(self):
        plan_data = self.plan
        assignments = {item["team_id"]: item for item in plan_data["assignments"]}
        games = []
        for game in plan_data["games"]:
            unit = f"fixture-unit-{game['game_id']}"
            row = dict(game, final=True, was_simulated=True, unit=unit, team_box_unit=unit,
                       player_box_unit=unit, score_conserved=True, team_boxes=[])
            for team_id in (game["home"], game["away"]):
                player = assignments[team_id]
                fga = 9 + (team_id % 3) + {"H": 2, "L": -2}.get(player["arm"], 0)
                row["team_boxes"].append({
                    "team_id": team_id, "candidate_uid": player["uid"], "disposition": "PLAYED",
                    "minutes": 27, "fga": fga, "team_fga": 83,
                })
            games.append(row)
        if self.fault == "partial":
            games.pop()
        if self.fault == "mixed_unit":
            games[0]["player_box_unit"] = "other-unit"
        if self.fault == "score":
            games[0]["score_conserved"] = False
        if self.fault == "dnp":
            games[0]["team_boxes"][0].update(disposition="DNP", minutes=0, fga=0)
        if self.fault == "unobserved":
            games[0]["team_boxes"][0].update(disposition="UNOBSERVED", minutes=None, fga=None)
        return {"identity": plan_data["identity"], "today": plan_data["stop"], "games": games}


class Journal:
    def __init__(self, root, plan_data):
        self.root = root / plan_data["research_plan_digest"]

    def write(self, name, payload):
        with (self.root / f"{name}.json").open("x", encoding="utf-8") as target:
            json.dump(payload, target, sort_keys=True, indent=2)
            target.flush()

    def inspect(self):
        return sorted(item.stem for item in self.root.glob("*.json"))

    def stop(self, reason):
        self.write("operator-stop", {"state": "STOP_REQUESTED", "reason": reason})


def fixture_permit(plan_data):
    return {"scope": "FIXTURE_ONLY", "plan_digest": plan_data["research_plan_digest"],
            "setter_digests": [digest(action) for action in plan_data["write_candidates"]],
            "calendar_target": plan_data["selected_end_inclusive"], "calendar_commands": 1}


def gate(plan_data, permit):
    if plan_data["evidence_scope"] != FIXTURE_SCOPE:
        raise ValueError("Live controller remains disabled until #39 and S4 authority are bound")
    body = {key: value for key, value in plan_data.items() if key != "research_plan_digest"}
    if (digest(body) != plan_data["research_plan_digest"] or permit != fixture_permit(plan_data)
            or plan_data["factor"] != "SHOT_TENDENCY"):
        raise ValueError("Exact fixture plan, window and separate batch bindings required")


def execute_fixture(root, plan_data, permit, port):
    gate(plan_data, permit)
    if type(port) is not FixturePort or port.plan != plan_data:
        raise ValueError("Offline harness accepts only its deterministic synthetic port")
    port.preflight()
    journal = Journal(root, plan_data)
    root.mkdir(parents=True, exist_ok=True)
    journal.root.mkdir()
    journal.write("intent", {"scope": FIXTURE_SCOPE, "digest": plan_data["research_plan_digest"]})
    try:
        for index, action in enumerate(plan_data["write_candidates"]):
            if "operator-stop" in journal.inspect():
                raise RuntimeError("operator stop after claim")
            journal.write(f"setter-{index:02d}-intent", {"digest": digest(action)})
            receipt = port.apply_exact_batch(action)
            journal.write(f"setter-{index:02d}-result", receipt)
            if (receipt["status"] != "VERIFIED" or receipt["fixture_action_digest"] != digest(action)
                    or receipt["observed_value"] != action["target"]):
                raise RuntimeError("setter not verified")
        if "operator-stop" in journal.inspect():
            raise RuntimeError("operator stop after claim")
        journal.write("calendar-intent", {"target": permit["calendar_target"]})
        if port.simulate_once() != "RETURNED":
            raise RuntimeError("calendar dispatch outcome unknown")
        journal.write("calendar-return", {"state": "RETURNED"})
        result = analyze(plan_data, port.capture())
        journal.write("checkpoint", {"state": "FIXTURE_VERIFIED", "analysis": result})
        return result
    except Exception as error:
        journal.write("halt", {"state": "PAUSE_AND_RECONCILE", "reason": str(error)})
        raise


def reconcile_fixture(root, plan_data, capture):
    journal = Journal(root, plan_data)
    events = journal.inspect()
    if plan_data["evidence_scope"] != FIXTURE_SCOPE or not {"intent", "calendar-intent"} <= set(events):
        raise ValueError("No bound fixture calendar attempt to reconcile")
    result = analyze(plan_data, capture)
    journal.write("reconciled-readback", {"state": "FIXTURE_READBACK_VERIFIED_NO_REPLAY", "analysis": result})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["plan", "dry-run", "one-window", "inspect", "reconcile", "stop"])
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--reason", default="operator request")
    args = parser.parse_args()
    plan_data = plan(fixture(), 20261107)
    permit = fixture_permit(plan_data)
    if args.command == "plan":
        output = plan_data
    elif args.command == "dry-run":
        gate(plan_data, permit)
        output = {"state": "FIXTURE_PREFLIGHT_PASS", "digest": plan_data["research_plan_digest"]}
    elif args.command == "one-window":
        output = execute_fixture(args.journal, plan_data, permit, FixturePort(plan_data))
    elif args.command == "reconcile":
        if not args.capture:
            parser.error("--capture is required for reconciliation")
        output = reconcile_fixture(args.journal, plan_data, json.loads(args.capture.read_bytes()))
    else:
        journal = Journal(args.journal, plan_data)
        if args.command == "stop":
            journal.stop(args.reason)
        output = {"events": journal.inspect()}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
