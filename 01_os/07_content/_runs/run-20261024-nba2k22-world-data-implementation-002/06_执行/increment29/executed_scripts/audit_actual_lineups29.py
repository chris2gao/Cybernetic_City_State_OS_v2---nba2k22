"""Actual lineup references/matrix, public PLAYER words and complete history audit."""
from collections import Counter
from contextlib import closing
import gzip,hashlib,json,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment29';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident,VERSION
from database_operations import file_sha256
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from query import team_lineups,native_player_rotation,native_team_finance,native_honors
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def text_prefix(raw):
    end=next((i for i in range(0,len(raw),2) if raw[i:i+2]==b'\0\0'),len(raw));return bytes(raw[:end]).decode('utf-16le').strip()
worker=json.loads((dest/'worker-result.json').read_bytes());assert worker['status']=='LINEUPS_UPGRADE_AND_CAPTURE_SUCCEEDED';terminal=json.loads((dest/'worker-terminal.json').read_bytes());assert terminal['worker_process_absent']
batch=json.loads((runtime/'lineups-refresh-29/refresh-report.json').read_bytes());assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['lineups'];entry=batch['sources'][0];unit=entry['unit']['unit_id'];source=runtime/'lineups-refresh-29'/entry['directory'];assert entry['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and entry['unit']['source_grade']=='LIVE_READ'
m=json.loads((source/'lineup-manifest.json').read_bytes());report=json.loads((source/'lineup-report.json').read_bytes());profile=json.loads((app/'lineup_native_profile.json').read_bytes());contexts=[json.loads(p.read_bytes())['epoch'] for p in (runtime/'lineups-refresh-29').glob('*-context.json')];assert len(contexts)==2 and contexts[0]==contexts[1] and contexts[0]['pid']==worker['pid']
before=json.loads((dest/'before.json').read_bytes());save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v20.sqlite';assert file_sha256(old)==worker['old_database_sha256']==before['database_sha256']=='c6e6befe0109c52d25e7eb3b35ebeee4a954df1ff5f782cff9ade9028f518309' and file_sha256(db)==worker['after_database_sha256'];assert binding['database_file']=='world-v21.sqlite' and {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in before['binding'].items() if k!='database_file'}
preserved={};deltas={};artifacts=0
with closing(connect(db,True)) as c:
    c.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[] and c.execute('PRAGMA user_version').fetchone()[0]==21
    for name in TABLES:
        columns=[r['name'] for r in c.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key
        if columns:
            clauses=['a.'+ident(column)+' IS NOT b.'+ident(column) for column in columns if not (name=='saves' and column=='schema_version')]
            assert c.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
            preserved[name]=c.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
        deltas[name]=c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    assert len(preserved)==88 and sum(preserved.values())==1382123
    annual=lambda prefix:sorted(tuple(r) for r in c.execute('SELECT unit_id,refresh_family,refresh_period_year FROM '+prefix+'capture_units JOIN '+prefix+'capture_runs USING(run_id) WHERE refresh_family IS NOT NULL'))
    assert annual('baseline.')==annual('')
    for table,count in entry['counts'].items():
        if table not in ('teams','field_gaps'):assert c.execute('SELECT count(*) FROM '+ident(table)+' WHERE unit_id=?',(unit,)).fetchone()[0]==count,table
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        path=source/Path(artifact['payload_ref']).name if artifact['payload_ref'].startswith(source.name+'/') else app/Path(artifact['payload_ref']).name
        assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifacts+=1
    prior=c.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0];successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==37
    source_players={r['source_player_index']:dict(r) for r in c.execute('SELECT * FROM native_player_sources WHERE unit_id=?',(unit,))}
pd=m['descriptors']['1'];td=m['descriptors']['8'];ranges=m['projection_ranges'];stride=m['projection_stride'];projection=(source/'player-detail-public-projections.bin').read_bytes();assert stride==102 and len(projection)==pd['count']*stride
raw_players={};roster={};pointer_map={int(k):v for k,v in m['core_team_pointer_map'].items()}
for address,tid in pointer_map.items():
    for slot,pointer in enumerate(struct.unpack('<25Q',(source/f'team-{tid}.roster.bin').read_bytes())):
        if not pointer:continue
        index,rem=divmod(pointer-pd['address'],1264);assert rem==0 and 0<=index<pd['count'] and index not in roster;roster[index]=(tid,slot)
identity_checks=0
for index in range(pd['count']):
    raw=bytearray(1264);at=0
    for a,b in ranges:raw[a:b]=projection[index*stride+at:index*stride+at+b-a];at+=b-a
    raw_players[index]=raw;p=source_players[index]
    assert p['native_unique_id_raw']==struct.unpack_from('<H',raw,244)[0] and p['preserved_id_raw']==struct.unpack_from('<I',raw,760)[0];identity_checks+=2
    try:name=(text_prefix(raw[40:80])+' '+text_prefix(raw[:40])).strip() or None
    except UnicodeDecodeError:name=None
    assert p['observed_name']==name;identity_checks+=1
    assert p['native_team_id']==pointer_map.get(struct.unpack_from('<Q',raw,96)[0]);identity_checks+=1
    assert (p['current_core_roster_status']=='CURRENT_CORE_ROSTER')==(index in roster)
seen=set();after=-1;pages=0;player_value_checks=0;force_counts=Counter();named={}
while True:
    page=native_player_rotation(db,current_roster_only=False,unit_id=unit,after_index=after,limit=100);pages+=1;assert page['source']['unit_id']==unit and page['source']['source_grade']=='LIVE_READ'
    for row in page['records']:
        index=row['source_player_index'];assert index not in seen;seen.add(index);raw=raw_players[index];playing=struct.unpack_from('<I',raw,248)[0]>>18&127;force=struct.unpack_from('<I',raw,764)[0]>>26&3;label=profile['enum_labels']['PLAYERDATA_FORCE_NON_STARTER_TYPE'].get(str(force),{}).get('label');assert row['playing_time_raw']==playing and row['force_non_starter_raw']==force and row['force_non_starter_label']==label;player_value_checks+=3;force_counts[str(force)]+=1
        if row['observed_name'] in ('Stephen Curry','LeBron James','Giannis Antetokounmpo') and row['current_core_roster_status']=='CURRENT_CORE_ROSTER':named[row['observed_name']]=row
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(source_players) and pages==(pd['count']+99)//100
core=set();after=-1
while True:
    page=native_player_rotation(db,unit_id=unit,after_index=after,limit=100);core.update(r['source_player_index'] for r in page['records'])
    if not page['has_more']:break
    after=page['next_after_index']
assert core==set(roster)
pointer_checks=0;matrix_checks=0;setting_checks=0;pointer_status=Counter();advanced_flags=Counter();global_slots=0;named_slots=0;queries=dest/'queries';queries.mkdir(exist_ok=True)
for team in m['teams']:
    tid=team['native_team_id'];key='team:native:'+str(tid);r=team_lineups(db,key,unit_id=unit,include_advanced=True);assert r['source']['unit_id']==r['game_mode']['unit_id']==unit and r['source']['source_grade']=='LIVE_READ';raw=bytearray(4696);part=(source/f'team-{tid}.lineup-projection.bin').read_bytes();at=0
    for a,b in m['team_projection_ranges']:raw[a:b]=part[at:at+b-a];at+=b-a
    assert at==len(part)==m['team_projection_bytes']
    for name,f in profile['team_flags'].items():
        value=int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit']&((1<<f['width'])-1);assert r['settings'][profile['team_flag_columns'][name]]==value;setting_checks+=1
    f=profile['team_counts']['NumberOfLineupPlayers'];assert r['settings']['number_of_lineup_players_raw']==int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit']&15;setting_checks+=1;advanced_flags[str(r['settings']['has_advanced_rotation_raw'])]+=1
    custom=profile['arrays']['CustomLineupName'];start=custom['binding']['offset']
    try:label=text_prefix(raw[start:start+24]) or None;status='OBSERVED_UTF16' if label else 'EMPTY_NATIVE_NAME'
    except UnicodeDecodeError:label=None;status='INVALID_UTF16_PREFIX'
    assert r['settings']['custom_lineup_name']==label and r['settings']['custom_name_status']==status and r['settings']['advanced_axis0_count']==48 and r['settings']['advanced_axis1_count']==5;setting_checks+=4
    for name,slots in {'LineupPlayer':r['global_slots'],**r['named_lineups']}.items():
        spec=profile['arrays'][name];assert len(slots)==spec['dimensions'][0]
        for slot in slots:
            pointer=struct.unpack_from('<Q',raw,spec['binding']['offset']+slot['slot_index']*8)[0];index,rem=divmod(pointer-pd['address'],1264)
            valid=pointer!=0 and 0<=index<pd['count'] and rem==0;expected=None if not valid else index
            assert slot['source_player_index']==expected and slot['source_player_id']==(None if expected is None else f'{unit}:player:{index}');pointer_checks+=1
            if not pointer:status='NULL_POINTER'
            elif not 0<=index<pd['count']:status='OUTSIDE_CURRENT_PLAYER_POOL'
            elif rem:status='MISALIGNED_PLAYER_POINTER'
            else:status='RECIPROCAL_CURRENT_TEAM_ROSTER' if index in roster and roster[index][0]==tid else 'CURRENT_POOL_REFERENT_WITHOUT_OWNER_ROSTER_MATCH'
            assert slot['pointer_status']==status;pointer_status[status]+=1
            if expected is not None:assert slot['player_id']==source_players[index]['player_id'] and slot['playing_time_raw']==struct.unpack_from('<I',raw_players[index],248)[0]>>18&127
            if name=='LineupPlayer':assert slot['planned_minutes'] is None and slot['role_code'] is None and slot['native_playing_time_raw']==slot['playing_time_raw'];global_slots+=1
            else:named_slots+=1
    spec=profile['arrays']['AdvancedRotationPlayerId'];assert r['advanced']['dimensions']==[48,5] and len(r['advanced']['slots'])==240
    for slot in r['advanced']['slots']:
        expected=struct.unpack_from('<H',raw,spec['binding']['offset']+slot['axis0_index']*10+slot['axis1_index']*2)[0];assert slot['native_player_id_raw']==expected and slot['namespace_status']=='UNVERIFIED_NATIVE_PLAYER_ID_NAMESPACE' and 'player_id' not in slot;matrix_checks+=1
    if tid in (0,8,31):write(queries/f'team-{tid}-lineups.json',r)
assert global_slots==390 and named_slots==1200 and matrix_checks==7200 and pointer_checks==1590
private_checks=0
for item in report['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
    if address+size>pd['address'] and address<pd['address']+pd['count']*1264:
        index,relative=divmod(address-pd['address'],1264);assert 0<=index<pd['count'] and any(a<=relative and relative+size<=b for a,b in ranges) and all(relative>=hi or relative+size<=lo for lo,hi in RESTRICTED_PLAYER_RANGES);private_checks+=1
assert private_checks==pd['count']*len(ranges)*3
assert query_at(db,prior,'team_lineups','team:native:0')['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'team_lineups','team:native:0',unit_id=unit)['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'native_player_rotation')['result']['status']=='NOT_OBSERVED'
assert native_team_finance(db)['source']['unit_id']=='native-finance:4e05cdc88e5ea0e9c3df9ed4' and native_honors(db,limit=1)['unit']['unit_id']=='native-honors:100325e0dd8283cf68d85b19'
for name,row in named.items():write(queries/(name.replace(' ','-').lower()+'-rotation.json'),native_player_rotation(db,unit_id=unit,source_index=row['source_player_index']))
write(queries/'before-lineups-as-of.json',query_at(db,prior,'team_lineups','team:native:0'))
def parts(path,prefix):
    rows=[]
    with path.open('rb') as src:
        while block:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(rows)+1).zfill(3));target.write_bytes(block);rows.append({'file':target.name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':rows}
native=runtime/'increment29-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('lineups-refresh-29','lineup-metadata-29','lineup-enum-29'):tar.add(runtime/name,arcname=name)
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment29-world-v21.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v21.sqlite.gz');snap.update(database_sha256=file_sha256(db),database_bytes=db.stat().st_size,save_id=binding['save_id'],schema_version=21);write(dest/'world-v21.snapshot.json',snap)
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==before['database_sha256']
audit={'status':'ACTUAL_NATIVE_LINEUPS_ROTATION_AND_V21_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'source_unit':unit,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'header_change':'saves.schema_version20->21 in copy only','after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':successful_units,'before_database_sha256':before['database_sha256'],'after_database_sha256':worker['after_database_sha256'],'process_epoch':contexts[0],'core_teams':30,'full_player_sources':pd['count'],'current_core_roster_sources':len(core),'player_query_pages':pages,'public_source_identity_checks':identity_checks,'player_rotation_value_comparisons':player_value_checks,'global_slots':global_slots,'named_lineup_slots':named_slots,'pointer_reference_comparisons':pointer_checks,'pointer_resolution_counts':dict(pointer_status),'advanced_matrix_comparisons':matrix_checks,'team_flag_count_comparisons':setting_checks,'advanced_flag_counts':dict(advanced_flags),'force_non_starter_counts':dict(force_counts),'private_free_player_interval_checks':private_checks,'public_player_projection_bytes':stride,'team_projection_bytes':m['team_projection_bytes'],'artifact_hashes_checked':artifacts,'annual_bucket_units_unchanged':True,'prior_finance_source_unchanged':True,'save_identity_unchanged':True,'old_database_retained_unchanged':True,'game_writes':False,'getter_invocations':0,'ui_capture_used':False,'annual_history_refreshed':False,'capacity_work_executed':False,'full_goal_complete':False,'limits':['Native PlayingTime UI minutes/units and actual lineup deployment are unproved; planned_minutes/role_code stay NULL.','Advanced array axes/strides are observed; clock/position labels and ID namespace are not inferred.','Current pointer/pool/roster aliases are not historical lifecycle certification.']}
write(dest/'actual-lineup-report.json',audit);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('inspect_coverage29.py','inspect_rotation_metadata.py','prepare_increment29.py','read_lineup_metadata29.py','start_lineup_metadata29.ps1','read_lineup_enum29.py','start_lineup_enum29.ps1','build_lineup_profile29.py','update_lineup_readme29.py','run_lineups_worker29.py','start_lineups_worker29.ps1','verify_lineups_terminal29.ps1',Path(__file__).name):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:audit[k] for k in ('status','prior_rows_preserved','after_total_rows','full_player_sources','current_core_roster_sources','global_slots','named_lineup_slots','advanced_matrix_comparisons','player_rotation_value_comparisons','private_free_player_interval_checks')}))
