"""Fresh-process selected-stat source, prior-row preservation and annual isolation."""
from collections import Counter,defaultdict
from contextlib import closing
import gzip,hashlib,json,shutil,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment27';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident,NATIVE_PLAYER_STAT_MAP
from database_operations import file_sha256
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from award_reader import AWARD_COLUMNS
from query import current_period_stats,native_honors,game_mode
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
worker=json.loads((runtime/'period-stats-worker-report.json').read_bytes());assert worker['status']=='CURRENT_PERIOD_STAT_REFRESH_FINISHED' and worker['binding_sha256_unchanged'];batch=worker['refresh'];assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['period-stats'];entry=batch['sources'][0];unit=entry['unit']['unit_id'];assert entry['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and entry['unit']['source_grade']=='LIVE_READ'
source=runtime/'period-stats-live-01'/entry['directory'];m=json.loads((source/'period-stats-manifest.json').read_bytes());report=json.loads((source/'period-stats-report.json').read_bytes());contexts=[json.loads(p.read_bytes())['epoch'] for p in (runtime/'period-stats-live-01').glob('*-context.json')];old_epoch=json.loads((run/'06_执行/increment26/actual-game-mode-report.json').read_bytes())['process_epoch']
assert len(contexts)==2 and contexts[0]==contexts[1] and contexts[0]['pid']==worker['game_pid'] and contexts[0]['creation_filetime']!=old_epoch['creation_filetime'] and contexts[0]['pid']!=old_epoch['pid']
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);assert binding_hash==worker['before_binding_sha256'] and file_sha256(db)==worker['after_database_sha256']
old=runtime/'increment27-baseline.sqlite'
if not old.exists():
    with gzip.open(runtime/'increment26-world-v19.sqlite.gz','rb') as src,old.open('xb') as dst:shutil.copyfileobj(src,dst,4*1024*1024)
assert file_sha256(old)==worker['before_database_sha256']=='d7296d67dcb7c1896a1e3ec242650769c2f84f848dec46049824d89a5395a117'
preserved={};deltas={};artifacts=0
with closing(connect(db,True)) as c:
    c.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[] and c.execute('PRAGMA user_version').fetchone()[0]==19
    for name in TABLES:
        columns=[r['name'] for r in c.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key;clauses=['a.'+ident(column)+' IS NOT b.'+ident(column) for column in columns]
        assert c.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
        preserved[name]=c.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0];deltas[name]=c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved[name]
    assert len(preserved)==87 and sum(preserved.values())==1374426
    for table,count in entry['counts'].items():assert c.execute('SELECT count(*) FROM '+ident(table)+' WHERE unit_id=?',(unit,)).fetchone()[0]==count
    assert c.execute('SELECT count(*) FROM native_player_stat_observations WHERE unit_id=? AND ('+' OR '.join(ident(name)+' IS NOT NULL' for name in AWARD_COLUMNS)+')',(unit,)).fetchone()[0]==0
    before_annual=[tuple(r) for r in c.execute("SELECT unit_id,refresh_family,refresh_period_year FROM baseline.capture_units JOIN baseline.capture_runs USING(run_id) WHERE refresh_family IS NOT NULL")];after_annual=[tuple(r) for r in c.execute("SELECT unit_id,refresh_family,refresh_period_year FROM capture_units JOIN capture_runs USING(run_id) WHERE refresh_family IS NOT NULL")];assert sorted(before_annual)==sorted(after_annual)
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        path=source/Path(artifact['payload_ref']).name if artifact['payload_ref'].startswith(source.name+'/') else app/Path(artifact['payload_ref']).name
        assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifacts+=1
    prior=c.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0];successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==35
    expected={row[0] for row in c.execute('SELECT source_player_index FROM native_player_sources WHERE unit_id=?',(unit,))};expected_core={row[0] for row in c.execute("SELECT source_player_index FROM native_player_sources WHERE unit_id=? AND current_core_roster_status='CURRENT_CORE_ROSTER'",(unit,))}
position=m['selected_array_position'];assert position==m['game_mode']['observation']['current_stat_array_position'];ranges=m['projection_ranges'];stride=m['projection_stride'];projection=(source/'selected-period-public-projections.bin').read_bytes();offset=252+position*2;slot_projection_offset=next(sum(b-a for a,b in ranges[:i])+offset-a for i,(a,b) in enumerate(ranges) if a<=offset and offset+2<=b)
assert stride==96 and len(projection)==len(expected)*stride;profile=json.loads((app/'award_native_profile.json').read_bytes());stat_columns={k:v for k,v in NATIVE_PLAYER_STAT_MAP.items() if v not in AWARD_COLUMNS};seen=set();valid=0;missing=0;comparisons=0;owners=defaultdict(set);statuses=Counter();years=Counter();named={};after=-1;pages=0
while True:
    page=current_period_stats(db,unit_id=unit,current_roster_only=False,after_index=after,limit=100);pages+=1;assert page['unit']['unit_id']==page['game_mode']['unit_id']==unit and page['game_mode']['current_stat_array_position']==position
    for player in page['records']:
        index=player['source_player_index'];assert index not in seen;seen.add(index);native_index=int.from_bytes(projection[index*stride+slot_projection_offset:index*stride+slot_projection_offset+2],'little');reference=player['selected_reference'];assert reference['native_stat_index_raw']==native_index and reference['history_slot_index']==position;statuses[reference['link_status']]+=1
        record=player['record'];can_read=native_index<32768 and native_index<m['stat_bank_descriptor']['count'];assert (record is not None)==can_read;assert player['phase_code'] is None
        if record is None:missing+=1;continue
        valid+=1;raw=(source/f'stat-{native_index}.bin').read_bytes();assert len(raw)==48 and record['source_stat_index']==native_index
        for native,column in stat_columns.items():
            f=profile['stat_fields'][native];value=int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit']&((1<<f['width'])-1);assert record[column]==value,(index,column);comparisons+=1
        assert record['stat_year']==1900+raw[5] and not any(k in record for k in AWARD_COLUMNS);years[record['stat_year']]+=1;owners[native_index].add(index)
        if player['observed_name'] in ('Stephen Curry','LeBron James','Giannis Antetokounmpo') and player['current_core_roster_status']=='CURRENT_CORE_ROSTER':named[player['observed_name']]=player
    if not page['has_more']:break
    assert page['next_after_index']>after;after=page['next_after_index']
assert seen==expected and pages==(len(expected)+99)//100 and valid+missing==len(expected)
core_seen=set();core_records=0;core_missing=0;core_pages=0;after=-1
while True:
    page=current_period_stats(db,unit_id=unit,after_index=after,limit=100);core_pages+=1
    for player in page['records']:core_seen.add(player['source_player_index']);core_records+=player['record'] is not None;core_missing+=player['record'] is None
    if not page['has_more']:break
    after=page['next_after_index']
assert core_seen==expected_core and current_period_stats(db,limit=1)['unit']['unit_id']==unit and game_mode(db)['records'][0]['unit_id']==unit
assert query_at(db,prior,'current_period_stats')['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'current_period_stats',unit_id=unit)['result']['status']=='NOT_OBSERVED'
assert native_honors(db,limit=1)['unit']['unit_id']=='native-honors:100325e0dd8283cf68d85b19'
pd=m['descriptors']['1'];base=pd['address'];end=base+pd['count']*1264;private_checks=0
for item in report['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
    if base<=address+size-1 and address<end:
        index,relative=divmod(address-base,1264);assert 0<=index<pd['count'] and any(a<=relative and relative+size<=b for a,b in ranges)
        assert all(address>=base+index*1264+hi or address+size<=base+index*1264+lo for lo,hi in RESTRICTED_PLAYER_RANGES);private_checks+=1
assert private_checks==len(expected)*len(ranges)*3
examples=dest/'queries';examples.mkdir(exist_ok=True)
for name,player in named.items():write(examples/(name.replace(' ','-').lower()+'.json'),current_period_stats(db,unit_id=unit,source_index=player['source_player_index']))
write(examples/'core-first-page.json',current_period_stats(db,unit_id=unit,limit=3));write(examples/'current-native-mode.json',game_mode(db));write(examples/'annual-honor-source-unchanged.json',{'unit':native_honors(db,limit=1)['unit']})
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==worker['before_database_sha256']
def parts(path,prefix):
    result=[]
    with path.open('rb') as src:
        while chunk:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(result)+1).zfill(3));target.write_bytes(chunk);result.append({'file':target.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':result}
native=runtime/'increment27-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:tar.add(runtime/'period-stats-live-01',arcname='period-stats-live-01')
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment27-world-v19.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v19.sqlite.gz');snap.update(database_sha256=worker['after_database_sha256'],database_bytes=db.stat().st_size,save_id=binding['save_id'],schema_version=19);write(dest/'world-v19.snapshot.json',snap)
result={'status':'ACTUAL_FRESH_PROCESS_SELECTED_PERIOD_STATS_AND_PRIOR_FACTS_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':19,'tables':87,'columns':1404,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':successful_units,'before_database_sha256':worker['before_database_sha256'],'after_database_sha256':worker['after_database_sha256'],'source_unit':unit,'process_epoch':contexts[0],'prior_process_epoch':old_epoch,'restarted_process_recalibrated':True,'source_player_count':len(expected),'core_roster_sources':len(expected_core),'full_source_query_pages':pages,'core_query_pages':core_pages,'captured_reference_count':valid+missing,'resolved_source_references':valid,'missing_source_references':missing,'core_roster_resolved_records':core_records,'core_roster_missing_records':core_missing,'distinct_stat_records':len(owners),'shared_stat_records':sum(len(v)>1 for v in owners.values()),'resolution_counts':dict(statuses),'record_year_counts':dict(years),'raw_stat_field_comparisons':comparisons,'source_artifact_hashes_checked':artifacts,'private_free_player_interval_checks':private_checks,'period_label':m['game_mode']['observation']['period_label'],'selected_array_position':position,'annual_award_columns_withheld':list(AWARD_COLUMNS),'annual_bucket_units_unchanged':True,'save_binding_unchanged':True,'game_writes':False,'getter_invocations':0,'annual_history_refreshed':False,'capacity_work_executed':False,'scheduler_started':False,'full_goal_complete':False,'limits':['Actual current sample selects position0 in REGULARSEASON; position24 is code/fixture verified, not an observed transition.','Raw record years, allocation and historical identities remain qualified; no accumulated phase is inferred.','Packed48-byte source windows can include overlapping honor bits; annual columns are omitted from ordinary typed facts and query.']}
write(dest/'actual-period-stat-report.json',result);write(dest/'worker-report.json',worker);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment27.py','capture_period_stats_live.py','start_period_stats_live.ps1',Path(__file__).name):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','prior_rows_preserved','after_total_rows','source_player_count','core_roster_sources','resolved_source_references','core_roster_resolved_records','distinct_stat_records','raw_stat_field_comparisons','private_free_player_interval_checks')}))
