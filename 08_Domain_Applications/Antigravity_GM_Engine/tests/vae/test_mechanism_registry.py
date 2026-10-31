"""
Tests for VAE Pillar 2: Sustainable Learning Mechanism Methodology & Interaction Graph.
Verifies:
- Mechanism catalog records field properties, allowed ranges, and evidence tiers.
- Interaction graph maintains directed candidate influence edges.
- Confounders and tradeoffs are tracked for each setting.
- Graph export and edge verification updates work correctly.
"""

import pytest
from src.vae.contracts import EvidenceTier, EvaluationOutcome
from src.vae.mechanism_registry import VAEMechanismRegistry


@pytest.fixture
def mechanism_registry():
    return VAEMechanismRegistry()


def test_mechanism_catalog_seeds(mechanism_registry):
    """Verifies that seed gameplay settings and mechanisms are registered."""
    export = mechanism_registry.export_graph()
    assert export["fields_count"] >= 5
    assert export["edges_count"] >= 5

    field_ids = export["fields"].keys()
    assert "three_point_success" in field_ids
    assert "coach_pace" in field_ids
    assert "rotation_starter_minutes" in field_ids
    assert "training_intensity" in field_ids
    assert "player_shot_tendency" in field_ids


def test_interaction_edges_and_confounders(mechanism_registry):
    """Verifies that interaction edges track hypotheses and confounders."""
    edges = mechanism_registry.get_edges_for_field("three_point_success")
    assert len(edges) >= 1
    edge = edges[0]
    assert edge.target_behavior == "team_3pt_pct"
    assert edge.edge_type == "MODULATOR"
    assert "contested_shot_percentage" in edge.confounders

    # Confounder lookup
    confounders = mechanism_registry.get_confounders("three_point_success")
    assert "fatigue_level" in confounders
    assert "shooter_badge_tiers" in confounders


def test_edge_verification_update(mechanism_registry):
    """Verifies that edge verification state updates with evaluation outcomes."""
    # EDGE-01 starts unverified
    edge = mechanism_registry.edges["EDGE-01"]
    assert edge.verified_in_game is False

    # Update with controlled confirmed outcome
    updated = mechanism_registry.update_edge_verification("EDGE-01", EvaluationOutcome.CONFIRMED_CONTROLLED)
    assert updated is True
    assert edge.verified_in_game is True
    assert edge.evidence_tier == EvidenceTier.COMPETITIVE_OBSERVED
