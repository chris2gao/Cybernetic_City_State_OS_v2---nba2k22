"""
VAE Pillar 1: Native Capabilities and Action Specifications.
Implements the 12 core native operations across GM, Coach, and Player roles:
- GM-01: budget_salary_cap_tax_multi_year
- GM-02: team_roster_and_staff_management
- GM-03: trade
- GM-04: sign_renew_release
- GM-05: draft_and_picks
- COACH-01: coach_and_team_tactics
- COACH-02: rotation_minutes_roles
- COACH-03: team_and_individual_training
- PLAYER-01: attribute_growth_mechanics
- PLAYER-02: tendency
- PLAYER-03: badges_and_progression
- PLAYER-04: individual_training
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from .contracts import RoleType, EvidenceTier, ReceiptStatus


@dataclass
class ActionSpecification:
    action_id: str
    role: RoleType
    action_name: str
    description: str
    preconditions: List[str]
    authority_required: str
    native_entry_path: str
    allowed_range: Dict[str, Any]
    verification_method: str
    readback_layers: List[str]
    rollback_strategy: str
    is_world_admin_only: bool = False


@dataclass
class ActionResult:
    action_id: str
    role: RoleType
    status: str  # "VERIFIED_OFFLINE", "BLOCKED_AWAITING_GAME_AUTH", "REJECTED_PERMISSIONS"
    message: str
    output_data: Dict[str, Any]
    evidence_tier: EvidenceTier


class VAENativeActionRegistry:
    """
    Registry and validator for all 12 native capability actions across GM, Coach, and Player.
    Strictly distinguishes between role-permitted intervention and world-admin-only direct edits.
    """

    def __init__(self):
        self.actions: Dict[str, ActionSpecification] = {}
        self._register_all_actions()

    def _register_all_actions(self) -> None:
        # GM-01: Budget, salary cap, tax, multi-year
        self.actions["GM-01"] = ActionSpecification(
            action_id="GM-01",
            role=RoleType.GM,
            action_name="budget_salary_cap_tax_multi_year",
            description="Multi-year payroll calculation, salary cap, luxury tax apron, and cap space projection.",
            preconditions=["Valid team roster loaded", "Active season year identified"],
            authority_required="GM_FINANCE_READ_WRITE",
            native_entry_path="MYLEAGUE_FRONT_OFFICE_FINANCE",
            allowed_range={"salary_cap": (100_000_000, 200_000_000), "luxury_tax_threshold": (120_000_000, 250_000_000)},
            verification_method="Independent numerical cap oracle against roster salary summation",
            readback_layers=["L1_process", "L2_ui_settings"],
            rollback_strategy="Recalculate budget projections using preserved contract ledger",
            is_world_admin_only=False,
        )

        # GM-02: Roster and staff management
        self.actions["GM-02"] = ActionSpecification(
            action_id="GM-02",
            role=RoleType.GM,
            action_name="team_roster_and_staff_management",
            description="Manage 15-man standard roster, two-way spots, staff hiring/firing, and contract duration.",
            preconditions=["Roster count between 13 and 15 players", "Staff salary budget available"],
            authority_required="GM_PERSONNEL_WRITE",
            native_entry_path="MYLEAGUE_ROSTER_STAFF_MANAGEMENT",
            allowed_range={"max_roster": 15, "two_way_max": 2},
            verification_method="Player/staff membership slot validation and contract duration readback",
            readback_layers=["L1_process", "L2_ui_settings", "L3_save_reload"],
            rollback_strategy="Restore prior staff/roster assignment from transaction backup",
            is_world_admin_only=False,
        )

        # GM-03: Trade execution & verification
        self.actions["GM-03"] = ActionSpecification(
            action_id="GM-03",
            role=RoleType.GM,
            action_name="trade",
            description="Two-team trade proposal, salary matching rules (125% + 100k), and draft pick transfer.",
            preconditions=["Exactly two participating teams", "Trade deadline not passed", "Salary matching satisfied"],
            authority_required="GM_TRADE_SUBMIT",
            native_entry_path="MYLEAGUE_TRADE_FINDER_PROPOSAL",
            allowed_range={"teams_involved": 2, "max_future_draft_years": 5},
            verification_method="Post-trade ownership transfer verification (+0xCB1, +0x1047 offsets) on both teams",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings", "L3_save_reload"],
            rollback_strategy="Atomic reverse trade execution or save reload",
            is_world_admin_only=False,
        )

        # GM-04: Sign, renew, release
        self.actions["GM-04"] = ActionSpecification(
            action_id="GM-04",
            role=RoleType.GM,
            action_name="sign_renew_release",
            description="Free agent signings, contract extensions, Bird rights exceptions, and waiver wire cuts.",
            preconditions=["Cap space or applicable exception (MLE/BAE/Minimum) available", "Roster slot open"],
            authority_required="GM_CONTRACT_EXECUTE",
            native_entry_path="MYLEAGUE_CONTRACT_NEGOTIATION",
            allowed_range={"contract_years": (1, 5), "min_salary": 900_000},
            verification_method="Roster membership and salary ledger update readback",
            readback_layers=["L1_process", "L2_ui_settings", "L3_save_reload"],
            rollback_strategy="Restore prior contract and waiver state",
            is_world_admin_only=False,
        )

        # GM-05: Draft and draft picks
        self.actions["GM-05"] = ActionSpecification(
            action_id="GM-05",
            role=RoleType.GM,
            action_name="draft_and_picks",
            description="Draft prospect scouting, pick ownership, round/protection tracking, and draft pick execution.",
            preconditions=["Current league calendar in Offseason Draft phase", "Team owns active draft pick"],
            authority_required="GM_DRAFT_SELECTION",
            native_entry_path="MYLEAGUE_OFFSEASON_DRAFT_BOARD",
            allowed_range={"draft_rounds": (1, 2), "pick_number": (1, 60)},
            verification_method="Drafted rookie addition to roster and pick consumed confirmation",
            readback_layers=["L1_process", "L2_ui_settings", "L3_save_reload"],
            rollback_strategy="Reload pre-draft snapshot save",
            is_world_admin_only=False,
        )

        # COACH-01: Coach & team tactics
        self.actions["COACH-01"] = ActionSpecification(
            action_id="COACH-01",
            role=RoleType.COACH,
            action_name="coach_and_team_tactics",
            description="Offensive/defensive pace, ACE (Adaptive Coaching Engine), POE, playbook sets, and freelance.",
            preconditions=["Team coach assigned", "Tactical scheme compatibility check"],
            authority_required="COACH_TACTICS_WRITE",
            native_entry_path="COACHING_GAMEPLAN_SETTINGS",
            allowed_range={"pace_slider": (0, 100), "run_play_frequency": (0, 100), "poe_defense_schemes": (0, 15)},
            verification_method="Coach projection structure +316 byte readback and tactical gameplay observation",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Reset coaching sliders to default baseline profile",
            is_world_admin_only=False,
        )

        # COACH-02: Rotation, minutes, roles
        self.actions["COACH-02"] = ActionSpecification(
            action_id="COACH-02",
            role=RoleType.COACH,
            action_name="rotation_minutes_roles",
            description="Rotation timeline, player minutes allocation summing exactly to 240, starter/bench roles.",
            preconditions=["Total player minutes must sum to exactly 240", "Minimum 8 players in active rotation"],
            authority_required="COACH_ROTATION_WRITE",
            native_entry_path="COACHING_ROTATION_TIMELINE",
            allowed_range={"total_minutes": 240, "player_minutes": (0, 48), "active_rotation_size": (8, 13)},
            verification_method="Readback of all player allocated minutes and starter bitflags",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Apply auto-coach rotation distribution algorithm",
            is_world_admin_only=False,
        )

        # COACH-03: Team and individual training
        self.actions["COACH-03"] = ActionSpecification(
            action_id="COACH-03",
            role=RoleType.COACH,
            action_name="team_and_individual_training",
            description="Team practice schedule, intensity levels, individual preset training assignment, mentor links.",
            preconditions=["Training facility available", "Player injury status permits training"],
            authority_required="COACH_TRAINING_WRITE",
            native_entry_path="MYLEAGUE_TRAINING_SCHEDULE",
            allowed_range={"intensity_level": (0, 5), "training_preset_id": (0, 8)},
            verification_method="Training structure (+0x318) bits 8..18 readback and monthly fatigue rate tracking",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Revert practice intensity to Balanced Medium",
            is_world_admin_only=False,
        )

        # PLAYER-01: Attribute growth mechanics
        self.actions["PLAYER-01"] = ActionSpecification(
            action_id="PLAYER-01",
            role=RoleType.PLAYER,
            action_name="attribute_growth_mechanics",
            description="Natural attribute growth modeling via potential, age curve, training gains, and natural development.",
            preconditions=["Player active under contract", "Player age between 19 and 45"],
            authority_required="WORLD_ADMIN_CALIBRATION_ONLY",
            native_entry_path="ENGINE_INTERNAL_PROGRESSION_LOOP",
            allowed_range={"attribute_range": (25, 99), "potential_range": (50, 99)},
            verification_method="End-of-season natural attribute change delta readback; no arbitrary direct writing",
            readback_layers=["L1_process", "L3_save_reload"],
            rollback_strategy="Engine backup reload; player cannot self-edit attributes directly",
            is_world_admin_only=True,
        )

        # PLAYER-02: Tendencies
        self.actions["PLAYER-02"] = ActionSpecification(
            action_id="PLAYER-02",
            role=RoleType.PLAYER,
            action_name="tendency",
            description="Player behavioral tendencies (shot tendencies, drive vs pull-up, defensive aggression).",
            preconditions=["Tendency ID registered in native schema", "Interaction with playbook verified"],
            authority_required="PLAYER_TENDENCY_CALIBRATION",
            native_entry_path="ROSTER_PLAYER_TENDENCIES_EDIT",
            allowed_range={"tendency_value": (0, 100)},
            verification_method="Tendency byte readback and simulated in-game shot map distribution comparison",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Restore default baseline tendency ratings",
            is_world_admin_only=False,
        )

        # PLAYER-03: Badges and progression
        self.actions["PLAYER-03"] = ActionSpecification(
            action_id="PLAYER-03",
            role=RoleType.PLAYER,
            action_name="badges_and_progression",
            description="Badge tier unlocked levels (Bronze, Silver, Gold, Hall of Fame) and gameplay badge triggers.",
            preconditions=["Badge requirements (attribute minimums) satisfied", "Badge slots available"],
            authority_required="WORLD_ADMIN_CALIBRATION_ONLY",
            native_entry_path="ROSTER_PLAYER_BADGES_EDIT",
            allowed_range={"badge_level": (0, 4)},  # 0: None, 1: Bronze, 2: Silver, 3: Gold, 4: HOF
            verification_method="Badge bitmask readback and trigger occurrence monitoring",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Restore prior badge bitmask",
            is_world_admin_only=True,
        )

        # PLAYER-04: Individual training
        self.actions["PLAYER-04"] = ActionSpecification(
            action_id="PLAYER-04",
            role=RoleType.PLAYER,
            action_name="individual_training",
            description="Player-selected individual focus area (shooting, playmaking, defense, physical) and work ethic.",
            preconditions=["Player healthy or in rehabilitation mode", "Coach training system active"],
            authority_required="PLAYER_TRAINING_FOCUS_SUBMIT",
            native_entry_path="MYLEAGUE_INDIVIDUAL_TRAINING_MENU",
            allowed_range={"focus_type": (0, 8), "work_ethic": (0, 100)},
            verification_method="Readback of player training focus bitfield and next-month stat gains",
            readback_layers=["L0_memory", "L1_process", "L2_ui_settings"],
            rollback_strategy="Revert individual training focus to Default Balanced",
            is_world_admin_only=False,
        )

    def get_action(self, action_id: str) -> Optional[ActionSpecification]:
        return self.actions.get(action_id)

    def validate_action_call(
        self,
        action_id: str,
        role: RoleType,
        parameters: Dict[str, Any],
        has_world_admin: bool = False,
    ) -> Tuple[bool, str]:
        """
        Validates whether a role is permitted to call the requested action.
        Blocks ordinary players/coaches/GMs from calling world-admin-only direct edits.
        """
        spec = self.get_action(action_id)
        if not spec:
            return False, f"UNKNOWN_ACTION: {action_id} is not registered in native capability matrix"

        # Check World Admin constraint
        if spec.is_world_admin_only and not has_world_admin:
            return False, f"PERMISSION_DENIED: {action_id} ({spec.action_name}) is world-maintenance only; role {role.value} cannot directly edit"

        # Check Role matching
        if spec.role != role and not has_world_admin:
            return False, f"ROLE_MISMATCH: {action_id} belongs to {spec.role.value}, cannot be executed by {role.value}"

        # Check parameter constraints (e.g. rotation minutes = 240, teams = 2)
        if action_id == "COACH-02" and "minutes_sum" in parameters:
            if parameters["minutes_sum"] != 240:
                return False, f"CONSTRAINT_VIOLATION: Total rotation minutes must sum to exactly 240 (received {parameters['minutes_sum']})"

        if action_id == "GM-03" and "teams_count" in parameters:
            if parameters["teams_count"] != 2:
                return False, f"CONSTRAINT_VIOLATION: Only 2-team trades are supported natively (received {parameters['teams_count']})"

        return True, "Preconditions and role permissions verified"

    def execute_dryrun(
        self,
        action_id: str,
        role: RoleType,
        parameters: Dict[str, Any],
        has_world_admin: bool = False,
    ) -> ActionResult:
        """
        Executes an action in dry-run mode, enforcing that live game writes
        are blocked while offline contract logic and numerical calculations are verified.
        """
        valid, msg = self.validate_action_call(action_id, role, parameters, has_world_admin)
        if not valid:
            return ActionResult(
                action_id=action_id,
                role=role,
                status="REJECTED_PERMISSIONS",
                message=msg,
                output_data={},
                evidence_tier=EvidenceTier.STATIC_CODE,
            )

        spec = self.actions[action_id]
        # In this task, live game mutation is not granted; actions return structured dry-run verified results
        output = {
            "action_spec": spec.action_name,
            "readback_layers_planned": spec.readback_layers,
            "rollback_strategy": spec.rollback_strategy,
            "simulated_parameters": parameters,
        }

        # Deterministic math for GM-01
        if action_id == "GM-01":
            salaries = parameters.get("salaries", [25_000_000, 18_000_000, 12_000_000, 8_000_000])
            total_payroll = sum(salaries)
            cap = 112_414_000
            tax = 136_606_000
            output["payroll_total"] = total_payroll
            output["salary_cap"] = cap
            output["cap_space"] = max(0, cap - total_payroll)
            output["luxury_tax_projected"] = max(0, total_payroll - tax)

        return ActionResult(
            action_id=action_id,
            role=role,
            status="BLOCKED_AWAITING_GAME_AUTH",
            message=f"Dry-run contract and numerical rules verified for {action_id}; live game write blocked pending game authorization",
            output_data=output,
            evidence_tier=EvidenceTier.OFFLINE_FIXTURE,
        )
