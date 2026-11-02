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
        dry_run: bool = False
    ) -> BridgeResult:
        """Converts sealed RoleActionBatch into BulkBatch and identifies unsupported actions."""
        # 1. Plan and validate using ExecutionAggregator
        batch_plan = self.aggregator.plan(
            role_batch,
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
                    intent.dependencies
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
        dependencies: Tuple[str, ...]
    ) -> List[BulkIntentItem]:
        """Translates intent parameters into one or more BulkIntentItem instances."""
        items: List[BulkIntentItem] = []

        if native_aid in ("PLAYER_PATCH_TENDENCIES", "PLAYER_PATCH_ATTRIBUTES"):
            team_id = params.get("team_id", 0)
            player_id = params.get("player_id") or params.get("player_uid")
            if player_id is None:
                raise ValueError("Missing player_id/player_uid")

            # Format 1: Direct single field (from bulk executor format)
            if "field_id" in params and "value" in params:
                exp_before = params.get("expected_before", 0)
                items.append(BulkIntentItem(
                    intent_id=f"{base_intent_id}-0",
                    action_id=native_aid,
                    team_id=int(team_id),
                    field_id=str(params["field_id"]),
                    expected_before=int(exp_before),
                    value=int(params["value"]),
                    player_id=int(player_id),
                    dependencies=dependencies
                ))
            # Format 2: Map of fields (values or tendency_map or attribute_map)
            elif "values" in params or "tendency_map" in params or "attribute_map" in params:
                field_map = params.get("values") or params.get("tendency_map") or params.get("attribute_map", {})
                for idx, (f_name, f_val) in enumerate(sorted(field_map.items())):
                    if isinstance(f_val, dict):
                        b_val = f_val.get("expected_before", 0)
                        t_val = f_val.get("value", f_val.get("target_value", b_val))
                    else:
                        b_val = params.get("expected_before", 0)
                        t_val = f_val
                    items.append(BulkIntentItem(
                        intent_id=f"{base_intent_id}-{idx}",
                        action_id=native_aid,
                        team_id=int(team_id),
                        field_id=str(f_name),
                        expected_before=int(b_val),
                        value=int(t_val),
                        player_id=int(player_id),
                        dependencies=dependencies
                    ))

        elif native_aid == "COACH_SET_KNOWN_CURRENT_SETTINGS":
            team_id = params.get("team_id", 0)
            if "field_id" in params and "expected_before" in params and "value" in params:
                items.append(BulkIntentItem(
                    intent_id=f"{base_intent_id}-0",
                    action_id=native_aid,
                    team_id=int(team_id),
                    field_id=str(params["field_id"]),
                    expected_before=int(params["expected_before"]),
                    value=int(params["value"]),
                    dependencies=dependencies
                ))
            elif "settings" in params:
                settings_map = params["settings"]
                for idx, (f_name, f_val) in enumerate(sorted(settings_map.items())):
                    if isinstance(f_val, dict):
                        b_val = f_val.get("expected_before", 0)
                        t_val = f_val.get("value", b_val)
                    else:
                        b_val = 0
                        t_val = f_val
                    items.append(BulkIntentItem(
                        intent_id=f"{base_intent_id}-{idx}",
                        action_id=native_aid,
                        team_id=int(team_id),
                        field_id=str(f_name),
                        expected_before=int(b_val),
                        value=int(t_val),
                        dependencies=dependencies
                    ))

        return items

    def map_receipts_to_outbox(
        self,
        bulk_receipts: List[Any],
        bridge_result: BridgeResult
    ) -> List[Dict[str, Any]]:
        """Maps BulkBatch ItemReceipts and unsupported intents back to ActionIntent receipt format."""
        # 1. Normalize receipts to dicts
        normalized_receipts: List[Dict[str, Any]] = []
        for br in bulk_receipts:
            if isinstance(br, dict):
                normalized_receipts.append(br)
            elif hasattr(br, '__dataclass_fields__'):
                normalized_receipts.append(asdict(br))
            else:
                normalized_receipts.append(vars(br))

        # 2. Group bulk receipts by role intent ID
        bulk_to_role = bridge_result.bulk_to_role_map
        role_receipt_groups: Dict[str, List[Dict[str, Any]]] = {}
        for br in normalized_receipts:
            b_iid = br.get("intent_id")
            role_iid = bulk_to_role.get(b_iid, b_iid)
            role_receipt_groups.setdefault(role_iid, []).append(br)

        outbox_receipts: List[Dict[str, Any]] = []
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 3. Aggregate outcomes per role intent ID
        for role_iid, group in role_receipt_groups.items():
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
            elif any(o == "SUCCESS_APPLIED" for o in outcomes):
                agg_outcome = "SUCCESS_APPLIED"
            else:
                agg_outcome = outcomes[0]

            combined_reason = "; ".join(reasons) if reasons else "OK"
            before_val = group[0].get("getter_before", group[0].get("actual_before"))
            after_val = group[-1].get("getter_after", group[-1].get("actual_after"))

            outbox_receipts.append({
                "intent_id": role_iid,
                "bulk_intent_ids": [r.get("intent_id") for r in group],
                "outcome": agg_outcome,
                "reason": combined_reason,
                "actual_before": before_val,
                "actual_after": after_val,
                "timestamp": group[0].get("timestamp", now)
            })

        # 4. Add unsupported items as NOT_EXECUTED
        for un in bridge_result.unsupported_intents:
            outbox_receipts.append({
                "intent_id": un["intent_id"],
                "outcome": "NOT_EXECUTED",
                "reason": un["reason"],
                "timestamp": now
            })

        return outbox_receipts
