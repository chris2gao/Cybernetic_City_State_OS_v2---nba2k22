import gzip,hashlib,json,shutil,struct,sys,tarfile
from collections import Counter,defaultdict
from contextlib import closing
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment32';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,VERSION
from live_world import read_binding,bound_database
from family_codec import decode_fixed_utf16
from staff_history_reader import PROFILE,classify_reference
from query import native_staff_history
from observation_scope import query_at
from database_operations import file_sha256
from process_session import owner_is_live
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
before=json.loads((dest/'before.json').read_bytes());worker=json.loads((dest/'worker-result.json').read_bytes());assert worker['status']=='ACTUAL_ANNUAL_STAFF_HISTORY_V23_AND_SAME_YEAR_SKIP_SUCCEEDED' and not owner_is_live(worker['worker_identity']);unit=worker['unit']['unit_id'];binding,_=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding)
batch=json.loads((r/'staff-history-refresh-32/refresh-report.json').read_bytes());source=r/'staff-history-refresh-32'/batch['sources'][0]['directory'];manifest=json.loads((source/'staff-history-manifest.json').read_bytes());trace=json.loads((source/'staff-history-report.json').read_bytes())['read_trace'];scalar_checks=link_checks=identity_checks=private_checks=0
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS prior',(str(db.with_name(before['database_file'])),));preserved=0
    for table,count in before['row_counts'].items():
        columns=[row[1] for row in conn.execute('PRAGMA prior.table_info("'+table+'")') if not (table=='saves' and row[1]=='schema_version')];key=next(row[1] for row in conn.execute('PRAGMA prior.table_info("'+table+'")') if row[5]);different=' OR '.join('a."'+col+'" IS NOT b."'+col+'"' for col in columns)
        mismatch=conn.execute('SELECT count(*) FROM prior."'+table+'" a LEFT JOIN main."'+table+'" b ON a."'+key+'"=b."'+key+'" WHERE b."'+key+'" IS NULL OR '+different).fetchone()[0];assert mismatch==0,table;preserved+=count
    counts={table:conn.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0] for table in TABLES};assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    old_annual=[dict(row) for row in conn.execute('SELECT run_id,refresh_family,refresh_period_year FROM capture_runs WHERE refresh_family IS NOT NULL AND run_id!=? ORDER BY run_id',(unit,))];assert old_annual==before['annual_buckets']
    subjects={row['source_staff_index']:dict(row) for row in conn.execute('SELECT * FROM native_staff_history_subjects WHERE unit_id=?',(unit,))};stats={row['source_stat_index']:dict(row) for row in conn.execute('SELECT * FROM native_coach_stat_observations WHERE unit_id=?',(unit,))};assert len(subjects)==manifest['staff_count'];refs=defaultdict(set);statuses=Counter();links={}
    artifact_checks=0
    for artifact in conn.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        relative=Path(artifact['payload_ref']);path=source/relative.name if relative.parts[0]==source.name else app/relative.name
        assert path.stat().st_size==artifact['byte_count'] and file_sha256(path)==artifact['sha256'];artifact_checks+=1
    for row in conn.execute('SELECT * FROM native_staff_stat_links WHERE unit_id=?',(unit,)):links[(row['history_subject_id'],row['array_position'])]=dict(row)
    for index,subject in subjects.items():
        raw=(source/f'staff-{index}.bin').read_bytes();assert len(raw)==162 and subject['native_staff_id_raw']==int.from_bytes(raw[160:162],'little');identity_checks+=1
        try:name=(decode_fixed_utf16(raw[:40])+' '+decode_fixed_utf16(raw[40:80])).strip();assert subject['observed_name']==name;identity_checks+=1
        except UnicodeError:assert subject['name_status']=='INVALID_UTF16_PREFIX'
        for position,value in enumerate(struct.unpack('<40h',raw[80:160])):
            row=links[(subject['history_subject_id'],position)];assert row['native_stat_index_signed']==value;status=classify_reference(value,manifest['stat_bank_count']);assert row['link_status']==status;statuses[status]+=1;link_checks+=1
            if 0<=value<manifest['stat_bank_count']:assert row['coach_stat_id']==stats[value]['coach_stat_id'];refs[value].add(index)
            else:assert row['coach_stat_id'] is None
    assert len(links)==40*len(subjects) and set(stats)==set(refs)
    for index,row in stats.items():
        raw=(source/f'stat-{index}.bin').read_bytes();assert len(raw)==12 and row['stat_year'] is None and row['subject_reference_count']==len(refs[index])
        for spec in PROFILE['stat_fields'].values():
            f=spec['binding'];value=int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little');assert row[spec['column']]==value;scalar_checks+=1
    assert conn.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0]==40
name_reads=[read for read in trace if read.get('operation')=='ReadProcessMemory' and read['label']=='ANNUAL_STAFF_PUBLIC_NAME'];ref_reads=[read for read in trace if read.get('operation')=='ReadProcessMemory' and read['label']=='ANNUAL_STAFF_REFERENCES_AND_UID'];assert len(name_reads)==len(ref_reads)==len(subjects)
if name_reads:
    staff_base=int(name_reads[0]['address'],16)-48
    for index,(name_read,ref_read) in enumerate(zip(name_reads,ref_reads)):
        assert int(name_read['address'],16)==staff_base+352*index+48 and int(ref_read['address'],16)==staff_base+352*index+136
    descriptor=next(read for read in trace if read.get('operation')=='ReadProcessMemory' and read['label']=='STAFF_HISTORY_DESCRIPTOR:19');assert descriptor['sha256']==hashlib.sha256(struct.pack('<QQ',len(subjects),staff_base)).hexdigest()
if stats:
    stat_reads=[read for read in trace if read.get('operation')=='ReadProcessMemory' and read['label']=='ANNUAL_COACH_STAT_RECORD'];assert len(stat_reads)==len(stats);first_index=min(stats);stat_base=int(stat_reads[0]['address'],16)-12*first_index
    for index,read in zip(sorted(stats),stat_reads):assert int(read['address'],16)==stat_base+12*index and read['requested_bytes']==12 and read['sha256']==file_sha256(source/f'stat-{index}.bin')
    descriptor=next(read for read in trace if read.get('operation')=='ReadProcessMemory' and read['label']=='STAFF_HISTORY_DESCRIPTOR:21');assert descriptor['sha256']==hashlib.sha256(struct.pack('<QQ',manifest['stat_bank_count'],stat_base)).hexdigest()
for read in trace:
    if read.get('operation')=='ReadProcessMemory' and read['label'].startswith(('ANNUAL_STAFF_PUBLIC_NAME','ANNUAL_STAFF_REFERENCES_AND_UID')):
        assert read['requested_bytes'] in (80,82) and read['success'];private_checks+=1
    assert not (read.get('operation')=='ReadProcessMemory' and 'PLAYER' in read.get('label',''))
skip_batch=json.loads((r/'staff-history-skip-32/refresh-report.json').read_bytes());skip_dir=r/'staff-history-skip-32'/skip_batch['sources'][0]['directory'];skip=json.loads((skip_dir/'ingest-result.json').read_bytes());assert skip['status']=='already_refreshed' and skip['previous_unit_id']==unit and not skip['full_source_acquisition'];assert all(not any(s in read.get('label','') for s in ('ANNUAL_STAFF','ANNUAL_COACH','STAFF_HISTORY_DESCRIPTOR')) for read in skip['read_trace'])
queries=dest/'queries';queries.mkdir(exist_ok=True);first=native_staff_history(db,limit=2);write(queries/'first-staff-history-page.json',first);before_query=query_at(db,batch['started_at'],'native_staff_history');assert before_query['result']['status']=='NOT_OBSERVED';write(queries/'before-source-as-of.json',before_query)
cursor=-1;queried=0
while True:
    page=native_staff_history(db,unit_id=unit,after_index=cursor,limit=50);queried+=len(page['records'])
    if not page['has_more']:break
    cursor=page['next_after_index']
assert queried==len(subjects)
assert file_sha256(db.with_name(before['database_file']))==before['database_sha256'] and file_sha256(db)==worker['after_database_sha256']
report={'status':'ACTUAL_ANNUAL_STAFF_HISTORY_RAW_REFERENCES_FIELDS_QUERIES_AND_PRIOR_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'unit_id':unit,'prior_rows_preserved':preserved,'prior_tables_preserved':len(before['row_counts']),'total_rows':sum(counts.values()),'successful_units':40,'source_staff_count':len(subjects),'referenced_coach_stat_records':len(stats),'identity_comparisons':identity_checks,'signed_reference_comparisons':link_checks,'scalar_comparisons':scalar_checks,'public_staff_interval_checks':private_checks,'reference_status_counts':dict(statuses),'shared_stat_records':sum(len(s)>1 for s in refs.values()),'stat_years_all_null':True,'canonical_subject_aliases':sum(s['staff_id'] is not None for s in subjects.values()),'query_subjects_verified':queried,'old_annual_families_unchanged':True,'same_year_skip_no_staff_or_stat_values_read':True,'old_database_retained_unchanged':True,'database_sha256':worker['after_database_sha256'],'game_writes':False,'computer_use_used':False,'capacity_work_executed':False,'independent_acceptance':False,'full_goal_complete':False}
write(dest/'actual-staff-history-report.json',report)
report['source_artifact_hashes_verified']=artifact_checks;write(dest/'actual-staff-history-report.json',report)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('inspect_staff_history32.py','read_staff_history_metadata32.py','start_staff_history_metadata32.ps1','label_staff_history32.py','read_staff_slot_enum32.py','start_staff_slot_enum32.ps1','label_staff_slot_enum32.py','inspect_staff_stat_consumers32.py','extract_staff_stat_code32.py','build_staff_history_profile32.py','prepare_increment32.py','run_staff_history_worker32.py','start_staff_history_worker32.ps1','audit_actual_staff_history32.py'):shutil.copyfile(r/name,scripts/name)
archive=dest/'native-history-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('staff-history-metadata-32','staff-slot-enum-32','staff-history-32-labeled.json','staff-stat-code32.json','staff-stat-consumer-candidates32.json','reconnect-history-32','staff-history-refresh-32','staff-history-skip-32'):tar.add(r/name,arcname=name)
write(dest/'native-history-evidence.archive.json',{'file':archive.name,'bytes':archive.stat().st_size,'sha256':file_sha256(archive),'restricted_owner_evidence':True,'game_save_included':False})
# Retain a full portable fact snapshot as bounded Git parts.
part=1;parts=[];stream_hash=hashlib.sha256();current=None;size=0;digest=None
class Parts:
    def write(self,data):
        global part,current,size,digest
        stream_hash.update(data);total=len(data);offset=0
        while offset<len(data):
            if current is None:current=(dest/f'world-v23.sqlite.gz.part{part:03d}').open('wb');size=0;digest=hashlib.sha256()
            chunk=data[offset:offset+min(len(data)-offset,32*1024*1024-size)];current.write(chunk);digest.update(chunk);size+=len(chunk);offset+=len(chunk)
            if size==32*1024*1024:self.close_part()
        return total
    def flush(self):
        if current:current.flush()
    def close_part(self):
        global part,current
        if current:current.close();parts.append({'file':Path(current.name).name,'bytes':size,'sha256':digest.hexdigest()});part+=1;current=None
sink=Parts()
with db.open('rb') as src,gzip.GzipFile(fileobj=sink,mode='wb',compresslevel=6,mtime=0) as gz:
    while block:=src.read(4*1024*1024):gz.write(block)
sink.close_part();write(dest/'world-v23.snapshot.json',{'database_file':db.name,'database_sha256':file_sha256(db),'stream_sha256':stream_hash.hexdigest(),'parts':parts,'schema_version':VERSION,'tables':len(TABLES),'rows':sum(counts.values())})
(dest/'.gitattributes').write_text('*.gz.part* -text\n*.tar.gz -text\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','source_staff_count','referenced_coach_stat_records','signed_reference_comparisons','scalar_comparisons','total_rows')}))
