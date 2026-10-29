"""Unit tests for GREA-01 Opponent Gameplan Codec, Multi-Opponent Isolation, and Call Chain.

This test runs strictly offline without requiring a live game process.
"""

import pytest

from ..gameplan_opponent import (
    AUTO_UID,
    GAMEPLAN_SIZE,
    MANAGER_DIRTY_FLAG_COACH_SYNC,
    MANAGER_DIRTY_FLAG_GAMEPLAN,
    MANAGER_OPPONENT_SLOTS_COUNT,
    MANAGER_SIZE,
    MATCHUP_COUNT,
    MATCHUP_STRIDE,
    OFFSET_IS_IN_USE,
    OFFSET_MATCHUPS,
    OFFSET_OPPONENT_TEAM_ID,
    OFFSET_OWNER_TEAM_ID,
    OFFSET_TAIL_AFTER_MATCHUPS,
    ForceDirection,
    FranchiseGameplanManager,
    MatchupDefensiveSettings,
    OpponentGameplan,
    OpponentMatchupEntry,
    PressureOffball,
    PressureOnball,
    ScreenDefenseHedge,
    ScreenDefenseOnBall,
)
from ..native_call_chain import (
    EvidenceMaturity,
    NATIVE_CALL_CHAIN_SPECS,
    OpponentGameplanTransactionHarness,
)


class TestGameplanBinaryLayout:
    """Verifies that the decoded structures match NBA 2K22 binary specifications."""

    def test_gameplan_total_size(self):
        assert GAMEPLAN_SIZE == 880  # 0x370
        assert OFFSET_MATCHUPS == 0x64  # 100 decimal
        assert MATCHUP_COUNT == 23
        assert MATCHUP_STRIDE == 12
        assert OFFSET_TAIL_AFTER_MATCHUPS == 0x64 + (23 * 12)  # 0x178 (376 decimal)

    def test_empty_gameplan_pack_unpack(self):
        gp = OpponentGameplan(owner_team_id=11, opponent_team_id=20)
        raw = gp.pack()
        assert len(raw) == 880

        unpacked = OpponentGameplan.unpack(raw)
        assert unpacked.is_in_use == 0
        assert unpacked.owner_team_id == 11
        assert unpacked.opponent_team_id == 20
        assert len(unpacked.matchups) == 23
        for m in unpacked.matchups:
            assert m.opponent_player_uid == AUTO_UID
            assert m.assigned_defender_uid == AUTO_UID
            assert m.defensive_settings.pressure_onball == PressureOnball.AUTO

    def test_manager_total_size_and_slots(self):
        assert MANAGER_SIZE == 0x13E70  # 81,520 bytes
        assert MANAGER_OPPONENT_SLOTS_COUNT == 35

        mgr = FranchiseGameplanManager(team_record_index=1, team_id=11)
        raw = mgr.pack()
        assert len(raw) == MANAGER_SIZE

        unpacked = FranchiseGameplanManager.unpack(raw)
        assert unpacked.team_record_index == 1
        assert unpacked.team_id == 11
        assert len(unpacked.slots) == 35
        assert unpacked.default_gameplan.opponent_team_id == AUTO_UID


class TestDefensiveSettingsBitfieldCodec:
    """Verifies bitfield packing and unpacking for PressureOnball and neighboring fields."""

    @pytest.mark.parametrize(
        "pressure",
        [
            PressureOnball.AUTO,
            PressureOnball.GAP,
            PressureOnball.MODERATE,
            PressureOnball.TIGHT,
            PressureOnball.SMOTHER,
        ],
    )
    def test_pressure_onball_roundtrip(self, pressure):
        settings = MatchupDefensiveSettings(pressure_onball=pressure)
        w1 = settings.pack_word1()

        # Check raw bits (0..2)
        assert (w1 & 0x7) == int(pressure)

        # Unpack back
        unpacked_settings = MatchupDefensiveSettings()
        MatchupDefensiveSettings.unpack_word1(w1, unpacked_settings)
        assert unpacked_settings.pressure_onball == pressure

    def test_neighboring_bitfield_isolation(self):
        """Verifies changing PressureOnball does not touch PressureOffball, ForceDirection, etc."""
        settings = MatchupDefensiveSettings(
            pressure_onball=PressureOnball.SMOTHER,  # bits 0..2 = 4 (0b100)
            pressure_offball=PressureOffball.DENY,   # bits 3..5 = 3 (0b011)
            force_direction=ForceDirection.BASELINE, # bits 6..7 = 2 (0b10)
            screen_defense_onball=ScreenDefenseOnBall.SWITCH, # bits 8..10 = 3
            screen_defense_hedge=ScreenDefenseHedge.SOFT_HEDGE, # bits 11..13 = 2
        )
        w1 = settings.pack_word1()

        unpacked = MatchupDefensiveSettings()
        MatchupDefensiveSettings.unpack_word1(w1, unpacked)

        assert unpacked.pressure_onball == PressureOnball.SMOTHER
        assert unpacked.pressure_offball == PressureOffball.DENY
        assert unpacked.force_direction == ForceDirection.BASELINE
        assert unpacked.screen_defense_onball == ScreenDefenseOnBall.SWITCH
        assert unpacked.screen_defense_hedge == ScreenDefenseHedge.SOFT_HEDGE

        # Mutate only pressure_onball to GAP
        unpacked.pressure_onball = PressureOnball.GAP
        w1_new = unpacked.pack_word1()

        reunpacked = MatchupDefensiveSettings()
        MatchupDefensiveSettings.unpack_word1(w1_new, reunpacked)
        assert reunpacked.pressure_onball == PressureOnball.GAP
        # Neighbors remain completely preserved
        assert reunpacked.pressure_offball == PressureOffball.DENY
        assert reunpacked.force_direction == ForceDirection.BASELINE
        assert reunpacked.screen_defense_onball == ScreenDefenseOnBall.SWITCH
        assert reunpacked.screen_defense_hedge == ScreenDefenseHedge.SOFT_HEDGE


class TestMultiOpponentIsolationInvariance:
    """Critical test: modifying gameplan for one opponent MUST NOT affect other opponents."""

    def test_multi_opponent_data_isolation(self):
        # IND Pacers (team_id=11)
        mgr = FranchiseGameplanManager(team_record_index=11, team_id=11)

        # 1. Setup opponent A: PHI 76ers (team_id=20)
        gp_phi = mgr.ensure_opponent_gameplan(opponent_team_id=20)
        gp_phi.set_onball_pressure(opponent_player_uid=101, pressure=PressureOnball.SMOTHER, assigned_defender_uid=301)
        gp_phi.set_onball_pressure(opponent_player_uid=102, pressure=PressureOnball.TIGHT, assigned_defender_uid=302)
        mgr.commit_gameplan(opponent_team_id=20)

        # 2. Setup opponent B: MIL Bucks (team_id=15)
        gp_mil = mgr.ensure_opponent_gameplan(opponent_team_id=15)
        gp_mil.set_onball_pressure(opponent_player_uid=201, pressure=PressureOnball.GAP, assigned_defender_uid=301)
        mgr.commit_gameplan(opponent_team_id=15)

        # 3. Setup opponent C: BKN Nets (team_id=2)
        gp_bkn = mgr.ensure_opponent_gameplan(opponent_team_id=2)
        gp_bkn.set_onball_pressure(opponent_player_uid=401, pressure=PressureOnball.MODERATE, assigned_defender_uid=305)
        mgr.commit_gameplan(opponent_team_id=2)

        # Pack full 81,520 bytes binary buffer and deserialize
        serialized_manager = mgr.pack()
        deserialized_mgr = FranchiseGameplanManager.unpack(serialized_manager)

        # Verify PHI Gameplan
        phi_recovered = deserialized_mgr.find_opponent_gameplan(20)
        assert phi_recovered is not None
        assert phi_recovered.is_in_use == 1
        m_101 = phi_recovered.find_or_create_matchup(101)
        assert m_101.defensive_settings.pressure_onball == PressureOnball.SMOTHER
        assert m_101.assigned_defender_uid == 301
        m_102 = phi_recovered.find_or_create_matchup(102)
        assert m_102.defensive_settings.pressure_onball == PressureOnball.TIGHT
        assert m_102.assigned_defender_uid == 302

        # Verify MIL Gameplan
        mil_recovered = deserialized_mgr.find_opponent_gameplan(15)
        assert mil_recovered is not None
        assert mil_recovered.is_in_use == 1
        m_201 = mil_recovered.find_or_create_matchup(201)
        assert m_201.defensive_settings.pressure_onball == PressureOnball.GAP
        assert m_201.assigned_defender_uid == 301

        # Verify BKN Gameplan
        bkn_recovered = deserialized_mgr.find_opponent_gameplan(2)
        assert bkn_recovered is not None
        assert bkn_recovered.is_in_use == 1
        m_401 = bkn_recovered.find_or_create_matchup(401)
        assert m_401.defensive_settings.pressure_onball == PressureOnball.MODERATE

        # Verify Default Gameplan (Slot 35) remains untouched
        default_gp = deserialized_mgr.default_gameplan
        assert default_gp.is_in_use == 0
        assert default_gp.opponent_team_id == AUTO_UID
        for m in default_gp.matchups:
            assert m.defensive_settings.pressure_onball == PressureOnball.AUTO

        # Verify remaining unused slots (32 slots) remain pristine
        unused_count = sum(1 for slot in deserialized_mgr.slots if slot.opponent_team_id == AUTO_UID)
        assert unused_count == 35 - 3  # exactly 32 unused slots


class TestTransactionHarnessAndNativeCallChain:
    """Verifies that the transaction simulation conforms to the native assembly call chain."""

    def test_transaction_harness_execution(self):
        mgr = FranchiseGameplanManager(team_record_index=0, team_id=11)
        harness = OpponentGameplanTransactionHarness(mgr)

        result = harness.execute_modify_opponent_onball_pressure(
            opponent_team_id=20,
            opponent_player_uid=101,
            pressure=PressureOnball.SMOTHER,
            assigned_defender_uid=301,
        )

        assert result["status"] == "SUCCESS"
        assert result["owner_team_id"] == 11
        assert result["opponent_team_id"] == 20
        assert result["opponent_player_uid"] == 101
        assert result["pressure_onball"] == "SMOTHER"
        assert result["is_in_use"] == 1
        assert result["flushed_flags"] == (MANAGER_DIRTY_FLAG_GAMEPLAN | MANAGER_DIRTY_FLAG_COACH_SYNC)

        # Check call chain step order
        log = result["call_log"]
        assert any("0x1244230 EnsureOpponentGameplan" in step for step in log)
        assert any("0x14651c0 InsertOrFindOpponentMatchup" in step for step in log)
        assert any("MUTATE MatchupDefensiveSettings" in step for step in log)
        assert any("0x146ec50 ApplyToCoach" in step for step in log)
        assert any("WRITE GAMEPLAN+0x0: IsInUse = 1" in step for step in log)
        assert any("0x131f110 CommitPendingFlags" in step for step in log)

    def test_native_specs_coverage(self):
        assert len(NATIVE_CALL_CHAIN_SPECS) >= 7
        rvs = [spec.rva for spec in NATIVE_CALL_CHAIN_SPECS]
        assert "0xfda730" in rvs
        assert "0x1244230" in rvs
        assert "0x12f21a0" in rvs
        assert "0x146c260" in rvs
        assert "0x14651c0" in rvs
        assert "0x146ec50" in rvs
        assert "0x131f110" in rvs
        assert "0x7a7840" in rvs

        for spec in NATIVE_CALL_CHAIN_SPECS:
            assert spec.evidence_maturity in [
                EvidenceMaturity.LIVE_VERIFIED,
                EvidenceMaturity.STATIC_DISASSEMBLED,
                EvidenceMaturity.STATIC_CROSS_REFERENCED,
                EvidenceMaturity.OFFLINE_SIMULATED,
            ]
            assert spec.rva.startswith("0x")
            assert len(spec.parameters) > 0 or spec.rva == "0x146c260"
