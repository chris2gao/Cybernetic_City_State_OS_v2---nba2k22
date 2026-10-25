"""Compare Native date/classification observations with raw bytes and retain provenance."""
from collections import Counter
from contextlib import closing
from datetime import date
import gzip,hashlib,json,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident
from database_operations import file_sha256
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from query import league_calendar,schedule,game_box,season_summary
from observation_scope import query_at
from calendar_codec import PROFILE
r=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');runtime=r/'_runtime';dest=r/'06_执行/increment23';dest.mkdir(parents=True,exist_ok=True);examples=dest/'queries';examples.mkdir(exist_ok=True)
w=json.loads((runtime/'calendar-v18-worker-report.json').read_bytes());assert w['status']=='NATIVE_V18_CALENDAR_AND_GAME_CLASSIFICATION_CAPTURE_FINISHED',w
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v17.sqlite';unit=w['capture']['unit_id'];source=runtime/'calendar-v18-live'
assert file_sha256(old)==w['before_database_sha256']=='ba0d03601940d6739aae90b885a6a13363e551298d6197bf30d990eb5219bade' and file_sha256(db)==w['after_database_sha256'] and w['context_before']['epoch']==w['context_after']['epoch']
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def raw_date(raw):
    value=int.from_bytes(raw,'little');month=value>>21&15;day=value>>16&31;year=2000+(value>>25);minutes=value>>5&2047;iso=None
    try:iso=date(year,month+1,day).isoformat() if month<12 else None
    except ValueError:pass
    return {'word_raw':value,'id_raw':value&31,'minutes_since_midnight_raw':minutes,'day_raw':day,'month_raw':month,'base_year_offset_raw':value>>25,
        'native_iso_date':iso,'native_time_hhmm':f'{minutes//60:02d}:{minutes%60:02d}' if iso and minutes<1440 else None}
preserved={};deltas={};field_comparisons=0;source_hashes=0;checks_by_game={}
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    for name, in conn.execute("SELECT name FROM baseline.sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols=[f['name'] for f in conn.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key;clauses=['a.'+ident(c)+' IS NOT b.'+ident(c) for c in cols if (name,c)!=('saves','schema_version')]
        assert conn.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
        preserved[name]=conn.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
    for name in TABLES:deltas[name]=conn.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    calendar=dict(conn.execute('SELECT * FROM season_calendar_observations WHERE unit_id=?',(unit,)).fetchone());checks=[dict(row) for row in conn.execute('SELECT c.*,g.native_game_id FROM game_source_checks c JOIN games g USING(game_id) WHERE c.unit_id=?',(unit,))]
    source_time=conn.execute('SELECT observed_at FROM capture_units WHERE unit_id=?',(unit,)).fetchone()[0]
    for artifact in conn.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        if artifact['payload_ref'].startswith(source.name+'/'):
            path=source/Path(artifact['payload_ref']).name;assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];source_hashes+=1
games=(source/'schedule-games.bin').read_bytes();prefix=(source/'schedule-header.bin').read_bytes();raw_current=raw_date(prefix[:4])
for name,value in raw_current.items():assert calendar['current_'+name]==value;field_comparisons+=1
assert calendar['period_raw']==int.from_bytes(prefix[4:8],'little') and calendar['period_label']==PROFILE['enum_labels']['SEASON_TIMEPERIOD'][str(calendar['period_raw'])]['label']
assert calendar['current_index_raw']==int.from_bytes(prefix[28:32],'little') and calendar['next_index_raw']==int.from_bytes(prefix[32:36],'little')
assert calendar['declared_game_count_raw']==calendar['source_slot10_count_raw']==len(games)//60 and calendar['game_capacity_verified']==1742 and calendar['box_stat_capacity_verified']==45292
manifest=json.loads((source/'schedule-manifest.json').read_bytes());entries={e['native_game_id']:e for e in manifest['entries']};periods=Counter();types=Counter();statuses=Counter();played_dates=0
bitfields={'time_period_raw':(56,4,6,3),'game_type_raw':(56,4,9,2),'force_winner_raw':(56,4,13,3),'home_uniform_id_raw':(16,2,0,16),'away_uniform_id_raw':(18,2,0,16),
    'was_simulated_raw':(56,4,18,1),'was_sim_to_end_raw':(56,4,19,1),'is_foreign_site_raw':(56,4,16,1),'is_selected_raw':(56,4,17,1),'is_nationally_televised_raw':(56,4,20,1),'overtime_count_raw':(56,4,0,6),'attendance_raw':(52,4,16,15)}
for check in checks:
    raw=games[entries[int(check['native_game_id'])]['pool_index']*60:][:60];checks_by_game[check['game_id']]=check
    for start,pref in ((0,'scheduled_'),(4,'played_')):
        for name,value in raw_date(raw[start:start+4]).items():assert check[pref+name]==value,(check['game_id'],pref+name);field_comparisons+=1
    for name,(offset,size,shift,width) in bitfields.items():assert check[name]==(int.from_bytes(raw[offset:offset+size],'little')>>shift)&((1<<width)-1);field_comparisons+=1
    for code,label,type_name in [('time_period_raw','time_period_label','SEASON_TIMEPERIOD'),('game_type_raw','game_type_label','SEASON_GAMETYPE'),('force_winner_raw','force_winner_label','SIM_FORCE_WINNER_TYPE'),('game_status_raw','status_label','SEASON_GAMESTATUS')]:
        assert check[label]==PROFILE['enum_labels'][type_name].get(str(check[code]),{}).get('label');field_comparisons+=1
    periods[check['time_period_label']]+=1;types[check['game_type_label']]+=1;statuses[check['status_label']]+=1;played_dates+=check['played_native_iso_date'] is not None
rows=schedule(db);assert len(rows)==len(checks)
for row in rows:
    check=checks_by_game[row['game_id']];assert row['native_game_date']==check['scheduled_native_iso_date'] and row['calendar_unit_id']==unit and row['calendar_observed_at']==source_time and row['game_date'] is None
    assert row['time_period_label']==check['time_period_label'] and row['game_type_label']==check['game_type_label']
read=league_calendar(db)['records'][0];assert read['unit_id']==unit and read['current_native_iso_date']==calendar['current_native_iso_date']
assert query_at(db,'2000-01-01T00:00:00Z','league_calendar')['result']['records']==[]
with closing(connect(db,True)) as conn:prior=conn.execute('SELECT max(observed_at) FROM capture_units WHERE unit_id<>?',(unit,)).fetchone()[0]
assert query_at(db,prior,'league_calendar')['result']['records']==[];old_rows=query_at(db,prior,'schedule')['result'];assert all(row['native_game_date'] is None for row in old_rows)
filters={}
for code in (0,1,2):
    selected=schedule(db,game_type_code=code);assert len(selected)==sum(check['game_type_raw']==code for check in checks);filters[str(code)]=len(selected);write(examples/('game-type-'+str(code)+'.json'),selected)
month='2021-11';selected=schedule(db,native_date_from=month+'-01',native_date_to=month+'-30');assert all(row['native_game_date'].startswith(month) for row in selected)
write(examples/'november-schedule.json',selected);write(examples/'calendar.json',league_calendar(db));write(examples/'season-summary.json',season_summary(db,'season:native-year:2022'))
summary=season_summary(db,'season:native-year:2022');assert all(r['totals']['phase_code'] is None for key in ('teams','players') for r in summary[key])
reused=next(c for c in checks if c['box_mode']=='REUSED_FROZEN_BOX');box=game_box(db,reused['game_id']);assert box['selected_unit_id']==reused['prior_full_unit_id'] and box['latest_header_check']['unit_id']==unit;write(examples/'frozen-game-with-current-calendar.json',box)
acq=json.loads((source/'acquisition-report.json').read_bytes());context=json.loads((source/'player-context.json').read_bytes());base=context['descriptors']['1']['address'];count=context['descriptors']['1']['count'];end=base+count*1264;private_checks=0
for item in acq['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
    if base<=address+size-1 and address<end:
        for index in range(max(0,(address-base)//1264),min(count-1,(address+size-1-base)//1264)+1):
            for lo,hi in RESTRICTED_PLAYER_RANGES:assert address>=base+index*1264+hi or address+size<=base+index*1264+lo
        private_checks+=1
assert sum(i.get('label')=='CALENDAR_YEAR_EPOCH_CODE' for i in acq['read_trace'])==2 and w['capture']['frozen_boxes_reused']==202 and w['capture']['native_boxes_read']==36
assert file_sha256(db)==w['after_database_sha256'] and file_sha256(old)==w['before_database_sha256']
def parts(path,prefix):
    result=[]
    with path.open('rb') as src:
        while chunk:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(result)+1).zfill(3));target.write_bytes(chunk);result.append({'file':target.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':result}
native=runtime/'increment23-calendar-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('calendar-metadata-01','calendar-metadata-02','calendar-v18-live'):tar.add(runtime/name,arcname=name)
    for name in ('calendar-year-code-candidates.json','calendar-code-inspection.json','calendar-metadata-02-labeled.json'):tar.add(runtime/name,arcname=name)
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment23-world-v18.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v18.sqlite.gz');snap.update({'database_sha256':w['after_database_sha256'],'database_bytes':db.stat().st_size,'save_id':'nba2k22_test_01','schema_version':18});write(dest/'world-v18.snapshot.json',snap)
result={'status':'ACTUAL_NATIVE_CALENDAR_CLASSIFICATION_AND_SOURCE_AGE_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':w['candidate_code_head'],'schema_version':18,'tables':86,'columns':1376,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,
    'before_database_sha256_unchanged':w['before_database_sha256'],'after_database_sha256':w['after_database_sha256'],'current_native_date':calendar['current_native_iso_date'],'current_native_time':calendar['current_native_time_hhmm'],'current_native_period':calendar['period_label'],'native_year_scope':'season:native-year:2022; distinct from civil calendar year2021',
    'games_checked':len(checks),'field_comparisons_with_raw_bytes':field_comparisons,'period_counts':dict(periods),'game_type_counts':dict(types),'status_counts':dict(statuses),'nonempty_played_dates':played_dates,'game_type_filter_counts':filters,'november_filtered_rows':len(selected),'source_artifact_hashes_checked':source_hashes,'player_private_interval_read_checks':private_checks,
    'frozen_boxes_reused':w['capture']['frozen_boxes_reused'],'native_boxes_read':w['capture']['native_boxes_read'],'calendar_hidden_before_its_observation':True,'cumulative_phase_not_inferred':True,'save_identity_preserved':True,'game_writes':False,'capacity_work_executed':False,'scheduler_started':False,'full_goal_complete':False,
    'limits':['Native civil dates and enums are verified; UI rendering/localization/timezone remain unaccepted.','Current SEASON period does not establish cumulative-stat phase or franchise offseason substage.','Old date candidates and immutable game identity columns are retained, not rewritten.']}
write(dest/'actual-calendar-report.json',result);write(dest/'worker-report.json',w);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in (Path(__file__).name,'capture_calendar_v18.py','start_calendar_v18.ps1','read_calendar_metadata.py','read_calendar_metadata_02.py','start_calendar_metadata.ps1','start_calendar_metadata_02.ps1','label_calendar_metadata.py','inspect_calendar_code.py','build_calendar_profile.py'):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification*/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','prior_rows_preserved','after_total_rows','current_native_date','current_native_period','games_checked','field_comparisons_with_raw_bytes','period_counts','game_type_counts','status_counts','frozen_boxes_reused','native_boxes_read')}))
