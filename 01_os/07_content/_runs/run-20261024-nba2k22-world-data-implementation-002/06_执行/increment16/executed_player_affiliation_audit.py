"""Verify actual classification and pointed college bytes through typed queries."""
from bisect import bisect_right
from collections import Counter
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from live_world import _json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import reconstruct_projection
from player_affiliation_reader import affiliation_payload,affiliation_projection_ranges
from player_affiliation_codec import PROFILE,decode_classification,decode_college,reconstruct_college_projection
from query import native_affiliations,native_player_state,player_card,player_badges,export_jsonl
from schema_model import TABLES,ident
runtime=RUN/'_runtime';capture=runtime/'player-affiliation-live-v15';dest=RUN/'06_执行/increment16';dest.mkdir(parents=True,exist_ok=True)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((capture/'affiliation-manifest.json').read_bytes());report=json.loads((capture/'affiliation-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert sha(capture/name)==digest,name
for name,digest in report['code_sha256'].items():assert sha(APP/name)==digest,name
trace=report['read_trace'];assert all(e['success'] for e in trace) and trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(e['address'],16),e['returned_bytes'],e['sha256']) for e in trace if e['operation']=='ReadProcessMemory'}
def prove(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
pd=m['descriptors']['1'];stride=m['projection_stride'];ranges=[tuple(r) for r in m['projection_ranges']];assert ranges==affiliation_projection_ranges()
raw=(capture/'player-affiliation-public-projections.bin').read_bytes();college_raw=(capture/'college-public-projections.bin').read_bytes();college_stride=m['college_projection_stride']
assert len(raw)==pd['count']*stride and len(college_raw)==len(m['college_rows'])*college_stride
forbidden=sorted((pd['address']+i*1264+low,pd['address']+i*1264+high) for i in range(pd['count']) for low,high in RESTRICTED_PLAYER_RANGES)
forbidden+=sorted((pointer+47,pointer+48) for pointer in m['college_object_pointers_owner_only'].values());forbidden.sort();starts=[low for low,high in forbidden]
for e in trace:
    if e['operation']!='ReadProcessMemory':continue
    start=int(e['address'],16);end=start+e['requested_bytes'];j=bisect_right(starts,end-1)-1
    assert j<0 or forbidden[j][1]<=start,('excluded-byte-overlap',e['label'])
link_by_index={r['source_player_index']:r for r in m['college_links']}
for i,row in enumerate(m['classification_rows']):
    packed=raw[i*stride:(i+1)*stride];at=0
    for low,high in ranges:prove(pd['address']+i*1264+low,packed[at:at+high-low]);at+=high-low
    player=reconstruct_projection(packed,ranges);pointer=int.from_bytes(player[120:128],'little');assert pointer==m['college_pointer_values_owner_only'][i]
    prove(pd['address']+i*1264+120,pointer.to_bytes(8,'little'))
    assert row=={'source_player_index':i,**decode_classification(player)}
    ordinal=link_by_index[i]['source_object_index']
    if ordinal is not None:assert m['college_object_pointers_owner_only'][str(ordinal)]==pointer
    for low,high in RESTRICTED_PLAYER_RANGES:assert player[low:high]==bytes(high-low)
for row in m['college_rows']:
    ordinal=row['source_object_index'];pointer=m['college_object_pointers_owner_only'][str(ordinal)];packed=college_raw[ordinal*college_stride:(ordinal+1)*college_stride];at=0
    assert not(pd['address']<pointer+60 and pointer<pd['address']+pd['count']*1264)
    for low,high in PROFILE['college_public_ranges']:prove(pointer+low,packed[at:at+high-low]);at+=high-low
    projected=reconstruct_college_projection(packed);assert projected[47]==0
    assert row=={'source_object_index':ordinal,**decode_college(projected)}
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);compared=0
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall()
    canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
    payload=affiliation_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1],canonical)
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual and all(actual[k]==value for k,value in expected.items()),(table,key);compared+=1
    matched=c.execute('SELECT count(*) FROM native_player_sources WHERE unit_id=? AND player_id IS NOT NULL',(unit,)).fetchone()[0]
    assert c.execute('SELECT count(*) FROM player_vitals_observations WHERE unit_id=? AND (country IS NOT NULL OR college IS NOT NULL OR height_raw IS NOT NULL OR weight_raw IS NOT NULL)',(unit,)).fetchone()[0]==0
    assert c.execute("SELECT count(*) FROM market_state_observations WHERE unit_id=? AND market_status<>'NATIVE_CLASSIFICATION_OBSERVED'",(unit,)).fetchone()[0]==0
    type_counts=[dict(r) for r in c.execute('SELECT native_player_type_label,count(*) AS rows FROM market_state_observations WHERE unit_id=? GROUP BY native_player_type_label',(unit,))]
    flags={name:c.execute('SELECT count(*) FROM market_state_observations WHERE unit_id=? AND '+ident(name)+'=1',(unit,)).fetchone()[0] for name,f in PROFILE['player_fields'].items() if f['width']==1}
    unrestricted_rostered=c.execute('''SELECT count(*) FROM market_state_observations m JOIN native_player_sources p ON p.player_source_id=m.source_player_id WHERE m.unit_id=? AND p.current_core_roster_status='CURRENT_CORE_ROSTER' AND m.free_agency_type_label='UNRESTRICTED' ''',(unit,)).fetchone()[0]
_json(queries/'native-curry-affiliations.json',native_affiliations(db,subject_name='Stephen Curry',unit_id=unit))
_json(queries/'historic-source-page.json',native_affiliations(db,flag='is_historic_raw',unit_id=unit))
_json(queries/'dleague-source-page.json',native_affiliations(db,flag='is_d_league_raw',unit_id=unit))
card=player_card(db,'player:native:1612');_json(queries/'curry-current-card.json',card)
with connect(save/'world-v14.sqlite',True) as old:
    for column,latest in card['families']['player_attribute_snapshots'].items():
        before=old.execute(f'''SELECT a.{ident(column)} AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade FROM player_attribute_snapshots a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE a.player_id=? AND a.{ident(column)} IS NOT NULL ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',('player:native:1612',)).fetchone()
        if before:assert all(latest[key]==value for key,value in dict(before).items()),column
        else:assert latest['value'] is None,column
assert player_badges(db,'player:native:1612')==player_badges(save/'world-v14.sqlite','player:native:1612')
old_state=native_player_state(save/'world-v14.sqlite',subject_name='Stephen Curry');new_state=native_player_state(db,subject_name='Stephen Curry');assert old_state['unit_id']==new_state['unit_id']
for before,after in zip(old_state['records'],new_state['records']):
    for family in ('vitals','health','morale'):assert all(after[family][k]==v for k,v in before[family].items())
seen=set();after=-1;pages=0
while True:
    page=native_affiliations(db,unit_id=unit,after_index=after,limit=100);pages+=1
    for row in page['records']:
        assert row['source_player_index'] not in seen and row['classification'] and row['school_country_source'];seen.add(row['source_player_index'])
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(range(pd['count']))
for path in queries.glob('*.json'):
    public=path.read_text(encoding='utf-8').lower();assert not any(s in public for s in ('potential','payload_ref','"address"','college_pointer_values','protected_value_ref'))
exports={}
for table in ('market_state_observations','native_college_observations','player_vitals_observations'):
    path=runtime/('increment16-'+table+'.jsonl');exports[table]=export_jsonl(db,path,table,limit=100000)['rows']
    with path.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as target:shutil.copyfileobj(src,target)
archives={}
for name,directory in (('player-affiliation-live-v15',capture),('affiliation-metadata-01',runtime/'affiliation-metadata-01'),('college-region-metadata-01',runtime/'college-region-metadata-01')):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive)}
archive=sources/'affiliation-metadata-research.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('read_affiliation_metadata.py','start_affiliation_metadata.ps1','read_college_region_metadata.py','start_college_region_metadata.ps1','inspect_player_affiliation_metadata.py','label_affiliation_metadata.py','affiliation-literal-labels.json','build_affiliation_profile.py'):tar.add(runtime/name,arcname=name,recursive=False)
archives['metadata_research']={'archive':archive.name,'sha256':sha(archive)}
for name in ('migrate_player_affiliation_v15.py','capture_player_affiliation_v15.py','start_player_affiliation_v15.ps1','curate_player_affiliation_fixture.py'):shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(runtime/'player-affiliation-migration-v15/migration-report.json',dest/'migration-report.json');_json(sources/'source_manifest.json',archives);_json(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v15.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes());assert sha(save/'world-v14.sqlite')==migration['old_database_sha256']
summary={'status':'NATIVE_AFFILIATION_AND_COLLEGE_BYTES_TO_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE',
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),'schema':summarize(db),
    'source_pid':report['pid'],'unit_id':unit,'latest_counts':result['counts'],'source_to_typed_rows_compared':compared,'public_player_projections_redecoded':pd['count'],
    'matched_current_roster_canonical_players':matched,'college_status_counts':m['college_status_counts'],'native_type_counts':type_counts,'native_flag_counts':flags,'unrestricted_code_on_current_roster_players':unrestricted_rostered,
    'old_rows_preserved':migration['preserved_rows'],'old_v14_file_hash_unchanged':True,'known_restricted_player_bytes_requested':0,'college_generation_byte47_requested':0,
    'old_attributes_badges_and_state_unchanged':True,'pinned_affiliation_pages':pages,'export_rows':exports,
    'world_sqlite_sha256':sha(db),'world_sqlite_bytes':db.stat().st_size,'compressed_world_bytes':(dest/'world-v15.sqlite.gz').stat().st_size,
    'game_writes':False,'full_goal_complete':False,'independent_review':False,
    'limits':['Native independent flags and agency type do not establish signability or current market availability.','G League code alone does not establish an active assignment or canonical team identity.','COLLEGEDATA labels and appearance groups do not prove college/country/nationality category.','Source lifecycle, remaining domains, capacity/recovery and final independent/Human acceptance remain open.']}
_json(dest/'player_affiliation_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_player_affiliation_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','source_to_typed_rows_compared','matched_current_roster_canonical_players','old_rows_preserved','college_status_counts','compressed_world_bytes')}))
