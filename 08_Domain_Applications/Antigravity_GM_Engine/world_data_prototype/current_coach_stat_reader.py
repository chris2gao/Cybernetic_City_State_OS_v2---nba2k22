"""Ordinary position0 coach win/loss observations; annual references/awards excluded."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from engine import connect,ingest_capture
from family_codec import decode_fixed_utf16
from game_mode_reader import collect_game_mode,game_mode_payload
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from staff_history_reader import PROFILE as HISTORY_PROFILE,verify_metadata,classify_reference
from staff_history_semantics import PROFILE as ROLE_PROFILE,verify_semantics_code

PROFILE_PATH=Path(__file__).with_name('current_coach_stat_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout'];COUNTER_COLUMNS=('coach_wins_raw','coach_losses_raw','coach_playoff_wins_raw','coach_playoff_losses_raw')


def decode_current_stat(raw):
    if len(raw)!=10:raise ValueError('ordinary coach stat projection must be exactly10 bytes; annual flags excluded')
    return {HISTORY_PROFILE['stat_fields'][name]['column']:int.from_bytes(raw[HISTORY_PROFILE['stat_fields'][name]['binding']['offset']:HISTORY_PROFILE['stat_fields'][name]['binding']['offset']+2],'little') for name in PROFILE['stat_fields']}


def collect_current_coach_stats(reader):
    if PROFILE['reference_position']!=0 or PROFILE['staff_projection_ranges']!=[[48,128],[136,138],[216,218]] or PROFILE['stat_projection_range']!=[0,10]:raise ValueError('ordinary coach projection contract changed')
    metadata=verify_metadata(reader);code=verify_semantics_code(reader);mode,blobs=collect_game_mode(reader);controls=[]
    def read(address,size,label):
        raw=reader.read(address,size,label);controls.append((address,raw,label));return raw
    ptr=read(reader.module_base+HISTORY_PROFILE['roster_pointer_rva'],8,'CURRENT_COACH_ROSTER_POINTER');root=int.from_bytes(ptr,'little');descs={};blobs['roster-root.bin']=ptr
    for slot,maximum,stride in ((19,8192,352),(21,65535,12)):
        raw=read(root+slot*16,16,'CURRENT_COACH_DESCRIPTOR:'+str(slot));count,address=struct.unpack('<QQ',raw)
        if count>maximum or (count and not 0x10000<=address<0x7fffffffffff):raise ValueError('current coach descriptor outside bounded envelope')
        descs[slot]={'count':count,'address':address,'stride':stride};blobs[f'descriptor-{slot}.bin']=raw
    staff=[];wanted=defaultdict(set)
    for index in range(descs[19]['count']):
        address=descs[19]['address']+352*index;name_raw=read(address+48,80,'CURRENT_COACH_PUBLIC_NAME');uid=read(address+216,2,'CURRENT_COACH_UID');ref=read(address+136,2,'CURRENT_COACH_POSITION0_REFERENCE');bad=False
        try:name=(decode_fixed_utf16(name_raw[:40])+' '+decode_fixed_utf16(name_raw[40:])).strip()
        except (UnicodeError,ValueError):name=None;bad=True
        value=struct.unpack('<h',ref)[0];staff.append({'source_staff_index':index,'native_staff_id_raw':int.from_bytes(uid,'little'),'observed_name':name,'name_status':'INVALID_UTF16_PREFIX' if bad else 'OBSERVED_UTF16' if name else 'EMPTY_NATIVE_NAME','native_stat_index_signed':value})
        if 0<=value<descs[21]['count']:wanted[value].add(index)
        blobs[f'staff-{index}.bin']=name_raw+uid+ref
    stats=[]
    for index,subjects in sorted(wanted.items()):
        raw=read(descs[21]['address']+12*index,10,'CURRENT_COACH_WIN_LOSS_PROJECTION');blobs[f'stat-{index}.bin']=raw;stats.append({'source_stat_index':index,'subject_reference_count':len(subjects),**decode_current_stat(raw)})
    for address,raw,label in controls:
        if reader.read(address,len(raw),label+':RECHECK')!=raw:raise ValueError('Native current coach source changed during acquisition')
    after,_=collect_game_mode(reader)
    if after['season_year']!=mode['season_year'] or after['observation']!=mode['observation']:raise ValueError('Native progress changed during current coach acquisition')
    return {'season_year':mode['season_year'],'staff_count':descs[19]['count'],'stat_bank_count':descs[21]['count'],'staff':staff,'stats':stats,'metadata':metadata,'storage_code_proof':code,'game_mode':mode,'limits':PROFILE['limits'],'game_writes':False,'annual_history_refreshed':False,'annual_other_reference_positions_read':0,'annual_award_value_bytes_read':0,'player_value_reads':0},blobs


def current_coach_payload(binding,m,artifacts,stamp,token,canonical):
    if sorted(s['source_staff_index'] for s in m['staff'])!=list(range(m['staff_count'])):raise ValueError('complete current coach source directory required')
    wanted=defaultdict(set)
    for row in m['staff']:
        status=classify_reference(row['native_stat_index_signed'],m['stat_bank_count'])
        if status.startswith('RESOLVED'):wanted[row['native_stat_index_signed']].add(row['source_staff_index'])
    stats={s['source_stat_index']:s for s in m['stats']};expected={'source_stat_index','subject_reference_count','next_free_raw',*COUNTER_COLUMNS}
    if len(stats)!=len(m['stats']) or set(stats)!=set(wanted):raise ValueError('complete distinct current coach stat projections required')
    for index,row in stats.items():
        if set(row)!=expected or row['subject_reference_count']!=len(wanted[index]):raise ValueError('current coach stat projection contains missing/annual fields or inconsistent sharing')
    unit='native-current-coach:'+token;sid='season:native-year:'+str(m['season_year']);uid=Counter(row['native_staff_id_raw'] for row in m['staff']);observations=[]
    for source in m['staff']:
        index=source['native_stat_index_signed'];stat=stats.get(index);key='staff:native:'+str(source['native_staff_id_raw']);accepted=uid[source['native_staff_id_raw']]==1 and source['name_status']=='OBSERVED_UTF16' and canonical.get(key)==source['observed_name'];marker='NOT_OBSERVED' if stat is None else 'MATCHES_NATIVE_ALLOCATION_MARKER' if stat['next_free_raw']==ROLE_PROFILE['next_free_allocation_marker'] else 'DIFFERS_FROM_NATIVE_ALLOCATION_MARKER; REACHABILITY_UNPROVED'
        row={**source,'staff_id':key if accepted else None,'canonical_link_status':'CURRENT_UNIQUE_UID_AND_EXACT_EXISTING_NAME; LIFECYCLE_UNPROVED' if accepted else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD','link_status':classify_reference(index,m['stat_bank_count']),'source_stat_index':None,'subject_reference_count':None,'next_free_raw':None,'native_allocation_marker_status':marker,'stat_year':None,**{c:None for c in COUNTER_COLUMNS}}
        if stat:row.update(stat)
        observations.append(row)
    facts={'native_current_coach_stat_observations':observations,'game_mode_observations':game_mode_payload(binding,m['game_mode'],[],stamp,token)['facts']['game_mode_observations'],'field_gaps':[{'affected_domain':'RES-C','target_field':'CURRENT_COACH_STAT_YEAR_PHASE_TEAM_AND_OWNERSHIP','reason':'Native position0 update role and signed bank resolution do not prove calendar year, phase, team scope, free-list reachability or historical ownership','impact':'Keep stat_year NULL and raw current win/loss fields source-qualified; no finalization or annual award event inferred'}]}
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_CURRENT_COACH_STATS','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':sid,'season_code':'NATIVE_YEAR:'+str(m['season_year'])},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_current_coach_stats(pid,save_directory,loaded_filename,new_output_directory):
    binding,bhash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_current_coach_stats(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'current-coach-manifest.json',m);_json(out/'current-coach-report.json',{'status':'CURRENT_NATIVE_COACH_WIN_LOSS_POSITION0_CAPTURED','observed_at':stamp,'pid':reader.pid,'binding_sha256':bhash,'read_trace':reader.trace,'game_writes':False,'annual_history_refreshed':False,'annual_award_value_bytes_read':0,'player_value_reads':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_CURRENT_COACH_WIN_LOSS_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('staff_history_native_profile.json'),Path(__file__).with_name('staff_history_semantics_native_profile.json')):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_CURRENT_COACH_LAYOUT_AND_CODE','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'current-coach-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as conn:
            canonical={r['staff_id']:r['display_name'] for r in conn.execute('SELECT staff_id,display_name FROM staff_members')};payload=current_coach_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(conn,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'annual_history_refreshed':False,'game_writes':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
