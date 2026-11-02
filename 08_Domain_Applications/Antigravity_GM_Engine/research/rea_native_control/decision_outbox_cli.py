"""CLI tool for Decision Outbox management and cycle lifecycle inspection.

NOTE ON SECURITY & AUTHENTICATION MODE:
The CLI flags `--profile-file` and `--phase-grants-file` operate in LOCAL_OPERATOR_TEST_MODE.
In production or multi-agent network topologies, caller identity, role profiles, and phase
grants must be resolved and authenticated by the trusted host service / OS gateway, not supplied
as unverified local input files.
"""
import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from decision_outbox import DecisionOutbox
from role_batches import ActionIntent, BatchContext
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


def _safe_read_json(path_str: str) -> Any:
    p = Path(path_str).resolve()
    return json.loads(p.read_text(encoding="utf-8-sig"))


def cmd_open_cycle(args, outbox: DecisionOutbox):
    ctx_data = _safe_read_json(args.context_file)
    context = BatchContext(**ctx_data)
    res = outbox.open_cycle(args.cycle_id, context)
    print(json.dumps(res, indent=2))


def cmd_add_intent(args, outbox: DecisionOutbox):
    intent_data = _safe_read_json(args.intent_file)
    profile_data = _safe_read_json(args.profile_file)
    profile = RoleCapabilityProfile(**profile_data)
    grants_data = _safe_read_json(args.phase_grants_file)
    phase_grants = {tuple(g) for g in grants_data}

    intent = ActionIntent.decided(
        intent_data["intent_id"],
        intent_data["issuer_uid"],
        intent_data["action_id"],
        intent_data["parameters"],
        dependencies=tuple(intent_data.get("dependencies", ())),
        agreement_ref=intent_data.get("agreement_ref")
    )
    res = outbox.add_intent(
        args.cycle_id,
        intent,
        profile,
        phase_grants,
        source_evidence_ref=args.source_evidence_ref or "",
        decision_reason=args.decision_reason or ""
    )
    print(json.dumps({"added_intent_id": res.intent_id, "action_id": res.action_id}, indent=2))


def cmd_supersede_intent(args, outbox: DecisionOutbox):
    intent_data = _safe_read_json(args.new_intent_file)
    profile_data = _safe_read_json(args.profile_file)
    profile = RoleCapabilityProfile(**profile_data)
    grants_data = _safe_read_json(args.phase_grants_file)
    phase_grants = {tuple(g) for g in grants_data}

    new_intent = ActionIntent.decided(
        intent_data["intent_id"],
        intent_data["issuer_uid"],
        intent_data["action_id"],
        intent_data["parameters"],
        dependencies=tuple(intent_data.get("dependencies", ())),
        agreement_ref=intent_data.get("agreement_ref")
    )
    res = outbox.supersede_intent(
        args.cycle_id,
        args.old_intent_id,
        new_intent,
        profile,
        phase_grants,
        decision_reason=args.decision_reason or ""
    )
    print(json.dumps({"superseded_intent_id": args.old_intent_id, "new_intent_id": res.intent_id}, indent=2))


def cmd_inspect(args, outbox: DecisionOutbox):
    cycle = outbox.get_cycle(args.cycle_id)
    if not cycle:
        print(f"Cycle not found: {args.cycle_id}", file=sys.stderr)
        sys.exit(1)
    analysis = outbox.inspect_conflicts_and_dependencies(args.cycle_id)
    intents = outbox.list_intents(args.cycle_id)
    summary = {
        "cycle": cycle,
        "conflict_and_dependency_analysis": analysis,
        "intent_count": len(intents),
        "intents": intents
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_seal(args, outbox: DecisionOutbox):
    sealed_batch = outbox.seal_cycle(
        args.cycle_id,
        aggregate_batch_id=args.batch_id,
        expected_revision=args.expected_revision
    )
    res = {
        "cycle_id": args.cycle_id,
        "sealed_batch_id": sealed_batch.batch_id,
        "intents_count": len(sealed_batch.intents),
        "status": "SEALED"
    }
    if args.output:
        Path(args.output).write_text(json.dumps({
            "batch_id": sealed_batch.batch_id,
            "context": json.loads(json.dumps(sealed_batch.context, default=lambda o: o.__dict__)),
            "intents": [
                {
                    "intent_id": i.intent_id,
                    "issuer_uid": i.issuer_uid,
                    "action_id": i.action_id,
                    "parameters": i.parameters,
                    "dependencies": list(i.dependencies),
                    "agreement_ref": i.agreement_ref
                }
                for i in sealed_batch.intents
            ]
        }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2))


def cmd_show_outcomes(args, outbox: DecisionOutbox):
    summary = outbox.get_outcome_summary(args.cycle_id)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="NBA2K22 REA Decision Outbox CLI")
    parser.add_argument("--db-path", default="outbox.db", help="Path to SQLite outbox database file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # open-cycle
    p_open = subparsers.add_parser("open-cycle", help="Open a new decision cycle")
    p_open.add_argument("--cycle-id", required=True)
    p_open.add_argument("--context-file", required=True)

    # add-intent
    p_add = subparsers.add_parser("add-intent", help="Add an ActionIntent to an open cycle")
    p_add.add_argument("--cycle-id", required=True)
    p_add.add_argument("--intent-file", required=True)
    p_add.add_argument("--profile-file", required=True)
    p_add.add_argument("--phase-grants-file", required=True)
    p_add.add_argument("--source-evidence-ref")
    p_add.add_argument("--decision-reason")

    # supersede-intent
    p_super = subparsers.add_parser("supersede-intent", help="Supersede an unsealed intent")
    p_super.add_argument("--cycle-id", required=True)
    p_super.add_argument("--old-intent-id", required=True)
    p_super.add_argument("--new-intent-file", required=True)
    p_super.add_argument("--profile-file", required=True)
    p_super.add_argument("--phase-grants-file", required=True)
    p_super.add_argument("--decision-reason")

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect cycle status, intents, and conflicts")
    p_insp.add_argument("--cycle-id", required=True)

    # seal
    p_seal = subparsers.add_parser("seal", help="Seal decision cycle into an immutable RoleActionBatch")
    p_seal.add_argument("--cycle-id", required=True)
    p_seal.add_argument("--batch-id", required=True)
    p_seal.add_argument("--expected-revision", type=int)
    p_seal.add_argument("--output", help="Optional path to export sealed batch JSON")

    # show-outcomes
    p_out = subparsers.add_parser("show-outcomes", help="Show execution outcome summary and exceptions")
    p_out.add_argument("--cycle-id", required=True)

    args = parser.parse_args()
    service = RoleCapabilityService()
    outbox = DecisionOutbox(args.db_path, capability_service=service)

    cmds = {
        "open-cycle": cmd_open_cycle,
        "add-intent": cmd_add_intent,
        "supersede-intent": cmd_supersede_intent,
        "inspect": cmd_inspect,
        "seal": cmd_seal,
        "show-outcomes": cmd_show_outcomes
    }
    cmds[args.command](args, outbox)


if __name__ == "__main__":
    main()
