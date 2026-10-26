"""Explicit, evidence-referenced bounded additions; never annual full readers.

This module does not discover every future fact automatically. A caller supplies
source selectors and a new-fact/omission evidence reference. Actual Native bytes,
layout/context checks and accepted-fact membership decide what can be appended.
"""
from collections import defaultdict
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from annual_ledger import baseline_row,sha
from cadence import ANNUAL_FAMILIES,validate_period
from engine import connect,ingest_acquired_capture
from game_mode_reader import collect_game_mode
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _AcquisitionReceipt,_json,read_binding,bound_database
from schema_model import VERSION

FORMAT='WORLD_ANNUAL_ADDITION_REQUEST_V1'


def load_request(path):
    path=Path(path)
    if path.suffix.lower()!='.json' or path.stat().st_size>1024*1024:raise ValueError('bounded JSON annual addition request required')
    request=json.loads(path.read_bytes())
    required={'format','save_id','family','period_year','baseline_unit_id','reason','evidence_ref','selectors'}
    if not isinstance(request,dict) or not required<=set(request) or set(request)-required-{'expected_game_year','expected_period_raw','fields'} or request['format']!=FORMAT:raise ValueError('invalid annual addition request shape')
    validate_period(request['family'],request['period_year'])
    if request['reason'] not in ('NEW_FACT','PROVEN_OMISSION'):raise ValueError('addition needs a new-fact/omission rationale')
    for name,bound in (('expected_game_year',9999),('expected_period_raw',4294967295)):
        if name in request and (type(request[name]) is not int or not 0<=request[name]<=bound):raise ValueError('invalid expected Native scene control')
    if any(not isinstance(request[n],str) or not 1<=len(request[n])<=8192 for n in ('save_id','baseline_unit_id','evidence_ref')):raise ValueError('addition needs explicit save/baseline/discovery evidence reference')
    if not isinstance(request['selectors'],dict):raise ValueError('typed source selectors required')
    selectors=request['selectors'];family=request['family']
    if 'fields' in request:
        from annual_ledger import allowed_native_fields
        fields=request['fields'];allowed=allowed_native_fields(family)
        if not isinstance(fields,list) or not 1<=len(fields)<=64 or any(not isinstance(n,str) or n not in allowed for n in fields) or len(set(fields))!=len(fields):raise ValueError('fields must be unique public Native stat columns for this annual family')
    expected={'history_indices','matrix_slots'} if family=='LEAGUE_HISTORY_AWARDS' else {'indices'}
    if set(selectors)!=expected:raise ValueError('selectors do not match annual source family')
    count=0
    for name,values in selectors.items():
        if not isinstance(values,list) or len(values)>128:raise ValueError('at most128 targeted records per addition')
        if name=='matrix_slots':
            if any(not isinstance(v,list) or len(v)!=2 or type(v[0]) is not int or type(v[1]) is not int or not 0<=v[0]<15 or not 0<=v[1]<5 for v in values):raise ValueError('matrix selectors must be [award0..14,recipient0..4]')
            keys=[tuple(v) for v in values]
        else:
            if any(type(v) is not int or not 0<=v<80000 for v in values):raise ValueError('bounded nonnegative Native indices required')
            keys=values
        if len(set(keys))!=len(keys):raise ValueError('duplicate source selectors')
        count+=len(values)
    if not 1<=count<=128:raise ValueError('request must select1..128 total Native records')
    return request,sha(request),count


class SelectedReads:
    def __init__(self,reader):self.reader=reader;self.controls=[];self.blobs={};self.cost=defaultdict(lambda:{'calls':0,'bytes':0})
    def read(self,address,size,label,kind='control'):
        raw=self.reader.read(address,size,label);self.controls.append((address,raw,label,kind));self.cost[kind]['calls']+=1;self.cost[kind]['bytes']+=size
        return raw
    def root(self,rva=ROSTER_RVA):
        value=int.from_bytes(self.read(self.reader.module_base+rva,8,'ANNUAL_ADD_ROOT'),'little')
        if not 0x10000<=value<0x7fffffffffff:raise ValueError('annual addition Native root invalid')
        return value
    def descriptor(self,root,slot,stride,maximum):
        count,address=struct.unpack('<QQ',self.read(root+slot*16,16,'ANNUAL_ADD_DESCRIPTOR:'+str(slot)))
        if not 0<=count<=maximum or (count and not 0x10000<=address<0x7fffffffffff):raise ValueError('annual addition Native directory outside bound')
        return {'count':count,'address':address,'stride':stride}
    def record(self,desc,index,label):
        if not 0<=index<desc['count']:raise ValueError('annual addition selected index outside current Native directory')
        raw=self.read(desc['address']+index*desc['stride'],desc['stride'],label,'targeted_history_record');self.blobs[label+'.bin']=raw;return raw
    def recheck(self):
        for address,raw,label,kind in self.controls:
            value=self.reader.read(address,len(raw),label+':RECHECK');self.cost[kind+'_recheck']['calls']+=1;self.cost[kind+'_recheck']['bytes']+=len(raw)
            if value!=raw:raise ValueError('Native annual addition source changed during bounded acquisition')


def collect_records_selected(session,request,year):
    from records_reader import RECORD_GETTER_RVA,GETTER_CORE,decode_record_word,records_payload
    root=session.root();getter=session.read(session.reader.module_base+RECORD_GETTER_RVA,64,'ANNUAL_ADD_RECORD_GETTER')
    if GETTER_CORE not in getter:raise ValueError('record-book Native getter changed')
    desc=session.descriptor(root,39,52,80000);indices=request['selectors']['indices']
    manifest={'season_year':year,'descriptors':{39:desc},'record_rows':[decode_record_word(session.record(desc,i,'record-'+str(i)),i) for i in indices],
        'capture_coverage':'EVIDENCED_NATIVE_INCREMENTAL_SUBSET','selected_source_indices':indices,'game_writes':False,'player_struct_reads':0}
    return manifest,records_payload


def collect_honors_selected(session,request,year):
    from award_reader import PROFILE_PATH,read_native_fields,decode_stat_record,honors_payload
    profile=json.loads(PROFILE_PATH.read_bytes());entry=next(e for e in profile['types'] if e['name']=='PLAYERSTATDATA');metadata=read_native_fields(session.reader,entry,48,read_enums=False)
    fields={f['name_crc']:f for f in metadata['fields']}
    for name,expected in profile['stat_fields'].items():
        actual=fields.get(zlib.crc32(name.encode()))
        if actual is None or any(actual[k]!=expected[k] for k in ('offset','size','width','start_bit','format')):raise ValueError('Native annual stat field layout changed')
    root=session.root();players=session.descriptor(root,1,1264,8192);stats=session.descriptor(root,24,48,65535);indices=request['selectors']['indices']
    rows=[{'source_stat_index':i,**decode_stat_record(session.record(stats,i,'honor-stat-'+str(i)),profile['stat_fields'])} for i in indices]
    manifest={'season_year':year,'descriptors':{1:players,24:stats},'metadata':[metadata],'players':[],'stat_records':rows,'stat_links':[],
        'season_stats_array_count':int.from_bytes(bytes.fromhex(profile['season_stats_array_dimension_control_hex'])[:4],'little'),
        'source_coverage':'EVIDENCED_NATIVE_INCREMENTAL_SUBSET','selected_stat_indices':indices,'game_writes':False,'restricted_player_bytes_read':0,'full_player_struct_reads':0,
        'identity_status':'TARGETED_STAT_SOURCE_ONLY; NO_CURRENT_OR_HISTORICAL_PLAYER_PROMOTION'}
    return manifest,honors_payload


def collect_staff_selected(session,request,year):
    from staff_history_reader import PROFILE,verify_metadata,decode_coach_stat,staff_history_payload
    from family_codec import decode_fixed_utf16
    metadata=verify_metadata(session.reader);root=session.root();staff=session.descriptor(root,19,352,8192);stats=session.descriptor(root,21,12,65535);indices=request['selectors']['indices'];wanted=set(indices);subjects=[];owners=defaultdict(set)
    for index in indices:
        if not 0<=index<stats['count']:raise ValueError('selected coach stat outside Native bank')
    # COACHSTATDATA has no owner/year. Re-read only the bounded reference/UID
    # directory to establish current shared-reference counts; no old stat values.
    for index in range(staff['count']):
        address=staff['address']+index*352;refs=session.read(address+136,82,'ANNUAL_ADD_STAFF_REFERENCE_DIRECTORY:'+str(index),'reference_directory');values=list(struct.unpack('<40h',refs[:80]));matched=wanted.intersection(values)
        for stat in matched:owners[stat].add(index)
        if not matched:continue
        names=session.read(address+48,80,'ANNUAL_ADD_STAFF_SUBJECT:'+str(index),'identity_context')
        try:name=(decode_fixed_utf16(names[:40])+' '+decode_fixed_utf16(names[40:])).strip();status='OBSERVED_UTF16' if name else 'EMPTY_NATIVE_NAME'
        except (UnicodeError,ValueError):name=None;status='INVALID_UTF16_PREFIX'
        subjects.append({'source_staff_index':index,'native_staff_id_raw':int.from_bytes(refs[80:82],'little'),'observed_name':name,'name_status':status,'references':values})
    if any(not owners[i] for i in indices):raise ValueError('selected coach stat has no current source reference; allocation/ownership unproved')
    rows=[{'source_stat_index':i,'subject_reference_count':len(owners[i]),'stat_year':None,**decode_coach_stat(session.record(stats,i,'coach-stat-'+str(i)))} for i in indices]
    manifest={'season_year':year,'staff':subjects,'stats':rows,'staff_count':staff['count'],'stat_bank_count':stats['count'],'metadata':metadata,'limits':PROFILE['limits'],
        'game_writes':False,'player_value_reads':0,'incremental_selection':True,'selected_stat_indices':indices}
    return manifest,staff_history_payload


def collect_league_selected(session,request,year):
    from league_reader import PROFILE_PATH,FRANCHISE_RVA,verify_league_metadata,decode_history_record
    from league_ingest import league_payload
    profile=json.loads(PROFILE_PATH.read_bytes());metadata=verify_league_metadata(session.reader,profile);root=session.root();franchise=session.root(FRANCHISE_RVA);history=session.descriptor(root,41,152,10000)
    indices=request['selectors']['history_indices'];slots=request['selectors']['matrix_slots'];binding=profile['bindings']['FRANCHISE']['SeasonAwardWinnerIndex']
    if binding['array_dimensions']!=[15,5]:raise ValueError('Native award matrix dimensions changed')
    rows=[decode_history_record(session.record(history,i,'league-history-'+str(i)),i,profile) for i in indices];matrix=[]
    for a,b in slots:
        raw=session.read(franchise+binding['offset']+(a*5+b)*2,2,'ANNUAL_ADD_MATRIX:'+str(a)+':'+str(b),'targeted_matrix_cell');session.blobs['matrix-'+str(a)+'-'+str(b)+'.bin']=raw
        matrix.append({'award_slot_index':a,'recipient_slot_index':b,'native_player_index_raw':int.from_bytes(raw,'little')})
    manifest={'capture_mode':'HISTORY_AWARDS','season_year':year,'metadata':metadata,'game_writes':False,'player_struct_reads':0,'history':rows,'history_descriptor':history,'award_winner_matrix':matrix,
        'manager_slot40_candidate':{'first_word':None,'free_chain':{'status':'NOT_SCANNED_TARGETED_ADDITION'}},'incremental_selection':True,
        'selected_history_indices':indices,'selected_matrix_slots':slots,'canonical_award_group_coverage':'NOT_ESTABLISHED_BY_TARGETED_ADDITION'}
    return manifest,league_payload


COLLECTORS={'RECORD_BOOK':collect_records_selected,'NATIVE_HONOR_STATS':collect_honors_selected,'LEAGUE_HISTORY_AWARDS':collect_league_selected,'STAFF_SEASON_HISTORY':collect_staff_selected}


def capture_annual_additions(pid,save_directory,loaded_filename,new_output_directory,request_file,*,family=None):
    request,request_hash,count=load_request(request_file)
    if family is not None and request['family']!=family:raise ValueError('annual addition request routed to wrong reader')
    family=request['family'];binding,binding_hash=read_binding(save_directory,loaded_filename);database=bound_database(save_directory,binding)
    if request['save_id']!=binding['save_id']:raise ValueError('annual addition request belongs to another save')
    with connect(database,True) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0]!=VERSION:raise ValueError('copy-upgrade to current schema before annual additions; preserve original v24')
        baseline=baseline_row(conn,family,request['period_year'])
        if baseline is None or baseline['unit_id']!=request['baseline_unit_id']:raise ValueError('annual addition requires this save/family/year baseline')
        prior=conn.execute('''SELECT u.unit_id,u.observed_at FROM capture_units u JOIN capture_runs r USING(run_id)
            WHERE u.unit_status='success' AND r.source_grade='LIVE_READ' AND r.refresh_kind='ADDITION' AND r.refresh_request_sha256=?
            AND r.refresh_family=? AND r.refresh_period_year=? AND r.refresh_baseline_unit_id=?''',(request_hash,family,request['period_year'],baseline['unit_id'])).fetchone()
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False)
    if prior:
        result={'status':'already_applied','unit_id':prior['unit_id'],'observed_at':prior['observed_at'],'refresh_kind':'ADDITION','refresh_family':family,'refresh_period_year':request['period_year'],
            'baseline_unit_id':baseline['unit_id'],'request_sha256':request_hash,'fresh_native_capture':False,'history_record_reads':0,'game_writes':False}
        _json(out/'ingest-result.json',result);return result
    reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        from process_session import resolve_pid
        reader=ReadOnlyGameProcess(resolve_pid(pid));mode,mode_blobs=collect_game_mode(reader);year=mode['season_year']
        if year<request['period_year'] or ('expected_game_year' in request and year!=request['expected_game_year']):raise ValueError('Native game year does not match addition scene')
        if 'expected_period_raw' in request and mode['observation']['period_raw']!=request['expected_period_raw']:raise ValueError('Native game period differs from addition scene')
        session=SelectedReads(reader);session.blobs.update(mode_blobs);manifest,factory=COLLECTORS[family](session,request,year)
        session.recheck();after,_=collect_game_mode(reader)
        if after['season_year']!=year or after['observation']!=mode['observation']:raise ValueError('Native scene changed during annual addition')
        if family=='STAFF_SEASON_HISTORY':manifest['game_mode']=mode
        rpm=[item for item in reader.trace if item.get('operation')=='ReadProcessMemory']
        scope={'format':'TARGETED_NATIVE_ANNUAL_ADDITION_V1','requested_records':count,'untargeted_history_full_record_reads':0,
            'read_cost':dict(session.cost),'read_cost_scope':'SelectedReads value/directory/control costs include rechecks; Native metadata and scene-check overhead is separately visible in the complete acquisition read_trace',
            'method':'EXPLICIT_EVIDENCE_REFERENCED_SELECTORS; NO_FULL_ANNUAL_READER','automatic_discovery':False,
            'rationale':request['reason'],'discovery_evidence_ref':request['evidence_ref'],'request_sha256':request_hash,
            'baseline_unit_id':baseline['unit_id'],'family':family,'refresh_period_year':request['period_year'],'observed_native_year':year,
            'field_selection':request.get('fields'),
            'process_read_trace_cost':{'calls':len(rpm),'requested_bytes':sum(item['requested_bytes'] for item in rpm),'returned_bytes':sum(item['returned_bytes'] for item in rpm),'basis':'COMPLETE_ACQUISITION_READPROCESSMEMORY_TRACE; controlled tests do not claim Windows reads'},
            'native_game_mode':mode['observation'],'interpretation':'Native raw facts retain existing source limitations; no canonical UI/award/lifecycle promotion'}
        _json(out/'addition-request.json',request);_json(out/'targeted-addition-evidence.json',scope);_json(out/'selected-source-manifest.json',manifest)
        for name,raw in session.blobs.items():(out/name).write_bytes(raw)
        _json(out/'acquisition-report.json',{'status':'TARGETED_NATIVE_CHECKS_PASSED','binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'scope':scope})
        artifacts=[{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'payload_kind':'TARGETED_NATIVE_VALUE' if path.suffix=='.bin' else 'ANNUAL_ADDITION_CONTROL','payload_ref':out.name+'/'+path.name,'source_version':'ANNUAL_TARGETED_ADDITION_V1','restricted':1} for path in sorted(out.iterdir()) if path.is_file()]
        token=hashlib.sha256((out/'acquisition-report.json').read_bytes()).hexdigest()[:24]
        if family=='STAFF_SEASON_HISTORY':payload=factory(binding,manifest,artifacts,stamp,token,{})
        elif family=='LEAGUE_HISTORY_AWARDS':payload=factory(binding,manifest,artifacts,stamp,token,{})
        else:payload=factory(binding,manifest,artifacts,stamp,token)
        payload.update(evidence_grade='LIVE_READ',refresh_family=family,refresh_period_year=request['period_year'],refresh_kind='ADDITION',
            refresh_baseline_unit_id=baseline['unit_id'],refresh_request_sha256=request_hash,
            refresh_evidence_sha256=hashlib.sha256((out/'targeted-addition-evidence.json').read_bytes()).hexdigest(),annual_addition_scope=scope)
        capability=_AcquisitionReceipt(payload,reader)
        with connect(database) as conn:status=ingest_acquired_capture(conn,payload,_live_receipt=capability)
        result={'status':status,'unit_id':payload['unit_id'] if status in ('ingested','already_applied') else None,'refresh_kind':'ADDITION',
            'refresh_family':family,'refresh_period_year':request['period_year'],'baseline_unit_id':baseline['unit_id'],'request_sha256':request_hash,
            'fresh_native_capture':True,'read_cost':dict(session.cost),'unit_scope':'Only new typed facts; known rows/flags are not recopied','game_writes':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'ANNUAL_ADDITION_NOT_ACCEPTED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else [],'game_writes':False});raise
    finally:
        if reader:reader.close()
