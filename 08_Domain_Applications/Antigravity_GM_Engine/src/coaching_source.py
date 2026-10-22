"""Snapshot-scoped coaching source; capture/audit use the caller's RO handle."""
import copy
import json
from coach_codec import load_profile,decode,validate_value
from gm_core.coaching import raw_from_team

SCHEMA='''
CREATE TABLE IF NOT EXISTS coaching_source_captures (
 snapshot_id TEXT PRIMARY KEY, save_id TEXT NOT NULL, observed_at TEXT NOT NULL,
 data_updated_at TEXT, context_json TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS coaching_team_observations (
 snapshot_id TEXT NOT NULL, team_id INTEGER NOT NULL, observation_json TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,team_id)
);
'''


def ensure_coaching_schema(conn):
    # execute one statement at a time: executescript would commit an outer capture transaction.
    for statement in SCHEMA.split(';'):
        if statement.strip():conn.execute(statement)


def validate_source(snapshot,expected_team_ids=None,profile=None):
    profile=profile or snapshot.get('capture_profile') or load_profile()
    if expected_team_ids is None:
        from config import CORE_TEAM_IDS
        expected_team_ids=CORE_TEAM_IDS
    if snapshot.get('observation_status')!='OBSERVED_LIVE_READ_ONLY':
        raise ValueError('COACHING_SOURCE_NOT_OBSERVED')
    teams=snapshot.get('teams',[])
    if len(teams)!=30 or {t['team_id'] for t in teams}!=set(expected_team_ids):
        raise ValueError('COACHING_SOURCE_REQUIRES_EXACT_30_TEAMS')
    fields=profile['gm_default_fields']
    identities=[]
    for team in teams:
        identity=team['coach_identity']
        binding=snapshot['context_identity'].get(str(team['team_id']),{})
        if (identity.get('role')!='HEAD_COACH' or identity.get('team_id')!=team['team_id']
            or binding.get('coach_identity')!=identity or binding.get('roster_signature')!=team['roster_signature']):
            raise ValueError('COACHING_SOURCE_AMBIGUOUS_COACH_OWNER')
        identities.append(identity['identity_tag'])
        raw=raw_from_team(team)
        if any(name not in team['values'] for name in fields):
            raise ValueError('COACHING_SOURCE_MISSING_DEFAULT_FIELD')
        for name in fields:
            f=profile['fields'][name]
            value=team['values'][name]
            validate_value(f,value,{p['enum_id'] for p in snapshot['playbooks']})
            if decode(raw,f)!=value:
                raise ValueError('COACHING_SOURCE_RAW_BLOCK_VALUE_MISMATCH')
        slots=profile['freelance_slot_order']
        if team.get('freelance_sets')!=[team['values'][n] for n in slots]:
            raise ValueError('COACHING_SOURCE_FREELANCE_ORDER_MISMATCH')
        opponents=[r['opponent_team_id'] for r in team['gameplans']]
        if len(opponents)!=29 or len(set(opponents))!=29 or set(opponents)!=set(expected_team_ids)-{team['team_id']}:
            raise ValueError('COACHING_SOURCE_INVALID_OPPONENT_SET')
    if len(set(identities))!=30:
        raise ValueError('COACHING_SOURCE_DUPLICATE_HEAD_COACH')
    return dict(status='OBSERVED',teams=30,default_fields_per_team=19,
        overall_defense_status=profile['opponent_overall_defense']['readiness'])


def capture_coaching_source(mem,context,expected_root=None,expected_teams=None,allow_unknown_date=False):
    if getattr(mem,'read_only',None) is not True:
        raise PermissionError('COACHING_SOURCE_REQUIRES_READ_ONLY_HANDLE')
    from coach_locator import CoachLocator,attach_process_identity
    from coaching_reader import coaching_snapshot
    if not hasattr(mem,'creation_time'):attach_process_identity(mem)
    loc=CoachLocator(mem).calibrate()
    if expected_root is not None and loc.root!=expected_root:
        raise RuntimeError('COACHING_SOURCE_DIFFERENT_ACTIVE_ROSTER')
    if expected_teams is not None and {k:v['address'] for k,v in loc.teams.items()}!={k:v['address'] for k,v in expected_teams.items()}:
        raise RuntimeError('COACHING_SOURCE_DIFFERENT_TEAM_DIRECTORY')
    snapshot=coaching_snapshot(loc,context,allow_unknown_date=allow_unknown_date)
    snapshot['capture_profile']=copy.deepcopy(loc.profile)
    validate_source(snapshot)
    return snapshot


def store_coaching_source(conn,snapshot_id,save_id,snapshot):
    validate_source(snapshot)
    if snapshot['career_id']!=save_id or snapshot['source_batch_id']!=snapshot_id:
        raise ValueError('COACHING_SOURCE_WRONG_CAPTURE_BINDING')
    ensure_coaching_schema(conn)
    payload=copy.deepcopy(snapshot)
    payload.pop('process_pid',None)
    payload.pop('process_creation_time',None)
    teams=payload.pop('teams')
    context={k:payload[k] for k in ('career_id','source_batch_id','game_season','game_date','policy_id')}
    conn.execute('DELETE FROM coaching_team_observations WHERE snapshot_id=?',(snapshot_id,))
    conn.execute('DELETE FROM coaching_source_captures WHERE snapshot_id=?',(snapshot_id,))
    conn.execute('INSERT INTO coaching_source_captures VALUES (?,?,?,?,?,?)',
        (snapshot_id,save_id,snapshot['observed_at'],None,json.dumps(context,sort_keys=True),json.dumps(payload,sort_keys=True)))
    for team in teams:
        # Native per-player matchup arrays are not the overall-defense business source.
        for gp in team['gameplans']:
            gp.pop('defensive_matchups',None)
            gp.pop('rotations',None)
        conn.execute('INSERT INTO coaching_team_observations VALUES (?,?,?)',
            (snapshot_id,team['team_id'],json.dumps(team,sort_keys=True)))


def load_coaching_source(conn,snapshot_id,save_id=None,data_updated_at=None):
    exists=conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='coaching_source_captures'").fetchone()
    if not exists:return None
    row=conn.execute('SELECT save_id,data_updated_at,metadata_json FROM coaching_source_captures WHERE snapshot_id=?',(snapshot_id,)).fetchone()
    if not row:return None
    if (save_id is not None and row[0]!=save_id) or (data_updated_at is not None and row[1]!=data_updated_at):
        raise ValueError('COACHING_SOURCE_WRONG_SAVE_OR_UPDATE_TIME')
    payload=json.loads(row[2])
    payload['teams']=[json.loads(r[0]) for r in conn.execute(
        'SELECT observation_json FROM coaching_team_observations WHERE snapshot_id=? ORDER BY team_id',(snapshot_id,))]
    validate_source(payload)
    return payload


def audit_coaching_source(conn,mem,snapshot_id):
    stored=load_coaching_source(conn,snapshot_id)
    if stored is None:raise RuntimeError('COACHING_SOURCE_CAPTURE_FAILED_MISSING')
    context={k:stored[k] for k in ('career_id','source_batch_id','game_season','game_date','policy_id')}
    live=capture_coaching_source(mem,context,allow_unknown_date=stored['game_date'] is None)
    if any(live[k]!=stored[k] for k in ('process_binding','context_identity','native_evidence','playbooks')):
        raise RuntimeError('COACHING_SOURCE_IDENTITY_CHANGED_DURING_AUDIT')
    for team in stored['teams']:
        current=next(t for t in live['teams'] if t['team_id']==team['team_id'])
        if current['values']!=team['values'] or current['blocks']!=team['blocks']:
            raise RuntimeError('COACHING_SOURCE_DEFAULT_VALUES_CHANGED_DURING_AUDIT')
        for record in team['gameplans']:
            now=next(g for g in current['gameplans'] if g['opponent_team_id']==record['opponent_team_id'])
            if record.get('overall_defense')!=now.get('overall_defense'):
                raise RuntimeError('COACHING_SOURCE_OVERALL_CHANGED_DURING_AUDIT')
    return {'coaching_30_teams_identity_defaults_and_verified_overall_match_live':True}


def coaching_public_files(source,batch_id,data_updated_at,profile=None):
    profile=profile or source.get('capture_profile') or load_profile()
    validate_source(source,profile=profile)
    payload=copy.deepcopy(source)
    payload.pop('capture_profile',None)
    payload['source_capture_id']=payload['source_batch_id']
    payload['source_batch_id']=batch_id
    payload['data_updated_at']=data_updated_at
    opponents={}
    owners={}
    for team in payload['teams']:
        opponents[team['abbreviation']]=team.pop('gameplans')
        owners[team['abbreviation']]=team['team_id']
        team['sim_read_only']={n:dict(raw=v,gm_control='GM_CONTROL_DISABLED') for n,v in team['values'].items() if n.startswith('Sim')}
        team['values']={n:team['values'][n] for n in profile['gm_default_fields']}
        team['readiness']={n:team['readiness'][n] for n in profile['gm_default_fields']}
        team['opponent_file']='coaching/opponents/'+team['abbreviation']+'.json'
    dictionary=dict(codec_version=profile['codec_version'],default_fields={n:profile['fields'][n] for n in profile['gm_default_fields']},
        freelance_slot_order=profile['freelance_slot_order'],playbooks=payload['playbooks'],
        overall_defense=profile['opponent_overall_defense'],defensive_fields=payload['defensive_field_catalog'],
        sim_control='GM_CONTROL_DISABLED',legacy_team_poe='LEGACY_UNVERIFIED')
    files={'coaching/teams.json':payload,'coaching/field_dictionary.json':dictionary,
        'coaching/opponents/index.json':{'teams':{name:'coaching/opponents/'+name+'.json' for name in opponents}}}
    for name,records in opponents.items():
        # Publish only the approved overall-defense scope, not opponent offense or player matchups.
        files['coaching/opponents/'+name+'.json']=dict(source_batch_id=batch_id,career_id=source['career_id'],team_id=owners[name],
            game_date=source['game_date'],data_updated_at=data_updated_at,records=[dict(opponent_team_id=r['opponent_team_id'],
                is_in_use_raw=r['is_in_use'],overall_defense=r.get('overall_defense'),
                readiness=profile['opponent_overall_defense']['readiness']) for r in records])
    return files
