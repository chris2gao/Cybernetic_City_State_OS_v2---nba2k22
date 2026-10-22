"""Offline coaching facts and proposal semantics; never imports game modules."""
from datetime import date
from coach_codec import load_profile, block_key, encode_changes, integer

CONTEXT = ("career_id", "source_batch_id", "game_season", "game_date", "policy_id")

def claims_authority(value):
    if isinstance(value, dict):
        return any((key in {"approved", "player_approved", "execution_authorized", "executed",
                            "write_authority"} and item not in (False, None))
                   or claims_authority(item) for key, item in value.items())
    return isinstance(value, list) and any(claims_authority(item) for item in value)

def validate_context(context, isolated=False):
    for key in CONTEXT:
        if key == "game_date" and isolated and context.get(key) is None:
            continue
        if not isinstance(context.get(key), str) or not context[key].strip():
            raise ValueError("CONTEXT_REQUIRED_" + key)
    if context.get("game_date") is not None:
        date.fromisoformat(context["game_date"])
    if context["policy_id"] != "PLAYER_RULES_20261017_V3":
        raise ValueError("WRONG_GAMEPLAY_POLICY")
    return {key: context[key] for key in CONTEXT}

def raw_from_team(team):
    raw = bytearray(0x160)
    for key, value in team["blocks"].items():
        offset, size = (int(part, 0) for part in key.split(":"))
        data = bytes.fromhex(value)
        if size != len(data) or offset < 0 or offset + size > len(raw):
            raise ValueError("INVALID_SNAPSHOT_BLOCK")
        raw[offset:offset + size] = data
    return bytes(raw)

def validate_plan(plan, snapshot, profile=None):
    profile = profile or load_profile()
    errors, readiness, prepared = [], [], []
    try:
        if not isinstance(plan, dict) or claims_authority(plan):
            raise ValueError("PROPOSAL_CANNOT_AUTHORIZE_EXECUTION")
        if not isinstance(snapshot,dict):
            raise ValueError("VERIFIED_COACHING_SNAPSHOT_REQUIRED")
        if plan.get("operation") != "TACTIC_CHANGE" or plan.get("status") != "PROPOSED":
            raise ValueError("TACTIC_CHANGE_PROPOSED_REQUIRED")
        for key in ("decision_id", "action_id", "snapshot_id", "expected_effect"):
            if not isinstance(plan.get(key), str) or not plan[key].strip():
                raise ValueError("REQUIRED_" + key)
        integer(plan.get("version"), 1, 1000000, "INVALID_VERSION")
        isolated = snapshot.get("environment") == "ISOLATED_TEST"
        validate_context(plan, isolated)
        if snapshot.get("schema_version") != 1 or snapshot.get("observation_status") != "OBSERVED_LIVE_READ_ONLY":
            raise ValueError("VERIFIED_COACHING_SNAPSHOT_REQUIRED")
        if snapshot.get("codec_version") != profile["codec_version"] or plan.get("codec_version") != profile["codec_version"]:
            raise ValueError("WRONG_CODEC_VERSION")
        selectable_ids=sorted(p["enum_id"] for p in snapshot["playbooks"] if p.get("name") and p.get("selectable",True))
        if len(set(selectable_ids))!=len(selectable_ids) or selectable_ids!=snapshot["loaded_playbook_ids"]:
            raise ValueError("INCONSISTENT_LOADED_PLAYBOOK_DIRECTORY")
        if any(plan.get(key) != snapshot.get(key) for key in CONTEXT) or plan["snapshot_id"] != snapshot["snapshot_id"]:
            raise ValueError("STALE_OR_WRONG_SOURCE")
        if plan.get("effect_status") != "SIM_EFFECT_PENDING_PLAYER_MONTH":
            raise ValueError("UNVERIFIED_EFFECT_CLAIM")
        integer(plan.get("team_id"), 0, 65535, "INVALID_TEAM_ID")
        rows = [t for t in snapshot["teams"] if t["team_id"] == plan["team_id"]]
        if len(rows) != 1 or plan.get("verified_coach_identity") != rows[0]["coach_identity"]:
            raise ValueError("WRONG_OR_AMBIGUOUS_COACH_IDENTITY")
        team = rows[0]
        scope = plan.get("scope")
        if scope == "VS_OPPONENT":
            opponent = plan.get("opponent_team_id")
            integer(opponent,0,65535,"INVALID_OPPONENT_TEAM_ID")
            if opponent==plan["team_id"]:
                raise ValueError("SELF_GAMEPLAN")
            records = [r for r in team.get("gameplans", []) if r["opponent_team_id"] == opponent]
            if len(records) != 1:
                raise ValueError("INVALID_OR_AMBIGUOUS_OPPONENT")
            # Presets are proposals only: never activate or alter Gameplan records.
            proposed = []
            for change in plan.get("changes", []):
                if not isinstance(change, dict) or set(change) != {"field","before_raw","after_raw"}:
                    raise ValueError("EXACT_CHANGE_CONTRACT_REQUIRED")
                if change["field"] not in records[0]["values"] or change["field"] not in profile["fields"]:
                    raise ValueError("MATCHUP_FIELD_UNVERIFIED")
                from coach_codec import validate_value
                validate_value(profile["fields"][change["field"]], change["after_raw"], snapshot["loaded_playbook_ids"], target=True)
                validate_value(profile["fields"][change["field"]], change["before_raw"], snapshot["loaded_playbook_ids"])
                if change["before_raw"] != records[0]["values"][change["field"]]:
                    raise ValueError("STALE_FIELD_VALUE")
                if change["field"] in proposed:
                    raise ValueError("UNKNOWN_OR_DUPLICATE_FIELD")
                proposed.append(change["field"])
            if not proposed:
                raise ValueError("SPECIFIC_CHANGES_REQUIRED")
            readiness.append("MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED")
        elif scope == "COACH_DEFAULT" and plan.get("opponent_team_id") is None:
            prepared = encode_changes(raw_from_team(team), plan.get("changes"), profile, snapshot["loaded_playbook_ids"])
            for block in prepared:
                key = block_key(block["offset"], block["size"])
                if key not in team["blocks"] or plan.get("old_blocks", {}).get(key) != team["blocks"][key]:
                    raise ValueError("FULL_OLD_BLOCK_REQUIRED")
            readiness += [profile["fields"][c["field"]]["readiness"] for c in plan["changes"]]
        else:
            raise ValueError("UNSUPPORTED_TACTICAL_SCOPE")
    except (ValueError, KeyError, TypeError, IndexError, OverflowError) as exc:
        errors.append(str(exc))
    return dict(valid=not errors, errors=errors, prepared_blocks=prepared if not errors else [],
                readiness=sorted(set(readiness)) if not errors else ["BLOCKED"],
                execution_authorized=False, effect_status="SIM_EFFECT_PENDING_PLAYER_MONTH")

def propose(snapshot, team_id, targets, decision_id, version, action_id, expected_effect,
            opponent_team_id=None, profile=None):
    profile = profile or load_profile()
    team = next(t for t in snapshot["teams"] if t["team_id"] == team_id)
    values = team["values"]
    if opponent_team_id is not None:
        values = next(r for r in team["gameplans"] if r["opponent_team_id"] == opponent_team_id)["values"]
    plan = dict(**{k:snapshot[k] for k in CONTEXT}, decision_id=decision_id, version=version,
                action_id=action_id, snapshot_id=snapshot["snapshot_id"], operation="TACTIC_CHANGE",
                status="PROPOSED", scope="VS_OPPONENT" if opponent_team_id is not None else "COACH_DEFAULT",
                opponent_team_id=opponent_team_id, team_id=team_id, codec_version=profile["codec_version"],
                verified_coach_identity=team["coach_identity"], expected_effect=expected_effect,
                effect_status="SIM_EFFECT_PENDING_PLAYER_MONTH", execution_authorized=False,
                old_blocks=team["blocks"], changes=[dict(field=f,before_raw=values[f],after_raw=v)
                                                  for f,v in targets.items()])
    result = validate_plan(plan, snapshot, profile)
    if not result["valid"]:
        raise ValueError(";".join(result["errors"]))
    return plan
