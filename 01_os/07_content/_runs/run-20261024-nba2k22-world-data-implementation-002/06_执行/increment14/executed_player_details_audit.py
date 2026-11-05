"""Recheck native public bytes, all detail facts, physical privacy and queries."""
from bisect import bisect_right
from collections import Counter
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from live_world import _json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import detail_payload,reconstruct_projection,projection_ranges
from player_detail_codec import PROFILE,native_contracts,native_badges
from family_codec import decode_fixed_utf16
from query import native_player_details,player_card,player_badges,export_jsonl
from schema_model import TABLES,ident
runtime=RUN/'_runtime';capture=runtime/'player-details-live-v13';dest=RUN/'06_执行/increment14';dest.mkdir(parents=True,exist_ok=True)
sources=dest/'native_sources';sources.mkdir(exist_ok=True);queries=dest/'queries';queries.mkdir(exist_ok=True)
_exclusive_json=_json
def _json(path,value):
    if path.exists():
        assert json.loads(path.read_bytes())==value,('refuse-changing-retained-evidence',path.name)
    else:_exclusive_json(path,value)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((capture/'player-detail-manifest.json').read_bytes());report=json.loads((capture/'player-detail-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,digest in report['artifact_sha256'].items():assert sha(capture/name)==digest,name
for name,digest in report['code_sha256'].items():assert sha(APP/name)==digest,name
trace=report['read_trace'];assert all(e['success'] for e in trace) and trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(e['address'],16),e['returned_bytes'],e['sha256']) for e in trace if e['operation']=='ReadProcessMemory'}
def proof(address,raw):assert (address,len(raw),hashlib.sha256(raw).hexdigest()) in calls
pd=m['descriptors']['1'];stride=m['projection_stride'];ranges=[tuple(r) for r in m['projection_ranges']];assert ranges==projection_ranges()
raw=(capture/'player-detail-public-projections.bin').read_bytes();assert len(raw)==pd['count']*stride
forbidden=sorted((pd['address']+i*1264+low,pd['address']+i*1264+high) for i in range(pd['count']) for low,high in RESTRICTED_PLAYER_RANGES);starts=[low for low,high in forbidden]
for e in trace:
    if e['operation']!='ReadProcessMemory':continue
    start=int(e['address'],16);end=start+e['requested_bytes'];j=bisect_right(starts,end-1)-1
    assert j<0 or forbidden[j][1]<=start,('private-read-overlap',e['label'])
for i,p in enumerate(m['players']):
    part=raw[i*stride:(i+1)*stride];at=0
    for low,high in ranges:proof(pd['address']+i*1264+low,part[at:at+high-low]);at+=high-low
    row=reconstruct_projection(part,ranges)
    assert int.from_bytes(row[244:246],'little')==p['native_unique_id_raw'] and int.from_bytes(row[760:764],'little')==p['preserved_id_raw']
    if p['name_status']=='OBSERVED_UTF16_PREFIX':assert (decode_fixed_utf16(row[40:80])+' '+decode_fixed_utf16(row[:40])).strip()==p['observed_name']
    expected=native_contracts(row);assert all(m['contract_rows'][i][key]==value for key,value in expected.items())
    assert m['badge_rows'][i*98:(i+1)*98]==[{'source_player_index':i,**badge} for badge in native_badges(row)]
    for low,high in RESTRICTED_PLAYER_RANGES:assert row[low:high]==bytes(high-low)
dispatch=PROFILE['badge_base_dispatch']
for key,address in (('code',dispatch['code_start_rva']),('table',dispatch['table_rva'])):
    value=bytes.fromhex(dispatch[key+'_hex'])
    for off in range(0,len(value),1200):proof(0x140000000+address+off,value[off:off+1200])
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);compared=0
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall()
    canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')};teams={r[0] for r in c.execute('SELECT team_id FROM teams')}
    payload=detail_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1],canonical,teams)
    for table,rows in payload['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual and all(actual[k]==value for k,value in expected.items()),(table,key);compared+=1
    matched=c.execute('SELECT count(*) FROM native_player_sources WHERE unit_id=? AND player_id IS NOT NULL',(unit,)).fetchone()[0]
    codes=[dict(r) for r in c.execute('SELECT native_kind,native_code,count(*) AS rows FROM player_badge_values WHERE unit_id=? GROUP BY native_kind,native_code ORDER BY native_kind,native_code',(unit,))]
    assert c.execute('SELECT count(*) FROM player_badge_values WHERE unit_id=? AND native_badge_id=0',(unit,)).fetchone()[0]==0
    alias_impact={name:sum(row[name+'_raw']>((1<<old)-1) for row in m['contract_rows']) for name,old in (('bird_years',4),('years_left_on_contract',4),('euro_stash_years_left',2))}
_json(queries/'native-curry-details.json',native_player_details(db,subject_name='Stephen Curry',unit_id=unit))
card=player_card(db,'player:native:1612');_json(queries/'curry-current-card.json',card)
assert len(player_badges(db,'player:native:1612'))==98
with connect(save/'world-v12.sqlite',True) as old:
    for column,latest in card['families']['player_attribute_snapshots'].items():
        old_value=old.execute(f'''SELECT a.{ident(column)} AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade
            FROM player_attribute_snapshots a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE a.player_id=? AND a.{ident(column)} IS NOT NULL ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',('player:native:1612',)).fetchone()
        if old_value:assert all(latest[key]==value for key,value in dict(old_value).items()),column
        else:assert latest['value'] is None,column
seen=set();after=-1;pages=0
while True:
    page=native_player_details(db,unit_id=unit,after_index=after,limit=100);pages+=1
    for row in page['records']:
        assert row['source_player_index'] not in seen and len(row['base_badges'])==98;seen.add(row['source_player_index'])
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(range(pd['count']))
for path in queries.glob('*.json'):
    public=path.read_text(encoding='utf-8').lower();assert not any(s in public for s in ('potential','payload_ref','"address"','protected_value_ref'))
exports={}
for table in ('player_badge_values','player_contract_observations'):
    temporary=runtime/('increment14-'+table+'.jsonl');exports[table]=export_jsonl(db,temporary,table,limit=1000000)['rows']
    with temporary.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as target:shutil.copyfileobj(src,target)
archives={}
for name,directory in (('player-details-live-v13',capture),('player-detail-metadata-01',runtime/'player-detail-metadata-01')):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive)}
archive=sources/'native-field-and-base-dispatch-research.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('read_player_detail_metadata.py','start_player_detail_metadata.ps1','inspect_player_native_fields.py','player-native-field-inspection.json','compare_player_registered_fields.py',
        'build_player_detail_profile.py','inspect_native_badge_getters.py','native-badge-getter-candidates.json','extract_badge_dispatch.py','badge-dispatch-function.json','prove_badge_dispatch.py','badge-dispatch-proof.json'):
        tar.add(runtime/name,arcname=name,recursive=False)
archives['static_research']={'archive':archive.name,'sha256':sha(archive)}
for name in ('migrate_player_details_v13.py','capture_player_details_v13.py','start_player_details_v13.ps1','curate_player_detail_fixture.py'):shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(runtime/'player-details-migration-v13/migration-report.json',dest/'migration-report.json');_json(sources/'source_manifest.json',archives);_json(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v13.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes());assert sha(save/'world-v12.sqlite')==migration['old_database_sha256']
summary={'status':'NATIVE_FULL_WIDTH_CONTRACTS_BASE_BADGES_PRIVACY_AND_HISTORY_VERIFIED_FULL_GOAL_INCOMPLETE',
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'schema':summarize(db),'source_pid':report['pid'],'unit_id':unit,'latest_counts':result['counts'],
    'complete_source_players':pd['count'],'matched_current_roster_canonical_players':matched,'source_to_typed_rows_compared':compared,
    'all_public_projection_rows_redecoded':pd['count'],'base_badge_dispatch_patterns_verified':dispatch['verified_input_patterns'],
    'old_rows_preserved':migration['preserved_rows'],'old_v12_file_hash_unchanged':True,'known_restricted_player_bytes_requested':0,
    'native_base_badge_code_counts':codes,'native_values_truncated_by_prior_narrow_masks':alias_impact,'pinned_detail_pages':pages,
    'old_attribute_observation_age_preserved':True,'export_rows':exports,'world_sqlite_sha256':sha(db),'world_sqlite_bytes':db.stat().st_size,
    'compressed_world_bytes':(dest/'world-v13.sqlite.gz').stat().st_size,'game_writes':False,'full_goal_complete':False,'independent_review':False,
    'limits':['Base badge decoding is not effective-context/UI certification.','Native salary scale, contract sentinels/UI years and legacy aliases need their stated semantics.','Historical pool source identities are not current canonical or lifecycle identities.','Capacity/recovery, remaining native families and whole-candidate independent/Human acceptance remain incomplete.']}
_json(dest/'player_details_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_player_details_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','source_to_typed_rows_compared','matched_current_roster_canonical_players','old_rows_preserved','native_values_truncated_by_prior_narrow_masks','compressed_world_bytes')}))
