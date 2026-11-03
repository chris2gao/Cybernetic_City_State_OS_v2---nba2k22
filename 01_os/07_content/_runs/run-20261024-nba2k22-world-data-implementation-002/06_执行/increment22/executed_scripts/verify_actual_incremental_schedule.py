"""Prove actual Box read avoidance, preserved source age and v16 copy retention."""
from collections import Counter
from contextlib import closing
import gzip,hashlib,json,shutil,sys,tarfile
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident
from database_operations import file_sha256
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from query import game_box,season_summary,player_card
from observation_scope import query_at
from schedule_reader import frozen_game_sources
run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');runtime=run/'_runtime';dest=run/'06_执行/increment22';dest.mkdir(parents=True,exist_ok=True);examples=dest/'queries';examples.mkdir(exist_ok=True)
worker=json.loads((runtime/'incremental-v17-worker-report.json').read_bytes());assert worker['status']=='NATIVE_V17_COPY_UPGRADE_AND_INCREMENTAL_SCHEDULE_FINISHED',worker
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v16.sqlite';seed=worker['seed']['unit_id'];incremental=worker['incremental']['unit_id']
assert file_sha256(old)==worker['before_database_sha256']=='5862abf394bf831b6f37cfd0f52c274f7d05bbfd41701f22761228505e93761c' and file_sha256(db)==worker['after_database_sha256']
old_binding=json.loads((save/'save.before-v17.json').read_bytes());assert {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in old_binding.items() if k!='database_file'}
assert binding['database_file']=='world-v17.sqlite' and worker['context_before']['epoch']==worker['context_after']['epoch']
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
preserved={};deltas={};source_counts={};api_metrics={};private_checks=0;source_hash_checks=0
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    old_names=[r[0] for r in conn.execute("SELECT name FROM baseline.sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    for name in old_names:
        cols=[r['name'] for r in conn.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key
        comparisons=[c for c in cols if (name,c)!=('saves','schema_version')]
        different=' OR '.join('a.'+ident(c)+' IS NOT b.'+ident(c) for c in comparisons)
        mismatches=conn.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+different).fetchone()[0];assert mismatches==0,name
        preserved[name]=conn.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
    assert conn.execute('SELECT schema_version FROM saves').fetchone()[0]==17
    for name in TABLES:deltas[name]=conn.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    for label,unit in [('seed',seed),('incremental',incremental)]:
        source_counts[label]={r[0]:r[1] for r in conn.execute('SELECT box_mode,count(*) FROM game_source_checks WHERE unit_id=? GROUP BY box_mode',(unit,))}
    assert source_counts['seed'].get('REUSED_FROZEN_BOX',0)==0
    checks=[dict(r) for r in conn.execute('SELECT * FROM game_source_checks WHERE unit_id=?',(incremental,))]
    reused=[r for r in checks if r['box_mode']=='REUSED_FROZEN_BOX'];full=[r for r in checks if r['box_mode']=='FULL_NATIVE_BOX'];future=[r for r in checks if r['box_mode']=='HEADER_ONLY_NOT_FINAL']
    assert len(reused)>0 and len(reused)+len(full)==source_counts['seed']['FULL_NATIVE_BOX']
    for check in reused:
        assert check['prior_full_unit_id']==seed and check['box_sha256'] is None
        for table in ('game_state_observations','game_period_scores','player_game_boxes','team_game_boxes','native_box_observations'):
            assert conn.execute('SELECT count(*) FROM '+table+' WHERE game_id=? AND unit_id=?',(check['game_id'],incremental)).fetchone()[0]==0,(check['game_id'],table)
    state_counts={unit:conn.execute('SELECT count(*) FROM game_state_observations WHERE unit_id=?',(unit,)).fetchone()[0] for unit in (seed,incremental)}
    box_counts={unit:conn.execute('SELECT count(*) FROM native_box_observations WHERE unit_id=?',(unit,)).fetchone()[0] for unit in (seed,incremental)}
    assert state_counts[incremental]==len(full)+len(future)
for label,unit,folder_name in [('seed',seed,'schedule-v17-seed'),('incremental',incremental,'schedule-v17-incremental')]:
    folder=runtime/folder_name;report=json.loads((folder/'acquisition-report.json').read_bytes());manifest=json.loads((folder/'schedule-manifest.json').read_bytes());context=json.loads((folder/'player-context.json').read_bytes());trace=report['read_trace'];base=context['descriptors']['1']['address'];count=context['descriptors']['1']['count'];end=base+count*1264
    box_reads=[r for r in trace if r.get('operation')=='ReadProcessMemory' and (r['label'].startswith('SCHEDULE_FINAL_BOX:') or r['label'].startswith('SCHEDULE_BOX_RECHECK:'))]
    assert not any(r.get('label','').startswith(('ONE_GAME_PARTICIPANT_STATBANK','ONE_SEASON_GAME','WORLD_BOX_RECHECK')) for r in trace)
    skipped_indices={e['pool_index'] for e in manifest['entries'] if e.get('prior_full_unit_id') is not None}
    assert not any(int(r['label'].split(':')[1]) in skipped_indices for r in box_reads)
    api_metrics[label]={'pid':report['pid'],'box_read_calls':len(box_reads),'box_read_bytes':sum(r['requested_bytes'] for r in box_reads),'distinct_box_indices_read':len({int(r['label'].split(':')[1]) for r in box_reads}),'frozen_boxes_skipped':len(skipped_indices),'historical_box_anchor_reads':0}
    assert len(box_reads)==4*manifest['native_boxes_read'] and len(skipped_indices)==manifest['frozen_boxes_reused']
    for item in trace:
        assert item['success'] is True
        if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
        if item['operation']!='ReadProcessMemory':continue
        address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
        if address>=end or address+size<=base:continue
        for index in range(max(0,(address-base)//1264),min(count-1,(address+size-1-base)//1264)+1):
            for low,high in RESTRICTED_PLAYER_RANGES:assert address>=base+index*1264+high or address+size<=base+index*1264+low
        private_checks+=1
    with closing(connect(db,True)) as conn:
        for artifact in conn.execute('SELECT sha256,payload_ref,byte_count FROM source_artifacts WHERE unit_id=?',(unit,)):
            prefix=folder_name+'/'
            if not artifact['payload_ref'].startswith(prefix):continue
            path=folder/artifact['payload_ref'][len(prefix):];assert path.is_file() and file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];source_hash_checks+=1
        assert context['game_season_year']==2022
        totals=[dict(r) for r in conn.execute('SELECT * FROM player_season_totals WHERE unit_id=?',(unit,))];source_years={c['totals']['season_year'] for link in context['player_links'] if link['selected_pool_index'] is not None for c in link['candidates'] if c['pool_index']==link['selected_pool_index'] and 'totals' in c}
        assert {r['season_id'] for r in totals}<={'season:native-year:2022'}
    write(dest/(label+'-source-summary.json'),{'manifest_counts':{k:manifest[k] for k in ('record_count','status_counts','native_boxes_read','frozen_boxes_reused')},'context_year':context['game_season_year'],'observed_native_total_years':sorted(source_years),'current_total_rows':len(totals),'api_metrics':api_metrics[label]})
assert api_metrics['incremental']['box_read_calls']<api_metrics['seed']['box_read_calls']
comparisons=[]
with closing(connect(db,True)) as conn:seed_time=conn.execute('SELECT observed_at FROM capture_units WHERE unit_id=?',(seed,)).fetchone()[0]
for check in checks:
    value=game_box(db,check['game_id']);expected=seed if check['box_mode']=='REUSED_FROZEN_BOX' else incremental
    assert value['selected_unit_id']==expected and value['latest_header_check']['unit_id']==incremental
    for table in ('states','period_scores','player_boxes','team_boxes'):assert all(r['unit_id']==expected for r in value[table])
    comparisons.append({'game_id':check['game_id'],'mode':check['box_mode'],'selected_box_unit':expected,'latest_header_unit':incremental})
sample=reused[0]['game_id'];current=game_box(db,sample);historical=query_at(db,seed_time,'game_box',sample)['result'];assert current['capture']==historical['capture'] and current['player_boxes']==historical['player_boxes'] and historical['latest_header_check']['unit_id']==seed
write(examples/'frozen-game-current.json',current);write(examples/'frozen-game-at-seed.json',historical);write(examples/'curry-current.json',player_card(db,'player:native:1612'));write(examples/'season-current.json',season_summary(db,'season:native-year:2022'))
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==worker['before_database_sha256']
def retain_parts(path,prefix):
    parts=[]
    with path.open('rb') as stream:
        while block:=stream.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(parts)+1).zfill(3));target.write_bytes(block);parts.append({'file':target.name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':parts}
native=runtime/'increment22-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('schedule-v17-seed','schedule-v17-incremental'):tar.add(runtime/name,arcname=name)
write(dest/'native-sources.archive.json',retain_parts(native,'native-sources.tar.gz'))
snapshot=runtime/'increment22-world-v17.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snapshot_manifest=retain_parts(snapshot,'world-v17.sqlite.gz');snapshot_manifest.update({'database_sha256':worker['after_database_sha256'],'database_bytes':db.stat().st_size,'save_id':'nba2k22_test_01','schema_version':17});write(dest/'world-v17.snapshot.json',snapshot_manifest)
result={'status':'ACTUAL_INCREMENTAL_NATIVE_BOX_READ_AVOIDANCE_AND_COPY_UPGRADE_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':17,'tables':85,'columns':1315,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'new_rows_by_table':deltas,'after_total_rows':sum(preserved.values())+sum(deltas.values()),
    'before_database_sha256_unchanged':worker['before_database_sha256'],'after_database_sha256':worker['after_database_sha256'],'save_identity_preserved':True,'old_database_retained':True,'process_context':worker['context_after']['epoch'],'source_counts':source_counts,'actual_native_box_read_metrics':api_metrics,'source_artifact_hashes_checked':source_hash_checks,'player_private_interval_read_checks':private_checks,
    'all_game_query_checks':len(comparisons),'box_source_time_preserved_on_reuse':True,'unit_box_counts':box_counts,'unit_state_counts':state_counts,'game_writes':False,'capacity_work_executed':False,'scheduler_started':False,'full_goal_complete':False,
    'limits':['A matching header reuses a prior frozen source; unread Native Box equality is not claimed. Explicit --recheck-frozen remains available.','Incomplete canonical mappings require full Box acquisition and remain explicit.','Copy migration changes only the schema-version header and adds typed source-check metadata; original facts are retained.','Native UI/calendar/identity lifecycle gaps and full independent/Human acceptance remain open.']}
write(dest/'actual-incremental-report.json',result);write(dest/'all-game-query-checks.json',comparisons);write(dest/'worker-report.json',worker)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in (Path(__file__).name,'capture_incremental_schedule_v17.py','start_incremental_schedule_v17.ps1'):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','prior_rows_preserved','after_total_rows','source_counts','actual_native_box_read_metrics','all_game_query_checks','source_artifact_hashes_checked','player_private_interval_read_checks')}))
