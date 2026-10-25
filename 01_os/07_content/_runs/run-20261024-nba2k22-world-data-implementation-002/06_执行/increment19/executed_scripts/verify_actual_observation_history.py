"""Check current actual facts at every recorded cutoff without game access."""
from datetime import datetime,timedelta,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from database_operations import file_sha256
from observation_scope import observed_as_of,query_at,query_connection,utc_stamp
from schema_model import TABLES,ident
import query
r=Path(__file__).resolve().parent;save=r/'world-saves/nba2k22_test_01';binding_raw=(save/'save.json').read_bytes();binding=json.loads(binding_raw);db=save/binding['database_file'];before=file_sha256(db)
dest=r.parent/'06_执行/increment19';dest.mkdir(parents=True,exist_ok=True);examples=dest/'queries';examples.mkdir()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
with connect(db,True) as owner:
    units=[dict(row) for row in owner.execute("SELECT unit_id,source_key,observed_at FROM capture_units WHERE unit_status='success' ORDER BY observed_at,unit_id")]
    assert all(utc_stamp(u['observed_at'])==u['observed_at'] for u in units)
    game=owner.execute('SELECT game_id FROM player_game_boxes ORDER BY game_id LIMIT 1').fetchone()[0];staff=owner.execute('SELECT staff_id FROM staff_members ORDER BY staff_id LIMIT 1').fetchone()[0]
    plan=owner.execute('SELECT team_id,opponent_team_id FROM gameplan_observations ORDER BY plan_id LIMIT 1').fetchone()
before_first=(datetime.fromisoformat(units[0]['observed_at'])-timedelta(microseconds=1)).isoformat(timespec='microseconds');cutoffs=[before_first]+sorted({u['observed_at'] for u in units});tables=[name for name,spec in TABLES.items() if spec.public and 'unit_id' in {c.name for c in spec.columns}]
comparisons=0;summaries=[]
with connect(db,True) as owner:
    for cutoff in cutoffs:
        with observed_as_of(db,cutoff) as scope,query_connection(db,True) as scoped:
            counts={}
            for name in tables:
                expected=owner.execute('SELECT count(*) FROM main.'+ident(name)+''' t JOIN main.capture_units u USING(unit_id) WHERE u.unit_status='success' AND u.observed_at<=?''',(scope.observed_through,)).fetchone()[0]
                found=scoped.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0];assert found==expected,(cutoff,name,found,expected);counts[name]=found;comparisons+=1
            summaries.append({'cutoff':cutoff,'committed_units':len(scope.unit_ids),'visible_observation_rows':sum(counts.values()),'row_counts':counts})
by_source={u['source_key']:u for u in units};last=units[-1]['observed_at'];field_comparisons=0
field_cutoffs=[]
for key in ('BOUND_PLAYER_CONTRACT_AND_BASE_BADGES','BOUND_PLAYER_VITALS_HEALTH_MORALE','BOUND_PUBLIC_PLAYER_SKILLS'):
    field_cutoffs.append((datetime.fromisoformat(by_source[key]['observed_at'])-timedelta(microseconds=1)).isoformat(timespec='microseconds'))
field_cutoffs.append(last)
with connect(db,True) as owner:
    for index,cutoff in enumerate(field_cutoffs):
        value=query_at(db,cutoff,'player_card','player:native:1612');card=value['result'];assert 'families' in card
        for name in ('player_vitals_observations','player_attribute_snapshots','player_tendency_snapshots','player_contract_observations','player_health_observations','player_morale_observations','player_training_observations'):
            for col in TABLES[name].columns:
                if col.name in ('player_id','unit_id',TABLES[name].key):continue
                expected=owner.execute('SELECT a.'+ident(col.name)+''' AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade FROM main.'''+ident(name)+''' a JOIN main.capture_units u USING(unit_id) JOIN main.capture_runs r USING(run_id)
                    WHERE a.player_id=? AND a.'''+ident(col.name)+''' IS NOT NULL AND u.unit_status='success' AND u.observed_at<=? ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',('player:native:1612',cutoff)).fetchone()
                actual=card['families'][name][col.name]
                if expected:assert all(actual[k]==v for k,v in dict(expected).items()),(cutoff,name,col.name)
                else:assert actual['value'] is None and actual['status']=='NOT_OBSERVED',(cutoff,name,col.name)
                field_comparisons+=1
        write(examples/('curry-cutoff-'+str(index)+'.json'),value)
calls=[('player_card',('player:native:1612',),{}),('team_card',('team:native:0',),{}),('staff_card',(staff,),{}),('game_box',(game,),{}),('schedule',(),{}),
    ('player_badges',('player:native:1612',),{}),('player_play_types',('player:native:1612',),{}),('market_snapshot',(),{}),('settings_snapshot',(),{}),('rules_snapshot',(),{}),('planning_snapshot',(),{}),('gameplan_card',(plan[0],plan[1]),{}),
    ('native_player_skills',(),{'subject_name':'Stephen Curry'}),('native_player_details',(),{'subject_name':'Stephen Curry'}),('native_player_state',(),{'subject_name':'Stephen Curry'}),('native_affiliations',(),{'subject_name':'Stephen Curry'}),
    ('native_honors',(),{'subject_name':'Stephen Curry','limit':5}),('record_book',(),{'subject_name':'Wilt Chamberlain','limit':5}),('awards',(),{'limit':5}),('league_history',(),{'limit':5}),('native_news',(),{'limit':5}),('native_transactions',(),{}),
    ('history',('player_attribute_snapshots',),{'entity_key':'player_id','entity_id':'player:native:1612','limit':5})]
equal={}
for name,args,kwargs in calls:
    plain=getattr(query,name)(db,*args,**kwargs);historical=query_at(db,last,name,*args,**kwargs)['result'];assert plain==historical,name;equal[name]=True
assert query_at(db,before_first,'player_card','player:native:1612')['result']['status']=='NOT_OBSERVED'
before_skill=field_cutoffs[2];skill_unit=by_source['BOUND_PUBLIC_PLAYER_SKILLS']['unit_id'];assert query_at(db,before_skill,'native_player_skills',unit_id=skill_unit)['result']['records']==[]
with connect(db,True) as owner:
    expected={r[0] for r in owner.execute('SELECT snapshot_id FROM player_attribute_snapshots')}
with observed_as_of(db,last) as scope:
    seen=set();cursor=None;pages=0
    while True:
        page=query.history_page(db,'player_attribute_snapshots',limit=250,cursor=cursor);pages+=1
        for row in page['records']:assert row['snapshot_id'] not in seen;seen.add(row['snapshot_id'])
        if not page['has_more']:break
        cursor=page['next_cursor']
    assert seen==expected
    page_scope=scope.metadata()
export=examples/'attributes-before-new-skill-capture.jsonl';exported=query_at(db,before_skill,'export_jsonl',export,'player_attribute_snapshots',limit=10000)
with connect(db,True) as owner:expected_export=owner.execute('SELECT count(*) FROM player_attribute_snapshots a JOIN capture_units u USING(unit_id) WHERE u.observed_at<=?',(before_skill,)).fetchone()[0]
assert exported['result']['rows']==expected_export;write(examples/'historical-export-receipt.json',exported)
assert file_sha256(db)==before and (save/'save.json').read_bytes()==binding_raw
report={'status':'ACTUAL_OBSERVATION_TIME_QUERIES_AND_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
    'source_database_sha256_unchanged':before,'reference_database_archive':'../increment17/world-v16.sqlite.gz','active_binding_unchanged':True,'schema_version':16,'tables':84,'columns':1306,
    'successful_units':len(units),'cutoffs_checked':len(cutoffs),'public_unit_tables_checked':len(tables),'table_cutoff_count_comparisons':comparisons,'per_field_direct_sql_comparisons':field_comparisons,
    'latest_plain_and_temporal_query_results_equal':equal,'future_identity_hidden':True,'future_explicit_unit_pin_blocked':True,'attribute_history_pages':pages,'attribute_history_rows':len(seen),'historical_export_rows':expected_export,'history_scope':page_scope,
    'time_basis':'HOST_CAPTURE_OBSERVED_AT; NOT_NATIVE_GAME_DATE_OR_UNOBSERVED_EVENT_TIME','cutoff_summaries':summaries,'game_access':False,'capacity_work_executed':False,'full_goal_complete':False,
    'limits':['Current schema/decoder interpretation is used; historical UI/lifecycle acceptance is not implied.','Contexts freeze committed units at entry; later backfill creates a different ledger and invalidates old cursors.','Scope wrappers are controlled query functionality, not an ACL for an owner holding the raw database.']}
write(dest/'actual-observation-history-report.json',report);scripts=dest/'executed_scripts';scripts.mkdir();(scripts/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:report[k] for k in ('status','successful_units','cutoffs_checked','table_cutoff_count_comparisons','per_field_direct_sql_comparisons','attribute_history_pages','attribute_history_rows','historical_export_rows')}))
