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
    rva_or_offset: Optional[str] = None
    epistemological_grade: str = "PROVEN_NATIVE_ASSEMBLY"


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: str  # "INPUT_TO", "TRANSFORMS_TO", "REGULATES", "OUTPUTS_TO", "MODULATES"
    epistemological_status: str  # "PROVEN_NATIVE_ASSEMBLY", "STATIC_CALL_RELATION", "PENDING_GAMEPLAY_VALIDATION"
    math_formula: Optional[str] = None
    telemetry_validation_id: Optional[str] = None
    description: str = ""


class MechanismRelationshipGraph:
    """
    Comprehensive mechanism relationship graph and impact chain tracker for NBA2K22.
    Explicitly tracks epistemological boundaries:
    - PROVEN_NATIVE_ASSEMBLY: Exact opcodes, registers, and memory tables verified in NBA2K22.exe.
    - STATIC_CALL_RELATION: Static caller/callee or pointer traversal verified in disassembly.
    - HYPOTHESIZED_BEHAVIOR: Behavioral impact based on engine architecture and domain literature.
    - PENDING_GAMEPLAY_VALIDATION: Real-world match outcome requiring future telemetry logging.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._build_default_graph()

    def _build_default_graph(self) -> None:
        # 1. Setting Nodes (Inputs)
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_005",
            node_type="SETTING_FIELD",
            category="COACH",
            description="Coach Gameplan: Tempo (Pace slider [0..100])",
            rva_or_offset="0x7ff4e7421160+0x13c",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_001",
            node_type="SETTING_FIELD",
            category="COACH",
            description="Coach Gameplan: POEOffense (Point of Emphasis Offense [0..6])",
            rva_or_offset="0x7ff4e742129c",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="COACH_DEFAULT_002",
            node_type="SETTING_FIELD",
            category="COACH",
            description="Coach Gameplan: POEDefense (Point of Emphasis Defense [0..6])",
            rva_or_offset="0x7ff4e742129e",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="TENDENCY_NATIVE_001",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            description="Player Tendency: ShotTendency (Getter RVA 0x975820, [0..100])",
            rva_or_offset="0x975820",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="TENDENCY_NATIVE_002",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            description="Player Tendency: Touches (Getter RVA 0x975b30, [0..100])",
            rva_or_offset="0x975b30",
            epistemological_grade="LIVE_RECEIPT",
        ))
        self.add_node(GraphNode(
            node_id="PLAYER_TACTICAL_ROLE_TIER",
            node_type="SETTING_FIELD",
            category="PLAYER_TENDENCY",
            description="Player Tactical Role Assignment: Primary Tier [rsp+0x20], Secondary [rsp+0x24] in [0..3]",
            rva_or_offset="[rsp+0x20]",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
        ))

        # 2. Native Transformer Nodes
        self.add_node(GraphNode(
            node_id="TRANSFORMER_ROLE_GOVERNOR",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="Tactical Role Hierarchy & Clamping Governor (RVA 0x1226942..0x1226a8b, Table 0x2b59798)",
            rva_or_offset="0x1226942",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
        ))
        self.add_node(GraphNode(
            node_id="TRANSFORMER_COACH_PACING",
            node_type="NATIVE_TRANSFORMER",
            category="SIMULATION_ENGINE",
            description="Coach Dynamic Pacing Engine: Linear transform with [10, 70] bounds clamping (RVA 0x120ba72)",
            rva_or_offset="0x120ba72",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
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
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
        ))

        # 3. Internal State Nodes
        self.add_node(GraphNode(
            node_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Clamped/Scaled Player Shot Tendency written to AI Controller struct [rdi+0x2dd]",
            rva_or_offset="[rdi+0x2dd]",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
        ))
        self.add_node(GraphNode(
            node_id="STATE_EFFECTIVE_TOUCHES",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Clamped/Scaled Player Touches written to AI Controller struct [rdi+0x2de]",
            rva_or_offset="[rdi+0x2de]",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
        ))
        self.add_node(GraphNode(
            node_id="STATE_NET_POSSESSION_PACE",
            node_type="INTERNAL_STATE",
            category="SIMULATION_ENGINE",
            description="Target possession seconds / pace delta written after (base_target - ecx) at RVA 0x120babd",
            rva_or_offset="0x120babd",
            epistemological_grade="PROVEN_NATIVE_ASSEMBLY",
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
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="eax = get_shot_tendency()",
            description="Passes raw shot tendency to governor in r8d",
        ))
        self.add_edge(GraphEdge(
            source_id="TENDENCY_NATIVE_002",
            target_id="TRANSFORMER_ROLE_GOVERNOR",
            relation_type="INPUT_TO",
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="eax = get_touches()",
            description="Passes raw touches to governor in eax/dl",
        ))
        self.add_edge(GraphEdge(
            source_id="PLAYER_TACTICAL_ROLE_TIER",
            target_id="TRANSFORMER_ROLE_GOVERNOR",
            relation_type="REGULATES",
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="rcx = [rsp+0x20], rbx = [rsp+0x24]",
            description="Selects Branch A (3,3), Branch B (3,!=3), or Branch C (!=3)",
        ))

        # Role Governor -> Effective Internal States
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_ROLE_GOVERNOR",
            target_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            relation_type="TRANSFORMS_TO",
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="Tier3: raw; Tier2: min(raw, ceil-5); Tier0/1: max(raw, floor)",
            description="Stores clamped shot tendency into [rdi+0x2dd]",
        ))
        self.add_edge(GraphEdge(
            source_id="TRANSFORMER_ROLE_GOVERNOR",
            target_id="STATE_EFFECTIVE_TOUCHES",
            relation_type="TRANSFORMS_TO",
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="Tier3: raw; Tier2: min(raw, ceil-5); Tier0/1: max(raw, floor)",
            description="Stores clamped touches into [rdi+0x2de]",
        ))

        # Coach Settings -> Coach Pacing Engine
        self.add_edge(GraphEdge(
            source_id="COACH_DEFAULT_005",
            target_id="TRANSFORMER_COACH_PACING",
            relation_type="INPUT_TO",
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="ecx = clamp(10, 70, (Tempo - 50) * 0.6 + 10)",
            description="Pacing slider converted to bounded pace modifier",
        ))
        self.add_edge(GraphEdge(
            source_id="COACH_DEFAULT_001",
            target_id="TRANSFORMER_POE_STRATEGY",
            relation_type="INPUT_TO",
            epistemological_status="STATIC_CALL_RELATION",
            math_formula="call 0x140f629f0 with slot 0x57",
            description="Offensive POE strategy lookup modifies offensive pacing weight",
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
            epistemological_status="PROVEN_NATIVE_ASSEMBLY",
            math_formula="net_target = base_possession_target - ecx",
            description="Stores net possession pace delta",
        ))

        # Internal States -> Observable Outcomes (PENDING_GAMEPLAY_VALIDATION)
        self.add_edge(GraphEdge(
            source_id="STATE_EFFECTIVE_SHOT_TENDENCY",
            target_id="OUTCOME_PLAYER_ACTUAL_FGA",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_FGA_SUPPRESSION",
            description="Clamped shot tendency directly regulates simulated / live game FGA volume",
        ))
        self.add_edge(GraphEdge(
            source_id="STATE_NET_POSSESSION_PACE",
            target_id="OUTCOME_TEAM_PACE_POSSESSIONS",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_TEMPO_SATURATION",
            description="Net possession target determines total game possessions",
        ))
        self.add_edge(GraphEdge(
            source_id="STATE_NET_POSSESSION_PACE",
            target_id="OUTCOME_PLAYER_FATIGUE_RATE",
            relation_type="OUTPUTS_TO",
            epistemological_status="PENDING_GAMEPLAY_VALIDATION",
            telemetry_validation_id="VAL_CONTRACT_TEMPO_FATIGUE",
            description="Higher tempo accelerates late-game stamina degradation",
        ))

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_forward_impact_chain(self, start_node_id: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph forward from a given field or transformer,
        returning the complete impact path and epistemological status of each step.
        """
        chain: List[Dict[str, Any]] = []
        visited: Set[str] = set()

        def dfs(curr_id: str, current_path: List[Dict[str, Any]]) -> None:
            visited.add(curr_id)
            outgoing = [e for e in self.edges if e.source_id == curr_id]
            if not outgoing:
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
        """
        contracts = []
        for edge in self.edges:
            if edge.epistemological_status == "PENDING_GAMEPLAY_VALIDATION" and edge.telemetry_validation_id:
                contracts.append({
                    "contract_id": edge.telemetry_validation_id,
                    "source_mechanism": edge.source_id,
                    "target_observable": edge.target_id,
                    "relation_type": edge.relation_type,
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                    "description": edge.description,
                })
        return contracts

    def export_graph_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "nba2k22.mechanism_relationship_graph.v1",
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes": {k: v.__dict__ for k, v in self.nodes.items()},
            "edges": [e.__dict__ for e in self.edges],
            "validation_contracts": self.get_validation_contracts(),
        }
