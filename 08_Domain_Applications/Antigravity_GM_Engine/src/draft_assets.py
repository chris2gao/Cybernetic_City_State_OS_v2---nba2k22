"""Read and decode simple draft assets; no writes or GM decision generation."""
from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path
import struct

VERIFIED = 'VERIFIED_SIMPLE_FUTURE_PICK'


@lru_cache(maxsize=1)
def profile():
    return json.loads((Path(__file__).resolve().parents[1] / 'config/draft_asset_profile.json').read_text(encoding='utf-8'))


def trade_window(next_draft_year):
    if type(next_draft_year) is not int or not 2000 <= next_draft_year <= 2100:
        raise ValueError('Verified next draft year required')
    return list(range(next_draft_year, next_draft_year + 3))


def decode_asset(raw, team_ids):
    p = profile()
    if len(raw) != p['record_stride']:
        raise RuntimeError('Truncated draft asset record')
    owner, original, assigned = struct.unpack_from('<QQQ', raw)
    meta = struct.unpack_from('<I', raw, p['metadata_offset'])[0]
    bits = lambda field: (meta >> p[field][0]) & ((1 << p[field][1]) - 1)
    year_offset, round_code = bits('native_year_offset_bits'), bits('round_bits')
    row = {'current_owner_team_id': team_ids.get(owner), 'original_owner_team_id': team_ids.get(original),
           'draft_year': None, 'draft_round': None, 'protection': None,
           'mapping_status': 'NOT_A_VERIFIED_FUTURE_PICK'}
    if not owner:
        return row
    if not p['native_future_year_offset_range'][0] <= year_offset <= p['native_future_year_offset_range'][1]:
        return row  # Past selected players and live prospects are not future pick assets.
    if owner not in team_ids or original not in team_ids or assigned or round_code not in (0, 1):
        raise RuntimeError('Invalid future draft owner/player/round structure')
    year = p['absolute_year_epoch'] + bits('absolute_year_bits')
    if not 2000 <= year <= 2100:
        raise RuntimeError('Invalid future draft year')
    row.update(draft_year=year, draft_round=round_code + 1, mapping_status=VERIFIED)
    return row


def read_assets(mem, directory, team_ids, season_year):
    """Require native code semantics and a complete, consistent NBA future-pick set."""
    for item in profile()['code_evidence']:
        expected = bytes.fromhex(item['expected_hex'])
        if mem.read_bytes(mem.base_address + item['module_rva'], len(expected)) != expected:
            raise RuntimeError(f"Draft getter version mismatch: {item['name']}")
    table = directory['draft_assets']
    observations, groups, indices, base_years = [], defaultdict(list), defaultdict(set), set()
    for slot in range(table['count']):
        raw = mem.read_bytes(table['address'] + slot * table['stride'], table['stride'])
        if raw is None:
            raise RuntimeError(f'Unreadable draft asset {slot}')
        row = decode_asset(raw, team_ids)
        observations.append((slot, row, raw))
        if row['mapping_status'] != VERIFIED:
            continue
        meta = struct.unpack_from('<I', raw, profile()['metadata_offset'])[0]
        key = (row['draft_year'], row['draft_round'])
        pick_index = (meta >> 8) & 255
        if pick_index in indices[key] or not 0 <= pick_index < len(team_ids):
            raise RuntimeError('Duplicate or invalid draft PickIndex within year/round')
        indices[key].add(pick_index)
        groups[key].append(row['original_owner_team_id'])
        base_years.add(row['draft_year'] - (meta & 7))
    if len(base_years) != 1:
        raise RuntimeError('Future draft years have conflicting or absent base years')
    next_year = base_years.pop()
    if next_year not in (season_year, season_year + 1):
        raise RuntimeError('Draft base year does not match the requested season')
    expected_groups = {(next_year + offset, rd) for offset in range(5) for rd in (1, 2)}
    if set(groups) != expected_groups or any(len(values) != len(team_ids) or set(values) != set(team_ids.values()) for values in groups.values()):
        raise RuntimeError('Future draft table lacks one original pick per NBA team/year/round')
    return observations, next_year


def capture_assets(conn, snapshot_id, mem, directory, team_ids, season_year):
    observations, next_year = read_assets(mem, directory, team_ids, season_year)
    for slot, row, raw in observations:
        conn.execute('INSERT INTO draft_asset_observations VALUES (?,?,?,?,?,?,?,?,?)',
                     (snapshot_id, slot, row['current_owner_team_id'], row['original_owner_team_id'],
                      row['draft_year'], row['draft_round'], None, row['mapping_status'], raw))
    return {'next_draft_year': next_year, 'tradeable_draft_years': trade_window(next_year),
            'verified_future_picks': sum(row['mapping_status'] == VERIFIED for _, row, _ in observations),
            'protection_and_swaps': 'NOT_USED_BY_PLAYER_RULES'}
