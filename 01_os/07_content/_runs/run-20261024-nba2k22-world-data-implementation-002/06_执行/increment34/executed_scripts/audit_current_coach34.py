import gzip,hashlib,json,shutil,struct,sys,tarfile
from collections import Counter
from contextlib import closing
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;run=r.parent;dest=run/'06_执行/increment34';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,VERSION
from live_world import read_binding,bound_database
from family_codec import decode_fixed_utf16
from query import current_coach_stats
from observation_scope import query_at
from database_operations import file_sha256
from process_session import owner_is_live
from current_coach_stat_reader import COUNTER_COLUMNS
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
before=json.loads((dest/'before.json').read_bytes());worker=json.loads((dest/'worker-result.json').read_bytes());assert worker['status']=='ACTUAL_ORDINARY_CURRENT_COACH_V24_TWO_OBSERVATIONS_SUCCEEDED' and not owner_is_live(worker['worker_identity']);binding,_=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',binding);identity_checks=reference_checks=stat_checks=private_checks=award_checks=artifact_checks=0;source_results=[]
with closing(connect(db,True)) as conn:
    conn.execute('ATTACH DATABASE ? AS prior',(str(db.with_name(before['database_file'])),));preserved=0
    for table,count in before['row_counts'].items():
        columns=[row[1] for row in conn.execute('PRAGMA prior.table_info("'+table+'")') if not (table=='saves' and row[1]=='schema_version')];key=next(row[1] for row in conn.execute('PRAGMA prior.table_info("'+table+'")') if row[5]);different=' OR '.join('a."'+col+'" IS NOT b."'+col+'"' for col in columns)
        assert conn.execute('SELECT count(*) FROM prior."'+table+'" a LEFT JOIN main."'+table+'" b ON a."'+key+'"=b."'+key+'" WHERE b."'+key+'" IS NULL OR '+different).fetchone()[0]==0,table;preserved+=count
    counts={table:conn.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0] for table in TABLES};assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    annual=[dict(row) for row in conn.execute('SELECT run_id,refresh_family,refresh_period_year FROM capture_runs WHERE refresh_family IS NOT NULL ORDER BY run_id')];assert annual==before['annual_buckets'];canonical={row['staff_id']:row['display_name'] for row in conn.execute('SELECT staff_id,display_name FROM staff_members')}
    for number in (1,2):
        batch=json.loads((r/f'current-coach-refresh-34-{number}/refresh-report.json').read_bytes());entry=batch['sources'][0];unit=entry['unit']['unit_id'];assert entry['unit']==worker['sources'][number-1]['unit'];source=r/f'current-coach-refresh-34-{number}'/entry['directory'];m=json.loads((source/'current-coach-manifest.json').read_bytes());trace=json.loads((source/'current-coach-report.json').read_bytes())['read_trace'];rows={row['source_staff_index']:dict(row) for row in conn.execute('SELECT * FROM native_current_coach_stat_observations WHERE unit_id=?',(unit,))};assert len(rows)==m['staff_count'];uid=Counter(row['native_staff_id_raw'] for row in rows.values());refs=Counter(row['native_stat_index_signed'] for row in rows.values() if row['source_stat_index'] is not None)
        staff_desc=(source/'descriptor-19.bin').read_bytes();stat_desc=(source/'descriptor-21.bin').read_bytes();staff_count,staff_base=struct.unpack('<QQ',staff_desc);stat_count,stat_base=struct.unpack('<QQ',stat_desc);assert staff_count==len(rows) and stat_count==m['stat_bank_count'];resolved=0
        for index,row in rows.items():
            raw=(source/f'staff-{index}.bin').read_bytes();assert len(raw)==84 and row['native_staff_id_raw']==int.from_bytes(raw[80:82],'little');identity_checks+=1;native_index=struct.unpack('<h',raw[82:84])[0];assert row['native_stat_index_signed']==native_index;reference_checks+=1
            try:name=(decode_fixed_utf16(raw[:40])+' '+decode_fixed_utf16(raw[40:80])).strip();assert row['observed_name']==name;identity_checks+=1
            except UnicodeError:assert row['name_status']=='INVALID_UTF16_PREFIX'
            candidate='staff:native:'+str(row['native_staff_id_raw']);accepted=uid[row['native_staff_id_raw']]==1 and row['name_status']=='OBSERVED_UTF16' and canonical.get(candidate)==row['observed_name'];assert row['staff_id']==(candidate if accepted else None) and row['stat_year'] is None
            if 0<=native_index<stat_count:
                resolved+=1;raw=(source/f'stat-{native_index}.bin').read_bytes();assert len(raw)==10;values=struct.unpack('<5H',raw);assert row['source_stat_index']==native_index and row['subject_reference_count']==refs[native_index]
                for column,value in zip(('next_free_raw',*COUNTER_COLUMNS),values):assert row[column]==value;stat_checks+=1
                marker='MATCHES_NATIVE_ALLOCATION_MARKER' if values[0]==65535 else 'DIFFERS_FROM_NATIVE_ALLOCATION_MARKER; REACHABILITY_UNPROVED';assert row['native_allocation_marker_status']==marker
            else:assert row['source_stat_index'] is None and all(row[column] is None for column in ('next_free_raw','subject_reference_count',*COUNTER_COLUMNS))
        for read in trace:
            if read.get('operation')!='ReadProcessMemory':continue
            label=read['label'];address=int(read['address'],16);size=read['requested_bytes']
            if label.startswith(('CURRENT_COACH_PUBLIC_NAME','CURRENT_COACH_UID','CURRENT_COACH_POSITION0_REFERENCE')):
                index,off=divmod(address-staff_base,352);assert 0<=index<staff_count and (off,size) in ((48,80),(216,2),(136,2)) and not (off<216 and 138<off+size) and not (off<265 and 260<off+size) and read['success'];private_checks+=1
            if label.startswith('CURRENT_COACH_WIN_LOSS_PROJECTION'):
                index,off=divmod(address-stat_base,12);assert off==0 and size==10 and index in refs and read['sha256']==file_sha256(source/f'stat-{index}.bin');award_checks+=1
            assert 'PLAYER' not in label
        for artifact in conn.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
            relative=Path(artifact['payload_ref']);path=source/relative.name if relative.parts[0]==source.name else app/relative.name;assert path.stat().st_size==artifact['byte_count'] and file_sha256(path)==artifact['sha256'];artifact_checks+=1
        run_row=conn.execute('SELECT refresh_family,refresh_period_year FROM capture_runs WHERE run_id=?',(unit,)).fetchone();assert tuple(run_row)==(None,None)
        source_results.append({'unit_id':unit,'source_staff_count':len(rows),'resolved_subjects':resolved,'distinct_stat_projections':len(refs),'observed_at':entry['unit']['observed_at'],'process_epoch':batch['process_epoch'],'annual_bucket_consumed':False})
    assert conn.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0]==42
queries=dest/'queries';queries.mkdir(exist_ok=True);latest=current_coach_stats(db);assert latest['source']['unit_id']==source_results[-1]['unit_id'];assert len(latest['records'])==min(20,source_results[-1]['resolved_subjects']) and latest['has_more']==(source_results[-1]['resolved_subjects']>20);write(queries/'latest-resolved-first-page.json',latest);old=query_at(db,source_results[0]['observed_at'],'current_coach_stats');assert old['result']['source']['unit_id']==source_results[0]['unit_id'];write(queries/'first-observation-as-of.json',old)
queried=0;cursor=-1
while True:
    page=current_coach_stats(db,unit_id=source_results[-1]['unit_id'],resolved_only=False,after_index=cursor,limit=100);queried+=len(page['records'])
    if not page['has_more']:break
    cursor=page['next_after_index']
assert queried==source_results[-1]['source_staff_count'];assert all(not any('won_title' in key or 'won_coach_of_the_year' in key for key in row) for row in latest['records'])
assert file_sha256(db.with_name(before['database_file']))==before['database_sha256'] and file_sha256(db)==worker['after_database_sha256']
report={'status':'ACTUAL_ORDINARY_COACH_STATS_V24_FIELDS_EXCLUSIONS_HISTORY_AND_QUERIES_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'prior_rows_preserved':preserved,'prior_tables_preserved':len(before['row_counts']),'total_rows':sum(counts.values()),'successful_units':42,'sources':source_results,'identity_comparisons':identity_checks,'signed_reference_comparisons':reference_checks,'counter_and_marker_comparisons':stat_checks,'annual_reference_and_private_interval_checks':private_checks,'award_free_stat_interval_checks':award_checks,'source_artifact_hashes_verified':artifact_checks,'query_subjects_verified':queried,'annual_buckets_unchanged':True,'old_database_retained_unchanged':True,'database_sha256':worker['after_database_sha256'],'game_writes':False,'computer_use_used':False,'capacity_work_executed':False,'independent_acceptance':False,'full_goal_complete':False};write(dest/'actual-current-coach-report.json',report)
scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment34.py','run_current_coach_worker34.py','start_current_coach_worker34.ps1','verify_current_coach_terminal34.ps1','audit_current_coach34.py'):shutil.copyfile(r/name,scripts/name)
archive=dest/'native-current-coach-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ('reconnect-current-coach-34','current-coach-refresh-34-1','current-coach-refresh-34-2'):tar.add(r/name,arcname=name)
write(dest/'native-current-coach-evidence.archive.json',{'file':archive.name,'bytes':archive.stat().st_size,'sha256':file_sha256(archive),'restricted_owner_evidence':True,'game_save_included':False})
part=1;parts=[];stream_hash=hashlib.sha256();current=None;size=0;digest=None
class Parts:
    def write(self,data):
        global part,current,size,digest
        stream_hash.update(data);total=len(data);offset=0
        while offset<len(data):
            if current is None:current=(dest/f'world-v24.sqlite.gz.part{part:03d}').open('wb');size=0;digest=hashlib.sha256()
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
sink.close_part();write(dest/'world-v24.snapshot.json',{'database_file':db.name,'database_sha256':file_sha256(db),'stream_sha256':stream_hash.hexdigest(),'parts':parts,'schema_version':VERSION,'tables':len(TABLES),'rows':sum(counts.values())});(dest/'.gitattributes').write_text('*.gz.part* -text\n*.tar.gz -text\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','tables','columns','total_rows','signed_reference_comparisons','counter_and_marker_comparisons','annual_reference_and_private_interval_checks','award_free_stat_interval_checks')}))
