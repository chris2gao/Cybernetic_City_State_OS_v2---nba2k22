"""
VAE Pillar 2: Sustainable Learning Mechanism Methodology and Interaction Graph.
Maintains field-level knowledge registry and directed candidate interaction edges:
- Tracks setting-to-gameplay consequences
- Distinguishes correlation from causation
- Identifies confounding factors and tradeoffs
- Supports incremental versioning and hypothesis testing
"""

from typing import Dict, Any, List, Optional
import json
from .contracts import MechanismInteractionEdge, EvidenceTier, EvaluationOutcome


class VAEMechanismRegistry:
    """
    Maintains the field-level mechanism knowledge registry and the interaction graph.
    Records hypotheses, evidence grades, confounders, and game verification states.
    """

    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, MechanismInteractionEdge] = {}
        self._populate_seed_mechanisms()

    def _populate_seed_mechanisms(self) -> None:
        # Seed 1: three_point_success
        self.register_field(
            field_id="three_point_success",
            domain="GAMEPLAY_SLIDERS",
            role="COMMISSIONER / SHARED",
            native_entry="GAME_SETTINGS.SLIDERS",
            allowed_range=(0, 100),
            evidence_tier=EvidenceTier.STATIC_CODE,
            description="Shot success probability scalar for three-point attempts across user and CPU.",
        )
        self.add_interaction_edge(MechanismInteractionEdge(
            edge_id="EDGE-01",
            source_field="three_point_success",
            target_behavior="team_3pt_pct",
            domain="TACTICS",
            edge_type="MODULATOR",
            evidence_tier=EvidenceTier.STATIC_CODE,
            hypothesis="Higher three_point_success linearly increases 3PT percentage holding shot quality constant.",
            expected_primary_metric="team_3pt_pct",
            side_effects=["team_effective_fg_pct", "defensive_rebound_rate", "pace"],
            confounders=["contested_shot_percentage", "shooter_badge_tiers", "fatigue_level", "opponent_defense_rating"],
            method_version="v2.0",
            verified_in_game=False,
        ))

        # Seed 2: coach_pace
        self.register_field(
            field_id="coach_pace",
            domain="COACHING_TACTICS",
            role="COACH",
            native_entry="COACH_SETTINGS.PACE",
            allowed_range=(0, 100),
            evidence_tier=EvidenceTier.STATIC_CODE,
            description="Team offensive pacing and early-shot-clock attack frequency.",
        )
        self.add_interaction_edge(MechanismInteractionEdge(
            edge_id="EDGE-02",
            source_field="coach_pace",
            target_behavior="total_possessions",
            domain="TACTICS",
            edge_type="DIRECT_CAUSE",
            evidence_tier=EvidenceTier.STATIC_CODE,
            hypothesis="Increasing coach pace raises game possessions per 48 minutes.",
            expected_primary_metric="pace",
            side_effects=["fast_break_points", "turnovers_per_game", "player_fatigue"],
            confounders=["opponent_transition_defense", "turnover_differential", "offensive_rebound_crashing"],
            method_version="v2.0",
            verified_in_game=False,
        ))

        # Seed 3: rotation_starter_minutes
        self.register_field(
            field_id="rotation_starter_minutes",
            domain="ROTATION",
            role="COACH",
            native_entry="ROTATION_TIMELINE",
            allowed_range=(20, 42),
            evidence_tier=EvidenceTier.STATIC_CODE,
            description="Minutes allocated to core starting lineup (total team allocation = 240).",
        )
        self.add_interaction_edge(MechanismInteractionEdge(
            edge_id="EDGE-03",
            source_field="rotation_starter_minutes",
            target_behavior="fourth_quarter_efficiency",
            domain="ROTATION",
            edge_type="MODULATOR",
            evidence_tier=EvidenceTier.STATIC_CODE,
            hypothesis="Excessive starter minutes (>38 min) depresses 4th quarter shooting due to stamina penalty.",
            expected_primary_metric="fourth_quarter_fg_pct",
            side_effects=["injury_probability", "bench_unit_plus_minus"],
            confounders=["timeout_usage", "foul_trouble_bench_time", "blowout_garbage_time"],
            method_version="v2.0",
            verified_in_game=False,
        ))

        # Seed 4: training_intensity
        self.register_field(
            field_id="training_intensity",
            domain="TRAINING",
            role="COACH / PLAYER",
            native_entry="TRAINING_SCHEDULE.INTENSITY",
            allowed_range=(0, 5),
            evidence_tier=EvidenceTier.STATIC_CODE,
            description="Practice intensity and training load (High, Medium, Low, Rest).",
        )
        self.add_interaction_edge(MechanismInteractionEdge(
            edge_id="EDGE-04",
            source_field="training_intensity",
            target_behavior="attribute_growth_rate",
            domain="TRAINING",
            edge_type="MODULATOR",
            evidence_tier=EvidenceTier.STATIC_CODE,
            hypothesis="Very high training intensity accelerates attribute progression but spikes injury risk.",
            expected_primary_metric="monthly_progression_points",
            side_effects=["wear_and_tear_injury_rate", "player_morale_complaints"],
            confounders=["training_facility_tier", "medical_staff_ratings", "player_work_ethic_badge"],
            method_version="v2.0",
            verified_in_game=False,
        ))

        # Seed 5: player_shot_tendency
        self.register_field(
            field_id="player_shot_tendency",
            domain="PLAYER_TENDENCIES",
            role="PLAYER",
            native_entry="PLAYER_EDIT.TENDENCIES.SHOT",
            allowed_range=(0, 100),
            evidence_tier=EvidenceTier.STATIC_CODE,
            description="Likelihood of taking a shot when holding the ball with defensive separation.",
        )
        self.add_interaction_edge(MechanismInteractionEdge(
            edge_id="EDGE-05",
            source_field="player_shot_tendency",
            target_behavior="field_goal_attempts_per_minute",
            domain="TENDENCY",
            edge_type="DIRECT_CAUSE",
            evidence_tier=EvidenceTier.STATIC_CODE,
            hypothesis="Raising shot tendency increases player usage rate and FGA holding playtime constant.",
            expected_primary_metric="fga_per_36",
            side_effects=["teammate_assist_rate", "shot_quality_index"],
            confounders=["playbook_priority_plays", "on_ball_vs_off_ball_role", "point_guard_pass_first_rating"],
            method_version="v2.0",
            verified_in_game=False,
        ))

    def register_field(
        self,
        field_id: str,
        domain: str,
        role: str,
        native_entry: str,
        allowed_range: tuple,
        evidence_tier: EvidenceTier,
        description: str,
    ) -> None:
        self.registry[field_id] = {
            "field_id": field_id,
            "domain": domain,
            "role": role,
            "native_entry": native_entry,
            "allowed_range": allowed_range,
            "evidence_tier": evidence_tier.value,
            "description": description,
        }

    def add_interaction_edge(self, edge: MechanismInteractionEdge) -> None:
        self.edges[edge.edge_id] = edge

    def get_edges_for_field(self, field_id: str) -> List[MechanismInteractionEdge]:
        return [e for e in self.edges.values() if e.source_field == field_id]

    def get_confounders(self, field_id: str) -> List[str]:
        confounders: List[str] = []
        for e in self.get_edges_for_field(field_id):
            confounders.extend(e.confounders)
        return list(dict.fromkeys(confounders))  # preserve order de-dup

    def update_edge_verification(self, edge_id: str, outcome: EvaluationOutcome) -> bool:
        if edge_id in self.edges:
            edge = self.edges[edge_id]
            if outcome == EvaluationOutcome.CONFIRMED_CONTROLLED:
                edge.verified_in_game = True
                edge.evidence_tier = EvidenceTier.COMPETITIVE_OBSERVED
            elif outcome in [EvaluationOutcome.OBSERVED_TREND_POSITIVE, EvaluationOutcome.OBSERVED_TREND_NEGATIVE]:
                edge.evidence_tier = EvidenceTier.COMPETITIVE_OBSERVED
            return True
        return False

    def export_graph(self) -> Dict[str, Any]:
        return {
            "fields_count": len(self.registry),
            "edges_count": len(self.edges),
            "fields": self.registry,
            "edges": {k: edge.__dict__ for k, edge in self.edges.items()},
        }
