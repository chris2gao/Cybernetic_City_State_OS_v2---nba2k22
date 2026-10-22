"""Read-only GAMEPLAN byte codec. This is not the packed COACHDATA layout."""

SIZE=0x370
POE_FIELDS=("POEOffense","POEOffense2","POEOffense3","POEDefense","POEDefense2","POEDefense3")
SLIDER_FIELDS=("HelpDefense","RunPlayTendency","ZoneUsage","BenchDepth","BenchUtilization","LineupFormFactor")

def decode_header(raw):
    if len(raw)!=SIZE:
        raise ValueError("INCOMPLETE_GAMEPLAN_RECORD")
    values=dict(zip(POE_FIELDS,raw[0x17e:0x184]))
    values.update(zip(SLIDER_FIELDS,raw[0x184:0x18a]))
    values.update(PlaybookID=raw[0x18a],FreelanceType=raw[0x18b])
    return dict(team_id=int.from_bytes(raw[2:4],"little"),opponent_team_id=int.from_bytes(raw[4:6],"little"),
                is_in_use=raw[0],is_tainted=raw[1],values=values)

def encode_changes(*args,**kwargs):
    raise PermissionError("MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED")
