"""GM Contract Offer and Transaction Codec for NBA 2K22 (Wave-03 W03-07)
Encodes and decodes Contract Offers, Options, RFA status, and Salary Schedules.

Binary Verified Anchors:
- 0x12bc4a0: Contract_ProcessOffer(ContractOfferContext* rcx)
  Resolves player at +0x0 (0x140f3f580), team at +0x2 (0x140f40eb0), contract flags at +0x20.
- 0x12bf5a0 / 0x12bf6c0: Contract_ProcessOptions(FranchiseContext* rcx)
  Processes Team/Player options during Offseason Phase 0x16 (22 decimal).
- 0x12b3840: Contract_CancelOffer(OfferContext* rsi)
  Clears pending offer bit and sets status to 0x1c0000 (WITHDRAWN).
- 0x9888b0: Player_GetSalary(PlayerRosterSlot* rcx)
- 0x9886c0: Player_GetRemainingContractYears(PlayerRosterSlot* rcx)
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import IntEnum

class ContractOptionType(IntEnum):
    NONE = 0
    TEAM_OPTION = 1
    PLAYER_OPTION = 2
    TWO_WAY = 3
    QUALIFYING_OFFER = 4

class OfferStatus(IntEnum):
    PENDING = 0x100000
    ACCEPTED = 0x200000
    REJECTED = 0x300000
    WITHDRAWN = 0x1c0000

@dataclass
class ContractOffer:
    player_id: int
    team_id: int
    years: int
    salaries: List[int] # Annual salaries for up to 5 years (in USD)
    option_type: ContractOptionType = ContractOptionType.NONE
    no_trade_clause: bool = False
    status: OfferStatus = OfferStatus.PENDING

    def validate_offer(self) -> bool:
        if not (1 <= self.years <= 5):
            return False
        if len(self.salaries) != self.years:
            return False
        if any(s < 0 for s in self.salaries):
            return False
        return True


class ContractOfferCodec:
    """Encodes and decodes Contract Offers matching native ContractOfferContext struct."""

    @staticmethod
    def encode_offer(offer: ContractOffer) -> bytearray:
        """Encodes ContractOffer into a 48-byte native context matching 0x12bc4a0."""
        if not offer.validate_offer():
            raise ValueError("Invalid contract offer terms")

        buf = bytearray(48)
        # +0x0: uint16 player_id
        buf[0:2] = (offer.player_id & 0xffff).to_bytes(2, "little")
        # +0x2: uint16 team_id
        buf[2:4] = (offer.team_id & 0xffff).to_bytes(2, "little")
        # +0x4: uint16 years
        buf[4:6] = (offer.years & 0xffff).to_bytes(2, "little")
        
        # +0x8..0x1c: 5x uint32 annual salaries
        for i in range(5):
            sal = offer.salaries[i] if i < len(offer.salaries) else 0
            buf[8 + i*4 : 12 + i*4] = (sal & 0xffffffff).to_bytes(4, "little")

        # +0x20: uint32 flags and status
        flags = int(offer.status)
        if offer.option_type == ContractOptionType.TEAM_OPTION:
            flags |= (1 << 12)
        elif offer.option_type == ContractOptionType.PLAYER_OPTION:
            flags |= (2 << 12)
        elif offer.option_type == ContractOptionType.TWO_WAY:
            flags |= (3 << 12)

        if offer.no_trade_clause:
            flags |= (1 << 14)

        buf[0x20:0x24] = (flags & 0xffffffff).to_bytes(4, "little")
        return buf

    @staticmethod
    def decode_offer(buf: bytes) -> ContractOffer:
        """Decodes 48-byte native context into ContractOffer."""
        if len(buf) < 48:
            raise ValueError(f"Buffer too short: {len(buf)} < 48")

        pid = int.from_bytes(buf[0:2], "little")
        tid = int.from_bytes(buf[2:4], "little")
        years = int.from_bytes(buf[4:6], "little")

        salaries = []
        for i in range(min(5, years)):
            sal = int.from_bytes(buf[8 + i*4 : 12 + i*4], "little")
            salaries.append(sal)

        flags = int.from_bytes(buf[0x20:0x24], "little")
        status_val = flags & 0x003f0000
        try:
            status = OfferStatus(status_val)
        except ValueError:
            status = OfferStatus.PENDING

        opt_bits = (flags >> 12) & 0x3
        if opt_bits == 1:
            opt = ContractOptionType.TEAM_OPTION
        elif opt_bits == 2:
            opt = ContractOptionType.PLAYER_OPTION
        elif opt_bits == 3:
            opt = ContractOptionType.TWO_WAY
        else:
            opt = ContractOptionType.NONE

        ntc = bool(flags & (1 << 14))

        return ContractOffer(
            player_id=pid,
            team_id=tid,
            years=years,
            salaries=salaries,
            option_type=opt,
            no_trade_clause=ntc,
            status=status
        )

    @staticmethod
    def simulate_withdraw_offer(buf: bytearray) -> None:
        """Simulates native 0x12b3840: sets offer status to WITHDRAWN (0x1c0000)."""
        current_flags = int.from_bytes(buf[0x20:0x24], "little")
        # and dword ptr [rsi + 0x20], 0xffdfffff; or dword ptr [rsi + 0x20], 0x1c0000
        new_flags = (current_flags & 0xffdfffff) | int(OfferStatus.WITHDRAWN)
        buf[0x20:0x24] = (new_flags & 0xffffffff).to_bytes(4, "little")
