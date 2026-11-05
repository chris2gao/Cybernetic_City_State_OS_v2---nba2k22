"""Retain and compare actual settings words, typed facts, and v7 history."""
from contextlib import closing
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database
from settings_reader import settings_payload,decode_word,SLIDER_RVA
from query import settings_snapshot,rules_snapshot,export_jsonl

def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

dest=RUN/'06_执行/increment09';dest.mkdir(parents=True,exist_ok=False)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/settings-live-01';manifest=json.loads((capture/'settings-manifest.json').read_bytes())
report=json.loads((capture/'settings-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert hashlib.sha256((capture/name).read_bytes()).hexdigest()==digest
assert report['reader_sha256']==hashlib.sha256((APP/'settings_reader.py').read_bytes()).hexdigest()
trace=report['read_trace'];assert all(x['success'] for x in trace)
assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
def proof(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
table=(capture/'tunedata-saved.bin').read_bytes();roots={int(k):v for k,v in manifest['roots'].items()}
for start in range(0,len(table),1200):proof(roots[SLIDER_RVA]+start,table[start:start+1200])
for row in manifest['rows']:
    raw=(table[row['source_offset']:row['source_offset']+4] if row['pointer_rva']==SLIDER_RVA else
         (capture/f'word-{row["pointer_rva"]:x}-{row["source_offset"]:x}-{row["encoding"]}.bin').read_bytes())
    if row['pointer_rva']!=SLIDER_RVA:proof(roots[row['pointer_rva']]+row['source_offset'],raw)
    assert all(row[k]==v for k,v in decode_word(raw,row['encoding']).items())
assert manifest['season_year']==1900+((capture/'season-control.bin').read_bytes()[4]&127)
# Exact executed code and trace only request registered setting words, root
# pointers, and TEAM/TEAM_STATS context; there is no PLAYER/attribute request.
prefixes=('SETTINGS_ROOT:','SETTINGS_ROOT_RECHECK:','SETTINGS_TUNEDATA_SAVED:','SETTINGS_TUNEDATA_RECHECK:',
 'SETTINGS_WORD:','SETTINGS_WORD_RECHECK:','SETTINGS_ROSTER_POINTER','SETTINGS_TEAM_DESCRIPTOR','SETTINGS_TEAM_STATS_DESCRIPTOR',
 'SETTINGS_TEAM_CONTROL_ID','SETTINGS_TEAM_CONTROL_STATS_INDEX','SETTINGS_SEASON_CONTROL','SETTINGS_TEAM_CONTROL_ID_RECHECK',
 'SETTINGS_TEAM_CONTROL_INDEX_RECHECK','SETTINGS_SEASON_RECHECK','SETTINGS_ROSTER_RECHECK','SETTINGS_TEAM_DESCRIPTOR_RECHECK','SETTINGS_STATS_DESCRIPTOR_RECHECK')
for event in trace:
    assert event['operation'] in ('OpenProcess','ReadProcessMemory','CloseHandle')
    if event['operation']=='ReadProcessMemory':assert event['label'].startswith(prefixes) and event['requested_bytes']<=1200
assert not manifest['targets_defaults_applied'] and not manifest['game_writes'] and manifest['player_struct_reads']==0
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
payload=settings_payload(binding,manifest,[],report['observed_at'],unit.split(':',1)[1]);old_rows=compared=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    with closing(connect(save/'world-v7.sqlite',True)) as old:
        for table_name,spec in TABLES.items():
            if table_name=='saves':continue
            for before in old.execute('SELECT * FROM '+ident(table_name)):
                after=c.execute(f'SELECT * FROM {ident(table_name)} WHERE {ident(spec.key)}=?',(before[spec.key],)).fetchone()
                assert after is not None and all(after[k]==before[k] for k in before.keys()),table_name;old_rows+=1
    for table_name,rows in payload['facts'].items():
        spec=TABLES[table_name]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table_name}:{i}');actual=c.execute(f'SELECT * FROM {ident(table_name)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual is not None and all(actual[k]==v for k,v in expected.items()),(table_name,key);compared+=1
old_hash=hashlib.sha256((save/'world-v7.sqlite').read_bytes()).hexdigest()
assert old_hash==json.loads((RUN/'06_执行/increment08/planning_world_report.json').read_bytes())['world_sqlite_sha256']
snapshot=settings_snapshot(db);rules=rules_snapshot(db)
assert len(snapshot['settings'])==546 and len(rules['rules'])==35
write(queries/'settings-latest.json',snapshot);write(queries/'rules-latest.json',rules)
exports={table:export_jsonl(db,queries/(table+'.jsonl'),table)['rows'] for table in ('game_setting_observations','league_rule_observations')}
for path in queries.iterdir():
    content=path.read_text(encoding='utf-8').lower();assert not any(x in content for x in ('payload_ref','"address"','raw_player_hex','protected_value_ref'))
archives={}
for name in ('settings-probe-01','settings-live-01'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
for name in ('settings-pe-inspection.json','inspect_settings_pe.py'):
    path=RUN/'_runtime'/name
    if path.is_file():
        shutil.copyfile(path,sources/name);archives[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
raw=db.read_bytes()
with gzip.open(dest/'world-v8.sqlite.gz','wb') as f:f.write(raw)
summary={'status':'ACTUAL_SETTINGS_WORDS_AND_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
 'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
 'latest_unit':unit,'source_pid':report['pid'],'latest_counts':result['counts'],
 'old_schema7_rows_preserved':old_rows,'old_database_byte_hash_unchanged':True,'source_to_typed_rows_compared':compared,
 'source_reader_at_acquisition_sha256':report['reader_sha256'],'player_structs_requested':0,'game_writes':False,
 'observed_words_outside_registered_candidates':sum('OUTSIDE_REGISTERED' in r['registered_range_status'] for r in manifest['rows']),
 'native_type_metadata_status':manifest['native_type_metadata_status'],'export_rows':exports,
 'world_sqlite_sha256':hashlib.sha256(raw).hexdigest(),'independent_review':False,'full_goal_complete':False}
write(dest/'settings_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_settings_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text\n*.py -text\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','old_schema7_rows_preserved','source_to_typed_rows_compared','player_structs_requested','observed_words_outside_registered_candidates')}))
