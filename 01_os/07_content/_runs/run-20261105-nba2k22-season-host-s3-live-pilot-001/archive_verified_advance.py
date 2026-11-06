"""Archive a successful live advance and its actual source receipts."""
import argparse
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from initialize_pilot import ROOT, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cycle", choices=tuple(f"cycle-{number:03}" for number in range(1, 5)))
    parser.add_argument("--reverified", action="store_true")
    args = parser.parse_args()
    runtime = ROOT.parent / "s3-live-private"
    dest = Path(__file__).resolve().parent / "receipts"
    prefix = f"advance-after-{args.cycle}"
    selected = prefix + "-reverified" if args.reverified else prefix
    receipt_path = runtime / f"{selected}.json"
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["status"] == "VERIFIED_HUMAN_ADVANCE"
    assert receipt["native_unchanged_during_host_readback"] is True
    raw_path = Path(receipt["refresh_report_local"]).resolve()
    assert raw_path.is_relative_to((runtime / "world").resolve())
    assert sha(raw_path) == receipt["refresh_report_sha256"]
    report = json.loads(raw_path.read_bytes())
    assert report["batch_id"] == receipt["refresh_batch_id"]
    assert report["status"] == "COMPLETED_REQUESTED_SOURCES"
    rows = [
        {"family": item["family"], "status": item["status"], "counts": item.get("counts", {}),
         "commit_status": item["commit_status"], "unit": item["unit"],
         "wall_seconds": (datetime.fromisoformat(item["finished_at"]) -
                          datetime.fromisoformat(item["started_at"])).total_seconds()}
        for item in report["sources"]
    ]
    summary = {
        "batch_id": report["batch_id"], "wall_seconds": (datetime.fromisoformat(report["finished_at"]) -
                                                         datetime.fromisoformat(report["started_at"])).total_seconds(),
        "source_status_counts": dict(Counter(row["status"] for row in rows)), "sources": rows,
        "raw_report_sha256": sha(raw_path), "new_final_games": len(receipt["native_new_final_ids"]),
        "native_game_writes_by_host": 0,
    }
    for name_prefix in {prefix, selected}:
        for suffix in (".json", ".stdout.log", ".stderr.log"):
            name = name_prefix + suffix
            shutil.copyfile(runtime / name, dest / name)
    (dest / f"{prefix}-sources.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "sources"}))


if __name__ == "__main__":
    main()
