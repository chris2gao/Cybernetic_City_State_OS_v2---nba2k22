"""Proposal semantics, not a player approval or an execution interface."""
from .data_reader import identifier, safe_child, load_json
from .tactics import check_field
from .trades import constraints
from .coverage import SOURCE_FIELDS, state_value, player_value

OPERATIONS = ("STRATEGY", "TRADE_INTEREST", "TRADE_PROPOSAL", "TACTIC_CHANGE", "COACHING_BATCH_CHANGE",
              "STAFF_CHANGE", "CONTRACT_CHANGE", "BUSINESS_CHANGE", "DRAFT_PLAN",
              "HISTORICAL_GRAVITY", "PLAYER_EDIT", "MC_GROWTH")


def approval_claim(value):
    if isinstance(value, dict):
        return any((key in ("approved", "player_approved", "executed", "write_authority", "execution_authorized") and item is not False and item is not None)
                   or approval_claim(item) for key, item in value.items())
    if isinstance(value, list):
        return any(approval_claim(item) for item in value)
    return False


def evidence_value(data, entry):
    relative = entry["file"]
    if not relative.endswith(".json"):
        raise ValueError("Evidence must reference a published JSON file")
    value = load_json(safe_child(data.batch_directory, relative))
    for part in entry["field"].split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def validate_proposal(proposal, data, calculation_ids=()):
    required = {"decision_id": str, "version": int, "career_id": str, "source_batch_id": str,
                "teams": list, "operation": str, "evidence": list, "calculation_refs": list,
                "expected_effect": str, "data_gaps": list, "requested_approval": list}
    errors, missing = [], []
    for name, kind in required.items():
        if type(proposal.get(name)) is not kind:
            errors.append(f"REQUIRED_{name}")
    if errors:
        return {"valid": False, "errors": errors, "readiness": "BLOCKED", "execution_authorized": False}
    try:
        identifier(proposal["decision_id"])
    except ValueError:
        errors.append("INVALID_DECISION_ID")
    if proposal["version"] < 1:
        errors.append("INVALID_VERSION")
    if proposal["career_id"] != data.source.career_id or proposal["source_batch_id"] != data.source.batch_id:
        errors.append("STALE_OR_WRONG_SOURCE")
    if proposal.get("status", "PROPOSED") != "PROPOSED" or approval_claim(proposal):
        errors.append("EXTERNAL_APPROVAL_OR_EXECUTION_CLAIM_REJECTED")
    if not proposal["teams"] or any(type(team) is not str or team not in data.teams for team in proposal["teams"]):
        errors.append("UNKNOWN_TEAM")
        return {"valid": False, "errors": errors, "readiness": "BLOCKED", "execution_authorized": False}
    operation = proposal["operation"]
    if operation not in OPERATIONS:
        errors.append("UNKNOWN_OPERATION")
    if operation in ("PLAYER_EDIT", "MC_GROWTH"):
        errors.append("PLAYER_EDIT_FORBIDDEN_OR_MC_DEFERRED")
    if proposal.get("changes") and operation not in ("TACTIC_CHANGE", "BUSINESS_CHANGE", "HISTORICAL_GRAVITY"):
        errors.append("CHANGES_NOT_ALLOWED_FOR_THIS_OPERATION")
    if not proposal["evidence"]:
        errors.append("EVIDENCE_REQUIRED")
    for entry in proposal["evidence"]:
        try:
            if not isinstance(entry, dict) or entry.get("source_batch_id") != data.source.batch_id:
                raise ValueError("Wrong evidence source")
            value = evidence_value(data, entry)
            if value is None and entry.get("availability") in ("OBSERVED", "CALCULATED"):
                errors.append("UNKNOWN_FIELD_CLAIMED_AS_FACT")
            if entry.get("availability") == "OBSERVED" and entry["file"].startswith("teams/"):
                abbreviation = entry["file"].split("/")[-1].removesuffix(".json")
                team = data.teams[abbreviation]
                parts = entry["field"].split(".")
                if parts[0] == "state" and len(parts) == 2:
                    source_id = next((source for source, keys in SOURCE_FIELDS.values() if parts[1] in keys), "team_state")
                    if state_value(data, team, parts[1], source_id) is None:
                        errors.append("UNOBSERVED_SOURCE_CLAIMED_AS_FACT")
                if parts[0] == "roster" and len(parts) == 3:
                    if player_value(data, team["roster"][int(parts[1])], parts[2]) is None:
                        errors.append("UNOBSERVED_SOURCE_CLAIMED_AS_FACT")
            if entry.get("availability") == "OBSERVED" and entry["file"] == "league.json" and entry["field"].startswith("rules."):
                errors.append("CONFIGURED_RULE_CLAIMED_AS_OBSERVED")
        except (ValueError, KeyError, IndexError, TypeError, OSError):
            errors.append("INVALID_EVIDENCE_REFERENCE")
    if any(type(ref) is not str or ref not in calculation_ids for ref in proposal["calculation_refs"]):
        errors.append("UNKNOWN_CALCULATION_REFERENCE")
    elif proposal["calculation_refs"]:
        if not isinstance(calculation_ids, dict) or any(
            not isinstance(calculation_ids[ref], dict) or calculation_ids[ref].get("availability") != "CALCULATED"
            or calculation_ids[ref].get("value") is None for ref in proposal["calculation_refs"]
        ):
            errors.append("CALCULATION_INPUT_UNAVAILABLE")
    if not proposal["requested_approval"]:
        errors.append("SPECIFIC_APPROVAL_CONTENT_REQUIRED")
    if operation == "TACTIC_CHANGE":
        from .coaching import validate_plan
        plan,snapshot=proposal.get("coaching_plan"),proposal.get("coaching_snapshot")
        if not isinstance(plan,dict) or not isinstance(snapshot,dict):
            errors.append("VERIFIED_NATIVE_COACHING_PLAN_AND_SNAPSHOT_REQUIRED")
        else:
            result=validate_plan(plan,snapshot)
            errors.extend(result["errors"])
            if any(plan.get(k)!=proposal.get(k) for k in ("decision_id","version","career_id","source_batch_id")):
                errors.append("COACHING_PLAN_CONTEXT_MISMATCH")
            team_rows=[t for t in snapshot.get("teams",[]) if t.get("team_id")==plan.get("team_id")]
            if len(team_rows)!=1 or proposal["teams"]!=[team_rows[0].get("abbreviation")]:
                errors.append("COACHING_PLAN_TEAM_MISMATCH")
            elif data.teams[proposal["teams"][0]].get("identity",{}).get("team_id")!=plan.get("team_id"):
                errors.append("COACHING_PLAN_TEAM_ID_MISMATCH")
            missing.extend(result["readiness"])
        if proposal.get("changes"):
            errors.append("LEGACY_TACTICAL_CHANGE_CONTRACT_REVOKED")
    if operation=='COACHING_BATCH_CHANGE':
        from .coaching_batch import validate_batch
        batch=proposal.get('coaching_batch')
        snapshot=proposal.get('coaching_snapshot')
        authoritative=getattr(data,'coaching',{})
        if not isinstance(batch,dict) or not isinstance(snapshot,dict) or not authoritative:
            errors.append('VERIFIED_PUBLISHED_COACHING_BATCH_SOURCE_REQUIRED')
        else:
            result=validate_batch(batch,snapshot)
            errors.extend(result['errors'])
            if any(batch.get(k)!=proposal.get(k) for k in ('decision_id','version','career_id','source_batch_id')):
                errors.append('COACHING_BATCH_CONTEXT_MISMATCH')
            if any(snapshot.get(k)!=authoritative.get(k) for k in ('snapshot_id','context_identity','native_evidence','playbooks','process_binding','defensive_field_catalog')):
                errors.append('COACHING_BATCH_SOURCE_IDENTITY_MISMATCH')
            selected={a.get('team_id') for a in batch.get('actions',[])}|set(batch.get('hold_team_ids',[]))
            advertised={data.teams[t]['identity']['team_id'] for t in proposal['teams']}
            if selected!=advertised:
                errors.append('COACHING_BATCH_TEAMS_MISMATCH')
            observed={t['team_id']:t for t in authoritative.get('teams',[])}
            for row in snapshot.get('teams',[]):
                original=observed.get(row.get('team_id'))
                if not original or any(row.get(k)!=original.get(k) for k in ('coach_identity','values','blocks','roster_signature')):
                    errors.append('COACHING_BATCH_VALUES_NOT_PUBLISHED_SOURCE')
                    break
            # Only load opponents selected by an action. Model-supplied overall
            # records must equal these published observations, not create facts.
            from .data_reader import DataReader
            reader=DataReader(data.root)
            for action in batch.get('actions',[]):
                if action.get('scope')!='VS_OPPONENT_DEFENSE':
                    continue
                try:
                    actual=reader.coaching_opponent(data,action['team_id'],action['opponent_team_id'])
                    rows=[t for t in snapshot['teams'] if t['team_id']==action['team_id']]
                    records=[g for g in rows[0]['gameplans'] if g['opponent_team_id']==action['opponent_team_id']]
                    if len(records)!=1 or records[0].get('overall_defense')!=actual.get('overall_defense'):
                        raise ValueError('Overall record differs from published source')
                    if records[0].get('is_in_use')!=actual.get('is_in_use_raw'):
                        raise ValueError('Inheritance flag differs from published source')
                except (ValueError,KeyError,IndexError,TypeError,OSError):
                    errors.append('COACHING_OVERALL_NOT_PUBLISHED_SOURCE')
            missing.extend('BLOCKED_ACTION:'+a for a in result['blocked_action_ids'])
    if operation == "BUSINESS_CHANGE":
        allowed = {"ticket_courtside", "ticket_lower", "ticket_upper"}
        from .calculations import number
        if not proposal.get("changes") or any(
            not isinstance(change, dict) or change.get("field") not in allowed
            or not number(change.get("value")) or change["value"] < 0 for change in proposal["changes"]
        ):
            errors.append("UNKNOWN_BUSINESS_FIELD_OR_INVALID_VALUE")
        missing.append("价格响应、玩家具体批准及当前执行器验收")
    trade = None
    if operation == "TRADE_PROPOSAL":
        assets = proposal.get("assets", [])
        if not assets or not all(isinstance(item, dict) for item in assets) or len(set(proposal["teams"])) < 2:
            errors.append("TRADE_ASSETS_AND_TWO_TEAMS_REQUIRED")
        else:
            trade = constraints(data, assets)
            errors += trade["errors"]
            missing += trade["missing_data"]
        if proposal.get("legality", "UNKNOWN") == "LEGAL":
            errors.append("V1_CANNOT_CERTIFY_TRADE_LEGALITY")
        if not proposal["calculation_refs"]:
            errors.append("TRADE_CALCULATIONS_REQUIRED")
    if operation == "HISTORICAL_GRAVITY":
        if not proposal.get("reference_sources") or not proposal.get("changes") or not proposal["calculation_refs"]:
            errors.append("HISTORICAL_REFERENCE_CHANGES_AND_CALCULATIONS_REQUIRED")
        missing.append("专项玩家批准与受控属性执行器验收")
    return {"valid": not errors, "errors": sorted(set(errors)), "readiness": "BLOCKED" if errors else
            ("PARTIAL" if proposal["data_gaps"] or missing else "READY"),
            "missing_data": proposal["data_gaps"] + missing, "proposal_status": "PROPOSED",
            "legality": trade["legality"] if trade else "UNKNOWN",
            "execution_authorized": False, "player_approval": "NOT_GRANTED",
            "meaning": "Structure only; no approval, no game write and no CBA certification"}
