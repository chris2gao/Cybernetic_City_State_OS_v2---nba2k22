from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factor_adapters import adapter_contract, coach_field, prepare_coach_patch, prepare_training_patch
from factor_analysis import adjust_fdr, compare_independent_worldlines, screen_game_window, screen_settled_events
from factor_assignment import Exposure, allocate_window, event_study, windows_for_schedule
from factor_inventory import StudyInputs
from factor_lab_cli import report
from factor_progress import ProgressEvent, ProgressLedger
from factor_runner import LiveEnvelope, WindowRunner, digest, window_operations
from native_factor_slots import resolve_tendency_slot, require_s4_live_tendency, tendency_slots
from bulk_executor import BulkBatch, BulkBatchHeader, BulkBatchPlanner, BulkFridaScriptCompiler, BulkIntentItem
from contracts import BUILD
import season_cycle_host
from season_cycle_host import SeasonCycleHost
import factor_readback
import player_skill_reader
import refresh

ROOT = Path(__file__).resolve().parents[5]
INPUTS = ROOT / "01_os/07_content/_runs/run-20261108-nba2k22-full-factor-plan-001"
SHA = "a" * 64


@pytest.fixture(scope="module")
def study():
    return StudyInputs.load(INPUTS)


def test_fixed_full_denominator_and_native_catalog(study):
    assert study.baseline["loaded_slot"] == "MyLEAGUE0005"
    assert study.baseline["frozen_origin"] == "MyLEAGUE0003"
    assert len(study.factors) == 223
    assert len(study.fixtures) == 1030
    assert len(tendency_slots()) == 99
    contracts = [adapter_contract(factor) for factor in study.factors.values()]
    assert sum(contract.action is not None for contract in contracts) == 153
    rows = study.crosswalk()
    assert sum(bool(row["reference_slots"]) for row in rows.values()) == 120
    assert sum(row["live_writer_qualified"] for row in rows.values()) == 1
    assert not any(row["execution_authorized"] for row in rows.values())


@pytest.mark.parametrize("filename", ["MyLEAGUE0005", "MyLEAGUE0003"])
def test_disposable_save_binding_excludes_cold_backup(filename):
    plan = {"worldline_id": "fixture", "stop_exclusive": "2022-01-09"}
    binding = {"loaded_filename": filename, "binding_sha256": SHA, "build_sha256": BUILD,
               "worldline_id": "fixture", "pid": 1, "epoch": {"pid": 1}, "last_regular_date": "2022-04-10"}
    raw = json.dumps({"schema": "nba2k22.vae.live_envelope.v1", "revoked": False,
                      "human_decision_ref": "fixture-only", "build_sha256": BUILD, "binding": binding,
                      "plan_digest": digest(plan), "operation_digests": [], "calendar_digests": [],
                      "max_setters": 0, "max_calendar": 0, "valid_from": "2022-01-01T00:00:00+00:00",
                      "expires_at": "2022-02-01T00:00:00+00:00"}).encode()
    envelope = LiveEnvelope(raw, sha256(raw).hexdigest())
    now = datetime(2022, 1, 8, tzinfo=timezone.utc)
    if filename == "MyLEAGUE0003":
        with pytest.raises(ValueError, match="LIVE_DISPOSABLE_SAVE_AND_EPOCH_REQUIRED"):
            envelope.verify(plan, binding, [], [], now)
    else:
        assert envelope.verify(plan, binding, [], [], now)["binding"] == binding


def test_unknown_slot_read_only_qualification_binds_roster_and_epoch(tmp_path, monkeypatch):
    host = SeasonCycleHost.__new__(SeasonCycleHost)
    database = tmp_path / "world.sqlite"
    binding = {"save_id": "save", "worldline_id": "world"}
    host.state = dict(binding, save_directory=str(tmp_path), loaded_filename="MyLEAGUE0005",
                      database_file=str(database))
    epoch = {"pid": 1, "creation_filetime": 10}
    progress = {"mode_raw": 1, "period_raw": 29, "today_native_iso_date": "2022-01-01"}
    monkeypatch.setattr(season_cycle_host, "read_binding", lambda *_: (binding, SHA))
    monkeypatch.setattr(season_cycle_host, "bound_database", lambda *_: database)
    monkeypatch.setattr(refresh, "_context", lambda _: {"epoch": epoch, "game_progress": dict(progress)})
    monkeypatch.setattr(refresh, "resolve_pid", lambda _: 1)
    reader = SimpleNamespace(creation_filetime=10, close=lambda: None)
    reads = []

    def read(address, width, label):
        reads.append(label)
        if address == 0x1000 + 0xa8 and width == 8:
            return (0x2000).to_bytes(8, "little")
        assert address == 0x1000 + 0x458 and width == 99
        return bytes([44] * 99)

    reader.read = read
    monkeypatch.setattr(season_cycle_host, "ReadOnlyGameProcess", lambda _: reader)
    player = {"native_unique_id_raw": 101, "current_core_roster_status": "CURRENT_CORE_ROSTER",
              "source_player_index": 0, "current_roster_slot": 1, "native_team_id": 2}
    model = {"descriptors": [None, {"address": 0x1000, "stride": 0x800, "count": 1}],
             "core_team_pointer_map": {0x2000: 2}, "players": [player], "skill_rows": [{"tendencies": {}}]}
    monkeypatch.setattr(player_skill_reader, "collect_player_skills", lambda _: (model, None))
    request = {"pid": 1, "epoch": epoch, "team_id": 2, "uid": 101,
               "field": "UNKNOWN_RAW_BYTE_016", "binding_sha256": SHA}
    result = host.read_factor_qualification_snapshot(**request)
    assert result["raw_value"] == 44 and result["factor_id"] == "TENDENCY_NATIVE_016"
    assert result["neighborhood_sha256"] == sha256(bytes([44] * 99)).hexdigest()
    assert result["write_qualified"] is False
    assert reads == ["S4_CONTRACT_TEAM", "PUBLIC_PLAYER_TENDENCY_NEIGHBORHOOD"]
    model["players"].append(dict(player))
    with pytest.raises(ValueError, match="QUALIFICATION_SNAPSHOT_ROSTER_OR_SCENE_CHANGED"):
        host.read_factor_qualification_snapshot(**request)


def test_worlddata_port_routes_host_state_through_calendar_orchestrator(tmp_path, monkeypatch):
    database = tmp_path / "world.sqlite"
    binding = {"save_id": "save", "worldline_id": "world", "loaded_filename": "MyLEAGUE0005",
               "pid": 1, "binding_sha256": SHA}
    state = {"save_directory": str(tmp_path), "loaded_filename": binding["loaded_filename"],
             "database_file": str(database)}
    orchestrator = SimpleNamespace(save_directory=tmp_path, loaded_filename=binding["loaded_filename"],
                                   database=database, binding=binding, save_id="save", binding_hash=SHA)

    def make_orchestrator(directory, filename, database_path):
        assert (directory, filename, database_path) == tuple(state.values())
        return orchestrator

    def refresh_fixture(pid, directory, filename, output, *, families):
        assert (pid, directory, filename) == (1, tmp_path, binding["loaded_filename"])
        assert families == ("schedule", "game-mode", "player-skills")
        output.mkdir()
        (output / "refresh-report.json").write_bytes(b"fixture")

    def capture(owner, directory, report_sha, plan, bound):
        assert owner is orchestrator and directory.name == "post" and bound is binding
        assert report_sha == sha256(b"fixture").hexdigest()
        return {"today": plan["stop_exclusive"]}

    monkeypatch.setattr(factor_readback, "CalendarSimOrchestrator", make_orchestrator)
    monkeypatch.setattr(factor_readback, "bound_database", lambda *_: database)
    monkeypatch.setattr(factor_readback, "capture_game_outcomes", capture)
    monkeypatch.setattr(refresh, "refresh_world", refresh_fixture)
    port = factor_readback.FactorWorldDataPort(SimpleNamespace(state=state), binding, tmp_path / "capture")
    assert port("post", {"stop_exclusive": "2022-01-02"}, []) == {"today": "2022-01-02"}
    orchestrator.binding_hash = "b" * 64
    with pytest.raises(ValueError, match="FACTOR_CAPTURE_HOST_SAVE_BINDING_MISMATCH"):
        port("pre", {}, [])


def test_real_windows_and_two_sided_multi_factor_plan(study):
    teams = {int(row["native_team_id"]) for row in study.players if row["eligible_now"] == "True"}
    windows = windows_for_schedule(study.fixtures, teams, "2021-11-16", "2022-04-10")
    assert len(windows) == 19
    assert sum(len(window["real_game_ids"]) for window in windows) == 981
    first = study.reference["windows"][0]
    values = {(row["factor_id"], row["uid"]): row["baseline"] for row in first["team_assignments"].values()
              if row["baseline"] is not None}
    prior = Exposure("ref", first["fields"][0], 1, 444, "2021-11-01", 55, "test-receipt", "2021-11-12")
    other_world = Exposure("old", first["fields"][0], 2, 222, "2021-11-01", 60, "other-world")
    result = allocate_window(study, windows[0], first["fields"], values, [prior, other_world],
                             worldline="ref", seed=study.reference["seed"])
    assert len(result["teams"]) == 30 and len(result["games"]) == 53
    assert result["treatment_slots"] == 20 and result["unqualified_treatment_slots"] >= 16
    assert result["cross_factor_opponent_games"] > 0
    assert result["estimand"] == "EXPLORATORY_WITH_CARRYOVER"
    assert result["teams"][1]["prior_team_treatments"][0]["receipt_ref"] == "test-receipt"
    assert not result["teams"][2]["prior_team_treatments"]
    assert not result["live_authorized"]


def test_export_has_five_exact_factors_and_keeps_original_unknown_slot():
    retained = INPUTS.parent / "run-20261108-nba2k22-full-factor-engineering-001/REFERENCE_TENDENCY_VALUES.json"
    result = report(INPUTS, retained)
    first = result["first_window"]
    original = result["recompiled_team_windows"][0]
    assert len(first["factors"]) == 5
    assert all(row["baseline"] is not None and row["target"] is not None for row in first["teams"].values())
    assert {game["game_id"] for game in first["games"]} == {game["game_id"] for game in original["games"]}
    assert "TENDENCY_NATIVE_016" in original["fields"] and "TENDENCY_NATIVE_016" not in first["factors"]


@pytest.mark.parametrize("key", ["SHOT_TENDENCY", "SHOT_THREE_TENDENCY", "TOUCHES_TENDENCY", "UNKNOWN_RAW_BYTE_016"])
def test_exact_field_and_neighbor_checks(key):
    slot = resolve_tendency_slot(key)
    before = bytes([50] * 99)
    after = slot.expected_image(before, 50, 55)
    assert slot.verify_readback(before, after, 50, 55, 55) == "VERIFIED"
    assert slot.verify_readback(before, before, 50, 50, 50) == "NOOP"
    with pytest.raises(ValueError, match="CAS"):
        slot.expected_image(before, 51, 55)
    neighbor = bytearray(after)
    neighbor[slot.ordinal % 99] = 49
    with pytest.raises(ValueError, match="NEIGHBOR"):
        slot.verify_readback(before, bytes(neighbor), 50, 55, 55)
    if key != "SHOT_TENDENCY":
        with pytest.raises(ValueError, match="NOT_LIVE_QUALIFIED"):
            require_s4_live_tendency(slot.native_key)


def test_coach_and_training_typed_storage(study):
    coach = adapter_contract(study.factors["COACH_DEFAULT_004"])
    packed = coach_field(coach)
    image = bytearray(352)
    image[319] = 0x87
    before = bytes(image)
    parameters, after = prepare_coach_patch(coach, "POEDefense", 1, before, 0, 13)
    assert parameters["values"] == {"POEDefense": 13}
    assert packed.verify(before, after, 0, 13) == 13
    assert after[319] == 0x87
    with pytest.raises(ValueError, match="DOMAIN"):
        packed.plan(before, 0, 31)
    training = adapter_contract(study.factors["TRAIN_DAILY/focus_01"])
    initial = struct.pack("<3f", 10, 20, 30) + bytes(range(44))
    params, changed = prepare_training_patch(training, 1, "2022-01-01", initial, 20, 22)
    assert params["focus_values_raw"] == [10, 22, 30]
    assert changed[12:] == initial[12:]
    with pytest.raises(ValueError, match="CAS"):
        prepare_training_patch(training, 1, "2022-01-01", initial, 30, 22)
    world = adapter_contract(study.factors["WORLD/sim_quarter_length"])
    assert world.unit == "WORLDLINE" and world.action is None


def settled_typed_fixture(study, factor_id):
    contract = adapter_contract(study.factors[factor_id])
    is_coach = factor_id.startswith("COACH")
    endpoint = "team_FGA" if is_coach else "fatigue"
    rows, refs = [], {}
    for i, arm in enumerate(("C", "H", "L"), 1):
        world = f"fixture-{i}"
        if is_coach:
            initial = bytearray(352)
            initial[316] = 14
            before, original, target = bytes(initial), 14, {"C": 14, "H": 13, "L": 15}[arm]
            payload, after = prepare_coach_patch(contract, "POEDefense", i, before, original, target)
            observed = coach_field(contract).verify(before, after, original, target)
        else:
            before, original, target = struct.pack("<3f", 10, 20, 30) + bytes(44), 20, {"C": 20, "H": 22, "L": 18}[arm]
            payload, after = prepare_training_patch(contract, i, "2022-01-02", before, original, target)
            observed = struct.unpack_from("<f", after, 4)[0]
            assert before[:4] + before[8:] == after[:4] + after[8:]
        refs[world] = {"event_id": f"fixture-{contract.object_kind}-{i}", "event_date": "2022-01-02",
                       "source_unit": f"{world}/settlement"}
        rows.append(dict(refs[world], mode="FIXTURE", worldline_id=world, arm=arm, factor_id=factor_id,
                         origin_sha256=SHA, before_source=f"{world}/before", after_source=f"{world}/after",
                         before_identity=f"team-{i}", after_identity=f"team-{i}", opportunity=True,
                         setter_verified=observed == target, requested_value=target, observed_value=observed,
                         action_payload=payload, before={endpoint: 20}, after={endpoint: {"C": 20, "H": 22, "L": 19}[arm]}))
    return event_study(study.factors[factor_id], list(refs), refs), rows, endpoint


@pytest.mark.parametrize("factor_id", ["COACH_DEFAULT_004", "TRAIN_DAILY/focus_01"])
def test_classified_typed_fixture_from_settings_to_settlement(study, factor_id):
    plan, rows, endpoint = settled_typed_fixture(study, factor_id)
    result = screen_settled_events(plan, rows, endpoint, mode="FIXTURE")
    assert result["effects"] == {"H_minus_C": 2, "L_minus_C": -1}
    assert result["status"] == "UNDERPOWERED"
    with pytest.raises(ValueError, match="IDENTITY_OR_SOURCE_MISMATCH"):
        screen_settled_events(plan, rows, endpoint, mode="LIVE")
    rows[1]["setter_verified"] = False
    assert screen_settled_events(plan, rows, endpoint, mode="FIXTURE")["excluded"] == {"fixture-2": "SETTER_UNVERIFIED"}


def test_bulk_compiles_three_different_native_indices_with_existing_cas_and_neighbor_gate():
    slots = [resolve_tendency_slot(key) for key in ("SHOT_THREE_TENDENCY", "TOUCHES_TENDENCY", "UNKNOWN_RAW_BYTE_016")]
    header = BulkBatchHeader("offline-factors", "fixture-slot", BUILD, "fixture-only", "fixture-snapshot")
    batch = BulkBatch(header, tuple(BulkIntentItem(f"i-{slot.ordinal}", "PLAYER_PATCH_TENDENCIES", 1,
                                                  slot.native_key, 50, 51, player_id=100 + index)
                                   for index, slot in enumerate(slots)))
    chunks = BulkBatchPlanner().plan(batch)
    assert len(chunks) == 1
    script = BulkFridaScriptCompiler().compile_chunk(chunks[0], header)
    for slot in slots:
        assert slot.native_key in script
        assert f'"native_index": {slot.index}' in script or f'"native_index":{slot.index}' in script
    assert "CAS_EXPECTED_BEFORE_MISMATCH" in script
    assert "UNREQUESTED_STAT_BYTE_CHANGED" in script


def fixture_plan():
    factor_ids = (resolve_tendency_slot("SHOT_THREE_TENDENCY").factor_id, "TENDENCY_NATIVE_066", "TENDENCY_NATIVE_016")
    teams = {}
    games = []
    for index, factor in enumerate(factor_ids):
        group = {}
        for offset, arm in enumerate("HLC"):
            team = index * 3 + offset + 1
            group[arm] = teams[team] = {"factor_id": factor, "team_id": team, "uid": 100 + team, "arm": arm,
                                       "baseline": 50, "target": {"H": 55, "L": 45, "C": 50}[arm],
                                       "live_writer_qualified": False}
        for day, arm in enumerate("HL", 1):
            home, away = group[arm], group["C"]
            games.append({"game_id": (day - 1) * 3 + index + 1, "date": f"2022-01-0{day}",
                          "home_team": home["team_id"], "away_team": away["team_id"], "home": home, "away": away})
    windows = [{"start": "2022-01-01", "stop_exclusive": "2022-01-02",
                "planned_finals": [1, 2, 3], "next_day_controls": [4, 5, 6]},
               {"start": "2022-01-02", "stop_exclusive": "2022-01-03",
                "planned_finals": [4, 5, 6], "next_day_controls": [7]}]
    return {"worldline_id": "FIXTURE", "start": windows[0]["start"], "stop_exclusive": windows[-1]["stop_exclusive"],
            "factors": factor_ids, "teams": teams, "games": games, "subwindows": windows}


class FixturePort:
    mode = "FIXTURE"

    def __init__(self, failure=None):
        self.failure = failure
        self.events = []

    def setter(self, key, op):
        self.events.append("setter")
        slot = resolve_tendency_slot(op["factor_id"])
        before = bytes([50] * 99)
        after = slot.expected_image(before, op["expected_before"], op["target"])
        if self.failure == "neighbor":
            bad = bytearray(after)
            bad[slot.ordinal % 99] = 48
            after = bytes(bad)
        try:
            slot.verify_readback(before, after, op["expected_before"], op["target"], op["target"])
        except ValueError:
            return {"status": "UNKNOWN", "source_ref": key}
        return {"status": "APPLIED", "source_ref": key, "value": op["target"]}

    def simulate(self, key, window):
        self.events.append("sim")
        return {"status": "VERIFIED", "source_ref": key, "today": window["stop_exclusive"],
                "final_game_ids": window["planned_finals"], "next_day_pending_ids": window["next_day_controls"]}

    def capture(self, phase, plan, setters):
        self.events.append(phase)
        result = {"mode": "FIXTURE", "worldline_id": "FIXTURE", "source_unit": f"fixture-{phase}"}
        if phase == "pre":
            result["today"] = plan["start"]
            result["applied_values"] = {digest(op): op["target"] for op in window_operations(plan)}
        else:
            result["today"] = plan["stop_exclusive"]
            games = []
            for game in plan["games"]:
                if self.failure == "partial" and game["game_id"] == 1:
                    continue
                unit = f"fixture-{game['game_id']}"
                boxes = [{"team_id": actor["team_id"], "uid": actor["uid"], "disposition": "PLAYED",
                          "metrics": {"FGA": {"H": 12, "L": 8, "C": 10}[actor["arm"]], "MIN": 24}}
                         for actor in (game["home"], game["away"])]
                games.append(dict(game, unit=unit, team_box_unit=unit, player_box_unit=unit, final=True,
                                  was_simulated=True, score_conserved=True, team_boxes=boxes))
            result["games"] = games
        return result


def test_multi_field_end_to_end_with_partial_local_readback(tmp_path):
    plan = fixture_plan()
    port = FixturePort("partial")
    runner = WindowRunner(port, tmp_path)
    result = runner.run(plan, screen_game_window)
    assert result["status"] == "ANALYSIS_RECORDED" and result["mode"] == "FIXTURE"
    assert result["setter_success"] == 6 and result["calendar_attempts"] == 2
    assert result["analysis"]["qualified_game_count"] == 5
    assert result["analysis"]["missing_game_ids"] == [1]
    unknown = result["analysis"]["factors"]["TENDENCY_NATIVE_016"]
    assert unknown["metrics"]["FGA"]["estimates"] == {"H_minus_C": 2, "L_minus_C": -2}
    assert unknown["status"] == "UNDERPOWERED"
    assert port.events == ["setter"] * 6 + ["pre", "sim", "sim", "post"]
    with pytest.raises(FileExistsError):
        runner.run(plan, screen_game_window)


def test_neighbor_unknown_stops_and_does_not_replay(tmp_path):
    port = FixturePort("neighbor")
    runner = WindowRunner(port, tmp_path)
    result = runner.run(fixture_plan(), screen_game_window)
    assert result["status"] == "STOPPED_UNKNOWN_NO_REPLAY"
    assert result["setter_attempts"] == 1 and result["calendar_attempts"] == 0
    assert port.events == ["setter"]


def test_fixture_cannot_use_human_grant(tmp_path):
    with pytest.raises(ValueError, match="FIXTURE_PORT"):
        WindowRunner(FixturePort(), tmp_path, live_envelope=LiveEnvelope(b"{}", SHA)).run(fixture_plan(), screen_game_window)


def test_event_factorial_and_no_replication_promotion(study):
    field = study.factors["TRAIN_DAILY/focus_01"]
    refs = {arm: {"event_id": f"training-{arm}", "event_date": "2022-01-01", "source_unit": arm}
            for arm in ("00", "10", "01", "11")}
    assert event_study(field, list(refs), refs)["classification"] == "EVENT_BOUND_REFERENCE"
    inputs = [{"worldline_id": arm, "arm": arm, "origin_sha256": SHA, "before_source": f"before-{arm}",
               "after_source": f"after-{arm}", "event_id": f"event-{arm}", "before": {"FGA": 10},
               "after": {"FGA": after}} for arm, after in zip(refs, (10, 11, 12, 15), strict=True)]
    result = compare_independent_worldlines(inputs, "FGA", factorial=True)
    assert result["effects"]["interaction"] == 2 and result["status"] == "UNDERPOWERED"
    with pytest.raises(ValueError, match="INDEPENDENT"):
        compare_independent_worldlines(inputs + [inputs[0]], "FGA", factorial=True)
    assert adjust_fdr({"a": .01, "b": .2}) == {"b": .2, "a": .02}
    ledger = ProgressLedger(study)
    ledger.record(ProgressEvent(field.factor_id, "NATIVE_LOCATED", "FIXTURE", SHA, {"build_sha256": SHA, "location": 12}))
    assert ledger.query(field.factor_id, "COACH")["source"] is None
    assert len(ledger.next_queue()) == 223
    with pytest.raises(ValueError, match="CANNOT_SKIP"):
        ledger.record(ProgressEvent(field.factor_id, "BROAD_SCREENED", "LIVE", SHA, {
            "worldline_id": "W", "effect": 2, "analysis_ref": "a", "limitations": []}))
