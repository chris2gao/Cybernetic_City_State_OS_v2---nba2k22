"""Verify actual finance words, same-unit context, migration and complete history."""
from contextlib import closing
import gzip,hashlib,json,math,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment28';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident,VERSION
from database_operations import file_sha256
from live_world import read_binding,bound_database
from query import native_team_finance,team_card,native_honors
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
worker=json.loads((dest/'retry-worker-result.json').read_bytes());assert worker['status']=='FINANCE_UPGRADE_AND_CAPTURE_SUCCEEDED'
terminal=json.loads((dest/'retry-worker-terminal.json').read_bytes());assert terminal['worker_process_absent']
batch=json.loads((runtime/'finance-refresh-02/refresh-report.json').read_bytes());assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['finance'];entry=batch['sources'][0];unit=entry['unit']['unit_id'];source=runtime/'finance-refresh-02'/entry['directory'];assert entry['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and entry['unit']['source_grade']=='LIVE_READ'
m=json.loads((source/'finance-manifest.json').read_bytes());report=json.loads((source/'finance-report.json').read_bytes());profile=json.loads((app/'finance_native_profile.json').read_bytes());contexts=[json.loads(p.read_bytes())['epoch'] for p in (runtime/'finance-refresh-02').glob('*-context.json')];assert len(contexts)==2 and contexts[0]==contexts[1] and contexts[0]['pid']==worker['pid']
before=json.loads((dest/'before.json').read_bytes());save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v19.sqlite';assert file_sha256(old)==before['database_sha256']==worker['old_database_sha256']=='9153a9a517372006168e5f1c32d29aed3580e1b3da84dc7105ad010e9b2809d7';assert file_sha256(db)==worker['after_database_sha256']
assert binding['database_file']=='world-v20.sqlite' and {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in before['binding'].items() if k!='database_file'}
preserved={};deltas={};artifacts=0
with closing(connect(db,True)) as c:
    c.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[] and c.execute('PRAGMA user_version').fetchone()[0]==20
    for name in TABLES:
        columns=[r['name'] for r in c.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key
        if columns:
            clauses=['a.'+ident(column)+' IS NOT b.'+ident(column) for column in columns if not (name=='saves' and column=='schema_version')]
            assert c.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
            preserved[name]=c.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
        deltas[name]=c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    assert len(preserved)==87 and sum(preserved.values())==1381986
    before_annual=sorted(tuple(r) for r in c.execute('SELECT unit_id,refresh_family,refresh_period_year FROM baseline.capture_units JOIN baseline.capture_runs USING(run_id) WHERE refresh_family IS NOT NULL'));after_annual=sorted(tuple(r) for r in c.execute('SELECT unit_id,refresh_family,refresh_period_year FROM capture_units JOIN capture_runs USING(run_id) WHERE refresh_family IS NOT NULL'));assert before_annual==after_annual
    assert c.execute('SELECT count(*) FROM native_team_finance_observations WHERE unit_id=?',(unit,)).fetchone()[0]==30
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        path=source/Path(artifact['payload_ref']).name if artifact['payload_ref'].startswith(source.name+'/') else app/Path(artifact['payload_ref']).name
        assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifacts+=1
    prior=c.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0];successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==36
result=native_team_finance(db);assert result['source']['unit_id']==unit and result['source']['source_grade']=='LIVE_READ' and result['game_mode']['unit_id']==unit and len(result['records'])==30
rows={r['team_id']:r for r in result['records']};comparisons=0;negative=[];read_checks=0
for team in m['teams']:
    tid='team:native:'+str(team['native_team_id']);row=rows[tid];raw=bytearray(4696);at=0;part=(source/f'team-{team["pool_index"]}.projection.bin').read_bytes()
    for low,high in m['projection_ranges']:raw[low:high]=part[at:at+high-low];at+=high-low
    assert at==len(part)==m['projection_bytes_per_core_team']
    for name,spec in profile['scalars'].items():
        f=spec['binding'];column=spec['column'];word=int.from_bytes(raw[f['offset']:f['offset']+4],'little')
        if spec['primitive']=='float':
            value=struct.unpack_from('<f',raw,f['offset'])[0];assert row[column+'_word_u32']==word and row[column+'_real']==(value if math.isfinite(value) else None);comparisons+=2
        else:
            value=struct.unpack_from('<i' if spec['primitive']=='int' else '<I',raw,f['offset'])[0];assert row[column]==value;comparisons+=1
            if value<0:negative.append({'team_id':tid,'field':column,'signed_value':value,'raw_word_u32':word})
    for name,spec in profile['packed'].items():
        f=spec['binding'];value=(int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit'])&((1<<f['width'])-1);assert row[spec['column']]==value;comparisons+=1
        if 'enum' in spec:assert row[spec['column'].removesuffix('_raw')+'_label']==profile['enum_labels'][spec['enum']].get(str(value),{}).get('label');comparisons+=1
    assert row['observation_season_id']==result['game_mode']['season_id']
for item in report['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
    if item['label'].startswith('FINANCE_TEAM_PROJECTION:'):
        _,index,low,*tail=item['label'].split(':');address=m['team_descriptor']['address']+int(index)*4696+int(low)
        assert int(item['address'],16)==address and any(a==int(low) and b-a==size for a,b in m['projection_ranges']);read_checks+=1
assert read_checks==30*len(m['projection_ranges'])*2 and comparisons==1890
assert query_at(db,prior,'native_team_finance')['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'native_team_finance',unit_id=unit)['result']['status']=='NOT_OBSERVED'
assert native_honors(db,limit=1)['unit']['unit_id']=='native-honors:100325e0dd8283cf68d85b19'
queries=dest/'queries';queries.mkdir(exist_ok=True);write(queries/'all-core-team-finance.json',result);write(queries/'first-team-card.json',team_card(db,result['records'][0]['team_id']));write(queries/'before-finance-as-of.json',query_at(db,prior,'native_team_finance'))
def parts(path,prefix):
    rows=[]
    with path.open('rb') as src:
        while block:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(rows)+1).zfill(3));target.write_bytes(block);rows.append({'file':target.name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':rows}
native=runtime/'increment28-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('finance-refresh-01','finance-refresh-02','finance-metadata-01','finance-metadata-02','finance-dimensions-01'):tar.add(runtime/name,arcname=name)
    tar.add(runtime/'finance-metadata-labeled.json',arcname='finance-metadata-labeled.json')
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment28-world-v20.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v20.sqlite.gz');snap.update(database_sha256=file_sha256(db),database_bytes=db.stat().st_size,save_id=binding['save_id'],schema_version=20);write(dest/'world-v20.snapshot.json',snap)
assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==before['database_sha256']
audit={'status':'ACTUAL_TYPED_FINANCE_SOURCE_AND_V20_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'source_unit':unit,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'header_change':'saves.schema_version19->20 in copy only','after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':successful_units,'before_database_sha256':before['database_sha256'],'after_database_sha256':worker['after_database_sha256'],'process_epoch':contexts[0],'core_teams':30,'typed_field_comparisons':comparisons,'bounded_team_projection_read_checks':read_checks,'projection_bytes_per_core_team':m['projection_bytes_per_core_team'],'negative_signed_fields':negative,'artifact_hashes_checked':artifacts,'annual_bucket_units_unchanged':True,'save_identity_unchanged':True,'old_database_retained_unchanged':True,'ui_capture_status':'FAILED_NO_IMAGE_OR_ACCEPTANCE','game_writes':False,'getter_invocations':0,'player_struct_reads':0,'annual_history_refreshed':False,'capacity_work_executed':False,'full_goal_complete':False,'limits':['UI currency/scale and accounting duration remain unproved.','BudgetTier and IsLuxuryTaxTeam are Native fields, not a legal spending or cap-space decision.','No live financial transition or season completion has been observed.']}
write(dest/'actual-finance-report.json',audit);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment28.py','record_ui_capture_failure.py','read_finance_metadata.py','start_finance_metadata.ps1','label_finance_metadata.py','inspect_finance_block.py','read_finance_enums.py','start_finance_enums.ps1','build_finance_profile.py','update_finance_readme.py','run_finance_worker.py','start_finance_worker.ps1','verify_finance_worker_terminal.ps1','read_finance_dimensions.py','start_finance_dimensions.ps1','run_finance_retry.py','start_finance_retry.ps1','verify_finance_retry_terminal.ps1','repair_increment28_evidence_refs.py',Path(__file__).name):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:audit[k] for k in ('status','prior_rows_preserved','after_total_rows','core_teams','typed_field_comparisons','bounded_team_projection_read_checks','after_database_sha256')}))
