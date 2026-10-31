from __future__ import annotations

import os
import struct
import pytest

from src.vae_rea_research.contracts import (
    FieldEntry,
    FieldResearchStatus,
    NativeIdentityGrade,
)
from src.vae_rea_research.live_analyzer import LiveEngineAnalyzer


@pytest.fixture
def repo_root():
    cur = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))


@pytest.fixture
def analyzer(repo_root):
    return LiveEngineAnalyzer(repo_root=repo_root)


def test_coach_out_of_bounds_rejection(analyzer):
    """
    REA-AUD-P0-01: Verifies that out-of-bounds Coach values from flawed TEAM structure offsets
    are strictly rejected by domain validation and cannot be promoted to LIVE_RECEIPT.
    """
    qm = analyzer.queue_mgr
    # Build dictionary of coach field entries
    coach_entries = {}
    for idx in range(qm.total_count):
        entry = qm.get_entry_at(idx)
        if entry and entry.family == "coach_settings":
            coach_entries[entry.candidate_native_key] = entry

    # Exact 10 invalid readings identified in independent audit probe
    invalid_cases = {
        "POEOffense": 97,
        "POEOffense3": 100,
        "POEDefense2": 101,
        "PreferredSystem": 223,
        "ActiveSystem": 230,
        "ZoneUsage": 112,
        "BenchUtilization": 104,
        "HelpDefense": 108,
        "FreelanceType2": 97,
        "FreelanceType4": 95,
    }

    for key, bad_val in invalid_cases.items():
        entry = coach_entries.get(key)
        assert entry is not None, f"Coach entry {key} missing from queue"
        is_valid, reason = analyzer.validate_bounds(entry, bad_val)
        assert not is_valid, f"Expected {key}={bad_val} to be rejected, but passed: {reason}"
        assert "OUT_OF_BOUNDS" in reason

    # Verifiable valid readings must pass
    valid_cases = {
        "POEOffense": 1,         # Valid in {0..6}
        "POEOffense2": 7,        # Valid in {0, 7, 8, 9}
        "PreferredSystem": 2,    # Valid in {0..7}
        "ActiveSystem": 5,       # Valid in {0..7}
        "HelpDefense": 50,       # Valid in [0, 100]
        "ZoneUsage": 20,         # Valid in [0, 100]
        "FreelanceType": 16,     # Valid in {0..33}
    }
    for key, good_val in valid_cases.items():
        entry = coach_entries[key]
        is_valid, reason = analyzer.validate_bounds(entry, good_val)
        assert is_valid, f"Expected {key}={good_val} to pass, but rejected: {reason}"


def test_world_float_decoding(analyzer):
    """
    REA-AUD-P0-02: Verifies typed float decoding distinguishing IEEE-754 float32 from uint32 bit patterns.
    Raw uint32 1056964608 must decode to float 0.5.
    """
    raw_uint = 1056964608
    raw_bytes = struct.pack("<I", raw_uint)

    # Decode as float
    val_float = analyzer.decode_world_raw(raw_bytes, storage_type="float")
    assert isinstance(val_float, float)
    assert round(val_float, 4) == 0.5

    # Decode as uint32
    val_uint = analyzer.decode_world_raw(raw_bytes, storage_type="uint32")
    assert isinstance(val_uint, int)
    assert val_uint == 1056964608

    # Verify world catalog has storage_type='float' for game_speed (WORLD_REG_002 and WORLD_REG_086)
    w002 = analyzer._world_catalog.get("WORLD_REG_002")
    assert w002 is not None
    assert w002["storage_type"] == "float"
    assert w002["slot"] == "SLOT_SETTINGS"

    w086 = analyzer._world_catalog.get("WORLD_REG_086")
    assert w086 is not None
    assert w086["storage_type"] == "float"


def test_world_out_of_bounds_rejection(analyzer):
    """
    REA-AUD-P0-02: Verifies out-of-bounds rejection for normalize_stats and player_non_financial_ambitions.
    """
    qm = analyzer.queue_mgr
    entries = {qm.get_entry_at(i).field_id: qm.get_entry_at(i) for i in range(qm.total_count)}

    # WORLD_REG_008 normalize_stats (declared [0, 1]) read 21234136
    e_norm = entries["WORLD_REG_008"]
    is_valid, reason = analyzer.validate_bounds(e_norm, 21234136)
    assert not is_valid
    assert "OUT_OF_BOUNDS" in reason

    is_valid_ok, _ = analyzer.validate_bounds(e_norm, 1)
    assert is_valid_ok

    # WORLD_REG_020 player_non_financial_ambitions (declared [0, 100]) read 271058973
    e_amb = entries["WORLD_REG_020"]
    is_valid, reason = analyzer.validate_bounds(e_amb, 271058973)
    assert not is_valid
    assert "OUT_OF_BOUNDS" in reason

    is_valid_ok, _ = analyzer.validate_bounds(e_amb, 50)
    assert is_valid_ok


def test_world_slot_and_alias_disambiguation(analyzer):
    """
    REA-AUD-P0-02 & REA-AUD-P1-10: Disambiguates discrete controller slots (SLOT_SETTINGS vs SLOT_SLIDERS)
    and verifies that collision table correctly groups the 36 alias pairs.
    """
    w002 = analyzer._world_catalog["WORLD_REG_002"]   # game_speed: SLOT_SETTINGS + 0x00
    w041 = analyzer._world_catalog["WORLD_REG_041"]   # game_difficulty_preset: SLOT_SLIDERS + 0x00
    w085 = analyzer._world_catalog["WORLD_REG_085"]   # game_difficulty_preset: SLOT_SLIDERS + 0x00
    w086 = analyzer._world_catalog["WORLD_REG_086"]   # game_speed: SLOT_SETTINGS + 0x00

    # Ensure slot controllers are distinguished
    assert w002["slot"] == "SLOT_SETTINGS"
    assert w041["slot"] == "SLOT_SLIDERS"
    assert w002["slot"] != w041["slot"]

    # Collision table verification
    col = analyzer.compute_physical_collision_table()
    assert col["total_world_seeds"] == 86
    assert col["unique_physical_locations"] == 50
    assert col["collision_groups_count"] == 36

    # Verify W002 and W086 are grouped together in SLOT_SETTINGS + 0x00
    speed_group = next(
        g for g in col["collision_groups"]
        if g["slot"] == "SLOT_SETTINGS" and g["offset"] == "0x00"
    )
    group_fids = [e["field_id"] for e in speed_group["entries"]]
    assert "WORLD_REG_002" in group_fids
    assert "WORLD_REG_086" in group_fids


def test_static_fallback_and_failed_read_rejection(analyzer):
    """
    REA-AUD-P0-03: Proves that read failures (None) and static fallbacks (STATIC_GP_LAYOUT)
    are NEVER promoted to LIVE_RECEIPT.
    """
    qm = analyzer.queue_mgr
    entry = qm.get_entry_at(0)

    # 1. Read failure: val is None
    is_valid, reason = analyzer.validate_bounds(entry, None)
    assert not is_valid
    assert reason == "VALUE_IS_NONE"

    # 2. When process is not attached, read_live_field returns is_valid=False and val=None
    saved_mem = analyzer._mem
    try:
        analyzer._mem = None
        val, addr, notes, valid, reason = analyzer.read_live_field(entry)
        assert val is None
        assert not valid
        assert "NO_PROCESS" in addr or "FAILED" in reason or "NO_PROCESS" in reason
    finally:
        analyzer._mem = saved_mem


def test_remediation_epistemology_and_downgrade(analyzer, tmp_path):
    """
    REA-AUD-P0-04 & REA-AUD-P0-05: Verifies that after remediation, records are appropriately downgraded
    and epistemological tier is set to PRIOR_LITERATURE_HYPOTHESIS.
    """
    import shutil
    orig_records = analyzer.records_dir
    orig_ledger = analyzer.ledger_path
    orig_evidence = analyzer.evidence_dir
    orig_checkpoint = analyzer.checkpoint_path

    test_records = str(tmp_path / "records_demote")
    test_evidence = str(tmp_path / "evidence_demote")
    os.makedirs(test_records, exist_ok=True)
    os.makedirs(test_evidence, exist_ok=True)
    for f in os.listdir(orig_records):
        shutil.copy2(os.path.join(orig_records, f), os.path.join(test_records, f))

    analyzer.records_dir = test_records
    analyzer.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    analyzer.evidence_dir = test_evidence
    analyzer.checkpoint_path = str(tmp_path / "checkpoint_demote.json")
    try:
        remediated = analyzer.remediate_all_field_records()
        assert remediated["total"] == 204
        assert remediated["coach_demoted"] == 19
        assert remediated["world_floats_decoded"] >= 10
        assert remediated["unknown"] >= 50

        # Verify coach record
        c1_path = os.path.join(analyzer.records_dir, "COACH_DEFAULT_001.json")
        import json
        with open(c1_path, "r", encoding="utf-8") as f:
            c1 = json.load(f)
        assert c1["native_identity_grade"] == NativeIdentityGrade.RAW_MEMORY_CAPTURE_CANDIDATE.value
        assert c1["research_status"] == FieldResearchStatus.UNKNOWN.value
        assert c1["mechanism_analysis"]["epistemological_tier"] == "PRIOR_LITERATURE_HYPOTHESIS"
        assert c1["mechanism_analysis"]["empirical_causality_verified"] is False
        assert "raw_legacy_capture" in c1
    finally:
        analyzer.records_dir = orig_records
        analyzer.ledger_path = orig_ledger
        analyzer.evidence_dir = orig_evidence
        analyzer.checkpoint_path = orig_checkpoint


def test_sweep_3_full_live_grounding(analyzer, tmp_path):
    """
    Verifies Sweep 3 full live grounding and 100% receipt resolution.
    - Resolves all 99 player tendencies with canonical keys, native getters, and consumer callers.
    - Decodes all 19 Coach Gameplan settings from genuine COACHDATA bitfields.
    - Verifies all 86 World Settings with typed float/uint32 decoding and in-bounds validation.
    """
    assert len(analyzer._player_catalog) == 99
    t1 = analyzer._player_catalog["TENDENCY_NATIVE_001"]
    assert t1["native_getter_rva"] == "0x975820"
    assert t1["consumer_call_rva"] == "0x174510e"

    t51 = analyzer._player_catalog["TENDENCY_NATIVE_051"]
    assert t51["canonical_key"] == "TripleThreatShootTendency"
    assert t51["native_getter_rva"] == "0x975c50"

    if analyzer._mem and analyzer._mem.pid:
        import shutil
        orig_records = analyzer.records_dir
        orig_ledger = analyzer.ledger_path
        orig_evidence = analyzer.evidence_dir
        orig_checkpoint = analyzer.checkpoint_path

        test_records = str(tmp_path / "records_sweep3")
        test_evidence = str(tmp_path / "evidence_sweep3")
        os.makedirs(test_records, exist_ok=True)
        os.makedirs(test_evidence, exist_ok=True)
        for f in os.listdir(orig_records):
            shutil.copy2(os.path.join(orig_records, f), os.path.join(test_records, f))

        analyzer.records_dir = test_records
        analyzer.ledger_path = str(tmp_path / "iteration_ledger_sweep3.jsonl")
        analyzer.evidence_dir = test_evidence
        analyzer.checkpoint_path = str(tmp_path / "checkpoint_sweep3.json")
        try:
            res = analyzer.execute_sweep_3_live()
            assert res["total"] == 204
            assert res["live_receipt"] == 204
            assert res["player_tendencies_verified"] == 99
            assert res["coach_verified"] == 19
            assert res["world_verified"] == 86
            assert res["unknown"] == 0
            assert res["out_of_bounds_flagged"] == 0
        finally:
            analyzer.records_dir = orig_records
            analyzer.ledger_path = orig_ledger
            analyzer.evidence_dir = orig_evidence
            analyzer.checkpoint_path = orig_checkpoint
