"""Bounded read-only TEAM finance, with Native primitive and enum verification."""
from datetime import datetime,timezone
import hashlib,json,math,struct
from pathlib import Path
from award_reader import read_native_fields
from league_reader import read_native_enum
from game_mode_reader import collect_game_mode
from family_codec import decode_fixed_utf16
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from engine import connect,ingest_capture

PROFILE_PATH=Path(__file__).with_name('finance_native_profile.json')
PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout'];STRIDE=PROFILE['struct_size']
CORE_IDS=set(range(7))|set(range(8,30))|{31}


def finance_projection_ranges():
    ranges=[]
    for spec in (PROFILE['scalars']|PROFILE['packed']|PROFILE['identity']).values():
        f=spec['binding'];ranges.append((f['offset'],f['offset']+spec.get('extent',1)*f['size']))
    merged=[]
    for low,high in sorted(ranges):
        if not 0<=low<high<=STRIDE:raise ValueError('finance projection outside TEAM')
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    return merged


def decode_finance(raw):
    if len(raw)!=STRIDE:raise ValueError('finance decoder needs reconstructed TEAM row')
    result={}
    for spec in PROFILE['scalars'].values():
        f=spec['binding'];part=raw[f['offset']:f['offset']+4];column=spec['column']
        if spec['primitive']=='float':
            word=int.from_bytes(part,'little');value=struct.unpack('<f',part)[0]
            result[column+'_word_u32']=word;result[column+'_real']=value if math.isfinite(value) else None
        else:result[column]=int.from_bytes(part,'little',signed=spec['primitive']=='int')
    for spec in PROFILE['packed'].values():
        f=spec['binding'];value=(int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little')>>f['start_bit'])&((1<<f['width'])-1)
        result[spec['column']]=value
        if 'enum' in spec:result[spec['column'].removesuffix('_raw')+'_label']=PROFILE['enum_labels'][spec['enum']].get(str(value),{}).get('label')
    return result


def verify_finance_metadata(reader):
    metadata=[]
    for entry in PROFILE['types']:
        if entry['name']=='TEAMDATA':
            value=read_native_fields(reader,entry,STRIDE,read_enums=False);native={f['name_crc']:f for f in value['fields']}
            for name,spec in (PROFILE['scalars']|PROFILE['packed']|PROFILE['identity']).items():
                old=spec['binding'];current=native[old['name_crc']]
                if current['words'][1]!=old['words'][1]:raise ValueError('finance Native primitive changed: '+name)
                if old['enum_pointer'] and current['enum_pointer']!=reader.module_base+old['enum_pointer']-0x140000000:raise ValueError('finance Native enum binding changed: '+name)
                if 'extent' in spec:
                    ptr=current['words'][6]|current['words'][7]<<32;raw=reader.read(ptr,24,'FINANCE_NAME_DIMENSION:'+name)
                    if raw!=bytes.fromhex(spec['dimension_control_hex']):raise ValueError('finance Native name dimensions changed: '+name)
                    if reader.read(ptr,24,'FINANCE_NAME_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('finance name dimensions unstable')
        else:
            value=read_native_enum(reader,entry);expected={(int(k),v['name_crc']) for k,v in PROFILE['enum_labels'][entry['name']].items()}
            if len(value['values'])!=len(expected) or {(v['value'],v['name_crc']) for v in value['values']}!=expected:raise ValueError('finance Native enum changed')
        metadata.append(value)
    return metadata


def collect_finance(reader):
    mode,blobs=collect_game_mode(reader);mode_blobs=dict(blobs);metadata=verify_finance_metadata(reader);controls=[]
    def read(address,size,label):
        raw=reader.read(address,size,label);controls.append((address,raw,label));return raw
    pointer=read(reader.module_base+ROSTER_RVA,8,'FINANCE_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    if root<0x10000:raise ValueError('finance roster root absent')
    descriptor=read(root+8*16,16,'FINANCE_TEAM_DESCRIPTOR');count,base=struct.unpack('<QQ',descriptor)
    if not 1<=count<=1024 or base<0x10000:raise ValueError('finance TEAM directory outside envelope')
    ranges=finance_projection_ranges();teams=[];seen=set();id_offset=PROFILE['identity']['Id']['binding']['offset']
    for index in range(count):
        address=base+index*STRIDE;native_id=int.from_bytes(read(address+id_offset,2,f'FINANCE_TEAM_ID:{index}'),'little')
        if native_id not in CORE_IDS:continue
        if native_id in seen:raise ValueError('finance duplicate current core TEAM ID')
        seen.add(native_id);raw=bytearray(STRIDE);parts=[]
        for low,high in ranges:
            part=read(address+low,high-low,f'FINANCE_TEAM_PROJECTION:{index}:{low}');raw[low:high]=part;parts.append(part)
        if int.from_bytes(raw[id_offset:id_offset+2],'little')!=native_id:raise ValueError('finance TEAM identity changed')
        names={}
        for name,key in (('UnlocalizedTeamName','name'),('UnlocalizedCityName','city'),('UnlocalizedShortTeamName','abbreviation')):
            spec=PROFILE['identity'][name];off=spec['binding']['offset'];names[key]=decode_fixed_utf16(raw[off:off+spec['extent']*2])
            if not names[key]:raise ValueError('finance TEAM public name absent')
        teams.append({'native_team_id':native_id,'pool_index':index,**names,'finance':decode_finance(raw)})
        blobs[f'team-{index}.projection.bin']=b''.join(parts)
    if seen!=CORE_IDS:raise ValueError('finance current core TEAM set incomplete')
    for address,raw,label in controls:
        if reader.read(address,len(raw),label+':RECHECK')!=raw:raise ValueError('finance source changed during acquisition')
    after,after_blobs=collect_game_mode(reader)
    if after['season_year']!=mode['season_year'] or after['observation']!=mode['observation'] or after_blobs!=mode_blobs:raise ValueError('finance game-mode context changed')
    return {'season_year':mode['season_year'],'game_mode':mode['observation'],'native_metadata':metadata,'teams':teams,
        'team_descriptor':{'count':count,'address':base,'stride':STRIDE},'projection_ranges':ranges,
        'projection_bytes_per_core_team':sum(b-a for a,b in ranges),'units':PROFILE['units'],
        'game_writes':False,'getter_invocations':0,'player_struct_reads':0},blobs


def finance_payload(binding,manifest,artifacts,observed_at,token):
    year=manifest['season_year'];sid=f'season:native-year:{year}';unit='native-finance:'+token
    facts={'teams':[],'native_team_finance_observations':[],'game_mode_observations':[{'season_id':sid,**manifest['game_mode']}]}
    for team in manifest['teams']:
        tid='team:native:'+str(team['native_team_id'])
        facts['teams'].append({'team_id':tid,'native_team_id':str(team['native_team_id']),'display_name':team['city']+' '+team['name'],'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
        facts['native_team_finance_observations'].append({'team_id':tid,'observation_season_id':sid,**team['finance']})
    facts['field_gaps']=[{'affected_domain':'RES-M','target_field':'FINANCE_UI_SCALE_ACCOUNTING_DURATION_AND_CAP_ARITHMETIC','reason':PROFILE['units'],'impact':'Keep Native signed/unsigned/float/enum representations; no inferred cap space, annual totals, legal spending or UI acceptance'}]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_TYPED_TEAM_FINANCE','observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':sid,'season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_finance(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_finance(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'finance-manifest.json',manifest);_json(out/'finance-report.json',{'status':'NATIVE_TYPED_TEAM_FINANCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'player_struct_reads':0,'getter_invocations':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_TYPED_TEAM_FINANCE_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('game_mode_native_profile.json'),Path(__file__).with_name('calendar_native_profile.json')):
            artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_NATIVE_FINANCE_MODE_DATE_LAYOUT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'finance-report.json').read_bytes()).hexdigest()[:24];payload=finance_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ';receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'counts':{k:len(v) for k,v in payload['facts'].items()},'source_grade':'LIVE_READ','game_writes':False,'player_struct_reads':0,'getter_invocations':0,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'FINANCE_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
