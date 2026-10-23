#!/usr/bin/env python3
"""
Verification script for NBA2K22-NATIVE-ATLAS-R00-WIDE-01.
Validates the 75-slot ROSTERDATA discovery atlas, Player/GM/Coach ingredient coverage matrix,
Codex breakthrough packets, priority queue, read audit log, and scope constraints.
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RESEARCH_DIR = REPO_ROOT / "08_Domain_Applications" / "Antigravity_GM_Engine" / "research" / "native_access" / "NATIVE_ATLAS_R00_WIDE_01"
RUN_DIR = REPO_ROOT / "01_os" / "07_content" / "_runs" / "run-20261023-native-atlas-r00-wide-01"

def check_atlas_75():
    atlas_path = RESEARCH_DIR / "native_object_atlas_75.json"
    if not atlas_path.is_file():
        print(f"FAIL: Missing {atlas_path}")
        return False
    with open(atlas_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data.get("task_id") == "NBA2K22-NATIVE-ATLAS-R00-WIDE-01", "task_id mismatch"
    summary = data.get("summary", {})
    assert summary.get("total_slots") == 75, f"total_slots must be 75, got {summary.get('total_slots')}"
    assert summary.get("active_readable_slots") == 67, f"active_readable_slots must be 67, got {summary.get('active_readable_slots')}"
    assert summary.get("empty_reserved_slots") == 8, f"empty_reserved_slots must be 8, got {summary.get('empty_reserved_slots')}"
    assert summary.get("anomalous_slots") == 0, f"anomalous_slots must be 0, got {summary.get('anomalous_slots')}"
    
    slots = data.get("slots", [])
    assert len(slots) == 75, f"slots array must have 75 items, got {len(slots)}"
    
    for s in slots:
        assert "role_domains" in s, f"Slot {s['slot_index']} missing role_domains"
        assert "confidence_maturity" in s, f"Slot {s['slot_index']} missing confidence_maturity"
        assert "temporal_or_identity_relation" in s, f"Slot {s['slot_index']} missing temporal_or_identity_relation"
        assert "open_reverse_engineering_questions" in s, f"Slot {s['slot_index']} missing open_reverse_engineering_questions"
    
    print("PASS: ATLAS_75_CHECK")
    return True

def check_ingredient_matrix():
    matrix_path = RESEARCH_DIR / "native_ingredient_matrix.json"
    if not matrix_path.is_file():
        print(f"FAIL: Missing {matrix_path}")
        return False
    with open(matrix_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    domains = data.get("domains", {})
    required_domains = {"PLAYER", "GM", "COACH"}
    missing_domains = required_domains - set(domains.keys())
    assert not missing_domains, f"Missing domains: {missing_domains}"
    
    tier_keys = [
        "tier_1_discovered_and_certified",
        "tier_2_discovered_uncertified_decoding",
        "tier_3_historical_research_clue_only",
        "tier_4_native_source_unknown",
        "tier_5_requires_cross_object_join",
        "tier_6_non_existent_or_unproven_in_game"
    ]
    for dom_name, dom_data in domains.items():
        for tk in tier_keys:
            assert tk in dom_data, f"Domain {dom_name} missing {tk}"
            assert isinstance(dom_data[tk], list), f"{dom_name}.{tk} must be a list"
            assert len(dom_data[tk]) > 0, f"{dom_name}.{tk} must not be empty"
    
    print("PASS: INGREDIENT_MATRIX_CHECK")
    return True

def check_codex_packets_and_queue():
    packets_path = RESEARCH_DIR / "codex_breakthrough_packets.json"
    if not packets_path.is_file():
        print(f"FAIL: Missing {packets_path}")
        return False
    with open(packets_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    packets = data.get("packets", [])
    assert len(packets) >= 4, f"Expected at least 4 packets, got {len(packets)}"
    for pkt in packets:
        assert "packet_id" in pkt, "Packet missing packet_id"
        assert "core_problem" in pkt, "Packet missing core_problem"
        assert "disassembly_anchor" in pkt, "Packet missing disassembly_anchor"
        assert "expected_decoded_shape" in pkt, "Packet missing expected_decoded_shape"
        assert "verification_method" in pkt, "Packet missing verification_method"
    
    queue_path = RESEARCH_DIR / "priority_research_queue.json"
    if not queue_path.is_file():
        print(f"FAIL: Missing {queue_path}")
        return False
    with open(queue_path, "r", encoding="utf-8") as f:
        q_data = json.load(f)
    
    q_items = q_data.get("queue_items", [])
    assert len(q_items) >= 5, f"Expected at least 5 queue items, got {len(q_items)}"
    ranks = [item["priority_rank"] for item in q_items]
    assert ranks == list(range(1, len(q_items) + 1)), "Priority ranks must be consecutive starting from 1"
    
    print("PASS: CODEX_PACKETS_AND_QUEUE_CHECK")
    return True

def check_read_audit_log():
    audit_path = RESEARCH_DIR / "read_audit_log.json"
    if not audit_path.is_file():
        print(f"FAIL: Missing {audit_path}")
        return False
    with open(audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data.get("read_only_enforced") is True, "read_only_enforced must be True"
    assert data.get("all_calls_successful") is True, "all_calls_successful must be True"
    assert data.get("total_calls", 0) >= 75, f"total_calls must be >= 75, got {data.get('total_calls')}"
    assert len(data.get("calls", [])) == data.get("total_calls"), "calls array length mismatch"
    
    print("PASS: READ_AUDIT_LOG_CHECK")
    return True

def check_scope_and_prohibitions():
    task_packet_path = RUN_DIR / "task_packet.yml"
    if not task_packet_path.is_file():
        print(f"FAIL: Missing {task_packet_path}")
        return False
    with open(task_packet_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "task_id: NBA2K22-NATIVE-ATLAS-R00-WIDE-01" in content, "task_id missing"
    assert "exact_base_sha: 7d84614710d9855d3ffd683da1cdb6fc896ebcf1" in content, "base sha mismatch"
    assert "game_memory_write" in content, "Prohibition missing"
    assert "game_save_write_or_edit" in content, "Prohibition missing"
    
    # Check that documentation deliverables exist and are nonempty
    discovery_map = RESEARCH_DIR / "object_discovery_map.md"
    assert discovery_map.is_file() and discovery_map.stat().st_size > 1000, "object_discovery_map.md missing or too small"
    
    roadmap = RESEARCH_DIR / "decoder_and_collector_roadmap.md"
    assert roadmap.is_file() and roadmap.stat().st_size > 1000, "decoder_and_collector_roadmap.md missing or too small"
    
    print("PASS: SCOPE_AND_PROHIBITIONS_CHECK")
    return True

CHECKS = {
    "ATLAS_75_CHECK": check_atlas_75,
    "INGREDIENT_MATRIX_CHECK": check_ingredient_matrix,
    "CODEX_PACKETS_AND_QUEUE_CHECK": check_codex_packets_and_queue,
    "READ_AUDIT_LOG_CHECK": check_read_audit_log,
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
