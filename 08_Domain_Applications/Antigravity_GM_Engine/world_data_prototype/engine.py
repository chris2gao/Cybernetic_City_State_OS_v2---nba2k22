"""Initial NBA2K22 per-save world-data SQLite prototype.

No memory access, game writes, live data claiming, or old-schema migration.
This first implementation accepts *only explicitly synthetic fixture inputs*.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

SCHEMA = Path(__file__).with_name('schema.sql')
ALLOWED_CAPTURE_FIELDS = frozenset({'overall_raw','shot_close_raw','driving_layup_raw'})
ALLOWED_TENDENCIES = frozenset({'shot_tendency_raw','drive_tendency_raw'})


def connect(path: str | Path, readonly: bool = False) -> sqlite3.Connection:
    target = Path(path).resolve()
    if readonly:
        conn = sqlite3.connect(target.as_uri() + '?mode=ro', uri=True)
    else:
        conn = sqlite3.connect(str(target))
    conn.execute('PRAGMA foreign_keys=ON')
    conn.row_factory = sqlite3.Row
    return conn


def create_database(path: str | Path, save_id: str) -> Path:
    """Create a *new* independent save database. Refuse any existing file."""
    if not isinstance(save_id,str) or not save_id or len(save_id)>128:
        raise ValueError('valid unique save_id required')
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental overwrite of a real/old database.
    with target.open('xb'):
        pass
    try:
        with connect(target) as conn:
            conn.executescript(SCHEMA.read_text(encoding='utf-8'))
            conn.execute('INSERT INTO saves(singleton,save_id,schema_version,created_at) VALUES(1,?,?,?)',
                         (save_id,1,datetime.now(timezone.utc).isoformat()))
            conn.execute('PRAGMA user_version=1')
            conn.commit()
            assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return target


def _digest(data: dict[str,Any]) -> str:
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _ensure_record(conn:sqlite3.Connection, table:str, key:str, record:dict[str,Any], match_fields:tuple[str,...]) -> None:
    current=conn.execute(f'SELECT * FROM {table} WHERE {key}=?',(record[key],)).fetchone()
    if current is None:
        cols=list(record)
        conn.execute(f"INSERT INTO {table}({','.join(cols)}) VALUES({','.join('?' for _ in cols)})",tuple(record.values()))
    elif any(current[field]!=record[field] for field in match_fields):
        raise ValueError(f'identity collision in {table}: {record[key]}')


def _check_clean_attributes(item:dict[str,Any], allow:frozenset[str]) -> None:
    fields=set(item)-{'player_id'}
    if fields-allow or any('potential' in k.lower() for k in item):
        raise PermissionError('only explicitly allowlisted GM-visible synthetic fields may be persisted')
    for key in fields:
        if item[key] is not None and (not isinstance(item[key],int) or isinstance(item[key],bool)):
            raise ValueError(f'{key} must be an integer or null; native range not yet verified')


def ingest_synthetic_capture(conn:sqlite3.Connection, payload:dict[str,Any]) -> str:
    """Atomic typed ingest; stable repeat => no-op; failed unit => no facts.

    Validates the DB save ID *before* any writes. No external game data adapter
    may call this under a Native-verified claim.
    """
    if payload.get('evidence_grade') != 'SYNTHETIC_FIXTURE':
        raise ValueError('only synthetic fixtures are authorized in this prototype')
    save_row=conn.execute('SELECT save_id FROM saves WHERE singleton=1').fetchone()
    if save_row is None or payload.get('save_id')!=save_row['save_id']:
        raise ValueError('cross-save fixture/database mismatch')
    required=('run_id','unit_id','source_key','observed_at','season')
    for key in required:
        if not payload.get(key): raise ValueError('missing '+key)
    season=payload['season']
    digest=_digest(payload)
    unit_status=payload.get('unit_status','success')
    if unit_status not in ('success','failed'):raise ValueError('invalid unit_status')
    # Avoid a failed-unit fake success by forbidden fact payloads.
    if unit_status=='failed' and any(payload.get(k) for k in ('teams','players','game','boxes','attributes','tendencies','badges','play_types','game_state')):
        raise ValueError('failed unit cannot carry accepted facts')
    with conn:
        prior=conn.execute('SELECT payload_sha256 FROM capture_units WHERE unit_id=?',(payload['unit_id'],)).fetchone()
        if prior is not None:
            if prior['payload_sha256'] != digest:raise ValueError('same unit_id with conflicting content')
            return 'already_applied'
        _ensure_record(conn,'seasons','season_id',{'season_id':season['season_id'],'season_code':season['season_code']},('season_code',))
        _ensure_record(conn,'capture_runs','run_id',{'run_id':payload['run_id'],'season_id':season['season_id'],'observed_at':payload['observed_at'],'source_grade':'SYNTHETIC_FIXTURE'},('season_id','observed_at','source_grade'))
        conn.execute('INSERT INTO capture_units(unit_id,run_id,source_key,payload_sha256,unit_status,observed_at) VALUES(?,?,?,?,?,?)',
                     (payload['unit_id'],payload['run_id'],payload['source_key'],digest,unit_status,payload['observed_at']))
        if unit_status=='failed':return 'failed_recorded'
        for team in payload.get('teams',[]):
            _ensure_record(conn,'teams','team_id',team,('display_name',))
        for player in payload.get('players',[]):
            _ensure_record(conn,'players','player_id',player,('display_name',))
        game=payload.get('game')
        if game is not None:
            item={'game_id':game['game_id'],'season_id':season['season_id'],'home_team_id':game['home_team_id'],'away_team_id':game['away_team_id'],'game_date':game.get('game_date')}
            _ensure_record(conn,'games','game_id',item,('season_id','home_team_id','away_team_id','game_date'))
        unit=payload['unit_id']
        if payload.get('game_state'):
            g=payload['game_state']
            conn.execute('INSERT INTO game_state_observations VALUES(?,?,?,?,?,?)',
                         (unit+':game',game['game_id'],unit,g['status_code'],g.get('home_points'),g.get('away_points')))
        for b in payload.get('boxes',[]):
            if not game or b['team_id'] not in (game['home_team_id'],game['away_team_id']):
                raise ValueError('box team is not a participant in the declared game')
            conn.execute('INSERT INTO player_game_boxes VALUES(?,?,?,?,?,?,?,?)',
                         (f"{unit}:box:{b['player_id']}",game['game_id'],b['player_id'],b['team_id'],unit,b.get('points'),b.get('fg_made'),b.get('fg_attempted')))
        for a in payload.get('attributes',[]):
            _check_clean_attributes(a,ALLOWED_CAPTURE_FIELDS)
            conn.execute('INSERT INTO player_attribute_snapshots VALUES(?,?,?,?,?,?)',
                         (f"{unit}:attrs:{a['player_id']}",a['player_id'],unit,a.get('overall_raw'),a.get('shot_close_raw'),a.get('driving_layup_raw')))
        for t in payload.get('tendencies',[]):
            _check_clean_attributes(t,ALLOWED_TENDENCIES)
            conn.execute('INSERT INTO player_tendency_snapshots VALUES(?,?,?,?,?)',
                         (f"{unit}:tendency:{t['player_id']}",t['player_id'],unit,t.get('shot_tendency_raw'),t.get('drive_tendency_raw')))
        for b in payload.get('badges',[]):
            conn.execute('INSERT INTO player_badge_values VALUES(?,?,?,?,?,?,?)',
                         (f"{unit}:badge:{b['player_id']}:{b['badge_key']}",b['player_id'],unit,b['badge_key'],b.get('native_code'),b.get('tier_label'),b.get('owned_state','unknown')))
        for p in payload.get('play_types',[]):
            conn.execute('INSERT INTO player_play_type_slots VALUES(?,?,?,?,?)',
                         (f"{unit}:playtype:{p['player_id']}:{p['slot_index']}",p['player_id'],unit,p['slot_index'],p.get('native_play_code')))
    return 'ingested'


def read_gm_observations(path:str|Path, player_id:str) -> list[dict[str,Any]]:
    with connect(path,readonly=True) as conn:
        rows=conn.execute('SELECT * FROM gm_player_observations WHERE player_id=? ORDER BY observed_at,unit_id',(player_id,)).fetchall()
        return [dict(x) for x in rows]


def summarize(path:str|Path) -> dict[str,Any]:
    with connect(path,readonly=True) as conn:
        save=conn.execute('SELECT save_id FROM saves WHERE singleton=1').fetchone()
        return {'save_id':save['save_id'],
                'table_count':conn.execute("SELECT count(*) AS n FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()['n'],
                'game_count':conn.execute('SELECT count(*) n FROM games').fetchone()['n'],
                'box_observations':conn.execute('SELECT count(*) n FROM player_game_boxes').fetchone()['n'],
                'attribute_observations':conn.execute('SELECT count(*) n FROM player_attribute_snapshots').fetchone()['n'],
                'capture_units':conn.execute('SELECT count(*) n FROM capture_units').fetchone()['n'],
                'foreign_key_errors':len(conn.execute('PRAGMA foreign_key_check').fetchall())}
