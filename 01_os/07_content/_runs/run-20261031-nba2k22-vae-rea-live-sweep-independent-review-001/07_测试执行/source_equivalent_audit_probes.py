"""Independent source-equivalent probes for f1e02101ead9e48c0dd3591e8c76501e407acfab.
This does NOT import Gemini original package, execute original eight pytest tests, nor attach to NBA2K22.
Record values manually transcribed from fixed GitHub field_records; source flow from
src/vae_rea_research/live_analyzer.py and src/memory.py; run: python source_equivalent_audit_probes.py
"""
import struct

coach = {
    'POEOffense': (97, {0,1,2,3,4,5,6}),
    'POEOffense2': (0, {0,7,8,9}),
    'POEOffense3': (100, {0,10,11,12}),
    'POEDefense': (0, {0,13,14,15}),
    'POEDefense2': (101, {0,16,17,18}),
    'POEDefense3': (0, {0,19,20,21}),
    'PreferredSystem': (223, set(range(8))),
    'ActiveSystem': (230, set(range(8))),
    'ZoneUsage': (112, set(range(101))),
    'BenchUtilization': (104, set(range(101))),
    'HelpDefense': (108, set(range(101))),
    'FreelanceType2': (97, set(range(34))),
    'FreelanceType4': (95, set(range(34))),
}
invalid=[name for name,(value,domain) in coach.items() if value not in domain]
assert len(invalid)==10, invalid
print("PASS_COACH_INVALID:",len(invalid),"of",len(coach),invalid)

raw=1056964608
assert struct.unpack('<f',struct.pack('<I',raw))[0]==0.5
print("PASS_FLOAT_DECODING: 1056964608 -> float32 0.5")

assert 21234136 not in (0,1) and not 0<=271058973<=100
print("PASS_WORLD_RANGE_INVALID: normalize_stats and player_non_financial_ambitions")

aliases={"WORLD_REG_002":"0x7ff4e68fe038","WORLD_REG_085":"0x7ff4e68fe038","WORLD_REG_086":"0x7ff4e68fe038"}
assert len(set(aliases.values()))==1
print("PASS_WORLD_ID_COLLISION: 3 seed IDs share one raw address")

value,addr=1,"STATIC_GP_LAYOUT"
promoted=value is not None and addr not in ("NO_PROCESS","UNKNOWN_OFFSET")
assert promoted
print("PASS_STATIC_FALLBACK_PROMOTION: incorrectly qualifies as LIVE_RECEIPT")

failed_safe=None
legacy_uint8=failed_safe if failed_safe is not None else 0
assert legacy_uint8==0 and legacy_uint8 is not None
print("PASS_FAILED_READ_AS_ZERO: erroneously qualifies for LIVE_RECEIPT")
