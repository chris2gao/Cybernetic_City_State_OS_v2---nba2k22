"""Deterministic, read-only domain knowledge checks for OS managed verification.

Use from repository root. Does not touch game, SQLite, DCR, network, or Git index.
"""
import argparse
import json
from pathlib import Path

ROOT = Path("08_Domain_Applications/Antigravity_GM_Engine")
DOC = ROOT / "docs/development"

def load(name):
    return json.loads((DOC/name).read_text(encoding="utf-8"))

def plan_and_task_dag():
    b = load("NBA2K22_OS_TASK_BACKLOG_V1.json")
    tasks = b["tasks"]
    ids = [t["id"] for t in tasks]
    assert len(ids) == 16 and len(ids) == len(set(ids)), "Duplicate/missing planned IDs"
    remaining = {t["id"]: t for t in tasks}
    resolved = set()
    while remaining:
        ready = [k for k,v in remaining.items() if set(v["depends_on"]) <= resolved]
        assert ready, f"Broken cycle or missing dependency: {sorted(remaining)}"
        for k in ready:
            resolved.add(k)
            del remaining[k]
    assert b["rules"]["this_file_is_plan_not_authorization"] is True
    assert b["knowledge_base"]["status"].startswith("candidate_")
    print("PLAN_AND_TASK_DAG PASS 16 unique task nodes")

def ledger_evidence_links():
    l = load("PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json")
    h = load("NBA2K22_HISTORICAL_TASK_REGISTER_V1.json")
    source = json.loads((ROOT/"docs/development_reviews/FINAL_CODEX_CAPABILITY_MATRIX_20261021_V1.json").read_text(encoding="utf-8"))
    families = source["families"]
    assert len(families) == len(l["capabilities"]) == 40
    for i, (a, b) in enumerate(zip(families, l["capabilities"])):
        assert a["family_id"] == b["id"], (i, "family ID mismatch")
        assert a["audit_category"] == b["audit_category"], (i, "audit category mismatch")
        assert a["current_blocker"] == b["risk_or_blocker"], (i, "blocker mismatch")
    assert sum(l["counts"]["audit_status_distribution"].values()) == 40
    assert l["counts"]["inherited_gaps"] == 20
    for w in l["workstreams"]:
        assert w["source_paths"], w["id"]
        for path in w["source_paths"]:
            assert (ROOT/path).exists(), f"Missing workstream evidence: {path}"
    for group in h["groups"]:
        for path in group["artifact_paths"]:
            assert (ROOT/path).is_file(), f"Missing historical document: {path}"
    for group in h["ag_native_research"]:
        for path in group["key_docs"] + group["tests"]:
            assert (ROOT/path).is_file(), f"Missing native evidence: {path}"
    print("LEDGER_EVIDENCE_LINKS PASS 40 families / 20 gaps / source paths")

def doc_authority_links():
    names = [
        "NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md",
        "NBA2K22_PLANNING_MODEL_ENTRY_V1.md",
        "NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md",
        "OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md",
        "NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md",
        "NBA2K22_OS_TASK_BACKLOG_V1.json",
        "PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json",
        "NBA2K22_HISTORICAL_TASK_REGISTER_V1.json",
        "PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md",
    ]
    for name in names:
        assert (DOC/name).is_file(), f"Missing project authority document: {name}"
    readme = (ROOT/"README.md").read_text(encoding="utf-8")
    assert "NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md" in readme
    for name in names[:3]:
        assert name in readme or name in (DOC/"NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md").read_text(encoding="utf-8")
    baseline = (DOC/names[0]).read_text(encoding="utf-8")
    assert "01_os/" in baseline and "AG-NATIVE-01" in baseline
    assert (ROOT/"docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md").is_file()
    print("DOC_AUTHORITY_LINKS PASS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=["PLAN_AND_TASK_DAG","LEDGER_EVIDENCE_LINKS","DOC_AUTHORITY_LINKS"],required=True)
    args = parser.parse_args()
    {"PLAN_AND_TASK_DAG":plan_and_task_dag,
     "LEDGER_EVIDENCE_LINKS":ledger_evidence_links,
     "DOC_AUTHORITY_LINKS":doc_authority_links}[args.check]()
