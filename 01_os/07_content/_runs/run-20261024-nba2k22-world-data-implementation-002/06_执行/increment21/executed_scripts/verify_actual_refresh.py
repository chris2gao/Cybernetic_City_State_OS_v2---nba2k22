"""Audit the explicit completed refresh, preserve all old facts and retain source evidence."""
from collections import Counter
from contextlib import closing
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from database_operations import file_sha256
from schema_model import TABLES,ident
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from refresh import SOURCES,_unit_receipt
from query import player_card,game_box,season_summary,team_card,native_player_details,native_player_state,native_player_skills,native_affiliations
run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');runtime=run/'_runtime';dest=run/'06_执行/increment21';dest.mkdir(parents=True,exist_ok=True);queries=dest/'queries';queries.mkdir(exist_ok=True)
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
worker=json.loads((runtime/'world-refresh-worker-report.json').read_bytes());before=json.loads((runtime/'world-refresh-before.json').read_bytes());batch=worker['result'];source=runtime/'world-refresh-live-01'
assert worker['status']=='EXPLICIT_NATIVE_WORLD_REFRESH_FINISHED' and batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==list(SOURCES)
assert worker['binding_unchanged'] and binding_hash==before['binding_sha256'] and file_sha256(db)==worker['database_sha256_after']
assert before['database_sha256']=='466d3eeaf7bda194cdba7f26f6013227a9c2a569084ee450a665792746135932'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
baseline=runtime/'increment21-baseline.sqlite'
if not baseline.exists():
    with gzip.open(run/'06_执行/increment17/world-v16.sqlite.gz','rb') as src,baseline.open('xb') as dst:shutil.copyfileobj(src,dst,4*1024*1024)
assert file_sha256(baseline)==before['database_sha256']
preserved={};new_counts={};rate_units={};source_rows={};source_artifacts_checked=0
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS baseline',(baseline.as_uri()+'?mode=ro',))
    assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    old_units={r[0] for r in conn.execute('SELECT unit_id FROM baseline.capture_units')};all_units={r[0] for r in conn.execute('SELECT unit_id FROM main.capture_units')}
    for name,spec in TABLES.items():
        count=conn.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
        differences=' OR '.join('old.'+ident(c.name)+' IS NOT current.'+ident(c.name) for c in spec.columns)
        mismatch=conn.execute('SELECT count(*) FROM baseline.'+ident(name)+' old LEFT JOIN main.'+ident(name)+' current ON current.'+ident(spec.key)+'=old.'+ident(spec.key)+' WHERE current.'+ident(spec.key)+' IS NULL OR '+differences).fetchone()[0]
        assert mismatch==0,(name,mismatch);preserved[name]=count;new_counts[name]=conn.execute('SELECT count(*) FROM main.'+ident(name)).fetchone()[0]-count
    acquired=set();skipped=set()
    for entry in batch['sources']:
        family=entry['family'];unit=entry['unit'];key=unit['unit_id'];rate_units[family]=key
        assert unit==_unit_receipt(db,{'status':'already_refreshed','previous_unit_id':key} if entry['status']=='ANNUAL_ALREADY_REFRESHED' else {'status':'ingested','unit_id':key},family,batch['game_season_year'])
        if entry['status']=='ACQUIRED':
            assert key not in old_units;acquired.add(key);source_rows[family]={}
            for table,count in entry['counts'].items():
                if 'unit_id' not in {c.name for c in TABLES[table].columns}:continue
                actual=conn.execute('SELECT count(*) FROM main.'+ident(table)+' WHERE unit_id=?',(key,)).fetchone()[0];assert actual==count,(family,table,actual,count);source_rows[family][table]=actual
            for artifact in conn.execute('SELECT sha256,payload_ref,byte_count FROM source_artifacts WHERE unit_id=?',(key,)):
                prefix=entry['directory']+'/'
                if not artifact['payload_ref'].startswith(prefix):continue
                path=source/entry['directory']/artifact['payload_ref'][len(prefix):]
                assert path.is_file() and file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];source_artifacts_checked+=1
        else:assert entry['status']=='ANNUAL_ALREADY_REFRESHED' and key in old_units;skipped.add(key)
    assert all_units-old_units==acquired and len(acquired)==10 and len(skipped)==3
    annual_before=[tuple(r) for r in conn.execute("SELECT u.unit_id,r.refresh_family,r.refresh_period_year FROM baseline.capture_runs r JOIN baseline.capture_units u USING(run_id) WHERE r.refresh_family IS NOT NULL ORDER BY u.unit_id")]
    annual_after=[tuple(r) for r in conn.execute("SELECT u.unit_id,r.refresh_family,r.refresh_period_year FROM main.capture_runs r JOIN main.capture_units u USING(run_id) WHERE r.refresh_family IS NOT NULL ORDER BY u.unit_id")];assert annual_before==annual_after
contexts=[json.loads(p.read_bytes()) for p in sorted(source.glob('*-context.json'))];assert len(contexts)==26 and all(c['epoch']==contexts[0]['epoch'] for c in contexts)
traces=[item for context in contexts for item in context['read_trace']];private_checks=0;physical_checks=0
for entry in batch['sources']:
    folder=source/entry['directory'];manifests=[json.loads(p.read_bytes()) for p in folder.glob('*manifest.json')]
    if (folder/'player-context.json').exists():manifests.append(json.loads((folder/'player-context.json').read_bytes()))
    pool=None
    for manifest in manifests:
        descriptors=manifest.get('descriptors',{});candidate=descriptors.get('1',{})
        if 'address' in candidate and 'count' in candidate:pool=(int(candidate['address']),candidate['count'])
    family_traces=[]
    for path in folder.glob('*.json'):
        value=json.loads(path.read_bytes())
        if isinstance(value,dict) and 'read_trace' in value:family_traces+=value['read_trace']
    if pool:
        base,count=pool;end=base+count*1264
        for item in family_traces:
            if item.get('operation')!='ReadProcessMemory':continue
            address=int(item['address'],16);size=item['requested_bytes']
            if address>=end or address+size<=base:continue
            first=max(0,(address-base)//1264);last=min(count-1,(address+size-1-base)//1264)
            for index in range(first,last+1):
                for low,high in RESTRICTED_PLAYER_RANGES:assert address>=base+index*1264+high or address+size<=base+index*1264+low,(entry['family'],item['label'],index,low)
            private_checks+=1
    if entry['family'] in ('player-details','player-state','affiliations','player-skills'):assert pool is not None
    traces+=family_traces
for item in traces:
    assert item['operation'] in ('OpenProcess','ReadProcessMemory','GetProcessTimes') and item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']=='ReadProcessMemory':assert 1<=item['requested_bytes']<=1248 and item['requested_bytes']==item['returned_bytes'];physical_checks+=1
card=player_card(db,'player:native:1612');write(queries/'curry-after-refresh.json',card)
for family,table in [('player-skills','player_attribute_snapshots'),('player-details','player_contract_observations'),('player-state','player_health_observations')]:
    observed={value['unit_id'] for value in card['families'][table].values() if isinstance(value,dict) and value.get('value') is not None};assert rate_units[family] in observed,(family,observed)
summary=season_summary(db,'season:native-year:2022');assert len(summary['players'])==369 and len(summary['teams'])==30
assert all(r['totals']['unit_id']==rate_units['schedule'] for r in summary['players']);assert all(r['totals']['unit_id']==rate_units['organization'] for r in summary['teams']);write(queries/'season-after-refresh.json',summary)
for family,function in [('player-details',native_player_details),('player-state',native_player_state),('affiliations',native_affiliations),('player-skills',native_player_skills)]:
    value=function(db,subject_name='Stephen Curry',unit_id=rate_units[family],limit=10);assert value['records'];write(queries/(family+'-curry.json'),value)
with closing(connect(db,True)) as conn:game=conn.execute('SELECT game_id FROM player_game_boxes WHERE unit_id=? ORDER BY game_id LIMIT 1',(rate_units['schedule'],)).fetchone()[0]
box=game_box(db,game);assert box['selected_unit_id']==rate_units['schedule'];write(queries/'game-after-refresh.json',box);write(queries/'team-after-refresh.json',team_card(db,'team:native:0'))
assert read_binding(save,'MyLEAGUE0003')[1]==binding_hash and file_sha256(db)==worker['database_sha256_after']
def archive_parts(path,prefix):
    parts=[]
    with path.open('rb') as src:
        index=0
        while chunk:=src.read(32*1024*1024):
            index+=1;part=dest/(prefix+'.part'+str(index).zfill(3));part.write_bytes(chunk);parts.append({'file':part.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':parts}
native_archive=runtime/'increment21-native-sources.tar.gz'
with tarfile.open(native_archive,'w:gz',compresslevel=6) as tar:tar.add(source,arcname=source.name)
native_manifest=archive_parts(native_archive,'native-sources.tar.gz');write(dest/'native-sources.archive.json',native_manifest)
snapshot=runtime/'increment21-world-v16.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
assert file_sha256(db)==worker['database_sha256_after']
snapshot_manifest=archive_parts(snapshot,'world-v16.sqlite.gz');snapshot_manifest.update({'database_sha256':worker['database_sha256_after'],'database_bytes':db.stat().st_size,'save_id':binding['save_id'],'schema_version':16});write(dest/'world-v16.snapshot.json',snapshot_manifest)
report={'status':'ACTUAL_SERIAL_WORLD_REFRESH_AND_APPEND_ONLY_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':before['candidate_code_head'],'successful_adapters':10,'verified_annual_skips':3,'context_checkpoints':len(contexts),'process_context':contexts[0]['epoch'],
    'before_database_sha256':before['database_sha256'],'after_database_sha256':worker['database_sha256_after'],'binding_unchanged':True,'prior_rows_preserved':sum(preserved.values()),'prior_table_rows':preserved,'new_rows_by_table':new_counts,'after_total_rows':sum(preserved.values())+sum(new_counts.values()),
    'prior_units':len(old_units),'after_units':len(all_units),'source_unit_ids':rate_units,'new_unit_table_counts':source_rows,'source_artifacts_hash_checked':source_artifacts_checked,'successful_bounded_read_checks':physical_checks,'reads_checked_against_private_player_intervals':private_checks,'annual_ledger_unchanged':True,
    'queries_verified':['player_card','season_summary','native_player_details','native_player_state','native_affiliations','native_player_skills','game_box','team_card'],'capacity_work_executed':False,'game_writes':False,'scheduler_started':False,'schema_migration':False,'full_goal_complete':False,
    'limits':['Source observations are independent atomic units, not one global point-in-time snapshot.','Native/UI/lifecycle/source gaps are unchanged; annual skips retain their earlier source time.','The present repeated month sample is not full-season capacity evidence or a retention decision.']}
write(dest/'actual-world-refresh-report.json',report);write(dest/'refresh-report.json',batch);write(dest/'worker-report.json',worker);write(dest/'before.json',before)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True);(scripts/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
for name in ('run_world_refresh_v16.py','start_world_refresh_v16.ps1'):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:report[k] for k in ('status','successful_adapters','verified_annual_skips','prior_rows_preserved','after_total_rows','after_units','context_checkpoints','source_artifacts_hash_checked','successful_bounded_read_checks','reads_checked_against_private_player_intervals')}))
