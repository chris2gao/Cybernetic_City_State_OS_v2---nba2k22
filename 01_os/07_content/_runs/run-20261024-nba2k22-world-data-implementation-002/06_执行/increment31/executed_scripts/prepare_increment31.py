import hashlib,json,subprocess,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment31';dest.mkdir(parents=True,exist_ok=True)
app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from live_world import read_binding,bound_database
from engine import connect
from database_operations import file_sha256
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
preflight=subprocess.run([sys.executable,'01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(repo),'--allow-dirty','--json'],capture_output=True,text=True,encoding='utf-8');assert preflight.returncode==0,preflight.stderr[:500];write(dest/'preflight-before.json',json.loads(preflight.stdout))
save=runtime/'world-saves/nba2k22_test_01';binding,bhash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
with connect(db,True) as conn:
    tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    counts={t:conn.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in tables}
    units=[dict(r) for r in conn.execute('SELECT * FROM capture_units ORDER BY unit_id')]
    annual=[dict(r) for r in conn.execute('SELECT run_id,refresh_family,refresh_period_year FROM capture_runs WHERE refresh_family IS NOT NULL ORDER BY run_id')]
digest=file_sha256(db);assert digest=='09fa9a373cb2bd0c994aacc8136e6c71255595f258bdb1b02f4733bd014009d1'
write(dest/'before.json',{'previous_goal_turn':'PROGRESS; verified v22 staff capture, history and source branch publication','save_id':binding['save_id'],'binding_sha256':bhash,'database_file':db.name,'database_sha256':digest,'row_counts':counts,'units':units,'annual_buckets':annual,'total_rows':sum(counts.values()),'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()})
write(dest/'computer-use-text-observation.json',{'method':'computer-use:computer-use; @oai/sky get_window_state include_screenshot=false include_text=true','window_title':'NBA 2K22','window_id':722502,'first_observation':'WINDOW_MINIMIZED; no input to game','recovery':'fresh unique window selection; activate_window; fresh get_window; text-only observation','accessibility_tree':'Window: "NBA 2K22", App: NBA2K22.exe.\n0 window NBA 2K22 Secondary Actions: Raise','game_menu_fields_or_values_observed':False,'screenshots_requested':0,'game_key_or_mouse_inputs':0,'game_value_edits':0,'conclusion':'Top-level window only. Text identification cannot currently support navigation or one-value differential tests. No UI field correspondence established.'})
print(json.dumps({'status':'BASELINE_AND_PREFLIGHT_RECORDED','tables':len(tables),'rows':sum(counts.values()),'units':len(units)}))
