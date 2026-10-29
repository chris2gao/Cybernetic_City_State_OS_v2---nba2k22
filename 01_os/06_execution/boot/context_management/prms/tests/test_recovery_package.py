from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError
from catalog import discover_g1
from context import plan_context, human_choice, assemble_context
from recovery import create_recovery_package, verify_window_recovery
from test_state import setup, apply

ROOT = Path(__file__).resolve().parents[6]
BASE = "446ca66ad48831f5fcdb1af18f37d07619e048c4"


def test_window_package_recovers_current_task_and_detects_drift(setup):
    store, gate, caller, _ = setup
    apply(store, gate, caller, "assignment", "ASSIGN", {"assignment_id": "task", "task_id": "PRMS",
                                                       "human_authority_ref": "fixture Human instruction"})
    apply(store, gate, caller, "decision", "APPEND", {"event_id": "decision", "task_id": "PRMS",
          "kind": "HUMAN_DECISION", "text": "Q52=B", "source_refs": [{"repository": "fixture/source", "commit": "a" * 40, "path": "Human.md"}]})
    apply(store, gate, caller, "checkpoint", "CHECKPOINT", {"task_id": "PRMS", "open_items": ["review"]})
    source = GitSource(ROOT, BASE, "chris2gao/Cybernetic_City_State_OS_v2---core")
    plan = plan_context(source, discover_g1(source), session_id="new-window", role="engineer", task_id="PRMS")
    choice = human_choice(plan, session_id="new-window", selected_paths=[], decision_source="fixture Human request")
    history = {"session_id": "new-window", "selected_event_ids": [], "decision_source": "fixture no optional history"}
    package = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                      history_choice=history, budget_bytes=1_000_000)
    assert package["status"] == "READY"
    assert package["selected_events"][0]["event"]["text"] == "Q52=B"
    assert package["role_current"]["checkpoint"]["state"]["open_items"] == ["review"]
    verify_window_recovery(gate, source, package, core_plan=plan, core_choice=choice, history_choice=history)
    base_used = assemble_context(source, plan, choice, budget_bytes=1_000_000)["used_bytes"]
    limited = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                      history_choice=history, budget_bytes=base_used)
    assert limited["status"] == "BLOCKED" and limited["excluded_events"]
    apply(store, gate, caller, "new-event", "APPEND", {"event_id": "new", "task_id": "PRMS",
          "kind": "MODEL_INFERENCE", "text": "new hypothesis", "source_refs": [{"repository": "fixture/source", "commit": "a" * 40, "path": "source.md"}]})
    with pytest.raises(PRMSError, match="VERSION_CONFLICT"):
        verify_window_recovery(gate, source, package, core_plan=plan, core_choice=choice, history_choice=history)
    refreshed = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                        history_choice=history, budget_bytes=1_000_000)
    assert refreshed["status"] == "PARTIAL" and "CHECKPOINT_LAGS_DURABLE_EVENTS" in refreshed["warnings"]


def test_depth_summary_and_full_audit_preserve_sources_and_fail_closed(setup):
    import base64
    import json
    store, gate, caller, _ = setup
    apply(store, gate, caller, "old-event", "APPEND", {"event_id": "old", "task_id": "prior-task",
          "kind": "MODEL_INFERENCE", "text": "historical evidence " * 60,
          "source_refs": [{"repository": "fixture/source", "commit": "a" * 40, "path": "source.md"}]})
    apply(store, gate, caller, "assignment", "ASSIGN", {"assignment_id": "task", "task_id": "PRMS",
                                                        "human_authority_ref": "fixture Human instruction"})
    apply(store, gate, caller, "checkpoint", "CHECKPOINT", {"task_id": "PRMS"})
    source = GitSource(ROOT, BASE, "fixture/core")
    plan = plan_context(source, discover_g1(source), session_id="depth", role="engineer", task_id="PRMS")
    choice = human_choice(plan, session_id="depth", selected_paths=[], decision_source="fixture")
    history = {"session_id": "depth", "selected_event_ids": ["old"], "depth": "L2", "decision_source": "fixture L2"}
    package = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                      history_choice=history, budget_bytes=1_000_000)
    assert package["selected_events"] == []
    assert package["optional_summaries"][0]["omitted_characters"] > 0
    assert package["optional_summaries"][0]["kind"] == "MODEL_INFERENCE"
    history.update(depth="L4", selected_event_ids=[])
    package = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                      history_choice=history, budget_bytes=1_000_000)
    audit = package["role_history_audit"]
    assert audit["status"] == "COMPLETE_WITHIN_ROLE_HISTORY"
    currents = [json.loads(base64.b64decode(x["content"])) for x in audit["items"] if x["path"].endswith("CURRENT.json")]
    assert {x["state_version"] for x in currents} == {1, 2, 3, 4}
    assert sum(x["path"].startswith("publications/") for x in audit["items"]) == 4
    verify_window_recovery(gate, source, package, core_plan=plan, core_choice=choice, history_choice=history)
    history["max_history_commits"] = 1
    bounded = create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                      history_choice=history, budget_bytes=1_000_000)
    assert bounded["status"] == "BLOCKED" and bounded["role_history_audit"]["unvisited_commits"]
    history.update(depth="L0", selected_event_ids=["old"])
    with pytest.raises(PRMSError, match="REJECTED"):
        create_recovery_package(gate, "engineer", source, core_plan=plan, core_choice=choice,
                                 history_choice=history, budget_bytes=1_000_000)
