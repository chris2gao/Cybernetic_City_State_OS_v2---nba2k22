from __future__ import annotations

import os
import shutil
import pytest

from src.vae_rea_research.consumer_tracer import NativeConsumerTracer


@pytest.fixture
def tracer():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    # In test mode, auto_attach=False to ensure test environment is strictly isolated
    return NativeConsumerTracer(repo_root=repo_root, auto_attach=False)


def test_tactical_role_governor_assembly_and_raw_bytes(tracer):
    """
    Verifies that the Tactical Role Governor contains exact machine code bytes,
    RVA locations, and verified control flow for core vs non-core role players.
    """
    callers = tracer.trace_shot_tendency_callers()
    assert len(callers) >= 2

    gov = next(c for c in callers if c["rva"] == "0x1226947")
    assert gov["role"] == "Role-Based Tactical Shot Ceiling Governor"
    assert gov["epistemological_grade"] == "STATIC_DISASSEMBLY_LEAD"
    assert "48 8d 4c 24 30" in gov["raw_bytes_hex"]  # lea rcx, [rsp + 0x30]
    assert "83 f9 03" in gov["raw_bytes_hex"]        # cmp ecx, 3
    assert "0f 4c c8" in gov["raw_bytes_hex"]        # cmovl ecx, eax

    # Check that disassembly text matches raw bytes
    disasm_text = "\n".join(gov["disassembly"])
    assert "cmp      ecx, 3" in disasm_text
    assert "cmovl    ecx, eax" in disasm_text
    assert "sub      edx, 5" in disasm_text


def test_coach_pacing_engine_raw_bytes_and_eax_proof(tracer):
    """
    Verifies Coach Dynamic Pacing Engine:
    - Proves eax is loaded with 0x46 (70 decimal) at 0x120ba98 before cmovg.
    - Proves eax is loaded with 0x0a (10 decimal) at 0x120bab0 before cmovl.
    - Proves raw machine code bytes match verified NBA2K22.exe executable.
    """
    traces = tracer.trace_coach_gameplan_consumers()
    pacing = traces["tempo_pacing_engine"]
    assert pacing["rva"] == "0x120ba72"
    assert pacing["clamping_bounds"] == [10, 70]
    assert pacing["epistemological_grade"] == "STATIC_DISASSEMBLY_LEAD"

    # Verify exact raw byte sequence for mov eax, 70 and mov eax, 10
    raw = pacing["raw_bytes_hex"]
    assert "b8 46 00 00 00" in raw  # mov eax, 0x46 (70)
    assert "0f 4f c8" in raw        # cmovg ecx, eax
    assert "b8 0a 00 00 00" in raw  # mov eax, 0x0a (10)
    assert "0f 4c c8" in raw        # cmovl ecx, eax

    disasm_text = "\n".join(pacing["disassembly"])
    assert "mov      eax, 0x46" in disasm_text
    assert "cmovg    ecx, eax" in disasm_text
    assert "mov      eax, 0xa" in disasm_text
    assert "cmovl    ecx, eax" in disasm_text


def test_roster_snapshot_stride_and_pipeline(tracer):
    """
    Verifies the roster snapshot pipeline disassembly lead.
    """
    callers = tracer.trace_shot_tendency_callers()
    snap = next(c for c in callers if c["rva"] == "0x174510e")
    assert snap["role"] == "Sequential Roster Snapshot Extraction"
    assert "e8 0d 07 23 00" in snap["raw_bytes_hex"]
    assert "89 85 e0 00 00 00" in snap["raw_bytes_hex"]


def test_consumer_trace_enrichment_coverage_in_tmp_path(tracer, tmp_path):
    """
    Verifies consumer trace enrichment on an isolated temporary directory.
    CRITICAL: Does NOT overwrite production 06_执行/field_records/ files during test run!
    """
    orig_records = tracer.records_dir
    test_records = str(tmp_path / "test_records")
    os.makedirs(test_records, exist_ok=True)

    # Copy production records to tmp_path
    for fname in os.listdir(orig_records):
        shutil.copy2(os.path.join(orig_records, fname), os.path.join(test_records, fname))

    # Run enrichment on test_records
    res = tracer.enrich_all_field_records_with_consumer_traces(target_dir=test_records)
    assert res["total_enriched"] == 204
    assert res["shot_tendency_enriched"] == 1
    assert res["touches_enriched"] == 1
    assert res["other_tendencies_enriched"] == 97
    assert res["coach_tempo_enriched"] == 1
    assert res["other_coach_settings_enriched"] == 18
    assert res["world_settings_enriched"] == 86

    # Verify that T1 in test_records has accurate epistemological statuses
    import json
    with open(os.path.join(test_records, "TENDENCY_NATIVE_001.json"), "r", encoding="utf-8") as f:
        t1 = json.load(f)
    assert t1["consumer_path_status"] == "DISASSEMBLY_ROLE_GOVERNOR_LOCATED"
    assert t1["game_effect_status"] == "STATIC_DISASSEMBLY_LEAD"
    assert t1["mechanism_analysis"]["epistemological_tier"] == "PRIOR_LITERATURE_HYPOTHESIS"
    assert t1["mechanism_analysis"]["empirical_causality_verified"] is False
    assert t1["raw_legacy_capture"]["legacy_timestamp"] == "2026-10-31T03:00:00Z"

    # Verify that Coach 14 (Tempo) vs Coach 1 (POEOffense) are differentiated
    with open(os.path.join(test_records, "COACH_DEFAULT_014.json"), "r", encoding="utf-8") as f:
        c14 = json.load(f)
    assert c14["consumer_path_status"] == "DISASSEMBLY_PACING_ENGINE_LOCATED"
    assert c14["game_effect_status"] == "STATIC_DISASSEMBLY_LEAD"

    with open(os.path.join(test_records, "COACH_DEFAULT_001.json"), "r", encoding="utf-8") as f:
        c1 = json.load(f)
    assert c1["consumer_path_status"] == "COACHDATA_STRUCTURE_LOCATED"
    assert c1["game_effect_status"] == "LIVE_BITFIELD_READ_ONLY"


def test_offline_mode_no_attach(tracer):
    """
    Verifies that in offline mode (auto_attach=False), tracer operates without crashing
    and gracefully reports NO_PROCESS_ATTACHED on verify_live_bytes.
    """
    assert tracer._mem is None
    res = tracer.verify_live_bytes()
    assert res["status"] == "NO_PROCESS_ATTACHED"
    assert res["bytes_verified"] is False
