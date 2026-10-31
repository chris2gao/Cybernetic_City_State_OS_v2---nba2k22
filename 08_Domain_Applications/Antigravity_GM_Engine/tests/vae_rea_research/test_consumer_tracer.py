from __future__ import annotations

import os
import json
import pytest

from src.vae_rea_research.consumer_tracer import NativeConsumerTracer


@pytest.fixture
def repo_root():
    cur = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))


@pytest.fixture
def tracer(repo_root):
    return NativeConsumerTracer(repo_root=repo_root)


def test_shot_tendency_call_sites_and_equilibrium_governor(tracer):
    """
    Verifies that the Shot-Touches Equilibrium Governor (RVA 0x1226947)
    and 3D pace multiplier (RVA 0x19b52d4) are documented with exact assembly.
    """
    call_sites = tracer.trace_shot_tendency_callers()
    assert len(call_sites) == 5

    # 1. Equilibrium Governor
    gov = next(c for c in call_sites if c["rva"] == "0x1226947")
    assert gov["role"] == "Shot-Touches Equilibrium Governor"
    assert any("0x140975820" in line for line in gov["assembly"])  # get_shot_tendency
    assert any("0x140975b30" in line for line in gov["assembly"])  # get_touches
    assert any("sub edx, 5" in line for line in gov["assembly"])   # margin clamp
    assert "tendency.TouchTendency" in gov["coupled_fields"]

    # 2. 3D Pace Multiplier
    pace = next(c for c in call_sites if c["rva"] == "0x19b52d4")
    assert pace["role"] == "Coach Tempo/Pace Multiplier Weighting"
    assert any("mulss xmm0, xmm6" in line for line in pace["assembly"])

    # 3. Snapshot Loop
    snap = next(c for c in call_sites if c["rva"] == "0x174510e")
    assert snap["role"] == "Sequential Roster Extraction"


def test_coach_gameplan_traversal_and_pacing_engine(tracer):
    """
    Verifies coaching staff array traversal (RVA 0xc03133) and
    the [10, 70] tempo clamping bounds in the dynamic pacing engine (RVA 0x120b9ae..0x120babb).
    """
    coach_data = tracer.trace_coach_gameplan_consumers()
    assert "staff_array_traversal" in coach_data
    assert "dynamic_pacing_engine" in coach_data

    # Staff traversal
    trav = coach_data["staff_array_traversal"]
    assert trav["rva"] == "0xc03133"
    assert any("0xce8" in line for line in trav["assembly"])

    # Dynamic pacing bounds [10, 70]
    pacing = coach_data["dynamic_pacing_engine"]
    assert pacing["rva"] == "0x120b9ae"
    assert any("cmp ecx, 0x46" in line for line in pacing["assembly"])  # 70 decimal
    assert any("cmovg ecx, eax" in line for line in pacing["assembly"])
    assert any("cmp ecx, 0xa" in line for line in pacing["assembly"])   # 10 decimal
    assert any("cmovl ecx, eax" in line for line in pacing["assembly"])


def test_roster_snapshot_stride_and_pipeline(tracer):
    """
    Verifies that the Roster Simulation Snapshot Function has player stride 0x27c (636 bytes).
    """
    pipeline = tracer.trace_roster_snapshot_pipeline()
    assert pipeline["function_rva"] == "0x1744bd0"
    assert "0x27c" in pipeline["player_stride"]
    assert "0x174510e..0x174566a" in pipeline["tendency_sequence_range"]


def test_consumer_trace_enrichment_coverage(tracer):
    """
    Verifies that all 204 field records are enriched with confirmed consumer call graphs.
    """
    results = tracer.enrich_all_field_records_with_consumer_traces()
    assert results["total_enriched"] == 204
    assert results["shot_tendency_enriched"] == 1
    assert results["touches_enriched"] == 1
    assert results["other_tendencies_enriched"] == 97
    assert results["coach_settings_enriched"] == 19
    assert results["world_settings_enriched"] == 86

    # Verify T1 record
    t1_path = os.path.join(tracer.records_dir, "TENDENCY_NATIVE_001.json")
    with open(t1_path, "r", encoding="utf-8") as f:
        t1 = json.load(f)
    assert t1["consumer_path_status"] == "CONFIRMED_NATIVE_CONSUMER_CALLGRAPH"
    assert "verified_consumer_call_graph" in t1
    assert t1["verified_consumer_call_graph"]["equilibrium_governor"]["rva"] == "0x1226947"

    # Verify C1 record
    c1_path = os.path.join(tracer.records_dir, "COACH_DEFAULT_001.json")
    with open(c1_path, "r", encoding="utf-8") as f:
        c1 = json.load(f)
    assert c1["consumer_path_status"] == "CONFIRMED_NATIVE_CONSUMER_CALLGRAPH"
    assert c1["verified_consumer_call_graph"]["dynamic_pacing_engine"]["tempo_clamping_bounds"] == [10, 70]
