"""Offline unit tests for W02-B: 18 Individual Defensive Matchup settings.

Tests cover default initialization (0x280000), adjacent bit isolation,
legal enum values for all 18 fields, and byte roundtrip serialization.
"""

import pytest

from ..defense_18_codec import (
    DEFENSIVE_18_SPECS,
    DEFENSIVE_SPECS_MAP,
    DEFAULT_WORD1,
    DEFAULT_WORD2_LOW11,
    DoubleTeamPerimeter,
    DoubleTeamPost,
    ForceDirection,
    HelpSetting,
    Matchup18DefenseSettings,
    OffballScreenDefense,
    PostDefense,
    PressureOffball,
    PressureOnball,
    ScreenDefenseHedge,
    ScreenDefenseHedge5,
    ScreenDefenseOnBall,
    ScreenDefenseOnBall5,
    SwitchRule,
    YesNoSetting,
)


class TestDefense18Codec:
    def test_specs_count(self):
        assert len(DEFENSIVE_18_SPECS) == 18

    def test_default_initialization(self):
        settings = Matchup18DefenseSettings()
        w1, w2 = settings.pack()
        assert w1 == DEFAULT_WORD1  # 0x00280000
        assert (w2 & 0x7FF) == DEFAULT_WORD2_LOW11  # 0x00000000
        assert settings.get("DoubleTeamPerimeter") == DoubleTeamPerimeter.MANUAL
        assert settings.get("DoubleTeamPost") == DoubleTeamPost.MANUAL
        assert settings.get("PressureOnball") == PressureOnball.AUTO

    def test_bit_packing_and_adjacent_isolation(self):
        """Mutate each of the 18 fields and verify zero adjacent bit corruption."""
        base = Matchup18DefenseSettings()
        w1_base, w2_base = base.pack()

        for spec in DEFENSIVE_18_SPECS:
            settings = Matchup18DefenseSettings()
            max_val = (1 << spec.width) - 1
            test_val = max_val  # Set to maximum allowed bits

            settings.set(spec.name, test_val)
            w1_mut, w2_mut = settings.pack()

            # Verify that only the target bits changed
            if spec.word_index == 0:
                diff = w1_mut ^ w1_base
                assert diff == (test_val ^ spec.default_value) << spec.start_bit
                assert w2_mut == w2_base
            else:
                diff = w2_mut ^ w2_base
                assert diff == (test_val ^ spec.default_value) << spec.start_bit
                assert w1_mut == w1_base

            # Unpack and verify all 18 fields
            recovered = Matchup18DefenseSettings.unpack(w1_mut, w2_mut)
            for other in DEFENSIVE_18_SPECS:
                if other.name == spec.name:
                    assert int(recovered.get(other.name)) == test_val
                else:
                    assert int(recovered.get(other.name)) == other.default_value

    def test_8byte_roundtrip(self):
        settings = Matchup18DefenseSettings()
        settings.set("PressureOnball", PressureOnball.SMOTHER)
        settings.set("PressureOffball", PressureOffball.DENY_BALL)
        settings.set("ForceDirection", ForceDirection.BASELINE)
        settings.set("ScreenDefenseOnBall", ScreenDefenseOnBall.SWITCH)
        settings.set("ScreenDefenseHedge", ScreenDefenseHedge.SOFT_HEDGE)
        settings.set("OffballScreenDefense", OffballScreenDefense.GO_UNDER)
        settings.set("PostDefense", PostDefense.FRONT)
        settings.set("DoubleTeamPerimeter", DoubleTeamPerimeter.ON_CATCH)
        settings.set("DoubleTeamPost", DoubleTeamPost.ON_DRIBBLE)
        settings.set("ScreenDefenseOnBall5", ScreenDefenseOnBall5.ICE)
        settings.set("ScreenDefenseHedge5", ScreenDefenseHedge5.CATCH_HEDGE)
        settings.set("SwitchRule", SwitchRule.SWITCH_ALL)
        settings.set("OnballHelp", HelpSetting.NO_HELP)
        settings.set("ScreenHelp", HelpSetting.HELP)
        settings.set("ExtendPressure", YesNoSetting.YES)
        settings.set("TagOnRoll", YesNoSetting.NO)
        settings.set("StayAttached", YesNoSetting.YES)
        settings.set("PreRotate", True)

        raw = settings.pack_bytes()
        assert len(raw) == 8

        unpacked = Matchup18DefenseSettings.unpack_bytes(raw)
        assert unpacked.get("PressureOnball") == PressureOnball.SMOTHER
        assert unpacked.get("PressureOffball") == PressureOffball.DENY_BALL
        assert unpacked.get("ForceDirection") == ForceDirection.BASELINE
        assert unpacked.get("ScreenDefenseOnBall") == ScreenDefenseOnBall.SWITCH
        assert unpacked.get("ScreenDefenseHedge") == ScreenDefenseHedge.SOFT_HEDGE
        assert unpacked.get("OffballScreenDefense") == OffballScreenDefense.GO_UNDER
        assert unpacked.get("PostDefense") == PostDefense.FRONT
        assert unpacked.get("DoubleTeamPerimeter") == DoubleTeamPerimeter.ON_CATCH
        assert unpacked.get("DoubleTeamPost") == DoubleTeamPost.ON_DRIBBLE
        assert unpacked.get("ScreenDefenseOnBall5") == ScreenDefenseOnBall5.ICE
        assert unpacked.get("ScreenDefenseHedge5") == ScreenDefenseHedge5.CATCH_HEDGE
        assert unpacked.get("SwitchRule") == SwitchRule.SWITCH_ALL
        assert unpacked.get("OnballHelp") == HelpSetting.NO_HELP
        assert unpacked.get("ScreenHelp") == HelpSetting.HELP
        assert unpacked.get("ExtendPressure") == YesNoSetting.YES
        assert unpacked.get("TagOnRoll") == YesNoSetting.NO
        assert unpacked.get("StayAttached") == YesNoSetting.YES
        assert unpacked.get("PreRotate") is True
