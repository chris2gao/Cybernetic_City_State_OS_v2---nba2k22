"""Actual native stat/reference decoding, history and physical privacy audit."""
from bisect import bisect_right
from collections import Counter
from contextlib import closing
import gzip,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
RUN=Path(__file__).resolve().parents[1];ROOT=RUN.parents[3];APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(APP))
from engine import connect,summarize
from schema_model import TABLES,ident
from live_world import read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from family_codec import decode_fixed_utf16
from award_reader import honors_payload,decode_stat_record,PROFILE_PATH,AWARD_COLUMNS
from query import native_honors,player_card,export_jsonl
def digest(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
dest=RUN/'06_执行/increment11';dest.mkdir(parents=True,exist_ok=False);sources=dest/'native_sources';sources.mkdir();queries=dest/'queries';queries.mkdir()
capture=RUN/'_runtime/honors-live-01';m=json.loads((capture/'honors-manifest.json').read_bytes());report=json.loads((capture/'honors-report.json').read_bytes());result=json.loads((capture/'ingest-result.json').read_bytes());unit=result['unit_id']
for name,expected in report['artifact_sha256'].items():assert digest((capture/name).read_bytes())==expected,name
assert report['reader_sha256']==digest((APP/'award_reader.py').read_bytes());assert report['profile_sha256']==digest(PROFILE_PATH.read_bytes())
trace=report['read_trace'];assert all(x['success'] for x in trace);assert trace[0]['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
calls={(int(x['address'],16),x['returned_bytes'],x['sha256']) for x in trace if x['operation']=='ReadProcessMemory'}
def proof(address,raw):assert (address,len(raw),digest(raw)) in calls
pd=m['descriptors']['1'];sd=m['descriptors']['24'];raw=(capture/'player-stat-bank.bin').read_bytes();projection=(capture/'player-public-projection.bin').read_bytes();profile=json.loads(PROFILE_PATH.read_bytes())
for start in range(0,sd['count'],1000):
    size=min(1000,sd['count']-start)*48
    for off in range(0,size,1200):
        at=start*48+off;proof(sd['address']+at,raw[at:at+min(1200,size-off)])
for i,row in enumerate(m['stat_records']):assert row==dict(source_stat_index=i,**decode_stat_record(raw[i*48:(i+1)*48],profile['stat_fields']))
assert m['season_stats_array_count']==25;stride=144
for p in m['players']:
    i=p['source_player_index'];address=pd['address']+i*1264;part=projection[i*stride:(i+1)*stride]
    for offset,data in ((0,part[:80]),(244,part[80:82]),(760,part[82:86]),(96,part[86:94]),(252,part[94:])):proof(address+offset,data)
    assert int.from_bytes(part[80:82],'little')==p['native_unique_id_raw'];assert int.from_bytes(part[82:86],'little')==p['preserved_id_raw']
    if p['name_status']=='OBSERVED_UTF16_PREFIX':assert (decode_fixed_utf16(part[40:80])+' '+decode_fixed_utf16(part[:40])).strip()==p['observed_name']
    links=[r for r in m['stat_links'][i*25:(i+1)*25]]
    assert [r['native_stat_index_raw'] for r in links]==list(__import__('struct').unpack('<25H',part[94:]))
forbidden=sorted((pd['address']+i*1264+low,pd['address']+i*1264+high) for i in range(pd['count']) for low,high in RESTRICTED_PLAYER_RANGES);starts=[a for a,b in forbidden]
for event in trace:
    if event['operation']!='ReadProcessMemory':continue
    start=int(event['address'],16);end=start+event['requested_bytes'];j=bisect_right(starts,end-1)-1
    assert j<0 or forbidden[j][1]<=start,('restricted_read_overlap',event['label'])
sample=(capture/'public-family-privacy-probe.bin').read_bytes();assert len(sample)==1264
for low,high in RESTRICTED_PLAYER_RANGES:assert not any(sample[low:high])
save=RUN/'_runtime/world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old_rows=compared=0
with closing(connect(db,True)) as c:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall()
    canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
    p=honors_payload(binding,m,[],report['observed_at'],unit.split(':',1)[1],canonical)
    with closing(connect(save/'world-v9.sqlite',True)) as old:
        for table,spec in TABLES.items():
            if table=='saves' or table in ('native_player_stat_observations','native_player_sources','native_player_stat_links'):continue
            for before in old.execute('SELECT * FROM '+ident(table)):
                after=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(before[spec.key],)).fetchone();assert after and all(after[k]==before[k] for k in before.keys()),table;old_rows+=1
    for table,rows in p['facts'].items():
        spec=TABLES[table]
        for i,expected in enumerate(rows):
            key=expected.get(spec.key,f'{unit}:{table}:{i}');actual=c.execute(f'SELECT * FROM {ident(table)} WHERE {ident(spec.key)}=?',(key,)).fetchone()
            assert actual and all(actual[k]==v for k,v in expected.items()),(table,key);compared+=1
    assert c.execute('SELECT count(*) FROM season_award_instances WHERE unit_id=?',(unit,)).fetchone()[0]==0
old_hash=digest((save/'world-v9.sqlite').read_bytes());assert old_hash==json.loads((RUN/'06_执行/increment10/records_world_report.json').read_bytes())['world_sqlite_sha256']
mvps=native_honors(db,flag='mvp_raw',limit=1000);write(queries/'native-mvp-source.json',mvps);write(queries/'native-honor-first-page.json',native_honors(db))
write(queries/'curry-identity-and-families.json',player_card(db,'player:native:1612'))
indices=[];after=-1;pages=0
while True:
    page=native_honors(db,unit_id=unit,after_index=after,limit=1000);pages+=1;indices.extend(r['source_stat_index'] for r in page['records'])
    if not page['has_more']:break
    after=page['next_after_index']
expected=[r['source_stat_index'] for r in m['stat_records'] if any(r[k]>0 for k in AWARD_COLUMNS)];assert indices==expected
exports={}
for table in ('native_player_stat_observations','native_player_sources','native_player_stat_links'):
    temporary=RUN/'_runtime'/('increment11-'+table+'.jsonl');exports[table]=export_jsonl(db,temporary,table,limit=200000)['rows']
    with temporary.open('rb') as src,gzip.open(queries/(table+'.jsonl.gz'),'wb') as dst:shutil.copyfileobj(src,dst)
for path in queries.glob('*.json'):
    content=path.read_text(encoding='utf-8').lower();assert not any(s in content for s in ('potential','payload_ref','"address"','protected_value_ref'))
archives={}
for name in ('award-metadata-01','award-metadata-02','award-metadata-03','award-metadata-04','honors-probe-01','honors-live-01'):
    archive=sources/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted((RUN/'_runtime'/name).iterdir()):
            if path.is_file():tar.add(path,arcname=path.name,recursive=False)
    archives[name]={'archive':archive.name,'sha256':digest(archive.read_bytes())}
research_archive=sources/'static-type-discovery.tar.gz'
with tarfile.open(research_archive,'w:gz') as tar:
    for name in ('native-type-initializer-map.json','map_native_type_initializers.py','awards-types-pe-inspection.json','inspect_awards_types_pe.py','award-type-ref-disassembly.json','disassemble_award_type_refs.py','award-metadata-labeled.json','resolve_award_field_labels.py'):
        tar.add(RUN/'_runtime'/name,arcname=name,recursive=False)
archives['static_type_discovery']={'archive':research_archive.name,'sha256':digest(research_archive.read_bytes())}
write(sources/'source_manifest.json',archives);write(sources/'save_binding.json',binding)
with db.open('rb') as src,gzip.open(dest/'world-v10.sqlite.gz','wb') as dst:shutil.copyfileobj(src,dst)
summary={'status':'NATIVE_STAT_HONOR_FIELDS_REFERENCES_PRIVACY_AND_HISTORY_VERIFIED_FULL_GOAL_INCOMPLETE','schema':summarize(db),
 'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
 'latest_unit':unit,'source_pid':report['pid'],'latest_counts':result['counts'],'old_schema9_rows_preserved':old_rows,
 'old_database_byte_hash_unchanged':True,'source_to_typed_rows_compared':compared,'known_restricted_player_bytes_requested':0,
 'native_mvp_flag_slots':mvps['matching_native_stat_slots'],'native_honor_flag_slots':len(indices),'pinned_pages_verified':pages,
 'native_stat_link_status_counts':m['link_status_counts'],'source_score_identity_counts':dict(Counter(r['scoring_identity_status'] for r in m['stat_records'])),
 'export_rows':exports,'world_sqlite_sha256':digest(db.read_bytes()),'game_writes':False,'independent_review':False,'full_goal_complete':False}
write(dest/'honors_world_report.json',summary);shutil.copyfile(__file__,dest/'executed_honors_audit.py')
(dest/'.gitattributes').write_text('*.gz -text\n*.json -text whitespace=cr-at-eol\n*.py -text\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ('status','old_schema9_rows_preserved','source_to_typed_rows_compared','known_restricted_player_bytes_requested','native_mvp_flag_slots','native_honor_flag_slots')}))
