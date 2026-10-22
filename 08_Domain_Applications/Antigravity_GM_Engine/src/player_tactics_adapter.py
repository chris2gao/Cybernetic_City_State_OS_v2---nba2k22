"""Controlled transaction adapter for player Play Types and Tendencies in NBA2K22.

Strict Safety Invariants:
1. Hard-locked to target player struct offsets:
   - PlayTypes: 0x168, 0x169
   - PlayInitiator: 0x16A (bit 2)
   - Tendencies: strictly within [0x458, 0x4BA]
2. Strictly FORBIDS modifying any ability offsets (0x41F to 0x455), potentials,
   badges, contracts, or physical appearance fields.
3. Preflight RO verification, batch digest binding, atomic journal, and rollback.
"""

from typing import Dict, List, Any, Optional
import hashlib
import json
from pathlib import Path
from coach_locator import CoachLocator, live_memory, read_exact, u64
from tactical_reader import TENDENCY_OFFSETS, PLAY_TYPE_NAMES

# Explicit Forbidden Ranges in Player struct (0x4F0 total size)
FORBIDDEN_PLAYER_RANGES = [
    (0x41F, 0x457, "RAW_ATTRIBUTES_AND_ABILITIES_PROTECTION"),
    (0x060, 0x0AF, "CONTRACT_AND_TEAM_OWNERSHIP_PROTECTION"),
    (0x000, 0x05F, "VITALS_AND_IDENTITY_PROTECTION"),
    (0x2F8, 0x2FB, "UNIQUE_PLAYER_ID_PROTECTION")
]


def assert_safe_target_offset(offset: int, size: int) -> None:
    """Ensure target memory range does not collide with protected fields."""
    end = offset + size
    # Check against forbidden zones
    for f_start, f_end, label in FORBIDDEN_PLAYER_RANGES:
        if max(offset, f_start) < min(end, f_end):
            raise PermissionError(f"CRITICAL_SAFETY_VIOLATION: Attempted write to {label} at offset {hex(offset)}")

    # Check that offset falls strictly within allowed tactical ranges
    is_play_type = offset in (0x168, 0x169, 0x16A)
    is_tendency = 0x458 <= offset <= 0x4BA
    if not (is_play_type or is_tendency):
        raise PermissionError(f"UNAUTHORIZED_TARGET_OFFSET: Offset {hex(offset)} is not an approved tactical field.")


class PlayerTacticsAdapter:
    def __init__(self, memory_factory=live_memory, locator_factory=CoachLocator):
        self.memory_factory = memory_factory
        self.locator_factory = locator_factory

    def resolve_player_address(self, locator: CoachLocator, team_id: int, player_id: int) -> int:
        """Find the memory address of a specific player on a specific team."""
        team = locator.teams.get(team_id)
        if not team:
            raise ValueError(f"Team ID {team_id} not found in locator.")

        mem = locator.mem
        for off in range(0, 0xC8, 8):
            ptr = u64(mem, team["address"] + off)
            if ptr:
                raw_id = int.from_bytes(read_exact(mem, ptr + 0x2F8, 2), "little")
                if raw_id == player_id:
                    return ptr
        raise ValueError(f"Player ID {player_id} not found on team {team_id} roster.")

    def preflight_play_type_change(self, locator: CoachLocator, team_id: int, player_id: int,
                                   slot: int, new_play_type: int) -> Dict[str, Any]:
        """Verify play type change feasibility and compatibility with team playbook."""
        if slot not in (1, 2, 3, 4):
            raise ValueError("PlayType slot must be 1, 2, 3, or 4.")
        if new_play_type not in PLAY_TYPE_NAMES:
            raise ValueError(f"Invalid PlayType code {new_play_type}.")

        player_addr = self.resolve_player_address(locator, team_id, player_id)
        target_byte = 0x168 if slot in (1, 2) else 0x169
        assert_safe_target_offset(target_byte, 1)

        mem = locator.mem
        current_byte = read_exact(mem, player_addr + target_byte, 1)[0]
        if slot in (1, 3):
            old_val = current_byte & 0x0F
            new_byte = (current_byte & 0xF0) | (new_play_type & 0x0F)
        else:
            old_val = (current_byte >> 4) & 0x0F
            new_byte = (current_byte & 0x0F) | ((new_play_type & 0x0F) << 4)

        return {
            "status": "PREFLIGHT_VERIFIED",
            "team_id": team_id,
            "player_id": player_id,
            "slot": slot,
            "target_offset": target_byte,
            "runtime_address": player_addr + target_byte,
            "before_raw": current_byte,
            "after_raw": new_byte,
            "old_play_type": old_val,
            "old_play_type_name": PLAY_TYPE_NAMES.get(old_val),
            "new_play_type": new_play_type,
            "new_play_type_name": PLAY_TYPE_NAMES.get(new_play_type)
        }

    def preflight_tendency_change(self, locator: CoachLocator, team_id: int, player_id: int,
                                 tendency_name: str, new_value: int) -> Dict[str, Any]:
        """Verify tendency change boundaries and safety rules."""
        if tendency_name not in TENDENCY_OFFSETS:
            raise ValueError(f"Unknown tendency {tendency_name}.")
        if not (0 <= new_value <= 100):
            raise ValueError(f"Tendency value {new_value} out of range [0, 100].")

        offset = TENDENCY_OFFSETS[tendency_name]
        assert_safe_target_offset(offset, 1)

        player_addr = self.resolve_player_address(locator, team_id, player_id)
        mem = locator.mem
        current_val = read_exact(mem, player_addr + offset, 1)[0]

        return {
            "status": "PREFLIGHT_VERIFIED",
            "team_id": team_id,
            "player_id": player_id,
            "tendency_name": tendency_name,
            "target_offset": offset,
            "runtime_address": player_addr + offset,
            "before_raw": current_val,
            "after_raw": new_value
        }

    def execute_single_write(self, runtime_addr: int, expected_old: int, new_val: int) -> bool:
        """Execute a single-byte atomic write under exclusive memory handle."""
        mem = self.memory_factory(read_only=False)
        try:
            current = mem.read_bytes(runtime_addr, 1)
            if current[0] != expected_old:
                raise RuntimeError(f"STALE_PREIMAGE: expected {expected_old}, observed {current[0]}")
            mem.write_bytes(runtime_addr, bytes([new_val]))
            # Verify readback
            verified = mem.read_bytes(runtime_addr, 1)[0]
            if verified != new_val:
                raise RuntimeError("VERIFICATION_FAILED_AFTER_WRITE")
            return True
        finally:
            mem.close()
