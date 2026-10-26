"""Complete public pool vitals, injury/fatigue and morale snapshots."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from award_reader import read_native_fields
from cadence import observed_game_season_year
from engine import connect,ingest_acquired_capture as ingest_capture
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _AcquisitionReceipt,_json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from player_state_codec import PROFILE,PROFILE_PATH,LAYOUT,decode_player_state


def state_projection_ranges():
    intervals=[(0,80),(96,104),(144,152),(244,246),(760,764)]
    for group in ('vitals','health','morale'):
        intervals.extend((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8) for f in PROFILE['groups'][group].values())
    merged=[]
    for low,high in sorted(intervals):
        if any(low<b and a<high for a,b in RESTRICTED_PLAYER_RANGES):raise ValueError('state field intersects private PLAYER storage')
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    return merged


def verify_state_metadata(reader):
    result=[]
    for entry in PROFILE['types']:
        if entry['constructor_rva']==0x1e53e90:
            value=read_native_enum(reader,entry);expected={(int(code),v['name_crc']) for code,v in PROFILE['enum_labels'][entry['name']].items()}
            if {(v['value'],v['name_crc']) for v in value['values']}!=expected or len(value['values'])!=len(expected):raise ValueError('native state enum changed')
        else:
            value=read_native_fields(reader,entry,entry['expected_size'],read_enums=False)
            if entry['name']=='PLAYERDATA':
                fields={f['name_crc']:f for f in value['fields']};private=[]
                for name in ('OriginalPotential','MinPotential','MaxPotential','PreviousPotentialRaw','PotentialRaw'):
                    f=fields[zlib.crc32(name.encode())];private.append((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8))
                merged=[]
                for low,high in sorted(private):
                    if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
                    else:merged.append((low,high))
                if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('private PLAYER layout changed')
                for name in ('UnlocalizedFirstName','UnlocalizedLastName'):
                    f=fields[zlib.crc32(name.encode())];w=f['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'PLAYER_STATE_NAME_DIMENSION:'+name)
                    if (w[5]>>16)!=1 or struct.unpack_from('<I',raw)[0]!=20:raise ValueError('state native name extent changed')
                    if reader.read(ptr,24,'PLAYER_STATE_NAME_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('name dimension unstable')
        result.append(value)
    return result


def collect_player_state(reader):
    manifest,blobs=collect_public_player_pool(reader,ranges=state_projection_ranges(),metadata=verify_state_metadata(reader))
    stride=manifest['projection_stride'];ranges=manifest['projection_ranges'];projection=blobs.pop('player-detail-public-projections.bin')
    blobs['player-state-public-projections.bin']=projection;appearance=bytearray();states=[];pointers=[];cache={}
    pd=manifest['descriptors'][1];base=pd['address'];pool_end=base+pd['count']*1264
    for i,player in enumerate(manifest['players']):
        raw=reconstruct_projection(projection[i*stride:(i+1)*stride],ranges);pointer=int.from_bytes(raw[144:152],'little');part=None
        if pointer==0:status='NO_NATIVE_APPEARANCE_POINTER'
        elif pointer<0x10000:status='INVALID_LOW_APPEARANCE_POINTER'
        elif base<pointer+4 and pointer<pool_end:status='INVALID_APPEARANCE_ALIAS_TO_PLAYER_POOL'
        else:
            if pointer not in cache:cache[pointer]=reader.read(pointer,4,'PLAYER_STATE_APPEARANCE_PUBLIC')
            part=cache[pointer];status='NATIVE_APPEARANCE_PUBLIC_FIELDS_OBSERVED'
        appearance.extend(part if part is not None else bytes(4));pointers.append(pointer)
        states.append({'source_player_index':i,**decode_player_state(raw,part,appearance_status=status)})
    for pointer,raw in cache.items():
        if reader.read(pointer,4,'PLAYER_STATE_APPEARANCE_RECHECK')!=raw:raise ValueError('appearance changed during state capture')
    for i,pointer in enumerate(pointers):
        if reader.read(base+i*1264+144,8,'PLAYER_STATE_APPEARANCE_POINTER_RECHECK')!=pointer.to_bytes(8,'little'):raise ValueError('appearance binding changed')
    root=reader.read(reader.module_base+ROSTER_RVA,8,'PLAYER_STATE_FINAL_ROOT')
    if reader.read(int.from_bytes(root,'little')+16,16,'PLAYER_STATE_FINAL_PLAYER_DESCRIPTOR')!=struct.pack('<QQ',pd['count'],pd['address']):raise ValueError('state player descriptor changed')
    if observed_game_season_year(reader)!=manifest['season_year']:raise ValueError('state observation year changed')
    blobs['appearance-public-projections.bin']=bytes(appearance)
    manifest.update({'state_rows':states,'source_coverage':'COMPLETE_NATIVE_POOL_VITALS_HEALTH_MORALE','appearance_pointer_values_owner_only':pointers,
        'appearance_status_counts':dict(Counter(row['vitals']['appearance_status'] for row in states))})
    return manifest,blobs


def state_payload(binding,manifest,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='player-state:'+token;year=manifest['season_year'];players=manifest['players'];count=len(players)
    descriptor=manifest['descriptors'].get('1',manifest['descriptors'].get(1))
    if manifest.get('game_writes') is not False or manifest.get('restricted_player_bytes_read')!=0:raise ValueError('state source must be read-only/private-free')
    if descriptor['count']!=count or {p['source_player_index'] for p in players}!=set(range(count)):raise ValueError('incomplete state subjects')
    if len(manifest['state_rows'])!=count or {p['source_player_index'] for p in manifest['state_rows']}!=set(range(count)):raise ValueError('incomplete/duplicate state families')
    facts={'native_fields':[],'native_player_sources':[],'player_vitals_observations':[],'player_health_observations':[],'player_morale_observations':[]};subject_ids={};linked_ids={}
    uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    for p in players:
        i=p['source_player_index'];key='player:native:'+str(p['preserved_id_raw']);linked=None
        if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(key)==p['observed_name']:linked=key
        subject_ids[i]=f'{unit}:player:{i}';linked_ids[i]=linked
        facts['native_player_sources'].append({'player_source_id':subject_ids[i],**p,'player_id':linked,
            'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for group,table in (('vitals','player_vitals_observations'),('health','player_health_observations'),('morale','player_morale_observations')):
        definitions={**PROFILE['groups'][group],**(PROFILE['groups']['appearance'] if group=='vitals' else {})}
        for column,f in definitions.items():
            target='weight_raw' if column=='weight' else 'morale_word_raw' if column=='morale' else column
            facts['native_fields'].append({'field_id':'CURRENT_PLAYER_STATE_V1:'+str(f['name_crc']),'source_group':'RES-P','native_key':f['native_name'],
                'table_name':table,'column_name':target,'evidence_grade':'CURRENT_NATIVE_FIELDS_PRIMITIVE_TYPES_AND_ENUMS_VERIFIED','visibility':'GM_PUBLIC',
                'min_native_value':0,'max_native_value':(1<<f['width'])-1,'codec':f'{f["native_type"]}_bit{f["start_bit"]}_width{f["width"]}_at{f["offset"]}',
                'layout_version':LAYOUT,'source_ref':'player_state_native_profile.json; current native metadata','unit':'native storage; named appearance units explicit; other UI scales separate','legal_range_state':'NATIVE_STORAGE_WIDTH_VERIFIED; UI_RANGE_SEPARATE'})
        for state in manifest['state_rows']:
            i=state['source_player_index'];row={'player_id':linked_ids[i],'source_player_id':subject_ids[i],'layout_version':LAYOUT,**state[group]}
            facts[table].append(row)
    facts['field_gaps']=[dict(affected_domain='RES-P',target_field=t,reason=r,impact=effect) for t,r,effect in (
        ('VITAL_UI_CALENDAR_WEIGHT_AND_ADDITIONAL_FIELDS','Raw birth components/positions and native float weight are read; weight UI unit, month convention, age, college/country remain incomplete','No canonical birth_date, age or country invented; appearance cm values derive only from named native units'),
        ('HEALTH_AGGREGATE_AVAILABILITY_AND_RECOVERY','Both native injury slots/statuses/durations/progress are observed; status combination, current energy and remaining recovery days need separate native/UI proof','No single severity/availability or recovery-day conversion inferred'),
        ('MORALE_UI_SCALE_AND_PLAYING_ROLE','Native morale float/event/s8 adjustment and OrgRole are observed; OrgRole is organizational and is not playing-time role or satisfaction','Keep float words and exact enum labels; legacy morale_raw/role_code/satisfaction remain unasserted'),
        ('STATE_SUBJECT_LIFECYCLE','Current reciprocal roster matches are qualified observations, not lifecycle certification','Source-only pool subjects retained without invented canonical players'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_PLAYER_VITALS_HEALTH_MORALE','observed_at':stamp,
        'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_player_state(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_player_state(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'player-state-manifest.json',manifest)
        report={'status':'COMPLETE_NATIVE_PLAYER_STATE_CAPTURED','observed_at':stamp,'pid':pid,'binding_sha256':binding_hash,'read_trace':reader.trace,
            'game_writes':False,'restricted_player_bytes_read':0,'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),PROFILE_PATH,Path(__file__).with_name('player_state_codec.py'),Path(__file__).with_name('player_detail_reader.py'))},
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'player-state-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'NATIVE_PUBLIC_PLAYER_STATE_OR_CONTROL','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        token=hashlib.sha256((out/'player-state-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as conn:
            canonical={r['player_id']:r['display_name'] for r in conn.execute('SELECT player_id,display_name FROM players')}
            payload=state_payload(binding,manifest,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ'
            receipt=_AcquisitionReceipt(payload,reader);status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'source_pid':pid,'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},
            'appearance_status_counts':manifest['appearance_status_counts'],'game_writes':False,'restricted_player_bytes_read':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'PLAYER_STATE_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
