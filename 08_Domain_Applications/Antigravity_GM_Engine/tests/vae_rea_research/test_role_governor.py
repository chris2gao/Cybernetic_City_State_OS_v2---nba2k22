from __future__ import annotations

import pytest
from src.vae_rea_research.role_governor import NativeTacticalRoleGovernor, NativeRoleGovernorResult


def test_native_role_governor_franchise_core():
    """Branch A: Primary=3, Secondary=3 bypasses all limits."""
    result = NativeTacticalRoleGovernor.evaluate(
        role_tier=3,
        secondary_tier=3,
        raw_shot_tendency=99,
        raw_touches=95,
        raw_ratings=[90, 88, 85, 82, 80],
    )
    assert result.governor_branch == "BRANCH_A_FRANCHISE_CORE"
    assert result.effective_shot_tendency == 99
    assert result.effective_touches == 95
    assert result.scaled_ratings == [90, 88, 85, 82, 80]
    assert result.applied_multiplier == 1.0
    assert result.epistemological_tier == "STATIC_DISASSEMBLY_LEAD"
    assert result.gameplay_validation_status == "PENDING_GAMEPLAY_VALIDATION"


def test_native_role_governor_secondary_core_clamping():
    """Branch B: Primary=3, Secondary=2 clamps to (table[2] - 5) = (74 - 5) = 69."""
    # When raw tendency exceeds ceiling
    res_high = NativeTacticalRoleGovernor.evaluate(
        role_tier=3,
        secondary_tier=2,
        raw_shot_tendency=90,
        raw_touches=85,
        raw_ratings=[85, 85, 85, 85, 85],
    )
    assert res_high.governor_branch == "BRANCH_B_SECONDARY_CORE"
    assert res_high.applied_ceiling_or_floor == 69
    assert res_high.effective_shot_tendency == 69
    assert res_high.effective_touches == 69
    assert res_high.scaled_ratings == [85, 85, 85, 85, 85]

    # When raw tendency is below ceiling
    res_low = NativeTacticalRoleGovernor.evaluate(
        role_tier=3,
        secondary_tier=2,
        raw_shot_tendency=50,
        raw_touches=45,
    )
    assert res_low.effective_shot_tendency == 50
    assert res_low.effective_touches == 45


def test_native_role_governor_non_core_support_floor_and_ratings():
    """Branch C: Primary=1 applies floor table[1]=83 and multiplier 0.96 with banker's rounding."""
    res = NativeTacticalRoleGovernor.evaluate(
        role_tier=1,
        secondary_tier=1,
        raw_shot_tendency=30,  # Below floor 83
        raw_touches=25,       # Below floor 83
        raw_ratings=[100, 90, 80, 70, 60],
    )
    assert res.governor_branch == "BRANCH_C_NON_CORE_SUPPORT"
    assert res.applied_ceiling_or_floor == 83
    assert res.effective_shot_tendency == 83
    assert res.effective_touches == 83
    assert res.applied_multiplier == 0.96
    # 100*0.96=96, 90*0.96=86.4->86, 80*0.96=76.8->77, 70*0.96=67.2->67, 60*0.96=57.6->58
    assert res.scaled_ratings == [96, 86, 77, 67, 58]


def test_native_role_governor_domain_boundary_and_strict():
    """Tests out-of-range role tiers in strict and non-strict modes."""
    # Non-strict mode clamps safely
    res = NativeTacticalRoleGovernor.evaluate(
        role_tier=5,
        secondary_tier=-1,
        raw_shot_tendency=50,
        raw_touches=50,
        strict=False,
    )
    assert res.domain_clamped is True
    assert res.role_tier == 3
    assert res.secondary_tier == 0

    # Strict mode raises ValueError
    with pytest.raises(ValueError):
        NativeTacticalRoleGovernor.evaluate(
            role_tier=5,
            secondary_tier=0,
            raw_shot_tendency=50,
            raw_touches=50,
            strict=True,
        )


def test_native_role_governor_telemetry_spec():
    """Verifies telemetry contract schema conforms to semantic requirements without physical schemas."""
    spec = NativeTacticalRoleGovernor.create_telemetry_validation_spec()
    assert spec["target_mechanism"] == "TACTICAL_ROLE_HIERARCHY_GOVERNOR"
    assert spec["epistemological_status"] == "STATIC_DISASSEMBLY_LEAD"
    assert len(spec["required_metrics"]) >= 3
    # Verify no physical schema leak
    for m in spec["required_metrics"]:
        assert "sql_type" not in m
        assert "table_name" not in m
