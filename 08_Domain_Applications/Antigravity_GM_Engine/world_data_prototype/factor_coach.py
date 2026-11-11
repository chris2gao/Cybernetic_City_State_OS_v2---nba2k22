"""Keep current COACHDATA readback, stored GAMEPLAN and consumed game settings distinct."""
from contextlib import closing
import hashlib
import json

from engine import connect
from factor_adapters import adapter_contract, coach_field
from factor_readback import _bound_report, _source_units
from factor_settlement import _read_clock, _sha
from schema_model import GAMEPLAN_HEADER_MAP


COACH_CAPTURE_FAMILIES = ("game-mode", "planning")


def capture_coach_exposure(host, study, plan, *, directory, report_sha256, binding,
                            proof_raw, approved_proof_sha256):
    """Reconcile independently accepted READ_COACH_CURRENT observations with bound opponent plans."""
    if hashlib.sha256(proof_raw).hexdigest() != approved_proof_sha256:
        raise PermissionError("COACH_EXPOSURE_PROOF_PIN_MISMATCH")
    proof = json.loads(proof_raw)
    scope = {key: binding[key] for key in ("save_id", "worldline_id", "loaded_filename", "binding_sha256", "epoch")}
    if (proof["schema"] != "nba2k22.vae.coach_exposure.v1" or proof["mode"] != "LIVE"
            or proof["binding"] != scope or proof["planning_report_sha256"] != report_sha256
            or not proof["independent_review_ref"]):
        raise ValueError("COACH_EXPOSURE_PROOF_SCOPE_MISMATCH")
    assignments = list(plan["teams"].values())
    if (not assignments or len({row["team_id"] for row in assignments}) != len(assignments)
            or any(row["uid"] is not None or study.factors[row["factor_id"]].category != "coach" for row in assignments)):
        raise ValueError("COACH_EXPOSURE_REQUIRES_TEAM_ASSIGNMENT")
    reads = {row["team_id"]: row for row in proof["current_projection"]}
    if len(reads) != len(proof["current_projection"]) or set(reads) != {row["team_id"] for row in assignments}:
        raise ValueError("COACH_CURRENT_PROJECTION_TEAM_SET_MISMATCH")
    consumers = {}
    for row in proof["consumers"]:
        key = row["game_id"], row["team_id"]
        if key in consumers or row["verified"] is not True or not _sha(row["source_sha256"]):
            raise ValueError("COACH_GAME_CONSUMER_EVIDENCE_INVALID")
        consumers[key] = row
    report = _bound_report(host, directory, report_sha256, plan, binding)
    exposure, expected_keys = [], set()
    with closing(connect(host.database, True)) as conn:
        units = _source_units(conn, report, binding["season_id"], COACH_CAPTURE_FAMILIES)
        day, minutes = _read_clock(conn, units["game-mode"])
        if (day.isoformat(), minutes) != (plan["start"], 0):
            raise ValueError("COACH_PLANNING_CAPTURE_NOT_AT_WINDOW_START")
        for assignment in assignments:
            contract = adapter_contract(study.factors[assignment["factor_id"]])
            packed = coach_field(contract)
            name = contract.layout["native_key"]
            current = reads[assignment["team_id"]]
            data = current["data"]
            value = data["known_current_settings"][name]
            if (current["read_action"] != "READ_COACH_CURRENT" or not _sha(current["source_sha256"])
                    or current["read_only"] is not True or data["team_id"] != assignment["team_id"]
                    or data["reciprocal_owner_matches"] is not True or type(value) is not int or value not in packed.legal
                    or value != assignment["target"]):
                raise ValueError("COACH_CURRENT_PROJECTION_READBACK_MISMATCH")
            for game in plan["games"]:
                team = assignment["team_id"]
                if team not in (game["home_team"], game["away_team"]):
                    continue
                opponent = game["away_team"] if team == game["home_team"] else game["home_team"]
                key = game["game_id"], team
                expected_keys.add(key)
                column = GAMEPLAN_HEADER_MAP[name]
                stored = conn.execute(f"""
                    SELECT p.plan_id,p.{column},p.is_in_use_raw,p.is_tainted_raw
                    FROM gameplan_observations p JOIN teams t ON t.team_id=p.team_id
                    JOIN teams o ON o.team_id=p.opponent_team_id
                    WHERE p.unit_id=? AND t.native_team_id=? AND o.native_team_id=?
                """, (units["planning"], team, opponent)).fetchall()
                if len(stored) != 1:
                    raise ValueError("COACH_STORED_OPPONENT_PLAN_NOT_UNIQUE")
                stored_plan, stored_value, in_use, tainted = tuple(stored[0])
                consumer = consumers.get(key)
                verified = bool(consumer is not None and consumer["factor_id"] == assignment["factor_id"]
                                and consumer["opponent_team_id"] == opponent and consumer["value"] == value
                                and consumer["game_date"] == game["date"])
                if consumer is not None and not verified:
                    raise ValueError("COACH_GAME_CONSUMER_ASSIGNMENT_MISMATCH")
                exposure.append({"game_id": game["game_id"], "team_id": team, "opponent_team_id": opponent,
                                 "factor_id": assignment["factor_id"], "native_key": name, "applied_value": value,
                                 "current_projection_source": current["source_sha256"], "stored_plan_id": stored_plan,
                                 "stored_plan_value": stored_value, "stored_in_use": in_use, "stored_tainted": tainted,
                                 "stored_matches_projection": stored_value == value,
                                 "consumer_source": consumer["source_sha256"] if consumer else None,
                                 "qualified": verified, "status": "CONSUMER_VERIFIED" if verified else "CONSUMER_UNVERIFIED"})
    if not consumers.keys() <= expected_keys:
        raise ValueError("COACH_CONSUMER_GAME_OUTSIDE_PLAN")
    return {"mode": "LIVE", "worldline_id": binding["worldline_id"], "start": plan["start"], "stop_exclusive": plan["stop_exclusive"],
            "planning_report_sha256": report_sha256, "proof_sha256": approved_proof_sha256,
            "planning_unit": units["planning"], "exposures": exposure}
