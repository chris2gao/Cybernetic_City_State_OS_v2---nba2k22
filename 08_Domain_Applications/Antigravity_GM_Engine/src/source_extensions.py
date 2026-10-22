"""Deterministic decoders for calibrated NBA2K22 roster records.

No process attachment or writes here. Runtime pointers are resolved to capture-local
team IDs, and are never persisted as entity identities.
"""
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
import struct

import config


@lru_cache(maxsize=1)
def profile():
    return json.loads((Path(__file__).resolve().parents[1] / 'config/memory_field_profile.json').read_text(encoding='utf-8'))


def decode_fields(raw, kind):
    result = {}
    for field in profile()['fields'][kind]:
        offset = field['offset']
        if 'bits' in field:
            count = (field['start_bit'] + field['bits'] + 7) // 8
        else:
            count = field['bytes']
        if offset + count > len(raw):
            raise ValueError(f"Truncated {kind} field {field['name']}")
        value = int.from_bytes(raw[offset:offset + count], 'little')
        if 'bits' in field:
            value = (value >> field['start_bit']) & ((1 << field['bits']) - 1)
        decoded = config.raw_to_rating(value) if field.get('conversion') == 'rating' else value
        row = {'raw': value, 'value': decoded}
        if 'labels' in field:
            row['label'] = field['labels'].get(str(value))
        result.setdefault(field['group'], {})[field['name']] = row
    return result


def player_details(raw, team_ids=None, game_date=None):
    fields = decode_fields(raw, 'PLAYER')
    birth = None
    try:
        birth = date(int.from_bytes(raw[0x6e:0x70], 'little') & 0xfff, raw[0x6f] >> 4, raw[0x70] & 31)
    except ValueError:
        pass  # Invalid/sentinel dates remain unknown, including historical models.
    age = None
    if birth and game_date:
        day = date.fromisoformat(game_date)
        candidate = day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))
        age = candidate if candidate >= 0 else None
    team_ids = team_ids or {}
    return {'profile_version': profile()['profile_version'], 'birth_date': birth.isoformat() if birth else None,
            'age': age, 'age_as_of': game_date if age is not None else None,
            'age_source': 'PYTHON_FROM_OBSERVED_DOB_AND_USER_DATE' if age is not None else 'DATE_UNCONFIRMED_OR_INVALID_DOB',
            'current_team_id': team_ids.get(struct.unpack_from('<Q', raw, 0x60)[0]),
            'contract_team_id': team_ids.get(struct.unpack_from('<Q', raw, 0xa8)[0]),
            'attributes': fields['attributes'], 'contract': fields['contract'],
            'overall_rating': None, 'overall_source': 'NOT_OBSERVED',
            'data_source': 'LIVE_MEMORY'}


STAFF_TEAM_SLOTS = {0: 0xce8, 1: 0xcf0, 2: 0xcf8, 3: 0xd00,
                    4: 0xd08, 5: 0xd10, 6: 0xd18, 7: 0xd20}


def roster_directory(mem, root):
    """Resolve descriptor pointers anew from the calibrated roster root.

    End-of-array equations establish counts/strides. Empty names do not end a pool.
    """
    definitions = {'players': (0x20, 0x4f0), 'staff': (0x140, 0x160),
                   'player_stats': (0x190, 48), 'team_stats': (0x1d0, 62),
                   'draft_assets': (0x2b0, 32)}
    result = {}
    for kind, (offset, stride) in definitions.items():
        address = mem.require_uint64(root + offset)
        count = mem.require_uint64(root + offset - 8)
        end = mem.require_uint64(root + offset + 0x10)
        if not 0 < count <= 100000 or end != address + count * stride:
            raise RuntimeError(f'Invalid roster directory descriptor: {kind}')
        if mem.read_bytes(address, stride) is None or mem.read_bytes(end - stride, stride) is None:
            raise RuntimeError(f'Unreadable roster directory array: {kind}')
        result[kind] = {'address': address, 'count': count, 'stride': stride}
    if result['players']['address'] != root + 0x4f0:
        raise RuntimeError('Player descriptor does not match calibrated historical-model anchors')
    return result


def stats_record(mem, directory, kind, index, season_year):
    table = directory[kind]
    if index == 65535:
        return None, None
    if not 0 <= index < table['count']:
        raise RuntimeError(f'Stats index outside {kind} descriptor')
    raw = mem.read_bytes(table['address'] + index * table['stride'], table['stride'])
    if raw is None:
        raise RuntimeError(f'Unreadable {kind} record')
    fields = decode_fields(raw, 'TEAM_STATS' if kind == 'team_stats' else 'PLAYER_STATS')['totals']
    values = {k: v['value'] for k, v in fields.items()}
    observed_year = 1900 + (raw[4] & 0x7f) if kind == 'team_stats' else 1900 + values['season']
    if observed_year != season_year:
        raise RuntimeError(f'Current stats points to another season: {observed_year}')
    ft_key = 'free_throws_made'
    if values['points'] != 2 * values['made'] + values['3pt_made'] + values[ft_key]:
        raise RuntimeError(f'Invalid scoring identity in {kind}')
    values['season_year'] = observed_year
    return values, raw


def per_game(total, games):
    return round(total / games, 6) if games else None


def percentage(made, attempts):
    return round(made / attempts, 8) if attempts else None


def team_statistics(values):
    games = values['w'] + values['l']
    return {'total_games': games, 'total_wins': values['w'], 'total_losses': values['l'],
            'win_pct': percentage(values['w'], games), 'ppg': per_game(values['points'], games),
            'opp_ppg': per_game(values['pa'], games), 'fg_pct': percentage(values['made'], values['attempted']),
            'three_pt_pct': percentage(values['3pt_made'], values['3pt_attempted']),
            'ft_pct': percentage(values['free_throws_made'], values['free_throws_attempted']),
            'rpg': per_game(values['offensive_rebounds'] + values['defensive_rebounds'], games),
            'apg': per_game(values['assists'], games), 'tov_pg': per_game(values['turnover'], games)}


def player_statistics(values):
    if values is None:
        return {}  # An absent stats ID does not prove zero games.
    games = values['times']
    return {'games_played': games, 'minutes_per_game': per_game(values['minutes'], games),
            'ppg': per_game(values['points'], games),
            'rpg': per_game(values['offensive_rebounds'] + values['defensive_rebounds'], games),
            'apg': per_game(values['assists'], games), 'spg': per_game(values['steals'], games),
            'bpg': per_game(values['blocks'], games), 'tov_pg': per_game(values['turnover'], games),
            'fg_pct': percentage(values['made'], values['attempted']),
            'three_pt_pct': percentage(values['3pt_made'], values['3pt_attempted']),
            'ft_pct': percentage(values['free_throws_made'], values['free_throws_attempted'])}


def staff_details(mem, name_anchor, slot, teams):
    address = name_anchor - 0x30
    raw = mem.read_bytes(address, 0x160)
    if raw is None:
        raise RuntimeError(f'Unreadable full staff record {slot}')
    team_pointer = struct.unpack_from('<Q', raw, 0x18)[0]
    matching = [(tid, t) for tid, t in teams.items() if t['address'] == team_pointer]
    team_id = None
    status = 'UNMAPPED_NOT_ASSUMED_FREE_AGENT'
    role = None
    if matching:
        team_id, team = matching[0]
    fields = decode_fields(raw, 'STAFF')
    role_code = fields['vitals']['position']['value']
    role = fields['vitals']['position'].get('label')
    if matching:
        if mem.require_uint64(team['address'] + STAFF_TEAM_SLOTS[role_code]) != address:
            raise RuntimeError(f'Staff {slot} team link lacks reciprocal role pointer')
        status = 'VERIFIED_RECIPROCAL_TEAM_ROLE'
    return {'staff_slot': slot, 'team_id': team_id, 'role': role, 'team_mapping_status': status,
            'first_name': raw[0x30:0x58].decode('utf-16le', errors='strict').split('\0')[0].strip(),
            'last_name': raw[0x58:0x80].decode('utf-16le', errors='strict').split('\0')[0].strip(),
            'fields': fields, 'profile_version': profile()['profile_version'], 'data_source': 'LIVE_MEMORY'}, raw


def ensure_extension_schema(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS player_source_details (
        snapshot_id TEXT NOT NULL, team_id INTEGER NOT NULL, roster_slot INTEGER NOT NULL,
        pool_slot INTEGER, player_name TEXT NOT NULL, face_id INTEGER NOT NULL,
        birth_date TEXT, age INTEGER, details_json TEXT NOT NULL,
        raw_struct BLOB NOT NULL,
        PRIMARY KEY(snapshot_id, team_id, roster_slot),
        FOREIGN KEY(snapshot_id) REFERENCES monthly_snapshots(snapshot_id))''')
    conn.execute('''CREATE TABLE IF NOT EXISTS team_source_stats (
        snapshot_id TEXT NOT NULL, team_id INTEGER NOT NULL, stats_index INTEGER NOT NULL,
        totals_json TEXT NOT NULL, raw_struct BLOB NOT NULL,
        PRIMARY KEY(snapshot_id,team_id))''')
    conn.execute('''CREATE TABLE IF NOT EXISTS draft_asset_observations (
        snapshot_id TEXT NOT NULL, asset_slot INTEGER NOT NULL,
        current_owner_team_id INTEGER, original_owner_team_id INTEGER,
        draft_year INTEGER, draft_round INTEGER, protection TEXT,
        mapping_status TEXT NOT NULL, raw_struct BLOB NOT NULL,
        PRIMARY KEY(snapshot_id,asset_slot))''')
    conn.execute('''CREATE TABLE IF NOT EXISTS staff_source_details (
        snapshot_id TEXT NOT NULL, staff_slot INTEGER NOT NULL, team_id INTEGER,
        role TEXT, team_mapping_status TEXT NOT NULL, details_json TEXT NOT NULL,
        raw_struct BLOB NOT NULL,
        PRIMARY KEY(snapshot_id, staff_slot),
        FOREIGN KEY(snapshot_id) REFERENCES monthly_snapshots(snapshot_id))''')


def store_player(conn, snapshot_id, tid, roster_slot, pool_slot, name, face_id, raw, team_ids, game_date):
    details = player_details(raw, team_ids, game_date)
    if details['current_team_id'] != tid:
        raise RuntimeError(f'Roster and player CURRENT_TEAM pointer disagree: {name}')
    conn.execute('INSERT INTO player_source_details VALUES (?,?,?,?,?,?,?,?,?,?)',
                 (snapshot_id, tid, roster_slot, pool_slot, name, face_id, details['birth_date'], details['age'],
                  json.dumps(details, sort_keys=True), raw))
    return details
