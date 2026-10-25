import hashlib,json,subprocess,sys,time
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from query import player_card,team_card,game_box,native_player_skills,native_player_details,native_player_state,native_affiliations
from database_operations import file_sha256
from engine import connect
r=Path(__file__).resolve().parent;save=r/'world-saves/nba2k22_test_01';binding=json.loads((save/'save.json').read_bytes());db=save/binding['database_file'];before=file_sha256(db)
with connect(db,True) as c:game=c.execute('SELECT game_id FROM player_game_boxes ORDER BY game_id LIMIT 1').fetchone()[0]
commands={'player_card':lambda:player_card(db,'player:native:1612'),'team_card':lambda:team_card(db,'team:native:0'),'game_box':lambda:game_box(db,game)}
for name,call in [('native_skills',native_player_skills),('native_details',native_player_details),('native_state',native_player_state),('native_affiliation',native_affiliations)]:commands[name]=lambda call=call:call(db,subject_name='Stephen Curry')
results={}
for name,call in commands.items():
    start=time.perf_counter();result=call();elapsed=time.perf_counter()-start;raw=json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();results[name]={'seconds':elapsed,'result_bytes':len(raw),'result_sha256':hashlib.sha256(raw).hexdigest()}
assert file_sha256(db)==before
report={'status':'MEASURED_CURRENT_DATABASE_QUERIES_NOT_100_SEASON_LATENCY','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),'database_sha256':before,'measurements':results,'cache_control':'one fixed-order run; OS/SQLite caches not cleared','game_access':False}
(r/'fact-recovery-actual-01/current-query-timings.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({name:round(value['seconds'],4) for name,value in results.items()}))
