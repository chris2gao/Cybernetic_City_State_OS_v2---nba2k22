import hashlib,json,shutil,sqlite3,subprocess,sys,time
from fractions import Fraction
from pathlib import Path
root=Path.cwd();run=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002';out=run/'06_执行/increment36';out.mkdir(parents=True,exist_ok=True)
app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from league_views import PLAYER_METRICS,SHOOTING
from query import league_standings,player_leaderboard
from observation_scope import query_at
db=run/'_runtime/world-saves/nba2k22_test_01/world-v24.sqlite';season='season:native-year:2022'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
before=digest(db);assert before=='f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218'
log=out/'verification';log.mkdir(exist_ok=True)
commands={'tests':[sys.executable,'-X','utf8','-m','unittest','discover','-s',str(app/'tests'),'-p','test_*.py'], 'sqlite_smoke':[sys.executable,'-X','utf8',str(app/'cli.py'),'smoke']}
operations={}
for name,cmd in commands.items():
    start=time.monotonic()
    with (log/(name+'.stdout.log')).open('w',encoding='utf-8') as stdout,(log/(name+'.stderr.log')).open('w',encoding='utf-8') as stderr:r=subprocess.run(cmd,stdout=stdout,stderr=stderr)
    operations[name]={'command':cmd,'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2)}
    write(log/'operations.json',operations)
    print(json.dumps({'operation':name,**operations[name]}),flush=True)
    assert r.returncode==0,name
c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
standings=league_standings(db,season);unit=standings['selected_unit_id'];assert standings['phase_code'] is None
raw=c.execute('SELECT * FROM team_season_totals WHERE unit_id=? AND season_id=? AND phase_code IS NULL',(unit,season)).fetchall()
expected=sorted([(Fraction(r['wins'],r['wins']+r['losses']),r['team_id']) for r in raw if r['wins'] is not None and r['losses'] is not None and r['wins']>=0 and r['losses']>=0 and r['wins']+r['losses']>0],key=lambda p:(-p[0],p[1]))
assert [(Fraction(r['value_exact']['numerator'],r['value_exact']['denominator']),r['totals']['team_id']) for r in standings['records']]==expected
leaders=player_leaderboard(db,season,limit=100);punit=leaders['selected_unit_id'];assert leaders['phase_code'] is None and leaders['coverage']['captured_rows']==370
comparisons=0;metric_counts={}
for metric in PLAYER_METRICS:
    params=[punit,season]
    if metric in SHOOTING:
        made,attempted=SHOOTING[metric];numerator=made;denominator=attempted;valid=f'{made}>=0 AND {attempted}>0 AND {made}<={attempted}'
    else:
        pg=metric.endswith('_per_game');field=metric.removesuffix('_per_game') if pg else metric
        numerator='offensive_rebounds+defensive_rebounds' if field=='total_rebounds' else field
        denominator='games_played' if pg else '1';valid=f'({numerator})>=0'
        if field=='total_rebounds':valid+=' AND offensive_rebounds>=0 AND defensive_rebounds>=0'
    sql=f'SELECT player_id,({numerator}) AS numerator,({denominator}) AS denominator FROM player_season_totals WHERE unit_id=? AND season_id=? AND phase_code IS NULL AND games_played>=1 AND {valid}'
    rows=c.execute(sql,params).fetchall();expected=sorted([(Fraction(r['numerator'],r['denominator']),r['player_id']) for r in rows],key=lambda p:(-p[0],p[1]))
    all_rows=[];offset=0
    while True:
        page=player_leaderboard(db,season,metric=metric,unit_id=punit,offset=offset,limit=73);all_rows.extend(page['records'])
        if page['next_offset'] is None:break
        offset=page['next_offset']
    got=[(Fraction(r['value_exact']['numerator'],r['value_exact']['denominator']),r['totals']['player_id']) for r in all_rows];assert got==expected,metric
    previous=None;rank=0
    for position,((value,pid),record) in enumerate(zip(expected,all_rows),1):
        if previous is None or value!=previous:rank=position
        assert record['rank']==rank and record['display_position']==position and record['totals']['unit_id']==punit
        previous=value;comparisons+=1
    metric_counts[metric]=len(expected)
older=c.execute("SELECT u.unit_id,u.observed_at FROM capture_units u WHERE u.unit_id IN (SELECT unit_id FROM player_season_totals WHERE season_id=?) AND u.unit_status='success' ORDER BY julianday(u.observed_at) ASC,u.unit_id ASC LIMIT 1",(season,)).fetchone()
historical=query_at(db,older['observed_at'],'player_leaderboard',season,limit=3);assert historical['result']['capture']['observed_at']==older['observed_at']
hidden=query_at(db,older['observed_at'],'player_leaderboard',season,unit_id=punit);assert hidden['result']['status']=='UNIT_NOT_OBSERVED_FOR_COHORT'
cli_results={}
for name,args in {'standings':['standings',str(db),season,'--unit-id',unit,'--limit','3'],'leaders':['player-leaderboard',str(db),season,'--metric','assists_per_game','--min-games','10','--limit','5'],'cutoff':['player-leaderboard',str(db),season,'--as-of',older['observed_at'],'--limit','3']}.items():
    r=subprocess.run([sys.executable,'-X','utf8',str(app/'cli.py'),*args],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stderr[:400];cli_results[name]=json.loads(r.stdout)
tables=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")];columns=sum(len(c.execute('PRAGMA table_info("'+t+'")').fetchall()) for t in tables)
units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];row_count=sum(c.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in tables);c.close()
after=digest(db);assert before==after
write(out/'actual-standings.json',standings);write(out/'actual-player-leaderboard.json',player_leaderboard(db,season,limit=10));write(out/'cli-results.json',cli_results)
code={n:digest(app/n) for n in ('league_views.py','query.py','cli.py','observation_scope.py','tests/test_league_views.py','README.md')}
head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
report={'status':'DATABASE_QUERY_VERIFIED','candidate_code_head':head,'code_sha256':code,'database_sha256_before':before,'database_sha256_after':after,'schema_version':24,'tables':len(tables),'columns':columns,'rows':row_count,'successful_units':units,'standings_unit_id':unit,'player_unit_id':punit,'team_rows_compared':len(raw),'player_metric_count':len(PLAYER_METRICS),'metric_row_comparisons':comparisons,'metric_ranked_counts':metric_counts,'historical_cutoff_verified':True,'new_live_game_reads':0,'database_writes':0,'new_capture_units':0,'computer_use_used':False,'capacity_work_executed':False,'overall_deferred':True,'full_goal_complete':False,'independent_acceptance':False}
write(out/'verification-report.json',report)
(out/'executed_scripts').mkdir(exist_ok=True);shutil.copyfile(Path(__file__),out/'executed_scripts'/Path(__file__).name)
print(json.dumps({k:v for k,v in report.items() if k not in ('code_sha256','metric_ranked_counts')},ensure_ascii=False),flush=True)
