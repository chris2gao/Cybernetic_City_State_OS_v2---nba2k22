"""W02-C: Team Playbook 68-Slot Native Structure Codec and Manipulation Engine.

Models the 360-byte (0x168) PLAYBOOKDATA structure in NBA 2K22, containing
68 uint32 play CRC slots across 4 partitions:
- REGULAR: Slots 0..29 (30 slots, offset 0x58..0xD0)
- BENCH: Slots 30..49 (20 slots, offset 0xD0..0x120)
- ENDGAME: Slots 50..59 (10 slots, offset 0x120..0x148)
- FAVORITE: Slots 60..67 (8 slots, offset 0x148..0x168)
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

PLAYBOOK_SIZE = 360  # 0x168 bytes
OFFSET_PLAY_SLOTS = 0x58  # 88 decimal
TOTAL_SLOTS = 68
EMPTY_PLAY_CRC = 0x00000000


class PlaybookPartition(str, Enum):
    REGULAR = "REGULAR"
    BENCH = "BENCH"
    ENDGAME = "ENDGAME"
    FAVORITE = "FAVORITE"


PARTITION_RANGES: Dict[PlaybookPartition, Tuple[int, int]] = {
    PlaybookPartition.REGULAR: (0, 30),      # [0, 30), length 30
    PlaybookPartition.BENCH: (30, 50),       # [30, 50), length 20
    PlaybookPartition.ENDGAME: (50, 60),     # [50, 60), length 10
    PlaybookPartition.FAVORITE: (60, 68),    # [60, 68), length 8
}


def get_partition_for_slot(slot_index: int) -> PlaybookPartition:
    if not (0 <= slot_index < TOTAL_SLOTS):
        raise IndexError(f"Slot index {slot_index} out of bounds (0..{TOTAL_SLOTS-1})")
    for part, (start, end) in PARTITION_RANGES.items():
        if start <= slot_index < end:
            return part
    raise RuntimeError(f"Slot {slot_index} not in any partition")


@dataclass
class TeamPlaybook:
    """Represents the 360-byte native PLAYBOOKDATA structure."""
    header_raw: bytes = field(default_factory=lambda: b"\x00" * OFFSET_PLAY_SLOTS)
    slots: List[int] = field(default_factory=lambda: [EMPTY_PLAY_CRC] * TOTAL_SLOTS)

    def __post_init__(self):
        if len(self.header_raw) != OFFSET_PLAY_SLOTS:
            self.header_raw = self.header_raw.ljust(OFFSET_PLAY_SLOTS, b"\x00")[:OFFSET_PLAY_SLOTS]
        if len(self.slots) != TOTAL_SLOTS:
            raise ValueError(f"Slots count must be exactly {TOTAL_SLOTS}, got {len(self.slots)}")

    def get_play(self, slot_index: int) -> int:
        if not (0 <= slot_index < TOTAL_SLOTS):
            raise IndexError(f"Slot {slot_index} out of bounds (0..{TOTAL_SLOTS-1})")
        return self.slots[slot_index]

    def set_play(self, slot_index: int, play_crc: int) -> None:
        if not (0 <= slot_index < TOTAL_SLOTS):
            raise IndexError(f"Slot {slot_index} out of bounds (0..{TOTAL_SLOTS-1})")
        self.slots[slot_index] = play_crc & 0xFFFFFFFF

    def remove_play(self, slot_index: int) -> None:
        self.set_play(slot_index, EMPTY_PLAY_CRC)

    def swap_plays(self, slot_a: int, slot_b: int) -> None:
        if not (0 <= slot_a < TOTAL_SLOTS) or not (0 <= slot_b < TOTAL_SLOTS):
            raise IndexError(f"Slots {slot_a}, {slot_b} out of bounds")
        self.slots[slot_a], self.slots[slot_b] = self.slots[slot_b], self.slots[slot_a]

    def add_play_to_partition(self, partition: PlaybookPartition, play_crc: int) -> int:
        """Finds first empty slot in partition and sets play_crc. Returns slot index."""
        start, end = PARTITION_RANGES[partition]
        # Check duplicate
        for idx in range(start, end):
            if self.slots[idx] == play_crc:
                raise ValueError(f"Play CRC {hex(play_crc)} already exists in partition {partition.value} at slot {idx}")
        # Find empty
        for idx in range(start, end):
            if self.slots[idx] == EMPTY_PLAY_CRC:
                self.slots[idx] = play_crc & 0xFFFFFFFF
                return idx
        raise RuntimeError(f"Partition {partition.value} is full (capacity {end - start})")

    def get_partition_plays(self, partition: PlaybookPartition) -> List[int]:
        start, end = PARTITION_RANGES[partition]
        return [crc for crc in self.slots[start:end] if crc != EMPTY_PLAY_CRC]

    def pack(self) -> bytes:
        slots_bytes = struct.pack(f"<{TOTAL_SLOTS}I", *self.slots)
        res = self.header_raw + slots_bytes
        if len(res) != PLAYBOOK_SIZE:
            raise ValueError(f"Packed playbook size {len(res)} does not match {PLAYBOOK_SIZE}")
        return res

    @classmethod
    def unpack(cls, data: bytes, offset: int = 0) -> TeamPlaybook:
        if len(data) < offset + PLAYBOOK_SIZE:
            raise ValueError(f"Data length {len(data)} is less than required {offset + PLAYBOOK_SIZE}")
        slice_data = data[offset:offset + PLAYBOOK_SIZE]
        header = slice_data[:OFFSET_PLAY_SLOTS]
        slots = list(struct.unpack_from(f"<{TOTAL_SLOTS}I", slice_data, OFFSET_PLAY_SLOTS))
        return cls(header_raw=header, slots=slots)
