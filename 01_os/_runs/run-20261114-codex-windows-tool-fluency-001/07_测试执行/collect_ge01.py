"""Extract only diagnostic cases from the exact public stopped GE-01 archive."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "01_os/06_execution/boot/context_management/prms"))
from source import GitSource


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nba-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = GitSource(args.nba_root, "99938b46e47c7ded9a8ba317fef6a7849342a171",
                       "chris2gao/Cybernetic_City_State_OS_v2---nba2k22")
    run = "01_os/07_content/_runs/run-20261111-nba2k22-live-research-continuation-001/"
    evidence = run + "evidence/ge01-audit/"
    validation = json.loads(source.read(evidence + "entry-native/"
                            "37373e0605674e0b9d1150085d83b989/evidence.json")[0])
    repair = evidence + "entry-repair-01-native/bc70f7bfe40140fbb484208589f259b9/"
    observation = json.loads(source.read(repair + "evidence.json")[0])["normalized_result"]
    program = source.read(repair + "program.js")[0].decode("utf-8-sig")
    audit = source.read(run + "GE01_EXECUTION_AUDIT.md")[0].decode("utf-8-sig")
    assert "durationMs" in audit and "Schedule fixture differs" in audit
    assert program.index("verifyWindow(false);") < program.index("invoke(17, payload)")
    result = {
        "source_refs": source.reads,
        "validation_error": validation,
        "fixture_error": {
            "description": observation["messages"][0]["description"],
            "line_number": observation["messages"][0]["line_number"],
            "cleanup_error": observation["cleanup_error"],
            "pre_dispatch_check_precedes_invoke": True,
            "observed_row_values": "NOT_RECORDED",
            "comparison_fields_from_source": ["id", "duplicate_id", "day", "home", "away"],
        },
        "audit_statistics": {
            "basis": "executor audit assertions, not independent replay",
            "first_attempt_seconds": 5152.458,
            "outer_tool_calls_before_first_attempt": 51,
            "calendar_dispatches": 0,
        },
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"diagnostic_sources": len(source.reads), "output": args.output.name}))


if __name__ == "__main__":
    main()
