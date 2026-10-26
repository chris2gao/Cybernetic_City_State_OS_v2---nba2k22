"""Actual staff scalars, identity/role edges, private-free projections and history."""
from collections import Counter,defaultdict
from contextlib import closing
import gzip,hashlib,json,shutil,struct,sys,tarfile
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;run=runtime.parent;dest=run/'06_执行/increment30';app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident,VERSION
from database_operations import file_sha256
from live_world import read_binding,bound_database
from query import native_staff,staff_team_slots,native_team_finance,native_honors,team_lineups
from observation_scope import query_at
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def text_prefix(raw):
    end=next((i for i in range(0,len(raw),2) if raw[i:i+2]==b'\0\0'),len(raw));return bytes(raw[:end]).decode('utf-16le').strip() or None
worker=json.loads((dest/'worker-result.json').read_bytes());assert worker['status']=='STAFF_UPGRADE_AND_CAPTURE_SUCCEEDED';terminal=json.loads((dest/'worker-terminal.json').read_bytes());assert terminal['worker_process_absent']
batch=json.loads((runtime/'staff-refresh-30/refresh-report.json').read_bytes());assert batch['status']=='COMPLETED_REQUESTED_SOURCES' and batch['requested_families']==['staff'];entry=batch['sources'][0];unit=entry['unit']['unit_id'];source=runtime/'staff-refresh-30'/entry['directory'];assert entry['commit_status']=='COMMITTED_SUCCESS_VERIFIED' and entry['unit']['source_grade']=='LIVE_READ'
m=json.loads((source/'staff-manifest.json').read_bytes());report=json.loads((source/'staff-report.json').read_bytes());profile=json.loads((app/'staff_native_profile.json').read_bytes());contexts=[json.loads(p.read_bytes())['epoch'] for p in (runtime/'staff-refresh-30').glob('*-context.json')];assert len(contexts)==2 and contexts[0]==contexts[1] and contexts[0]['pid']==worker['pid']
before=json.loads((dest/'before.json').read_bytes());save=runtime/'world-saves/nba2k22_test_01';binding,_=read_binding(save,'MyLEAGUE0003');db=bound_database(save,binding);old=save/'world-v21.sqlite';assert file_sha256(old)==worker['old_database_sha256']==before['database_sha256']=='f0f000957404b9a9c536a1a73be7045d1536e253c689d7dcde12158dd776f0b2' and file_sha256(db)==worker['after_database_sha256'];assert binding['database_file']=='world-v22.sqlite' and {k:v for k,v in binding.items() if k!='database_file'}=={k:v for k,v in before['binding'].items() if k!='database_file'}
preserved={};deltas={};artifacts=0
with closing(connect(db,True)) as c:
    c.execute('ATTACH DATABASE ? AS baseline',(old.as_uri()+'?mode=ro',));assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[] and c.execute('PRAGMA user_version').fetchone()[0]==22
    for name in TABLES:
        columns=[r['name'] for r in c.execute('PRAGMA baseline.table_info('+ident(name)+')')];key=TABLES[name].key
        if columns:
            clauses=['a.'+ident(column)+' IS NOT b.'+ident(column) for column in columns if not (name=='saves' and column=='schema_version')]
            assert c.execute('SELECT count(*) FROM baseline.'+ident(name)+' a LEFT JOIN main.'+ident(name)+' b ON a.'+ident(key)+'=b.'+ident(key)+' WHERE b.'+ident(key)+' IS NULL OR '+' OR '.join(clauses)).fetchone()[0]==0,name
            preserved[name]=c.execute('SELECT count(*) FROM baseline.'+ident(name)).fetchone()[0]
        deltas[name]=c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]-preserved.get(name,0)
    assert len(preserved)==92 and sum(preserved.values())==1397842
    annual=lambda prefix:sorted(tuple(r) for r in c.execute('SELECT unit_id,refresh_family,refresh_period_year FROM '+prefix+'capture_units JOIN '+prefix+'capture_runs USING(run_id) WHERE refresh_family IS NOT NULL'))
    assert annual('baseline.')==annual('')
    for table,count in entry['counts'].items():
        if table not in ('teams','field_gaps'):assert c.execute('SELECT count(*) FROM '+ident(table)+' WHERE unit_id=?',(unit,)).fetchone()[0]==count,table
    for artifact in c.execute('SELECT * FROM source_artifacts WHERE unit_id=?',(unit,)):
        path=source/Path(artifact['payload_ref']).name if artifact['payload_ref'].startswith(source.name+'/') else app/Path(artifact['payload_ref']).name
        assert file_sha256(path)==artifact['sha256'] and path.stat().st_size==artifact['byte_count'];artifacts+=1
    prior=c.execute('SELECT max(observed_at) FROM baseline.capture_units').fetchone()[0];successful_units=c.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0];assert successful_units==38
    canonical={r['staff_id']:r['display_name'] for r in c.execute('SELECT staff_id,display_name FROM staff_members')}
sd=m['directories']['19'];td=m['directories']['8'];ranges=m['projection_ranges'];stride=m['projection_bytes'];projection=(source/'staff-public-projections.bin').read_bytes();assert len(projection)==sd['count']*stride;raws={}
for index in range(sd['count']):
    raw=bytearray(352);at=0
    for a,b in ranges:raw[a:b]=projection[index*stride+at:index*stride+at+b-a];at+=b-a
    raws[index]=raw
uid_counts=Counter(struct.unpack_from('<H',r,216)[0] for r in raws.values());team_ids={int(i):tid for i,tid in m['team_pool_native_ids'].items()};core_indexes={t['pool_index']:t['native_team_id'] for t in m['teams']};refs=defaultdict(list);slot_checks=0;slot_states=Counter();queries=dest/'queries';queries.mkdir(exist_ok=True)
for team in m['teams']:
    tid=team['native_team_id'];rows=staff_team_slots(db,'team:native:'+str(tid),unit_id=unit);assert rows['source']['unit_id']==unit and len(rows['records'])==8;role_bytes=(source/f'team-{tid}.staff-roles.bin').read_bytes()
    for slot in rows['records']:
        pointer=struct.unpack_from('<Q',role_bytes,slot['role_slot_index']*8)[0];index,rem=divmod(pointer-sd['address'],352);valid=pointer!=0 and 0<=index<sd['count'] and rem==0
        expected=f'{unit}:staff:{index}' if valid else None;assert slot['source_staff_id']==expected
        state='NULL_POINTER' if pointer==0 else 'OUTSIDE_CURRENT_POOL' if not 0<=index<sd['count'] else 'MISALIGNED_POOL_POINTER' if rem else 'CURRENT_POOL_REFERENT';assert slot['pointer_status']==state;slot_states[state]+=1
        if valid:refs[index].append((tid,slot['role_slot_index']))
        slot_checks+=1
    if tid in (0,8,31):write(queries/f'team-{tid}-staff-slots.json',rows)
assert slot_checks==240
def team_ref(pointer):
    if pointer==0:return None,None,'NULL_POINTER'
    index,rem=divmod(pointer-td['address'],4696)
    if not 0<=index<td['count']:return None,None,'OUTSIDE_CURRENT_POOL'
    if rem:return None,None,'MISALIGNED_POOL_POINTER'
    core=core_indexes.get(index);return team_ids[index],core,'CURRENT_CORE_TEAM_POINTER' if core is not None else 'CURRENT_NONCORE_TEAM_POOL_POINTER'
seen=set();after=-1;pages=0;identity_checks=0;scalar_checks=0;assignment_counts=Counter();status_counts=Counter();person_counts=Counter();aliases=0;names=0;examples=[]
while True:
    page=native_staff(db,current_core_only=False,include_details=True,unit_id=unit,after_index=after,limit=100);pages+=1;assert page['source']['unit_id']==page['game_mode']['unit_id']==unit and page['source']['source_grade']=='LIVE_READ' and page['source_staff_count']==sd['count']
    for row in page['records']:
        index=row['source_staff_index'];assert index not in seen;seen.add(index);raw=raws[index];uid=struct.unpack_from('<H',raw,216)[0];person=struct.unpack_from('<I',raw,268)[0]>>18&15;status=struct.unpack_from('<I',raw,272)[0]>>14&3;assert row['native_staff_id_raw']==uid and row['person_type_raw']==person and row['status_raw']==status;identity_checks+=3
        first=last=None;bad=False
        try:first=text_prefix(raw[48:88])
        except UnicodeDecodeError:bad=True
        try:last=text_prefix(raw[88:128])
        except UnicodeDecodeError:bad=True
        name=' '.join(n for n in (first,last) if n) or None;name_status='INVALID_UTF16_PREFIX' if bad else 'OBSERVED_UTF16' if name else 'EMPTY_NATIVE_NAME';assert row['first_name']==first and row['last_name']==last and row['observed_name']==name and row['name_status']==name_status;identity_checks+=4;names+=name is not None
        assert row['person_type_label']==profile['enum_labels']['COACHDATA_PERSONTYPE'].get(str(person),{}).get('label') and row['status_label']==profile['enum_labels']['COACHDATA_STATUS'].get(str(status),{}).get('label');identity_checks+=2
        current_core=None
        for prefix,offset in (('current_team',24),('previous_team',32),('myteam_team',40)):
            native,core,state=team_ref(struct.unpack_from('<Q',raw,offset)[0]);assert row[prefix+'_native_id_raw']==native and row[prefix+'_pointer_status']==state;identity_checks+=2
            if prefix=='current_team':current_core=core;assert row['current_core_team_id']==('team:native:'+str(core) if core is not None else None)
        assignment='NO_CORE_ROLE_REFERENCE' if not refs[index] else 'MULTIPLE_CORE_ROLE_REFERENCES_CANONICAL_WITHHELD' if len(refs[index])>1 else 'RECIPROCAL_CURRENT_TEAM_ROLE' if refs[index][0]==(current_core,person) else 'CORE_ROLE_REFERENCE_WITH_TEAM_OR_TYPE_MISMATCH';assert row['assignment_status']==assignment and row['core_slot_reference_count']==len(refs[index]);assignment_counts[assignment]+=1;status_counts[row['status_label'] or 'UNKNOWN']+=1;person_counts[row['person_type_label'] or 'UNKNOWN']+=1
        accepted=assignment=='RECIPROCAL_CURRENT_TEAM_ROLE' and uid_counts[uid]==1 and name_status=='OBSERVED_UTF16' and canonical.get('staff:native:'+str(uid))==name;assert row['staff_id']==('staff:native:'+str(uid) if accepted else None);aliases+=accepted
        for spec in profile['fields'].values():
            f=spec['binding'];size=(f['start_bit']+f['width']+7)//8;value=int.from_bytes(raw[f['offset']:f['offset']+size],'little')>>f['start_bit']&((1<<f['width'])-1);column=spec['column'];child=row[spec['group']];assert child['unit_id']==unit and child['source_staff_id']==row['staff_source_id']
            if spec['primitive']=='int':signed=value-(1<<f['width']) if value&(1<<(f['width']-1)) else value;assert child[column+'_bits_raw']==value and child[column+'_signed']==signed;scalar_checks+=2
            else:assert child[column+'_raw']==value;scalar_checks+=1
            if spec['enum']:assert child[column+'_label']==profile['enum_labels'][spec['enum']].get(str(value),{}).get('label');scalar_checks+=1
        assert not any('potential' in k.lower() for group in ('profile','tactics') for k in row[group])
        if len(examples)<4 and name and (accepted or not refs[index]):examples.append(row)
    if not page['has_more']:break
    after=page['next_after_index']
assert seen==set(raws) and scalar_checks==len(raws)*174
core_seen=set();after=-1
while True:
    page=native_staff(db,unit_id=unit,after_index=after,limit=100);core_seen.update(r['source_staff_index'] for r in page['records'])
    if not page['has_more']:break
    after=page['next_after_index']
assert len(core_seen)==assignment_counts['RECIPROCAL_CURRENT_TEAM_ROLE']
private_checks=0
for item in report['read_trace']:
    assert item['success'] is True
    if item['operation']=='OpenProcess':assert item['requested_access']=='0x1010 VM_READ|QUERY_LIMITED_INFORMATION'
    if item['operation']!='ReadProcessMemory':continue
    address=int(item['address'],16);size=item['requested_bytes'];assert 1<=size<=1248 and item['returned_bytes']==size
    if address+size>sd['address'] and address<sd['address']+sd['count']*352:
        index,relative=divmod(address-sd['address'],352);assert 0<=index<sd['count'] and any(a<=relative and relative+size<=b for a,b in ranges) and all(relative>=hi or relative+size<=lo for lo,hi in profile['excluded_staff_byte_ranges']) and (relative>=216 or relative+size<=136);private_checks+=1
assert private_checks==len(raws)*len(ranges)*2 and m['player_value_reads']==m['staff_annual_stat_references_read']==0
assert query_at(db,prior,'native_staff')['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'native_staff',unit_id=unit)['result']['status']=='NOT_OBSERVED' and query_at(db,prior,'staff_team_slots','team:native:0')['result']['status']=='NOT_OBSERVED'
assert native_team_finance(db)['source']['unit_id']=='native-finance:4e05cdc88e5ea0e9c3df9ed4' and native_honors(db,limit=1)['unit']['unit_id']=='native-honors:100325e0dd8283cf68d85b19' and team_lineups(db,'team:native:0')['source']['unit_id']=='native-lineups:5a40fe8ac5ba9af13d8dc077'
write(queries/'source-first-page.json',native_staff(db,current_core_only=False,unit_id=unit,limit=5));write(queries/'selected-public-staff-details.json',{'source_unit':unit,'records':examples});write(queries/'before-staff-as-of.json',query_at(db,prior,'native_staff'))
def parts(path,prefix):
    rows=[]
    with path.open('rb') as src:
        while block:=src.read(32*1024*1024):
            target=dest/(prefix+'.part'+str(len(rows)+1).zfill(3));target.write_bytes(block);rows.append({'file':target.name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
    return {'format':'CONCATENATE_ORDERED_PARTS_TO_RECREATE_GZIP_STREAM','stream_sha256':file_sha256(path),'parts':rows}
native=runtime/'increment30-native-sources.tar.gz'
with tarfile.open(native,'w:gz',compresslevel=6) as tar:
    for name in ('staff-refresh-30','staff-metadata-30','staff-enums-30'):tar.add(runtime/name,arcname=name)
    tar.add(runtime/'staff-metadata-30-labeled.json',arcname='staff-metadata-30-labeled.json')
write(dest/'native-sources.archive.json',parts(native,'native-sources.tar.gz'));snapshot=runtime/'increment30-world-v22.sqlite.gz'
with db.open('rb') as src,gzip.open(snapshot,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst,4*1024*1024)
snap=parts(snapshot,'world-v22.sqlite.gz');snap.update(database_sha256=file_sha256(db),database_bytes=db.stat().st_size,save_id=binding['save_id'],schema_version=22);write(dest/'world-v22.snapshot.json',snap);assert file_sha256(db)==worker['after_database_sha256'] and file_sha256(old)==before['database_sha256']
audit={'status':'ACTUAL_PUBLIC_STAFF_SOURCE_TYPED_FIELDS_ROLES_AND_V22_HISTORY_VERIFIED_NOT_FINAL_ACCEPTANCE','candidate_code_head':worker['candidate_code_head'],'schema_version':VERSION,'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values()),'source_unit':unit,'prior_rows_preserved':sum(preserved.values()),'prior_tables_preserved':len(preserved),'header_change':'saves.schema_version21->22 in copy only','after_total_rows':sum(preserved.values())+sum(deltas.values()),'new_rows_by_table':deltas,'successful_units':successful_units,'before_database_sha256':before['database_sha256'],'after_database_sha256':worker['after_database_sha256'],'process_epoch':contexts[0],'core_teams':30,'full_staff_source_slots':len(raws),'named_source_slots':names,'reciprocal_core_staff_sources':len(core_seen),'qualified_canonical_aliases':aliases,'full_source_query_pages':pages,'raw_identity_pointer_checks':identity_checks,'typed_scalar_label_comparisons':scalar_checks,'team_slot_pointer_checks':slot_checks,'slot_pointer_states':dict(slot_states),'assignment_counts':dict(assignment_counts),'native_status_counts':dict(status_counts),'native_person_type_counts':dict(person_counts),'private_free_staff_interval_checks':private_checks,'public_staff_projection_bytes':stride,'excluded_staff_byte_ranges':profile['excluded_staff_byte_ranges'],'artifact_hashes_checked':artifacts,'annual_bucket_units_unchanged':True,'prior_finance_and_lineup_sources_unchanged':True,'save_identity_unchanged':True,'old_database_retained_unchanged':True,'game_writes':False,'getter_invocations':0,'player_value_reads':0,'annual_staff_stat_references_read':0,'computer_use_used':False,'capacity_work_executed':False,'full_goal_complete':False,'limits':['Staff descriptor slots/status/role pointers do not prove allocation, lifecycle or hiring eligibility.','UI wages/grade presentation, sentinel meaning and behavior remain unproved.','Existing generic Potential-key restriction remains; max/growth and shared TightLipped bytes are not acquired.','Annual40-reference staff history and referenced player/signature/portrait namespace bindings remain unacquired.']}
write(dest/'actual-staff-report.json',audit);scripts=dest/'executed_scripts';scripts.mkdir(exist_ok=True)
for name in ('prepare_increment30.py','read_staff_metadata30.py','start_staff_metadata30.ps1','label_staff_metadata30.py','inspect_staff_fields30.py','read_staff_enums30.py','start_staff_enums30.ps1','build_staff_profile30.py','update_staff_readme30.py','run_staff_worker30.py','start_staff_worker30.ps1','verify_staff_terminal30.ps1',Path(__file__).name):(scripts/name).write_bytes((runtime/name).read_bytes())
(dest/'.gitattributes').write_text('*.json -text whitespace=cr-at-eol\n*.part* -text\nqueries/* -text whitespace=cr-at-eol\nexecuted_scripts/* -text whitespace=cr-at-eol\nverification/* -text whitespace=cr-at-eol\n',encoding='utf-8',newline='\n')
print(json.dumps({k:audit[k] for k in ('status','prior_rows_preserved','after_total_rows','full_staff_source_slots','named_source_slots','reciprocal_core_staff_sources','qualified_canonical_aliases','typed_scalar_label_comparisons','team_slot_pointer_checks','private_free_staff_interval_checks')}))
