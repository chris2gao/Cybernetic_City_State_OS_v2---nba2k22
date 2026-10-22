"""Same-session observation projection into facts, M0 snapshots and reconciliation."""
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import save_context
from .common import binding, canonical
from .registry import Registry
from .workspace import Workspaces

SCHEMA = '''
CREATE TABLE IF NOT EXISTS state_io_captures(
 snapshot_id TEXT PRIMARY KEY,save_id TEXT NOT NULL,save_instance_id TEXT,generation_id TEXT,
 registry_version TEXT NOT NULL,observed_at TEXT NOT NULL,metadata_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS state_io_objects(
 snapshot_id TEXT NOT NULL,object_key TEXT NOT NULL,object_json TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,object_key));
CREATE TABLE IF NOT EXISTS observed_setting_values(
 snapshot_id TEXT NOT NULL,object_key TEXT NOT NULL,domain TEXT NOT NULL,target_kind TEXT NOT NULL,
 team_id INTEGER,opponent_team_id INTEGER,player_identity TEXT,side TEXT,slot_index INTEGER,
 field_key TEXT NOT NULL,value_json TEXT,raw_hex TEXT,source_status TEXT NOT NULL,registry_version TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,object_key,field_key));
CREATE INDEX IF NOT EXISTS state_io_values_domain ON observed_setting_values(snapshot_id,domain,team_id,player_identity,field_key);
'''


def ensure_schema(c):
    for statement in SCHEMA.split(';'):
        if statement.strip():
            c.execute(statement)


def capture(mem, coaching, registry=None, *, session=None, object_provider=None):
    from .adapters import NativeSession, capture_objects
    reg = registry or Registry()
    session = session or NativeSession(True,reg,memory=mem)
    if getattr(mem,'read_only',None) is not True:
        raise PermissionError('CAPTURE_REQUIRES_EXISTING_READ_ONLY_SESSION')
    session.verify_context(dict(process_binding=coaching['process_binding'],source_context=coaching))
    objects,coverage = (object_provider or capture_objects)(session,coaching)
    session.verify_context(dict(process_binding=coaching['process_binding'],source_context=coaching))
    manager = Workspaces()
    save_id = coaching['career_id']
    w = manager.active(save_id) if manager.path(save_id).exists() else dict(save_id=save_id,save_instance_id=None,generation_id=None)
    context_keys = ('process_binding','context_identity','native_evidence','playbooks')
    source_context = {k:coaching[k] for k in context_keys}
    return dict(**binding(w),source_batch_id=coaching['source_batch_id'],source_snapshot_id=coaching['source_batch_id'],
                registry_version=reg.version,observed_at=coaching['observed_at'],process_binding=coaching['process_binding'],
                source_context=source_context,loaded_playbooks=[p['enum_id'] for p in coaching['playbooks'] if p.get('name')],
                team_directory={str(tid):{k:t.get(k) for k in ('name','city','abbreviation')}
                                for tid,t in session.loc.teams.items()},
                loaded_play_crcs=sorted({crc for p in coaching['playbooks'] for crc in p.get('play_crc_slots',[])}),
                objects=objects,coverage=coverage,observation_status='OBSERVED_SAME_SESSION',
                native_dictionary=reg.fields)


def store(c, source):
    ensure_schema(c)
    sid = source['source_snapshot_id']
    c.execute('DELETE FROM observed_setting_values WHERE snapshot_id=?',(sid,))
    c.execute('DELETE FROM state_io_objects WHERE snapshot_id=?',(sid,))
    c.execute('DELETE FROM state_io_captures WHERE snapshot_id=?',(sid,))
    meta = {k:v for k,v in source.items() if k!='objects'}
    c.execute('INSERT INTO state_io_captures VALUES (?,?,?,?,?,?,?)',
              (sid,source['save_id'],source['save_instance_id'],source['generation_id'],source['registry_version'],
               source['observed_at'],canonical(meta)))
    values=[]
    for obj in source['objects']:
        c.execute('INSERT INTO state_io_objects VALUES (?,?,?)',(sid,obj['object_key'],canonical(obj)))
        s = obj['selector']
        for key in obj['field_keys']:
            field = source['native_dictionary'][key]
            raw = obj.get('raw')
            if raw:
                layout=field['layout']
                raw=bytes.fromhex(raw)[layout['offset']:layout['offset']+layout['storage_bytes']].hex()
            values.append((sid,obj['object_key'],field['domain'],s['target_kind'],s.get('team_id'),s.get('opponent_team_id'),
                           s.get('player_identity') or s.get('opponent_player_identity'),s.get('side'),s.get('slot_index'),key,
                           canonical(obj['values'].get(key)),raw,obj['source_status'],source['registry_version']))
    c.executemany('INSERT INTO observed_setting_values VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',values)
    return dict(status='OBSERVED_SAME_INGESTION_RO_SESSION',objects=len(source['objects']),fields=len(values),coverage=source['coverage'])


def load_from_connection(c, snapshot_id, batch_id=None):
    exists = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='state_io_captures'").fetchone()
    if not exists:
        raise ValueError('STATE_IO_NOT_OBSERVED_IN_THIS_BATCH')
    row = c.execute('SELECT metadata_json FROM state_io_captures WHERE snapshot_id=?',(snapshot_id,)).fetchone()
    if not row:
        raise ValueError('STATE_IO_NOT_OBSERVED_IN_THIS_BATCH')
    source=json.loads(row[0])
    source['objects']=[json.loads(r[0]) for r in c.execute('SELECT object_json FROM state_io_objects WHERE snapshot_id=? ORDER BY object_key',(snapshot_id,))]
    if batch_id:
        source['source_batch_id']=batch_id
    return source


def load_audited_source(career, batch, query_root=None, published_root=None):
    """Reuse M0 validation, never open active saves as GM source authority."""
    from gm_data_access.query import QuerySession
    root=Path(save_context.PROJECT_DIR)
    session=QuerySession(query_root or root/'database/query_snapshots',published_root or root/'published',career,batch)
    try:
        session.require_gm_sanitized()
        c=sqlite3.connect((session.directory/'league_state.sqlite').as_uri()+'?mode=ro',uri=True)
        try:
            source=load_from_connection(c,session.binding['snapshot_id'],session.batch)
        finally:
            c.close()
        if source['save_id'] != career:
            raise ValueError('CROSS_SAVE_SNAPSHOT')
        return source
    finally:
        session.close()


def mark_captured(save_id, snapshot_id):
    manager=Workspaces()
    if not manager.path(save_id).exists():
        return
    w=manager.active(save_id)
    paths=save_context.save_paths(save_id)
    with closing(sqlite3.connect(paths['db_path'])) as c:
        source=load_from_connection(c,snapshot_id)
    if binding(source) != binding(w):
        raise ValueError('CAPTURE_GENERATION_MISMATCH')
    manager.write(dict(w,lifecycle_status='CAPTURED',last_snapshot_id=snapshot_id))


def audit(c, mem, snapshot_id):
    """Reuse the existing source audit session; compare native fields and identity."""
    from .adapters import NativeSession
    from .codec import decode
    source=load_from_connection(c,snapshot_id)
    reg=Registry()
    if source['registry_version']!=reg.version:
        raise ValueError('STATE_IO_AUDIT_REGISTRY_CHANGED')
    session=NativeSession(True,reg,memory=mem)
    session.verify_context(source)
    for obj in source['objects']:
        for target in obj.get('members') or [obj]:
            at=session.resolve(target)
            raw=session.read(at,len(bytes.fromhex(target['raw'])))
            for key in obj['field_keys']:
                if decode(raw,reg.field(key))!=decode(bytes.fromhex(target['raw']),reg.field(key)):
                    raise ValueError('STATE_IO_SOURCE_CHANGED_DURING_AUDIT:'+key)
    session.verify_context(source)
    return {'state_io_registered_fields_and_identities_match_same_session':True}
