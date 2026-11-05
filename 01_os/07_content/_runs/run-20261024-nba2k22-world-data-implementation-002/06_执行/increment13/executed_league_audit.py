"""Reconcile actual native bytes, source facts, canonical archives and role queries."""
import gzip,hashlib,json,shutil,struct,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path.cwd();RUN=Path(__file__).resolve().parent.parent;APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from league_ingest import league_payload
from league_reader import PROFILE_PATH,decode_history_record,decode_social_message,decode_native_date,unsigned_fields
from live_world import _json,read_binding,bound_database
from query import awards,league_history,native_news,native_transactions,export_jsonl
from schema_model import TABLES,ident

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):_json(path,value)
runtime=RUN/'_runtime';capture=runtime/'league-live-v12';dest=RUN/'06_执行/increment13';dest.mkdir(parents=True,exist_ok=True)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir();profile=json.loads(PROFILE_PATH.read_bytes())
overall=json.loads((capture/'league-report.json').read_bytes());assert overall['status']=='LEAGUE_HISTORY_AWARDS_AND_ORDINARY_EVENTS_CAPTURED'
save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
compared=decoded=0;details={}
with connect(db,True) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall()
    for name,directory in (('history','history-first'),('news','news-first')):
        folder=capture/directory;m=json.loads((folder/'league-source-manifest.json').read_bytes());report=json.loads((folder/'league-source-report.json').read_bytes())
        result=overall['results'][name];unit=result['unit_id'];trace=report['read_trace']
        for filename,digest in report['artifact_sha256'].items():assert sha(folder/filename)==digest,filename
        for filename,digest in report['executed_code_sha256'].items():assert sha(APP/filename)==digest,filename
        assert all(e['success'] for e in trace) and trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
        labels=[e['label'] for e in trace if e['operation']=='ReadProcessMemory']
        if name=='history':assert not any(label.startswith(('LEAGUE_SOCIAL_','LEAGUE_TRANSACTIONS:')) for label in labels)
        else:assert not any(label.startswith(('LEAGUE_HISTORY_TABLE:','LEAGUE_AWARD_MATRIX')) for label in labels)
        def prove_chunks(filename,label):
            raw=(folder/filename).read_bytes();calls=[e for e in trace if e['operation']=='ReadProcessMemory' and e['label'].startswith(label+':')]
            assert len(calls)==(len(raw)+1199)//1200
            start=int(calls[0]['address'],16)
            for offset,event in zip(range(0,len(raw),1200),calls):
                part=raw[offset:offset+1200]
                assert event['label']==label+':'+str(offset) and int(event['address'],16)==start+offset
                assert event['returned_bytes']==len(part) and event['sha256']==hashlib.sha256(part).hexdigest()
            return raw
        if name=='history':
            raw=prove_chunks('league-history.bin','LEAGUE_HISTORY_TABLE')
            for i,row in enumerate(m['history']):assert row==decode_history_record(raw[i*152:(i+1)*152],i,profile);decoded+=1
            free=m['manager_slot40_candidate']['free_chain'];invalid={r['source_row_index'] for r in m['history'] if r['values']['Type']==0}
            assert set(free['indices'])==invalid and len(invalid)==4000
            matrix=(folder/'season-award-winner-matrix.bin').read_bytes();assert set(struct.unpack('<75H',matrix))=={65535}
        else:
            raw=prove_chunks('social-messages.bin','LEAGUE_SOCIAL_MESSAGES')
            for r in m['messages']:
                offset=(r['bank_index']*2000+r['source_slot_index'])*124;expected=decode_social_message(raw[offset:offset+124],r['bank_index'],r['source_slot_index'],profile)
                expected['active_prefix_status']='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if r['source_slot_index']<m['social_active_counts'][r['bank_index']] else 'OUTSIDE_DECLARED_COUNT_PREFIX'
                assert r==expected;decoded+=1
            raw=prove_chunks('transactions.bin','LEAGUE_TRANSACTIONS')
            for i,r in enumerate(m['transactions']):
                part=raw[i*320:(i+1)*320];assert r['values']==unsigned_fields(part,profile['bindings']['FRANCHISE_TRANSACTION'])
                assert r['date']==decode_native_date(part[312:316],profile['bindings']['SCHEDULEDATE'])
                for j,item in enumerate(r['items']):assert item==dict(source_item_index=j,**unsigned_fields(part[j*8:(j+1)*8],profile['bindings']['FRANCHISE_TRANSACTION_RECORD']));decoded+=1
            assert m['transaction_count']==0
        payload=league_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1])
        for table,rows in payload['facts'].items():
            spec=TABLES[table]
            for i,expected in enumerate(rows):
                key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
                assert actual and all(actual[k]==value for k,value in expected.items()),(table,key);compared+=1
        details[name]={'unit_id':unit,'counts':result['counts'],'runtime_types_verified':len(m['metadata']),'source_year':m['season_year']}
    assert c.execute('SELECT count(*) FROM season_award_instances').fetchone()[0]==764
    assert c.execute('SELECT count(*) FROM award_recipients WHERE player_id IS NOT NULL OR team_id IS NOT NULL OR staff_id IS NOT NULL').fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM external_transaction_events').fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM game_news_entries WHERE text_body IS NOT NULL OR occurrence_time IS NOT NULL').fetchone()[0]==0
repeat=overall['results']['history_repeat'];calls=[e for e in repeat['read_trace'] if e['operation']=='ReadProcessMemory']
assert repeat['status']=='already_refreshed' and repeat['previous_unit_id']==details['history']['unit_id']
assert all(e['label'].startswith('CADENCE_') for e in calls)
write(queries/'2021-native-awards.json',awards(db,year=2021));write(queries/'2021-mvp.json',awards(db,year=2021,award_code='MVP'))
write(queries/'native-history-first-page.json',league_history(db));write(queries/'native-news-first-page.json',native_news(db));write(queries/'native-transactions.json',native_transactions(db))
assert awards(db,year=2021,award_code='MVP')['awards'][0]['recipients'][0]['player_first_name']=='Nikola'
pages={}
for key,method in (('history',league_history),('news',native_news)):
    count=0;after=-1;unit=details[key]['unit_id'];seen=set()
    while True:
        page=method(db,unit_id=unit,after_index=after,limit=1000)
        for row in page['records']:
            i=row['source_row_index'] if key=='history' else row['bank_index']*2000+row['source_slot_index']
            assert i not in seen;seen.add(i);count+=1
        if not page['has_more']:break
        after=page['next_after_index']
    pages[key]=count
assert pages=={'history':2769,'news':1281}
for path in queries.glob('*.json'):
    content=path.read_text(encoding='utf-8').lower();assert not any(s in content for s in ('potential','payload_ref','"address"','data_u32_raw','string1_fragment'))
exports={}
for table in ('native_league_history_observations','season_award_instances','award_recipients','native_award_matrix_observations'):
    temporary=runtime/('increment13-'+table+'.jsonl');exports[table]=export_jsonl(db,temporary,table,limit=100000)['rows']
    with temporary.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as target:shutil.copyfileobj(src,target)
archives={}
for name in ('history-first','history-repeat','news-first'):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted((capture/name).iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive)}
for name in ('league-metadata-01','league-metadata-02','league-metadata-03','league-source-probe-01'):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted((runtime/name).iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':sha(archive),'scope':'earlier bounded metadata/source investigation; not typed ingest'}
original=json.loads((runtime/'league-source-probe-01/league-source-report.json').read_bytes())
assert sha(runtime/'league_reader_probe_original.py')==original['reader_sha256']
for name in ('league_reader_probe_original.py','capture_league_v12.py','start_league_v12.ps1','migrate_league_v12.py','curate_league_fixture.py'):
    shutil.copyfile(runtime/name,sources/name)
shutil.copyfile(capture/'league-report.json',sources/'league-report.json');shutil.copyfile(runtime/'league-migration-v12/migration-report.json',dest/'migration-report.json')
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v12.sqlite.gz','wb') as target:shutil.copyfileobj(src,target)
migration=json.loads((dest/'migration-report.json').read_bytes());assert sha(save/'world-v11.sqlite')==migration['old_database_sha256']
result={'status':'NATIVE_ARCHIVED_AWARDS_AND_ORDINARY_EVENTS_SOURCE_TO_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE',
    'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
    'schema':summarize(db),'sources':details,'raw_records_or_items_redecoded':decoded,'source_to_typed_rows_compared':compared,
    'old_schema11_rows_preserved':migration['preserved_rows'],'old_schema11_file_hash_unchanged':True,
    'annual_history_repeat_control_calls':len(calls),'annual_history_repeat_control_bytes':sum(e['returned_bytes'] for e in calls),
    'pinned_history_and_news_rows':pages,'export_rows':exports,'world_sqlite_sha256':sha(db),
    'game_writes':False,'player_struct_reads':0,'full_goal_complete':False,'independent_review':False,
    'limits':['Native roster history finality does not certify this save simulating historical years.','Historical subject lifecycle identities remain unbound.','News rendering/parameter meanings and active UI semantics remain unaccepted.','Date epoch/month/time UI, transaction lifecycle and remaining full-system domain/capacity/recovery/acceptance are open.']}
write(dest/'league_world_report.json',result);shutil.copyfile(__file__,dest/'executed_league_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nnative_sources/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('status','raw_records_or_items_redecoded','source_to_typed_rows_compared','old_schema11_rows_preserved','pinned_history_and_news_rows')}))
