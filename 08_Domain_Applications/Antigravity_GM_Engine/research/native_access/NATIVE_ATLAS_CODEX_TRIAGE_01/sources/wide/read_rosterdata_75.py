#!/usr/bin/env python3
"""
Live ROSTERDATA 75-Slot Directory Reader & Audit Logger.
Reads all 75 descriptors (1,200 bytes) from live NBA2K22.exe process in read-only mode,
verifies pointer readability for active slots, and records an exact audit trail of all reads.
"""

import sys
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_DIR = Path(__file__).resolve().parents[3] / "src"
HISTORICAL_FIXTURE = Path(__file__).resolve().parents[3] / "research" / "native_access" / "AG_NATIVE_01B" / "fixtures" / "sample_descriptors.json"
OUTPUT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(SRC_DIR))
from memory import GameMemory

def run_extraction():
    audit_calls = []
    
    def log_read(addr, size, target, success, data_preview=None):
        audit_calls.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "address_hex": f"0x{addr:X}",
            "size_bytes": size,
            "target": target,
            "success": bool(success),
            "data_preview_hex": data_preview.hex() if data_preview else None
        })

    with open(HISTORICAL_FIXTURE, "r", encoding="utf-8") as f:
        hist_data = json.load(f)
    hist_slots = {d["slot_index"]: d for d in hist_data["descriptors"]}

    results = []

    with GameMemory(read_only=True) as mem:
        pid = mem.pid
        base_addr = mem.base_address
        
        # 1. Read static pointer g_pRosterData at NBA2K22.exe+0x06347720
        manager_ptr_addr = base_addr + 0x06347720
        raw_ptr = mem.read_bytes(manager_ptr_addr, 8)
        log_read(manager_ptr_addr, 8, "static_g_pRosterData_pointer", raw_ptr is not None, raw_ptr)
        
        assert raw_ptr is not None, "Failed to read g_pRosterData pointer"
        import struct
        roster_mgr_addr = struct.unpack("<Q", raw_ptr)[0]
        
        # 2. Read all 75 descriptors table (75 * 16 = 1200 bytes)
        raw_table = mem.read_bytes(roster_mgr_addr, 1200)
        log_read(roster_mgr_addr, 1200, "rosterdata_75_descriptors_table", raw_table is not None, raw_table[:32] if raw_table else None)
        assert raw_table is not None, "Failed to read 1200 bytes descriptor table"

        # 3. Parse each slot
        for i in range(75):
            slot_offset = i * 16
            slot_raw = raw_table[slot_offset:slot_offset + 16]
            count, pdata = struct.unpack("<QQ", slot_raw)
            
            hist = hist_slots.get(i, {})
            hist_name = hist.get("object_name", "UNKNOWN")
            hist_family = hist.get("family", "UNKNOWN")
            hist_stride = hist.get("inferred_stride", None)
            hist_getter = hist.get("getter_rva", None)
            
            readable = False
            first_4_bytes_hex = None
            last_byte_readable = False
            
            if count > 0 and pdata != 0:
                # Minimal probe: read first 4 bytes to verify address readability
                try:
                    probe_head = mem.read_bytes(pdata, 4)
                    readable = probe_head is not None
                    if probe_head:
                        first_4_bytes_hex = probe_head.hex()
                    log_read(pdata, 4, f"slot_{i}_head_probe", readable, probe_head)
                except Exception as e:
                    print(f"Slot {i} head probe failed: {e}")
                
                # Check last byte if stride is known
                if hist_stride and count > 0:
                    try:
                        stride_int = int(hist_stride)
                        tail_addr = int(pdata + (count * stride_int) - 1)
                        if 0 <= tail_addr < 0x7FFFFFFFFFFFFFFF:
                            probe_tail = mem.read_bytes(tail_addr, 1)
                            last_byte_readable = probe_tail is not None
                            log_read(tail_addr, 1, f"slot_{i}_tail_probe", last_byte_readable, probe_tail)
                        else:
                            print(f"Slot {i} tail address out of bounds: 0x{tail_addr:X}")
                    except Exception as e:
                        print(f"Slot {i} tail probe failed: {e}")
            
            status = "CONFIRMED_ACTIVE_READABLE" if (count > 0 and readable) else ("EMPTY_RESERVED" if count == 0 and pdata == 0 else "ANOMALOUS_COUNT_OR_NULL")
            
            results.append({
                "slot_index": i,
                "descriptor_offset_hex": f"+0x{slot_offset:03X}",
                "descriptor_offset_dec": slot_offset,
                "live_count": count,
                "live_pdata_hex": f"0x{pdata:X}" if pdata else "NULL",
                "is_readable": readable,
                "first_4_bytes_hex": first_4_bytes_hex,
                "tail_byte_readable": last_byte_readable,
                "historical_count": hist.get("count", None),
                "historical_pointer_hex": hist.get("pointer_hex", None),
                "inferred_stride_bytes": hist_stride,
                "total_buffer_bytes": count * hist_stride if (hist_stride and count) else None,
                "historical_name": hist_name,
                "historical_family": hist_family,
                "native_getter_rva": hist_getter,
                "status": status
            })

    output_atlas = {
        "schema_version": "nba2k22.native_object_atlas_75.v1",
        "task_id": "NBA2K22-NATIVE-ATLAS-R00-WIDE-01",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "process_context": {
            "pid": pid,
            "base_address_hex": f"0x{base_addr:X}",
            "manager_pointer_address_hex": f"0x{manager_ptr_addr:X}",
            "manager_instance_address_hex": f"0x{roster_mgr_addr:X}"
        },
        "summary": {
            "total_slots": 75,
            "active_readable_slots": sum(1 for r in results if r["status"] == "CONFIRMED_ACTIVE_READABLE"),
            "empty_reserved_slots": sum(1 for r in results if r["status"] == "EMPTY_RESERVED"),
            "anomalous_slots": sum(1 for r in results if r["status"] == "ANOMALOUS_COUNT_OR_NULL")
        },
        "slots": results
    }

    atlas_path = OUTPUT_DIR / "native_object_atlas_75.json"
    with open(atlas_path, "w", encoding="utf-8") as f:
        json.dump(output_atlas, f, indent=2, ensure_ascii=False)
    print(f"Atlas written to {atlas_path}")

    audit_path = OUTPUT_DIR / "read_audit_log.json"
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump({
            "schema_version": "nba2k22.read_audit_log.v1",
            "task_id": "NBA2K22-NATIVE-ATLAS-R00-WIDE-01",
            "total_calls": len(audit_calls),
            "all_calls_successful": all(c["success"] for c in audit_calls),
            "read_only_enforced": True,
            "calls": audit_calls
        }, f, indent=2, ensure_ascii=False)
    print(f"Audit log written to {audit_path}")

if __name__ == "__main__":
    run_extraction()
