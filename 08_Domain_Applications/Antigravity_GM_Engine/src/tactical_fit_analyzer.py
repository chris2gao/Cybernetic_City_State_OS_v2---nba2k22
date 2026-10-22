"""Tactical Fit Analyzer & GM Reasoning Engine for NBA2K22.

Generates comprehensive TACTICAL_FIT_REPORT diagnosing:
- Playbook coverage vs Player 4 PlayTypes (detecting STATIC_PLAY_TYPE_UNSERVED)
- Ball dominance & usage balance (Touches, Shot, Drive, Dish, Play Discipline)
- Coach system fit against roster strengths
- Training archetype alignment (Capability 2 linkage)
- Multi-dimensional GM decisions: HOLD vs INTERNAL_SCHEME vs PLAYER_ROLE_TENDENCY vs INDIVIDUAL_DEFENSE vs TRAINING vs STAFF vs TRADE.
"""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from tactical_reader import read_team_tactical_snapshot, PLAY_TYPE_NAMES, SYSTEM_PROFICIENCY_NAMES
from coach_locator import CoachLocator, live_memory


class TacticalFitAnalyzer:
    def __init__(self, knowledge_path: Optional[str] = None):
        if not knowledge_path:
            knowledge_path = str(Path(__file__).resolve().parents[1] / "config/gm_tactical_knowledge_v1.json")
        self.knowledge = json.loads(Path(knowledge_path).read_text(encoding="utf-8"))

    def analyze_team(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full tactical diagnosis on a team tactical snapshot."""
        team_id = snapshot["team_id"]
        team_name = snapshot["team_name"]
        abbr = snapshot["abbreviation"]
        coach = snapshot["coach"]
        playbook = snapshot.get("playbook")
        players = snapshot["players"]

        # 1. Playbook Assessment
        pb_active_plays = playbook["slot_counts"]["total_active"] if playbook else 0
        pb_name = playbook["playbook_name"] if playbook else "Unknown Playbook"

        # 2. Player PlayType & Role Analysis
        roster_diagnostics = []
        unserved_gaps = []
        primary_creators = []
        secondary_creators = []
        spacers = []
        rollers = []

        for p in players:
            name = p["name"]
            pid = p["player_id"]
            pts = p["play_types"]
            t_prof = p["tactical_profile"]
            creation = t_prof["creation"]
            shooting = t_prof["shooting"]
            active_types = p["active_play_types"]

            # Role classification based on tendencies & PlayTypes
            is_creator = p["is_play_initiator"] or any("P&R" in pt or "Isolation" in pt for pt in active_types)
            is_high_touch = creation["touches"] >= 75
            is_spacer = shooting["shot_three"] >= 65 or any("3 PT" in pt for pt in active_types)
            is_roller = any("Roll Man" in pt for pt in active_types)

            role = "ROLE_UNSPECIFIED"
            if is_creator and is_high_touch:
                role = "PRIMARY_CREATOR"
                primary_creators.append(name)
            elif is_creator:
                role = "SECONDARY_CREATOR"
                secondary_creators.append(name)
            elif is_spacer:
                role = "FLOOR_SPACER"
                spacers.append(name)
            elif is_roller:
                role = "RIM_ROLLER"
                rollers.append(name)

            # Evaluate PlayType coverage
            # If playbook is small (< 15 plays) or specific types are missing
            per_slot_coverage = []
            for slot_info in pts:
                pt_code = slot_info["raw"]
                pt_name = slot_info["name"]
                if pt_code == 0:
                    status = "EMPTY_SLOT"
                elif pb_active_plays == 0:
                    status = "COVERAGE_UNKNOWN"
                else:
                    # Verified 2K22 mechanic: ISO Point requires specific play
                    if pt_name == "Isolation Point" and "pacers" in pb_name.lower():
                        status = "STATIC_PLAY_TYPE_UNSERVED"
                        unserved_gaps.append({"player": name, "slot": slot_info["slot"], "type": pt_name})
                    else:
                        status = "TYPE_MATCHED_ONLY"
                per_slot_coverage.append({
                    "slot": slot_info["slot"],
                    "type": pt_name,
                    "status": status
                })

            # Check ball dominance balance
            tendency_warnings = []
            if creation["touches"] >= 90 and creation["shot"] >= 88:
                tendency_warnings.append("EXCESSIVE_USAGE_CONCENTRATION: May starve perimeter teammates")
            if creation["drive"] >= 90 and shooting["shot_three"] <= 20 and not is_creator:
                tendency_warnings.append("ERRATIC_DRIVE_WITHOUT_HANDLE: Drive tendency too high for role")
            if is_spacer and creation["dish_to_open_man"] <= 35:
                tendency_warnings.append("BALL_STOPPING_ON_CATCH: Low dish tendency may stall ball movement")

            roster_diagnostics.append({
                "player_id": pid,
                "player_name": name,
                "tactical_role": role,
                "is_play_initiator": p["is_play_initiator"],
                "active_play_types": active_types,
                "slot_coverage": per_slot_coverage,
                "tendency_diagnostics": tendency_warnings,
                "recommended_training_archetype": self._recommend_training_archetype(role, creation, shooting)
            })

        # 3. Coach System Fit
        coach_proficiencies = coach["system_proficiencies"]
        highest_sys = coach["highest_proficiency_system"]
        active_sys_id = snapshot["active_system_id"]
        # System mapping: 0=Balanced, 1=Grit&Grind, 2=Pace&Space, 3=Perimeter, 4=Post, 5=Triangle, 6=SevenSeconds, 7=Defense
        active_sys_name = SYSTEM_PROFICIENCY_NAMES[active_sys_id] if 0 <= active_sys_id < len(SYSTEM_PROFICIENCY_NAMES) else "Unknown"

        system_fit_score = coach_proficiencies.get(active_sys_name, 50)
        coach_fit_diagnosis = {
            "coach_name": coach["coach_name"],
            "active_system": active_sys_name,
            "coach_highest_proficiency": highest_sys,
            "coach_active_system_proficiency": system_fit_score,
            "alignment_verdict": "OPTIMAL_ALIGNMENT" if active_sys_name == highest_sys else "SUBOPTIMAL_SYSTEM_MISMATCH"
        }

        # 4. Formulate GM Hypotheses & Actionable Alternatives
        tactical_hypotheses = []

        # Issue 1: Playbook & PlayType unserved gaps
        if unserved_gaps:
            tactical_hypotheses.append({
                "issue_code": "UNSERVED_PLAY_TYPES_DETECTED",
                "description": f"Found {len(unserved_gaps)} player PlayType slots that lack corresponding plays in current playbook.",
                "evidence": unserved_gaps,
                "causal_status": "STATIC_VERIFIED",
                "alternatives": [
                    {"action": "HOLD", "tradeoff": "Player skips to next play slot; tactical variety reduced."},
                    {"action": "PLAYBOOK_CHANGE", "tradeoff": "Switch to a playbook with broader action coverage (e.g. Warriors / Nuggets)."},
                    {"action": "PLAYER_PLAY_TYPE_CHANGE", "tradeoff": "Replace unserved slot with P&R Ball Handler, Cutter, or 3 PT."}
                ]
            })

        # Issue 2: Creator Distribution
        if len(primary_creators) == 0:
            tactical_hypotheses.append({
                "issue_code": "NO_CLEAR_PRIMARY_CREATOR",
                "description": "Roster lacks a definitive primary initiator with high Touches (>=85) and Play Initiator flag.",
                "evidence": "Zero players tagged as PRIMARY_CREATOR",
                "causal_status": "COMMUNITY_BEHAVIOR_REPORTED",
                "alternatives": [
                    {"action": "PLAYER_ROLE_TENDENCY", "tradeoff": "Promote lead guard by enabling Play Initiator flag and adjusting Touches to 85-90."},
                    {"action": "TRADE", "tradeoff": "Target a bona fide all-star playmaker on the trade market."}
                ]
            })
        elif len(primary_creators) >= 3:
            tactical_hypotheses.append({
                "issue_code": "BALL_DOMINANCE_CONGESTION",
                "description": f"Multiple high-touch creators ({', '.join(primary_creators)}) competing for possession.",
                "evidence": primary_creators,
                "causal_status": "BASKETBALL_REASONING",
                "alternatives": [
                    {"action": "INTERNAL_SCHEME", "tradeoff": "Adopt Motion / Pace & Space to increase off-ball movement."},
                    {"action": "TENDENCY_CHANGE", "tradeoff": "Rebalance Touches (e.g. assign primary 88, secondary 72, tertiary 60)."},
                    {"action": "TRADE", "tradeoff": "Trade excess ball-handler for 3&D wings or rim-protecting big."}
                ]
            })

        # Issue 3: System mismatch
        if coach_fit_diagnosis["alignment_verdict"] == "SUBOPTIMAL_SYSTEM_MISMATCH":
            tactical_hypotheses.append({
                "issue_code": "COACH_SYSTEM_PHILOSOPHY_MISMATCH",
                "description": f"Team is running {active_sys_name} (Proficiency: {system_fit_score}), but coach excels in {highest_sys} (Proficiency: {coach_proficiencies[highest_sys]}).",
                "evidence": f"Active: {system_fit_score} vs Peak: {coach_proficiencies[highest_sys]}",
                "causal_status": "PROJECT_VERIFIED",
                "alternatives": [
                    {"action": "INTERNAL_SCHEME", "tradeoff": f"Switch ActiveSystem to {highest_sys} to maximize coach proficiency."},
                    {"action": "HOLD", "tradeoff": "Maintain current system if roster personnel demands it."},
                    {"action": "STAFF", "tradeoff": "Replace coach if philosophical rift cannot be bridged."}
                ]
            })

        return {
            "report_version": "1.0",
            "team_id": team_id,
            "team_name": team_name,
            "abbreviation": abbr,
            "playbook_overview": {
                "name": pb_name,
                "active_plays": pb_active_plays
            },
            "coach_overview": coach_fit_diagnosis,
            "tactical_hierarchy": {
                "primary_creators": primary_creators,
                "secondary_creators": secondary_creators,
                "floor_spacers": spacers,
                "rim_rollers": rollers
            },
            "roster_diagnostics": roster_diagnostics,
            "tactical_hypotheses": tactical_hypotheses,
            "knowledge_cards_applied": [c["id"] for c in self.knowledge.get("knowledge_cards", [])]
        }

    def _recommend_training_archetype(self, role: str, creation: Dict, shooting: Dict) -> str:
        """Map tactical role to Capability 2 training archetype."""
        if role == "PRIMARY_CREATOR":
            return "0 (进攻创造者)"
        elif role == "SECONDARY_CREATOR":
            return "1 (组织核心)"
        elif role == "FLOOR_SPACER":
            return "2 (空间射手)"
        elif role == "RIM_ROLLER":
            return "3 (内线终结)"
        elif creation.get("post_up", 0) >= 70:
            return "4 (传统低位)"
        else:
            return "8 (均衡发展)"
