"""Independent stored-fact comparisons; no game access or new capture."""
from collections import Counter,defaultdict
from contextlib import closing
from datetime import datetime,timedelta
import json,subprocess,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from database_operations import file_sha256
from observation_scope import query_at,utc_stamp
from query import game_box,season_summary,player_seasons

run=next(p for p in Path(__file__).resolve().parents if p.name=='run-20261024-nba2k22-world-data-implementation-002');runtime=run/'_runtime';save=runtime/'world-saves/nba2k22_test_01';binding_raw=(save/'save.json').read_bytes();binding=json.loads(binding_raw);db=save/binding['database_file'];before=file_sha256(db)
dest=run/'06_执行/increment20';dest.mkdir(parents=True,exist_ok=True);examples=dest/'queries';examples.mkdir(exist_ok=True)
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
table_map={'states':'game_state_observations','period_scores':'game_period_scores','player_boxes':'player_game_boxes','team_boxes':'team_game_boxes'}
games_checked=0;row_comparisons=0;score_status=Counter();coverage_status=Counter();selected_units=Counter();multiple=0;receipts=[];selected_examples={}
with closing(connect(db,True)) as owner:
    games=[dict(r) for r in owner.execute('SELECT * FROM games ORDER BY game_id')]
    units={r['unit_id']:dict(r) for r in owner.execute("SELECT * FROM capture_units WHERE unit_status='success'")}
    last=max(utc_stamp(r['observed_at']) for r in units.values())
    identities={r['player_id']:r['native_player_id'] for r in owner.execute('SELECT player_id,native_player_id FROM players')}
    team_ids={r['team_id']:r['native_team_id'] for r in owner.execute('SELECT team_id,native_team_id FROM teams')}
    for game in games:
        gid=game['game_id'];value=game_box(db,gid);assert value['status']=='SINGLE_OBSERVATION_UNIT',gid
        candidates=set()
        for table in (*table_map.values(),'native_box_observations'):
            candidates.update(r[0] for r in owner.execute('SELECT DISTINCT unit_id FROM '+table+' WHERE game_id=?',(gid,)))
        candidates&=units.keys();expected_unit=max(candidates,key=lambda u:(utc_stamp(units[u]['observed_at']),u));unit=value['selected_unit_id'];assert unit==expected_unit
        if len(candidates)>1:
            multiple+=1;old=min(candidates,key=lambda u:(utc_stamp(units[u]['observed_at']),u));pinned=game_box(db,gid,unit_id=old);assert pinned['selected_unit_id']==old
            for rows in table_map:
                assert all(r['unit_id']==old for r in pinned[rows])
        for key,table in table_map.items():
            expected=[dict(r) for r in owner.execute('SELECT * FROM '+table+' WHERE game_id=? AND unit_id=?',(gid,unit))]
            columns=list(expected[0]) if expected else []
            actual=[{k:r[k] for k in columns} for r in value[key]]
            assert Counter(json.dumps(r,sort_keys=True) for r in actual)==Counter(json.dumps(r,sort_keys=True) for r in expected),(gid,key)
            row_comparisons+=len(expected);assert all(r['unit_id']==unit for r in value[key])
        native=[dict(r) for r in owner.execute('SELECT * FROM native_box_observations WHERE game_id=? AND unit_id=?',(gid,unit))]
        qualified={}
        for side,team in [('HOME',game['home_team_id']),('AWAY',game['away_team_id'])]:
            active=[r for r in native if r['side']==side and r['in_use']==1]
            canonical=[r for r in value['player_boxes'] if r['team_id']==team and r['in_use']!=0]
            pairs=[(str(r['native_player_id']),r['points']) for r in active]
            mapped=[(str(identities[r['player_id']]),r['points']) for r in canonical if identities[r['player_id']] is not None]
            full=bool(active and len(canonical)==len(active) and len({r['native_player_id'] for r in active})==len(active)
                and all(r['in_use']==1 and r['points'] is not None for r in canonical) and all(r['points'] is not None and r['identity_status']=='CURRENT_CONTEXT_RESOLVED' and str(r['native_team_id'])==str(team_ids[team]) for r in active)
                and Counter(mapped)==Counter(pairs))
            qualified[side]=sum(r['points'] for r in canonical) if full else None
            assert value['scores']['derived_canonical_points'][side]==qualified[side],(gid,side)
            native_sum=sum(r['points'] for r in active) if active and all(r['points'] is not None for r in active) else None
            assert value['scores']['captured_native_points'][side]==native_sum
            coverage_status[value['coverage'][side]['status']]+=1
        state=value['states'][0] if value['states'] else {};literal=[state.get('home_points'),state.get('away_points')]
        expected=literal if any(n is not None for n in literal) else ([qualified['HOME'],qualified['AWAY']] if all(n is not None for n in qualified.values()) else [None,None])
        assert [value['scores']['home_points'],value['scores']['away_points']]==expected
        kind=value['scores']['value_status'];score_status[kind]+=1;selected_units[unit]+=1;games_checked+=1
        receipts.append({'game_id':gid,'selected_unit_id':unit,'available_units':len(candidates),'canonical_rows':len(value['player_boxes']),'native_rows':len(native),'score_status':kind,'coverage':{k:v['status'] for k,v in value['coverage'].items()}})
        if kind not in selected_examples:selected_examples[kind]=value
    totals={};all_total_times=[]
    for table,entity in [('player_season_totals','player_id'),('team_season_totals','team_id')]:
        selected={}
        for raw in owner.execute('SELECT * FROM '+table):
            row=dict(raw)
            if row['unit_id'] not in units:continue
            all_total_times.append(utc_stamp(units[row['unit_id']]['observed_at']))
            key=(row[entity],row['season_id'],row['phase_code'])+((row['team_scope'],row['team_id']) if entity=='player_id' else ())
            sort=(utc_stamp(units[row['unit_id']]['observed_at']),row['unit_id'])
            if key not in selected or sort>selected[key][0]:selected[key]=(sort,row)
        totals[table]=[r[1] for r in selected.values()]
    season_ids=sorted({r['season_id'] for values in totals.values() for r in values});rate_comparisons=0;season_counts={}
    count_fields='points fg_made fg_attempted three_made three_attempted ft_made ft_attempted offensive_rebounds defensive_rebounds assists steals blocks turnovers fouls'.split()
    for sid in season_ids:
        value=season_summary(db,sid);assert value==query_at(db,last,'season_summary',sid)['result'];season_counts[sid]={}
        for key,table,isplayer in [('players','player_season_totals',True),('teams','team_season_totals',False)]:
            expected=[r for r in totals[table] if r['season_id']==sid];cols=list(expected[0]) if expected else []
            actual=[{k:r['totals'][k] for k in cols} for r in value[key]]
            assert Counter(json.dumps(r,sort_keys=True) for r in actual)==Counter(json.dumps(r,sort_keys=True) for r in expected)
            season_counts[sid][key]=len(actual)
            for record in value[key]:
                row=record['totals'];derived=record['derived'];gp=row['games_played'] if isplayer else (row['wins']+row['losses'] if row['wins'] is not None and row['losses'] is not None else None)
                assert derived['games_denominator']==gp
                valid=type(gp) is int and gp>0 and (isplayer or (row['wins']>=0 and row['losses']>=0))
                for field in count_fields:
                    expected_rate=row[field]/gp if valid and row[field] is not None else None
                    assert derived['per_game_counts'][field]==expected_rate;rate_comparisons+=1
                for label,m,a in [('field_goal_fraction','fg_made','fg_attempted'),('three_point_fraction','three_made','three_attempted'),('free_throw_fraction','ft_made','ft_attempted')]:
                    expected_rate=row[m]/row[a] if row[m] is not None and row[a] is not None and 0<=row[m]<=row[a] and row[a]>0 else None
                    assert derived['shooting_fractions'][label]['value']==expected_rate;rate_comparisons+=1
        write(examples/('season-'+sid.replace(':','-')+'.json'),value)
    player_ids=sorted({r['player_id'] for r in totals['player_season_totals']});player_checks=0
    for pid in player_ids:
        value=player_seasons(db,pid);expected=[r for r in totals['player_season_totals'] if r['player_id']==pid]
        assert len(value['records'])==len(expected);assert {(r['totals']['season_id'],r['totals']['phase_code'],r['totals']['team_scope'],r['totals']['team_id'],r['totals']['unit_id']) for r in value['records']}=={(r['season_id'],r['phase_code'],r['team_scope'],r['team_id'],r['unit_id']) for r in expected};player_checks+=1
    first_totals=min(all_total_times)
    cutoff=(datetime.fromisoformat(first_totals)-timedelta(microseconds=1)).isoformat(timespec='microseconds')
    for sid in season_ids:
        historical=query_at(db,cutoff,'season_summary',sid)['result'];assert historical['players']==[] and historical['teams']==[]
    sample=player_seasons(db,'player:native:1612');write(examples/'curry-season-observations.json',sample)
for index,(kind,value) in enumerate(selected_examples.items()):write(examples/('game-box-'+str(index)+'.json'),value)
assert file_sha256(db)==before and (save/'save.json').read_bytes()==binding_raw
report={'status':'ACTUAL_SINGLE_UNIT_BOXES_AND_SEASON_DERIVATIONS_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
    'source_database_sha256_unchanged':before,'reference_database_archive':'../increment17/world-v16.sqlite.gz','active_binding_unchanged':True,
    'games_checked':games_checked,'public_box_rows_compared_to_direct_sql':row_comparisons,'games_with_multiple_units_checked':multiple,'score_status_counts':dict(score_status),'coverage_status_counts':dict(coverage_status),'selected_unit_counts':dict(selected_units),
    'season_totals_counts':season_counts,'derived_rate_comparisons':rate_comparisons,'player_season_query_checks':player_checks,'latest_season_as_of_parity':True,'before_first_totals_hidden':True,'game_access':False,'new_captures':False,'capacity_work_executed':False,'schema_migration':False,'full_goal_complete':False,
    'limits':['Captured Native sums do not resolve missing canonical players.','Unknown phase/team scope/finality is not promoted; no career sum or official seed is inferred.','Minutes retain raw Native units; current identity lifecycle and UI semantics remain separate evidence.']}
write(dest/'actual-competition-report.json',report);write(dest/'game-unit-comparisons.json',receipts)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True);(scripts/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:report[k] for k in ('status','games_checked','public_box_rows_compared_to_direct_sql','games_with_multiple_units_checked','score_status_counts','coverage_status_counts','season_totals_counts','derived_rate_comparisons','player_season_query_checks')}))
