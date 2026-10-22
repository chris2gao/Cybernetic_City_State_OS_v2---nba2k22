"""Matchup Defense Adapter for NBA2K22.

Enables targeted preflight and controlled adjustments for individual player matchups,
distinguishing personal assignments from bulk overall settings.
"""

from typing import Dict, List, Any, Optional
from coach_locator import CoachLocator, live_memory, read_exact
from coaching_reader import defensive_catalog, DEFENSE_NAMES
import struct


class MatchupDefenseAdapter:
    def __init__(self, memory_factory=live_memory, locator_factory=CoachLocator):
        self.memory_factory = memory_factory
        self.locator_factory = locator_factory

    def locate_matchup_entry(self, locator: CoachLocator, owner_team_id: int,
                             opponent_team_id: int, opponent_player_id: int):
        """Locate the 8-byte defensive setting block for a specific opponent player."""
        n = locator.profile["native"]
        mgr_addr = locator.managers[owner_team_id]
        mem = locator.mem

        for idx in range(n["gameplan_capacity"]):
            gp_addr = mgr_addr + n["gameplan_start"] + idx * n["gameplan_stride"]
            hdr = read_exact(mem, gp_addr, 6)
            owner = int.from_bytes(hdr[2:4], "little")
            opp = int.from_bytes(hdr[4:6], "little")
            if owner == owner_team_id and opp == opponent_team_id:
                # Found the gameplan
                for j in range((0x178 - 0x64) // 12):
                    entry_off = 0x64 + j * 12
                    entry_raw = read_exact(mem, gp_addr + entry_off, 12)
                    m_id = int.from_bytes(entry_raw[:2], "little")
                    d_id = int.from_bytes(entry_raw[2:4], "little")
                    if m_id == opponent_player_id:
                        return {
                            "gameplan_address": gp_addr,
                            "entry_offset": entry_off,
                            "settings_address": gp_addr + entry_off + 4,
                            "opponent_player_id": m_id,
                            "defender_id": d_id,
                            "current_raw": entry_raw[4:12]
                        }
        raise ValueError(f"Matchup for opponent player {opponent_player_id} not found in {owner_team_id} vs {opponent_team_id} gameplan.")

    def preflight_matchup_setting(self, locator: CoachLocator, owner_team_id: int,
                                 opponent_team_id: int, opponent_player_id: int,
                                 field_name: str, new_value: int) -> Dict[str, Any]:
        """Preflight an individual matchup defensive setting change."""
        catalog = defensive_catalog(locator)
        if field_name not in catalog:
            raise ValueError(f"Unknown defensive field {field_name}.")
        field = catalog[field_name]

        entry = self.locate_matchup_entry(locator, owner_team_id, opponent_team_id, opponent_player_id)
        current_data = entry["current_raw"]

        # Decode current value
        shift = field["offset"] * 8 + field["start_bit"]
        mask = ((1 << field["width"]) - 1)
        raw_int = int.from_bytes(current_data, "little")
        old_val = (raw_int >> shift) & mask

        # Encode new value into 8 bytes
        cleared = raw_int & ~(mask << shift)
        new_int = cleared | ((new_value & mask) << shift)
        new_data = new_int.to_bytes(8, "little")

        return {
            "status": "PREFLIGHT_VERIFIED",
            "owner_team_id": owner_team_id,
            "opponent_team_id": opponent_team_id,
            "opponent_player_id": opponent_player_id,
            "field": field_name,
            "old_value": old_val,
            "new_value": new_value,
            "settings_address": entry["settings_address"],
            "before_raw": current_data.hex(),
            "after_raw": new_data.hex()
        }

    def execute_matchup_write(self, settings_addr: int, expected_raw_hex: str, new_raw_hex: str) -> bool:
        """Write 8-byte updated matchup settings under exclusive memory lock."""
        mem = self.memory_factory(read_only=False)
        try:
            current = mem.read_bytes(settings_addr, 8)
            if current != bytes.fromhex(expected_raw_hex):
                raise RuntimeError("STALE_MATCHUP_PREIMAGE")
            mem.write_bytes(settings_addr, bytes.fromhex(new_raw_hex))
            # Verify readback
            verified = mem.read_bytes(settings_addr, 8)
            if verified != bytes.fromhex(new_raw_hex):
                raise RuntimeError("VERIFICATION_FAILED_AFTER_MATCHUP_WRITE")
            return True
        finally:
            mem.close()
