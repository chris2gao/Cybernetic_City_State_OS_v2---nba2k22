import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from contract_offer_codec import (
    ContractOfferCodec,
    ContractOffer,
    ContractOptionType,
    OfferStatus
)

def test_contract_offer_roundtrip():
    offer = ContractOffer(
        player_id=123,
        team_id=15,
        years=4,
        salaries=[25000000, 27000000, 29000000, 31000000],
        option_type=ContractOptionType.TEAM_OPTION,
        no_trade_clause=True,
        status=OfferStatus.PENDING
    )
    
    raw = ContractOfferCodec.encode_offer(offer)
    assert len(raw) == 48
    
    decoded = ContractOfferCodec.decode_offer(raw)
    assert decoded.player_id == 123
    assert decoded.team_id == 15
    assert decoded.years == 4
    assert decoded.salaries == [25000000, 27000000, 29000000, 31000000]
    assert decoded.option_type == ContractOptionType.TEAM_OPTION
    assert decoded.no_trade_clause is True
    assert decoded.status == OfferStatus.PENDING

def test_contract_withdraw():
    offer = ContractOffer(
        player_id=456,
        team_id=2,
        years=1,
        salaries=[5000000],
        option_type=ContractOptionType.NONE,
        status=OfferStatus.PENDING
    )
    raw = ContractOfferCodec.encode_offer(offer)
    ContractOfferCodec.simulate_withdraw_offer(raw)
    
    decoded = ContractOfferCodec.decode_offer(raw)
    assert decoded.status == OfferStatus.WITHDRAWN
