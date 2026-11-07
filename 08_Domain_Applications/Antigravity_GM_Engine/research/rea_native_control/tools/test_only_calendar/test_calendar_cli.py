import json
import struct
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import calendar_cli as cli
from decision_outbox import DecisionOutbox
from role_batches import BatchContext


def plan():
    return {
        "schema": cli.SCHEMA, "test_only": True, "disposable_save": True,
        "event_free_regular_season": True, "build_sha256": cli.BUILD,
        "source_sha256": cli.load(cli.HERE / "capability_manifest.json")["source_sha256"],
        "start": "2021-12-31", "stop_exclusive": "2022-01-01", "season_stop_exclusive": "2022-04-01",
        "today_raw": 0x2b7f0002, "save_id": "test-save", "worldline_id": "test-world",
        "loaded_filename": "MyLEAGUE0005", "authorization_scope": "test-scope",
        "binding_sha256": "1" * 64, "disk_sha256": "2" * 64, "cold_backup_sha256": "3" * 64,
        "epoch": {"pid": 1000, "creation_filetime": 134385176534141007,
                  "module_base": "0x140000000", "module_size": 115056640,
                  "pe_timestamp": 1652287197, "game_season_year": 2022},
        "engine_thread": 42, "engine_thread_evidence": "fixture-frame",
        "observation_ms": 15000,
        "games": [
            {"id": 100, "day": "2021-12-31", "home": 1, "away": 2},
            {"id": 101, "day": "2022-01-01", "home": 2, "away": 3},
        ],
    }


def receipt(frozen):
    header = bytearray(60)
    start = cli.word(cli.civil(frozen["start"]))
    struct.pack_into("<IIIHH", header, 0, start, start, 100, 1, 2)
    struct.pack_into("<BB", header, 22, 1, 1)
    struct.pack_into("<I", header, 56, 0x41000)
    header[44], header[48] = 2, 3
    stats = struct.pack("<IIIIII", 0x10001, 1, 0, 0, 0, 0)
    stats += struct.pack("<IIIIII", 0x10002, 1 | (1 << 17), 0, 0, 0, 0)
    events = [
        {"event": "WILL_DISPATCH_ONCE", "command": 17, "thread": 42, "selected": start},
        {"event": "DISPATCH_RETURN", "status": 0x504521a8, "today": 0x2c010000, "frame_idle": True},
        {"event": "REA_POST_SIM_BOX_UNIT", "part": 0, "total": 1, "pid": 1000, "today_raw": 0x2c010000,
         "games": [{"id": 100, "header_hex": header.hex(), "box_hex": stats.hex()}]},
        {"event": "NEXT_DAY_PENDING", "ids": [101]},
    ]
    return {"evidence_id": "fixture-evidence", "normalized_result": {
        "pid": 1000, "messages_truncated": False, "cleanup_error": None,
        "messages": [{"type": "send", "payload": event} for event in events],
    }}


class CalendarTests(unittest.TestCase):
    def test_worlddata_imports_resolve_to_worlddata(self):
        import live_world
        import readers
        import refresh

        self.assertEqual(Path(readers.__file__).resolve().parent, cli.WORLD)
        self.assertTrue(callable(live_world.read_binding))
        self.assertTrue(callable(refresh._context))

    def test_date_rollover_and_readonly_source(self):
        frozen = plan()
        cli.validate_plan(frozen)
        script = cli.render(frozen, dispatch=False, expires=datetime.now(timezone.utc) + timedelta(minutes=5))
        self.assertIn('"creation_filetime":"134385176534141007"', script)
        self.assertIn('"dispatch":false', script)
        self.assertIn('"stop":738263040', script)
        self.assertIn('today_raw:capture.today.raw', script)
        frozen["engine_thread"] = 0
        frozen["engine_thread_evidence"] = None
        cli.validate_plan(frozen, observe=True)
        with self.assertRaisesRegex(ValueError, "thread"):
            cli.validate_plan(frozen)

    def test_boundary_and_duplicate_ids_refused(self):
        for mutation in (
            {"season_stop_exclusive": "2022-01-01"},
            {"stop_exclusive": "2022-01-08"},
            {"today_raw": 0x2b7f0020},
            {"disposable_save": False},
            {"source_sha256": {}},
            {"games": plan()["games"] * 2},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                cli.validate_plan(plan() | mutation)

    def test_mismatched_scene_and_post_date(self):
        frozen = plan()
        scene = {"epoch": frozen["epoch"], "game_progress": {
            "mode_raw": 1, "period_raw": 29, "today_native_iso_date": frozen["start"],
            "today_minutes_since_midnight_raw": 0,
        }}
        cli.ensure_scene(frozen, scene)
        with self.assertRaises(ValueError):
            cli.ensure_scene(frozen, scene, after=True)
        scene["epoch"] = dict(frozen["epoch"], creation_filetime=2)
        with self.assertRaises(ValueError):
            cli.ensure_scene(frozen, scene)

    def test_valid_receipt_and_corrupt_units(self):
        frozen = plan()
        self.assertEqual(cli.audit_native_result(receipt(frozen), frozen)["final_game_ids"], [100])
        for fault in ("truncated", "date-label", "score", "exception", "missing", "overshoot", "duplicate"):
            raw = receipt(frozen)
            normalized = raw["normalized_result"]
            if fault == "truncated":
                normalized["messages_truncated"] = True
            elif fault == "date-label":
                normalized["messages"][2]["payload"]["today_raw"] = 0x2b7f0000
            elif fault == "score":
                normalized["messages"][2]["payload"]["games"][0]["box_hex"] = "00" * 48
            elif fault == "exception":
                normalized["messages"].append({"type": "send", "payload": {"event": "NATIVE_EXCEPTION_OBSERVED"}})
            elif fault == "missing":
                normalized["messages"].pop(2)
            elif fault == "overshoot":
                normalized["messages"][3]["payload"]["ids"] = []
            else:
                normalized["messages"].insert(0, deepcopy(normalized["messages"][0]))
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                cli.audit_native_result(raw, frozen)

    def test_missing_exact_approval_is_inert(self):
        with patch.object(cli, "invoke") as launch:
            with self.assertRaisesRegex(ValueError, "DISABLED"):
                cli.simulate_to_native_date(SimpleNamespace(execute_once=False), plan())
            launch.assert_not_called()

    def test_approval_digest_scope_and_expiry(self):
        now = datetime.now(timezone.utc)
        frozen = plan()
        grant = {"action": cli.ACTION, "plan_digest": cli.digest(frozen),
                 "authorization_scope": frozen["authorization_scope"], "max_dispatches": 1,
                 "approved_by_operator": True, "human_decision_ref": "fixture",
                 "revoked": False, "valid_from": (now - timedelta(minutes=1)).isoformat(),
                 "expires_at": (now + timedelta(minutes=5)).isoformat()}
        with tempfile.TemporaryDirectory() as path:
            file = Path(path) / "grant.json"
            file.write_bytes(cli.canonical(grant))
            sha = cli.sha_file(file)
            cli.load_approval(frozen, file, sha, now)
            with self.assertRaises(ValueError):
                cli.load_approval(frozen, file, sha, now + timedelta(hours=1))
            with self.assertRaises(ValueError):
                cli.load_approval(dict(frozen, start="2021-12-30"), file, sha, now)
            file.write_bytes(cli.canonical(grant | {"revoked": True}))
            with self.assertRaises(ValueError):
                cli.load_approval(frozen, file, sha, now)
            with self.assertRaises(ValueError):
                cli.load_approval(frozen, file, cli.sha_file(file), now)

    def test_unknown_transport_keeps_durable_claim(self):
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            db = root / "outbox.db"
            DecisionOutbox(db)
            frozen = plan() | {"outbox_db": str(db)}
            approval = root / "approval.json"
            approval.write_bytes(cli.canonical({
                "action": cli.ACTION, "plan_digest": cli.digest(frozen), "authorization_scope": "test-scope",
                "max_dispatches": 1, "approved_by_operator": True, "human_decision_ref": "fixture",
                "revoked": False, "valid_from": (now - timedelta(minutes=1)).isoformat(),
                "expires_at": (now + timedelta(minutes=5)).isoformat(),
            }))
            args = SimpleNamespace(execute_once=True, approval=approval, approved_sha=cli.sha_file(approval), outbox=db)
            with patch.object(cli, "preflight"), patch.object(cli, "invoke", side_effect=OSError("provider disconnected")) as port:
                result = cli.simulate_to_native_date(args, frozen)
                self.assertEqual(result["status"], "UNKNOWN_NO_REPLAY")
                with self.assertRaisesRegex(ValueError, "NO_REPLAY"):
                    cli.simulate_to_native_date(args, frozen)
                port.assert_called_once()
            self.assertEqual(DecisionOutbox.inspect_test_calendar(db, cli.digest(frozen))["status"], "UNKNOWN")

    def test_full_wrapper_verified_and_explicit_zero_dispatch(self):
        for returned in ("RETURNED_WITH_NATIVE_READBACK", "FRAME_GATE_NOT_OBSERVED"):
            with self.subTest(returned=returned), tempfile.TemporaryDirectory() as path:
                root = Path(path)
                db = root / "outbox.db"
                DecisionOutbox(db)
                frozen = plan() | {"outbox_db": str(db)}
                grant = {"human_decision_ref": "fixture",
                         "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}
                args = SimpleNamespace(execute_once=True, approval="fixture", approved_sha="fixture", outbox=db)

                def fixture_port(_args, script, *_scope):
                    program = root / "program.js"
                    program.write_text(script, encoding="utf-8")
                    raw = receipt(frozen)
                    raw["normalized_result"]["source_sha256"] = cli.sha_file(program)
                    if returned == "FRAME_GATE_NOT_OBSERVED":
                        raw["normalized_result"]["messages"] = [{"type": "send", "payload": {"status": returned}}]
                    (root / "evidence.json").write_bytes(cli.canonical(raw))
                    return {"status": returned, "plan_digest": cli.digest(frozen), "runtime_directory": str(root)}

                with patch.object(cli, "load_approval", return_value=grant), patch.object(cli, "preflight") as check, \
                        patch.object(cli, "invoke", side_effect=fixture_port) as port:
                    outcome = cli.simulate_to_native_date(args, frozen)
                    port.assert_called_once()
                    status = "VERIFIED_IN_MEMORY" if returned == "RETURNED_WITH_NATIVE_READBACK" else "NOT_EXECUTED"
                    self.assertEqual(outcome["status"], status)
                    self.assertEqual(check.call_count, 3 if status == "VERIFIED_IN_MEMORY" else 2)
                self.assertEqual(DecisionOutbox.inspect_test_calendar(db, cli.digest(frozen))["status"], status)

    def test_calendar_claim_blocks_setter_and_concurrent_calendars(self):
        with tempfile.TemporaryDirectory() as path:
            db = Path(path) / "outbox.db"
            outbox = DecisionOutbox(db)
            context = BatchContext("test-world", "MyLEAGUE0005", "generation", "2021-22", "REGULAR_SEASON", "snapshot", "v1")
            outbox.open_cycle("cycle", context)
            with closing(outbox._get_connection()) as conn, conn:
                conn.execute("UPDATE decision_cycles SET status='SEALED' WHERE cycle_id='cycle'")

            def attempt(key):
                try:
                    DecisionOutbox(db).claim_test_calendar(key, "test-world", "MyLEAGUE0005", "epoch", "2021-12-31")
                    return key
                except ValueError:
                    return None

            with ThreadPoolExecutor(max_workers=2) as executor:
                winners = [key for key in executor.map(attempt, ("first", "second")) if key]
            self.assertEqual(len(winners), 1)
            with self.assertRaisesRegex(ValueError, "TEST_CALENDAR_UNRESOLVED"):
                outbox.claim_execution("cycle", "s4-plan")
            outbox.finish_test_calendar(winners[0], "UNKNOWN", "private-receipt")
            with self.assertRaisesRegex(ValueError, "NO_REPLAY"):
                outbox.claim_test_calendar("different", "test-world", "MyLEAGUE0005", "other-epoch", "2022-01-01")
            self.assertEqual(outbox.inspect_test_calendar(db, winners[0])["status"], "UNKNOWN")

    def test_s4_claim_blocks_calendar_and_verified_releases_only_future_window(self):
        with tempfile.TemporaryDirectory() as path:
            db = Path(path) / "outbox.db"
            outbox = DecisionOutbox(db)
            context = BatchContext("test-world", "MyLEAGUE0005", "generation", "2021-22", "REGULAR_SEASON", "snapshot", "v1")
            outbox.open_cycle("cycle", context)
            with closing(outbox._get_connection()) as conn, conn:
                conn.execute("UPDATE decision_cycles SET status='SEALED' WHERE cycle_id='cycle'")
                conn.execute("""INSERT INTO outbox_events (cycle_id,event_type,revision,timestamp)
                                VALUES ('cycle','EXECUTION_CLAIMED',1,'fixture')""")
            with self.assertRaisesRegex(ValueError, "S4_EXECUTION_UNRESOLVED"):
                outbox.claim_test_calendar("calendar", "test-world", "MyLEAGUE0005", "epoch", "2021-12-31")
            with closing(outbox._get_connection()) as conn, conn:
                conn.execute("UPDATE decision_cycles SET status='COMPLETED' WHERE cycle_id='cycle'")
            outbox.claim_test_calendar("calendar", "test-world", "MyLEAGUE0005", "epoch", "2021-12-31")
            outbox.finish_test_calendar("calendar", "VERIFIED_IN_MEMORY", "receipt")
            with self.assertRaises(cli.sqlite3.IntegrityError):
                outbox.claim_test_calendar("replay", "test-world", "MyLEAGUE0005", "epoch", "2021-12-31")
            outbox.claim_test_calendar("later", "test-world", "MyLEAGUE0005", "epoch", "2022-01-01")


if __name__ == "__main__":
    unittest.main()
