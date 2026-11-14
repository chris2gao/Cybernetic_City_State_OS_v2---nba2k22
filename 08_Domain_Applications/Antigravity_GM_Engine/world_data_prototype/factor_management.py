"""Join independently decoded management events to native transaction and contract observations."""
from contextlib import closing

from engine import connect
from factor_readback import _bound_report, _source_units
from factor_settlement import _analysis_row, _proof_context, _read_clock, _subject


MANAGEMENT_CAPTURE_FAMILIES = ("game-mode", "player-details", "news")
_KINDS = {"CONTRACT": ("NATIVE_CONTRACT_SIGNED", "NATIVE_CONTRACT_EXTENDED"),
          "TRADE_DRAFT": ("NATIVE_PLAYER_TRADE_SETTLED",)}
_TERMS = ("original_contract_years_raw", "years_left_on_contract_raw", "contract_option_raw", "no_trade_raw",
          "extension_length_raw", "extension_option_raw", "extension_no_trade_raw", "contract_type_raw",
          "contract_year_1_raw", "contract_year_2_raw", "contract_year_3_raw", "contract_year_4_raw",
          "contract_year_5_raw", "contract_year_6_raw")


def _matched_transactions(conn, unit, signature):
    items = signature["items"]
    if (type(signature["type_code"]) is not int or not 0 <= signature["type_code"] <= 15
            or type(signature["date_word"]) is not int or not 0 <= signature["date_word"] <= 0xffffffff
            or not 1 <= len(items) <= 39
            or any(len(item) != 2 or type(item[0]) is not int or not 0 <= item[0] <= 7
                   or type(item[1]) is not int or not 0 <= item[1] <= 0xffffffff for item in items)):
        raise ValueError("MANAGEMENT_TRANSACTION_SIGNATURE_INVALID")
    matches = []
    candidates = conn.execute("""
        SELECT native_transaction_id FROM native_transaction_observations
        WHERE unit_id=? AND native_type_code=? AND date_word_raw=? AND data_count_raw=?
          AND active_prefix_status='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE'
    """, (unit, signature["type_code"], signature["date_word"], len(items)))
    for (transaction_id,) in candidates:
        actual = conn.execute("""
            SELECT source_item_index,native_type_code,integer_word_raw
            FROM native_transaction_item_observations
            WHERE unit_id=? AND native_transaction_id=? AND source_item_index<? ORDER BY source_item_index
        """, (unit, transaction_id, len(items)))
        if [tuple(row) for row in actual] == [(index, *item) for index, item in enumerate(items)]:
            matches.append(transaction_id)
    return matches


def _snapshot(host, directory, report_sha, binding, plan, uid, team, signature):
    report = _bound_report(host, directory, report_sha, plan, binding)
    with closing(connect(host.database, True)) as conn:
        units = _source_units(conn, report, binding["season_id"], MANAGEMENT_CAPTURE_FAMILIES)
        clock = _read_clock(conn, units["game-mode"])
        row = _subject(conn, units["player-details"], "player_contract_observations",
                       (*_TERMS, "native_contract_team_id_raw", "contract_team_status"), uid, team)
        if (row["native_contract_team_id_raw"] != team
                or row["contract_team_status"] != "NATIVE_CORE_TEAM_POINTER_OBSERVED"):
            raise ValueError("MANAGEMENT_CONTRACT_OWNER_AND_ROSTER_DISAGREE")
        matches = _matched_transactions(conn, units["news"], signature)
    return {"clock": clock, "player_id": row["player_id"], "units": units,
            "metrics": {key: row[key] for key in _TERMS}, "transactions": matches,
            "sources": {"player-details": {"unit_id": units["player-details"], "player_source_id": row["player_source_id"]},
                        "news": {"unit_id": units["news"], "matching_transaction_ids": matches}}}


def capture_management_event(host, factor, *, proof_raw, approved_proof_sha256, before_directory, after_directory,
                             before_binding, after_binding):
    """Require a new, exact raw transaction match and independently accepted actor/date semantics."""
    proof, setter_verified = _proof_context(factor, proof_raw, approved_proof_sha256, before_binding, after_binding,
                                           schema="nba2k22.vae.management_settlement.v1", kinds=_KINDS)
    plan = {"worldline_id": proof["binding"]["worldline_id"]}
    evidence = proof["settlement"]
    trade = proof["protocol"] == "TRADE_DRAFT"
    before_team, after_team = proof["team_id"], evidence["after_team_id"]
    if type(after_team) is not int or not 0 <= after_team <= 29 or (before_team != after_team) != trade:
        raise ValueError("MANAGEMENT_OWNER_TRANSITION_SCOPE_MISMATCH")
    endpoints = proof["endpoints"]
    allowed = {*_TERMS, "ownership_moved"} if trade else set(_TERMS)
    if not endpoints or len(endpoints) != len(set(endpoints)) or not set(endpoints) <= allowed:
        raise ValueError("MANAGEMENT_RAW_ENDPOINTS_REQUIRED")
    signature = evidence["transaction_signature"]
    uid = proof["uid"]
    before = _snapshot(host, before_directory, proof["before_report_sha256"], before_binding, plan, uid, before_team, signature)
    after = _snapshot(host, after_directory, proof["after_report_sha256"], after_binding, plan, uid, after_team, signature)
    if before["transactions"] or after["transactions"] != [evidence["native_transaction_id"]]:
        raise ValueError("MANAGEMENT_TRANSACTION_NOT_NEW_UNIQUE_AND_EXACT")
    if not trade and before["metrics"] == after["metrics"]:
        raise ValueError("MANAGEMENT_CONTRACT_TERMS_CHANGE_NOT_OBSERVED")
    if trade:
        before["metrics"]["ownership_moved"] = 0
        after["metrics"]["ownership_moved"] = 1
    for phase in (before, after):
        phase["metrics"] = {key: phase["metrics"][key] for key in endpoints}
    row = _analysis_row(proof, setter_verified, before, after, approved_proof_sha256)
    return dict(row, before_team_id=before_team, after_team_id=after_team,
                native_transaction_id=evidence["native_transaction_id"])
