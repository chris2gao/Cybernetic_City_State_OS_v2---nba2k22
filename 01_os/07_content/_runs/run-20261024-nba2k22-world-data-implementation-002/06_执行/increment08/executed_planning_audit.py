"""Offline audit of actual stored plan/training fields and preserved history."""
from bisect import bisect_left,bisect_right
from contextlib import closing
import gzip,hashlib,json,shutil,struct,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database,POTENTIAL
from family_codec import decode_fixed_utf16
from planning_reader import planning_payload,decode_plan,training_player_values,training_team_values,TRAINING_PROFILE,COACH_PROFILE
from query import planning_snapshot,gameplan_card,export_jsonl

def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

dest=RUN/'06_执行/increment08';dest.mkdir(parents=True,exist_ok=False);sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/planning-capture-01';manifest=json.loads((capture/'planning-manifest.json').read_bytes())
report=json.loads((capture/'planning-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert hashlib.sha256((capture/name).read_bytes()).hexdigest()==digest
trace=report['read_trace'];assert all(x['success'] for x in trace);assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
def proof(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
pd=manifest['descriptors']['1'];excluded=[pd['address']+i*1264+POTENTIAL for i in range(pd['count'])]
pt=TRAINING_PROFILE['structures']['player_training'];training=manifest['training_root'];native=COACH_PROFILE['native']
history=[(training+int(pt['array_offset'],16)+i*pt['stride']+0x125,training+int(pt['array_offset'],16)+i*pt['stride']+0x318) for i in range(pt['max_players'])]
badge_ranges=[]
for r in manifest['mentor_relations']:
    manager=next(m for m in manifest['mentor_managers'] if m['native_team_id']==r['native_team_id'])
    start=manifest['franchise_root']+native['franchise_teams_offset']+manager['franchise_slot']*native['franchise_team_stride']+0x132A8+12+r['source_slot_index']*204
    badge_ranges.append((start+24,start+204))
badge_ranges.sort();badge_starts=[a for a,b in badge_ranges];history_starts=[a for a,b in history]
for x in trace:
    if x['operation']!='ReadProcessMemory':continue
    start=int(x['address'],16);end=start+x['requested_bytes'];i=bisect_left(excluded,start)
    assert i==len(excluded) or excluded[i]>=end
    for intervals,starts in ((history,history_starts),(badge_ranges,badge_starts)):
        j=bisect_right(starts,end-1)-1
        assert j<0 or intervals[j][1]<=start
teams={t['native_team_id']:t for t in manifest['teams']}
for p in manifest['players']:
    address=pd['address']+p['pool_index']*1264
    name=(capture/f'player-{p["pool_index"]}.name.bin').read_bytes();rawid=(capture/f'player-{p["pool_index"]}.id.bin').read_bytes();owner=(capture/f'player-{p["pool_index"]}.team.bin').read_bytes()
    proof(address,name);proof(address+0x2F8,rawid);proof(address+0x60,owner)
    assert int.from_bytes(rawid,'little')==p['native_player_id'] and int.from_bytes(owner,'little')==teams[p['native_team_id']]['address']
    assert (decode_fixed_utf16(name[40:80])+' '+decode_fixed_utf16(name[:40])).strip()==p['display_name']
    roster=(capture/f'team-{p["native_team_id"]}.roster.bin').read_bytes();assert struct.unpack_from('<Q',roster,p['roster_slot']*8)[0]==address
for p in manifest['plans']:
    raw=(capture/f'gameplan-{p["native_team_id"]}-{p["source_slot_index"]}.bin').read_bytes()
    address=manifest['franchise_root']+native['franchise_teams_offset']+p['franchise_slot']*native['franchise_team_stride']+native['gameplan_start']+p['source_slot_index']*880
    proof(address,raw);decoded=decode_plan(raw,manifest['defense_catalog'])
    assert all(decoded[k]==p[k] for k in ('header','rotations','defenses'))
ids=(capture/'training-id-projection.bin').read_bytes();flags=(capture/'training-flags-projection.bin').read_bytes()
for p in manifest['player_training_slots']:
    i=p['source_slot_index'];rawid=ids[i*4:i*4+4];raw=flags[i*4:i*4+4]
    address=training+int(pt['array_offset'],16)+i*pt['stride'];proof(address,rawid);proof(address+0x318,raw)
    assert int.from_bytes(rawid,'little')==p['native_player_id_raw'] and training_player_values(raw)==p['values']
for t in manifest['team_training']:
    raw=(capture/f'team-training-{t["native_team_id"]}.bin').read_bytes();proof(training+t['franchise_slot']*88,raw);assert training_team_values(raw)==t['values']
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
payload=planning_payload(binding,manifest,[],report['observed_at'],unit.split(':',1)[1]);old_rows=compared=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    with closing(connect(save/'world-v6.sqlite',True)) as old:
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
    assert c.execute('SELECT count(*) FROM gameplan_observations WHERE unit_id=? AND is_in_use_raw=1',(unit,)).fetchone()[0]==1
old_hash=hashlib.sha256((save/'world-v6.sqlite').read_bytes()).hexdigest()
assert old_hash==json.loads((RUN/'06_执行/increment07/market_world_report.json').read_bytes())['world_sqlite_sha256']
snapshot=planning_snapshot(db);assert len(snapshot['families']['gameplan_observations'])==870
write(queries/'planning-latest.json',snapshot);write(queries/'gameplan-nyk-phi.json',gameplan_card(db,'team:native:20','team:native:0'))
exports={table:export_jsonl(db,queries/(table+'.jsonl'),table)['rows'] for table in ('team_training_settings','player_training_observations','mentorship_relations')}
for path in queries.iterdir():
    text=path.read_text(encoding='utf-8').lower();assert not any(x in text for x in ('potential','payload_ref','"address"','raw_struct'))
archives={}
for name in ('planning-probe-01','planning-capture-01'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
raw=db.read_bytes()
with gzip.open(dest/'world-v7.sqlite.gz','wb') as f:f.write(raw)
summary={'status':'STORED_PLAN_TRAINING_SOURCE_AND_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'latest_unit':unit,'source_pid':report['pid'],'latest_counts':result['counts'],'native_commit_flag_counts':result['native_commit_flag_counts'],
    'old_schema6_rows_preserved':old_rows,'old_database_byte_hash_unchanged':True,'source_to_typed_rows_compared':compared,
    'source_code_at_acquisition_sha256':json.loads((capture/'executed_code_sha256.json').read_bytes()),
    'potential_bytes_requested':0,'training_history_bytes_requested':0,'mentor_badge_slot_bytes_requested':0,
    'export_rows':exports,'world_sqlite_sha256':hashlib.sha256(raw).hexdigest(),'game_writes':False,'independent_review':False,'full_goal_complete':False}
write(dest/'planning_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_planning_audit.py')
print(json.dumps({k:summary[k] for k in ('status','old_schema6_rows_preserved','source_to_typed_rows_compared','potential_bytes_requested','training_history_bytes_requested','mentor_badge_slot_bytes_requested')}))
