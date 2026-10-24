"""Compare every record byte/typed row and all preserved schema8 history."""
from contextlib import closing
from collections import Counter
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database
from records_reader import records_payload,decode_record_word,GETTER_CORE
from query import record_book,export_jsonl

def digest(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

dest=RUN/'06_执行/increment10';dest.mkdir(parents=True,exist_ok=False)
sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/records-live-01';manifest=json.loads((capture/'records-manifest.json').read_bytes())
report=json.loads((capture/'records-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,expected in report['artifact_sha256'].items():assert digest((capture/name).read_bytes())==expected,name
assert report['reader_sha256']==digest((APP/'records_reader.py').read_bytes())
trace=report['read_trace'];assert all(x['success'] for x in trace)
assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
raw=(capture/'record-book.bin').read_bytes();table=manifest['descriptors']['39'];assert len(raw)==table['count']*52
for start in range(0,table['count'],1000):
    size=min(1000,table['count']-start)*52
    for off in range(0,size,1200):
        at=start*52+off;part=raw[at:at+min(1200,size-off)]
        assert (table['address']+at,len(part),digest(part)) in calls
assert GETTER_CORE in (capture/'record-getter.bin').read_bytes()
assert manifest['capture_coverage']=='COMPLETE_NATIVE_COUNT'
for i,row in enumerate(manifest['record_rows']):assert decode_record_word(raw[i*52:(i+1)*52],i)==row,i
assert not manifest['game_writes'] and manifest['player_struct_reads']==0
for event in trace:
    assert event['operation'] in ('OpenProcess','ReadProcessMemory','CloseHandle')
    if event['operation']=='ReadProcessMemory':assert event['label'].startswith('RECORDS_') and event['requested_bytes']<=1200
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding)
payload=records_payload(binding,manifest,[],report['observed_at'],unit.split(':',1)[1]);old_rows=compared=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT source_grade FROM capture_runs WHERE run_id=?',(unit,)).fetchone()[0]=='LIVE_READ'
    with closing(connect(save/'world-v8.sqlite',True)) as old:
        for table_name,spec in TABLES.items():
            if table_name=='saves':continue
            for before in old.execute('SELECT * FROM '+ident(table_name)):
                after=c.execute(f'SELECT * FROM {ident(table_name)} WHERE {ident(spec.key)}=?',(before[spec.key],)).fetchone()
                assert after is not None and all(after[k]==before[k] for k in before.keys()),table_name;old_rows+=1
    for table_name,rows in payload['facts'].items():
        spec=TABLES[table_name]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table_name}:{i}');actual=c.execute(f'SELECT * FROM {ident(table_name)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual is not None and all(actual[k]==v for k,v in expected.items()),(table_name,key);compared+=1
    assert c.execute('''SELECT count(*) FROM season_record_entries WHERE unit_id=? AND
      (season_id IS NOT NULL OR occurred_at IS NOT NULL OR holder_player_id IS NOT NULL OR holder_team_id IS NOT NULL)''',(unit,)).fetchone()[0]==0
    assert c.execute('SELECT count(*) FROM season_award_instances WHERE unit_id=?',(unit,)).fetchone()[0]==0
old_hash=digest((save/'world-v8.sqlite').read_bytes())
assert old_hash==json.loads((RUN/'06_执行/increment09/settings_world_report.json').read_bytes())['world_sqlite_sha256']
first=record_book(db);write(queries/'record-book-first-page.json',first)
write(queries/'wilt-records-native-008f.json',record_book(db,category_code=0x8f,subject_name='Wilt Chamberlain'))
indices=[];after=-1;pages=0
while True:
    page=record_book(db,unit_id=unit,after_index=after,limit=10000);pages+=1
    indices.extend(r['source_row_index'] for r in page['records'])
    if not page['has_more']:break
    after=page['next_after_index']
assert indices==list(range(table['count']))
temp_export=RUN/'_runtime/record-book-full-10.jsonl';export=export_jsonl(db,temp_export,'season_record_entries',limit=100000)
with temp_export.open('rb') as src,gzip.open(queries/'record-book-full.jsonl.gz','wb') as dst:shutil.copyfileobj(src,dst)
for path in queries.glob('*.json'):
    content=path.read_text(encoding='utf-8').lower();assert not any(x in content for x in ('payload_ref','"address"','raw_player_hex','protected_value_ref','potential'))
archives={}
for name in ('records-probe-01','records-live-01'):
    directory=RUN/'_runtime'/name;archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(directory.iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':digest(archive.read_bytes())}
for name in ('record-sources-pe-inspection.json','inspect_record_sources_pe.py'):
    path=RUN/'_runtime'/name;shutil.copyfile(path,sources/name);archives[name]={'sha256':digest(path.read_bytes())}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v9.sqlite.gz','wb') as dst:shutil.copyfileobj(src,dst)
summary={'status':'COMPLETE_NATIVE_RECORD_BOOK_AND_QUERY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
 'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
 'latest_unit':unit,'source_pid':report['pid'],'latest_counts':result['counts'],
 'old_schema8_rows_preserved':old_rows,'old_database_byte_hash_unchanged':True,'source_to_typed_rows_compared':compared,
 'source_reader_at_acquisition_sha256':report['reader_sha256'],'player_structs_requested':0,'game_writes':False,
 'native_categories':len(set(r['native_category_code'] for r in manifest['record_rows'])),
 'unmapped_category_rows':sum(r['category_label_candidate'] is None for r in manifest['record_rows']),
 'date_candidate_status_counts':dict(Counter(r['date_status'] for r in manifest['record_rows'])),
 'pagination_rows_verified':len(indices),'pagination_pages':pages,'export_rows':export['rows'],
 'full_export_uncompressed_sha256':digest(temp_export.read_bytes()),'world_sqlite_sha256':digest(db.read_bytes()),
 'independent_review':False,'full_goal_complete':False}
write(dest/'records_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_records_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','old_schema8_rows_preserved','source_to_typed_rows_compared','pagination_rows_verified','native_categories')}))
