"""Independent source-equivalent reproduction for ee515e0b.
Not the developer's actual 14 pytest or live game access. All files are temporary.
Transcribed critical flow of live_analyzer.py::remediate_all_field_records.
Run: python non_idempotent_remediation_probe.py
"""
import json
import struct
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    record_path = Path(tmp) / "WORLD_REG_002.json"
    ledger = Path(tmp) / "iteration_ledger.jsonl"
    record_path.write_text(json.dumps({
        "live_evidence": {
            "live_value": 1056964608,
            "read_address": "0x7ff4e68fe038",
            "read_timestamp": "2026-10-31T03:31:03.580403+00:00",
            "read_notes": "Read from original live slot"
        }
    }), encoding="utf-8")

    def remediate_once():
        rec = json.loads(record_path.read_text(encoding="utf-8"))
        old = rec.get("live_evidence", {})
        rec["raw_legacy_capture"] = {
            "legacy_value": old.get("live_value"),
            "legacy_address": old.get("read_address", "UNKNOWN"),
            "legacy_timestamp": old.get("read_timestamp", ""),
            "legacy_notes": old.get("read_notes", "")
        }
        value = old.get("live_value")
        if isinstance(value, int) and value > 1000:
            value = round(struct.unpack("<f", struct.pack("<I", value))[0], 4)
        rec["live_evidence"] = {
            "live_value": value,
            "read_address": old.get("read_address"),
            "read_notes": "Observation reinterpreted"
            # Original read_timestamp omitted in the source remediation
        }
        record_path.write_text(json.dumps(rec), encoding="utf-8")
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"operation": "FORENSIC_REMEDIATION_SWEEP"}) + "\n")
        return rec

    first = remediate_once()
    second = remediate_once()
    assert first["raw_legacy_capture"]["legacy_value"] == 1056964608
    assert second["raw_legacy_capture"]["legacy_value"] == 0.5
    assert first["raw_legacy_capture"]["legacy_timestamp"] != ""
    assert second["raw_legacy_capture"]["legacy_timestamp"] == ""
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 2
    print("PASS: second remediation overwrote raw legacy value and original capture time")
    print("PASS: repeated remediation adds another ledger entry")
