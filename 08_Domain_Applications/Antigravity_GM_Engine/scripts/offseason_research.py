"""P0 local archive inventory only; no capture, publication, or game writes."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from offseason_research import inventory, output_directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-save-id", required=True,
                        help="Existing archived dataset ID, not proof of the loaded game save")
    parser.add_argument("--output", required=True, help="New local directory below _exports")
    args = parser.parse_args()
    report = inventory(ROOT, args.archive_save_id)
    output = output_directory(ROOT, args.output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "P0_INVENTORY.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output),
                      "blockers": report["blockers"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
