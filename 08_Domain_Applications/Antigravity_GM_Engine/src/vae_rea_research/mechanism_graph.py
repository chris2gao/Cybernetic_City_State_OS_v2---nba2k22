from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class GraphNode:
    node_id: str
    node_type: str  # "SETTING_FIELD", "NATIVE_TRANSFORMER", "INTERNAL_STATE", "OBSERVABLE_OUTCOME"
    category: str   # "COACH", "PLAYER_TENDENCY", "WORLD_RULE", "SIMULATION_ENGINE"
    description: str
    canonical_key: Optional[str] = None
    rva_or_offset: Optional[str] = None
    epistemological_grade: str = "STATIC_DISASSEMBLY_LEAD"


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: str  # "INPUT_TO", "TRANSFORMS_TO", "REGULATES", "OUTPUTS_TO", "MODULATES"
    epistemological_status: str  # "STATIC_DISASSEMBLY_LEAD", "STATIC_CALL_RELATION", "PENDING_GAMEPLAY_VALIDATION"
    math_formula: Optional[str] = None
    telemetry_validation_id: Optional[str] = None
    description: str = ""


class MechanismRelationshipGraph:
    """
    Comprehensive mechanism relationship graph and impact chain tracker for NBA2K22.
    Explicitly tracks epistemological boundaries:
    - STATIC_DISASSEMBLY_LEAD: Direct instruction / register flow disassembled from NBA2K22.exe.
    - STATIC_CALL_RELATION: Static caller/callee or pointer traversal verified in disassembly.
    - HYPOTHESIZED_BEHAVIOR: Behavioral impact based on engine architecture and domain literature.
    - PENDING_GAMEPLAY_VALIDATION: Real-world match outcome requiring future telemetry logging.
    """

    def __init__(self, repo_root: Optional[str] = None) -> None:
        if repo_root is None:
            cur = os.path.abspath(__file__)
            repo_root = os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))
        self.repo_root = repo_root
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._build_default_graph()

    def _build_default_graph(self) -> None:
        # 1. Setting Nodes (Inputs) - Verified against VAE_FIELD_INVENTORY_SHARED_V1.json
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_014",
            node_type="SETTING_FIELD",
            category="COACH",
            canonical_key="Tempo",
            description="Coach Gameplan: Tempo (Pace slider [0..100])",
            rva_or_offset="0x7ff4e7421160+0x13c",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_001",
            node_type="SETTING_FIELD",
            category="COACH",
            canonical_key="POEOffense",
            description="Coach Gameplan: POEOffense (Point of Emphasis Offense [0..6])",
            rva_or_offset="0x7ff4e742129c",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_004",
            node_type="SETTING_FIELD",
            category="COACH",
            canonical_key="POEDefense",
            description="Coach Gameplan: POEDefense (Point of Emphasis Defense [0..6])",
            rva_or_offset="0x7ff4e742129e",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="TENDENCY_NATIVE_001",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            canonical_key="tendency.SHOT_TENDENCY",
            description="Player Tendency: ShotTendency (Getter RVA 0x975820, [0..100])",
            rva_or_offset="0x975820",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="TENDENCY_NATIVE_066",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            canonical_key="tendency.TOUCHES_TENDENCY",
            description="Player Tendency: Touches (Getter RVA 0x975b30, [0..100])",
            rva_or_offset="0x975b30",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="PLAYER_TACTICAL_ROLE_TIER",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            canonical_key="player.role_tier",
            description="Player Tactical Role Assignment: Primary Tier [rsp+0x20], Secondary [rsp+0x24] in [0..3]",
            rva_or_offset="[rsp+0x20]",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))

        # 2. Native Transformer Nodes
        self.add_node(GraphNode(
            node_id="TRANSFORMER_ROLE_GOVERNOR",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="Tactical Role Hierarchy & Clamping Governor (RVA 0x1226942..0x1226a8b, Table 0x2b59798)",
            rva_or_offset="0x1226942",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))
        self.add_node(GraphNode(
            node_id="TRANSFORMER_COACH_PACING",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="Coach Dynamic Pacing Engine: Linear transform with [10, 70] bounds clamping (RVA 0x120ba72)",
            rva_or_offset="0x120ba72",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))
        self.add_node(GraphNode(
            node_id="TRANSFORMER_POE_STRATEGY",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="POE Strategy Dispatcher: Play selection frequency modulator (RVA 0x140f629f0)",
            rva_or_offset="0x140f629f0",
            epistemological_grade="STATIC_CALL_RELATION",
        ))
        self.add_node(GraphNode(
            node_id="TRANSFORMER_SNAPSHOT_PIPELINE",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="Simulation Roster Snapshot Pipeline: Copies all 99 tendencies with stride 0x27c (RVA 0x1744bd0)",
            rva_or_offset="0x1744bd0",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))

        # 3. Internal State Nodes
        self.add_node(GraphNode(
            node_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Clamped/Scaled Player Shot Tendency written to AI Controller struct [rdi+0x2dd]",
            rva_or_offset="[rdi+0x2dd]",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))
        self.add_node(GraphNode(
            node_id="STATE_EFFECTIVE_TOUCHES",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Clamped/Scaled Player Touches written to AI Controller struct [rdi+0x2de]",
            rva_or_offset="[rdi+0x2de]",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))
        self.add_node(GraphNode(
            node_id="STATE_NET_POSSESSION_PACE",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Target possession seconds / pace delta written after (base_target - ecx) at RVA 0x120babd",
            rva_or_offset="0x120babd",
            epistemological_grade="STATIC_DISASSEMBLY_LEAD",
        ))

        # 4. Observable Outcome Nodes (Requiring Gameplay Telemetry)
        self.add_node(GraphNode(
            node_id="OUTCOME_PLAYER_ACTUAL_FGA",
            node_type="OBSERVABLE_OUTCOME",
            category="SIMULATION_ENGINE",
            description="In-game / Simulated Box Score: Field Goal Attempts (FGA) per 36 minutes",
            epistemological_grade="PENDING_GAMEPLAY_VALIDATION",
        ))
        self.add_node(GraphNode(
            node_id="OUTCOME_TEAM_PACE_POSSESSIONS",
            node_type="OBSERVABLE_OUTCOME",
            category="SIMULATION_ENGINE",
            description="In-game / Simulated Box Score: Total Possessions per 48 minutes",
            epistemological_grade="PENDING_GAMEPLAY_VALIDATION",
        ))
        self.add_node(GraphNode(
            node_id="OUTCOME_PLAYER_FATIGUE_RATE",
            node_type="OBSERVABLE_OUTCOME",
            category="SIMULATION_ENGINE",
            description="In-game / Simulated Box Score: 4th Quarter Stamina Drain and Performance Penalty",
            epistemological_grade="PENDING_GAMEPLAY_VALIDATION",
        ))

        # 5. Edges
        # Tendencies & Roles -> Role Governor
        self.add_edge(GraphEdge(
            source_id="TENDENCY_NATIVE_001",
            target_id="TRANSFORMER_ROLE_GOVERNOR",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="eax = get_shot_tendency()",
            description="Passes raw shot tendency to governor in r8d",
        ))
        self.add_edge(GraphEdge(
            source_id="TENDENCY_NATIVE_066",
            target_id="TRANSFORMER_ROLE_GOVERNOR",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="eax = get_touches()",
            description="Passes raw touches to governor in eax/dl",
        ))
        self.add_edge(GraphEdge(
            source_id="PLAYER_TACTICAL_ROLE_TIER",
            target_id="TRANSFORMER_ROLE_GOVERNOR",
            relation_type="REGULATES",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="rcx = [rsp+0x20], rbx = [rsp+0x24]",
            description="Selects Branch A (3,3), Branch B (3,!=3), or Branch C (!=3)",
        ))

        # Role Governor -> Effective Internal States
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_ROLE_GOVERNOR",
            target_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            relation_type="TRANSFORMS_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="Tier3: raw; Tier2: min(raw, ceil-5); Tier0/1: max(raw, floor)",
            description="Stores clamped shot tendency into [rdi+0x2dd]",
        ))
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_ROLE_GOVERNOR",
            target_id="STATE_EFFECTIVE_TOUCHES",
            relation_type="TRANSFORMS_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="Tier3: raw; Tier2: min(raw, ceil-5); Tier0/1: max(raw, floor)",
            description="Stores clamped touches into [rdi+0x2de]",
        ))

        # Coach Settings -> Coach Pacing Engine & Strategy
        self.add_edge(GraphEdge(
            source_id="COACH_DEFAULT_014",
            target_id="TRANSFORMER_COACH_PACING",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="ecx = clamp(10, 70, (Tempo - 50) * 1.2 + 10)",
            description="Tempo slider converted to bounded pace modifier via fixed-point IMUL",
        ))
        self.add_edge(GraphEdge(
            source_id="COACH_DEFAULT_001",
            target_id="TRANSFORMER_POE_STRATEGY",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_CALL_RELATION",
            math_formula="call 0x140f629f0 with slot 0x57",
            description="Offensive POE strategy lookup modulates offensive pacing weight",
        ))
        self.add_edge(GraphEdge(
            source_id="COACH_DEFAULT_004",
            target_id="TRANSFORMER_POE_STRATEGY",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_CALL_RELATION",
            math_formula="call 0x140f629f0 with slot 0x58",
            description="Defensive POE strategy lookup modulates defensive pacing weight",
        ))
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_POE_STRATEGY",
            target_id="TRANSFORMER_COACH_PACING",
            relation_type="MODULATES",
            epistemological_status="STATIC_CALL_RELATION",
            math_formula="mulss xmm8, xmm13; mulss xmm6, xmm14",
            description="POE strategy factors scale pace evaluation curve",
        ))
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_COACH_PACING",
            target_id="STATE_NET_POSSESSION_PACE",
            relation_type="TRANSFORMS_TO",
            epistemological_status="STATIC_DISASSEMBLY_LEAD",
            math_formula="hypothesized_net_target = base_possession_target - ecx",
            description="Computes hypothesized net possession pace delta",
        ))

        # Internal States -> Observable Outcomes (PENDING_GAMEPLAY_VALIDATION)
        self.add_edge(GraphEdge(
            source_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            target_id="OUTCOME_PLAYER_ACTUAL_FGA",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_FGA_SUPPRESSION",
            description="Hypothesized in-engine factor modulating simulated and live game FGA volume",
        ))
        self.add_edge(GraphEdge(
            source_id="STATE_NET_POSSESSION_PACE",
            target_id="OUTCOME_TEAM_PACE_POSSESSIONS",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_TEMPO_SATURATION",
            description="Hypothesized simulation factor modulating total team game possessions",
        ))
        self.add_edge(GraphEdge(
            source_id="STATE_NET_POSSESSION_PACE",
            target_id="OUTCOME_PLAYER_FATIGUE_RATE",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_TEMPO_FATIGUE",
            description="Hypothesized factor modulating late-game stamina degradation rate",
        ))

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def validate_graph_invariants(self, inventory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Validates graph integrity:
        1. All SETTING_FIELD nodes exist in VAE_FIELD_INVENTORY_SHARED_V1.json with matching canonical keys.
        2. All edge sources and targets exist in the graph.
        3. Graph is a Directed Acyclic Graph (DAG) with no cycles.
        4. No unverified edge claims PROVEN_NATIVE_ASSEMBLY for gameplay outcomes.
        """
        if inventory_path is None:
            inventory_path = os.path.join(
                self.repo_root, "01_os", "07_content", "_runs",
                "run-20261030-nba2k22-vae-rea-single-field-loop-001",
                "01_任务输入", "VAE_FIELD_INVENTORY_SHARED_V1.json"
            )

        if not os.path.exists(inventory_path):
            # Fallback path if non-ASCII path issue arises
            candidate = os.path.join(
                self.repo_root, "01_os", "07_content", "_runs",
                "run-20261030-nba2k22-vae-stage01-001",
                "01_任务输入", "VAE_FIELD_INVENTORY_SHARED_V1.json"
            )
            if os.path.exists(candidate):
                inventory_path = candidate

        inventory_entries: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(inventory_path):
            with open(inventory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("field_entries", []):
                inventory_entries[item["field_id"]] = item

        # Invariant 1: Check setting field keys against inventory
        setting_mismatches = []
        for node_id, node in self.nodes.items():
            if node.node_type == "SETTING_FIELD":
                # Special internal state setting
                if node_id == "PLAYER_TACTICAL_ROLE_TIER":
                    continue
                if node_id not in inventory_entries:
                    setting_mismatches.append(f"Node {node_id} not found in inventory")
                    continue
                inv_item = inventory_entries[node_id]
                expected_key = inv_item.get("candidate_native_key") or inv_item.get("canonical_name")
                if node.canonical_key and node.canonical_key != expected_key:
                    setting_mismatches.append(
                        f"Node {node_id} canonical_key mismatch: graph has '{node.canonical_key}', "
                        f"inventory has '{expected_key}'"
                    )

        if setting_mismatches:
            raise ValueError(f"Graph setting field invariant violation: {setting_mismatches}")

        # Invariant 2: Check edge endpoints exist
        broken_edges = []
        for e in self.edges:
            if e.source_id not in self.nodes:
                broken_edges.append(f"Edge source {e.source_id} not in graph")
            if e.target_id not in self.nodes:
                broken_edges.append(f"Edge target {e.target_id} not in graph")
        if broken_edges:
            raise ValueError(f"Graph broken edges detected: {broken_edges}")

        # Invariant 3: Cycle Detection (Topological Sort / DFS)
        visited = {}  # 0: unvisited, 1: visiting, 2: visited
        for nid in self.nodes:
            visited[nid] = 0

        adj = {nid: [] for nid in self.nodes}
        for e in self.edges:
            adj[e.source_id].append(e.target_id)

        def has_cycle(u: str) -> bool:
            visited[u] = 1
            for v in adj[u]:
                if visited[v] == 1:
                    return True
                if visited[v] == 0:
                    if has_cycle(v):
                        return True
            visited[u] = 2
            return False

        for nid in self.nodes:
            if visited[nid] == 0:
                if has_cycle(nid):
                    raise ValueError(f"Graph cycle detected containing or reachable from node '{nid}'")

        # Invariant 4: No PROVEN_NATIVE_ASSEMBLY overclaim on observable outcome edges
        for e in self.edges:
            target_node = self.nodes.get(e.target_id)
            if target_node and target_node.node_type == "OBSERVABLE_OUTCOME":
                if e.epistemological_status != "PENDING_GAMEPLAY_VALIDATION":
                    raise ValueError(
                        f"Edge {e.source_id} -> {e.target_id} targets an observable outcome but has status "
                        f"'{e.epistemological_status}'; must be 'PENDING_GAMEPLAY_VALIDATION'."
                    )

        return {
            "is_valid": True,
            "total_nodes_validated": len(self.nodes),
            "total_edges_validated": len(self.edges),
            "setting_fields_verified": len([n for n in self.nodes.values() if n.node_type == "SETTING_FIELD"]),
            "is_dag": True,
        }

    def get_forward_impact_chain(self, start_node_id: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph forward from a given field or transformer,
        returning the complete impact path and epistemological status of each step.
        """
        if start_node_id not in self.nodes:
            raise KeyError(f"Start node '{start_node_id}' not found in graph.")

        chain: List[Dict[str, Any]] = []

        def dfs(curr_id: str, current_path: List[Dict[str, Any]]) -> None:
            outgoing = [e for e in self.edges if e.source_id == curr_id]
            if not outgoing:
                if current_path:
                    chain.append({
                        "path_nodes": [p["target_id"] for p in current_path],
                        "steps": list(current_path),
                    })
                return

            for edge in outgoing:
                step_info = {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "relation_type": edge.relation_type,
                    "epistemological_status": edge.epistemological_status,
                    "math_formula": edge.math_formula,
                    "telemetry_validation_id": edge.telemetry_validation_id,
                    "description": edge.description,
                }
                current_path.append(step_info)
                dfs(edge.target_id, current_path)
                current_path.pop()

        dfs(start_node_id, [])
        return chain

    def get_validation_contracts(self) -> List[Dict[str, Any]]:
        """
        Extracts all telemetry validation contracts requiring future in-game measurement.
        Conforms strictly to semantic requirements without prescribing physical database schemas.
        """
        contracts = [
            {
                "contract_id": "VAL_CONTRACT_FGA_SUPPRESSION",
                "hypothesis_name": "Secondary Core Role Ceiling Clamping",
                "target_mechanism": "TACTICAL_ROLE_HIERARCHY_GOVERNOR",
                "required_metrics": [
                    {"metric_name": "player_role_tier", "role": "independent_variable", "feasibility": "DIRECT_READ"},
                    {"metric_name": "actual_fga_per_36", "role": "primary_outcome", "feasibility": "DERIVED_FROM_BOXSCORE"},
                    {"metric_name": "normalize_stats_rule", "role": "confounder_control", "feasibility": "DIRECT_READ"},
                    {"metric_name": "sim_quarter_length", "role": "confounder_control", "feasibility": "DIRECT_READ"},
                ],
                "comparison_protocol": "A/B paired match comparison: RoleTier=2 vs RoleTier=3 players with identical raw ShotTendency > 85.",
                "expected_trend": "RoleTier=2 players exhibit statistically significant FGA suppression conforming to (ceiling - 5).",
                "confounders": ["normalize_stats", "sim_quarter_length", "game_difficulty"],
                "fallback_if_unrecorded": "FLAG_AS_UNKNOWN",
            },
            {
                "contract_id": "VAL_CONTRACT_TEMPO_SATURATION",
                "hypothesis_name": "Coach Tempo Bounds [10, 70] Pace Saturation",
                "target_mechanism": "COACH_DYNAMIC_PACING_ENGINE",
                "required_metrics": [
                    {"metric_name": "coach_tempo_slider", "role": "independent_variable", "feasibility": "DIRECT_READ"},
                    {"metric_name": "team_possessions_per_48", "role": "primary_outcome", "feasibility": "DERIVED_FROM_BOXSCORE"},
                    {"metric_name": "normalize_stats_rule", "role": "confounder_control", "feasibility": "DIRECT_READ"},
                ],
                "comparison_protocol": "A/B match series: Tempo=100 vs Tempo=80 vs Tempo=50.",
                "expected_trend": "Possessions curve reaches upper saturation plateau as native modifier reaches 70.",
                "confounders": ["normalize_stats", "sim_quarter_length", "bench_depth"],
                "fallback_if_unrecorded": "FLAG_AS_UNKNOWN",
            },
            {
                "contract_id": "VAL_CONTRACT_TEMPO_FATIGUE",
                "hypothesis_name": "High Tempo Accelerated Stamina Depletion",
                "target_mechanism": "COACH_DYNAMIC_PACING_ENGINE",
                "required_metrics": [
                    {"metric_name": "coach_tempo_slider", "role": "independent_variable", "feasibility": "DIRECT_READ"},
                    {"metric_name": "fourth_quarter_stamina_avg", "role": "primary_outcome", "feasibility": "DERIVED_FROM_TELEMETRY"},
                    {"metric_name": "fourth_quarter_fg_pct_drop", "role": "secondary_outcome", "feasibility": "DERIVED_FROM_BOXSCORE"},
                ],
                "comparison_protocol": "A/B match series: High tempo (Tempo > 75) vs Normal tempo (Tempo = 50).",
                "expected_trend": "High tempo teams experience greater stamina degradation and fourth-quarter efficiency drops.",
                "confounders": ["player_stamina_rating", "bench_utilization", "quarter_length"],
                "fallback_if_unrecorded": "FLAG_AS_UNKNOWN",
            },
        ]
        return contracts

    def export_graph_dict(self) -> Dict[str, Any]:
        # Validate invariants before export
        self.validate_graph_invariants()

        return {
            "schema_version": "nba2k22.mechanism_relationship_graph.v1",
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes": {k: v.__dict__ for k, v in self.nodes.items()},
            "edges": [e.__dict__ for e in self.edges],
            "validation_contracts": self.get_validation_contracts(),
        }
