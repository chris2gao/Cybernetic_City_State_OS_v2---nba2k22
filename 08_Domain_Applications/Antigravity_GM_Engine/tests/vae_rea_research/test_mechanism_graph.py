from __future__ import annotations

import json
import pytest
from src.vae_rea_research.mechanism_graph import MechanismRelationshipGraph, GraphNode, GraphEdge


def test_mechanism_graph_initialization():
    graph = MechanismRelationshipGraph()
    export = graph.export_graph_dict()
    assert export["total_nodes"] >= 10
    assert export["total_edges"] >= 10

    # Verify correct canonical field IDs (INT-P0-01)
    assert "COACH_DEFAULT_014" in graph.nodes
    assert graph.nodes["COACH_DEFAULT_014"].canonical_key == "Tempo"

    assert "TENDENCY_NATIVE_066" in graph.nodes
    assert graph.nodes["TENDENCY_NATIVE_066"].canonical_key == "tendency.TOUCHES_TENDENCY"

    assert "COACH_DEFAULT_001" in graph.nodes
    assert graph.nodes["COACH_DEFAULT_001"].canonical_key == "POEOffense"

    assert "COACH_DEFAULT_004" in graph.nodes
    assert graph.nodes["COACH_DEFAULT_004"].canonical_key == "POEDefense"

    # Verify old erroneous IDs are NOT setting fields
    assert "COACH_DEFAULT_005" not in graph.nodes
    assert "TENDENCY_NATIVE_002" not in graph.nodes


def test_graph_invariants_validation():
    graph = MechanismRelationshipGraph()
    val_res = graph.validate_graph_invariants()
    assert val_res["is_valid"] is True
    assert val_res["is_dag"] is True
    assert val_res["total_nodes_validated"] == len(graph.nodes)


def test_negative_wrong_setting_id_rejection():
    """Negative test: injecting an existing ID with wrong canonical name triggers violation."""
    graph = MechanismRelationshipGraph()
    # Inject COACH_DEFAULT_005 (which is POEDefense2) with canonical_key 'Tempo'
    bad_node = GraphNode(
        node_id="COACH_DEFAULT_005",
        node_type="SETTING_FIELD",
        category="COACH",
        canonical_key="Tempo",  # Wrong! In inventory it's POEDefense2
        description="Mistaken tempo node",
    )
    graph.add_node(bad_node)
    with pytest.raises(ValueError, match="Graph setting field invariant violation"):
        graph.validate_graph_invariants()


def test_negative_cycle_detection():
    """Negative test: adding a cyclic edge triggers cycle detection error."""
    graph = MechanismRelationshipGraph()
    # Add cycle from OUTCOME_TEAM_PACE_POSSESSIONS back to COACH_DEFAULT_014
    bad_edge = GraphEdge(
        source_id="OUTCOME_TEAM_PACE_POSSESSIONS",
        target_id="COACH_DEFAULT_014",
        relation_type="INPUT_TO",
        epistemological_status="PENDING_GAMEPLAY_VALIDATION",
    )
    graph.add_edge(bad_edge)
    with pytest.raises(ValueError, match="Graph cycle detected"):
        graph.validate_graph_invariants()


def test_forward_impact_chain_shot_tendency():
    graph = MechanismRelationshipGraph()
    chains = graph.get_forward_impact_chain("TENDENCY_NATIVE_001")
    assert len(chains) >= 1
    found_outcome = False
    for c in chains:
        if "OUTCOME_PLAYER_ACTUAL_FGA" in c["path_nodes"]:
            found_outcome = True
            assert "TRANSFORMER_ROLE_GOVERNOR" in c["path_nodes"]
    assert found_outcome


def test_forward_impact_chain_coach_tempo():
    graph = MechanismRelationshipGraph()
    chains = graph.get_forward_impact_chain("COACH_DEFAULT_014")
    assert len(chains) >= 1
    found_pace = False
    for c in chains:
        if "OUTCOME_TEAM_PACE_POSSESSIONS" in c["path_nodes"]:
            found_pace = True
            assert "TRANSFORMER_COACH_PACING" in c["path_nodes"]
    assert found_pace


def test_validation_contracts_semantic_only():
    """Verifies contracts provide semantic requirements without physical schemas."""
    graph = MechanismRelationshipGraph()
    contracts = graph.get_validation_contracts()
    assert len(contracts) >= 3
    for contract in contracts:
        assert contract["fallback_if_unrecorded"] == "FLAG_AS_UNKNOWN"
        assert "comparison_protocol" in contract
        assert "confounders" in contract
        # Ensure no premature physical schema leak
        assert "sql_schema" not in contract
        assert "db_table" not in contract
