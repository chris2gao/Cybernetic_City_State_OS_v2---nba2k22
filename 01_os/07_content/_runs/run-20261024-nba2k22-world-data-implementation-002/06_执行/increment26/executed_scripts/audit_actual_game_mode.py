"""Raw game-mode prefix, old facts and query separation; no game operations."""
from contextlib import closing
from datetime import date
import gzip,hashlib,json,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment26';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident
from live_world import read_binding,bound_database
from database_operations import file_sha256
from query import game_mode,league_calendar,season_summary,native_player_seasons
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
worker=json.loads((runtime/'game-mode-v19-worker-report.json').read_bytes());assert worker['status']=='NATIVE_GAME_MODE_V19_COPY_UPGRADE_AND_CAPTURE_FINISHED' and worker['old_database_sha256_unchanged'];batch=worker['refresh'];assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['game-mode'];entry=batch['sources'][0];assert entry['status']=='ACQUIRED' and entry['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and entry['unit']['source_grade']=='LIVE_READ'
unit=entry['unit']['unit_id'];source=runtime/'game-mode-v19-live'/entry['directory'];raw=(source/'game-mode-public-prefix.bin').read_bytes();assert len(raw)==24
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v18.sqlite';assert file_sha256(old)==worker['before_database_sha256']=='46eec932562bb5b722c490bb71011b4d21db87a4f86d1be742ba5435ea87514d' and file_sha256(db)==worker['after_database_sha256']
contexts=[json.loads(p.read_bytes())['epoch'] for p in (runtime/'game-mode-v19-live').glob('*-context.json')];assert len(contexts)==2 and contexts[0]==contexts[1]
previous=json.loads((save/'save.before-v19.json').read_bytes());assert {k:v for k,v in previous.items() if k!='database_file'}=={k:v for k,v in binding.items() if k!='database_file'}
preserved={};deltas={};artifacts=0;comparisons=0;profile=json.loads((app/'game_mode_native_profile.json').read_bytes())
with closing(connect(db,True)) as c:
    c.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert c.execute('PRAGMA user_version').fetchone()[0]==19 and c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[]
    for name, in c.execute("SELECT name FROM baseline.sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        columns=[row['name'] for row in c.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key;clauses=['a.'+ident(column)+' IS NOT b.'+ident(column) for column in columns if (name,column)!=('saves','schema_version')]
        assert c.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
        preserved[name]=c.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
    assert len(preserved)==86 and sum(preserved.values())==1374390
    for name in TABLES:deltas[name]=c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    row=dict(c.execute('SELECT * FROM game_mode_observations WHERE unit_id=?',(unit,)).fetchone());prior=c.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0]
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        if artifact['payload_ref'].startswith(source.name+'/'):path=source/Path(artifact['payload_ref']).name
        elif artifact['payload_ref'].startswith('world_data_prototype/'):path=app/Path(artifact['payload_ref']).name
        else:raise AssertionError('unexpected mode artifact reference')
        assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifacts+=1
    successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==34
for column,offset,size in [('num_teams_raw',0,1),('num_draft_teams_raw',1,1),('current_year_byte_raw',2,1),('draft_year_byte_raw',3,1),('mode_raw',4,4),('league_raw',8,4),('period_raw',12,4),('previous_period_raw',16,4)]:assert row[column]==int.from_bytes(raw[offset:offset+size],'little');comparisons+=1
for label,code,type_name in [('mode_label','mode_raw','GAMEMODE_MODE'),('league_label','league_raw','GAMEMODE_LEAGUE'),('period_label','period_raw','GAMEMODE_TIMEPERIOD'),('previous_period_label','previous_period_raw','GAMEMODE_TIMEPERIOD')]:assert row[label]==profile['enum_labels'][type_name].get(str(row[code]),{}).get('label');comparisons+=1
word=int.from_bytes(raw[20:24],'little');minutes=word>>5&2047;month=word>>21&15;day=word>>16&31;year=2000+(word>>25);iso=None
try:iso=date(year,month+1,day).isoformat() if month<12 else None
except ValueError:pass
for column,value in {'word_raw':word,'id_raw':word&31,'minutes_since_midnight_raw':minutes,'day_raw':day,'month_raw':month,'base_year_offset_raw':word>>25,'native_iso_date':iso,'native_time_hhmm':f'{minutes//60:02d}:{minutes%60:02d}' if iso and minutes<1440 else None}.items():assert row['today_'+column]==value;comparisons+=1
assert row['current_stat_array_position']==(24 if row['period_raw'] in (2,24,26,28,30) else 0);comparisons+=1
queried=game_mode(db);assert queried['records'][0]['unit_id']==unit and queried['records'][0]['period_label']==row['period_label'];assert query_at(db,prior,'game_mode')['result']['records']==[]
calendar=league_calendar(db);assert calendar['records'][0]['unit_id']!=unit
summary=season_summary(db,'season:native-year:2022');assert all(item['totals']['phase_code'] is None for key in ('teams','players') for item in summary[key]);assert native_player_seasons(db,limit=1)['unit']['unit_id']=='native-honors:100325e0dd8283cf68d85b19'
report=json.loads((source/'game-mode-report.json').read_bytes());low=worker['player_interval']['address'];high=low+worker['player_interval']['count']*1264;code_bytes=0;prefix_reads=0
for item in report['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size and (address>=high or address+size<=low)
    if item.get('label','').startswith('GAME_MODE_CODE:'):code_bytes+=size
    if item.get('label','').startswith('GAME_MODE_PUBLIC_PREFIX'):prefix_reads+=1;assert size==24
assert code_bytes==800 and prefix_reads==2 and report['getter_invocations']==report['player_struct_reads']==0
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==worker['before_database_sha256']
examples=dest/'queries';examples.mkdir(exist_ok=True)
for name,value in [('game-mode',queried),('season-calendar-separate-source',calendar),('before-game-mode-observation',query_at(db,prior,'game_mode'))]:write(examples/(name+'.json'),value)
def parts(path,prefix):
    found=[]
    with path.open('rb') as stream:
        while chunk:=stream.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(found)+1).zfill(3));target.write_bytes(chunk);found.append({'file':target.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':found}
native=runtime/'increment26-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('stat-mode-metadata-01','game-mode-v19-live','stat-mode-metadata-labeled.json','stat-mode-switch.json'):tar.add(runtime/name,arcname=name)
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment26-world-v19.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v19.sqlite.gz');snap.update(database_sha256=worker['after_database_sha256'],database_bytes=db.stat().st_size,save_id=binding['save_id'],schema_version=19);write(dest/'world-v19.snapshot.json',snap)
result={'status':'ACTUAL_NATIVE_GAME_MODE_STAGE_SOURCE_QUERY_AND_V19_HISTORY_PRESERVATION_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':19,'tables':87,'columns':1404,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':successful_units,'old_database_sha256_unchanged':worker['before_database_sha256'],'after_database_sha256':worker['after_database_sha256'],'source_unit':unit,'process_epoch':contexts[0],'raw_prefix_bytes':24,'mode_label':row['mode_label'],'league_label':row['league_label'],'period_raw':row['period_raw'],'period_label':row['period_label'],'previous_period_label':row['previous_period_label'],'today_native_iso_date':row['today_native_iso_date'],'current_year_byte_raw':row['current_year_byte_raw'],'draft_year_byte_raw':row['draft_year_byte_raw'],'current_stat_array_position':row['current_stat_array_position'],'raw_field_comparisons':comparisons,'source_artifact_hashes_checked':artifacts,'native_game_mode_period_enum_values':31,'code_proof_bytes_verified':code_bytes,'save_identity_preserved':True,'cumulative_phase_not_inferred':True,'annual_history_refreshed':False,'game_writes':False,'getter_invocations':0,'capacity_work_executed':False,'scheduler_started':False,'full_goal_complete':False,'limits':['Only REGULARSEASON is an actual current mode sample; other period labels are verified enum metadata, not observed transitions.','Shared array position24 does not imply one cumulative-stat phase.','CurrentYear/DraftYear raw bytes have no generalized absolute-year conversion.','Native named stages/dates do not establish UI localization or game effects.']}
write(dest/'actual-game-mode-report.json',result);write(dest/'worker-report.json',worker);write(dest/'binding-declarations.json',{'before':previous,'after':binding,'identity_fields_unchanged':True})
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment26.py','inspect_stat_mode.py','read_stat_mode_metadata.py','start_stat_mode_metadata.ps1','label_stat_mode_metadata.py','build_game_mode_profile.py','capture_game_mode_v19.py','start_game_mode_v19.ps1',Path(__file__).name):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','prior_rows_preserved','after_total_rows','period_label','previous_period_label','today_native_iso_date','current_stat_array_position','raw_field_comparisons')}))
