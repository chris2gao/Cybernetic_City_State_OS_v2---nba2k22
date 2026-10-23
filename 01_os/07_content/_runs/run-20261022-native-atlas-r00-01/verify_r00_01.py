#!/usr/bin/env python3
"""
Verification script for NATIVE-ATLAS-R00-01.
Validates offline calibration artifacts, origin hypotheses, native deltas,
and fail-closed invariants for ROSTERDATA Slot 1 and Slot 24.
"""

import sys
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RESEARCH_DIR = REPO_ROOT / "08_Domain_Applications" / "Antigravity_GM_Engine" / "research" / "native_access" / "NATIVE_ATLAS_R00_01"
RUN_DIR = REPO_ROOT / "01_os" / "07_content" / "_runs" / "run-20261022-native-atlas-r00-01"

def check_source_manifest():
    manifest_path = RESEARCH_DIR / "source_manifest.json"
    if not manifest_path.is_file():
        print(f"FAIL: Missing {manifest_path}")
        return False
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data.get("task_id") == "NATIVE-ATLAS-R00-01", "task_id mismatch"
    assert data.get("target_object") == "ROSTERDATA", "target_object mismatch"
    
    source_ids = {s["source_id"] for s in data.get("sources", [])}
    required_sources = {
        "HINTS_V0_ROOTS_0",
        "HINTS_V0_SLOT_1_PLAYER",
        "HINTS_V0_SLOT_24_PLAYER_STATS",
        "QUEUE_V0_R00_01",
        "AG_01C_OBJECT_CATALOG_DESC_1_AND_24",
        "AG_01B_DIRECTORY_AUDIT",
        "AG_01D_BOXSCORE_STATBANK_ALIGNMENT"
    }
    missing = required_sources - source_ids
    assert not missing, f"Missing required sources: {missing}"
    
    boundary = data.get("provenance_boundary", {})
    assert boundary.get("live_game_attached") is False, "live_game_attached must be False"
    assert boundary.get("live_memory_read") is False, "live_memory_read must be False"
    assert boundary.get("historical_heap_addresses_treated_as_live") is False, "historical addresses must not be live"
    
    print("PASS: SOURCE_MANIFEST_CHECK")
    return True

def check_descriptor_hypotheses():
    hyp_path = RESEARCH_DIR / "descriptor_origin_hypotheses.json"
    if not hyp_path.is_file():
        print(f"FAIL: Missing {hyp_path}")
        return False
    with open(hyp_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    hypotheses = {h["hypothesis_id"]: h for h in data.get("hypotheses", [])}
    assert "HYP-A-NATIVE-DISASSEMBLY" in hypotheses, "Missing HYP-A"
    assert "HYP-B-LEGACY-CALIBRATION-ARTIFACT" in hypotheses, "Missing HYP-B"
    
    hyp_a = hypotheses["HYP-A-NATIVE-DISASSEMBLY"]
    assert hyp_a.get("status") == "CONFIRMED_BY_STATIC_DISASSEMBLY", "HYP-A status mismatch"
    assert hyp_a.get("descriptor_struct", {}).get("stride_bytes") == 16, "Struct size must be 16 bytes"
    
    slot1_a = hyp_a.get("slot_computations", {}).get("slot_1_player", {})
    assert slot1_a.get("descriptor_offset_hex") == "+0x010", "Slot 1 offset mismatch"
    assert slot1_a.get("historical_count") == 3390, "Slot 1 count mismatch"
    assert slot1_a.get("element_stride_bytes") == 1264, "Slot 1 stride mismatch"
    assert slot1_a.get("historical_buffer_bytes") == 4284960, "Slot 1 buffer size mismatch"
    
    slot24_a = hyp_a.get("slot_computations", {}).get("slot_24_player_stats", {})
    assert slot24_a.get("descriptor_offset_hex") == "+0x180", "Slot 24 offset mismatch"
    assert slot24_a.get("historical_count") == 9773, "Slot 24 count mismatch"
    assert slot24_a.get("element_stride_bytes") == 48, "Slot 24 stride mismatch"
    assert slot24_a.get("historical_buffer_bytes") == 469104, "Slot 24 buffer size mismatch"
    
    hyp_b = hypotheses["HYP-B-LEGACY-CALIBRATION-ARTIFACT"]
    assert hyp_b.get("status") == "REFUTED_HISTORICAL_ARTIFACT", "HYP-B status mismatch"
    assert hyp_b.get("shift_derivation", {}).get("root_difference_bytes") == -8, "Shift must be -8 bytes"
    
    assert data.get("conclusion", {}).get("canonical_hypothesis") == "HYP-A-NATIVE-DISASSEMBLY", "Canonical must be HYP-A"
    
    print("PASS: DESCRIPTORS_HYPOTHESES_CHECK")
    return True

def check_native_object_delta():
    delta_path = RESEARCH_DIR / "native_object_delta.json"
    if not delta_path.is_file():
        print(f"FAIL: Missing {delta_path}")
        return False
    with open(delta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    mgr = data.get("target_manager", {})
    assert mgr.get("object_name") == "ROSTERDATA", "Manager object mismatch"
    assert mgr.get("static_module_rva") == "NBA2K22.exe+0x06347720", "RVA mismatch"
    assert mgr.get("retrieval_function_rva") == "0x11D5DE0", "Getter RVA mismatch"
    assert mgr.get("total_slots") == 75, "Total slots must be 75"
    assert mgr.get("descriptor_stride_bytes") == 16, "Descriptor stride must be 16 bytes"
    assert mgr.get("live_runtime_state", {}).get("game_build_hash") is None, "Live hash must be null"
    assert mgr.get("live_runtime_state", {}).get("live_base_address") is None, "Live base must be null"
    
    descriptors = {d["slot_index"]: d for d in data.get("calibrated_descriptors", [])}
    assert set(descriptors.keys()) == {1, 24}, "Exactly slots 1 and 24 must be calibrated in R00-01"
    
    d1 = descriptors[1]
    assert d1.get("record_name") == "PLAYER", "Slot 1 name mismatch"
    assert d1.get("offsets", {}).get("canonical_manager_offset_hex") == "+0x010", "Slot 1 canonical offset mismatch"
    assert d1.get("dimensions", {}).get("historical_count") == 3390, "Slot 1 count mismatch"
    assert d1.get("dimensions", {}).get("stride_bytes") == 1264, "Slot 1 stride mismatch"
    assert "EMPIRICAL" in d1.get("dimensions", {}).get("stride_source", ""), "Slot 1 stride source must reflect empirical inference"
    assert d1.get("dimensions", {}).get("stride_maturity") == "EMPIRICALLY_INFERRED_PENDING_GETTER_ISOLATION", "Slot 1 maturity mismatch"
    assert d1.get("verification_axes", {}).get("RESEARCH_INDEXED") is True, "RESEARCH_INDEXED must be True"
    assert d1.get("verification_axes", {}).get("NATIVE_LAYOUT") is True, "NATIVE_LAYOUT must be True"
    assert d1.get("verification_axes", {}).get("FIXTURE_PASS") is False, "FIXTURE_PASS must be False"
    assert d1.get("verification_axes", {}).get("LIVE_UI_MATCH") is False, "LIVE_UI_MATCH must be False"
    
    d24 = descriptors[24]
    assert d24.get("record_name") == "PLAYER_STATS", "Slot 24 name mismatch"
    assert d24.get("offsets", {}).get("canonical_manager_offset_hex") == "+0x180", "Slot 24 canonical offset mismatch"
    assert d24.get("dimensions", {}).get("historical_count") == 9773, "Slot 24 count mismatch"
    assert d24.get("dimensions", {}).get("stride_bytes") == 48, "Slot 24 stride mismatch"
    assert "EMPIRICAL" in d24.get("dimensions", {}).get("stride_source", ""), "Slot 24 stride source must reflect empirical validation"
    assert d24.get("dimensions", {}).get("stride_maturity") == "EMPIRICALLY_VALIDATED_STATISTICAL_PARITY", "Slot 24 maturity mismatch"
    assert d24.get("verification_axes", {}).get("RESEARCH_INDEXED") is True, "RESEARCH_INDEXED must be True"
    assert d24.get("verification_axes", {}).get("NATIVE_LAYOUT") is True, "NATIVE_LAYOUT must be True"
    assert d24.get("verification_axes", {}).get("FIXTURE_PASS") is False, "FIXTURE_PASS must be False"
    assert d24.get("verification_axes", {}).get("LIVE_UI_MATCH") is False, "LIVE_UI_MATCH must be False"
    
    assert data.get("delta_summary", {}).get("calibrated_in_this_delta") == 2, "Delta calibrated count mismatch"
    assert data.get("delta_summary", {}).get("remaining_uncalibrated_slots") == 73, "Remaining count mismatch"
    
    print("PASS: NATIVE_OBJECT_DELTA_CHECK")
    return True

def check_unresolved_findings():
    unres_path = RESEARCH_DIR / "unresolved_findings.json"
    if not unres_path.is_file():
        print(f"FAIL: Missing {unres_path}")
        return False
    with open(unres_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    findings = {item["finding_id"]: item for item in data.get("unresolved_items", [])}
    for fid, item in findings.items():
        assert item.get("status") == "HOLD_UNKNOWN", f"Item {fid} status must be HOLD_UNKNOWN"
    
    assert "UNRES-01-LIVE-EXECUTABLE-AND-ASLR" in findings, "Missing UNRES-01"
    assert "UNRES-02-SAVE-IDENTITY-AND-DYNAMIC-COUNTS" in findings, "Missing UNRES-02"
    assert "UNRES-03-DYNAMIC-HEAP-LIFECYCLE-AND-EXPANSION" in findings, "Missing UNRES-03"
    assert "UNRES-04-REMAINING-SLOTS-UNCALIBRATED" in findings, "Missing UNRES-04"
    assert "UNRES-05-EXACT-GETTER-RVA-FOR-SLOTS-1-AND-24" in findings, "Missing UNRES-05"
    
    boundary = data.get("phase_b_live_probe_authorization_boundary", {}).get("strict_limits", {})
    assert boundary.get("target_manager_limit") == 1, "target_manager_limit must be 1"
    assert boundary.get("allowed_slots") == [1, 24], "allowed_slots must be [1, 24]"
    assert boundary.get("max_sample_records_per_slot") <= 2, "max sample records <= 2"
    assert boundary.get("max_investigation_time_minutes") <= 20, "max time <= 20 min"
    
    print("PASS: UNRESOLVED_FINDINGS_CHECK")
    return True

def check_scope_and_prohibitions():
    task_packet_path = RUN_DIR / "task_packet.yml"
    if not task_packet_path.is_file():
        print(f"FAIL: Missing {task_packet_path}")
        return False
    with open(task_packet_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "task_id: NATIVE-ATLAS-R00-01" in content, "task_id missing in task_packet"
    assert "exact_base_sha: 97fe60de5b30d0e3ccf9af8f45f051e20dc2140a" in content, "base sha mismatch"
    assert "live_game_process_read_or_write" in content, "Prohibition missing"
    assert "dereference_historical_heap_pointers" in content, "Prohibition missing"
    
    print("PASS: SCOPE_AND_PROHIBITIONS_CHECK")
    return True

CHECKS = {
    "SOURCE_MANIFEST_CHECK": check_source_manifest,
    "DESCRIPTORS_HYPOTHESES_CHECK": check_descriptor_hypotheses,
    "NATIVE_OBJECT_DELTA_CHECK": check_native_object_delta,
    "UNRESOLVED_FINDINGS_CHECK": check_unresolved_findings,
    "SCOPE_AND_PROHIBITIONS_CHECK": check_scope_and_prohibitions,
}

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target not in CHECKS:
            print(f"Unknown check: {target}. Available: {list(CHECKS.keys())}")
            sys.exit(2)
        success = CHECKS[target]()
        sys.exit(0 if success else 1)
    else:
        all_passed = True
        for name, fn in CHECKS.items():
            if not fn():
                all_passed = False
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
