"""Deterministic external free-agency planning, with no execution authority.

The only admitted source in this revision is a labelled synthetic snapshot.
P0 has not certified a real offseason source. No JSON field can enable one or
grant approval. Monetary inputs are integer USD; choices use integer scores.
"""
from copy import deepcopy
from datetime import datetime
import re


VERSION = "offseason_planner_v1_1_unverified"
MONEY_MAX = (1 << 31) - 1
PATHS = ("CAP_SPACE", "VERIFIED_BIRD", "VERIFIED_EARLY_BIRD", "VERIFIED_NON_BIRD",
         "VERIFIED_EXCEPTION", "VERIFIED_MINIMUM")
FILES = ("offseason_run.json", "expiring_candidates.json", "free_agency_offers.json",
         "offseason_proposal.json", "OFFSEASON_SUMMARY.md")
DEFAULT_SCORING = {"total_salary": 1, "role": 100000, "strategy": 100000, "home": 100000}


def integer(value, name, low=0, high=MONEY_MAX):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name}: integer required in [{low}, {high}]")
    return value


def identifier(value, name):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        raise ValueError(f"{name}: invalid identifier")
    return value


def season(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{4}", value):
        raise ValueError("Season must be YYYY-YYYY")
    start, end = map(int, value.split("-"))
    if end != start + 1:
        raise ValueError("Season years must be consecutive")
    return start, end


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Source timestamp required")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() is None:
        raise ValueError("Source timestamp must include timezone")


def _validate_input(data):
    for key in ("save_id", "offseason_run_id", "source_batch_id", "policy_id",
                "rules_version", "game_state_version"):
        identifier(data[key], key)
    integer(data["proposal_version"], "proposal_version", 1)
    _, completed = season(data["completed_season"])
    target, _ = season(data["target_season"])
    if target != completed:
        raise ValueError("Target season must follow completed season")
    _timestamp(data["data_updated_at"])
    if data["schema_version"] != 1 or type(data["schema_version"]) is not int:
        raise ValueError("Unsupported snapshot schema")
    teams = data["teams"]
    if not isinstance(teams, list) or len(teams) != 30:
        raise ValueError("Complete, explicit 30-team coverage required")
    ids = [integer(t["team_id"], "team_id") for t in teams]
    if len(set(ids)) != 30:
        raise ValueError("Duplicate team identity")
    candidates = data["candidates"]
    if not isinstance(candidates, list):
        raise ValueError("Candidate list required")
    candidate_ids, entities = set(), set()
    for candidate in candidates:
        cid = identifier(candidate["candidate_id"], "candidate_id")
        identity = candidate["verified_player_identity"]
        entity = identifier(identity["entity_id"], "entity_id")
        if cid in candidate_ids or entity in entities:
            raise ValueError("Duplicate candidate or entity identity; names/slots are not identity")
        candidate_ids.add(cid)
        entities.add(entity)
        if candidate.get("previous_team_id") is not None:
            integer(candidate["previous_team_id"], "previous_team_id")
            if candidate["previous_team_id"] not in ids:
                raise ValueError("Unknown previous team")
    scoring = data.get("scoring", DEFAULT_SCORING)
    if set(scoring) != set(DEFAULT_SCORING):
        raise ValueError("All four explicit scoring weights required")
    for key, value in scoring.items():
        integer(value, f"scoring.{key}", 0, 1000000000)


def _candidate_reason(c, data):
    if not isinstance(c.get("display_name"), str) or not c["display_name"].strip():
        return "DISPLAY_IDENTITY_MISSING"
    identity = c["verified_player_identity"]
    if identity.get("scheme") != "SYNTHETIC" or not identity.get("continuity_ref"):
        return "IDENTITY_CONTINUITY_NOT_VERIFIED"
    if not c.get("roster_provenance"):
        return "ROSTER_PROVENANCE_MISSING"
    if c.get("option_status") not in ("NO_OPTION", "RESOLVED_DECLINED"):
        return "PENDING_OPTION_OR_OPTION_EXERCISED"
    if c.get("extension_status") not in ("NONE", "RESOLVED_EXPIRED"):
        return "EXTENSION_STATUS_UNRESOLVED"
    if c.get("free_agency_status") not in ("VERIFIED_UFA", "VERIFIED_RFA"):
        return "FREE_AGENCY_STATUS_UNKNOWN"
    if c["free_agency_status"] == "VERIFIED_RFA":
        qo = c.get("qualifying_offer", {})
        if qo.get("valid") is not True or not qo.get("evidence_ref"):
            return "RFA_VALID_QO_NOT_VERIFIED"
    if c.get("origin") == "EXPIRING":
        if c.get("previous_team_id") is None:
            return "EXPIRING_HOME_TEAM_UNKNOWN"
        if c.get("expiry_verified_for") != data["completed_season"] or not c.get("expiry_evidence_ref"):
            return "EXPIRY_SEASON_NOT_VERIFIED"
        years = c.get("contract_years_left")
        if type(years) is not int or years not in (0, 1):
            return "CONTRACT_NOT_EXPIRING"
        slots = c.get("next_season_salary_slots")
        if not isinstance(slots, list) or not slots or any(type(v) is not int or v != 0 for v in slots):
            return "NEXT_SEASON_COMMITMENT_OR_UNKNOWN"
    elif c.get("origin") == "EXISTING_FA":
        if not c.get("free_agent_evidence_ref"):
            return "FREE_AGENT_SOURCE_NOT_VERIFIED"
    else:
        return "CANDIDATE_ORIGIN_UNKNOWN"
    return None


def _team_context(team):
    # These are supplied synthetic signing capacities, never cap-minus-payroll proxies.
    if team.get("pending_offers") or team.get("reserved_first_year_salary", 0) != 0:
        raise ValueError("Unresolved prior-run offers/reservations require a new reconciled snapshot")
    result = {"team_id": team["team_id"], "reserved_first_year_salary": 0, "signings": [],
              "remaining_cap_room": team.get("validated_cap_room"),
              "remaining_spending_limit": team.get("signing_spending_limit"),
              "available_slots": team.get("available_slots"),
              "exception_remaining": deepcopy(team.get("exception_budgets", {}))}
    for key in ("payroll_current", "projected_next_year_committed_payroll", "validated_cap_room",
                "signing_spending_limit", "cash", "budget"):
        if team.get(key) is not None:
            integer(team[key], key)
    if result["available_slots"] is not None:
        integer(result["available_slots"], "available_slots", 0, 100)
    for key, value in result["exception_remaining"].items():
        identifier(key, "exception budget id")
        integer(value, "exception budget")
    return result


def _grant(team, cid, path):
    grants = team.get("game_eligibility", {}).get(cid, {})
    grant = grants.get(path)
    if not isinstance(grant, dict) or grant.get("status") != "SYNTHETIC_VERIFIED" or not grant.get("evidence_ref"):
        return None
    return grant


def _legal(offer, candidate, team, ledger, rules):
    path = offer["path"]
    if path not in PATHS:
        return "UNSUPPORTED_SIGNING_PATH"
    grant = _grant(team, candidate["candidate_id"], path)
    if grant is None:
        return "SIGNING_QUALIFICATION_UNKNOWN"
    if path in ("VERIFIED_BIRD", "VERIFIED_EARLY_BIRD", "VERIFIED_NON_BIRD"):
        if team["team_id"] != candidate.get("previous_team_id"):
            return "HOME_RIGHT_ON_WRONG_TEAM"
        if candidate.get("bird_rights_status") != "SYNTHETIC_VERIFIED":
            return "BIRD_RIGHT_NOT_VERIFIED"
    limits = rules.get("candidate_limits", {}).get(candidate["candidate_id"], {}).get(path)
    if not limits or not limits.get("evidence_ref"):
        return "INDIVIDUAL_CONTRACT_LIMITS_UNKNOWN"
    minimum = integer(limits["minimum_salary"], "minimum salary", 1)
    maximum = integer(limits["maximum_salary"], "maximum salary", minimum)
    years = integer(limits["maximum_years"], "maximum years", 1, 6)
    raises = integer(limits["maximum_raise_bps"], "maximum raise bps", 0, 10000)
    salaries = offer["salaries"]
    if not salaries or len(salaries) > years:
        return "CONTRACT_LENGTH_OUT_OF_RANGE"
    for amount in salaries:
        integer(amount, "annual salary", 1)
    # Maxima/minima apply to first year. Each subsequent year's permitted range
    # is computed from first-year salary, not compounded floating point raises.
    if not minimum <= salaries[0] <= maximum:
        return "FIRST_YEAR_SALARY_OUT_OF_RANGE"
    for previous, current in zip(salaries, salaries[1:]):
        if abs(current - previous) * 10000 > salaries[0] * raises:
            return "ANNUAL_CHANGE_OUT_OF_RANGE"
    if ledger["available_slots"] is None or ledger["available_slots"] < 1:
        return "NO_VERIFIED_ROSTER_SLOT"
    if team.get("projected_next_year_committed_payroll") is None:
        return "COMMITTED_PAYROLL_UNKNOWN"
    if ledger["remaining_spending_limit"] is None:
        return "FINANCIAL_SPENDING_LIMIT_UNKNOWN"
    if salaries[0] > ledger["remaining_spending_limit"]:
        return "FINANCIAL_SPENDING_LIMIT_EXCEEDED"
    if path == "CAP_SPACE":
        if ledger["remaining_cap_room"] is None or salaries[0] > ledger["remaining_cap_room"]:
            return "INSUFFICIENT_VERIFIED_CAP_SPACE"
        if team["projected_next_year_committed_payroll"] + ledger["reserved_first_year_salary"] + salaries[0] > rules["cap"]:
            return "CAP_PAYROLL_CEILING_EXCEEDED"
    if path in ("VERIFIED_EXCEPTION", "VERIFIED_MINIMUM"):
        budget_id = grant.get("budget_id")
        if budget_id not in ledger["exception_remaining"] or salaries[0] > ledger["exception_remaining"][budget_id]:
            return "INSUFFICIENT_EXCEPTION_CAPACITY"
    ceiling = team.get("validated_payroll_ceiling")
    if ceiling is not None:
        integer(ceiling, "validated payroll ceiling")
        after = team["projected_next_year_committed_payroll"] + ledger["reserved_first_year_salary"] + salaries[0]
        if after > ceiling:
            return "VALIDATED_PAYROLL_CEILING_EXCEEDED"
    return None


def _make_offer(c, team, rules):
    request = team.get("strategy", {}).get("candidate_offers", {}).get(c["candidate_id"], {})
    if request.get("decline") is True:
        return None, "STRATEGY_DECLINED"
    amount = request.get("first_year_salary", c.get("asking_salary"))
    pricing = "SYNTHETIC_ASKING_SALARY" if c.get("asking_salary") is not None else "HEURISTIC_PROPOSED"
    if "first_year_salary" in request:
        pricing = "STRATEGY_PROPOSED"
    if amount is None:
        anchor = c.get("previous_salary")
        if anchor is None:
            return None, "PRICE_ANCHOR_UNKNOWN"
        integer(anchor, "previous salary", 1)
        multiplier = integer(rules.get("heuristic_salary_bps", 10000), "heuristic bps", 1, 100000)
        amount = anchor * multiplier // 10000
    amount = integer(amount, "first year salary", 1)
    years = integer(request.get("years", 1), "offer years", 1, 6)
    raises = integer(request.get("annual_raise_bps", 0), "offer raise bps", 0, 10000)
    # Round the permitted annual increment down once. Rounding each cumulative
    # target independently could make a later year-to-year increment round up
    # beyond the exact first-year-based limit checked by _legal.
    annual_increment = amount * raises // 10000
    salaries = [integer(amount + annual_increment * i, "salary schedule", 1) for i in range(years)]
    return {"candidate_id": c["candidate_id"], "team_id": team["team_id"],
            "salaries": salaries, "total_salary": sum(salaries), "pricing": pricing,
            "annual_raise_dollars": annual_increment,
            "role_score": integer(request.get("role_score", 0), "role score", 0, 100),
            "strategy_score": integer(request.get("strategy_score", 0), "strategy score", 0, 100),
            "strategy_source": team.get("strategy", {}).get("source", "CONFIGURED_NEUTRAL_BASELINE"),
            "kind": "INITIAL", "path": None}, None


def _choose_path(offer, c, team, ledger, rules):
    reasons = {}
    for path in PATHS:
        attempt = dict(offer, path=path)
        reason = _legal(attempt, c, team, ledger, rules)
        if reason is None:
            limits = rules["candidate_limits"][c["candidate_id"]][path]
            attempt["first_year_interval"] = [limits["minimum_salary"], limits["maximum_salary"]]
            attempt["limits_evidence_ref"] = limits["evidence_ref"]
            attempt["eligibility_evidence_ref"] = _grant(team, c["candidate_id"], path)["evidence_ref"]
            return attempt, None
        reasons[path] = reason
    return None, reasons


def _rank(offer, c, weights):
    home = int(offer["team_id"] == c.get("previous_team_id"))
    home_preference = integer(c.get("home_preference", 0), "home preference", 0, 100)
    score = (weights["total_salary"] * offer["total_salary"]
             + weights["role"] * offer["role_score"]
             + weights["strategy"] * offer["strategy_score"]
             + weights["home"] * home * home_preference)
    return (-score, -offer["total_salary"], offer["team_id"], offer["kind"], offer["path"])


def _reserve(offer, c, team, ledger):
    amount = offer["salaries"][0]
    ledger["reserved_first_year_salary"] += amount
    ledger["remaining_spending_limit"] -= amount
    ledger["available_slots"] -= 1
    if ledger["remaining_cap_room"] is not None:
        ledger["remaining_cap_room"] = max(0, ledger["remaining_cap_room"] - amount)
    if offer["path"] in ("VERIFIED_EXCEPTION", "VERIFIED_MINIMUM"):
        budget = _grant(team, c["candidate_id"], offer["path"])["budget_id"]
        ledger["exception_remaining"][budget] -= amount
    ledger["signings"].append(c["candidate_id"])


def _financials(teams, ledgers, rules):
    rows = []
    for tid, team in sorted(teams.items()):
        ledger = ledgers[tid]
        before = team.get("projected_next_year_committed_payroll")
        after = before + ledger["reserved_first_year_salary"] if before is not None else None
        rows.append({"team_id": tid, "payroll_current": team.get("payroll_current"),
                     "committed_payroll_before": before, "payroll_after_proposed": after,
                     "reserved_first_year_salary": ledger["reserved_first_year_salary"],
                     "available_slots_after": ledger["available_slots"],
                     "cap_room_after": ledger["remaining_cap_room"],
                     "signing_spending_limit_after": ledger["remaining_spending_limit"],
                     "exception_capacity_after": ledger["exception_remaining"],
                     "distances_before": {k: rules[k] - before if before is not None and rules.get(k) is not None else None
                                          for k in ("cap", "tax_line", "apron")},
                     "distances_after": {k: rules[k] - after if after is not None and rules.get(k) is not None else None
                                         for k in ("cap", "tax_line", "apron")},
                     "tax_exposure": "ABOVE_TAX_LINE" if after is not None and rules.get("tax_line") is not None and after > rules["tax_line"] else "UNKNOWN_OR_BELOW_LINE",
                     "tax_amount": None, "cash_impact": None,
                     "cash_observation": team.get("cash"), "budget_observation": team.get("budget"),
                     "signings": ledger["signings"]})
    return rows


def plan(data):
    """Return replayable proposals; never approve, sign, spend cash, or call a game."""
    _validate_input(data)
    frozen = deepcopy(data)
    metadata = {key: frozen[key] for key in (
        "save_id", "completed_season", "target_season", "offseason_run_id", "proposal_version",
        "source_batch_id", "data_updated_at", "policy_id", "rules_version", "game_state_version")}
    purpose = "SIMULATION" if frozen.get("purpose") == "SIMULATION" else "ANALYSIS_ONLY"
    metadata.update(planner_version=VERSION, purpose=purpose, status="BLOCKED",
                    approval_status="NOT_APPROVED", executable_operation_ready=False,
                    source_freshness="NOT_LIVE_VERIFIED", blockers=[])
    metadata["idempotency_key"] = [metadata[k] for k in (
        "save_id", "completed_season", "offseason_run_id", "proposal_version")]
    result = {"offseason_run.json": metadata, "expiring_candidates.json": {"eligible": [], "excluded": []},
              "free_agency_offers.json": {"offers": [], "rejections": [], "home_counters": []},
              "offseason_proposal.json": {"status": "PROPOSED", "purpose": purpose,
                  "decision_id": frozen["offseason_run_id"], "version": frozen["proposal_version"],
                  "source": deepcopy(metadata), "allocations": [], "unsigned": [], "teams": [],
                  "executable_operation_ready": False, "approval_status": "NOT_APPROVED"}}
    # Hard admission gate: self-authored VERIFIED booleans cannot turn real game
    # facts into an accepted source. A certified adapter must be implemented after P0.
    if frozen.get("purpose") != "SIMULATION" or frozen.get("source_profile") != "SYNTHETIC_OFFSEASON_V1":
        metadata["blockers"].append("REAL_OFFSEASON_SOURCE_NOT_IMPLEMENTED")
    if frozen.get("synthetic") is not True:
        metadata["blockers"].append("SYNTHETIC_SOURCE_LABEL_REQUIRED")
    if frozen.get("game_phase") != "SYNTHETIC_OFFSEASON_FROZEN":
        metadata["blockers"].append("OFFSEASON_SAFE_GATE_NOT_FOUND")
    if frozen.get("native_ai_control_status") != "SYNTHETIC_CONTAINED":
        metadata["blockers"].append("NATIVE_AI_SIGNING_NOT_CONTAINED")
    rules = frozen.get("season_rules", {}).get(frozen["target_season"])
    if not rules or rules.get("status") != "SYNTHETIC_VERIFIED" or not rules.get("evidence_ref"):
        metadata["blockers"].append("TARGET_SEASON_RULES_UNVERIFIED")
    if metadata["blockers"]:
        result["offseason_proposal.json"]["status"] = "BLOCKED"
        result["offseason_proposal.json"]["source"] = deepcopy(metadata)
        return _summary(result)
    for key in ("cap", "tax_line", "apron"):
        if rules.get(key) is not None:
            integer(rules[key], key, 1)
    if rules.get("cap") is None or rules.get("tax_line") is None:
        raise ValueError("Explicit target-season cap and tax line required")
    teams = {t["team_id"]: t for t in frozen["teams"]}
    ledgers = {tid: _team_context(t) for tid, t in teams.items()}
    candidates, initial = {}, {}
    offer_log = result["free_agency_offers.json"]
    for c in sorted(frozen["candidates"], key=lambda c: c["candidate_id"]):
        reason = _candidate_reason(c, frozen)
        if reason:
            result["expiring_candidates.json"]["excluded"].append({"candidate_id": c["candidate_id"], "reason": reason})
            continue
        cid = c["candidate_id"]
        candidates[cid] = c
        result["expiring_candidates.json"]["eligible"].append(c)
        initial[cid] = []
        for tid, team in sorted(teams.items()):
            offer, reason = _make_offer(c, team, rules)
            if offer:
                offer, reason = _choose_path(offer, c, team, ledgers[tid], rules)
            if offer:
                initial[cid].append(offer)
                offer_log["offers"].append(offer)
            else:
                offer_log["rejections"].append({"candidate_id": cid, "team_id": tid,
                                                 "stage": "INITIAL", "reason": reason})
    # League order is public and independent of JSON input order.
    order = sorted(candidates, key=lambda cid: (-max((o["total_salary"] for o in initial[cid]), default=0), cid))
    metadata["allocation_order"] = order
    metadata["scoring"] = deepcopy(frozen.get("scoring", DEFAULT_SCORING))
    proposal = result["offseason_proposal.json"]
    for cid in order:
        c = candidates[cid]
        viable = []
        for offer in initial[cid]:
            tid = offer["team_id"]
            current, reason = _choose_path(offer, c, teams[tid], ledgers[tid], rules)
            if current:
                viable.append(current)
            else:
                offer_log["rejections"].append({"candidate_id": cid, "team_id": tid,
                                                 "stage": "AFTER_RESERVATIONS", "reason": reason})
        external = [o for o in viable if o["team_id"] != c.get("previous_team_id")]
        matching = None
        if external and c.get("previous_team_id") in teams:
            best = min(external, key=lambda o: _rank(o, c, metadata["scoring"]))
            home_id = c["previous_team_id"]
            strategy = teams[home_id].get("strategy", {}).get("candidate_offers", {}).get(cid, {})
            counter = dict(best, team_id=home_id, kind="HOME_FINAL_COUNTER",
                           role_score=integer(strategy.get("role_score", 0), "home role", 0, 100),
                           strategy_score=integer(strategy.get("strategy_score", 0), "home strategy", 0, 100),
                           strategy_source=teams[home_id].get("strategy", {}).get("source", "CONFIGURED_NEUTRAL_BASELINE"))
            if strategy.get("decline") is True:
                counter, reason = None, "STRATEGY_DECLINED"
            else:
                counter, reason = _choose_path(counter, c, teams[home_id], ledgers[home_id], rules)
            offer_log["home_counters"].append({"candidate_id": cid, "matched_offer": best,
                                               "offer": counter, "rejection": reason})
            if counter:
                viable.append(counter)
                qo = c.get("qualifying_offer", {})
                if c["free_agency_status"] == "VERIFIED_RFA" and qo.get("matching_right") is True and qo.get("matching_right_evidence_ref"):
                    matching = counter
        if not viable:
            proposal["unsigned"].append({"candidate_id": cid, "status": "UNSIGNED", "reason": "NO_LEGAL_OFFER_IN_SIMULATION"})
            continue
        preferred = min(viable, key=lambda o: _rank(o, c, metadata["scoring"]))
        # Matching substitutes the selected outside contract only. It must not
        # replace a home contract the player already prefers (which may have
        # better terms than the home team's final matching counter).
        match_applied = matching is not None and preferred["team_id"] != c.get("previous_team_id")
        winner = matching if match_applied else preferred
        tid = winner["team_id"]
        _reserve(winner, c, teams[tid], ledgers[tid])
        proposal["allocations"].append(dict(winner,
            action_id=f"sign_{cid}", verified_player_identity=deepcopy(c["verified_player_identity"]),
            previous_team_id=c.get("previous_team_id"),
            selection="RFA_CONFIRMED_MATCH_SIMULATED" if match_applied else "DETERMINISTIC_PLAYER_CHOICE",
            matched_external_team_id=preferred["team_id"] if match_applied else None,
            score=-_rank(winner, c, metadata["scoring"])[0],
            calculation_ref=f"{frozen['offseason_run_id']}.{cid}.integer_allocation",
            candidate_state_version=frozen["game_state_version"]))
    proposal["teams"] = _financials(teams, ledgers, rules)
    metadata["status"] = "AWAITING_PLAYER_REVIEW_SIMULATION_ONLY"
    metadata["coverage"] = {"teams": 30, "input_candidates": len(frozen["candidates"]),
                            "eligible": len(candidates),
                            "free_agent_pool": frozen.get("free_agent_pool_coverage", "UNKNOWN")}
    metadata["state_trace"] = ["PLAYER_TRIGGERED_SIMULATION", "SYNTHETIC_PHASE_GUARD_CHECKED",
        "EXPIRING_POOL_LOCKED", "OFFERS_GENERATED", "LEGALITY_SIMULATED", "HOME_COUNTER_OFFERED",
        "ALLOCATED", "PROPOSED", "AWAITING_PLAYER_REVIEW_SIMULATION_ONLY"]
    proposal["source"] = deepcopy(metadata)
    return _summary(result)


def _summary(result):
    run = result["offseason_run.json"]
    p = result["offseason_proposal.json"]
    rows = ["# 休赛期集中竞价：离线规划", "", f"状态：{run['status']}",
            f"存档/赛季/运行：{run['save_id']} / {run['completed_season']} → {run['target_season']} / {run['offseason_run_id']}",
            "", "当前仅准入 SYNTHETIC 合成数据；真实来源输入会被阻止。未认证原生签约控制或游戏写回。",
            "方案状态 PROPOSED，不构成玩家批准；不能交给游戏执行。",
            "", "阻塞：" + (", ".join(run["blockers"]) or "真实游戏准入仍未实现，当前只允许合成模拟"),
            "", "## 分配", "", "| 候选 | 球队 | 逐年美元 | 路径 | 选择 |", "| --- | --- | --- | --- | --- |"]
    for a in p["allocations"]:
        rows.append(f"| {a['candidate_id']} | {a['team_id']} | {a['salaries']} | {a['path']} | {a['selection']} |")
    rows.extend(["", "## 球队财务", "", "| 球队 | 目标季原承诺 | 建议后 | 距工资帽 | 距税线 | 距 apron |", "| --- | --- | --- | --- | --- | --- |"])
    for team in p["teams"]:
        d = team["distances_after"]
        rows.append(f"| {team['team_id']} | {team['committed_payroll_before']} | {team['payroll_after_proposed']} | {d['cap']} | {d['tax_line']} | {d['apron']} |")
    rows.extend(["", "税额与 cash 影响为 UNKNOWN；不重复扣税，不修改资金。",
                 "中性评分和策略输入属于配置/提议，不表示已有 GM 确认偏好。",
                 "同价 UFA 保留择队；RFA 只有合成夹具中的有效 QO 及匹配权才触发模拟匹配。",
                 "", f"未签候选：{[u['candidate_id'] for u in p['unsigned']]}",
                 f"排除记录：{result['expiring_candidates.json']['excluded']}"])
    result["OFFSEASON_SUMMARY.md"] = "\n".join(rows) + "\n"
    return result


def validate_proposal(data, actual, current_context=None):
    """Replay frozen inputs and check the independent caller-supplied context.

    This is proposal consistency, not a live audit, approval, or a game executor.
    """
    expected = plan(data)
    errors = [f"ARTIFACT_MISMATCH:{name}" for name in FILES if actual.get(name) != expected[name]]
    if current_context is None:
        errors.append("CURRENT_CONTEXT_REQUIRED")
    else:
        for key in ("save_id", "completed_season", "target_season", "source_batch_id",
                    "data_updated_at", "game_state_version", "policy_id", "rules_version",
                    "game_phase", "native_ai_control_status"):
            if current_context.get(key) != data.get(key):
                errors.append(f"SOURCE_STALE:{key}")
    if expected["offseason_run.json"]["blockers"]:
        errors.extend(expected["offseason_run.json"]["blockers"])
    return {"status": "BLOCKED" if errors else "SIMULATION_CONSISTENT",
            "errors": errors, "executable_operation_ready": False,
            "approval_status": "NOT_APPROVED", "live_freshness_verified": False}
