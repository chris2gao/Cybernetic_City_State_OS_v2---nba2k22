"""Read-only, no-external-dependency checks for NBA2K22 OS roadmap candidate.

Run only from repository root in managed verification. No game, local save,
credential or DCR access is needed. Exits nonzero on mismatch.
"""
import argparse
import json
from pathlib import Path

RUN = Path("01_os/07_content/_runs/run-20261022-nba2k22-os-onboarding-001")
BUSINESS = Path("08_Domain_Applications/Antigravity_GM_Engine/docs/development")
ROADMAP = BUSINESS / "OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md"
BACKLOG = BUSINESS / "NBA2K22_OS_TASK_BACKLOG_V1.json"
TEMPLATE = BUSINESS / "NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md"
PACKET = RUN / "任务包.yml"
PLAN = RUN / "verification_plan.json"

def check_docs_and_scope():
    for path in (ROADMAP, BACKLOG, TEMPLATE, PACKET, PLAN):
        if not path.is_file():
            raise AssertionError(f"Missing tracked candidate artifact: {path}")
    r = ROADMAP.read_text(encoding="utf-8")
    if "OS-BASELINE-01" not in r or "WORLD-DATA-ARCH-01" not in r:
        raise AssertionError("Roadmap lacks entry or first architecture task")
    packet = PACKET.read_text(encoding="utf-8")
    for p in (ROADMAP, BACKLOG, TEMPLATE):
        if str(p) not in packet:
            raise AssertionError(f"Unlisted path in allowed_changed_paths: {p}")

def check_backlog_dag():
    data = json.loads(BACKLOG.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    ids = [x["id"] for x in tasks]
    if len(set(ids)) != len(ids):
        raise AssertionError("Duplicate task ID")
    pending = set(ids)
    available = set()
    while pending:
        ready = [t for t in tasks if t["id"] in pending and all(d in available for d in t["depends_on"])]
        if not ready:
            raise AssertionError("Missing dependency or cycle: " + ", ".join(sorted(pending)))
        for task in ready:
            available.add(task["id"])
            pending.remove(task["id"])
    if data["rules"]["this_file_is_plan_not_authorization"] is not True:
        raise AssertionError("Backlog mistakenly confers execution authority")

def check_doc_crossref():
    md = ROADMAP.read_text(encoding="utf-8")
    tmp = TEMPLATE.read_text(encoding="utf-8")
    data = json.loads(BACKLOG.read_text(encoding="utf-8"))
    critical = ["OS-BASELINE-01","WORLD-DATA-ARCH-01","NATIVE-ACCEPT-01",
                "WORLD-DATA-SCHEMA-01","WORLD-DATA-INGEST-01",
                "WORLD-DATA-PUBLISH-01","WORLD-DATA-QUERY-01",
                "WORLD-DATA-MIGRATION-01","WORLD-ACTOR-DATA-01"]
    for value in critical:
        if value not in md or value not in [x["id"] for x in data["tasks"]]:
            raise AssertionError(f"Missing critical task from roadmap: {value}")
    if "DCR" not in tmp or "completion pointer" not in tmp:
        raise AssertionError("No local access/OS handoff guidance")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=["DOCS_AND_SCOPE", "BACKLOG_DAG", "DOC_CROSSREF"], required=True)
    args = parser.parse_args()
    {"DOCS_AND_SCOPE":check_docs_and_scope,"BACKLOG_DAG":check_backlog_dag,
     "DOC_CROSSREF":check_doc_crossref}[args.check]()
    print(args.check, "PASS")
