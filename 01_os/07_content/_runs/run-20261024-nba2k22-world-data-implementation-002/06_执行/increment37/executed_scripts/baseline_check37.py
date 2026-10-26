"""Bounded regular-season engineering closeout; no game process is opened."""
import hashlib,importlib,json,platform,shutil,sqlite3,subprocess,sys,time,zlib
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment37';out.mkdir(parents=True,exist_ok=True)
app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from schema_model import VERSION,TABLES,ident,schema_sql,dictionary
from refresh import SOURCES
from query import query_facts,export_filtered_facts,fact_fields
from observation_scope import query_at,observed_as_of
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from database_operations import file_sha256
save=run/'_runtime/world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args):return subprocess.run(['git',*args],capture_output=True,text=True,encoding='utf-8',check=True).stdout.strip()
head=git('rev-parse','HEAD');before=file_sha256(db);assert before=='f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218'
logs=out/'verification';logs.mkdir(exist_ok=True);operations={}
commands={'tests':[sys.executable,'-X','utf8','-m','unittest','discover','-s',str(app/'tests'),'-p','test_*.py'], 'sqlite_smoke':[sys.executable,'-X','utf8',str(app/'cli.py'),'smoke']}
for name,cmd in commands.items():
    start=time.monotonic()
    with (logs/(name+'.stdout.log')).open('w',encoding='utf-8') as stdout,(logs/(name+'.stderr.log')).open('w',encoding='utf-8') as stderr:r=subprocess.run(cmd,stdout=stdout,stderr=stderr)
    operations[name]={'command':cmd,'exit_code':r.returncode,'elapsed_seconds':round(time.monotonic()-start,2)};write(logs/'operations.json',operations);print(json.dumps({'operation':name,'exit_code':r.returncode}),flush=True);assert r.returncode==0,name
assert 'Ran 301 tests' in (logs/'tests.stderr.log').read_text(encoding='utf-8')
assert (app/'schema.sql').read_text(encoding='utf-8')==schema_sql();assert json.loads((app/'field_dictionary.json').read_bytes())==dictionary()
c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('BEGIN')
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchmany(1)
fresh=sqlite3.connect(':memory:');fresh.executescript(schema_sql())
schema_query="SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
actual_schema=[tuple(r) for r in c.execute(schema_query)];expected_schema=[tuple(r) for r in fresh.execute(schema_query)];assert actual_schema==expected_schema,'physical schema differs from generated current DDL';fresh.close()
physical_tables={r['name']:r['strict'] for r in c.execute('PRAGMA table_list') if r['name'] in TABLES};assert len(physical_tables)==100 and all(physical_tables.values())
table_inventory=[];field_matrix=[];domain_counts={}
for name,spec in TABLES.items():
    rows=c.execute('SELECT count(*) AS total,'+','.join('count('+ident(col.name)+') AS f'+str(i) for i,col in enumerate(spec.columns))+' FROM '+ident(name)).fetchone();count=rows['total']
    table_inventory.append({'table':name,'domain':spec.domain,'rows':count,'columns':len(spec.columns),'public':spec.public,'source':spec.source,'grain':spec.grain})
    d=domain_counts.setdefault(spec.domain,{'tables':0,'columns':0,'rows':0});d['tables']+=1;d['columns']+=len(spec.columns);d['rows']+=count
    for i,col in enumerate(spec.columns):field_matrix.append({'table':name,'column':col.name,'sqlite_type':col.kind,'non_null_rows':rows['f'+str(i)],'null_rows':count-rows['f'+str(i)],'source_declaration':col.source,'unit_declaration':col.unit,'role_visibility':col.visibility if spec.public else 'OWNER_ONLY','maturity_note':'Stored values and catalog declaration only; this count is not Native/UI/conversion validation'})
units=[dict(r) for r in c.execute('SELECT u.unit_id,u.source_key,u.observed_at,u.effective_at,u.completeness,u.layout_version,r.source_grade,r.refresh_family,r.refresh_period_year FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_status=\'success\' ORDER BY u.observed_at,u.unit_id')]
family_inventory=[]
for family,(module,function,key,annual) in SOURCES.items():
    assert callable(getattr(importlib.import_module(module),function));eligible=[u for u in units if u['source_key']==key];latest=max(eligible,key=lambda u:u['observed_at']) if eligible else None
    counts={}
    if latest:
        for name,spec in TABLES.items():
            if any(col.name=='unit_id' for col in spec.columns):
                count=c.execute('SELECT count(*) FROM '+ident(name)+' WHERE unit_id=?',(latest['unit_id'],)).fetchone()[0]
                if count:counts[name]=count
    family_inventory.append({'family':family,'reader_module':module,'capture_function':function,'source_key':key,'annual_family':annual,'successful_units':len(eligible),'latest_capture':latest,'latest_unit_table_rows':counts,'new_live_validation_in_closeout':False})
assert len(family_inventory)==20 and all(f['successful_units'] for f in family_inventory)
gaps=[dict(r) for r in c.execute('SELECT * FROM field_gaps ORDER BY gap_id')]
annual=[dict(r) for r in c.execute('SELECT refresh_family,refresh_period_year,count(*) AS successful_units FROM capture_runs r JOIN capture_units u USING(run_id) WHERE u.unit_status=\'success\' AND refresh_family IS NOT NULL GROUP BY refresh_family,refresh_period_year')]
assert len(annual)==4;assert c.execute('SELECT count(*) FROM player_restricted_observations').fetchone()[0]==0
assert tuple(RESTRICTED_PLAYER_RANGES)==((785,786),(880,882),(930,931),(1089,1090))
header=dict(c.execute('SELECT save_id,schema_version FROM saves').fetchone());assert header=={'save_id':'nba2k22_test_01','schema_version':24}
# Independent real-row filtering comparison, across all result pages.
punit='live-world:62052310fffb4ca792946781';filters=[{'column':'unit_id','op':'eq','value':punit},{'column':'games_played','op':'gte','value':10},{'column':'points','op':'gte','value':100}];columns=['player_id','games_played','points','phase_code']
expected=[dict(r) for r in c.execute('SELECT total_id,player_id,games_played,points,phase_code FROM player_season_totals WHERE unit_id=? AND games_played>=10 AND points>=100 ORDER BY total_id',(punit,))]
actual=[];cursor=None;pages=0
while True:
    page=query_facts(db,'player_season_totals',columns=columns,filters=filters,limit=17,cursor=cursor);actual.extend(page['records']);pages+=1;cursor=page['next_cursor']
    if cursor is None:break
assert [{'total_id':r['row_key'],**r['values']} for r in actual]==expected
assert all(r['provenance']['unit_id']==punit for r in actual)
export=export_filtered_facts(db,out/'actual-filtered-export','player_season_totals',columns=columns,filters=filters,max_rows=1000)
lines=[json.loads(line) for line in (out/'actual-filtered-export/facts.jsonl').read_text(encoding='utf-8').splitlines()];assert lines==actual and export['rows']==len(expected) and file_sha256(out/'actual-filtered-export/facts.jsonl')==export['sha256']
cutoff='2026-10-24T23:59:59Z';historic=query_at(db,cutoff,'query_facts','player_season_totals',columns=columns,filters=[{'column':'unit_id','op':'eq','value':punit}]);assert historic['result']['records']==[]
write(out/'actual-filtered-query.json',{'filters':filters,'columns':columns,'pages':pages,'rows':actual})
artifact=c.execute('SELECT payload_ref,sha256,byte_count FROM source_artifacts LIMIT 1').fetchone();write(out/'artifact-ledger-shape.json',{'fields':list(artifact.keys()) if artifact else [],'scope':'Full source artifact rows remain in retained owner database; this closeout does not re-read Native values or certify every external raw file'})
c.close()
# Verify the already published v24 snapshot stream, without capacity experiments.
snapdir=run/'06_执行/increment34';manifest=json.loads((snapdir/'world-v24.snapshot.json').read_bytes());decoder=zlib.decompressobj(31);compressed=hashlib.sha256();decoded=hashlib.sha256();decoded_bytes=0
for part in manifest['parts']:
    path=snapdir/part['file'];assert path.stat().st_size==part['bytes'] and file_sha256(path)==part['sha256']
    with path.open('rb') as stream:
        while block:=stream.read(4*1024*1024):
            compressed.update(block);pending=block
            while pending:
                data=decoder.decompress(pending,4*1024*1024);decoded.update(data);decoded_bytes+=len(data);pending=decoder.unconsumed_tail
data=decoder.flush();decoded.update(data);decoded_bytes+=len(data)
assert decoder.eof and not decoder.unused_data and compressed.hexdigest()==manifest['stream_sha256'] and decoded.hexdigest()==manifest['database_sha256']==before and decoded_bytes==db.stat().st_size
help_checks={}
for command in ('refresh-world','reconnect-game','query-facts','export-filtered','standings','player-leaderboard','backup-facts','restore-facts'):
    result=subprocess.run([sys.executable,'-X','utf8',str(app/'cli.py'),command,'--help'],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,command;help_checks[command]=result.returncode
after=file_sha256(db);assert before==after
code_paths=[p for p in app.iterdir() if p.suffix in ('.py','.sql','.json')];code_hashes={p.name:file_sha256(p) for p in code_paths}
for name,digest in code_hashes.items():
    blob=subprocess.run(['git','show',head+':'+(app/name).relative_to(root).as_posix()],capture_output=True,check=True).stdout;assert hashlib.sha256(blob).hexdigest()==digest,name
write(out/'source-coverage.json',{'reader_families':family_inventory,'successful_units':units,'annual_buckets':annual,'source_local_gaps':gaps,'gap_interpretation':'Source-local historical declarations may be superseded by later families; unresolved items require explicit semantic assessment, not blind gap counting'})
write(out/'table-inventory.json',{'schema_version':VERSION,'tables':table_inventory,'domains':domain_counts})
write(out/'field-maturity.json',{'schema_version':VERSION,'note':'Non-NULL is storage evidence, not UI/Native semantic proof. Use source-specific reader profiles and executed increment evidence; unknown units remain unknown.','fields':field_matrix})
write(out/'snapshot-check.json',{'manifest_ref':'06_执行/increment34/world-v24.snapshot.json','parts_verified':len(manifest['parts']),'compressed_sha256':compressed.hexdigest(),'decoded_sha256':decoded.hexdigest(),'decoded_bytes':decoded_bytes,'matches_bound_database':True})
report={'status':'REGULAR_SEASON_ENGINEERING_BASELINE_CHECK_PASSED_PENDING_INDEPENDENT_REVIEW','candidate_code_head':head,'environment':{'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'platform':platform.system()},'tests':301,'code_sha256':code_hashes,'database_sha256_before':before,'database_sha256_after':after,'binding_sha256':binding_hash,'save_id':binding['save_id'],'native_save_filename':binding['native_save_filename'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'rows':sum(t['rows'] for t in table_inventory),'successful_units':len(units),'registered_reader_families':len(SOURCES),'annual_families':len(annual),'schema_dictionary_and_physical_ddl_equal':True,'strict_tables':len(physical_tables),'integrity':'ok','foreign_key_errors':0,'real_filtered_rows_compared':len(expected),'query_pages':pages,'filtered_export_sha256_verified':True,'cli_help_checks':help_checks,'snapshot_stream_verified':True,'raw_artifact_revalidation':'Not exhaustive; retained source ledger and existing per-increment archive checks remain evidence','new_live_game_reads':0,'new_capture_units':0,'database_writes':0,'computer_use_used':False,'new_native_research':False,'capacity_work_executed':False,'game_writes':False,'full_lifecycle_acceptance':False,'full_underlying_system_complete':False,'independent_review':'NOT_RUN','master_integration':'NOT_PERFORMED'}
write(out/'verification-report.json',report);(out/'executed_scripts').mkdir(exist_ok=True)
for name in ('baseline_check37.py','preflight37.py'):shutil.copyfile(run/'_runtime'/name,out/'executed_scripts'/name)
print(json.dumps({k:v for k,v in report.items() if k not in ('code_sha256','cli_help_checks')},ensure_ascii=False),flush=True)
