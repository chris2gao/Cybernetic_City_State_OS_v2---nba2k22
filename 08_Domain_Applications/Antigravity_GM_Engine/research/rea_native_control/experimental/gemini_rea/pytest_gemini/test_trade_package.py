import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from trade_package_codec import (
    TradePackageCodec,
    TradePackage,
    TradeAsset
)

def test_salary_matching_legal_two_team():
    # Team 1 trades $10M player to Team 2 for $12M player
    # Band for $10M: outgoing + $5.0M = $15.0M max incoming. $12M <= $15M -> Legal.
    pkg = TradePackage(
        participating_teams=[1, 2],
        assets=[
            TradeAsset(asset_type="PLAYER", asset_id=101, from_team_id=1, to_team_id=2, salary=10000000),
            TradeAsset(asset_type="PLAYER", asset_id=202, from_team_id=2, to_team_id=1, salary=12000000),
        ]
    )
    valid, msg = pkg.validate_salary_matching()
    assert valid is True
    assert msg == "Valid"

def test_salary_matching_illegal_mismatch():
    # Team 1 trades $3M player to Team 2 for $25M player (Severe mismatch)
    pkg = TradePackage(
        participating_teams=[1, 2],
        assets=[
            TradeAsset(asset_type="PLAYER", asset_id=101, from_team_id=1, to_team_id=2, salary=3000000),
            TradeAsset(asset_type="PLAYER", asset_id=202, from_team_id=2, to_team_id=1, salary=25000000),
        ]
    )
    valid, msg = pkg.validate_salary_matching()
    assert valid is False
    assert "exceeds allowed max" in msg

def test_three_team_trade_serialization():
    pkg = TradePackage(
        participating_teams=[1, 2, 3],
        assets=[
            TradeAsset(asset_type="PLAYER", asset_id=101, from_team_id=1, to_team_id=2, salary=8000000),
            TradeAsset(asset_type="PICK", asset_id=501, from_team_id=2, to_team_id=3, salary=0),
            TradeAsset(asset_type="PLAYER", asset_id=301, from_team_id=3, to_team_id=1, salary=7500000),
        ]
    )
    serialized = TradePackageCodec.serialize_trade_package(pkg)
    assert serialized["teams"] == [1, 2, 3]
    assert serialized["asset_count"] == 3
    assert len(serialized["assets"]) == 3
