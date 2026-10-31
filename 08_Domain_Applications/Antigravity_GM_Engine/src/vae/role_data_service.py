"""
VAE Pillar 3: Role-Specific Data Service and Negative Access Control.
Provides segregated, permissioned data views for GM, Coach, and Player:
- GM: finance_projection, market_and_assets, roster_staff, transactions_and_draft, team_and_league_context
- Coach: team_and_opponent_tactics, rotation, training_and_fatigue, available_player_profiles, recent_games
- Player: own_attribute_and_growth, tendencies_and_badges, own_training, health_and_usage, permitted_history
Strictly enforces negative ACL (unauthorized roles are denied access).
"""

from typing import Dict, Any, List, Optional
import datetime
from .contracts import RoleType, RoleDataQuery, RoleDataView, EvidenceTier


class VAERoleDataService:
    """
    Segregates data queries into permissioned role views with negative access control.
    Prevents role privilege leaks (e.g. Players cannot read GM financial models, Coaches cannot read owner dividends).
    """

    ROLE_PERMITTED_CATEGORIES = {
        RoleType.GM: {
            "finance_projection",
            "market_and_assets",
            "roster_staff",
            "transactions_and_draft",
            "team_and_league_context",
        },
        RoleType.COACH: {
            "team_and_opponent_tactics",
            "rotation",
            "training_and_fatigue",
            "available_player_profiles",
            "recent_games",
        },
        RoleType.PLAYER: {
            "own_attribute_and_growth",
            "tendencies_and_badges",
            "own_training",
            "health_and_usage",
            "permitted_history",
        },
        RoleType.WORLD_ADMIN: {
            "all",
        },
    }

    def __init__(self):
        pass

    def query_role_view(self, query: RoleDataQuery) -> RoleDataView:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Check ACL permission
        permitted = self.ROLE_PERMITTED_CATEGORIES.get(query.requester_role, set())
        if "all" not in permitted and query.target_category not in permitted:
            return RoleDataView(
                query_id=query.query_id,
                role=query.requester_role,
                category=query.target_category,
                save_id=query.save_id,
                season=query.season,
                timestamp=now_str,
                freshness="N/A",
                data={},
                source_grade=EvidenceTier.STATIC_CODE,
                access_granted=False,
                rejection_reason=f"ACCESS_DENIED: Role {query.requester_role.value} has no permission to access category '{query.target_category}'",
            )

        # Generate deterministic role payload
        payload = self._generate_role_payload(query)

        return RoleDataView(
            query_id=query.query_id,
            role=query.requester_role,
            category=query.target_category,
            save_id=query.save_id,
            season=query.season,
            timestamp=now_str,
            freshness="LIVE_SIMULATION_STAGING",
            data=payload,
            source_grade=EvidenceTier.OFFLINE_FIXTURE,
            access_granted=True,
            rejection_reason=None,
        )

    def _generate_role_payload(self, query: RoleDataQuery) -> Dict[str, Any]:
        cat = query.target_category

        if cat == "finance_projection":
            return {
                "team_id": "CHI",
                "salary_cap": 112_414_000,
                "luxury_tax_threshold": 136_606_000,
                "apron_hard_cap": 143_002_000,
                "committed_payroll": 105_200_000,
                "projected_cap_space": 7_214_000,
                "tax_penalty_projected": 0,
                "cap_holds": [{"type": "FirstRoundPick", "amount": 2_450_000}],
            }

        elif cat == "rotation":
            return {
                "team_id": "CHI",
                "total_target_minutes": 240,
                "active_rotation_slots": 9,
                "starter_minutes_sum": 164,
                "bench_minutes_sum": 76,
                "foul_trouble_strategy": "AUTO_BENCH_AT_TWO_FOULS_FIRST_QUARTER",
            }

        elif cat == "own_attribute_and_growth":
            return {
                "player_id": query.object_id or "PL_23",
                "overall_rating": 84,
                "potential": 89,
                "age": 22,
                "development_phase": "RAPID_ASCENT",
                "recent_attribute_deltas": {
                    "three_point_shot": +2,
                    "perimeter_defense": +1,
                    "lateral_quickness": 0,
                },
                "training_progression_bar": 0.68,
            }

        elif cat == "team_and_opponent_tactics":
            return {
                "offensive_scheme": "PACE_AND_SPACE",
                "defensive_scheme": "SWITCH_ALL_PERIMETER",
                "pace_slider": 62,
                "fast_break_focus": "RUN_LANES",
                "crash_offensive_glass": "BACK_ON_DEFENSE",
            }

        return {
            "category": cat,
            "status": "VALID_ROLE_DATA_AVAILABLE",
            "object_id": query.object_id,
        }
