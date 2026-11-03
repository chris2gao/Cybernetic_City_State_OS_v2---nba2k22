import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment32';dest.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_world import read_binding,bound_database
from engine import connect
from database_operations import file_sha256
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stderr[:500];write(dest/'preflight-before.json',json.loads(p.stdout))
binding,bhash=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding);digest=file_sha256(db);assert digest=='26cf0d4ceeadb902d02331a8ed8681181b77e92d4104a44fd2494a17cea55567'
with connect(db,True) as conn:
    tables=[row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")];counts={t:conn.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in tables};annual=[dict(v) for v in conn.execute('SELECT run_id,refresh_family,refresh_period_year FROM capture_runs WHERE refresh_family IS NOT NULL ORDER BY run_id')]
write(dest/'before.json',{'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'previous_goal_turn':'PROGRESS; automatic restart handling and live reconnect verified/published','save_id':binding['save_id'],'binding_sha256':bhash,'database_file':db.name,'database_sha256':digest,'row_counts':counts,'total_rows':sum(counts.values()),'annual_buckets':annual})
print(json.dumps({'status':'V22_BASELINE_RECORDED','rows':sum(counts.values()),'tables':len(tables)}))
