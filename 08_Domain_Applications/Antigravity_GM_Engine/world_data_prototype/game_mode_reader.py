"""Named Native game-mode stages and current-stat slot selector; read only."""
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from award_reader import read_native_fields
from league_reader import read_native_enum
from calendar_codec import PROFILE as CALENDAR_PROFILE,native_unsigned,date_columns
from cadence import observed_game_season_year
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from engine import connect,ingest_capture

PROFILE_PATH=Path(__file__).with_name('game_mode_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout']
RAW_FIELDS={'num_teams_raw':'NumTeams','num_draft_teams_raw':'NumDraftTeams','current_year_byte_raw':'CurrentYear','draft_year_byte_raw':'DraftYear','mode_raw':'Mode','league_raw':'League','period_raw':'Period','previous_period_raw':'PreviousPeriod'}
LABELS={'mode_label':('mode_raw','GAMEMODE_MODE'),'league_label':('league_raw','GAMEMODE_LEAGUE'),'period_label':('period_raw','GAMEMODE_TIMEPERIOD'),'previous_period_label':('previous_period_raw','GAMEMODE_TIMEPERIOD')}

def decode_game_mode(raw):
    if len(raw)!=24:raise ValueError('Native public GAMEMODE prefix must be24 bytes')
    row={column:native_unsigned(raw,PROFILE['bindings'][name]) for column,name in RAW_FIELDS.items()}
    row.update({column:PROFILE['enum_labels'][kind].get(str(row[source]),{}).get('label') for column,(source,kind) in LABELS.items()})
    row.update(date_columns(raw[20:24],'today_'));special=row['period_raw'] in PROFILE['shared_special_stat_period_codes']
    row.update({'current_stat_array_position':24 if special else 0,'stat_selector_rule':'NATIVE_CURRENT_TIMEPERIOD_SELECTOR_V1; POSITION24_SHARED_BY_MULTIPLE_PERIODS',
                'stat_selector_status':'KNOWN_NATIVE_PERIOD' if row['period_label'] is not None else 'UNREGISTERED_PERIOD_NATIVE_DEFAULT_PRIMARY_SLOT; LABEL_WITHHELD'})
    return row

def verify_game_mode_metadata(reader):
    metadata=[];entries=PROFILE['types']+[e for e in CALENDAR_PROFILE['types'] if e['name'] in ('SCHEDULEDATE','SCHEDULEDATE_MONTH')]
    for entry in entries:
        if entry['constructor_rva']==31800976:
            value=read_native_enum(reader,entry);labels=(PROFILE if entry['name'] in PROFILE['enum_labels'] else CALENDAR_PROFILE)['enum_labels'][entry['name']]
            if {(v['value'],v['name_crc']) for v in value['values']}!={(int(code),v['name_crc']) for code,v in labels.items()}:raise ValueError('Native game-mode enum changed')
        else:
            value=read_native_fields(reader,entry,entry['expected_size'],read_enums=False);bindings=PROFILE['bindings'] if entry['name']=='GAMEMODE' else CALENDAR_PROFILE['bindings'][entry['name']]
            expected={f['name_crc']:f for f in bindings.values()}
            for field in value['fields']:
                old=expected[field['name_crc']]
                if field['words'][1]!=old['words'][1]:raise ValueError('Native game-mode primitive binding changed')
                if old['enum_pointer'] and field['enum_pointer']!=reader.module_base+old['enum_pointer']-0x140000000:raise ValueError('Native game-mode nested type changed')
        metadata.append(value)
    for proof in PROFILE['code_proofs']:
        raw=bytes.fromhex(proof['code_hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'GAME_MODE_CODE:'+proof['role'])!=raw:raise ValueError('Native game-mode selector/getter code changed')
    for proof in CALENDAR_PROFILE['code_proofs']:
        raw=bytes.fromhex(proof['hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'GAME_MODE_DATE_EPOCH_CODE')!=raw:raise ValueError('Native game-mode date epoch code changed')
    return metadata

def collect_game_mode(reader):
    metadata=verify_game_mode_metadata(reader);year=observed_game_season_year(reader);controls=[]
    def read(address,size,label):
        raw=reader.read(address,size,label);controls.append((address,raw,label));return raw
    direct=read(reader.module_base+PROFILE['game_mode_pointer_rva'],8,'GAME_MODE_DATA_POINTER');root=int.from_bytes(direct,'little')
    obj_raw=read(reader.module_base+PROFILE['virtual_object_pointer_rva'],8,'GAME_MODE_OBJECT_POINTER');obj=int.from_bytes(obj_raw,'little')
    if min(root,obj)<0x10000:raise ValueError('Native game-mode context absent')
    vtable=int.from_bytes(read(obj,8,'GAME_MODE_OBJECT_VTABLE'),'little')
    if not reader.module_base<=vtable<reader.module_base+reader.module_size-PROFILE['virtual_period_slot_offset']-8:raise ValueError('Native game-mode vtable outside module')
    target=int.from_bytes(read(vtable+PROFILE['virtual_period_slot_offset'],8,'GAME_MODE_VIRTUAL_PERIOD_POINTER'),'little')
    if target!=reader.module_base+PROFILE['verified_virtual_getter_rva']:raise ValueError('Native period virtual getter differs from verified source')
    prefix=read(root,24,'GAME_MODE_PUBLIC_PREFIX');row=decode_game_mode(prefix)
    for address,raw,label in controls:
        if reader.read(address,len(raw),label+':RECHECK')!=raw:raise ValueError('Native game-mode context changed during acquisition')
    if observed_game_season_year(reader)!=year:raise ValueError('Native game season changed during game-mode acquisition')
    return {'season_year':year,'observation':row,'metadata':metadata,'virtual_getter_rva':PROFILE['verified_virtual_getter_rva'],
            'public_prefix_bytes':24,'game_writes':False,'getter_invocations':0,'player_struct_reads':0,
            'cumulative_phase_inferred':False,'current_year_semantics':PROFILE['current_year_field_semantics']},{'game-mode-public-prefix.bin':prefix}

def game_mode_payload(binding,manifest,artifacts,observed_at,token):
    year=manifest['season_year'];season={'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'};unit='native-game-mode:'+token
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_GAME_MODE_PERIOD','observed_at':observed_at,
            'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
            'season':season,'facts':{'game_mode_observations':[{'season_id':season['season_id'],**manifest['observation']}]},'artifacts':artifacts,'completeness':'PARTIAL'}

def capture_game_mode(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_game_mode(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'game-mode-manifest.json',manifest);_json(out/'game-mode-report.json',{'status':'NATIVE_GAME_MODE_PERIOD_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'getter_invocations':0,'player_struct_reads':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_GAME_MODE_SOURCE_AND_CODE_METADATA','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('calendar_native_profile.json')):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_NATIVE_MODE_AND_DATE_LAYOUT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'game-mode-report.json').read_bytes()).hexdigest()[:24];payload=game_mode_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ';receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'counts':{'game_mode_observations':1},'source_grade':'LIVE_READ','period_raw':manifest['observation']['period_raw'],'period_label':manifest['observation']['period_label'],'current_stat_array_position':manifest['observation']['current_stat_array_position'],'game_writes':False,'getter_invocations':0,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'GAME_MODE_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
