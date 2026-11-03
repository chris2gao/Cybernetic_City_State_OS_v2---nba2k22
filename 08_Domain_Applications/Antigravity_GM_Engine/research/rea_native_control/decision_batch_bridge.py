"""Bridge between RoleActionBatch and Native BulkBatch for REA execution.
Converts verified role decision intents into granular Native BulkIntentItems,
partitions unsupported actions, and maps execution receipts back to Outbox items.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    BulkBatchPlanner,
    FieldCatalogLoader,
    canonical_encode,
    sha256_digest
)
from role_batches import (
    ActionIntent,
    BatchContext,
    ExecutionAggregator,
    RoleActionBatch,
    COACH_FIELDS
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


@dataclass(frozen=True)
class BridgeResult:
    bulk_batch: Optional[BulkBatch]
    unsupported_intents: Tuple[Dict[str, Any], ...]
    role_to_bulk_map: Dict[str, Tuple[str, ...]]
    bulk_to_role_map: Dict[str, str]
    planning_issues: Tuple[str, ...]

    @property
    def has_executable_batch(self) -> bool:
        return self.bulk_batch is not None and len(self.bulk_batch.intents) > 0


class DecisionBatchBridge:
    """Translates sealed RoleActionBatches to executable Native BulkBatches."""

    SUPPORTED_NATIVE_ACTIONS = frozenset([
        "PLAYER_PATCH_TENDENCIES",
        "PLAYER_PATCH_ATTRIBUTES",
        "COACH_SET_KNOWN_CURRENT_SETTINGS"
    ])

    ROLE_TO_NATIVE_MAPPING = {
        "PLAYER.EDIT.TENDENCY_BATCH": "PLAYER_PATCH_TENDENCIES",
        "PLAYER.EDIT.ATTR_BATCH": "PLAYER_PATCH_ATTRIBUTES",
        "COACH.STRATEGY.RUN_PLAY": "COACH_SET_KNOWN_CURRENT_SETTINGS",
        "COACH.STRATEGY.ZONE_USAGE": "COACH_SET_KNOWN_CURRENT_SETTINGS",
        "COACH.STRATEGY.BENCH_DEPTH": "COACH_SET_KNOWN_CURRENT_SETTINGS",
        "COACH.STRATEGY.LINEUP_MATCHUPS": "COACH_SET_KNOWN_CURRENT_SETTINGS"
    }

    def __init__(
        self,
        capability_service: Optional[RoleCapabilityService] = None,
        field_catalog: Optional[Dict[str, Any]] = None
    ):
        self.service = capability_service or RoleCapabilityService()
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()
        self.aggregator = ExecutionAggregator(self.service)

    def bridge_batch(
        self,
        role_batch: RoleActionBatch,
        *,
        profiles: Tuple[RoleCapabilityProfile, ...],
        phase_grants: Set[Tuple[str, str]],
        agreements: Tuple[Any, ...] = (),
        expected_pid: Optional[int] = None,
        authorization_ref: str = "HUMAN-AUTHORIZED-ROLE-BATCH",
        dry_run: bool = False,
        allow_partial_execution: bool = True,
        cas_context: Optional[Dict[str, Any]] = None
    ) -> BridgeResult:
        """Converts sealed RoleActionBatch into BulkBatch and identifies unsupported actions."""
        # Sanitize parameters for ExecutionAggregator.plan so that CAS context (expected_before, etc.)
        # does not cause unexpected-field schema errors against the frozen action_registry schemas.
        sanitized_intents = []
        for it in role_batch.intents:
            clean_params = dict(it.parameters)
            clean_params.pop("expected_before", None)
            clean_params.pop("expected_after", None)
            sanitized_intents.append(ActionIntent.decided(
                it.intent_id,
                it.issuer_uid,
                it.action_id,
                clean_params,
                dependencies=it.dependencies,
                agreement_ref=it.agreement_ref
            ))
        sanitized_batch = RoleActionBatch(role_batch.batch_id, role_batch.context, tuple(sanitized_intents))

        # 1. Plan and validate using ExecutionAggregator
        batch_plan = self.aggregator.plan(
            sanitized_batch,
            profiles=profiles,
            phase_grants=phase_grants,
            agreements=agreements
        )

        bulk_intents: List[BulkIntentItem] = []
        unsupported: List[Dict[str, Any]] = []
        role_to_bulk: Dict[str, List[str]] = {}
        bulk_to_role: Dict[str, str] = {}

        # Map planned actions by intent_id
        planned_map = {p.intent.intent_id: p for p in batch_plan.actions}
        issue_map: Dict[str, str] = {}
        for iss in batch_plan.issues:
            if ":" in iss:
                parts = iss.split(":", 1)
                issue_map[parts[0]] = parts[1]

        # Check partial execution policy
        if batch_plan.issues and not allow_partial_execution:
            for intent in role_batch.intents:
                unsupported.append({
                    "intent_id": intent.intent_id,
                    "action_id": intent.action_id,
                    "reason": f"PARTIAL_EXECUTION_DISALLOWED_BY_POLICY: {issue_map.get(intent.intent_id, 'PLANNING_ISSUES_EXIST')}"
                })
            return BridgeResult(
                bulk_batch=None,
                unsupported_intents=tuple(unsupported),
                role_to_bulk_map={},
                bulk_to_role_map={},
                planning_issues=batch_plan.issues
            )

        # 2. Iterate through ALL intents in the role batch
        for intent in role_batch.intents:
            iid = intent.intent_id
            aid = intent.action_id
            params = intent.parameters

            planned = planned_map.get(iid)
            if not planned:
                # Dropped by aggregator planning (e.g. trade agreement error, permission, etc.)
                reason = issue_map.get(iid, "PLANNING_REJECTED")
                unsupported.append({
                    "intent_id": iid,
                    "action_id": aid,
                    "reason": f"UNSUPPORTED_OR_BLOCKED: {reason}"
                })
                continue

            # Determine canonical native action ID
            native_aid = (
                planned.native_action_id
                if planned.native_action_id in self.SUPPORTED_NATIVE_ACTIONS
                else self.ROLE_TO_NATIVE_MAPPING.get(aid)
                or self.service.mapping.get(aid)
            )

            if native_aid not in self.SUPPORTED_NATIVE_ACTIONS:
                unsupported.append({
                    "intent_id": iid,
                    "action_id": aid,
                    "native_action_id": native_aid,
                    "reason": f"UNSUPPORTED_OR_EXTERNAL: action family '{aid}' -> '{native_aid}' cannot be executed via BoundedSessionExecutor bulk setter"
                })
                continue

            # Translate supported actions into BulkIntentItems
            try:
                translated_items = self._translate_action(
                    iid,
                    native_aid,
                    aid,
                    params,
                    intent.dependencies,
                    cas_context=cas_context
                )
                if not translated_items:
                    unsupported.append({
                        "intent_id": iid,
                        "action_id": aid,
                        "reason": "EMPTY_OR_UNPARSABLE_PARAMETERS"
                    })
                    continue

                for b_item in translated_items:
                    bulk_intents.append(b_item)
                    role_to_bulk.setdefault(iid, []).append(b_item.intent_id)
                    bulk_to_role[b_item.intent_id] = iid

            except Exception as e:
                unsupported.append({
                    "intent_id": iid,
                    "action_id": aid,
                    "reason": f"TRANSLATION_ERROR: {e}"
                })

        # 3. Build BulkBatch if executable items exist
        bulk_batch = None
        if bulk_intents:
            header = BulkBatchHeader(
                batch_id=f"BULK-{role_batch.batch_id}",
                save_instance_id=role_batch.context.save_instance_id,
                game_build_sha256=contracts.BUILD,
                authorization_ref=authorization_ref,
                source_snapshot_ref=role_batch.context.snapshot_ref,
                expected_process_name="NBA2K22.exe",
                expected_pid=expected_pid,
                dry_run=dry_run
            )
            bulk_batch = BulkBatch(header=header, intents=tuple(bulk_intents))

        return BridgeResult(
            bulk_batch=bulk_batch,
            unsupported_intents=tuple(unsupported),
            role_to_bulk_map={k: tuple(v) for k, v in role_to_bulk.items()},
            bulk_to_role_map=bulk_to_role,
            planning_issues=batch_plan.issues
        )

    def _translate_action(
        self,
        base_intent_id: str,
        native_aid: str,
        role_aid: str,
        params: Dict[str, Any],
        dependencies: Tuple[str, ...],
        cas_context: Optional[Dict[str, Any]] = None
    ) -> List[BulkIntentItem]:
        """Translates intent parameters into one or more BulkIntentItem instances."""
        items: List[BulkIntentItem] = []
        cas_ctx = cas_context or {}

        def _resolve_cas(f_name: str, sub_val: Any) -> Optional[int]:
            if isinstance(sub_val, dict) and "expected_before" in sub_val and sub_val["expected_before"] is not None:
                return int(sub_val["expected_before"])
            if "expected_before" in params and params["expected_before"] is not None:
                return int(params["expected_before"])
            scoped_key = f"{base_intent_id}:{f_name}"
            if scoped_key in cas_ctx and cas_ctx[scoped_key] is not None:
                return int(cas_ctx[scoped_key])
            if f_name in cas_ctx and cas_ctx[f_name] is not None:
                return int(cas_ctx[f_name])
            return None

        if "team_id" not in params or params["team_id"] is None:
            raise ValueError(f"MISSING_REQUIRED_CAS_CONTEXT: 'team_id' is required for action translation of '{base_intent_id}'")
        team_id = int(params["team_id"])

        if native_aid in ("PLAYER_PATCH_TENDENCIES", "PLAYER_PATCH_ATTRIBUTES"):
            player_id = params.get("player_id") or params.get("player_uid")
            if player_id is None:
                raise ValueError("Missing player_id/player_uid")

            # Format 1: Direct single field (from bulk executor format)
            if "field_id" in params and "value" in params:
                f_id = str(params["field_id"])
                exp_before = _resolve_cas(f_id, params.get("expected_before"))
                if exp_before is None:
                    raise ValueError(f"MISSING_REQUIRED_CAS_CONTEXT: 'expected_before' is required for field '{f_id}'")
                items.append(BulkIntentItem(
                    intent_id=f"{base_intent_id}-0",
                    action_id=native_aid,
                    team_id=team_id,
                    field_id=f_id,
                    expected_before=exp_before,
                    value=int(params["value"]),
                    player_id=int(player_id),
                    dependencies=dependencies
                ))
            # Format 2: Map of fields (values or tendency_map or attribute_map)
            elif "values" in params or "tendency_map" in params or "attribute_map" in params:
                field_map = params.get("values") or params.get("tendency_map") or params.get("attribute_map", {})
                for idx, (f_name, f_val) in enumerate(sorted(field_map.items())):
                    b_val = _resolve_cas(f_name, f_val)
                    if b_val is None:
                        raise ValueError(f"MISSING_REQUIRED_CAS_CONTEXT: 'expected_before' is required for field '{f_name}'")
                    if isinstance(f_val, dict):
                        t_val = f_val.get("value", f_val.get("target_value", b_val))
                    else:
                        t_val = f_val
                    items.append(BulkIntentItem(
                        intent_id=f"{base_intent_id}-{idx}",
                        action_id=native_aid,
                        team_id=team_id,
                        field_id=str(f_name),
                        expected_before=b_val,
                        value=int(t_val),
                        player_id=int(player_id),
                        dependencies=dependencies
                    ))

        elif native_aid == "COACH_SET_KNOWN_CURRENT_SETTINGS":
            if "field_id" in params and "value" in params:
                f_id = str(params["field_id"])
                exp_before = _resolve_cas(f_id, params.get("expected_before"))
                if exp_before is None:
                    raise ValueError(f"MISSING_REQUIRED_CAS_CONTEXT: 'expected_before' is required for coach setting '{f_id}'")
                items.append(BulkIntentItem(
                    intent_id=f"{base_intent_id}-0",
                    action_id=native_aid,
                    team_id=team_id,
                    field_id=f_id,
                    expected_before=exp_before,
                    value=int(params["value"]),
                    dependencies=dependencies
                ))
            elif "settings" in params:
                settings_map = params["settings"]
                for idx, (f_name, f_val) in enumerate(sorted(settings_map.items())):
                    b_val = _resolve_cas(f_name, f_val)
                    if b_val is None:
                        raise ValueError(f"MISSING_REQUIRED_CAS_CONTEXT: 'expected_before' is required for coach setting '{f_name}'")
                    if isinstance(f_val, dict):
                        t_val = f_val.get("value", b_val)
                    else:
                        t_val = f_val
                    items.append(BulkIntentItem(
                        intent_id=f"{base_intent_id}-{idx}",
                        action_id=native_aid,
                        team_id=team_id,
                        field_id=str(f_name),
                        expected_before=b_val,
                        value=int(t_val),
                        dependencies=dependencies
                    ))

        return items

    def map_receipts_to_outbox(
        self,
        bulk_receipts: List[Any],
        bridge_result: BridgeResult
    ) -> List[Dict[str, Any]]:
        """Maps BulkBatch ItemReceipts and unsupported intents back to ActionIntent receipt format.
        Guarantees strict 1-to-1 conservation: multi-sub-intent items are only SUCCESS if all sub-items succeed.
        """
        # 1. Normalize receipts to dicts
        normalized_receipts: List[Dict[str, Any]] = []
        for br in bulk_receipts:
            if isinstance(br, dict):
                normalized_receipts.append(br)
            elif hasattr(br, '__dataclass_fields__'):
                normalized_receipts.append(asdict(br))
            else:
                normalized_receipts.append(vars(br))

        receipts_by_bulk_id = {r.get("intent_id"): r for r in normalized_receipts if r.get("intent_id")}

        outbox_receipts: List[Dict[str, Any]] = []
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 2. Iterate through each role intent declared in role_to_bulk_map
        for role_iid, expected_sub_iids in bridge_result.role_to_bulk_map.items():
            group = [receipts_by_bulk_id[b_id] for b_id in expected_sub_iids if b_id in receipts_by_bulk_id]

            # Check for missing sub-intent receipts
            if len(group) != len(expected_sub_iids):
                missing = set(expected_sub_iids) - {r.get("intent_id") for r in group}
                outbox_receipts.append({
                    "intent_id": role_iid,
                    "bulk_intent_ids": list(expected_sub_iids),
                    "outcome": "INCOMPLETE_RECEIPTS",
                    "reason": f"MISSING_SUB_INTENT_RECEIPTS: missing {sorted(list(missing))}",
                    "actual_before": None,
                    "actual_after": None,
                    "timestamp": now
                })
                continue

            outcomes = [r.get("outcome", "UNKNOWN") for r in group]
            reasons = [r.get("reason", "") for r in group if r.get("reason")]

            if any("UNKNOWN" in o for o in outcomes):
                agg_outcome = "UNKNOWN_EXECUTION_OUTCOME"
            elif any(o in ("FAILED", "CAS_EXPECTED_BEFORE_MISMATCH") for o in outcomes):
                agg_outcome = "FAILED"
            elif all(o == "SUCCESS_APPLIED" for o in outcomes):
                agg_outcome = "SUCCESS_APPLIED"
            elif all(o in ("UNCHANGED_ALREADY_TARGET", "NOOP", "REUSED_HISTORICAL_RECEIPT") for o in outcomes):
                agg_outcome = "UNCHANGED_ALREADY_TARGET"
            elif all(o in ("NOT_EXECUTED", "BLOCKED_BY_PRIOR_UNKNOWN_CLAIM") for o in outcomes):
                agg_outcome = "NOT_EXECUTED"
            else:
                # Partial execution halted (e.g. 1 succeeded, 1 not executed or blocked)
                agg_outcome = "PARTIAL_EXECUTION_HALTED"
                succ_cnt = sum(1 for o in outcomes if o == "SUCCESS_APPLIED")
                reasons.append(f"PARTIAL_EXECUTION_HALTED: {succ_cnt} of {len(outcomes)} sub-intents succeeded")
                reasons.append("; ".join(f"{r.get('intent_id')}:{r.get('outcome')}" for r in group))

            combined_reason = "; ".join(reasons) if reasons else "OK"
            before_val = group[0].get("getter_before", group[0].get("actual_before"))
            after_val = group[-1].get("getter_after", group[-1].get("actual_after"))

            outbox_receipts.append({
                "intent_id": role_iid,
                "bulk_intent_ids": list(expected_sub_iids),
                "outcome": agg_outcome,
                "reason": combined_reason,
                "actual_before": before_val,
                "actual_after": after_val,
                "timestamp": group[0].get("timestamp", now)
            })

        # 3. Add unsupported items as NOT_EXECUTED
        for un in bridge_result.unsupported_intents:
            outbox_receipts.append({
                "intent_id": un["intent_id"],
                "outcome": "NOT_EXECUTED",
                "reason": un["reason"],
                "timestamp": now
            })

        return outbox_receipts
