"""Join accepted training/progression settlement evidence to bound WorldData snapshots."""
from contextlib import closing
from datetime import date
import hashlib
import json

from engine import connect
from factor_readback import _bound_report, _source_units
from player_skill_codec import PROFILE


DEVELOPMENT_CAPTURE_FAMILIES = ("game-mode", "player-skills", "player-state")
_SETTLEMENT_KINDS = {"TRAINING": ("NATIVE_TRAINING_SETTLED",), "PROGRESSION": ("NATIVE_PROGRESSION_SETTLED",)}
_HEALTH_FIELDS = frozenset({"fatigue_raw", "energy_raw", "wear_and_tear_raw", "injury1_type_raw", "injury2_type_raw"})
_ATTR_FIELDS = frozenset(PROFILE["attributes"])


def _clock(day, minutes):
    if type(minutes) is not int or not 0 <= minutes < 1440:
        raise ValueError("DEVELOPMENT_NATIVE_MINUTES_INVALID")
    return date.fromisoformat(day), minutes


def _sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _subject(conn, unit, table, columns, uid, team):
    projection = ", ".join("s." + column for column in columns)
    rows = conn.execute(f"""
        SELECT n.player_id, n.player_source_id, {projection}
        FROM native_player_sources n
        JOIN {table} s ON s.source_player_id=n.player_source_id AND s.unit_id=n.unit_id
        WHERE n.unit_id=? AND n.native_unique_id_raw=? AND n.native_team_id=?
          AND n.current_core_roster_status='CURRENT_CORE_ROSTER' AND n.player_id IS NOT NULL
          AND n.player_id=s.player_id
    """, (unit, uid, team)).fetchall()
    if len(rows) != 1:
        raise ValueError("DEVELOPMENT_PLAYER_IDENTITY_NOT_UNIQUE")
    return rows[0]


def _read_clock(conn, unit):
    mode = conn.execute("""
        SELECT today_native_iso_date,today_minutes_since_midnight_raw,mode_label,league_label
        FROM game_mode_observations WHERE unit_id=?
    """, (unit,)).fetchall()
    if len(mode) != 1 or tuple(mode[0])[2:] != ("FRANCHISE", "NBA"):
        raise ValueError("EVENT_GAME_MODE_NOT_OBSERVED")
    return _clock(*tuple(mode[0])[:2])


def _snapshot(host, directory, report_sha, binding, plan, uid, team, endpoints):
    report = _bound_report(host, directory, report_sha, plan, binding)
    families = DEVELOPMENT_CAPTURE_FAMILIES
    with closing(connect(host.database, True)) as conn:
        units = _source_units(conn, report, binding["season_id"], families)
        clock = _read_clock(conn, units["game-mode"])
        measures, sources, identities = {}, {}, set()
        for group, family, table in (("skill", "player-skills", "player_attribute_snapshots"),
                                      ("health", "player-state", "player_health_observations")):
            columns = [name for prefix, name in endpoints if prefix == group]
            # Keep both source families identity-bound even if one is used only as context.
            fields = columns or (["stamina_raw"] if group == "skill" else ["wear_and_tear_raw"])
            row = _subject(conn, units[family], table, fields, uid, team)
            identities.add(row["player_id"])
            sources[family] = {"unit_id": units[family], "player_source_id": row["player_source_id"]}
            for name in columns:
                measures[f"{group}.{name}"] = row[name]
        if len(identities) != 1:
            raise ValueError("DEVELOPMENT_CAPTURE_PLAYER_CHANGED_BETWEEN_FAMILIES")
        player_id, = identities
    return {"clock": clock, "player_id": player_id, "metrics": measures, "sources": sources, "units": units}


def _proof_context(factor, proof_raw, approved_proof_sha256, before_binding, after_binding, *, schema, kinds):
    if hashlib.sha256(proof_raw).hexdigest() != approved_proof_sha256:
        raise PermissionError("EVENT_SETTLEMENT_PROOF_PIN_MISMATCH")
    proof = json.loads(proof_raw)
    protocol = proof["protocol"]
    evidence = proof["settlement"]
    treatment = proof["treatment"]
    scope_keys = ("save_id", "worldline_id", "loaded_filename", "binding_sha256")
    scope = {key: before_binding[key] for key in scope_keys}
    if (proof["schema"] != schema or proof["mode"] != "LIVE"
            or protocol not in kinds or evidence["kind"] not in kinds[protocol]
            or proof["factor_id"] != factor.factor_id or protocol != factor.protocol
            or evidence["verified"] is not True or not evidence["independent_review_ref"]
            or not evidence["event_id"] or not evidence["source_unit"]
            or not _sha(evidence["source_sha256"]) or not _sha(proof["origin_sha256"])
            or proof["binding"] != scope or any(after_binding[key] != scope[key] for key in scope_keys)
            or proof["before_season_id"] != before_binding["season_id"] or proof["after_season_id"] != after_binding["season_id"]
            or (protocol != "PROGRESSION" and before_binding["season_id"] != after_binding["season_id"])):
        raise ValueError("EVENT_SETTLEMENT_PROOF_SCOPE_MISMATCH")
    epoch_keys = ("pid", "creation_filetime", "module_base", "module_size", "pe_timestamp")
    if any(before_binding["epoch"][key] != after_binding["epoch"][key] for key in epoch_keys):
        raise ValueError("EVENT_PROCESS_EPOCH_CHANGED")
    uid, team = proof["uid"], proof["team_id"]
    if (type(uid) is not int or not 1 <= uid <= 65535 or type(team) is not int or not 0 <= team <= 29
            or proof["arm"] not in ("H", "L", "C") or not proof["factor_id"]):
        raise ValueError("EVENT_EXACT_FACTOR_SUBJECT_REQUIRED")
    if treatment["status"] not in ("APPLIED_VERIFIED", "CONTROL_UNCHANGED", "SETTER_UNVERIFIED"):
        raise ValueError("EVENT_TREATMENT_STATUS_INVALID")
    expected_treatment = "CONTROL_UNCHANGED" if proof["arm"] == "C" else "APPLIED_VERIFIED"
    setter_verified = treatment["status"] == expected_treatment
    if setter_verified and (not _sha(treatment["source_sha256"]) or treatment["requested"] is None
                            or treatment["observed"] != treatment["requested"]):
        raise ValueError("EVENT_TREATMENT_RECEIPT_INCOMPLETE")
    before_sha, after_sha = proof["before_report_sha256"], proof["after_report_sha256"]
    if not _sha(before_sha) or not _sha(after_sha) or before_sha == after_sha:
        raise ValueError("EVENT_REQUIRES_DISTINCT_REPORTS")
    return proof, setter_verified


def _analysis_row(proof, setter_verified, before, after, approved_proof_sha256):
    evidence, treatment = proof["settlement"], proof["treatment"]
    if set(before["units"].values()) & set(after["units"].values()) or before["player_id"] != after["player_id"]:
        raise ValueError("EVENT_BEFORE_AFTER_IDENTITY_OR_SOURCE_REUSED")
    if evidence["source_unit"] in {*before["units"].values(), *after["units"].values()}:
        raise ValueError("EVENT_SETTLEMENT_REQUIRES_INDEPENDENT_EVENT_SOURCE")
    if not before["clock"] < _clock(evidence["event_date"], evidence["minutes"]) <= after["clock"]:
        raise ValueError("EVENT_SETTLEMENT_OUTSIDE_OBSERVED_INTERVAL")
    return {"mode": "LIVE", "factor_id": proof["factor_id"], "protocol": proof["protocol"],
            "worldline_id": proof["binding"]["worldline_id"],
            "arm": proof["arm"], "origin_sha256": proof["origin_sha256"], "event_id": evidence["event_id"],
            "event_date": evidence["event_date"], "source_unit": evidence["source_unit"], "opportunity": True,
            "setter_verified": setter_verified, "requested_value": treatment["requested"], "observed_value": treatment["observed"],
            "before_identity": before["player_id"], "after_identity": after["player_id"],
            "uid": proof["uid"], "team_id": proof["team_id"],
            "before_source": proof["before_report_sha256"], "after_source": proof["after_report_sha256"],
            "before": before["metrics"], "after": after["metrics"],
            "before_source_units": before["sources"], "after_source_units": after["sources"],
            "before_game_time": {"date": before["clock"][0].isoformat(), "minutes": before["clock"][1],
                                 "unit_id": before["units"]["game-mode"]},
            "after_game_time": {"date": after["clock"][0].isoformat(), "minutes": after["clock"][1],
                                "unit_id": after["units"]["game-mode"]},
            "settlement_proof_sha256": approved_proof_sha256, "settlement_source_sha256": evidence["source_sha256"]}


def capture_development_event(host, factor, *, proof_raw, approved_proof_sha256, before_directory, after_directory,
                              before_binding, after_binding):
    """Build an analysis row using separately accepted native settlement and treatment evidence."""
    proof, setter_verified = _proof_context(factor, proof_raw, approved_proof_sha256, before_binding, after_binding,
                                           schema="nba2k22.vae.development_settlement.v1", kinds=_SETTLEMENT_KINDS)
    endpoints = [tuple(key.split(".", 1)) for key in proof["endpoints"]]
    if (not endpoints or len(endpoints) != len(set(endpoints))
            or any(len(parts) != 2 or not ((parts[0] == "skill" and parts[1] in _ATTR_FIELDS)
                                         or (parts[0] == "health" and parts[1] in _HEALTH_FIELDS)) for parts in endpoints)):
        raise ValueError("DEVELOPMENT_PUBLIC_ENDPOINTS_REQUIRED")
    plan = {"worldline_id": proof["binding"]["worldline_id"]}
    uid, team = proof["uid"], proof["team_id"]
    before = _snapshot(host, before_directory, proof["before_report_sha256"], before_binding, plan, uid, team, endpoints)
    after = _snapshot(host, after_directory, proof["after_report_sha256"], after_binding, plan, uid, team, endpoints)
    return _analysis_row(proof, setter_verified, before, after, approved_proof_sha256)
