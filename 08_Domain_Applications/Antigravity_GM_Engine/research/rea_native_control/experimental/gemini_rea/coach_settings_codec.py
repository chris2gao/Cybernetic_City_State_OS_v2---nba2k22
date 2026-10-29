"""Coach Settings and Freelance Codec for NBA 2K22 (Wave-03 W03-04)
Encodes and decodes Coach Settings, POEs, Freelance slots, and Automation flags
into the native GAMEPLAN 880-byte buffer and COACHDATA structure.

Binary Verified Anchors:
- 0x146eaa0: CoachData_ApplyGameplan(GAMEPLAN* rcx, COACHDATA* rdx)
- 0x131f110: Team_ApplyPendingGameplanAndCoachSettings
- 0x131f1b0: Team_FlushCoachSettingsIfDirty
- 0x140f3f580: Play_ResolveById(uint16 play_id) -> Play*
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class CoachSettings:
    # 6 POE values (each 0..31, 5 bits)
    poe_offense_1: int = 0
    poe_offense_2: int = 0
    poe_offense_3: int = 0
    poe_defense_1: int = 0
    poe_defense_2: int = 0
    poe_defense_3: int = 0
    
    # Sliders & Rates (0..100 or specific enums)
    run_play_tendency: int = 50       # GAMEPLAN+0x185 -> COACHDATA+0xe0
    zone_usage: int = 0              # GAMEPLAN+0x186 -> COACHDATA+0xe2
    bench_depth: int = 7             # GAMEPLAN+0x187 -> COACHDATA+0xde
    bench_utilization: int = 50      # GAMEPLAN+0x188 -> COACHDATA+0x138
    sub_method: int = 0              # GAMEPLAN+0x189 -> COACHDATA+0xdf
    ace_mode: int = 1                # GAMEPLAN+0x18a -> COACHDATA+0x109
    
    # Automation bitfield (6 bits: 0..63)
    automation_flags: int = 0        # GAMEPLAN+0x18b -> COACHDATA+0xfc bits 25..30
    
    # System & Freelance
    tactical_system: int = 0         # GAMEPLAN+0x184 -> COACHDATA+0x148 bits 17..24
    freelance_slots: List[int] = None # GAMEPLAN+0x178..0x17e (up to 4 uint16 slots)

    def __post_init__(self):
        if self.freelance_slots is None:
            self.freelance_slots = [0xffff, 0xffff, 0xffff, 0xffff]


class CoachSettingsCodec:
    """Encodes/Decodes Coach Settings into GAMEPLAN offsets 0x178..0x18c"""
    
    @staticmethod
    def encode_gameplan_tail(settings: CoachSettings, buffer: bytearray) -> None:
        """Writes coach settings into GAMEPLAN buffer at offset 0x178 (20 bytes)."""
        if len(buffer) < 0x18c:
            buffer.extend(b"\x00" * (0x18c - len(buffer)))
            
        # Freelance slots (3 or 4 slots at 0x178, 0x17a, 0x17c)
        for i in range(min(3, len(settings.freelance_slots))):
            slot_val = settings.freelance_slots[i] & 0xffff
            buffer[0x178 + i*2 : 0x17a + i*2] = slot_val.to_bytes(2, "little")
            
        # POE fields in GAMEPLAN
        buffer[0x181] = settings.poe_offense_1 & 0x1f
        buffer[0x182] = settings.poe_offense_2 & 0x1f
        buffer[0x183] = settings.poe_offense_3 & 0x1f
        buffer[0x17e] = settings.poe_defense_1 & 0x1f
        buffer[0x17f] = settings.poe_defense_2 & 0x1f
        buffer[0x180] = settings.poe_defense_3 & 0x1f
        
        # System & Sliders
        buffer[0x184] = settings.tactical_system & 0xff
        buffer[0x185] = min(100, max(0, settings.run_play_tendency))
        buffer[0x186] = min(100, max(0, settings.zone_usage))
        buffer[0x187] = min(15, max(0, settings.bench_depth))
        buffer[0x188] = min(100, max(0, settings.bench_utilization))
        buffer[0x189] = settings.sub_method & 0xff
        buffer[0x18a] = settings.ace_mode & 0xff
        buffer[0x18b] = settings.automation_flags & 0x3f

    @staticmethod
    def decode_gameplan_tail(buffer: bytes) -> CoachSettings:
        """Reads coach settings from GAMEPLAN buffer."""
        if len(buffer) < 0x18c:
            raise ValueError(f"Buffer too short: {len(buffer)} < 0x18c")
            
        slots = [
            int.from_bytes(buffer[0x178:0x17a], "little"),
            int.from_bytes(buffer[0x17a:0x17c], "little"),
            int.from_bytes(buffer[0x17c:0x17e], "little"),
            0xffff
        ]
        
        return CoachSettings(
            poe_offense_1=buffer[0x181] & 0x1f,
            poe_offense_2=buffer[0x182] & 0x1f,
            poe_offense_3=buffer[0x183] & 0x1f,
            poe_defense_1=buffer[0x17e] & 0x1f,
            poe_defense_2=buffer[0x17f] & 0x1f,
            poe_defense_3=buffer[0x180] & 0x1f,
            run_play_tendency=buffer[0x185],
            zone_usage=buffer[0x186],
            bench_depth=buffer[0x187],
            bench_utilization=buffer[0x188],
            sub_method=buffer[0x189],
            ace_mode=buffer[0x18a],
            automation_flags=buffer[0x18b] & 0x3f,
            tactical_system=buffer[0x184],
            freelance_slots=slots
        )

    @staticmethod
    def simulate_apply_to_coachdata(settings: CoachSettings) -> Dict[str, Any]:
        """Simulates native function 0x146eaa0 mapping from GAMEPLAN into COACHDATA offsets."""
        # 1. 0x13c packs 6 5-bit POE fields
        dword_13c = (
            (settings.poe_offense_1 & 0x1f) |
            ((settings.poe_offense_2 & 0x1f) << 5) |
            ((settings.poe_offense_3 & 0x1f) << 10) |
            ((settings.poe_defense_1 & 0x1f) << 15) |
            ((settings.poe_defense_2 & 0x1f) << 20) |
            ((settings.poe_defense_3 & 0x1f) << 25)
        )
        
        # 2. 0x148 bits 17..24 for tactical system
        dword_148 = (settings.tactical_system & 0xff) << 17
        
        # 3. 0xfc bits 25..30 for automation flags
        dword_fc = (settings.automation_flags & 0x3f) << 25
        
        return {
            "coachdata_0x13c_poe_packed": dword_13c,
            "coachdata_0x148_system": dword_148,
            "coachdata_0xfc_automation": dword_fc,
            "coachdata_0xe0_run_play": settings.run_play_tendency,
            "coachdata_0xe2_zone_usage": settings.zone_usage,
            "coachdata_0xde_bench_depth": settings.bench_depth,
            "coachdata_0x138_bench_util": settings.bench_utilization,
            "coachdata_0xdf_sub_method": settings.sub_method,
            "coachdata_0x109_ace_mode": settings.ace_mode,
            "freelance_slot_play_ids": settings.freelance_slots[:3]
        }
