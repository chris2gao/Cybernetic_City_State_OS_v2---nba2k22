"""Training and Mentorship Codec for NBA 2K22 (Wave-03 W03-06)
Encodes and decodes Team Training Schedule (30 bytes), Training Intensity,
and Mentorship List (10 slots x 204 bytes = 2040 bytes at TeamFranchise+0xc).

Binary Verified Anchors:
- 0x13256a0 / 0x1325710: Team_SetTrainingScheduleOnDate(TrainingProfile* rcx, uint8 day, uint32 mode)
  Copies 30-byte training schedule at [rcx + 0xf]..[rcx + 0x2c].
- 0x124f0f0: Mentor_AppendPair(TeamMentorshipContext* rcx, MentorEntry* rdx)
  Validates max 10 pairs (cmp r9b, 0xa), slot stride 0xcc (204 bytes), unassigned 0xffff.
- 0x125ed70: Mentor_RemovePair(TeamMentorshipContext* rcx, MentorEntry* rdx)
  Divides by 0xcc to obtain slot index (0..9) and clears entry.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

MAX_MENTOR_PAIRS = 10
MENTOR_SLOT_SIZE = 0xcc  # 204 bytes
EMPTY_SLOT_MARKER = 0xffff

@dataclass
class MentorshipPair:
    slot_index: int
    mentor_player_id: int
    mentee_player_id: int
    badge_target_id: int = 0
    active: bool = True

@dataclass
class DailyTrainingSchedule:
    day_index: int          # 0..6 (Day of week) or calendar day
    intensity: int          # 0: Off, 1: Very Low, 2: Low, 3: Medium, 4: High, 5: Very High
    focus_category: int     # 0: Balanced, 1: Offense, 2: Defense, 3: Shooting, 4: Physical, 5: Tactical
    b2b_rest_enabled: bool = True
    team_recovery_day: bool = False

class TrainingMentorshipCodec:
    """Encodes and decodes Training Schedule and Mentorship structures."""

    @staticmethod
    def encode_mentorship_table(pairs: List[MentorshipPair]) -> bytearray:
        """Encodes up to 10 mentorship pairs into 2040-byte buffer (10 * 0xcc)."""
        buffer = bytearray(MAX_MENTOR_PAIRS * MENTOR_SLOT_SIZE)
        # Initialize all slots with EMPTY_SLOT_MARKER (0xffff)
        for i in range(MAX_MENTOR_PAIRS):
            offset = i * MENTOR_SLOT_SIZE
            buffer[offset + 4 : offset + 8] = EMPTY_SLOT_MARKER.to_bytes(4, "little")

        for p in pairs[:MAX_MENTOR_PAIRS]:
            if not p.active or p.mentor_player_id == 0:
                continue
            offset = p.slot_index * MENTOR_SLOT_SIZE
            # mentor id at offset + 4
            buffer[offset + 4 : offset + 8] = (p.mentor_player_id & 0xffff).to_bytes(4, "little")
            # mentee id at offset + 8
            buffer[offset + 8 : offset + 12] = (p.mentee_player_id & 0xffff).to_bytes(4, "little")
            # badge target at offset + 12
            buffer[offset + 12 : offset + 16] = (p.badge_target_id & 0xffff).to_bytes(4, "little")

        return buffer

    @staticmethod
    def decode_mentorship_table(buffer: bytes) -> List[MentorshipPair]:
        """Decodes 10-slot mentorship buffer into list of active pairs."""
        pairs = []
        for i in range(MAX_MENTOR_PAIRS):
            offset = i * MENTOR_SLOT_SIZE
            if offset + 16 > len(buffer):
                break
            mentor_id = int.from_bytes(buffer[offset + 4 : offset + 8], "little")
            if mentor_id == EMPTY_SLOT_MARKER or mentor_id == 0:
                continue
            mentee_id = int.from_bytes(buffer[offset + 8 : offset + 12], "little")
            badge_id = int.from_bytes(buffer[offset + 12 : offset + 16], "little")
            pairs.append(MentorshipPair(
                slot_index=i,
                mentor_player_id=mentor_id,
                mentee_player_id=mentee_id,
                badge_target_id=badge_id,
                active=True
            ))
        return pairs

    @staticmethod
    def encode_training_schedule_slice(schedule: DailyTrainingSchedule) -> bytes:
        """Encodes 30-byte training schedule record starting at offset 0xf."""
        buf = bytearray(30)
        buf[0] = schedule.intensity & 0x7
        buf[1] = schedule.focus_category & 0xf
        buf[2] = 1 if schedule.b2b_rest_enabled else 0
        buf[3] = 1 if schedule.team_recovery_day else 0
        return bytes(buf)
