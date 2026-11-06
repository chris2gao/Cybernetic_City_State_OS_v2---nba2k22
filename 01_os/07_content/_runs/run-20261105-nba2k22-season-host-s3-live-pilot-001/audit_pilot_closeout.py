"""Read-only audit of the four Human-triggered S3 calendar rounds."""
import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    receipts = Path(__file__).resolve().parent / "receipts"
    state = read(runtime / "host-state.json")
    baseline = read(runtime / "l2-receipt.json")
    original = read(receipts / "s3-isolation-l0.json")
    assert baseline["status"] == "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE"
    assert digest(args.historical / original["historical_database"]["name"]) == original["historical_database"]["sha256"]
    assert digest(args.historical / "save.json") == original["historical_binding"]["sha256"]
    binding = read(runtime / "world/save.json")
    assert binding["native_save_filename"] == "MyLEAGUE0003"
    assert digest(runtime / "world/save.json") == baseline["binding_sha256"]
    assert digest(runtime / "native-disk-backup/MyLEAGUE0003") == baseline["native_sha256_before"]
    assert state["worldline_id"] == baseline["worldline_id"] == binding["worldline_id"]
    expected_count = baseline["final_games_in_sqlite"]
    expected_date = baseline["game_date"]
    seals = [baseline["sealed"]]
    all_new_ids = set()
    results = []
    for number in range(1, 5):
        cycle = f"cycle-{number:03}"
        suffix = "-reverified" if number == 1 else ""
        name = f"advance-after-{cycle}{suffix}.json"
        actual = runtime / name
        assert actual.read_bytes() == (receipts / name).read_bytes()
        round_result = read(actual)
        assert round_result["after_cycle"] == cycle and round_result["human_trigger"]
        assert round_result["status"] == "VERIFIED_HUMAN_ADVANCE"
        assert round_result["worldline_id"] == binding["worldline_id"] and round_result["epoch"] == baseline["context"]
        assert round_result["native_unchanged_during_host_readback"]
        assert round_result["native_sha256_before_readback"] == round_result["native_sha256_after_readback"]
        assert round_result["final_count_before"] == expected_count and round_result["game_date_before"] == expected_date
        new_ids = set(round_result["native_new_final_ids"])
        assert new_ids and not all_new_ids.intersection(new_ids)
        all_new_ids.update(new_ids)
        readbacks = round_result["readbacks"]
        assert {row["game_id"].rsplit(":", 1)[1] for row in readbacks} == new_ids
        assert len(readbacks) == len(new_ids)
        assert all(row["verified_in_db"] and row["was_simulated"] == 1 and row["score_conservation"] for row in readbacks)
        expected_count += len(new_ids)
        expected_date = round_result["game_date_after"]
        assert round_result["final_count_after"] == round_result["native_final_count"] == expected_count
        report_path = Path(round_result["refresh_report_local"])
        assert digest(report_path) == round_result["refresh_report_sha256"]
        report = read(report_path)
        assert report["status"] == "COMPLETED_REQUESTED_SOURCES" and report["binding_sha256"] == baseline["binding_sha256"]
        assert report["batch_id"] == round_result["refresh_batch_id"] and report["process_epoch"] == baseline["context"]
        sources = report["sources"]
        assert len(sources) == 20 and all(row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED" for row in sources)
        schedule_unit = next(row["unit"]["unit_id"] for row in sources if row["family"] == "schedule")
        assert all(row["unit_id"] == schedule_unit for row in readbacks)
        summary = read(receipts / f"advance-after-{cycle}-sources.json")
        assert summary["raw_report_sha256"] == round_result["refresh_report_sha256"]
        results.append({
            "cycle": cycle, "schedule_date": expected_date, "today": round_result["today"],
            "elapsed_days": round_result["elapsed_days"], "new_finals": len(new_ids),
            "overtime_games": sum(bool(row["overtime_count"]) for row in readbacks),
            "batch": report["batch_id"], "refresh_seconds": summary["wall_seconds"],
            "source_statuses": dict(Counter(row["status"] for row in sources)),
            "reported_source_rows": sum(sum(row.get("counts", {}).values()) for row in sources),
            "plan_digest": seals[-1]["plan_digest"], "receipt": name,
        })
        assert seals[-1]["cycle_id"] == cycle and seals[-1]["executable_intents_count"] == 0
        if number < 4:
            seals.append(round_result["next_seal"])
        else:
            assert "next_seal" not in round_result and "opened" not in round_result
    assert state["current_game_date"] == expected_date and state["active_plan"] is None
    with closing(sqlite3.connect(Path(state["database_file"]).as_uri() + "?mode=ro", uri=True)) as conn:
        sql_finals = conn.execute("SELECT count(DISTINCT game_id) FROM game_state_observations WHERE is_final=1").fetchone()[0]
    assert sql_finals == expected_count
    with closing(sqlite3.connect((runtime / "outbox.sqlite").as_uri() + "?mode=ro", uri=True)) as conn:
        cycles = conn.execute("SELECT cycle_id,status,sealed_digest FROM decision_cycles ORDER BY cycle_id").fetchall()
        intents = conn.execute("SELECT count(*) FROM decision_intents").fetchone()[0]
    assert cycles == [(row["cycle"], "COMPLETED", row["plan_digest"]) for row in results]
    assert intents == 0
    print(json.dumps({
        "status": "VERIFIED_FOUR_HUMAN_CALENDAR_ROUNDS", "rounds": results,
        "final_games": sql_finals, "new_finals": len(all_new_ids), "outbox_intents": intents,
        "host_cursor": {"status": state["status"], "cycle": state["current_cycle_id"]},
        "old_database_and_binding_sha256_match": True, "pilot_disk_backup_sha256_match": True,
        "native_write_path": "NOT_EXERCISED_ZERO_INTENTS",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
