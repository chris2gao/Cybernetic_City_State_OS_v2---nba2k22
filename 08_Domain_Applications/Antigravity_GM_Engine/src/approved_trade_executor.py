"""Controlled, player-authorized roster and simple-pick ownership transfers.

Bounded regular-roster executor v2: memory effects only, never saves/advances a game.
The caller must carry a concrete human approval; JSON cannot grant that approval.
No salary, attributes, minutes, strategy, or finance fields are written.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import struct

from source_extensions import player_details, roster_directory
from draft_assets import VERIFIED, read_assets, trade_window
from roster_associations import describe as roster_description, active_count_byte, verify_code
import config

VERSION = 'ownership_transfer_v2'
EXECUTION_ENABLED = True  # W02 count repair and CHI/DET UI accepted by player; bounded v2 only.
ROSTER_SIZE = 25
REGULAR_SLOTS = 15
# Observed pointer arrays in the current roster. No strategy/minute bytes overlap.
ACTIVE_POINTERS = (0xd0, 13)
LINEUP_POINTERS = (0xd28, 40)


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, data):
    """Durably replace a local journal; never upload runtime addresses."""
    import os
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def read_exact(mem, address, size):
    raw = mem.read_bytes(address, size)
    if raw is None or len(raw) != size:
        raise OSError(f'Incomplete read at {address:#x}, size {size}')
    return raw


def name(raw):
    part = lambda offset: raw[offset:offset + 40].decode('utf-16le').split('\0')[0].strip()
    return f'{part(40)} {part(0)}'.strip()


def identity(raw, specification):
    detail = player_details(raw)
    return (name(raw) == specification['name'] and
            struct.unpack_from('<H', raw, 0x6c)[0] == specification['face_id'] and
            detail['birth_date'] == specification['birth_date'])


def observe(mem, season_year=2022):
    """Calibrate one roster directory; never choose saved addresses unchecked."""
    from address_calibrator import AddressCalibrator
    import win32process
    verify_code(mem)
    calibrator = AddressCalibrator(mem)
    calibrator._save_runtime_map = lambda data: None
    ok, _, teams = calibrator.check_and_calibrate_teams()
    if not ok:
        raise RuntimeError('Team calibration failed')
    ok, root = calibrator.check_and_calibrate_player_pool()
    if not ok:
        raise RuntimeError('Player calibration failed')
    directory = roster_directory(mem, root)
    team_ids = {team['address']: tid for tid, team in teams.items()}
    team_raw = {tid: read_exact(mem, team['address'], config.TEAM_STRUCT_STRIDE)
                for tid, team in teams.items()}
    rosters = {tid: list(struct.unpack_from('<25Q', raw)) for tid, raw in team_raw.items()}
    members = {}
    for tid, pointers in rosters.items():
        for slot, pointer in enumerate(pointers):
            if pointer:
                members.setdefault(pointer, []).append((tid, slot))
    if any(len(locations) != 1 for locations in members.values()):
        raise RuntimeError('Duplicate NBA roster player pointer')
    assets, next_year = read_assets(mem, directory, team_ids, season_year)
    # A pointer's current-season header +4 is part of the observed statistics layout.
    season_headers = {}
    for tid, raw in team_raw.items():
        index = struct.unpack_from('<H', raw, 0xe80)[0]
        table = directory['team_stats']
        if index >= table['count']:
            raise RuntimeError('Invalid current team statistics index')
        record = read_exact(mem, table['address'] + index * table['stride'], table['stride'])
        season_headers[tid] = record[4] & 0x7f
    # Header convention comes from source_extensions.stats_record.
    if set(season_headers.values()) != {season_year-1900}:
        raise RuntimeError(f'Current season headers do not match approved season {season_year}: {set(season_headers.values())}')
    return {'pid': mem.pid, 'module_base': mem.base_address,
            'creation_time': str(win32process.GetProcessTimes(mem.handle)['CreationTime']),
            'root': root, 'directory': directory, 'teams': teams, 'team_ids': team_ids,
            'team_raw': team_raw, 'rosters': rosters, 'members': members,
            'assets': assets, 'next_draft_year': next_year, 'season_headers': season_headers}


def roster_transfer(raw, outgoing, incoming, replacement_map):
    """Keep other members and two-way slots; remove only transferred references.

    Existing lineup references are substituted with approved incoming players.
    A surplus outgoing member is removed from the active list; no new minutes or
    strategic choices are assigned. Situational five-player groups must remain
    complete and unique, otherwise the entire plan is rejected before writing.
    """
    if not roster_description(raw)['valid']:
        raise ValueError('Native roster/active/two-way counts or membership disagree before planning')
    result = bytearray(raw)
    original = list(struct.unpack_from('<25Q', raw))
    if any(pointer in outgoing for pointer in original[REGULAR_SLOTS:]):
        raise ValueError('Two-way outgoing transfers are outside this implementation')
    regular = original[:REGULAR_SLOTS]
    occupied = [p for p in regular if p]
    if regular[:len(occupied)] != occupied:
        raise ValueError('Non-contiguous regular roster layout')
    if set(outgoing) - set(occupied):
        raise ValueError('Outgoing member absent from source roster')
    mapped = [replacement_map.get(p, p) for p in occupied if replacement_map.get(p, p)]
    for pointer in incoming:
        if pointer not in mapped:
            mapped.append(pointer)
    if len(mapped) > REGULAR_SLOTS or len(mapped) != len(set(mapped)):
        raise ValueError('Roster capacity or duplicate incoming member')
    struct.pack_into('<15Q', result, 0, *(mapped + [0] * (REGULAR_SLOTS - len(mapped))))
    result[0xcb1] = len(mapped)
    allowed = set(mapped) | {p for p in original[REGULAR_SLOTS:] if p}
    offset, count = ACTIVE_POINTERS
    active = list(struct.unpack_from(f'<{count}Q', raw, offset))
    if any(p and p not in occupied for p in active) or len([p for p in active if p]) != len(set(p for p in active if p)):
        raise ValueError('Unrecognized active pointer list')
    active_new = [replacement_map.get(p, p) for p in active if replacement_map.get(p, p)]
    if len(active_new) != len(set(active_new)) or any(p not in allowed for p in active_new):
        raise ValueError('Invalid active pointer substitutions')
    struct.pack_into('<13Q', result, offset, *(active_new + [0] * (13 - len(active_new))))
    result[0x1047] = active_count_byte(raw[0x1047],len(active_new))
    offset, count = LINEUP_POINTERS
    refs = list(struct.unpack_from(f'<{count}Q', raw, offset))
    refs_new = []
    for begin in range(0, count, 5):
        group = refs[begin:begin + 5]
        if any(p and p not in occupied for p in group):
            raise ValueError('Unrecognized lineup reference')
        changed = [replacement_map.get(p, p) for p in group]
        if any(p not in allowed for p in changed) or len(set(changed)) != 5:
            raise ValueError('Removing a member would invalidate a five-player reference group')
        refs_new.extend(changed)
    struct.pack_into('<40Q', result, offset, *refs_new)
    # Reject target references outside the evidenced arrays rather than guessing.
    known = set(range(0, 0xc8, 8)) | set(range(0xd0, 0x138, 8)) | set(range(0xd28, 0xe68, 8))
    for off in range(0, len(raw) - 7, 8):
        if struct.unpack_from('<Q', raw, off)[0] in outgoing and off not in known:
            raise ValueError(f'Outgoing pointer at unknown team field {off:#x}')
    expected = (set(original) - {0} - set(outgoing)) | set(incoming)
    if set(struct.unpack_from('<25Q', result)) - {0} != expected:
        raise AssertionError('Non-target roster membership changed')
    if not roster_description(bytes(result))['valid']:
        raise ValueError('Planned native roster counts or associations are inconsistent')
    return bytes(result)


def player_row(raw, team_ids):
    data = player_details(raw, team_ids)
    return {'name': name(raw), 'face_id': struct.unpack_from('<H', raw, 0x6c)[0],
            'birth_date': data['birth_date'], 'current_team_id': data['current_team_id'],
            'contract_team_id': data['contract_team_id'], 'contract': data['contract']}


def build_plan(mem, state, specification, allow_count_repair=False):
    """Resolve identities, all-before/all-after state, and exact 64-bit patches."""
    rows, statuses = [], []
    for tid,raw in state['team_raw'].items():
        if not allow_count_repair and not roster_description(raw)['valid']:
            raise ValueError(f'Team {tid} roster/count inconsistency: investigate before trading')
    for player in specification['players']:
        found = []
        for tid in (player['from_team'], player['to_team']):
            for slot, pointer in enumerate(state['rosters'][tid]):
                if not pointer:
                    continue
                raw = read_exact(mem, pointer, 0x4f0)
                if identity(raw, player):
                    found.append((tid, slot, pointer, raw))
        if len(found) != 1:
            raise ValueError(f"Ambiguous/missing identity: {player['name']}")
        tid, slot, pointer, raw = found[0]
        details = player_row(raw, state['team_ids'])
        salary = [details['contract'][f'contract_year_{i}']['value'] for i in range(1, 7)]
        if salary != player['salary_sequence'] or details['contract']['years_left_on_contract']['value'] != player['years_left']:
            raise ValueError(f"Salary/term precondition changed: {player['name']}")
        if player.get('option') and details['contract']['contract_option'].get('label') != player['option']:
            raise ValueError('Approved contract option not present')
        if details['current_team_id'] != tid or details['contract_team_id'] != tid:
            raise ValueError('Current, contract and roster associations disagree')
        statuses.append('BEFORE' if tid == player['from_team'] else 'AFTER')
        rows.append({**player, 'address': pointer, 'roster_slot': slot,
                     'observed': details, 'raw_before': raw.hex()})
    picks = []
    for pick in specification['picks']:
        found = [(slot, row, raw) for slot, row, raw in state['assets']
                 if (row['draft_year'], row['draft_round'], row['original_owner_team_id']) ==
                 (pick['year'], pick['round'], pick['original_team']) and row['mapping_status'] == VERIFIED]
        if len(found) != 1 or pick['year'] not in trade_window(state['next_draft_year']):
            raise ValueError('Unverified/ambiguous/out-of-window draft asset')
        slot, row, raw = found[0]
        owner = row['current_owner_team_id']
        if owner not in (pick['from_team'], pick['to_team']):
            raise ValueError('Pick currently owned by a third team')
        statuses.append('BEFORE' if owner == pick['from_team'] else 'AFTER')
        picks.append({**pick, 'slot': slot, 'observed': row, 'raw_before': raw.hex(),
                      'address': state['directory']['draft_assets']['address'] + slot * 32})
    if len(set(statuses)) != 1:
        raise ValueError('Mixed/partially applied transaction: reconstruct before writing')
    tids = sorted({p[k] for p in rows for k in ('from_team','to_team')})
    plan = {'executor_version': VERSION, 'action_id': specification['action_id'],
            'decision_id': specification['decision_id'], 'version': specification.get('version',1),
            'save_id': None, 'save_identity_provenance': 'PLAYER_CURRENT_OPEN_SAVE',
            'game_date': None, 'season_verified': f"{1900+next(iter(state['season_headers'].values()))-1}-{1900+next(iter(state['season_headers'].values()))}",
            'process': {k: state[k] for k in ('pid','module_base','creation_time','root')},
            'status': 'NO_WRITE_NEEDED' if statuses[0] == 'AFTER' else 'PLANNED',
            'players': rows, 'picks': picks, 'patches': [],
            'teams': {str(tid): {'address': state['teams'][tid]['address'],
                                'before': state['team_raw'][tid].hex()} for tid in tids}}
    if plan['status'] == 'NO_WRITE_NEEDED':
        return plan
    def patch(address, old, new, kind, entity):
        if old != new:
            plan['patches'].append({'address': address, 'before': old.hex(), 'after': new.hex(),
                                    'kind': kind, 'entity': entity})
    for tid in tids:
        outgoing = [p['address'] for p in rows if p['from_team'] == tid]
        incoming = [p['address'] for p in rows if p['to_team'] == tid]
        # Role mappings are part of this task specification, never model-selected at runtime.
        by_face = {p['face_id']: p['address'] for p in rows}
        replacements = {by_face[int(face)]: by_face.get(target, 0)
                        for face, target in specification['reference_replacements'][str(tid)].items()}
        if set(replacements) != set(outgoing) or any(p and p not in incoming for p in replacements.values()):
            raise ValueError('Replacement mapping leaves approved assets')
        old = state['team_raw'][tid]
        new = roster_transfer(old, outgoing, incoming, replacements)
        plan['teams'][str(tid)]['expected'] = new.hex()
        reference_offsets = sorted(set(range(0,0xc8,8)) | set(range(0xd0,0x138,8)) | set(range(0xd28,0xe68,8)))
        for offset in reference_offsets:
            if old[offset:offset+8] != new[offset:offset+8]:
                patch(state['teams'][tid]['address'] + offset, old[offset:offset+8], new[offset:offset+8],
                      'TEAM_PLAYER_REFERENCE', f'team:{tid}:{offset:#x}')
        for offset in (0xcb1,0x1047):
            patch(state['teams'][tid]['address']+offset,old[offset:offset+1],new[offset:offset+1],
                  'TEAM_ROSTER_COUNT',f'team:{tid}:{offset:#x}')
    for player in rows:
        old = bytes.fromhex(player['raw_before'])
        new_owner = struct.pack('<Q', state['teams'][player['to_team']]['address'])
        for offset in (0x60, 0xa8):
            patch(player['address'] + offset, old[offset:offset+8], new_owner,
                  'PLAYER_TEAM_ASSOCIATION', f"{player['name']}:{offset:#x}")
    for pick in picks:
        old = bytes.fromhex(pick['raw_before'])
        new_owner = struct.pack('<Q', state['teams'][pick['to_team']]['address'])
        patch(pick['address'], old[:8], new_owner, 'PICK_CURRENT_OWNER',
              f"draft_pick:{pick['year']}:{pick['round']}:{pick['original_team']}")
    return plan


def verify_plan(mem, plan, state):
    results = {'teams': {}, 'players': [], 'picks': [], 'checks': {}, 'observed_at': now()}
    all_members = {}
    for tid, team in state['teams'].items():
        raw = read_exact(mem, team['address'], config.TEAM_STRUCT_STRIDE)
        pointers = list(struct.unpack_from('<25Q', raw))
        for pointer in pointers:
            if pointer:
                all_members.setdefault(pointer, []).append(tid)
        if str(tid) in plan['teams']:
            expected = bytes.fromhex(plan['teams'][str(tid)].get('expected', plan['teams'][str(tid)]['before']))
            # The complete team player-reference arrays must match. Finance is never written.
            windows = [(0,0xc8), (0xd0,0x138), (0xd28,0xe68),(0xcb1,0xcb2),(0x1047,0x1048)]
            matches = all(raw[a:b] == expected[a:b] for a,b in windows)
            results['teams'][str(tid)] = {'roster_count': sum(bool(p) for p in pointers),
                'roster_pointers': pointers, 'expected_reference_arrays_match': matches}
            results['checks'][f'team_{tid}_references'] = matches
        else:
            results['checks'][f'non_target_team_{tid}_roster'] = pointers == state['rosters'][tid]
        results['checks'][f'team_{tid}_native_counts'] = roster_description(raw)['valid']
    results['checks']['no_duplicate_nba_memberships'] = all(len(v) == 1 for v in all_members.values())
    for player in plan['players']:
        raw = read_exact(mem, player['address'], 0x4f0)
        detail = player_row(raw, state['team_ids'])
        old = bytearray.fromhex(player['raw_before'])
        # Identity, attributes, salary flags, terms, options, and all non-owner bytes preserved.
        for offset in (0x60,0xa8):
            old[offset:offset+8] = struct.pack('<Q', state['teams'][player['to_team']]['address'])
        checks = {'identity': identity(raw, player),
                  'current_owner': detail['current_team_id'] == player['to_team'],
                  'contract_owner': detail['contract_team_id'] == player['to_team'],
                  'unique_roster': all_members.get(player['address']) == [player['to_team']],
                  'non_owner_bytes_preserved': raw == bytes(old)}
        results['players'].append({**detail, 'target_team_id': player['to_team'], 'checks': checks})
        results['checks'][f"player_{player['face_id']}"] = all(checks.values())
    for pick in plan['picks']:
        raw = read_exact(mem, pick['address'], 32)
        old = bytes.fromhex(pick['raw_before'])
        expected = struct.pack('<Q', state['teams'][pick['to_team']]['address']) + old[8:]
        good = raw == expected
        results['picks'].append({'year': pick['year'], 'round': pick['round'],
            'original_team_id': pick['original_team'],
            'current_owner_team_id': state['team_ids'].get(struct.unpack_from('<Q', raw)[0]),
            'non_owner_bytes_preserved': raw[8:] == old[8:], 'matches': good})
        results['checks'][f"pick_{pick['year']}_{pick['round']}_{pick['original_team']}"] = good
    results['verified'] = all(results['checks'].values())
    return results


def execute_plan(mem, plan, state, output, human_approval_confirmed=False):
    """One write attempt per patch, immediate readback, durable partial receipts.

    No automatic retry or rollback: a failed API may have changed some bytes.
    The local before-byte journal supports diagnosis, not blind restoration.
    """
    if not EXECUTION_ENABLED:
        raise PermissionError('Executor quarantined after W02 crash / incomplete game roster; read-only investigation required')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'WRITE_ATTEMPTED').exists():
        raise RuntimeError('Prior write attempt exists; preserve receipt and inspect, never replay')
    receipt = {'executor_version': VERSION, 'action_id': plan['action_id'],
        'decision_id': plan['decision_id'], 'version': plan['version'], 'save_id': plan['save_id'],
        'process': plan['process'], 'started_at': now(), 'status': 'PRECONDITION_FAILED',
        'memory_scope': 'ROSTER_AND_OWNERSHIP_ONLY', 'journal': [], 'write_calls': 0,
        'persistence': 'PERSISTENCE_NOT_VERIFIED', 'player_ui_validation': 'PENDING',
        'database': 'NOT_SYNCED', 'published': False, 'automatic_rollback': False}
    dump(output / 'plan.json', plan)
    dump(output / 'receipt.json', receipt)
    if plan['status'] == 'NO_WRITE_NEEDED':
        receipt['verification'] = verify_plan(mem, plan, state)
        receipt['status'] = 'NO_WRITE_NEEDED' if receipt['verification']['verified'] else 'PRECONDITION_FAILED'
        dump(output / 'receipt.json', receipt)
        return receipt
    if not human_approval_confirmed or mem.read_only:
        raise PermissionError('Concrete human approval and an explicit write handle are required')
    # Entire transaction before checks, including the complete player/roster structures.
    for tid, data in plan['teams'].items():
        if read_exact(mem, data['address'], config.TEAM_STRUCT_STRIDE) != bytes.fromhex(data['before']):
            raise RuntimeError(f'Team {tid} changed since planning')
    for player in plan['players']:
        if read_exact(mem, player['address'], 0x4f0) != bytes.fromhex(player['raw_before']):
            raise RuntimeError('Player changed since planning')
    for pick in plan['picks']:
        if read_exact(mem, pick['address'], 32) != bytes.fromhex(pick['raw_before']):
            raise RuntimeError('Pick changed since planning')
    try:
        for item in plan['patches']:
            if mem.pid != plan['process']['pid'] or mem.base_address != plan['process']['module_base']:
                raise RuntimeError('Process identity changed')
            size=len(bytes.fromhex(item['before']))
            if size not in (1,8) or len(bytes.fromhex(item['after']))!=size:
                raise ValueError('Only evidenced one-byte counts and 64-bit pointers can be written')
            if read_exact(mem, item['address'], size) != bytes.fromhex(item['before']):
                raise RuntimeError(f"Write-before compare failed: {item['entity']}")
            step = {**item, 'status': 'WRITE_RESULT_UNKNOWN', 'at': now()}
            receipt['journal'].append(step)
            receipt['status'] = 'WRITE_RESULT_UNKNOWN'
            # Marker and journal are durable before the first mutation.
            (output / 'WRITE_ATTEMPTED').touch(exist_ok=True)
            dump(output / 'receipt.json', receipt)
            receipt['write_calls'] += 1
            success = mem.write_bytes(item['address'], bytes.fromhex(item['after']))
            actual = mem.read_bytes(item['address'], size)
            step['readback'] = actual.hex() if actual is not None else None
            step['api_success'] = success
            if not success or actual != bytes.fromhex(item['after']):
                raise OSError(f"Write/readback failed: {item['entity']}")
            step['status'] = 'READBACK_MATCHED'
            dump(output / 'receipt.json', receipt)
        receipt['verification'] = verify_plan(mem, plan, state)
        receipt['status'] = 'EXECUTED_VERIFIED' if receipt['verification']['verified'] else 'PARTIALLY_APPLIED'
    except Exception as exc:
        receipt['error'] = f'{type(exc).__name__}: {exc}'
        if any(s['status'] == 'READBACK_MATCHED' for s in receipt['journal']):
            receipt['status'] = 'PARTIALLY_APPLIED'
        elif receipt['write_calls']:
            receipt['status'] = 'WRITE_RESULT_UNKNOWN'
        try:
            receipt['verification'] = verify_plan(mem, plan, state)
        except Exception as read_error:
            receipt['verification_error'] = str(read_error)
    receipt['completed_at'] = now()
    dump(output / 'receipt.json', receipt)
    return receipt
