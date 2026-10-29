import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from training_mentorship_codec import (
    TrainingMentorshipCodec,
    MentorshipPair,
    DailyTrainingSchedule,
    MAX_MENTOR_PAIRS,
    MENTOR_SLOT_SIZE
)

def test_mentorship_table_roundtrip():
    pairs = [
        MentorshipPair(slot_index=0, mentor_player_id=101, mentee_player_id=202, badge_target_id=15),
        MentorshipPair(slot_index=3, mentor_player_id=105, mentee_player_id=208, badge_target_id=22),
        MentorshipPair(slot_index=9, mentor_player_id=110, mentee_player_id=215, badge_target_id=5)
    ]
    
    buf = TrainingMentorshipCodec.encode_mentorship_table(pairs)
    assert len(buf) == MAX_MENTOR_PAIRS * MENTOR_SLOT_SIZE # 2040 bytes
    
    decoded = TrainingMentorshipCodec.decode_mentorship_table(buf)
    assert len(decoded) == 3
    assert decoded[0].mentor_player_id == 101
    assert decoded[0].mentee_player_id == 202
    assert decoded[0].badge_target_id == 15
    assert decoded[1].slot_index == 3
    assert decoded[2].slot_index == 9

def test_training_schedule_slice():
    sched = DailyTrainingSchedule(
        day_index=2,
        intensity=4, # High
        focus_category=3, # Shooting
        b2b_rest_enabled=True,
        team_recovery_day=False
    )
    raw = TrainingMentorshipCodec.encode_training_schedule_slice(sched)
    assert len(raw) == 30
    assert raw[0] == 4
    assert raw[1] == 3
    assert raw[2] == 1
    assert raw[3] == 0
