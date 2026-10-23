#!/usr/bin/env python3
"""
Verification script for NBA2K22-NATIVE-ATLAS-R00-01-LIVE01.
Validates live process memory inspection artifacts, Slot 1 and Slot 24 readings,
negative controls, and scope compliance.
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RESEARCH_DIR = REPO_ROOT / "08_Domain_Applications" / "Antigravity_GM_Engine" / "research" / "native_access" / "NATIVE_ATLAS_R00_01_LIVE01"
RUN_DIR = REPO_ROOT / "01_os" / "07_content" / "_runs" / "run-20261023-native-atlas-r00-01-live01"

def check_live_source_manifest():
    manifest_path = RESEARCH_DIR / "live_source_manifest.json"
    if not manifest_path.is_file():
        print(f"FAIL: Missing {manifest_path}")
        return False
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data.get("task_id") == "NBA2K22-NATIVE-ATLAS-R00-01-LIVE01", "task_id mismatch"
    assert data.get("target_object") == "ROSTERDATA", "target_object mismatch"
    
    proc = data.get("live_process_identity", {})
    assert proc.get("process_name") == "NBA2K22.exe", "process_name mismatch"
    assert proc.get("pid") == 1828, "PID mismatch"
    assert proc.get("module_base_address_hex") == "0x140000000", "module base mismatch"
    assert proc.get("executable_sha256") == "1727AD72085FBA39E789EE574FC15AAB623AD1651CF6879E95E8CD53B6FFBBF5", "hash mismatch"
    
    binding = data.get("static_rva_binding", {})
    assert binding.get("static_manager_rva") == "0x06347720", "static RVA mismatch"
    assert binding.get("effective_virtual_address_hex") == "0x146347720", "virtual address mismatch"
    assert binding.get("resolved_manager_instance_pointer_hex") == "0x7FF4E6DFB2F0", "manager ptr mismatch"
    
    safety = data.get("safety_guarantees", {})
    assert safety.get("read_only_enforced") is True, "read_only_enforced must be True"
    assert safety.get("memory_writes_performed") is False, "writes must be False"
    
    print("PASS: LIVE_SOURCE_MANIFEST_CHECK")
    return True

def check_live_descriptor_readings():
    readings_path = RESEARCH_DIR / "live_descriptor_readings.json"
    if not readings_path.is_file():
        print(f"FAIL: Missing {readings_path}")
        return False
    with open(readings_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    slots = {s["slot_index"]: s for s in data.get("slot_readings", [])}
    assert set(slots.keys()) == {1, 24}, "Exactly Slot 1 and 24 must be read"
    
    s1 = slots[1]
    assert s1.get("record_name") == "PLAYER", "Slot 1 name mismatch"
    assert s1.get("live_values", {}).get("count") == 3390, "Slot 1 count mismatch"
    assert s1.get("live_values", {}).get("pdata_hex") == "0x7FF4E6DFB7D8", "Slot 1 pdata mismatch"
    assert s1.get("live_values", {}).get("stride_bytes") == 1264, "Slot 1 stride mismatch"
    assert s1.get("boundary_checks", {}).get("boundary_pass") is True, "Slot 1 boundary check failed"
    assert len(s1.get("samples", [])) == 2, "Slot 1 must have exactly 2 samples"
    
    s24 = slots[24]
    assert s24.get("record_name") == "PLAYER_STATS", "Slot 24 name mismatch"
    assert s24.get("live_values", {}).get("count") == 9773, "Slot 24 count mismatch"
    assert s24.get("live_values", {}).get("pdata_hex") == "0x7FF4E74A7A3C", "Slot 24 pdata mismatch"
    assert s24.get("live_values", {}).get("stride_bytes") == 48, "Slot 24 stride mismatch"
    assert s24.get("boundary_checks", {}).get("boundary_pass") is True, "Slot 24 boundary check failed"
    assert len(s24.get("samples", [])) == 2, "Slot 24 must have exactly 2 samples"
    
    neg = data.get("live_negative_controls", {})
    assert "plus_8_misalignment_check" in neg, "Missing plus_8 check"
    assert "contiguous_endpointer_refutation_check" in neg, "Missing contiguous check"
    assert neg["contiguous_endpointer_refutation_check"]["measured_gap_bytes"] == 4, "Slot 9->10 gap must be 4"
    
    print("PASS: LIVE_DESCRIPTOR_READINGS_CHECK")
    return True

def check_live_object_delta():
    delta_path = RESEARCH_DIR / "live_object_delta.json"
    if not delta_path.is_file():
        print(f"FAIL: Missing {delta_path}")
        return False
    with open(delta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    mgr = data.get("target_manager", {})
    assert mgr.get("calibration_status") == "CALIBRATED_LIVE_READ_CONFIRMED", "Manager status mismatch"
    assert mgr.get("live_runtime_state", {}).get("pid") == 1828, "PID mismatch"
    assert mgr.get("live_runtime_state", {}).get("live_manager_instance") == "0x7FF4E6DFB2F0", "Instance mismatch"
    
    descriptors = {d["slot_index"]: d for d in data.get("calibrated_descriptors", [])}
    assert set(descriptors.keys()) == {1, 24}, "Descriptors must be Slot 1 and 24"
    
    d1 = descriptors[1]
    assert d1.get("calibration_status") == "CALIBRATED_LIVE_READ_CONFIRMED", "Slot 1 status mismatch"
    assert d1.get("verification_axes", {}).get("FIXTURE_PASS") is True, "FIXTURE_PASS must be True"
    assert d1.get("verification_axes", {}).get("LIVE_UI_MATCH") is False, "LIVE_UI_MATCH must be False"
    assert d1.get("offsets", {}).get("legacy_source_extensions_pdata_offset_hex") == "+0x020", "Slot 1 legacy pdata offset mismatch"
    
    d24 = descriptors[24]
    assert d24.get("calibration_status") == "CALIBRATED_LIVE_READ_CONFIRMED", "Slot 24 status mismatch"
    assert d24.get("verification_axes", {}).get("FIXTURE_PASS") is True, "FIXTURE_PASS must be True"
    assert d24.get("offsets", {}).get("legacy_source_extensions_pdata_offset_hex") == "+0x190", "Slot 24 legacy pdata offset mismatch"
    
    print("PASS: LIVE_OBJECT_DELTA_CHECK")
    return True

def check_live_unresolved_findings():
    unres_path = RESEARCH_DIR / "live_unresolved_findings.json"
    if not unres_path.is_file():
        print(f"FAIL: Missing {unres_path}")
        return False
    with open(unres_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    items = {item["finding_id"]: item for item in data.get("unresolved_items", [])}
    for fid, item in items.items():
        assert item.get("status") == "HOLD_UNKNOWN", f"Item {fid} must be HOLD_UNKNOWN"
    
    assert "LIVE-UNRES-01-CAREER-SAVE-BINDING" in items, "Missing LIVE-UNRES-01"
    assert "LIVE-UNRES-02-EXACT-GETTER-RVA-FOR-SLOTS-1-AND-24" in items, "Missing LIVE-UNRES-02"
    assert "LIVE-UNRES-03-DYNAMIC-HEAP-REALLOCATION" in items, "Missing LIVE-UNRES-03"
    assert "LIVE-UNRES-04-REMAINING-SLOTS-UNCALIBRATED" in items, "Missing LIVE-UNRES-04"
    
    print("PASS: LIVE_UNRESOLVED_FINDINGS_CHECK")
    return True

def check_scope_and_prohibitions():
    task_packet_path = RUN_DIR / "task_packet.yml"
    if not task_packet_path.is_file():
        print(f"FAIL: Missing {task_packet_path}")
        return False
    with open(task_packet_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "task_id: NBA2K22-NATIVE-ATLAS-R00-01-LIVE01" in content, "task_id mismatch"
    assert "exact_base_sha: 1d980be8f32642e8c177a6ad8e9b429beaa48647" in content, "base sha mismatch"
    assert "game_memory_write" in content, "Prohibition missing"
    assert "advance_game_or_simulate_season" in content, "Prohibition missing"
    
    print("PASS: SCOPE_AND_PROHIBITIONS_CHECK")
    return True

CHECKS = {
    "LIVE_SOURCE_MANIFEST_CHECK": check_live_source_manifest,
    "LIVE_DESCRIPTOR_READINGS_CHECK": check_live_descriptor_readings,
    "LIVE_OBJECT_DELTA_CHECK": check_live_object_delta,
    "LIVE_UNRESOLVED_FINDINGS_CHECK": check_live_unresolved_findings,
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
