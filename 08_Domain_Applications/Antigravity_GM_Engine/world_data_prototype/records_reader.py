"""Read the complete bounded native record book, without PLAYER acquisition.

Historical record names/IDs are source subjects, not current PLAYER identities.
Category labels and packed dates are research interpretations, not UI acceptance.
"""
from collections import Counter
from datetime import date,datetime,timezone
import hashlib,importlib.util,json,math,struct
from pathlib import Path
from schema_model import DOMAIN
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json,read_binding,bound_database,_AcquisitionReceipt
from schedule_reader import bounded_block
from engine import connect,ingest_capture

RECORD_STRIDE=52
RECORD_GETTER_RVA=0xF400A0
# cmp ebx,[rax+270]; jnb +14; imul rbx,rbx,34; add rbx,[rax+278]
GETTER_CORE=bytes.fromhex('3b98700200007314486bdb3448039878020000')
DECODER_PATH=DOMAIN/'research/native_access/AG_NATIVE_01C/decoders/record_book_decoder.py'
_spec=importlib.util.spec_from_file_location('world_record_category_research',DECODER_PATH)
_research=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_research)
CATEGORY_CANDIDATES=_research.CATEGORY_NAMES


def decode_record_word(raw,index):
    if len(raw)!=RECORD_STRIDE:raise ValueError('record-book row must be 52 bytes')
    def name(part):
        prefix=part.split(b'\0',1)[0]
        if any(b<32 or b==127 for b in prefix):return None,'INVALID_NAME_CONTROL_BYTES'
        return prefix.decode('latin1').strip(),('ASCII_PREFIX' if all(b<128 for b in prefix) else 'LATIN1_PREFIX_CANDIDATE')
    first,fs=name(raw[:20]);last,ls=name(raw[20:40]);word=int.from_bytes(raw[40:44],'little');value=struct.unpack_from('<f',raw,40)[0]
    packed,category,native_id,flags=struct.unpack_from('<4H',raw,44)
    candidate=None;date_status='ZERO_DATE_NO_CANDIDATE'
    if packed:
        try:candidate=date(1920+(packed>>9),(packed>>5)&15,packed&31).isoformat();date_status='VALID_GREGORIAN_1920_EPOCH_CANDIDATE_UI_UNVERIFIED'
        except ValueError:date_status='INVALID_GREGORIAN_PACKED_WORD_RETAINED'
    if not any(raw):status='EMPTY_ALL_ZERO'
    elif first is None or last is None:status='INVALID_SOURCE_NAME_PREFIX'
    elif not first and not last:status='UNNAMED_SOURCE_SLOT'
    elif not math.isfinite(value):status='NONFINITE_SOURCE_METRIC'
    else:status='NAMED_FINITE_RECORD_SOURCE'
    return {'source_row_index':index,'first_name':first or None,'last_name':last or None,
        'name_encoding_status':fs+';'+ls,'raw_value_u32':word,'value_real':value if math.isfinite(value) else None,
        'value_text':float(value).hex() if math.isfinite(value) else f'NONFINITE_NATIVE_FLOAT_WORD:{word:08x}',
        'packed_date_raw':packed,'date_candidate':candidate,'date_status':date_status,
        'native_category_code':category,'category_label_candidate':CATEGORY_CANDIDATES.get(category),
        'native_player_id_raw':native_id,'flags_raw':flags,'decode_status':status}


def collect_records(reader):
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'RECORDS_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    getter=reader.read(reader.module_base+RECORD_GETTER_RVA,64,'RECORDS_NATIVE_GETTER')
    if GETTER_CORE not in getter:raise ValueError('record-book native getter layout changed')
    descriptors={};tables={};controls=[];blobs={'record-getter.bin':getter}
    for slot,maximum,stride in ((39,80000,52),(8,1024,4696),(28,10000,62)):
        raw=reader.read(root+slot*16,16,f'RECORDS_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum or not 0x10000<=address<0x00007FFFFFFFFFFF:raise ValueError('record source descriptor outside explicit bound')
        descriptors[slot]=raw;tables[slot]={'count':count,'address':address,'stride':stride}
    season_control=None
    for i in range(tables[8]['count']):
        address=tables[8]['address']+i*4696;ident=reader.read(address+0xCA8,2,'RECORDS_TEAM_CONTROL_ID')
        if int.from_bytes(ident,'little')!=0:continue
        idxraw=reader.read(address+0xE80,2,'RECORDS_TEAM_STATS_INDEX');idx=int.from_bytes(idxraw,'little')
        if idx>=tables[28]['count']:raise ValueError('record observation season index outside stats descriptor')
        target=tables[28]['address']+idx*62;season_control=reader.read(target,62,'RECORDS_SEASON_CONTROL')
        controls.extend(((address+0xCA8,ident,'RECORDS_TEAM_ID_RECHECK'),(address+0xE80,idxraw,'RECORDS_STATS_INDEX_RECHECK'),(target,season_control,'RECORDS_SEASON_RECHECK')));break
    if season_control is None:raise ValueError('record observation season context absent')
    blobs['season-control.bin']=season_control;table=tables[39];parts=[]
    # Complete native count, record-aligned blocks; each RPM call <=1200 bytes.
    for start in range(0,table['count'],1000):
        size=min(1000,table['count']-start)*52
        parts.append(bounded_block(reader,table['address']+start*52,size,f'RECORDS_TABLE:{start}'))
    raw=b''.join(parts);blobs['record-book.bin']=raw
    rows=[decode_record_word(raw[i*52:(i+1)*52],i) for i in range(table['count'])]
    for start in range(0,table['count'],1000):
        offset=start*52;size=min(1000,table['count']-start)*52
        if bounded_block(reader,table['address']+offset,size,f'RECORDS_TABLE_RECHECK:{start}')!=raw[offset:offset+size]:raise ValueError('record book changed during acquisition')
    controls.append((reader.module_base+RECORD_GETTER_RVA,getter,'RECORDS_GETTER_RECHECK'))
    for address,data,label in controls:
        if reader.read(address,len(data),label)!=data:raise ValueError('record source context changed')
    if reader.read(reader.module_base+ROSTER_RVA,8,'RECORDS_ROOT_RECHECK')!=pointer:raise ValueError('record root changed')
    for slot,data in descriptors.items():
        if reader.read(root+slot*16,16,f'RECORDS_SLOT{slot}_RECHECK')!=data:raise ValueError('record directory changed')
    return {'season_year':1900+(season_control[4]&127),'descriptors':tables,'record_rows':rows,'capture_coverage':'COMPLETE_NATIVE_COUNT',
        'decode_status_counts':dict(Counter(r['decode_status'] for r in rows)),
        'getter_status':'CURRENT_NATIVE_COUNT_POINTER_AND_52_BYTE_STRIDE_VERIFIED',
        'category_labels_status':'RESEARCH_CANDIDATES_NOT_CURRENT_UI_CERTIFIED',
        'canonical_player_binding':'NOT_INFERRED_FROM_NAME_OR_NATIVE_ID','game_writes':False,'player_struct_reads':0},blobs


def probe_records(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_records(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'records-manifest.json',manifest)
        report.update({'status':'RECORDS_SOURCE_CAPTURED','read_trace':reader.trace,
            'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'RECORDS_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'records-report.json',report);return report


def records_payload(binding,manifest,artifacts,observed_at,token):
    rows=manifest['record_rows'];unit='records:'+token;year=manifest['season_year'];count=manifest['descriptors']['39']['count'] if '39' in manifest['descriptors'] else manifest['descriptors'][39]['count']
    if manifest.get('game_writes') is not False or manifest.get('player_struct_reads')!=0:raise ValueError('record capture must be observation only, without PLAYER structs')
    coverage=manifest.get('capture_coverage');indices=[r['source_row_index'] for r in rows]
    if len(indices)!=len(set(indices)) or any(type(i) is not int or not 0<=i<count for i in indices):raise ValueError('invalid/duplicate record source index')
    if coverage=='COMPLETE_NATIVE_COUNT':
        if set(indices)!=set(range(count)):raise ValueError('incomplete native record count')
    elif coverage!='CURATED_RESEARCH_SUBSET':raise ValueError('record source coverage must be explicit')
    facts={'season_record_entries':[],'field_gaps':[]}
    for row in rows:
        # Reconstruct and decode the exact value word, rejecting payload edits
        # that silently round values or substitute a different decoded metric.
        native=struct.unpack('<f',row['raw_value_u32'].to_bytes(4,'little'))[0]
        if row['value_real']!=(native if math.isfinite(native) else None):raise ValueError('record value/raw word mismatch')
        if row['value_text']!=(float(native).hex() if math.isfinite(native) else f'NONFINITE_NATIVE_FLOAT_WORD:{row["raw_value_u32"]:08x}'):raise ValueError('record exact value text mismatch')
        facts['season_record_entries'].append({'season_id':None,'observed_in_season_id':f'season:native-year:{year}',
            'record_key':f'ROSTER_SLOT39:INDEX:{row["source_row_index"]}',
            'holder_player_id':None,'holder_team_id':None,'occurred_at':None,
            'value_raw':row['value_text'],'source_ref':'ROSTERDATA_SLOT39_RECORD52_CURRENT_GETTER',
            'source_row_index':row['source_row_index'],'source_first_name':row['first_name'],'source_last_name':row['last_name'],
            'native_value_word_u32':row['raw_value_u32'],'native_value_real':row['value_real'],'packed_date_raw':row['packed_date_raw'],
            'native_category_code':row['native_category_code'],'category_label_candidate':row['category_label_candidate'],
            'native_player_id_raw':row['native_player_id_raw'],'flags_raw':row['flags_raw'],'decode_status':row['decode_status'],
            'name_encoding_status':row['name_encoding_status'],'record_date_candidate':row['date_candidate'],
            'date_interpretation_status':row['date_status'],'source_scope_status':'NATIVE_CATEGORY_AND_FLAGS_OBSERVED; RECORD_SEASON_AND_UI_SCOPE_UNVERIFIED'})
    facts['field_gaps']=[dict(affected_domain='RES-H',target_field=t,reason=r,impact=i) for t,r,i in (
        ('RECORD_SUBJECT_LIFECYCLE_IDENTITY','Inline record names and native IDs are not proven current save-local PLAYER identities','Keep observed names/raw ID; canonical holder FK remains NULL'),
        ('RECORD_CATEGORY_FLAGS_AND_SCOPE','Most native category codes and trailing flags have no current accepted UI mapping','No team, scope, rank or season inference'),
        ('RECORD_DATE_ENCODING_APPLICABILITY','1920-epoch date formula is a research candidate and invalid for many observed words','Keep packed word and qualified candidate; occurred_at remains NULL'),
        ('ACTUAL_SEASON_AWARDS','Record-book observations do not establish award winners or final season honors','Award/recipient tables remain unobserved by this source'),
        ('NATIVE_NEWS_SOURCE','No actual news object/source is provided by the record book','Do not manufacture news from records or leading statistics'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_RECORD_BOOK',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'NATIVE_RECORD52_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},
        'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_records(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_records(reader);reader.close()
        if manifest['capture_coverage']!='COMPLETE_NATIVE_COUNT':raise ValueError('live adapter requires complete bounded native count')
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'records-manifest.json',manifest)
        report={'status':'RECORDS_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,
            'game_writes':False,'player_struct_reads':0,'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'records-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'BOUNDED_NATIVE_RECORD_BOOK_OR_CONTROL','source_version':'NATIVE_RECORD52_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (Path(__file__),DECODER_PATH):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'EXECUTED_READER_OR_RESEARCH_CATEGORY_SOURCE','source_version':'NATIVE_RECORD52_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'records-report.json').read_bytes()).hexdigest()[:24]
        payload=records_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as c:status=ingest_capture(c,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'counts':{name:len(values) for name,values in payload['facts'].items()},'game_writes':False,'player_struct_reads':0,
            'decode_status_counts':manifest['decode_status_counts'],'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'RECORDS_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_records(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status']=='RECORDS_SOURCE_CAPTURED' else 2)
