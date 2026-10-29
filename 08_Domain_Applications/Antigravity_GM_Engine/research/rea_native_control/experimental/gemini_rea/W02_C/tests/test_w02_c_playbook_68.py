"""Offline unit tests for W02-C: Team Playbook 68-slot codec and partition manipulation.

Verifies:
1. Exact 360-byte binary size and relative offset 0x58 (88 decimal).
2. Four partition slot counts and boundaries (30, 20, 10, 8).
3. Add, remove, swap, and duplicate rejection in partitions.
4. Binary roundtrip serialization.
"""

import pytest

from ..playbook_68_codec import (
    EMPTY_PLAY_CRC,
    OFFSET_PLAY_SLOTS,
    PARTITION_RANGES,
    PLAYBOOK_SIZE,
    TOTAL_SLOTS,
    PlaybookPartition,
    TeamPlaybook,
    get_partition_for_slot,
)


class TestPlaybook68Codec:
    def test_playbook_size_and_offsets(self):
        assert PLAYBOOK_SIZE == 360  # 0x168
        assert OFFSET_PLAY_SLOTS == 0x58  # 88 decimal
        assert TOTAL_SLOTS == 68
        assert OFFSET_PLAY_SLOTS + TOTAL_SLOTS * 4 == PLAYBOOK_SIZE

    def test_partition_boundaries(self):
        assert PARTITION_RANGES[PlaybookPartition.REGULAR] == (0, 30)
        assert PARTITION_RANGES[PlaybookPartition.BENCH] == (30, 50)
        assert PARTITION_RANGES[PlaybookPartition.ENDGAME] == (50, 60)
        assert PARTITION_RANGES[PlaybookPartition.FAVORITE] == (60, 68)

        # Total partition capacity sum
        total_capacity = sum(end - start for start, end in PARTITION_RANGES.values())
        assert total_capacity == 68

        # Verify mapping
        assert get_partition_for_slot(0) == PlaybookPartition.REGULAR
        assert get_partition_for_slot(29) == PlaybookPartition.REGULAR
        assert get_partition_for_slot(30) == PlaybookPartition.BENCH
        assert get_partition_for_slot(49) == PlaybookPartition.BENCH
        assert get_partition_for_slot(50) == PlaybookPartition.ENDGAME
        assert get_partition_for_slot(59) == PlaybookPartition.ENDGAME
        assert get_partition_for_slot(60) == PlaybookPartition.FAVORITE
        assert get_partition_for_slot(67) == PlaybookPartition.FAVORITE

        with pytest.raises(IndexError):
            get_partition_for_slot(68)

    def test_slot_manipulation_operations(self):
        pb = TeamPlaybook()

        # Add to REGULAR partition
        crc_floppy = 0x12345678
        slot_floppy = pb.add_play_to_partition(PlaybookPartition.REGULAR, crc_floppy)
        assert slot_floppy == 0
        assert pb.get_play(0) == crc_floppy

        # Add another to REGULAR
        crc_horns = 0x87654321
        slot_horns = pb.add_play_to_partition(PlaybookPartition.REGULAR, crc_horns)
        assert slot_horns == 1
        assert pb.get_play(1) == crc_horns

        # Verify duplicate rejected in same partition
        with pytest.raises(ValueError):
            pb.add_play_to_partition(PlaybookPartition.REGULAR, crc_floppy)

        # Swap plays
        pb.swap_plays(0, 1)
        assert pb.get_play(0) == crc_horns
        assert pb.get_play(1) == crc_floppy

        # Remove play
        pb.remove_play(0)
        assert pb.get_play(0) == EMPTY_PLAY_CRC

        # Add to FAVORITE partition
        crc_iso = 0xAABBCCDD
        slot_iso = pb.add_play_to_partition(PlaybookPartition.FAVORITE, crc_iso)
        assert slot_iso == 60
        assert pb.get_play(60) == crc_iso

    def test_binary_roundtrip(self):
        pb = TeamPlaybook(header_raw=b"\xAA" * OFFSET_PLAY_SLOTS)
        pb.set_play(0, 0x11223344)
        pb.set_play(30, 0x55667788)
        pb.set_play(55, 0x99AABBCC)
        pb.set_play(67, 0xDDEEFF00)

        raw = pb.pack()
        assert len(raw) == 360

        unpacked = TeamPlaybook.unpack(raw)
        assert unpacked.header_raw == b"\xAA" * OFFSET_PLAY_SLOTS
        assert unpacked.get_play(0) == 0x11223344
        assert unpacked.get_play(30) == 0x55667788
        assert unpacked.get_play(55) == 0x99AABBCC
        assert unpacked.get_play(67) == 0xDDEEFF00
        assert unpacked.get_play(1) == EMPTY_PLAY_CRC
