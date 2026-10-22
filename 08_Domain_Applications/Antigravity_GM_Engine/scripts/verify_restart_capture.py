"""Verify a real process restart, audited recapture, and cache reuse against a preserved baseline."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from snapshot_integrity import file_sha256, snapshot_digest, write_json_atomic


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def connect(path):
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def rows(connection, table, keys, excluded, snapshot=None):
    query = f"SELECT * FROM {table}"
    fetched = connection.execute(query + " WHERE snapshot_id=?", (snapshot,)).fetchall() if snapshot else connection.execute(query).fetchall()
    result = {}
    for row in fetched:
        key = tuple(row[column] for column in keys)
        if key in result:
            raise RuntimeError(f"Duplicate comparison identity in {table}: {key}")
        result[key] = {column: row[column] for column in row.keys() if column not in excluded}
    return result


def compare(left, right):
    added, removed = set(right) - set(left), set(left) - set(right)
    differences, field_counts = [], {}
    changed_rows = 0
    for key in sorted(set(left) & set(right), key=repr):
        changed = {field: [left[key].get(field), right[key].get(field)]
                   for field in set(left[key]) | set(right[key]) if left[key].get(field) != right[key].get(field)}
        if changed:
            changed_rows += 1
            for field in changed:
                field_counts[field] = field_counts.get(field, 0) + 1
            if len(differences) < 12:
                differences.append({"key": key, "fields": changed})
    return {"equal": not added and not removed and not changed_rows,
            "before_count": len(left), "after_count": len(right),
            "added_count": len(added), "removed_count": len(removed),
            "changed_rows": changed_rows, "changed_field_counts": field_counts,
            "examples": differences, "added_examples": sorted(added, key=repr)[:12],
            "removed_examples": sorted(removed, key=repr)[:12]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.save_id):
        raise ValueError("Invalid save ID")
    save = ROOT / "database" / "saves" / args.save_id
    validation = save / "validation"
    baseline = validation / "pre_restart"
    evidence = load(baseline / "baseline_evidence.json")
    before_id = evidence["snapshot_id"]
    prefix = before_id.rsplit("PRE_RESTART", 1)[0]
    after_id, repeat_id = prefix + "POST_RESTART", prefix + "POST_RESTART_REPEAT"
    snapshots = [(baseline, before_id, baseline / "player_pool.sqlite"),
                 (save / "snapshots", after_id, validation / "post_restart_player_pool.sqlite"),
                 (save / "snapshots", repeat_id, save / "player_pool.sqlite")]
    connections = [connect(baseline / "league_state.sqlite"), connect(save / "league_state.sqlite"),
                   connect(baseline / "player_pool.sqlite"), connect(validation / "post_restart_player_pool.sqlite"),
                   connect(save / "player_pool.sqlite")]
    checks, manifests, audits = {}, [], []
    comparisons = {}
    try:
        for index, (directory, snapshot, pool_path) in enumerate(snapshots):
            manifest_path = directory / f"ingest_manifest_{snapshot}.json"
            manifest = load(manifest_path)
            audit = load(directory / f"ai_sampling_audit_{snapshot}.json")
            manifests.append(manifest)
            audits.append(audit)
            connection = connections[0 if index == 0 else 1]
            checks[f"batch_{index}_audited_and_bound"] = (
                manifest["status"] == "INGEST_SUCCESS" and audit["verdict"] == "PASS_VERIFIED"
                and bool(audit["checks"]) and all(audit["checks"].values())
                and file_sha256(str(manifest_path)) == audit["manifest_binding"]["manifest_sha256"]
                and snapshot_digest(connection, snapshot) == audit["database_digest_sha256"]
                and file_sha256(str(pool_path)) == audit["player_pool_sha256"])
            # Historical captures may include a separately generated GM artifact.
            # A data-only restart verification must not require GM decisions.
            legacy_gm_path = directory / f"gm_decision_manifest_{snapshot}.json"
            if index and legacy_gm_path.is_file():
                gm = load(legacy_gm_path)
                checks[f"batch_{index}_gm_uses_audited_snapshot"] = (
                    gm["snapshot_id"] == snapshot
                    and gm["audit_prerequisite"]["verdict"] == "PASS_VERIFIED"
                    and gm["execution_policy"].startswith("HUMAN_APPROVAL_REQUIRED"))
        before_pid = evidence["before_pid"]
        first, repeated = manifests[1]["calibration"], manifests[2]["calibration"]
        checks["new_process_detected"] = first["pid"] != before_pid
        checks["old_pid_cache_invalidated"] = first.get("process_changed") is True and first.get("previous_pid") == before_pid
        checks["new_pid_cache_reused"] = repeated["pid"] == first["pid"] and repeated.get("process_changed") is False
        checks["all_calibrations_healthy"] = all(manifest["calibration"]["status"] == "HEALTHY" for manifest in manifests)
        definitions = [
            ("teams", "team_monthly_stats", ("team_id",), {"id", "snapshot_id"}),
            ("rosters", "player_monthly_stats", ("team_id", "player_name", "face_id"), {"id", "snapshot_id", "player_id"}),
            ("staff_identity", "staff_pool_observations", ("staff_slot",), {"snapshot_id", "raw_struct", "memory_address", "raw_team_id"}),
        ]
        for name, table, keys, excluded in definitions:
            before = rows(connections[0], table, keys, excluded, before_id)
            after = rows(connections[1], table, keys, excluded, after_id)
            repeat = rows(connections[1], table, keys, excluded, repeat_id)
            comparisons[name] = {"restart": compare(before, after), "repeat": compare(after, repeat)}
        pools = [rows(conn, "player_pool", ("slot_id",), {"raw_struct", "memory_addr"}) for conn in connections[2:]]
        comparisons["player_pool_decoded_fields"] = {"restart": compare(pools[0], pools[1]), "repeat": compare(pools[1], pools[2])}
        for name, comparison in comparisons.items():
            checks[f"{name}_unchanged_across_restart"] = comparison["restart"]["equal"]
            checks[f"{name}_stable_on_repeat"] = comparison["repeat"]["equal"]
        # Raw staff team IDs are unverified observations, not accepted ownership.
        comparisons["unverified_staff_raw_team_ids"] = compare(
            rows(connections[0], "staff_pool_observations", ("staff_slot",), {"snapshot_id", "raw_struct", "memory_address", "first_name", "last_name", "team_mapping_status"}, before_id),
            rows(connections[1], "staff_pool_observations", ("staff_slot",), {"snapshot_id", "raw_struct", "memory_address", "first_name", "last_name", "team_mapping_status"}, after_id))
    finally:
        for connection in connections:
            connection.close()
    old_map = load(baseline / "runtime_memory_map.json")
    new_map = load(validation / "post_restart_runtime_map.json")
    checks["preserved_maps_match_verified_pids"] = old_map["pid"] == before_pid and new_map["pid"] == first["pid"]
    process = load(validation / "game_process_after_restart.json")
    checks["observed_new_process_matches_capture"] = process["Id"] == first["pid"]
    addresses = {}
    for section, key in (("teams", "pacers_base"), ("player_pool", "base_addr"), ("staff_pool", "base_addr"), ("active_player", "current_addr")):
        left, right = old_map[section][key], new_map[section][key]
        addresses[section] = {"before": left, "after": right, "changed": left != right}
    checks["actual_heap_address_change_observed"] = any(item["changed"] for item in addresses.values())
    rescan = load(validation / "forced_rescan_validation.json")
    checks["all_current_pool_blobs_match_new_process"] = rescan["pid"] == first["pid"] and rescan["passed"] and rescan["checks"]["all_database_player_blobs_match_live"] is True
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "save_id": args.save_id,
        "before_pid": before_pid, "after_pid": first["pid"], "verified_real_restarts": 1,
        "after_process_start_time": process["StartTime"],
        "checks": checks, "real_restart_verified": all(checks.values()),
        "calibration_ms": {"first_new_process_scan": first["elapsed_ms"], "new_cache_reuse": repeated["elapsed_ms"]},
        "audit_check_counts": [len(audit["checks"]) for audit in audits],
        "addresses": addresses, "comparisons": comparisons,
        "scope": "Decoded captured fields compared; runtime BLOBs not assumed identical across processes; staff ownership remains unverified.",
    }
    output = validation / "real_restart_verification.json"
    write_json_atomic(str(output), report)
    print(json.dumps({key: value for key, value in report.items() if key not in ("comparisons", "scope")}, ensure_ascii=True, indent=2))
    print(f"Report: {output}")
    if not report["real_restart_verified"]:
        raise RuntimeError("Restart evidence contains failures or unexplained business-field differences")


if __name__ == "__main__":
    main()
