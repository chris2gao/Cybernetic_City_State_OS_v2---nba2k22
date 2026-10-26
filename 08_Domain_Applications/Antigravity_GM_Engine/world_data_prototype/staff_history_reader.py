"""Annual public staff-history source; independent signed references, no year guess."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from award_reader import read_native_fields
from cadence import prepare_annual_capture,attach_annual_period,observed_game_season_year
from engine import connect,ingest_acquired_capture as ingest_capture
from game_mode_reader import collect_game_mode,game_mode_payload
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from family_codec import decode_fixed_utf16

PROFILE_PATH=Path(__file__).with_name('staff_history_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout'];FAMILY='STAFF_SEASON_HISTORY'


def classify_reference(index,count):
    if type(index) is not int or not -32768<=index<=32767:raise ValueError('signed16 staff stat reference required')
    if index<0:return 'NEGATIVE_NATIVE_GETTER_REJECTED'
    if index>=count:return 'OUTSIDE_CURRENT_NATIVE_BANK'
    return 'RESOLVED_CURRENT_BANK_INDEX; HISTORICAL_YEAR_AND_OWNERSHIP_UNPROVED'


def decode_coach_stat(raw):
    if len(raw)!=12:raise ValueError('COACHSTATDATA must be12 bytes')
    return {s['column']:int.from_bytes(raw[s['binding']['offset']:s['binding']['offset']+s['binding']['size']],'little') for s in PROFILE['stat_fields'].values()}


def verify_metadata(reader):
    values=[read_native_fields(reader,e,352 if e['name']=='COACHDATA' else 12,read_enums=False) for e in PROFILE['types']]
    for value in values:
        specs=PROFILE['identity']|{'SeasonStats':PROFILE['season_stats']} if value['name']=='COACHDATA' else {n:s['binding'] for n,s in PROFILE['stat_fields'].items()}
        actual={f['name_crc']:f for f in value['fields']}
        for name,old in specs.items():
            f=actual[old['name_crc']]
            if f['words'][1:6]!=old['words'][1:6]:raise ValueError('Native staff history binding changed: '+name)
            if name in ('FirstName','LastName','SeasonStats'):
                ptr=f['words'][6]|f['words'][7]<<32;raw=reader.read(ptr,24,'STAFF_HISTORY_ARRAY_DIMENSION:'+name);extent,stride=struct.unpack_from('<I',raw)[0],struct.unpack_from('<Q',raw,8)[0]
                if extent!=(40 if name=='SeasonStats' else 20) or stride!=2 or reader.read(ptr,24,'STAFF_HISTORY_ARRAY_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('Native staff history array dimensions changed')
    for proof in PROFILE['code_windows']:
        raw=bytes.fromhex(proof['code_hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'STAFF_HISTORY_GETTER_CODE')!=raw:raise ValueError('Native coach stat signed-index/getter code changed')
    return values


def collect_staff_history(reader):
    metadata=verify_metadata(reader);mode,mode_blobs=collect_game_mode(reader);year=mode['season_year'];controls=[];blobs=dict(mode_blobs)
    def read(address,size,label):
        raw=reader.read(address,size,label);controls.append((address,raw,label));return raw
    ptr=read(reader.module_base+PROFILE['roster_pointer_rva'],8,'STAFF_HISTORY_ROSTER_POINTER');root=int.from_bytes(ptr,'little');descs={}
    for slot,maximum,stride in ((19,8192,352),(21,65535,12)):
        raw=read(root+slot*16,16,'STAFF_HISTORY_DESCRIPTOR:'+str(slot));count,address=struct.unpack('<QQ',raw)
        if count>maximum or (count and not 0x10000<=address<0x7fffffffffff):raise ValueError('staff history descriptor outside bounded envelope')
        descs[slot]={'count':count,'address':address,'stride':stride}
    staff=[];wanted=defaultdict(set)
    for i in range(descs[19]['count']):
        address=descs[19]['address']+i*352;names=read(address+48,80,'ANNUAL_STAFF_PUBLIC_NAME');refid=read(address+136,82,'ANNUAL_STAFF_REFERENCES_AND_UID');bad=False
        try:first=decode_fixed_utf16(names[:40]);last=decode_fixed_utf16(names[40:]);name=(first+' '+last).strip()
        except (UnicodeError,ValueError):name=None;bad=True
        refs=struct.unpack('<40h',refid[:80]);row={'source_staff_index':i,'native_staff_id_raw':int.from_bytes(refid[80:82],'little'),'observed_name':name,'name_status':'INVALID_UTF16_PREFIX' if bad else 'OBSERVED_UTF16' if name else 'EMPTY_NATIVE_NAME','references':list(refs)};staff.append(row)
        for index in refs:
            if 0<=index<descs[21]['count']:wanted[index].add(i)
        blobs[f'staff-{i}.bin']=names+refid
    stats=[]
    for index,subjects in sorted(wanted.items()):
        raw=read(descs[21]['address']+index*12,12,'ANNUAL_COACH_STAT_RECORD');blobs[f'stat-{index}.bin']=raw;stats.append({'source_stat_index':index,'subject_reference_count':len(subjects),'stat_year':None,**decode_coach_stat(raw)})
    for address,raw,label in controls:
        if reader.read(address,len(raw),label+':RECHECK')!=raw:raise ValueError('Native staff history source changed during acquisition')
    after,_=collect_game_mode(reader)
    if after['observation']!=mode['observation'] or after['season_year']!=year:raise ValueError('Native progress changed during staff history acquisition')
    return {'season_year':year,'staff':staff,'stats':stats,'staff_count':descs[19]['count'],'stat_bank_count':descs[21]['count'],'metadata':metadata,'game_mode':mode,'limits':PROFILE['limits'],'game_writes':False,'player_value_reads':0},blobs


def staff_history_payload(binding,m,artifacts,stamp,token,canonical):
    if sorted(s['source_staff_index'] for s in m['staff'])!=list(range(m['staff_count'])):raise ValueError('incomplete or duplicate annual staff source directory')
    needed=defaultdict(set)
    for s in m['staff']:
        if len(s['references'])!=40:raise ValueError('complete40-position annual staff reference array required')
        for index in s['references']:
            status=classify_reference(index,m['stat_bank_count'])
            if status.startswith('RESOLVED'):needed[index].add(s['source_staff_index'])
    if len(m['stats'])!=len(needed) or {r['source_stat_index'] for r in m['stats']}!=set(needed):raise ValueError('referenced annual coach stat records are incomplete or duplicated')
    expected={s['column'] for s in PROFILE['stat_fields'].values()}|{'source_stat_index','stat_year','subject_reference_count'}
    for r in m['stats']:
        if set(r)!=expected or r['stat_year'] is not None or r['subject_reference_count']!=len(needed[r['source_stat_index']]):raise ValueError('coach stat field family/year/shared-reference count inconsistent')
    unit='native-staff-history:'+token;sid='season:native-year:'+str(m['season_year']);subjects={};stats={r['source_stat_index']:f'{unit}:stat:{r["source_stat_index"]}' for r in m['stats']};uid=Counter(s['native_staff_id_raw'] for s in m['staff']);facts={'native_staff_history_subjects':[],'native_coach_stat_observations':[],'native_staff_stat_links':[],'field_gaps':[]}
    for row in m['staff']:
        index=row['source_staff_index'];subjects[index]=subject=f'{unit}:staff:{index}';key='staff:native:'+str(row['native_staff_id_raw']);accepted=uid[row['native_staff_id_raw']]==1 and row['name_status']=='OBSERVED_UTF16' and canonical.get(key)==row['observed_name']
        facts['native_staff_history_subjects'].append({k:v for k,v in row.items() if k!='references'}|{'history_subject_id':subject,'staff_id':key if accepted else None,'canonical_link_status':'UNIQUE_CURRENT_POOL_ID_AND_EXACT_EXISTING_NAME; LIFECYCLE_UNPROVED' if accepted else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
        if len(row['references'])!=40:raise ValueError('complete40-position annual staff reference array required')
        for position,index in enumerate(row['references']):facts['native_staff_stat_links'].append({'history_subject_id':subject,'array_position':position,'native_stat_index_signed':index,'coach_stat_id':stats.get(index),'link_status':classify_reference(index,m['stat_bank_count'])})
    for row in m['stats']:facts['native_coach_stat_observations'].append({'coach_stat_id':stats[row['source_stat_index']],**row})
    facts['game_mode_observations']=game_mode_payload(binding,m['game_mode'],[],stamp,token)['facts']['game_mode_observations']
    facts['field_gaps']=[{'affected_domain':'RES-H','target_field':name,'reason':reason,'impact':impact} for name,reason,impact in (
        ('COACH_STAT_CALENDAR_YEAR_AND_POSITION_SEMANTICS','Native12-byte row has no year member;40-position calendar/current-slot mapping not proved','stat_year remains NULL; no invented year, phase, team or season-finalization'),
        ('COACH_STAT_ALLOCATION_AND_HISTORICAL_SUBJECT_OWNERSHIP','Native bounds prove pointer resolution; free-list lifecycle and shared references do not prove unique historic ownership','Keep NextFree raw and distinct-subject reference count; no canonical award event is fabricated'))]
    payload={'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_ANNUAL_STAFF_STATS','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':sid,'season_code':'NATIVE_YEAR:'+str(m['season_year'])},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}
    return attach_annual_period(payload,FAMILY,m['season_year'])


def capture_staff_history(pid,save_directory,loaded_filename,new_output_directory):
    binding,bhash=read_binding(save_directory,loaded_filename);db=bound_database(save_directory,binding);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);year,previous=prepare_annual_capture(reader,db,FAMILY)
        if previous:
            previous.update(save_id=binding['save_id'],read_trace=reader.trace);_json(out/'ingest-result.json',previous);return previous
        m,blobs=collect_staff_history(reader)
        if m['season_year']!=year:raise ValueError('annual staff refresh year changed')
        reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'staff-history-manifest.json',m);_json(out/'staff-history-report.json',{'status':'NATIVE_ANNUAL_STAFF_REFERENCES_AND_COACH_STATS_CAPTURED','pid':reader.pid,'observed_at':stamp,'binding_sha256':bhash,'read_trace':reader.trace,'game_writes':False,'player_value_reads':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_ANNUAL_STAFF_HISTORY_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        artifacts.append({'sha256':hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),'byte_count':PROFILE_PATH.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_STAFF_HISTORY_LAYOUT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+PROFILE_PATH.name})
        token=hashlib.sha256((out/'staff-history-report.json').read_bytes()).hexdigest()[:24]
        with connect(db) as conn:
            canonical={r['staff_id']:r['display_name'] for r in conn.execute('SELECT staff_id,display_name FROM staff_members')};payload=staff_history_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(conn,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'game_writes':False,'refresh_family':FAMILY,'refresh_period_year':year};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
