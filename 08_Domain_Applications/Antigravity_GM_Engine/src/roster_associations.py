"""Exact NBA2K22 roster counts, independent of game writes or attachment."""
from functools import lru_cache
import json
from pathlib import Path
import struct


@lru_cache(maxsize=1)
def profile():
    return json.loads((Path(__file__).resolve().parents[1] / 'config/roster_association_profile.json').read_text(encoding='utf-8'))


def active_count_byte(original, count):
    if type(original) is not int or not 0 <= original <= 255:
        raise ValueError('Original byte required')
    if type(count) is not int or not 0 <= count <= 13:
        raise ValueError('Active count outside native capacity')
    return (original & 0x0f) | (count << 4)


def describe(raw):
    if len(raw) != 0x1258:
        raise ValueError('Full team structure required')
    pointers = list(struct.unpack_from('<25Q',raw))
    regular = pointers[:15]
    active = list(struct.unpack_from('<13Q',raw,0xd0))
    regular_count = sum(bool(p) for p in regular)
    active_count = sum(bool(p) for p in active)
    twoway_count = sum(bool(p) for p in pointers[21:23])
    unique = [p for p in pointers if p]
    checks = {
        'regular_capacity':regular_count <= 15,
        'regular_contiguous':regular[:regular_count] == [p for p in regular if p],
        'reserved_slots_empty':not any(pointers[15:21]) and not any(pointers[23:]),
        'unique_members':len(unique)==len(set(unique)),
        'active_contiguous':active[:active_count] == [p for p in active if p],
        'unique_active':len([p for p in active if p])==len(set(p for p in active if p)),
        'active_members_are_rostered':all(p in pointers for p in active if p),
        'regular_count_matches':raw[0xcb1]==regular_count,
        'active_count_matches':raw[0x1047]>>4==active_count,
        'two_way_count_matches':raw[0x1047]&3==twoway_count,
    }
    return {'regular_count':regular_count,'regular_count_field':raw[0xcb1],
            'active_count':active_count,'active_count_field':raw[0x1047]>>4,
            'two_way_count':twoway_count,'two_way_count_field':raw[0x1047]&3,
            'packed_count_raw':raw[0x1047],'checks':checks,'valid':all(checks.values())}


def verify_code(mem):
    for item in profile()['code_evidence']:
        expected = bytes.fromhex(item['expected_hex'])
        actual = mem.read_bytes(mem.base_address + item['module_rva'],len(expected))
        if actual != expected:
            raise RuntimeError('Roster-count native signature mismatch: '+item['name'])
