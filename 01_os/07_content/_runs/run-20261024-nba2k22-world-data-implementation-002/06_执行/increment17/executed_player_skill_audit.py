"""Compare every actual public skill projection to typed storage and full pages."""
from bisect import bisect_right
from collections import Counter
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from live_world import _json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import reconstruct_projection
from player_skill_reader import skill_payload,skill_projection_ranges
from player_skill_codec import PROFILE,decode_skills
from query import native_player_skills,native_player_state,native_affiliations,player_card,player_badges,export_jsonl
from schema_model import TABLES,ident
runtime=RUN/'_runtime';capture=runtime/'player-skill-live-v16';dest=RUN/'06_执行/increment17';dest.mkdir(parents=True,exist_ok=True);sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((capture/'skill-manifest.json').read_bytes());report=json.loads((capture/'skill-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert sha(capture/name)==digest,name
for name,digest in report['code_sha256'].items():assert sha(APP/name)==digest,name
trace=report['read_trace'];assert all(e['success'] for e in trace) and trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(e['address'],16),e['returned_bytes'],e['sha256']) for e in trace if e['operation']=='ReadProcessMemory'}
def prove(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
pd=m['descriptors']['1'];stride=m['projection_stride'];ranges=[tuple(r) for r in m['projection_ranges']];assert ranges==skill_projection_ranges();raw=(capture/'player-skill-public-projections.bin').read_bytes();assert len(raw)==pd['count']*stride
forbidden=sorted((pd['address']+i*1264+low,pd['address']+i*1264+high) for i in range(pd['count']) for low,high in RESTRICTED_PLAYER_RANGES);starts=[low for low,high in forbidden]
for e in trace:
    if e['operation']!='ReadProcessMemory':continue
    start=int(e['address'],16);end=start+e['requested_bytes'];j=bisect_right(starts,end-1)-1;assert j<0 or forbidden[j][1]<=start,('private-overlap',e['label'])
assert not any(a<368 and 364<b for a,b in ranges),'cached overall acquired'
for i,row in enumerate(m['skill_rows']):
    packed=raw[i*stride:(i+1)*stride];at=0
    for low,high in ranges:prove(pd['address']+i*1264+low,packed[at:at+high-low]);at+=high-low
    player=reconstruct_projection(packed,ranges);assert row=={'source_player_index':i,**decode_skills(player)}
    for low,high in RESTRICTED_PLAYER_RANGES:assert player[low:high]==bytes(high-low)
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);compared=0
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall();canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
    payload=skill_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1],canonical)
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone();assert actual and all(actual[k]==v for k,v in expected.items()),(table,key);compared+=1
    matched=c.execute('SELECT count(*) FROM native_player_sources WHERE unit_id=? AND player_id IS NOT NULL',(unit,)).fetchone()[0]
    assert c.execute('SELECT count(*) FROM player_attribute_snapshots WHERE unit_id=? AND overall_raw IS NOT NULL',(unit,)).fetchone()[0]==0
    play_counts=[dict(row) for row in c.execute('SELECT native_play_code,native_play_label,count(*) AS rows FROM player_play_type_slots WHERE unit_id=? GROUP BY native_play_code,native_play_label ORDER BY CAST(native_play_code AS INTEGER)',(unit,))]
    raw_ranges={}
    for group,table in [('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots')]:
        for name in PROFILE[group]:
            value=c.execute('SELECT min('+ident(name)+'),max('+ident(name)+'),count('+ident(name)+') FROM '+ident(table)+' WHERE unit_id=?',(unit,)).fetchone();assert value[2]==pd['count'];raw_ranges[name]={'observed_min':value[0],'observed_max':value[1],'count':value[2],'range_meaning':'OBSERVED_SAMPLE_NOT_UI_LEGAL_LIMIT'}
_json(queries/'native-curry-skills.json',native_player_skills(db,subject_name='Stephen Curry',unit_id=unit));card=player_card(db,'player:native:1612');_json(queries/'curry-current-card.json',card)
for group,table in [('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots')]:
    for name in PROFILE[group]:assert card['families'][table][name]['unit_id']==unit and card['families'][table][name]['value'] is not None,name
assert player_badges(db,'player:native:1612')==player_badges(save/'world-v15.sqlite','player:native:1612')
assert native_player_state(db,subject_name='Stephen Curry')==native_player_state(save/'world-v15.sqlite',subject_name='Stephen Curry')
assert native_affiliations(db,subject_name='Stephen Curry')==native_affiliations(save/'world-v15.sqlite',subject_name='Stephen Curry')
seen=set();after=-1;pages=0
while True:
    page=native_player_skills(db,unit_id=unit,after_index=after,limit=100);pages+=1
    for row in page['records']:
        assert row['source_player_index'] not in seen and row['attributes'] and row['tendencies'] and len(row['play_types'])==4;seen.add(row['source_player_index'])
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(range(pd['count']))
for path in queries.glob('*.json'):
    text=path.read_text(encoding='utf-8').lower();assert not any(s in text for s in ('potential','payload_ref','"address"','protected_value_ref'))
exports={}
for table in ('player_attribute_snapshots','player_tendency_snapshots','player_play_type_slots'):
    path=runtime/('increment17-'+table+'.jsonl');exports[table]=export_jsonl(db,path,table,limit=100000)['rows']
    with path.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as target:shutil.copyfileobj(src,target)
archives={}
for name,directory in (('player-skill-live-v16',capture),('skill-metadata-01',runtime/'skill-metadata-01'),('restart-audit-20261025-01',runtime/'restart-audit-20261025-01')):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive)}
archive=sources/'skill-metadata-research.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('inspect_public_skill_sources.py','public-skill-metadata-inspection.json','summarize_public_skill_sources.py','read_skill_metadata.py','start_skill_metadata.ps1','build_player_skill_profile.py','audit_restart_20261025_01.py','start_restart_audit_20261025_01.ps1'):tar.add(runtime/name,arcname=name,recursive=False)
archives['metadata_research']={'archive':archive.name,'sha256':sha(archive)}
for name in ('migrate_player_skill_v16.py','capture_player_skill_v16.py','start_player_skill_v16.ps1','curate_player_skill_fixture.py'):shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(runtime/'player-skill-migration-v16/migration-report.json',dest/'migration-report.json');_json(sources/'source_manifest.json',archives);_json(sources/'save_binding.json',binding)
restart=json.loads((runtime/'restart-audit-20261025-01/report.json').read_bytes());_json(dest/'restart_context_check.json',{k:v for k,v in restart.items() if k not in ('read_trace','fresh_descriptors','artifact_sha256')})
with db.open('rb') as src,gzip.open(dest/'world-v16.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes());assert sha(save/'world-v15.sqlite')==migration['old_database_sha256']
summary={'status':'NATIVE_PUBLIC_SKILL_BYTES_TO_TYPED_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'schema':summarize(db),'source_pid':report['pid'],'unit_id':unit,'latest_counts':result['counts'],'source_to_typed_rows_compared':compared,'public_player_projections_redecoded':pd['count'],'public_raw_attribute_fields':56,'native_raw_tendency_fields':99,'independent_initiator_flag':True,
    'matched_current_roster_canonical_players':matched,'play_code_counts':play_counts,'observed_raw_ranges':raw_ranges,'old_rows_preserved':migration['preserved_rows'],'old_v15_file_hash_unchanged':True,'known_restricted_player_bytes_requested':0,
    'old_badges_state_and_affiliation_unchanged':True,'pinned_skill_pages':pages,'export_rows':exports,'world_sqlite_sha256':sha(db),'world_sqlite_bytes':db.stat().st_size,'compressed_world_bytes':(dest/'world-v16.sqlite.gz').stat().st_size,
    'game_writes':False,'full_goal_complete':False,'independent_review':False,'limits':['Raw storage does not certify UI rating transforms, legal UI ranges or effective behavior.','Current Overall getter/cache, lifecycle identities, remaining domains, role/capacity/recovery and final independent/Human acceptance remain open.']}
_json(dest/'player_skill_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_player_skill_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','source_pid','source_to_typed_rows_compared','matched_current_roster_canonical_players','old_rows_preserved','compressed_world_bytes')}))
