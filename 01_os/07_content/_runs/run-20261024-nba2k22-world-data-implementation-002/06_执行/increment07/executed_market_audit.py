"""Offline Native market source, typed facts, hidden-byte and migration checks."""
from bisect import bisect_left
from contextlib import closing
import gzip,hashlib,json,shutil,struct,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from market_reader import market_payload,draft_codec,DRAFT_PROFILE,decode_waived_record,decode_prospect_slot
from live_world import read_binding,bound_database,POTENTIAL
from query import market_snapshot,export_jsonl

def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

dest=RUN/'06_执行/increment07';dest.mkdir(parents=True,exist_ok=False);sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/market-capture-01';manifest=json.loads((capture/'market-manifest.json').read_bytes())
report=json.loads((capture/'market-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert hashlib.sha256((capture/name).read_bytes()).hexdigest()==digest
trace=report['read_trace'];assert all(x['success'] for x in trace);assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
excluded=sorted(d['address']+i*1264+POTENTIAL for slot in ('1','4') for d in [manifest['descriptors'][slot]] for i in range(d['count']))
for x in trace:
    if x['operation']!='ReadProcessMemory':continue
    start=int(x['address'],16);end=start+x['requested_bytes'];i=bisect_left(excluded,start)
    assert i==len(excluded) or excluded[i]>=end
def proof(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
team_ids={t['address']:t['native_team_id'] for t in manifest['teams']}
for w in manifest['waived_salaries']:
    raw=(capture/f'waived-{w["source_row_index"]}.bin').read_bytes();proof(manifest['descriptors']['61']['address']+w['source_row_index']*136,raw)
    assert decode_waived_record(raw,w['source_row_index'],team_ids)==w
for p in manifest['prospects']:
    raw=(capture/f'prospect-{p["source_row_index"]}.public.bin').read_bytes();assert raw[POTENTIAL]==0
    address=manifest['descriptors']['4']['address']+p['source_row_index']*1264
    proof(address,raw[:POTENTIAL]);proof(address+POTENTIAL+1,raw[POTENTIAL+1:])
    assert decode_prospect_slot(raw,p['source_row_index'])==p
    assert p['decode_status']=='UNINITIALIZED_NO_NAME'
class RecordedMemory:
    base_address=0x140000000
    def read_bytes(self,address,size):
        for i,item in enumerate(DRAFT_PROFILE['code_evidence']):
            if address==self.base_address+item['module_rva']:
                raw=(capture/f'draft-code-{i}.bin').read_bytes();proof(address,raw);return raw
        index,rem=divmod(address-manifest['descriptors']['42']['address'],32)
        assert not rem and 0<=index<manifest['descriptors']['42']['count'] and size==32
        raw=(capture/f'draft-asset-{index}.bin').read_bytes();proof(address,raw);return raw
observations,next_year=draft_codec().read_assets(RecordedMemory(),{'draft_assets':manifest['descriptors']['42']},team_ids,manifest['season_year'])
assert next_year==2022 and sum(r['mapping_status']=='VERIFIED_SIMPLE_FUTURE_PICK' for _,r,_ in observations)==300
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
payload=market_payload(binding,manifest,[],report['observed_at'],unit.split(':',1)[1]);old_rows=compared=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    with closing(connect(save/'world-v5.sqlite',True)) as old:
        names={r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table,spec in TABLES.items():
            if table=='saves' or table not in names:continue
            for before in old.execute('SELECT * FROM '+ident(table)):
                after=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(before[spec.key],)).fetchone()
                assert after is not None and all(after[k]==before[k] for k in before.keys()),table;old_rows+=1
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual is not None and all(actual[k]==v for k,v in expected.items()),(table,key);compared+=1
    for table in ('draft_prospects','draft_results','market_state_observations'):
        assert c.execute('SELECT count(*) FROM '+ident(table)).fetchone()[0]==0
old_hash=hashlib.sha256((save/'world-v5.sqlite').read_bytes()).hexdigest()
assert old_hash==json.loads((RUN/'06_执行/increment06/organization_world_report.json').read_bytes())['world_sqlite_sha256']
snapshot=market_snapshot(db);assert len(snapshot['future_picks'])==300 and len(snapshot['draft_pool_slots'])==90
assert all(p['protection_status']=='UNKNOWN' and p['swap_status']=='UNKNOWN' for p in snapshot['future_picks'])
assert sum(w['owner_mapping_status']=='CORE_TEAM_POINTER' for w in snapshot['waived_salary_source_observations'])==32
write(queries/'market-latest.json',snapshot);write(queries/'market-team-celtics.json',market_snapshot(db,team_id='team:native:5'))
exports={table:export_jsonl(db,queries/(table+'.jsonl'),table)['rows'] for table in ('draft_pick_ownerships','waived_salary_observations','draft_pool_slot_observations')}
for path in queries.iterdir():
    text=path.read_text(encoding='utf-8').lower();assert not any(x in text for x in ('potential','payload_ref','"address"','raw_struct'))
archives={}
for name in ('market-probe-01','market-capture-01'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
raw=db.read_bytes()
with gzip.open(dest/'world-v6.sqlite.gz','wb') as f:f.write(raw)
summary={'status':'NATIVE_MARKET_SOURCE_AND_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'latest_unit':unit,'source_pid':report['pid'],'latest_counts':result['counts'],'future_pick_years':[2022,2023,2024,2025,2026],
    'old_schema5_rows_preserved':old_rows,'old_database_byte_hash_unchanged':True,'source_to_typed_rows_compared':compared,
    'source_code_at_acquisition_sha256':json.loads((capture/'executed_code_sha256.json').read_bytes()),
    'potential_bytes_requested':0,'core_owner_waived_records':32,'unnamed_prospect_slots':90,'actual_named_prospects':0,
    'export_rows':exports,'world_sqlite_sha256':hashlib.sha256(raw).hexdigest(),'game_writes':False,'independent_review':False,'full_goal_complete':False}
write(dest/'market_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_market_audit.py')
print(json.dumps({k:summary[k] for k in ('status','old_schema5_rows_preserved','source_to_typed_rows_compared','core_owner_waived_records','unnamed_prospect_slots','actual_named_prospects')}))
