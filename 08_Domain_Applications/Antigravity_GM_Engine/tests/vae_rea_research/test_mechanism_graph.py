from __future__ import annotations

import json
import pytest
from src.vae_rea_research.mechanism_graph import MechanismRelationshipGraph, GraphNode, GraphEdge


def test_mechanism_graph_initialization():
    graph = MechanismRelationshipGraph()
    export = graph.export_graph_dict()
    assert export["total_nodes"] >= 10
    assert export["total_edges"] >= 10
    assert "COACH_DEFAULT_005" in graph.nodes
    assert "TENDENCY_NATIVE_001" in graph.nodes
    assert "TRANSFORMER_ROLE_GOVERNOR" in graph.nodes


def test_forward_impact_chain_shot_tendency():
    graph = MechanismRelationshipGraph()
    chains = graph.get_forward_impact_chain("TENDENCY_NATIVE_001")
    assert len(chains) >= 1
    # Check that at least one chain leads to OUTCOME_PLAYER_ACTUAL_FGA
    found_outcome = False
    for c in chains:
        if "OUTCOME_PLAYER_ACTUAL_FGA" in c["path_nodes"]:
            found_outcome = True
            # Verify intermediate step includes TRANSFORMER_ROLE_GOVERNOR
            assert "TRANSFORMER_ROLE_GOVERNOR" in c["path_nodes"]
    assert found_outcome


def test_forward_impact_chain_coach_tempo():
    graph = MechanismRelationshipGraph()
    chains = graph.get_forward_impact_chain("COACH_DEFAULT_005")
    assert len(chains) >= 1
    found_pace = False
    for c in chains:
        if "OUTCOME_TEAM_PACE_POSSESSIONS" in c["path_nodes"]:
            found_pace = True
            assert "TRANSFORMER_COACH_PACING" in c["path_nodes"]
    assert found_pace


def test_validation_contracts_extraction():
    graph = MechanismRelationshipGraph()
    contracts = graph.get_validation_contracts()
    assert len(contracts) >= 3
    for contract in contracts:
        assert contract["verification_gate"] == "PENDING_GAMEPLAY_VALIDATION"
        assert contract["contract_id"].startswith("VAL_CONTRACT_")


def test_graph_json_serializability():
    graph = MechanismRelationshipGraph()
    d = graph.export_graph_dict()
    s = json.dumps(d)
    assert len(s) > 100
    assert "nba2k22.mechanism_relationship_graph.v1" in s
