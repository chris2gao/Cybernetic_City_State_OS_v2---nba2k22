"""Verify every native state projection, appearance binding, typed row and page."""
from bisect import bisect_right
from collections import Counter
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from live_world import _json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import reconstruct_projection
from player_state_reader import state_payload,state_projection_ranges
from player_state_codec import decode_player_state
from query import native_player_state,player_card,player_badges,export_jsonl
from schema_model import TABLES,ident
runtime=RUN/'_runtime';capture=runtime/'player-state-live-v14';dest=RUN/'06_执行/increment15';dest.mkdir(parents=True,exist_ok=True)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((capture/'player-state-manifest.json').read_bytes());report=json.loads((capture/'player-state-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert sha(capture/name)==digest,name
for name,digest in report['code_sha256'].items():assert sha(APP/name)==digest,name
trace=report['read_trace'];assert all(e['success'] for e in trace) and trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(e['address'],16),e['returned_bytes'],e['sha256']) for e in trace if e['operation']=='ReadProcessMemory'}
def prove(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
pd=m['descriptors']['1'];stride=m['projection_stride'];ranges=[tuple(r) for r in m['projection_ranges']];assert ranges==state_projection_ranges()
raw=(capture/'player-state-public-projections.bin').read_bytes();appearance=(capture/'appearance-public-projections.bin').read_bytes()
assert len(raw)==pd['count']*stride and len(appearance)==pd['count']*4
forbidden=sorted((pd['address']+i*1264+low,pd['address']+i*1264+high) for i in range(pd['count']) for low,high in RESTRICTED_PLAYER_RANGES);starts=[low for low,high in forbidden]
for e in trace:
    if e['operation']!='ReadProcessMemory':continue
    start=int(e['address'],16);end=start+e['requested_bytes'];j=bisect_right(starts,end-1)-1
    assert j<0 or forbidden[j][1]<=start,('private-overlap',e['label'])
assert not any(low<1251 and 1211<high for low,high in ranges),'state collector unexpectedly acquires base badges'
for i,state in enumerate(m['state_rows']):
    packed=raw[i*stride:(i+1)*stride];at=0
    for low,high in ranges:prove(pd['address']+i*1264+low,packed[at:at+high-low]);at+=high-low
    player=reconstruct_projection(packed,ranges);pointer=int.from_bytes(player[144:152],'little');status=state['vitals']['appearance_status'];part=None
    assert pointer==m['appearance_pointer_values_owner_only'][i]
    if status=='NATIVE_APPEARANCE_PUBLIC_FIELDS_OBSERVED':
        part=appearance[i*4:(i+1)*4];prove(pointer,part)
        assert not(pd['address']<pointer+4 and pointer<pd['address']+pd['count']*1264)
    assert state=={'source_player_index':i,**decode_player_state(player,part,appearance_status=status)}
    for low,high in RESTRICTED_PLAYER_RANGES:assert player[low:high]==bytes(high-low)
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);compared=0
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall()
    canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
    payload=state_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1],canonical)
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual and all(actual[k]==value for k,value in expected.items()),(table,key);compared+=1
    matched=c.execute('SELECT count(*) FROM native_player_sources WHERE unit_id=? AND player_id IS NOT NULL',(unit,)).fetchone()[0]
    assert c.execute('SELECT count(*) FROM player_health_observations WHERE unit_id=? AND (availability IS NOT NULL OR energy_raw IS NOT NULL OR recovery_days IS NOT NULL OR severity IS NOT NULL)',(unit,)).fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM player_morale_observations WHERE unit_id=? AND (morale_raw IS NOT NULL OR role_code IS NOT NULL OR role_satisfaction_raw IS NOT NULL)',(unit,)).fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM player_vitals_observations WHERE unit_id=? AND (age_raw IS NOT NULL OR birth_date IS NOT NULL OR country IS NOT NULL OR college IS NOT NULL)',(unit,)).fetchone()[0]==0
    injury_status=[dict(r) for r in c.execute('SELECT injury1_status_label,injury2_status_label,count(*) AS rows FROM player_health_observations WHERE unit_id=? GROUP BY injury1_status_label,injury2_status_label',(unit,))]
_json(queries/'native-curry-state.json',native_player_state(db,subject_name='Stephen Curry',unit_id=unit))
card=player_card(db,'player:native:1612');_json(queries/'curry-current-card.json',card)
with connect(save/'world-v13.sqlite',True) as old:
    for column,latest in card['families']['player_attribute_snapshots'].items():
        before=old.execute(f'''SELECT a.{ident(column)} AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade
            FROM player_attribute_snapshots a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE a.player_id=? AND a.{ident(column)} IS NOT NULL ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',('player:native:1612',)).fetchone()
        if before:assert all(latest[key]==value for key,value in dict(before).items()),column
        else:assert latest['value'] is None,column
assert player_badges(db,'player:native:1612')==player_badges(save/'world-v13.sqlite','player:native:1612')
seen=set();after=-1;pages=0
while True:
    page=native_player_state(db,unit_id=unit,after_index=after,limit=100);pages+=1
    for row in page['records']:
        assert row['source_player_index'] not in seen and all(row[g] is not None for g in ('vitals','health','morale'));seen.add(row['source_player_index'])
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(range(pd['count']))
for path in queries.glob('*.json'):
    public=path.read_text(encoding='utf-8').lower();assert not any(s in public for s in ('potential','payload_ref','"address"','appearance_pointer_values','protected_value_ref'))
exports={}
for table in ('player_vitals_observations','player_health_observations','player_morale_observations'):
    path=runtime/('increment15-'+table+'.jsonl');exports[table]=export_jsonl(db,path,table,limit=100000)['rows']
    with path.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as target:shutil.copyfileobj(src,target)
archives={}
for name,directory in (('player-state-live-v14',capture),('player-state-metadata-01',runtime/'player-state-metadata-01')):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive)}
archive=sources/'state-metadata-research.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('inspect_player_state_metadata.py','player-state-metadata-inspection.json','read_player_state_metadata.py','start_player_state_metadata.ps1','summarize_player_state_metadata.py','player-state-literal-labels.json','build_player_state_profile.py'):
        tar.add(runtime/name,arcname=name,recursive=False)
archives['metadata_research']={'archive':archive.name,'sha256':sha(archive)}
for name in ('migrate_player_state_v14.py','capture_player_state_v14.py','start_player_state_v14.ps1','curate_player_state_fixture.py'):shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(runtime/'player-state-migration-v14/migration-report.json',dest/'migration-report.json');_json(sources/'source_manifest.json',archives);_json(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v14.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes());assert sha(save/'world-v13.sqlite')==migration['old_database_sha256']
summary={'status':'NATIVE_PLAYER_VITALS_HEALTH_MORALE_BYTES_TO_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE',
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),'schema':summarize(db),
    'source_pid':report['pid'],'unit_id':unit,'latest_counts':result['counts'],'source_to_typed_rows_compared':compared,'public_player_projections_redecoded':pd['count'],
    'matched_current_roster_canonical_players':matched,'appearance_status_counts':m['appearance_status_counts'],'injury_status_source_counts':injury_status,
    'old_rows_preserved':migration['preserved_rows'],'old_v13_file_hash_unchanged':True,'known_restricted_player_bytes_requested':0,
    'old_attributes_and_base_badges_unchanged':True,'pinned_state_pages':pages,'export_rows':exports,
    'world_sqlite_sha256':sha(db),'world_sqlite_bytes':db.stat().st_size,'compressed_world_bytes':(dest/'world-v14.sqlite.gz').stat().st_size,
    'game_writes':False,'full_goal_complete':False,'independent_review':False,
    'limits':['Named native appearance units support explicit derived cm, not UI acceptance.','Weight/morale UI scale, calendar/birth month and additional vitals remain incomplete.','Two injury slots do not establish aggregate availability, energy or remaining recovery days.','OrgRole is not playing-time role/satisfaction; source lifecycle, remaining domains, capacity/recovery and final acceptance remain open.']}
_json(dest/'player_state_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_player_state_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','source_to_typed_rows_compared','matched_current_roster_canonical_players','old_rows_preserved','appearance_status_counts','compressed_world_bytes')}))
