"""Offline source-to-row, migration and role projection audit of actual org unit."""
from contextlib import closing
import gzip,hashlib,json,shutil,struct,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database
from organization_reader import verify_staff_assignment,coach_values,registered_fields,reconcile_team,organization_payload
from query import team_card,staff_card,export_jsonl
from readers import _module

def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

dest=RUN/'06_执行/increment06';dest.mkdir(parents=True,exist_ok=False);sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/organization-capture-01';manifest=json.loads((capture/'organization-manifest.json').read_bytes())
source_report=json.loads((capture/'organization-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in source_report['artifact_sha256'].items():assert hashlib.sha256((capture/name).read_bytes()).hexdigest()==digest
trace=source_report['read_trace'];assert all(x['success'] for x in trace);assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
def proof(address,raw,chunk=1200):
    for off in range(0,len(raw),chunk):
        data=raw[off:off+chunk];assert (address+off,len(data),hashlib.sha256(data).hexdigest()) in calls
games=(capture/'schedule-games.bin').read_bytes();decoder=_module('boxscore_decoder').BoxScoreDecoder
entries=[decoder.decode_game_header(games[i:i+60]) for i in range(0,len(games),60)]
season={'games':games,'manifest':{'entries':entries}}
teams={t['native_team_id']:t for t in manifest['teams']};uid=manifest['native_staff_uid_field']
for t in manifest['teams']:
    raw=(capture/f'team-{t["pool_index"]}.bin').read_bytes();proof(t['address'],raw)
    stats=next(s for s in manifest['team_totals'] if s['native_team_id']==t['native_team_id'])
    data=(capture/f'team-{t["pool_index"]}.stats.bin').read_bytes();proof(manifest['descriptors']['28']['address']+stats['stats_index']*62,data)
    actual=reconcile_team(data,season,t['native_team_id']);assert actual['values']==stats['values']
for s in manifest['staff']:
    raw=(capture/f'staff-{s["pool_index"]}.bin').read_bytes();proof(manifest['descriptors']['19']['address']+s['pool_index']*352,raw)
    assert verify_staff_assignment(raw,teams[s['native_team_id']]['address'],int(s['role_code']))==s['fields']
    assert int.from_bytes(raw[uid['offset']:uid['offset']+uid['size']],'little')==s['native_staff_id']
    if s['role_code']=='0':assert coach_values(raw)==s['coach_values']
for b in manifest['playbooks']:
    raw=(capture/f'playbook-{b["pool_index"]}.bin').read_bytes()
    assert list(struct.unpack_from('<68I',raw,0x58))==b['play_crc_slots']
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
payload=organization_payload(binding,manifest,[],source_report['observed_at'],unit.split(':',1)[1])
copied=0;facts=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    with closing(connect(save/'world-v4.sqlite',True)) as old:
        names={r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table,spec in TABLES.items():
            if table=='saves' or table not in names:continue
            for before in old.execute('SELECT * FROM '+ident(table)):
                after=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(before[spec.key],)).fetchone()
                assert after is not None and all(after[k]==before[k] for k in before.keys()),table;copied+=1
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}')
            actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual is not None and all(actual[k]==v for k,v in expected.items()),(table,key);facts+=1
    for table,count in result['counts'].items():
        if any(col.name=='unit_id' for col in TABLES[table].columns):assert c.execute(f'SELECT count(*) FROM {ident(table)} WHERE unit_id=?',(unit,)).fetchone()[0]==count
old_hash=hashlib.sha256((save/'world-v4.sqlite').read_bytes()).hexdigest()
assert old_hash==json.loads((RUN/'06_执行/increment05/season_world_report.json').read_bytes())['world_sqlite_sha256']
for tid in teams:
    card=team_card(db,'team:native:'+str(tid));assert len(card['assigned_staff'])==8 and len(card['playbook_slots'])==68
write(queries/'team-76ers.json',team_card(db,'team:native:0'));write(queries/'staff-doc-rivers.json',staff_card(db,'staff:native:70'))
exports={table:export_jsonl(db,queries/(table+'.jsonl'),table)['rows'] for table in
    ('team_finance_observations','team_season_totals','staff_team_assignments','team_tactic_settings')}
for path in queries.iterdir():
    content=path.read_text(encoding='utf-8').lower();assert not any(word in content for word in ('potential','payload_ref','raw_struct','"address"'))
archives={}
for name in ('organization-probe-01','organization-capture-01'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
raw=db.read_bytes()
with gzip.open(dest/'world-v5.sqlite.gz','wb') as f:f.write(raw)
summary={'status':'ORGANIZATION_SOURCE_QUERY_AND_MIGRATION_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'latest_unit':unit,'source_pid':source_report['pid'],'latest_counts':result['counts'],'native_metadata':result['native_metadata'],
    'source_to_typed_rows_compared':facts,'old_schema4_rows_preserved':copied,'old_database_byte_hash_unchanged':True,
    'source_code_at_acquisition_sha256':json.loads((capture/'executed_code_sha256.json').read_bytes()),
    'current_code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (APP/'organization_reader.py',APP/'schema_model.py',APP/'query.py')},
    'native_loaded_playbooks':len(manifest['playbooks']),'export_rows':exports,'world_sqlite_sha256':hashlib.sha256(raw).hexdigest(),
    'game_writes':False,'player_struct_reads':0,'independent_review':False,'full_goal_complete':False}
write(dest/'organization_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_organization_audit.py')
print(json.dumps({'status':summary['status'],'old_rows_preserved':copied,'source_rows_compared':facts,'teams':30,'staff':240,'tactics':30,'book_slots':2040}))
