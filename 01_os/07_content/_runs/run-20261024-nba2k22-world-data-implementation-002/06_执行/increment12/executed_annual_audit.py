"""Retain real annual acquisitions, atomic facts, repeats and old DB evidence."""
from bisect import bisect_right
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES,_json
from records_reader import records_payload
from award_reader import honors_payload
from query import native_honors,record_book

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
dest=RUN/'06_执行/increment12';dest.mkdir(parents=True,exist_ok=False)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
runtime=RUN/'_runtime';live=runtime/'annual-live-v11';summary=json.loads((live/'annual-report.json').read_bytes())
assert summary['status']=='ANNUAL_FIRST_CAPTURE_AND_REPEAT_SKIP_VERIFIED'
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
proofs={};compared=0
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
    for family,prefix,builder in (('records','records',records_payload),('honors','honors',honors_payload)):
        directory=live/(family+'-first');m=json.loads((directory/(prefix+'-manifest.json')).read_bytes())
        report=json.loads((directory/(prefix+'-report.json')).read_bytes());r=summary['results'][family];first=r['first'];repeat=r['repeat'];unit=first['unit_id']
        for name,digest in report['artifact_sha256'].items():assert sha(directory/name)==digest,name
        reader='records_reader.py' if family=='records' else 'award_reader.py'
        assert sha(APP/reader)==report['reader_sha256']
        assert all(e['success'] for e in report['read_trace'])
        assert report['read_trace'][0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
        controls=[e for e in repeat['read_trace'] if e['operation']=='ReadProcessMemory']
        assert controls and all(e['label'].startswith('CADENCE_') for e in controls)
        assert repeat['previous_unit_id']==unit and not repeat['full_source_acquisition']
        args=(binding,m,[],report['observed_at'],unit.split(':',1)[1])
        payload=builder(*args,canonical) if family=='honors' else builder(*args)
        for table,rows in payload['facts'].items():
            spec=TABLES[table]
            for i,expected in enumerate(rows):
                key=expected.get(spec.key,f'{unit}:{table}:{i}')
                actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
                assert actual and all(actual[k]==v for k,v in expected.items()),(table,key)
                compared+=1
        periods=c.execute('''SELECT count(*) FROM capture_runs r JOIN capture_units u USING(run_id)
            WHERE r.refresh_family=? AND r.refresh_period_year=? AND r.source_grade='LIVE_READ' AND u.unit_status='success' ''',
            (first['refresh_family'],first['refresh_period_year'])).fetchone()[0]
        assert periods==1
        if family=='honors':
            pd=m['descriptors']['1'];forbidden=sorted((pd['address']+i*1264+lo,pd['address']+i*1264+hi) for i in range(pd['count']) for lo,hi in RESTRICTED_PLAYER_RANGES)
            starts=[lo for lo,hi in forbidden]
            for event in report['read_trace']:
                if event['operation']!='ReadProcessMemory':continue
                start=int(event['address'],16);end=start+event['requested_bytes'];j=bisect_right(starts,end-1)-1
                assert j<0 or forbidden[j][1]<=start,('restricted-byte-overlap',event['label'])
        proofs[family]={'annual_unit_id':unit,'game_season_year':first['refresh_period_year'],
            'fact_counts':first['counts'],'repeat_status':repeat['status'],'repeat_native_control_read_calls':len(controls),
            'repeat_native_control_bytes':sum(e['returned_bytes'] for e in controls),'full_repeat_source_acquired':False}
    assert c.execute('SELECT count(*) FROM capture_runs WHERE refresh_family IS NOT NULL').fetchone()[0]==2
    assert c.execute('SELECT count(*) FROM season_award_instances').fetchone()[0]==0
_json(queries/'record-book-first-page.json',record_book(db))
_json(queries/'native-honor-first-page.json',native_honors(db))
for path in queries.glob('*.json'):
    content=path.read_text(encoding='utf-8').lower()
    assert not any(word in content for word in ('potential','payload_ref','"address"','protected_value_ref'))
archives={}
for family in ('records-first','records-repeat','honors-first','honors-repeat'):
    directory=live/family;archive=sources/(family+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[family]={'archive':archive.name,'sha256':sha(archive)}
for name in ('annual_capture_v11.py','start_annual_live_v11.ps1','annual_verify_migration_v11.py'):
    shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(live/'annual-report.json',sources/'annual-report.json')
shutil.copyfile(runtime/'annual-migration-v11/migration-report.json',dest/'migration-report.json')
_json(sources/'source_manifest.json',archives);_json(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v11.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes())
assert sha(save/'world-v10.sqlite')==migration['old_database_sha256_before']
result={'status':'ANNUAL_HISTORY_AND_HONOR_REFRESH_REAL_SOURCE_AND_REPEATED_SKIP_VERIFIED',
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'schema':summarize(db),'source_pid':2132,'save_id':binding['save_id'],'annual_families':proofs,
    'source_to_typed_rows_compared':compared,'old_fact_rows_preserved':migration['preserved_fact_rows'],
    'old_database_hash_unchanged':True,'legacy_periods_relabelled':0,'known_restricted_player_bytes_requested':0,
    'world_sqlite_sha256':sha(db),'game_writes':False,'full_goal_complete':False,
    'limits':['Current native honor flags are not accepted final awards.','League-history annual family remains reserved pending typed adapter.','Whole-system capacity/recovery, independent review and Human acceptance remain incomplete.']}
_json(dest/'annual_world_report.json',result)
shutil.copyfile(__file__,dest/'executed_annual_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\n*.ps1 -text whitespace=cr-at-eol\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','source_to_typed_rows_compared','old_fact_rows_preserved','annual_families')}))
