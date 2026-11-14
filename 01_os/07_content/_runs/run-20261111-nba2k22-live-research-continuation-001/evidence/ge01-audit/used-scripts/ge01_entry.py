"""Execute only the Human-approved seven-game entry through the existing calendar CLI."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[5]
NATIVE = REPO / "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"
sys.path.insert(0, str(NATIVE / "tools/test_only_calendar"))
import calendar_cli as calendar

ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")


def main():
    approval = calendar.load(ROOT / "HUMAN_APPROVAL.json")
    assert approval["approved"] is True and approval["qualification_reuse_accepted"] is True
    assert calendar.sha_file(ROOT / "GE01_W01_REVIEW_ENVELOPE.json") == approval["approved_proposal_sha256"]
    plans = calendar.load(ROOT / "GE01_NATIVE_CALENDAR_PLANS.json")
    plan = plans[0]
    assert plan["entry_transition"] and plan["entry_minutes"] == 1170
    assert [row["id"] for row in plan["games"] if row["day"] < plan["stop_exclusive"]] == list(range(203, 210))
    started = ROOT / "ENTRY_STARTED.json"
    with started.open("x", encoding="utf-8") as stream:
        json.dump({"approval_sha256": calendar.sha_file(ROOT / "HUMAN_APPROVAL.json"),
                   "plan_digest": calendar.digest(plan), "maximum_dispatches": 1}, stream)
    now = datetime.now(timezone.utc)
    grant = {"action": calendar.ACTION, "plan_digest": calendar.digest(plan),
             "authorization_scope": plan["authorization_scope"], "max_dispatches": 1,
             "approved_by_operator": True, "human_decision_ref": "Current Human approved GE01 envelope " + approval["approved_proposal_sha256"],
             "revoked": False, "valid_from": now.isoformat(), "expires_at": (now + timedelta(hours=2)).isoformat()}
    grant_path = ROOT / "ENTRY_APPROVAL.json"
    with grant_path.open("x", encoding="utf-8") as stream:
        json.dump(grant, stream, indent=2)
    args = SimpleNamespace(runtime=ROOT / "entry-native", node=None, rea=None, outbox=Path(plan["outbox_db"]),
                           execute_once=True, approval=grant_path, approved_sha=calendar.sha_file(grant_path))
    print("Dispatching the approved seven-game entry once via the existing Calendar primitive", flush=True)
    result = calendar.simulate_to_native_date(args, plan)
    with (ROOT / "ENTRY_RESULT.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result), flush=True)
    return result["status"] != "VERIFIED_IN_MEMORY"


if __name__ == "__main__":
    raise SystemExit(main())
