"""Audit actual two-source acquisition, prior rows, raw totals and read traces."""
from collections import Counter
from contextlib import closing
import gzip,hashlib,json,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment24';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident,PROFILE
from database_operations import file_sha256
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from query import league_calendar,schedule,game_box,season_summary
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
worker=json.loads((runtime/'auxiliary-refresh-worker-report.json').read_bytes());assert worker['status']=='REQUESTED_SCHEDULE_AND_ORGANIZATION_REFRESH_FINISHED' and worker['binding_sha256_unchanged'] and worker['before_image_sha256_unchanged']
batch=worker['refresh'];assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['schedule','organization']
source=runtime/'organization-header-refresh-live-01';entries={s['family']:s for s in batch['sources']};paths={k:source/v['directory'] for k,v in entries.items()};units={k:v['unit']['unit_id'] for k,v in entries.items()}
assert all(s['status']=='ACQUIRED' and s['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and s['unit']['source_grade']=='LIVE_READ' for s in entries.values())
contexts=[json.loads(p.read_bytes())['epoch'] for p in source.glob('*-context.json')];assert len(contexts)==4 and all(c==contexts[0] for c in contexts)
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=runtime/'increment24-baseline.sqlite'
assert binding_hash==worker['before_binding_sha256'] and file_sha256(old)==worker['before_database_sha256'] and file_sha256(db)==worker['after_database_sha256']
org=json.loads((paths['organization']/'organization-manifest.json').read_bytes());sched=json.loads((paths['schedule']/'schedule-manifest.json').read_bytes())
assert org['native_boxes_read']==0 and org['final_headers_without_box_reads']==238 and org['schedule_read_policy']=='AUXILIARY_HEADER_ONLY_NO_BOX_REVALIDATION'
assert org['player_struct_reads']==org['player_potential_bytes_read']==0 and not list(paths['organization'].glob('schedule-box-*'))
assert org['schedule_index_relationship']['record_count']==1232 and all(v==1232 for v in org['schedule_index_relationship']['all_record_matches'].values())
assert sched['frozen_boxes_reused']==202 and sched['native_boxes_read']==36 and sched['record_count']==1232
games=(paths['organization']/'schedule-games.bin').read_bytes();aggregate={t['native_team_id']:{k:0 for k in ('wins','losses','points','opponent_points','games')} for t in org['teams']};status_counts=Counter()
for at in range(0,len(games),60):
    raw=games[at:at+60];status=int.from_bytes(raw[56:60],'little')>>11&3;status_counts[status]+=1
    if status!=2:continue
    home,away=struct.unpack_from('<HH',raw,12);home_score=sum(raw[44:48])+raw[52];away_score=sum(raw[48:52])+raw[53];assert home_score!=away_score
    for team,own,other in ((home,home_score,away_score),(away,away_score,home_score)):
        if team in aggregate:
            target=aggregate[team];target['games']+=1;target['wins']+=own>other;target['losses']+=own<other;target['points']+=own;target['opponent_points']+=other
assert dict(status_counts)=={2:238,0:994}
preserved={};deltas={};artifact_checks=0;comparisons=0
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert conn.execute('PRAGMA user_version').fetchone()[0]==18 and conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    for name, in conn.execute("SELECT name FROM baseline.sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols=[row['name'] for row in conn.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key
        clauses=['a.'+ident(c)+' IS NOT b.'+ident(c) for c in cols]
        assert conn.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
        preserved[name]=conn.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
    assert len(preserved)==86 and sum(preserved.values())==1361150
    for name in TABLES:deltas[name]=conn.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved[name]
    for family,entry in entries.items():
        unit=units[family]
        for table,count in entry['counts'].items():
            if 'unit_id' in [r['name'] for r in conn.execute('PRAGMA table_info('+ident(table)+')')]:assert conn.execute('SELECT count(*) FROM '+ident(table)+' WHERE unit_id=?',(unit,)).fetchone()[0]==count,(family,table)
        for artifact in conn.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
            if artifact['payload_ref'].startswith(paths[family].name+'/'):
                path=paths[family]/Path(artifact['payload_ref']).name;assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifact_checks+=1
    for team,totals in aggregate.items():
        row=conn.execute('SELECT * FROM team_season_totals WHERE unit_id=? AND team_id=?',(units['organization'],'team:native:'+str(team))).fetchone()
        native_team=next(t for t in org['teams'] if t['native_team_id']==team);pool=native_team['pool_index'];team_bytes=(paths['organization']/f'team-{pool}.bin').read_bytes()
        assert int.from_bytes(team_bytes[0xCA8:0xCAA],'little')==team and int.from_bytes(team_bytes[0xE80:0xE82],'little')==native_team['current_stats_index']
        raw=(paths['organization']/f'team-{pool}.stats.bin').read_bytes();assert len(raw)==62 and row['phase_code'] is None
        for native,column in (('w','wins'),('l','losses'),('points','points'),('pa','opponent_points')):
            field=next(f for f in PROFILE['fields']['TEAM_STATS'] if f['name']==native);width=field.get('bits',field.get('bytes',0)*8);start=field.get('start_bit',0);offset=field['offset'];size=(start+width+7)//8
            value=int.from_bytes(raw[offset:offset+size],'little')>>start&((1<<width)-1);assert value==row[column]==totals[column],{'team':team,'column':column,'field':field,'raw_value':value,'typed_value':row[column],'header_total':totals[column]};comparisons+=1
        assert totals['games']==row['wins']+row['losses']
    checks=[dict(row) for row in conn.execute('SELECT * FROM game_source_checks WHERE unit_id=?',(units['schedule'],))];assert len(checks)==1232
    reuse=next(c for c in checks if c['box_mode']=='REUSED_FROZEN_BOX');prior_time=conn.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0]
    total_units=conn.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert total_units==33
rows=schedule(db);assert len(rows)==1232 and all(row['calendar_unit_id']==units['schedule'] for row in rows)
calendar=league_calendar(db);assert calendar['records'][0]['unit_id']==units['organization'] and calendar['records'][0]['current_native_iso_date']=='2021-11-19'
assert query_at(db,prior_time,'league_calendar')['result']['records'][0]['unit_id'] not in units.values()
box=game_box(db,reuse['game_id']);assert box['selected_unit_id']==reuse['prior_full_unit_id'] and box['latest_header_check']['unit_id']==units['schedule']
summary=season_summary(db,'season:native-year:2022');assert all(r['totals']['phase_code'] is None for key in ('teams','players') for r in summary[key])
context=json.loads((paths['schedule']/'player-context.json').read_bytes());player_base=context['descriptors']['1']['address'];player_count=context['descriptors']['1']['count'];player_end=player_base+player_count*1264
trace_results={};private_checks=0
for family in entries:
    name='organization-report.json' if family=='organization' else 'acquisition-report.json';report=json.loads((paths[family]/name).read_bytes());box_reads=[];player_reads=0
    for item in report['read_trace']:
        assert item['success'] is True
        if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
        if item['operation']!='ReadProcessMemory':continue
        address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
        if 'FINAL_BOX' in item.get('label','') or 'BOX_RECHECK' in item.get('label',''):box_reads.append(item)
        if player_base<=address+size-1 and address<player_end:
            player_reads+=1
            for index in range(max(0,(address-player_base)//1264),min(player_count-1,(address+size-1-player_base)//1264)+1):
                for lo,hi in RESTRICTED_PLAYER_RANGES:assert address>=player_base+index*1264+hi or address+size<=player_base+index*1264+lo
            private_checks+=1
    trace_results[family]={'box_read_calls':len(box_reads),'box_read_bytes':sum(i['requested_bytes'] for i in box_reads),'player_interval_read_calls':player_reads}
assert trace_results['organization']=={'box_read_calls':0,'box_read_bytes':0,'player_interval_read_calls':0}
assert trace_results['schedule']['box_read_calls']==144 and trace_results['schedule']['box_read_bytes']==89280
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==worker['before_database_sha256']
examples=dest/'queries';examples.mkdir(exist_ok=True)
for name,value in [('calendar',calendar),('season-summary',summary),('frozen-game',box),('organization-team-header-reconciliation',aggregate)]:write(examples/(name+'.json'),value)
def parts(path,prefix):
    result=[]
    with path.open('rb') as src:
        while chunk:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(result)+1).zfill(3));target.write_bytes(chunk);result.append({'file':target.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':result}
native=runtime/'increment24-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    tar.add(source,arcname=source.name);tar.add(runtime/'current-stat-getter-candidates.json',arcname='static-current-stat-getter-candidates.json')
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment24-world-v18.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v18.sqlite.gz');snap.update({'database_sha256':worker['after_database_sha256'],'database_bytes':db.stat().st_size,'save_id':binding['save_id'],'schema_version':18});write(dest/'world-v18.snapshot.json',snap)
result={'status':'ACTUAL_AUXILIARY_HEADER_ONLY_READS_AND_PRIOR_FACTS_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':18,'tables':86,'columns':1376,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':total_units,'before_database_sha256':worker['before_database_sha256'],'after_database_sha256':worker['after_database_sha256'],'process_epoch':contexts[0],'source_units':units,'read_trace_results':trace_results,'current_native_date':'2021-11-19','game_status_counts':dict(status_counts),'games_checked':1232,'organization_final_headers_checked':238,'organization_teams_reconciled':len(aggregate),'raw_team_total_comparisons':comparisons,'source_artifact_hashes_checked':artifact_checks,'player_private_interval_checks':private_checks,'schedule_frozen_boxes_reused':202,'schedule_full_boxes_acquired':36,'save_binding_unchanged':True,'cumulative_phase_not_inferred':True,'game_writes':False,'capacity_work_executed':False,'scheduler_started':False,'full_goal_complete':False,'limits':['This run refreshes exactly schedule and organization; other eleven families retain their prior source times.','Unread organization Box bytes are not revalidated. Schedule reuse retains original Box source age.','Static stat-index getter candidates do not prove cumulative-stat phase or UI labels.']}
write(dest/'actual-auxiliary-report.json',result);write(dest/'worker-report.json',worker);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment24.py','capture_auxiliary_refresh.py','start_auxiliary_refresh.ps1','verify_actual_auxiliary.py','inspect_current_stat_getters.py'):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','prior_rows_preserved','after_total_rows','read_trace_results','raw_team_total_comparisons','source_artifact_hashes_checked')}))
