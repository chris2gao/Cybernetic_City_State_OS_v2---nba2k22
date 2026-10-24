"""Per-save typed world facts: atomic append-only ingestion, no game writes."""
from __future__ import annotations
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from schema_model import TABLES, VERSION, LEGACY_TABLES, dictionary, ident

SCHEMA=Path(__file__).with_name('schema.sql')
ALLOWED_CAPTURE_FIELDS=frozenset(c.name for c in TABLES['player_attribute_snapshots'].columns if c.name not in ('snapshot_id','player_id','unit_id'))
ALLOWED_TENDENCIES=frozenset(c.name for c in TABLES['player_tendency_snapshots'].columns if c.name not in ('snapshot_id','player_id','unit_id'))
RESERVED={'saves','seasons','capture_runs','capture_units','source_artifacts'}
BLOCKED_INPUT={'player_restricted_observations'}


class ManagedConnection(sqlite3.Connection):
    def __enter__(self):
        self._context_depth=getattr(self,'_context_depth',0)+1
        return super().__enter__()

    def __exit__(self,kind,value,traceback):
        try:return super().__exit__(kind,value,traceback)
        finally:
            self._context_depth-=1
            if self._context_depth==0:self.close()


def connect(path,readonly=False):
    target=Path(path).resolve()
    conn=sqlite3.connect(target.as_uri()+('?mode=ro' if readonly else '?mode=rw'),uri=True,factory=ManagedConnection)
    conn.execute('PRAGMA foreign_keys=ON');conn.row_factory=sqlite3.Row
    return conn


def _digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def _utc(value):
    return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc).isoformat(timespec='microseconds')


def _insert(conn,table,record):
    allowed={c.name:c for c in TABLES[table].columns}
    if set(record)-allowed.keys():raise PermissionError('unknown/unapproved columns for '+table+': '+','.join(sorted(set(record)-allowed.keys())))
    for k,v in record.items():
        if v is None:continue
        kind=allowed[k].kind
        if kind=='INTEGER' and (not isinstance(v,int) or isinstance(v,bool)):raise ValueError(table+'.'+k+' must be integer or null')
        if kind=='TEXT' and not isinstance(v,str):raise ValueError(table+'.'+k+' must be text or null')
        if kind=='REAL' and (not isinstance(v,(int,float)) or isinstance(v,bool)):raise ValueError(table+'.'+k+' must be numeric or null')
    cols=list(record)
    conn.execute(f'INSERT INTO {ident(table)} ({",".join(map(ident,cols))}) VALUES ({",".join("?" for _ in cols)})',tuple(record.values()))


def _ensure_record(conn,table,key,record,match_fields=None):
    current=conn.execute(f'SELECT * FROM {ident(table)} WHERE {ident(key)}=?',(record[key],)).fetchone()
    if current is None:_insert(conn,table,record)
    elif any(current[k]!=record[k] for k in (match_fields or record.keys())):raise ValueError('identity collision in '+table+': '+str(record[key]))


def _seed_registry(conn,only_missing=False):
    for t in dictionary()['tables']:
        for c in t['columns']:
            key=t['name']+'.'+c['name']
            if only_missing and conn.execute('SELECT 1 FROM native_fields WHERE field_id=?',(key,)).fetchone():continue
            _insert(conn,'native_fields',{'field_id':key,'source_group':t['domain'],'native_key':c['name'],
                'table_name':t['name'],'column_name':c['name'],'source_ref':c['source'],
                'evidence_grade':'RESEARCH_LEAD' if any(x in c['source'].lower() for x in ('registr','research')) else 'UNKNOWN',
                'visibility':c['visibility'],'unit':c['unit'],'legal_range_state':c['legal_game_range']})


def create_database(path,save_id,*,_migration_header=None,_seed_catalog=True):
    if not isinstance(save_id,str) or not save_id.strip() or len(save_id)>128:raise ValueError('valid unique save_id required')
    target=Path(path).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb'):pass
    try:
        with closing(connect(target)) as conn:
            conn.executescript('BEGIN IMMEDIATE;\n'+SCHEMA.read_text(encoding='utf-8'))
            header={'singleton':1,'save_id':save_id,'schema_version':VERSION,'created_at':datetime.now(timezone.utc).isoformat(),'source_grade':'UNBOUND'}
            if _migration_header:
                header.update({k:v for k,v in _migration_header.items() if k in ('created_at','source_grade','game_build','native_save_fingerprint')})
            _insert(conn,'saves',header)
            if _seed_catalog:_seed_registry(conn)
            conn.execute('PRAGMA user_version=3');conn.commit()
            if conn.execute('PRAGMA foreign_key_check').fetchall():raise RuntimeError('schema FK failure')
    except BaseException:
        target.unlink(missing_ok=True);raise
    return target


def _check_envelope(conn,payload,live_receipt=None):
    if conn.in_transaction:raise ValueError('ingest requires a clean connection transaction boundary')
    save=conn.execute('SELECT save_id,schema_version FROM saves WHERE singleton=1').fetchone()
    if not save or payload.get('save_id')!=save['save_id']:raise ValueError('cross-save capture/database mismatch')
    if save['schema_version']!=VERSION:raise ValueError('explicit copy migration to current schema required')
    for k in ('run_id','unit_id','source_key','observed_at','season'):
        if not payload.get(k):raise ValueError('missing '+k)
    stamp=datetime.fromisoformat(payload['observed_at'].replace('Z','+00:00'))
    if stamp.utcoffset() is None:raise ValueError('observation requires timezone')
    grade=payload.get('evidence_grade')
    if grade=='LIVE_READ':
        from live_world import _AcquisitionReceipt
        if type(live_receipt) is not _AcquisitionReceipt or not live_receipt.matches(payload):
            raise ValueError('live provenance requires acquisition adapter, no assertion-only promotion')
    elif grade not in ('SYNTHETIC_FIXTURE','RESEARCH_FIXTURE'):raise ValueError('unrecognized evidence grade')
    artifacts=payload.get('artifacts',[])
    if grade=='RESEARCH_FIXTURE' and (not artifacts or not payload.get('decoder_version')):raise ValueError('research capture needs hashed artifacts and decoder version')
    for a in artifacts:
        if len(a.get('sha256',''))!=64 or any(x not in '0123456789abcdef' for x in a['sha256']):raise ValueError('invalid artifact hash')
    facts=payload.get('facts',{})
    if set(facts)-TABLES.keys() or set(facts)&(RESERVED|BLOCKED_INPUT):raise PermissionError('reserved/restricted capture table')
    for t,rows in facts.items():
        if not isinstance(rows,list):raise ValueError('facts must be lists of typed records')
        for row in rows:
            if any('potential' in k.lower() or 'raw_struct' in k.lower() for k in row):raise PermissionError('restricted raw field')
            if 'unit_id' in row and row['unit_id']!=payload['unit_id']:raise ValueError('cross-unit fact reference')
            if 'save_id' in row and row['save_id']!=payload['save_id']:raise ValueError('cross-save fact reference')
    status=payload.get('unit_status','success')
    if status not in ('success','failed'):raise ValueError('invalid unit_status')
    if status=='failed' and any(facts.values()):raise ValueError('failed unit cannot carry accepted facts')
    for t,required in payload.get('required_fields',{}).items():
        if t not in facts or not facts[t]:raise ValueError('missing required source family '+t)
        for row in facts[t]:
            if any(row.get(k) is None for k in required):raise ValueError('incomplete source family '+t)


def ingest_capture(conn,payload,*,_live_receipt=None):
    """One typed consistency unit, all-or-nothing. Fixture is not live evidence."""
    _check_envelope(conn,payload,_live_receipt);digest=_digest(payload)
    prior=conn.execute('SELECT payload_sha256 FROM capture_units WHERE unit_id=?',(payload['unit_id'],)).fetchone()
    if prior:
        if prior['payload_sha256']!=digest:raise ValueError('same unit_id with conflicting content')
        return 'already_applied'
    unit=payload['unit_id'];season=payload['season']
    with conn:
        conn.execute('PRAGMA defer_foreign_keys=ON')
        _ensure_record(conn,'seasons','season_id',{'season_id':season['season_id'],'season_code':season['season_code']})
        _ensure_record(conn,'capture_runs','run_id',{'run_id':payload['run_id'],'season_id':season['season_id'],
            'observed_at':_utc(payload['observed_at']),'source_grade':payload['evidence_grade'],
            'decoder_version':payload.get('decoder_version'),'save_binding_ref':payload.get('save_binding_ref')})
        status=payload.get('unit_status','success')
        _insert(conn,'capture_units',{'unit_id':unit,'run_id':payload['run_id'],'source_key':payload['source_key'],
            'payload_sha256':digest,'unit_status':status,'observed_at':_utc(payload['observed_at']),'effective_at':payload.get('effective_at'),
            'layout_version':payload.get('decoder_version'),'completeness':'FAILED' if status=='failed' else payload.get('completeness','PARTIAL')})
        for n,a in enumerate(payload.get('artifacts',[])):
            record={'artifact_id':f'{unit}:artifact:{n}','unit_id':unit,'restricted':1,**a}
            if record['unit_id']!=unit:raise ValueError('artifact scope mismatch')
            _insert(conn,'source_artifacts',record)
        for name in TABLES:
            if name not in payload.get('facts',{}):continue
            spec=TABLES[name]
            for n,original in enumerate(payload['facts'][name]):
                item=dict(original);cols={c.name for c in spec.columns}
                if 'unit_id' in cols:item.setdefault('unit_id',unit)
                if 'save_id' in cols:item.setdefault('save_id',payload['save_id'])
                item.setdefault(spec.key,f'{unit}:{name}:{n}')
                if not spec.observation or name=='native_fields':_ensure_record(conn,name,spec.key,item)
                else:_insert(conn,name,item)
    return 'failed_recorded' if status=='failed' else 'ingested'


def ingest_synthetic_capture(conn,payload):
    """Translate original 16-table synthetic API without promoting its evidence."""
    if payload.get('evidence_grade')!='SYNTHETIC_FIXTURE':raise ValueError('synthetic API cannot promote Native claims')
    facts={}
    aliases=[('teams','teams'),('players','players'),('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots'),('badges','player_badge_values'),('play_types','player_play_type_slots')]
    for old,new in aliases:facts[new]=payload.get(old,[])
    game=payload.get('game')
    if game:
        if any(b['team_id'] not in (game['home_team_id'],game['away_team_id']) for b in payload.get('boxes',[])):
            raise ValueError('box team is not a game participant')
        facts['games']=[dict(game,season_id=payload['season']['season_id'])]
        facts['player_game_boxes']=[dict(b,game_id=game['game_id']) for b in payload.get('boxes',[])]
        if payload.get('game_state'):facts['game_state_observations']=[dict(payload['game_state'],game_id=game['game_id'])]
    translated={k:v for k,v in payload.items() if k not in {'teams','players','attributes','tendencies','badges','play_types','game','boxes','game_state'}}
    translated['facts']=facts
    return ingest_capture(conn,translated)


def ingest_or_quarantine(conn,payload):
    """Keep proposed conflicting historical facts out of accepted fact tables.

    The quarantine stores digests, not restricted proposed bytes. Human decisions
    arrive as new immutable records, never an UPDATE of old game history.
    """
    try:return ingest_capture(conn,payload)
    except sqlite3.IntegrityError as exc:
        if not ('frozen game conflict' in str(exc) or 'already finalized' in str(exc)):raise
        digest=_digest(payload)
        quarantine=dict(payload)
        quarantine['unit_id']='quarantine:'+payload['unit_id']
        quarantine['source_key']='quarantine:'+payload['source_key']
        quarantine['required_fields']={}
        quarantine['facts']={'fact_conflicts':[{'object_ref':payload['unit_id'],
            'evidence_a':'Existing immutable game/season history; '+str(exc),
            'evidence_b':'PROPOSED_PAYLOAD_SHA256:'+digest,'review_status':'PENDING_HUMAN'}]}
        ingest_capture(conn,quarantine)
        return 'quarantined_pending_human'


def read_gm_observations(path,player_id):
    with closing(connect(path,True)) as c:return [dict(r) for r in c.execute('SELECT * FROM gm_player_observations WHERE player_id=? ORDER BY observed_at,unit_id',(player_id,))]


def summarize(path):
    with closing(connect(path,True)) as c:
        names={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if names-TABLES.keys():raise ValueError('unknown database tables; not a recognized world fact schema')
        counts={t:c.execute(f'SELECT count(*) FROM {ident(t)}').fetchone()[0] for t in names}
        grades={r[0]:r[1] for r in c.execute('SELECT source_grade,count(*) FROM capture_runs GROUP BY source_grade')}
        header=c.execute('SELECT save_id,schema_version FROM saves').fetchone()
        return {'save_id':header['save_id'],'schema_version':header['schema_version'],
            'table_count':len(names),'column_count':sum(len(c.execute(f'PRAGMA table_info({ident(t)})').fetchall()) for t in names),
            'game_count':counts['games'],'box_observations':counts['player_game_boxes'],
            'attribute_observations':counts['player_attribute_snapshots'],'capture_units':counts['capture_units'],
            'foreign_key_errors':len(c.execute('PRAGMA foreign_key_check').fetchall()),'source_grades':grades,
            'nonempty_fact_tables':[t for t,n in counts.items() if n and t not in RESERVED|{'native_fields'}]}


def migrate_database(source,new_path):
    """Copy-upgrade v1/v2 to a NEW fact file, preserving all existing tables/rows."""
    src=Path(source).resolve();dst=Path(new_path).resolve()
    with closing(connect(src,True)) as old:
        if old.execute('PRAGMA user_version').fetchone()[0] not in (1,2):raise ValueError('source must be v1 or v2')
        if old.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('source integrity failure')
        names={r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if names-TABLES.keys():raise ValueError('migration cannot silently discard unknown source tables')
        save=dict(old.execute('SELECT * FROM saves').fetchone());create_database(dst,save['save_id'],_migration_header=save,_seed_catalog=False)
        try:
            with closing(connect(dst)) as new:
                with new:
                    new.execute('PRAGMA defer_foreign_keys=ON')
                    for name in TABLES:
                        if name not in names or name=='saves':continue
                        for row in old.execute(f'SELECT * FROM {ident(name)}'):_insert(new,name,dict(row))
                    for name in names-{'saves'}:
                        if old.execute(f'SELECT count(*) FROM {ident(name)}').fetchone()[0]!=new.execute(f'SELECT count(*) FROM {ident(name)}').fetchone()[0]:raise RuntimeError('migration count mismatch '+name)
                    _seed_registry(new,only_missing=True)
                    if new.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('migration foreign key failure')
        except BaseException:
            dst.unlink(missing_ok=True);raise
    return dst


def migrate_v1(source,new_path):
    with closing(connect(source,True)) as old:
        if old.execute('PRAGMA user_version').fetchone()[0]!=1:raise ValueError('source must be v1')
    return migrate_database(source,new_path)
