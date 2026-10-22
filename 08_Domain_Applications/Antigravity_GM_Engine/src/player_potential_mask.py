"""GM-world fog: mask only persisted PLAYER Potential, never game memory.

Run against capture working copies before installation/hash/immutable export.
Old sealed batches are excluded from GM consumption, not rewritten. Staff and
all other PLAYER bytes remain unchanged. Unknown mirrors fail closed.
"""
from copy import deepcopy
import json
import hashlib
import sqlite3

VERSION = 'potential_v1'
PLAYER_BYTES = 0x4f0
OFFSET = 0x441
PLAYER_KINDS = {'PLAYER_TENDENCY','PLAYER_PLAYTYPE','PLAYER_ROTATION_OVR_BIAS'}
MARKERS = dict(source_role='GM_SANITIZED', potential_mask_version=VERSION,
               player_raw_masked=True)
FIELD_MARKERS = dict(visibility='MASKED_BY_GM_WORLD_RULE', evidence='NOT_GAME_OBSERVED')


def mask_raw(raw):
    raw = bytes(raw)
    if len(raw) != PLAYER_BYTES:
        raise ValueError('POTENTIAL_SANITIZATION_FAILED_INCOMPLETE_PLAYER_RAW')
    return raw[:OFFSET]+b'\x01'+raw[OFFSET+1:]


def mask_details(details):
    result = deepcopy(details)
    potential = result.get('attributes',{}).get('potential')
    if not isinstance(potential,dict) or 'raw' not in potential or 'value' not in potential:
        raise ValueError('POTENTIAL_SANITIZATION_FAILED_MISSING_PLAYER_POTENTIAL')
    # Drop any future, unreviewed aliases rather than accidentally retaining an
    # original value under a new key inside this known field.
    result['attributes']['potential'] = dict(raw=1, value=1, **FIELD_MARKERS)
    result.update(MARKERS)
    result['mask_version'] = VERSION
    return result


def tables(c):
    return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def policy(c, snapshot_id):
    if 'player_potential_masks' not in tables(c):
        return None
    row = c.execute('SELECT policy_json FROM player_potential_masks WHERE snapshot_id=?',(snapshot_id,)).fetchone()
    return json.loads(row[0]) if row else None


def masked(c, snapshot_id):
    p = policy(c,snapshot_id)
    return bool(p and p.get('potential_mask_version') == VERSION and p.get('source_role') == 'GM_SANITIZED')


def _unknown_mirrors(c, known):
    # Explicit coverage inventory. A new schema surface must get a reviewed
    # sanitizer; silently hiding it in a query is insufficient.
    for table in tables(c):
        if table.startswith('staff_'):
            continue
        columns = [r[1] for r in c.execute('PRAGMA table_info("'+table.replace('"','""')+'")')]
        if any('potential' in col.lower() for col in columns) and table != 'player_pool':
            raise ValueError('UNKNOWN_POTENTIAL_COLUMN:'+table)
        quoted = '"'+table.replace('"','""')+'"'
        if 'raw_struct' in columns and table not in known:
            if c.execute('SELECT 1 FROM '+quoted+' WHERE length(raw_struct)=? LIMIT 1',(PLAYER_BYTES,)).fetchone():
                raise ValueError('UNKNOWN_PLAYER_RAW_MIRROR:'+table)
        for col in columns:
            if (col.endswith('_json') or col.endswith('Json')) and (table,col) not in {
                ('player_pool','source_details_json'),('player_source_details','details_json'),
                ('state_io_objects','object_json'),('player_potential_masks','policy_json')}:
                qcol='"'+col.replace('"','""')+'"'
                for row in c.execute('SELECT '+qcol+' FROM '+quoted+' WHERE '+qcol+' IS NOT NULL'):
                    # Catalogs contain a field name, not original player values.
                    value=json.loads(row[0])
                    if _has_potential_value(value) or _contains_player_blob(value):
                        raise ValueError('UNKNOWN_PLAYER_POTENTIAL_JSON_MIRROR:'+table+'.'+col)


def _has_potential_value(value):
    if isinstance(value,dict):
        return any(('potential' in k.casefold() and k not in ('potential_mask_version',))
                   or _has_potential_value(v) for k,v in value.items())
    return isinstance(value,list) and any(_has_potential_value(v) for v in value)


def _contains_player_blob(value):
    if isinstance(value,str) and len(value)==PLAYER_BYTES*2:
        try:
            bytes.fromhex(value)
            return True
        except ValueError:
            return False
    if isinstance(value,dict):
        return any(_contains_player_blob(v) for v in value.values())
    return isinstance(value,list) and any(_contains_player_blob(v) for v in value)


def _check_state_object(obj):
    if _has_potential_value(obj) or _contains_player_blob({k:v for k,v in obj.items() if k!='raw'}):
        raise ValueError('UNKNOWN_PLAYER_STATE_IO_POTENTIAL_ALIAS')


def _unmasked_fingerprint(league,pool):
    result=hashlib.sha256()
    def add(identity,raw):
        raw=bytes(raw)
        if len(raw)!=PLAYER_BYTES:
            raise ValueError('INCOMPLETE_PLAYER_RAW')
        result.update(json.dumps(identity,separators=(',',':')).encode())
        result.update(raw[:OFFSET]+raw[OFFSET+1:])
    for slot,raw in pool.execute('SELECT slot_id,raw_struct FROM player_pool ORDER BY slot_id'):
        add(['pool',slot],raw)
    for sid,tid,slot,raw in league.execute('SELECT snapshot_id,team_id,roster_slot,raw_struct FROM player_source_details ORDER BY snapshot_id,team_id,roster_slot'):
        add(['roster',sid,tid,slot],raw)
    if 'state_io_objects' in tables(league):
        for sid,key,payload in league.execute('SELECT snapshot_id,object_key,object_json FROM state_io_objects ORDER BY snapshot_id,object_key'):
            obj=json.loads(payload)
            if obj['selector']['target_kind'] in PLAYER_KINDS:
                add(['state_io',sid,key],bytes.fromhex(obj['raw']))
    return result.hexdigest()


def sanitize_player_potential(league, pool, snapshot_id, *, dry_run=False):
    """Use savepoints on both working copies. Caller commits and installs both.

    A dry run performs and verifies changes under savepoints, then rolls them
    back. Never return or log original Potential values.
    """
    existing=policy(league,snapshot_id)
    if existing and existing==policy(pool,snapshot_id):
        # Re-validating an already complete cohort must not rewrite its bytes.
        return dict(verify_sanitized_pair(league,pool,snapshot_id),dry_run=dry_run)
    connections=(league,pool)
    for c in connections:
        c.execute('PRAGMA secure_delete=ON')
        c.execute('SAVEPOINT potential_mask')
    try:
        if 'player_pool' not in tables(pool) or 'player_source_details' not in tables(league):
            raise ValueError('REQUIRED_PLAYER_SURFACE_MISSING')
        _unknown_mirrors(pool,{'player_pool'})
        _unknown_mirrors(league,{'player_source_details'})
        unmasked_before=_unmasked_fingerprint(league,pool)
        counts=dict(pool=0,roster=0,state_io_player_mirrors=0)
        for slot,raw,detail_json in pool.execute('SELECT slot_id,raw_struct,source_details_json FROM player_pool').fetchall():
            detail=mask_details(json.loads(detail_json))
            pool.execute('UPDATE player_pool SET raw_potential=1,potential=1,raw_struct=?,source_details_json=? WHERE slot_id=?',
                         (mask_raw(raw),json.dumps(detail,sort_keys=True),slot))
            counts['pool']+=1
        # New export copies can contain historical rows; sanitize those copies
        # as well, while immutable old archives/snapshots remain untouched.
        for sid,tid,slot,raw,detail_json in league.execute('SELECT snapshot_id,team_id,roster_slot,raw_struct,details_json FROM player_source_details').fetchall():
            league.execute('UPDATE player_source_details SET raw_struct=?,details_json=? WHERE snapshot_id=? AND team_id=? AND roster_slot=?',
                           (mask_raw(raw),json.dumps(mask_details(json.loads(detail_json)),sort_keys=True),sid,tid,slot))
            counts['roster']+=1
        if 'state_io_objects' in tables(league):
            for sid,key,payload in league.execute('SELECT snapshot_id,object_key,object_json FROM state_io_objects').fetchall():
                obj=json.loads(payload)
                _check_state_object(obj)
                kind=obj['selector']['target_kind']
                if kind in PLAYER_KINDS:
                    obj['raw']=mask_raw(bytes.fromhex(obj['raw'])).hex()
                    obj.update(MARKERS)
                    counts['state_io_player_mirrors']+=1
                    league.execute('UPDATE state_io_objects SET object_json=? WHERE snapshot_id=? AND object_key=?',
                                   (json.dumps(obj,sort_keys=True),sid,key))
                elif kind.startswith('PLAYER') and obj.get('raw') and len(bytes.fromhex(obj['raw']))==PLAYER_BYTES:
                    raise ValueError('UNKNOWN_PLAYER_STATE_IO_MIRROR:'+kind)
        if not counts['pool'] or not counts['roster']:
            raise ValueError('EMPTY_REQUIRED_PLAYER_SURFACE')
        if 'state_io_captures' in tables(league):
            for sid,payload in league.execute('SELECT snapshot_id,metadata_json FROM state_io_captures').fetchall():
                meta=json.loads(payload);meta.update(MARKERS)
                meta['mask_scope']='PLAYER_POTENTIAL_ONLY_STAFF_UNCHANGED'
                league.execute('UPDATE state_io_captures SET metadata_json=? WHERE snapshot_id=?',
                               (json.dumps(meta,sort_keys=True),sid))
        receipt=dict(**MARKERS,mask_version=VERSION,masked_value=1,counts=counts,
                     pool_total=counts['pool'],roster_total=counts['roster'],
                     masked_json_count=counts['pool']+counts['roster'],
                     masked_blob_count=sum(counts.values()),missed_rows=0,
                     nonpotential_player_bytes_sha256=unmasked_before,
                     visibility='MASKED_BY_GM_WORLD_RULE',evidence='NOT_GAME_OBSERVED',
                     historical_access='OLD_UNMASKED_BATCHES_EXCLUDED_FROM_GM_NOT_REWRITTEN')
        for c in connections:
            c.execute('CREATE TABLE IF NOT EXISTS player_potential_masks(snapshot_id TEXT PRIMARY KEY,policy_json TEXT NOT NULL)')
            c.execute('INSERT OR REPLACE INTO player_potential_masks VALUES (?,?)',(snapshot_id,json.dumps(receipt,sort_keys=True)))
        verify_sanitized_pair(league,pool,snapshot_id)
        for c in connections:
            if dry_run:
                c.execute('ROLLBACK TO potential_mask')
            c.execute('RELEASE potential_mask')
        return dict(receipt,dry_run=dry_run)
    except Exception as exc:
        for c in connections:
            c.execute('ROLLBACK TO potential_mask')
            c.execute('RELEASE potential_mask')
        raise ValueError('POTENTIAL_SANITIZATION_FAILED:'+str(exc)) from exc


def verify_sanitized_pair(league,pool,snapshot_id):
    """Validate database surfaces before sealing, not publication JSON sync."""
    if not masked(league,snapshot_id) or policy(league,snapshot_id) != policy(pool,snapshot_id):
        raise ValueError('POTENTIAL_SANITIZATION_FAILED_MASK_POLICY_REQUIRED')
    _unknown_mirrors(pool,{'player_pool'})
    _unknown_mirrors(league,{'player_source_details'})
    counts=dict(pool=0,roster=0,state_io_player_mirrors=0)
    for raw,pot,rawpot,detail in pool.execute('SELECT raw_struct,potential,raw_potential,source_details_json FROM player_pool'):
        data=json.loads(detail)
        if mask_raw(raw)!=raw or (pot,rawpot)!=(1,1) or mask_details(data)!=data:
            raise ValueError('POTENTIAL_SANITIZATION_FAILED_POOL_NOT_MASKED')
        counts['pool']+=1
    for raw,detail in league.execute('SELECT raw_struct,details_json FROM player_source_details'):
        data=json.loads(detail)
        if mask_raw(raw)!=raw or mask_details(data)!=data:
            raise ValueError('POTENTIAL_SANITIZATION_FAILED_ROSTER_NOT_MASKED')
        counts['roster']+=1
    if 'state_io_objects' in tables(league):
        for payload, in league.execute('SELECT object_json FROM state_io_objects'):
            obj=json.loads(payload);kind=obj['selector']['target_kind']
            _check_state_object(obj)
            if kind in PLAYER_KINDS:
                counts['state_io_player_mirrors']+=1
                raw=bytes.fromhex(obj['raw'])
                if raw!=mask_raw(raw) or any(obj.get(k)!=v for k,v in MARKERS.items()):
                    raise ValueError('POTENTIAL_SANITIZATION_FAILED_STATE_IO_NOT_MASKED')
            elif kind.startswith('PLAYER') and obj.get('raw') and len(bytes.fromhex(obj['raw']))==PLAYER_BYTES:
                raise ValueError('POTENTIAL_SANITIZATION_FAILED_UNKNOWN_STATE_IO_PLAYER')
    receipt=policy(league,snapshot_id)
    if not counts['pool'] or not counts['roster'] or receipt['counts']!=counts:
        raise ValueError('POTENTIAL_SANITIZATION_FAILED_COVERAGE_COUNT_MISMATCH')
    if receipt['nonpotential_player_bytes_sha256'] != _unmasked_fingerprint(league,pool):
        raise ValueError('POTENTIAL_SANITIZATION_FAILED_UNSELECTED_PLAYER_BYTES_CHANGED')
    return receipt
