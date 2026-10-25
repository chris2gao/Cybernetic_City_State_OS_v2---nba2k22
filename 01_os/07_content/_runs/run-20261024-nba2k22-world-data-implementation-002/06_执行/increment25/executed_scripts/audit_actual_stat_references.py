"""Actual source-to-query checks; reuse annual raw data and leave DB bytes equal."""
from collections import Counter,defaultdict
from contextlib import closing
import hashlib,json,shutil,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;run=runtime.parent;dest=run/'06_执行/increment25';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from database_operations import file_sha256
from live_world import read_binding,bound_database
from query import native_player_seasons
from observation_scope import query_at
from schema_model import NATIVE_PLAYER_STAT_MAP
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
proof=json.loads((dest/'native-contract-report.json').read_bytes());before=json.loads((dest/'before.json').read_bytes());assert proof['status']=='CURRENT_NATIVE_STAT_REFERENCE_CODE_AND_METADATA_VERIFIED' and proof['binding_unchanged']
assert proof['context_before']['epoch']==proof['context_after']['epoch'] and proof['contract']['native_array_count']==25 and proof['getter_invocations']==0 and not proof['annual_data_refreshed']
assert proof['before_database_sha256']==proof['after_database_sha256']==before['database_sha256']=='46eec932562bb5b722c490bb71011b4d21db87a4f86d1be742ba5435ea87514d'
interval=proof['player_interval'];lo=interval['address'];hi=lo+interval['count']*1264;trace=proof['read_trace'];code_reads=[]
for item in trace:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size and (address>=hi or address+size<=lo)
    if item.get('label','').startswith('STAT_REFERENCE_CODE:'):code_reads.append(item)
assert len(code_reads)==4 and sum(i['requested_bytes'] for i in code_reads)==469
save=runtime/'world-saves/nba2k22_test_01';binding,binding_hash=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);assert file_sha256(db)==before['database_sha256'] and binding_hash==before['binding_sha256']
source=runtime/'annual-live-v11/honors-first';ingest=json.loads((source/'ingest-result.json').read_bytes());unit=ingest['unit_id'];statraw=(source/'player-stat-bank.bin').read_bytes();public=(source/'player-public-projection.bin').read_bytes();profile=json.loads((app/'award_native_profile.json').read_bytes());source_hashes=0
with closing(connect(db,True)) as c:
    stats_count=c.execute('SELECT count(*) FROM native_player_stat_observations WHERE unit_id=?',(unit,)).fetchone()[0];player_count=c.execute('SELECT count(*) FROM native_player_sources WHERE unit_id=?',(unit,)).fetchone()[0];link_count=c.execute('SELECT count(*) FROM native_player_stat_links WHERE unit_id=?',(unit,)).fetchone()[0]
    assert (stats_count,player_count,link_count)==(9773,3390,84750) and len(statraw)==stats_count*48 and len(public)==player_count*144
    stored_unit=dict(c.execute('SELECT unit_id,observed_at FROM capture_units WHERE unit_id=?',(unit,)).fetchone());assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[]
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        if artifact['payload_ref'].startswith(source.name+'/'):
            path=source/Path(artifact['payload_ref']).name;assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];source_hashes+=1
    successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==33
    links={row['stat_link_id']:dict(row) for row in c.execute('SELECT * FROM native_player_stat_links WHERE unit_id=?',(unit,))}
    expected_sources={row[0] for row in c.execute('SELECT source_player_index FROM native_player_sources WHERE unit_id=?',(unit,))}
seen=set();references=0;resolved=0;comparisons=0;zero_resolved=0;after_gap_resolved=0;old_null_resolved=0;pages=0;statuses=Counter();years=Counter();owners=defaultdict(set);named={};after=-1;first_page=None
while True:
    page=native_player_seasons(db,unit_id=unit,after_index=after,limit=100);pages+=1;assert page['unit']['unit_id']==unit and page['unit']['source_grade']=='LIVE_READ' and page['unit']['observed_at']==stored_unit['observed_at']
    if first_page is None:first_page=page
    for player in page['records']:
        index=player['source_player_index'];assert index not in seen and player['reference_array_complete'] and player['captured_reference_count']==25;seen.add(index);after_gap=False
        if player['observed_name'] in ('Stephen Curry','LeBron James','Giannis Antetokounmpo'):named.setdefault(player['observed_name'],player)
        for reference in player['stat_references']:
            references+=1;position=reference['array_position'];native_index=int.from_bytes(public[index*144+94+position*2:index*144+96+position*2],'little');assert native_index==reference['native_stat_index_raw']
            old=links[reference['reference_id']];assert old['link_status']==reference['capture_link_status'] and old['stat_observation_id']==reference['capture_stat_observation_id'];assert reference['phase_code'] is None
            valid=native_index<32768 and native_index<stats_count;record=reference['record'];statuses[reference['resolution_status']]+=1
            assert (record is not None)==valid
            if not valid:after_gap=True;continue
            assert reference['resolution_status']=='RESOLVED_SAME_UNIT_NATIVE_RECORD' and record['source_stat_index']==native_index;raw=statraw[native_index*48:(native_index+1)*48];resolved+=1;zero_resolved+=native_index==0;after_gap_resolved+=after_gap;old_null_resolved+=old['stat_observation_id'] is None
            for native,column in NATIVE_PLAYER_STAT_MAP.items():
                f=profile['stat_fields'][native];value=int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit']&((1<<f['width'])-1);assert record[column]==value,(index,position,column);comparisons+=1
            assert record['stat_year']==1900+raw[5];years[record['stat_year']]+=1;owners[native_index].add(index)
    if not page['has_more']:break
    assert page['next_after_index']>after;after=page['next_after_index']
assert seen==expected_sources and references==84750 and pages==34 and named
latest=native_player_seasons(db,limit=1);assert latest['unit']['unit_id']==unit
hidden=query_at(db,'2000-01-01T00:00:00Z','native_player_seasons')['result'];assert hidden['status']=='NOT_OBSERVED'
examples=dest/'queries';examples.mkdir(exist_ok=True)
for name,player in named.items():
    output=native_player_seasons(db,unit_id=unit,source_index=player['source_player_index']);write(examples/(name.replace(' ','-').lower()+'.json'),output)
    record_years={r['record']['stat_year'] for r in player['stat_references'] if r['record'] is not None}
    for year in record_years:
        filtered=native_player_seasons(db,unit_id=unit,source_index=player['source_player_index'],year=year);assert filtered['records'] and all(r['record']['stat_year']==year for r in filtered['records'][0]['stat_references'])
    if player['player_id']:
        canonical=native_player_seasons(db,unit_id=unit,player_id=player['player_id']);assert any(p['source_player_index']==player['source_player_index'] for p in canonical['records'])
write(examples/'first-page.json',{'unit':first_page['unit'],'source_player_indices':[p['source_player_index'] for p in first_page['records']],'has_more':first_page['has_more'],'next_after_index':first_page['next_after_index']})
assert file_sha256(db)==before['database_sha256'];sources=dest/'sources';sources.mkdir(exist_ok=True)
for name in ('player-public-projection.bin','player-stat-bank.bin','ingest-result.json'):shutil.copyfile(source/name,sources/name)
shutil.copyfile(runtime/'stat-consumer-code.json',dest/'static-stat-consumers.json')
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment25.py','inspect_current_stat_getters.py','inspect_stat_consumers.py','build_stat_reference_profile.py','verify_stat_reference_live.py','start_stat_reference_live.ps1',Path(__file__).name):shutil.copyfile(runtime/name,scripts/name)
result={'status':'ACTUAL_ANNUAL_NATIVE_STAT_SOURCE_TO_QUERY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':proof['candidate_code_head'],'schema_version':18,'tables':86,'columns':1376,'database_sha256_unchanged':before['database_sha256'],'save_binding_sha256_unchanged':binding_hash,'source_unit':stored_unit,'current_code_contract_observed_at':proof['observed_at'],'source_rows':{'stat_records':stats_count,'player_sources':player_count,'references':link_count},'query_pages_verified':pages,'source_players_queried':len(seen),'references_checked_against_raw_bytes':references,'resolved_references':resolved,'resolved_zero_indices':zero_resolved,'resolved_after_gaps':after_gap_resolved,'resolved_with_original_null_capture_link':old_null_resolved,'raw_stat_field_comparisons':comparisons,'resolution_counts':dict(statuses),'observed_year_reference_counts':dict(years),'shared_stat_records':sum(len(v)>1 for v in owners.values()),'source_artifact_hashes_checked':source_hashes,'code_windows_verified':4,'code_window_bytes':469,'successful_units_unchanged':successful_units,'annual_history_refreshed':False,'db_rows_written':0,'getter_invocations':0,'game_writes':False,'capacity_work_executed':False,'full_goal_complete':False,'limits':['Record associations remain source references; allocation, historical identity and ownership are not established.','No chronological array order, cumulative phase, career sum, UI units or award finalization is inferred.','Annual historical data retains its original observation time; current code verification is a separate observation.']}
write(dest/'actual-stat-reference-report.json',result)
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\nsources/* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','query_pages_verified','source_players_queried','references_checked_against_raw_bytes','resolved_references','resolved_zero_indices','resolved_after_gaps','resolved_with_original_null_capture_link','raw_stat_field_comparisons','shared_stat_records')}))
