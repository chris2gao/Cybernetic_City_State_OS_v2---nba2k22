"""Offline audit of actual captured season sources and migrated fact history."""
from bisect import bisect_left
from contextlib import closing
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3]
APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from live_world import read_binding,bound_database,POTENTIAL
from query import schedule,export_jsonl
from readers import _module
from schema_model import TABLES,ident
from schedule_reader import index_relationship

def write(path,obj):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

dest=RUN/'06_执行/increment05';dest.mkdir(parents=True,exist_ok=False)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
capture=RUN/'_runtime/season-admin-03';result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
manifest=json.loads((capture/'schedule-manifest.json').read_bytes());context=json.loads((capture/'player-context.json').read_bytes())
report=json.loads((capture/'acquisition-report.json').read_bytes())
for name,digest in report['artifact_sha256'].items():assert hashlib.sha256((capture/name).read_bytes()).hexdigest()==digest
trace=report['read_trace'];assert all(x['success'] for x in trace)
assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
pd=context['descriptors']['1'];excluded=[pd['address']+i*pd['stride']+POTENTIAL for i in range(pd['count'])]
reads=set()
for x in trace:
    if x['operation']!='ReadProcessMemory':continue
    start=int(x['address'],16);end=start+x['requested_bytes'];i=bisect_left(excluded,start)
    assert i==len(excluded) or excluded[i]>=end
    reads.add((start,x['returned_bytes'],x['sha256']))
for path in capture.glob('*.public.bin'):
    raw=path.read_bytes();assert raw[POTENTIAL]==0 and len(raw)==1264
    idx=int(path.name.split('-')[1].split('.')[0]);address=pd['address']+idx*1264
    for off,data in ((0,raw[:POTENTIAL]),(POTENTIAL+1,raw[POTENTIAL+1:])):
        assert (address+off,len(data),hashlib.sha256(data).hexdigest()) in reads
games=(capture/'schedule-games.bin').read_bytes();index=(capture/'schedule-native_index.bin').read_bytes()
relation=index_relationship({'games':games,'native_index':index,'manifest':manifest},context)
decoder=_module('boxscore_decoder').BoxScoreDecoder
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    for i,entry in enumerate(manifest['entries']):
        if entry['status']!=2:continue
        raw=(capture/f'schedule-box-{i}.bin').read_bytes();full=decoder.decode_full_boxscore(games[i*60:(i+1)*60],raw)
        assert full['conservation']['home_score_exact'] and full['conservation']['away_score_exact']
        gid=result['season']['season_id']+':game:'+str(full['game_id'])
        native=[r[0] for r in c.execute('SELECT sum(points) FROM native_box_observations WHERE game_id=? AND unit_id=? GROUP BY side ORDER BY side',(gid,unit))]
        assert native==[full['away_score'],full['home_score']]
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    assert c.execute('SELECT count(*) FROM games').fetchone()[0]==1232
    counts={t:c.execute(f'SELECT count(*) FROM {ident(t)} WHERE unit_id=?',(unit,)).fetchone()[0]
        for t in ('game_state_observations','player_game_boxes','native_box_observations','player_season_totals')}
    old_counts={}
    with closing(connect(save/'world.sqlite',True)) as old:
        for name,spec in TABLES.items():
            if name=='saves':continue
            before=list(old.execute('SELECT * FROM '+ident(name)));old_counts[name]=len(before)
            for row in before:
                current=c.execute(f'SELECT * FROM {ident(name)} WHERE {ident(spec.key)}=?',(row[spec.key],)).fetchone()
                assert current is not None and dict(row)==dict(current),name
    for native_id in result['unresolved_native_player_ids']:
        assert not c.execute('SELECT 1 FROM player_game_boxes b JOIN players p USING(player_id) WHERE b.unit_id=? AND p.native_player_id=?',(unit,str(native_id))).fetchone()
rows=schedule(db);finals=schedule(db,status_code='2');future=schedule(db,status_code='0')
assert len(rows)==1232 and len(finals)==238 and len(future)==994
assert all(r['home_points_derived'] is None and r['away_points_derived'] is None for r in future)
assert all(r['game_date'] is None for r in rows)
try:schedule(db,limit=100)
except ValueError:pass
else:raise AssertionError('schedule silently truncated')
write(queries/'schedule-latest.json',rows);write(queries/'final-games.json',finals)
export=export_jsonl(db,queries/'player-box-history.jsonl','player_game_boxes',limit=20000)
for path in queries.iterdir():
    text=path.read_text(encoding='utf-8').lower()
    assert not any(k in text for k in ('potential','payload_ref','raw_player_hex','current_team_pointer'))
source_manifest={}
for name in ('schedule-admin-01','season-admin-01','season-admin-02','season-admin-03'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    source_manifest[name]={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'files':sum(p.is_file() for p in directory.iterdir())}
write(sources/'source_manifest.json',source_manifest);write(sources/'save_binding.json',binding)
raw=db.read_bytes()
with gzip.open(dest/'world-v4.sqlite.gz','wb') as f:f.write(raw)
source_code={name:hashlib.sha256((APP/name).read_bytes()).hexdigest() for name in
    ('schedule_reader.py','live_world.py','live_reader.py','family_codec.py','engine.py','schema_model.py','cli.py','query.py')}
summary={'status':'COMPLETE_OBSERVED_WINDOW_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'source_code_sha256':source_code,'latest_unit':unit,'latest_counts':counts,'resolved_players':411,
    'final_games':len(finals),'unplayed_games':len(future),'complete_canonical_box_games':sum(r['canonical_box_complete'] for r in finals),
    'unresolved_native_player_ids':result['unresolved_native_player_ids'],'index_relationship':relation,
    'old_schema3_rows_preserved':sum(old_counts.values()),'all_old_rows_compared':True,'potential_bytes_read':0,
    'world_sqlite_sha256':hashlib.sha256(raw).hexdigest(),'exported_history_boxes':export['rows'],
    'game_writes':False,'full_goal_complete':False,'independent_review':False,
    'source_process_pid':report['pid'],'process_restart_after_capture':'Human reported restart; old addresses are historical only'}
write(dest/'season_world_report.json',summary)
shutil.copyfile(__file__,dest/'executed_season_audit.py')
print(json.dumps({k:summary[k] for k in ('status','resolved_players','final_games','unplayed_games','complete_canonical_box_games','old_schema3_rows_preserved','exported_history_boxes')}))
