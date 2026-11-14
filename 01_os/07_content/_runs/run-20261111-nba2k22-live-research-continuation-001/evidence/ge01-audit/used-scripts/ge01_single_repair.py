"""The single repair/retrial explicitly allowed by Human: duration 120000 -> 60000."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[5]
NATIVE = REPO / "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"
sys.path.insert(0, str(NATIVE / "tools/test_only_calendar"))
import calendar_cli as calendar
from decision_outbox import DecisionOutbox

ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")


def write(name, value):
    with (ROOT / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def main():
    approval = calendar.load(ROOT / "HUMAN_APPROVAL.json")
    assert approval["approved"] and calendar.sha_file(ROOT / "GE01_W01_REVIEW_ENVELOPE.json") == approval["approved_proposal_sha256"]
    prior = calendar.load(ROOT / "ENTRY_RESULT.json")
    original = calendar.load(ROOT / "GE01_NATIVE_CALENDAR_PLANS.json")[0]
    assert prior["status"] == "UNKNOWN_NO_REPLAY" and prior["plan_digest"] == calendar.digest(original)
    native = Path(prior["private_receipt"])
    failure = calendar.load(native / "evidence.json")
    assert failure["code"] == "VALIDATION_ERROR" and failure["fieldErrors"][0]["path"] == "durationMs"
    assert "60000" in failure["fieldErrors"][0]["message"] and "evidence_id" not in failure
    probe = calendar.load(ROOT / "ENTRY_RECONCILIATION_TODAY.json")["structuredContent"]
    today, = [item["payload"] for item in probe["normalized_result"]["messages"] if item["type"] == "send"]
    assert today["raw"] == original["today_raw"] and today["pid"] == original["epoch"]["pid"]
    write("REPAIR_01_STARTED.json", {"maximum_repair_attempts": 1,
          "human_instruction": "只修复一次，如果没解决就停止任务，并记录当前任务从开始阶段的执行",
          "started_at": datetime.now(timezone.utc).isoformat(), "change": "observation_ms:120000->60000"})
    proof = {"disposition": "VALIDATION_REJECTED_BEFORE_INSTRUMENTATION_NO_CALENDAR_EFFECT",
             "original_plan_digest": calendar.digest(original), "raw_error_sha256": calendar.sha_file(native / "evidence.json"),
             "native_today_evidence": probe["evidence_id"], "human_observation": "没发生日历模拟",
             "native_dispatches": 0, "original_unknown_receipt_retained": str(native)}
    write("ENTRY_NO_EFFECT_PROOF.json", proof)
    row = DecisionOutbox.inspect_test_calendar(original["outbox_db"], calendar.digest(original))
    assert row["status"] == "UNKNOWN" and Path(row["receipt_ref"]).resolve() == native.resolve()
    outbox = DecisionOutbox(original["outbox_db"])
    outbox.record_test_calendar_no_effect(calendar.digest(original), row["receipt_ref"],
                                        str(ROOT / "ENTRY_NO_EFFECT_PROOF.json") + "#" + calendar.sha_file(ROOT / "ENTRY_NO_EFFECT_PROOF.json"))
    repaired = original | {"observation_ms": 60000}
    assert {key for key in repaired if repaired[key] != original[key]} == {"observation_ms"}
    calendar.validate_plan(repaired)
    write("ENTRY_REPAIRED_PLAN.json", repaired)
    now = datetime.now(timezone.utc)
    grant = {"action": calendar.ACTION, "plan_digest": calendar.digest(repaired),
             "authorization_scope": repaired["authorization_scope"], "max_dispatches": 1,
             "approved_by_operator": True, "human_decision_ref": "Current Human approved GE01 envelope and exactly one duration repair/retrial",
             "revoked": False, "valid_from": now.isoformat(), "expires_at": (now + timedelta(hours=2)).isoformat()}
    write("ENTRY_REPAIR_APPROVAL.json", grant)
    args = SimpleNamespace(runtime=ROOT / "entry-repair-01-native", node=None, rea=None,
                           outbox=Path(repaired["outbox_db"]), execute_once=True,
                           approval=ROOT / "ENTRY_REPAIR_APPROVAL.json", approved_sha=calendar.sha_file(ROOT / "ENTRY_REPAIR_APPROVAL.json"))
    print("Single allowed retry: same exact entry business scope, observation_ms=60000", flush=True)
    try:
        result = calendar.simulate_to_native_date(args, repaired)
    except Exception as error:
        result = {"status": "STOPPED_REPAIR_NOT_RESOLVED", "error_type": type(error).__name__, "reason": str(error)}
    result["repair_attempts"] = 1
    result["no_further_repairs_authorized"] = True
    write("REPAIR_01_RESULT.json", result)
    print(json.dumps(result), flush=True)
    return result["status"] != "VERIFIED_IN_MEMORY"


if __name__ == "__main__":
    raise SystemExit(main())
