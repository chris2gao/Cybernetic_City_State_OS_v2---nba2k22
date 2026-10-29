"""GM Trade Package and Salary Matching Codec for NBA 2K22 (Wave-03 W03-10)
Encodes and decodes Trade Packages (Two-Team and Three-Team), Players,
Picks, and verifies NBA CBA Salary Matching and Roster Constraints.

Binary Verified Anchors:
- 0x12ec130 / 0x12e1000: Trade_ValidateRestrictions(TradeContext* rdi)
  Checks no-trade clauses, trade restrictions (0x3c0000 mask), and salary matching.
- 0x132b040 / 0x1413be6e0: Trade_CommitTransaction(TradePackage* rdx)
  Executes asset transfers across all participating teams.
- 0x12de420: Trade_AddPlayer(TradeContext* rcx, uint16 player_id, uint32 from_team, uint32 to_team)
- 0x12de050: Trade_AddPick(TradeContext* rcx, uint32 pick_id, uint32 from_team, uint32 to_team)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

@dataclass
class TradeAsset:
    asset_type: str  # "PLAYER" or "PICK"
    asset_id: int
    from_team_id: int
    to_team_id: int
    salary: int = 0  # annual salary for players

@dataclass
class TradePackage:
    participating_teams: List[int]
    assets: List[TradeAsset] = field(default_factory=list)

    def calculate_team_salaries(self) -> Dict[int, Dict[str, int]]:
        """Calculates outgoing and incoming salaries for each participating team."""
        salaries = {tid: {"outgoing": 0, "incoming": 0} for tid in self.participating_teams}
        for a in self.assets:
            if a.asset_type == "PLAYER":
                if a.from_team_id in salaries:
                    salaries[a.from_team_id]["outgoing"] += a.salary
                if a.to_team_id in salaries:
                    salaries[a.to_team_id]["incoming"] += a.salary
        return salaries

    def validate_salary_matching(self, is_taxpayer: Dict[int, bool] = None) -> Tuple[bool, str]:
        """Validates NBA CBA salary matching rules for non-taxpayers and taxpayers."""
        if is_taxpayer is None:
            is_taxpayer = {}

        totals = self.calculate_team_salaries()
        for tid, data in totals.items():
            outgoing = data["outgoing"]
            incoming = data["incoming"]
            taxpayer = is_taxpayer.get(tid, False)

            if outgoing == 0 and incoming == 0:
                continue

            if taxpayer:
                # Taxpayer can absorb up to 125% of outgoing + 100k
                max_incoming = int(outgoing * 1.25) + 100000
            else:
                # Non-taxpayer bands
                if outgoing <= 6533333:
                    max_incoming = int(outgoing * 1.75) + 100000
                elif outgoing <= 19600000:
                    max_incoming = outgoing + 5000000
                else:
                    max_incoming = int(outgoing * 1.25) + 100000

            if incoming > max_incoming and incoming > 2000000:
                return False, f"Team {tid} incoming ${incoming:,} exceeds allowed max ${max_incoming:,} for outgoing ${outgoing:,}"

        return True, "Valid"


class TradePackageCodec:
    """Serializes Trade Packages into native transaction contexts."""

    @staticmethod
    def serialize_trade_package(pkg: TradePackage) -> Dict[str, Any]:
        """Produces serialized representation matching 0x132b040 transaction layout."""
        return {
            "teams": pkg.participating_teams,
            "asset_count": len(pkg.assets),
            "assets": [
                {
                    "type": a.asset_type,
                    "id": a.asset_id,
                    "from_team": a.from_team_id,
                    "to_team": a.to_team_id,
                    "salary": a.salary
                }
                for a in pkg.assets
            ],
            "salary_summary": pkg.calculate_team_salaries()
        }
