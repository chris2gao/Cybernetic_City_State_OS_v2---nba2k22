"""Empirical probe: does normalize_packet preserve stage_actions transparently?

The input below is authored here, independently of the parser. The expected value
is the input itself -- an identity property. Nothing is recomputed by the code
under test.
"""
import json
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO / "01_os/06_execution/task_discipline/packet_input"))
import task_packet_input as reader  # noqa: E402

STAGE_ACTIONS = [
    {
        "action_id": "w6-stage-03",
        "kind": "ordinary_task_work",
        "target": "refs/heads/claude/stage-human-alignment-wiring-001",
        "expected_target_head": None,
        "stage_ids": ["workflow_stage_03_result_modeling"],
        "paths": ["01_os/01_workflow/03_结果建模/实现/最小运行schema_v1.yml"],
        "confirmation": None,
    }
]

BODY = {
    "schema_version": "citystate.task_packet.v1",
    "task_id": "os-v2-stage-human-alignment-wiring-001",
    "branch": "claude/stage-human-alignment-wiring-001",
    "exact_base_sha": "b6782775d7734fb10f5119ce04a057b5af0ef5f3",
    "allowed_changed_paths": ["01_os/**"],
    "required_tests": ["mol_static"],
    "prohibitions": ["master_publication"],
    "stage_actions": STAGE_ACTIONS,
}

results = []


def record(name, ok, detail=""):
    results.append((name, ok, detail))


# --- probe 1: wrapped form, stage_actions must survive byte-identically ---
try:
    out = reader.normalize_packet({"task_packet": json.loads(json.dumps(BODY))})
    same = out.body.get("stage_actions") == STAGE_ACTIONS
    record("wrapped_preserves_stage_actions", same,
           f"source_format={out.source_format} present={'stage_actions' in out.body}")
except Exception as exc:
    record("wrapped_preserves_stage_actions", False, f"{type(exc).__name__}: {exc}")

# --- probe 2: bare form ---
try:
    out2 = reader.normalize_packet(json.loads(json.dumps(BODY)))
    same2 = out2.body.get("stage_actions") == STAGE_ACTIONS
    record("bare_preserves_stage_actions", same2,
           f"source_format={out2.source_format}")
except Exception as exc:
    record("bare_preserves_stage_actions", False, f"{type(exc).__name__}: {exc}")

# --- probe 3: an unknown field must not be rejected and must not be dropped ---
probe = json.loads(json.dumps(BODY))
probe["a_field_no_parser_knows_about"] = {"nested": [1, 2, 3]}
try:
    out3 = reader.normalize_packet({"task_packet": probe})
    kept = out3.body.get("a_field_no_parser_knows_about") == {"nested": [1, 2, 3]}
    record("unknown_field_passes_through", kept, "")
except Exception as exc:
    record("unknown_field_passes_through", False, f"{type(exc).__name__}: {exc}")

# --- probe 4: whole body round-trips unchanged ---
try:
    out4 = reader.normalize_packet({"task_packet": json.loads(json.dumps(BODY))})
    record("whole_body_roundtrips", out4.body == BODY,
           f"normalized_fields={getattr(out4, 'normalized_fields', 'n/a')}")
except Exception as exc:
    record("whole_body_roundtrips", False, f"{type(exc).__name__}: {exc}")

# --- probe 5: does it reject a sibling next to task_packet (documented behaviour) ---
try:
    reader.normalize_packet({"task_packet": json.loads(json.dumps(BODY)), "sibling": "x"})
    record("sibling_next_to_task_packet_rejected", False, "accepted, no error raised")
except Exception as exc:
    record("sibling_next_to_task_packet_rejected", True, f"{type(exc).__name__}")

print(f"probe run against repo {REPO}")
print(f"reader file: {reader.__file__}")
print()
width = max(len(n) for n, _, _ in results)
failed = 0
for name, ok, detail in results:
    mark = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
    print(f"{mark}  {name:<{width}}  {detail}")
print()
print(f"{len(results) - failed}/{len(results)} probes passed")
sys.exit(1 if failed else 0)
