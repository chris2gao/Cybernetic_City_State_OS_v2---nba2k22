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
