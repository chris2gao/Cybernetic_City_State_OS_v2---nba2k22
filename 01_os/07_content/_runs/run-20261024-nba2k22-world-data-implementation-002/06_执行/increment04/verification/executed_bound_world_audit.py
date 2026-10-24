"""Retain actual capture evidence and query the bound world without a live read."""
from contextlib import closing
import gzip,hashlib,json,shutil,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parents[1]
APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(APP))
from engine import connect,summarize
from query import player_card,game_box,export_jsonl
from live_world import read_binding,POTENTIAL

def write(path,obj):
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

save=RUN/'_runtime/world-saves/nba2k22_test_01'
binding,binding_hash=read_binding(save,'MyLEAGUE0003')
dest=RUN/'06_执行/increment04';dest.mkdir(parents=True,exist_ok=False)
sources=dest/'native_sources';sources.mkdir()
query_out=dest/'queries';query_out.mkdir()
source_manifest={}
for capture in ('live-world-admin-01','live-world-admin-02'):
    directory=RUN/'_runtime'/capture
    report=json.loads((directory/'acquisition-report.json').read_bytes())
    result=json.loads((directory/'ingest-result.json').read_bytes())
    manifest=json.loads((directory/'world-manifest.json').read_bytes())
    for name,digest in report['artifact_sha256'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest
    assert report['binding_sha256']==binding_hash
    trace=report['read_trace'];assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    assert all(x['success'] for x in trace)
    for name in ('header.bin','game.bin','box.bin'):
        data=(directory/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
        assert any(x.get('sha256')==digest and x.get('returned_bytes')==len(data) for x in trace)
    pd=manifest['descriptors']['1'];ranges=[]
    for i in range(pd['count']):ranges.append(pd['address']+i*pd['stride']+POTENTIAL)
    for call in trace:
        if call['operation']!='ReadProcessMemory':continue
        start=int(call['address'],16);end=start+call['requested_bytes']
        assert not any(start<=excluded<end for excluded in ranges)
    for path in directory.glob('*.public.bin'):
        raw=path.read_bytes();assert len(raw)==1264 and raw[POTENTIAL]==0
        index=int(path.name.split('-')[1].split('.')[0])
        address=pd['address']+index*pd['stride']
        for offset,data in ((0,raw[:POTENTIAL]),(POTENTIAL+1,raw[POTENTIAL+1:])):
            assert any(x.get('address')==hex(address+offset) and x.get('sha256')==hashlib.sha256(data).hexdigest() for x in trace)
    pack=sources/(capture+'.tar.gz')
    with tarfile.open(pack,'w:gz') as archive:
        for path in sorted(directory.iterdir()):
            if path.is_file():archive.add(path,arcname=path.name,recursive=False)
    source_manifest[capture]={'archive':pack.name,'archive_sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),
        'report_sha256':hashlib.sha256((directory/'acquisition-report.json').read_bytes()).hexdigest(),
        'read_calls':len(trace)-1,'bound_save_id':result['save_id'],'native_save_filename':result['native_save_filename'],
        'unit_id':result['unit_id'],'current_counts':result['counts'],'potential_bytes_requested':0,
        'executed_source_code_sha256':json.loads((directory/'executed_code_sha256.json').read_bytes()) if (directory/'executed_code_sha256.json').exists() else
            {name:hashlib.sha256((APP/name).read_bytes()).hexdigest() for name in ('engine.py','live_world.py','live_reader.py','family_codec.py','schema_model.py','cli.py')}}
latest=json.loads((RUN/'_runtime/live-world-admin-02/ingest-result.json').read_bytes())
db=save/'world.sqlite';unit=latest['unit_id']
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    grade=c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0];assert grade=='LIVE_READ'
    count=c.execute('SELECT count(*) FROM player_game_boxes WHERE unit_id=?',(unit,)).fetchone()[0];assert count==26
    totals=c.execute('SELECT count(*) FROM player_season_totals WHERE unit_id=?',(unit,)).fetchone()[0];assert totals==25
    score=[dict(r) for r in c.execute('SELECT team_id,count(*) AS rows,sum(points) AS points FROM player_game_boxes WHERE unit_id=? GROUP BY team_id',(unit,))]
    assert sorted(row['points'] for row in score)==[106,122]
    memberships=c.execute('SELECT count(*) FROM roster_memberships WHERE unit_id=? AND team_id IS NOT NULL',(unit,)).fetchone()[0];assert memberships==26
    hood=c.execute("SELECT player_id FROM players WHERE display_name='Rodney Hood'").fetchone()[0]
    assert c.execute('SELECT count(*) FROM player_season_totals WHERE player_id=?',(hood,)).fetchone()[0]==0
    names=[dict(r) for r in c.execute('SELECT p.display_name,b.team_id,b.points,b.minutes_raw FROM player_game_boxes b JOIN players p USING(player_id) WHERE b.unit_id=? ORDER BY b.team_id,b.points DESC',(unit,))]
write(query_out/'rodney-hood-player-card.json',player_card(db,hood))
write(query_out/'game-history.json',game_box(db,latest['game_id']))
write(query_out/'latest-named-box.json',names)
export=export_jsonl(db,query_out/'public-box-history.jsonl','player_game_boxes')
for path in query_out.iterdir():
    content=path.read_text(encoding='utf-8').lower()
    assert not any(word in content for word in ('potential','payload_ref','raw_struct','raw_player_hex','current_team_pointer'))
write(sources/'save_binding.json',binding)
write(sources/'source_manifest.json',source_manifest)
db_bytes=db.read_bytes()
with gzip.open(dest/'bound-world.sqlite.gz','wb') as f:f.write(db_bytes)
report={'status':'BOUND_LIVE_READ_AND_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
    'latest_unit':unit,'latest_capture_counts':latest['counts'],'latest_box_score':score,
    'latest_memberships':memberships,'source_grade':grade,'native_save_filename':'MyLEAGUE0003',
    'identity_basis':'HUMAN_DECLARED_LOADED_SAVE_FILE','save_id':'nba2k22_test_01',
    'world_sqlite_sha256':hashlib.sha256(db_bytes).hexdigest(),'export_history_rows':export['rows'],
    'bound_world_file':str(db),'source_manifest':'native_sources/source_manifest.json',
    'game_writes':False,'potential_bytes_read':0,'ui_semantics_acceptance':False,'independent_review':False,
    'full_goal_complete':False}
write(dest/'bound_world_report.json',report)
print(json.dumps({'status':report['status'],'latest_player_boxes':count,'latest_season_totals':totals,'history_export_rows':export['rows'],'source_grade':grade}))
