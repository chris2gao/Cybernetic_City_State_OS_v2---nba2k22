"""Native global TEAM lineups, stored rotation matrix and PLAYER PlayingTime."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,math,struct,zlib
from pathlib import Path
from award_reader import read_native_fields
from league_reader import read_native_enum
from game_mode_reader import collect_game_mode
from family_codec import decode_fixed_utf16
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt,RESTRICTED_PLAYER_RANGES
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from engine import connect,ingest_acquired_capture as ingest_capture

PROFILE_PATH=Path(__file__).with_name('lineup_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout'];CORE_IDS=set(range(7))|set(range(8,30))|{31}
LINEUP_KINDS=tuple(n for n in PROFILE['arrays'] if n not in ('CustomLineupName','AdvancedRotationPlayerId','LineupPlayer'))


def native_unsigned(raw,field):
    offset,size,start,width=(field[k] for k in ('offset','size','start_bit','width'))
    if not 1<=width<=64 or start+width>size*8 or offset+size>len(raw):raise ValueError('lineup scalar outside source')
    return int.from_bytes(raw[offset:offset+size],'little')>>start&((1<<width)-1)


def lineup_player_ranges():
    ranges=[(0,80),(96,104),(244,246),(248,252),(760,768)]
    if any(a<hi and lo<b for a,b in ranges for lo,hi in RESTRICTED_PLAYER_RANGES):raise ValueError('lineup projection intersects private PLAYER field')
    return ranges


def verify_lineup_metadata(reader):
    result=[]
    for entry in PROFILE['types']:
        name=entry['name']
        if name in PROFILE['enum_labels']:
            value=read_native_enum(reader,entry);expected={(int(k),v['name_crc']) for k,v in PROFILE['enum_labels'][name].items()}
            if len(value['values'])!=len(expected) or {(v['value'],v['name_crc']) for v in value['values']}!=expected:raise ValueError('Native lineup enum changed')
        else:
            value=read_native_fields(reader,entry,4696 if name=='TEAMDATA' else 1264,read_enums=False);native={f['name_crc']:f for f in value['fields']}
            specs={n:s['binding'] for n,s in PROFILE['arrays'].items()}|PROFILE['team_flags']|PROFILE['team_counts']|{n:s['binding'] for n,s in PROFILE['team_identity'].items()} if name=='TEAMDATA' else PROFILE['player_fields']|PROFILE['private_player_fields']
            for field_name,old in specs.items():
                current=native[old['name_crc']]
                if current['words'][1]!=old['words'][1]:raise ValueError('Native lineup primitive binding changed')
                if old['enum_pointer'] and current['enum_pointer']!=reader.module_base+old['enum_pointer']-0x140000000:raise ValueError('Native lineup nested enum changed')
                if name=='TEAMDATA' and field_name in PROFILE['arrays']:
                    spec=PROFILE['arrays'][field_name];rank=current['words'][5]>>16;ptr=current['words'][6]|current['words'][7]<<32
                    if rank!=len(spec['dimensions']):raise ValueError('Native lineup array rank changed')
                    raw=reader.read(ptr,rank*24,'LINEUP_DIMENSIONS:'+field_name)
                    if [struct.unpack_from('<I',raw,i*24)[0] for i in range(rank)]!=spec['dimensions'] or [struct.unpack_from('<Q',raw,i*24+8)[0] for i in range(rank)]!=spec['dimension_strides']:raise ValueError('Native lineup array extent/stride changed')
                    if reader.read(ptr,rank*24,'LINEUP_DIMENSIONS_RECHECK:'+field_name)!=raw:raise ValueError('Native lineup dimensions unstable')
                    current['runtime_dimension_control_hex']=raw.hex()
                elif field_name in ('UnlocalizedFirstName','UnlocalizedLastName') or name=='TEAMDATA' and field_name in PROFILE['team_identity'] and 'extent' in PROFILE['team_identity'][field_name]:
                    extent=20 if name=='PLAYERDATA' else PROFILE['team_identity'][field_name]['extent'];w=current['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'LINEUP_NAME_DIMENSION:'+field_name)
                    if w[5]>>16!=1 or struct.unpack_from('<I',raw)[0]!=extent or reader.read(ptr,24,'LINEUP_NAME_DIMENSION_RECHECK:'+field_name)!=raw:raise ValueError('Native lineup identity name extent changed')
            if name=='PLAYERDATA':
                ranges=[]
                for old in PROFILE['private_player_fields'].values():
                    f=native[old['name_crc']];ranges.append((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8))
                merged=[]
                for a,b in sorted(ranges):
                    if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
                    else:merged.append((a,b))
                if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('private PLAYER exclusion changed')
        result.append(value)
    return result


def resolve_lineup_pointer(pointer,descriptor,players,owner):
    if pointer==0:return {'source_player_index':None,'pointer_status':'NULL_POINTER'}
    index,remainder=divmod(pointer-descriptor['address'],1264)
    if not 0<=index<descriptor['count']:return {'source_player_index':None,'pointer_status':'OUTSIDE_CURRENT_PLAYER_POOL'}
    if remainder:return {'source_player_index':None,'pointer_status':'MISALIGNED_PLAYER_POINTER'}
    p=players[index];same=p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and p['native_team_id']==owner
    return {'source_player_index':index,'pointer_status':'RECIPROCAL_CURRENT_TEAM_ROSTER' if same else 'CURRENT_POOL_REFERENT_WITHOUT_OWNER_ROSTER_MATCH'}


def decode_team_lineups(raw,player_descriptor,players,owner):
    if len(raw)!=4696:raise ValueError('reconstructed TEAM lineup source must be4696 bytes')
    settings={PROFILE['team_flag_columns'][name]:native_unsigned(raw,f) for name,f in PROFILE['team_flags'].items()}
    settings['number_of_lineup_players_raw']=native_unsigned(raw,PROFILE['team_counts']['NumberOfLineupPlayers']);spec=PROFILE['arrays']['CustomLineupName'];off=spec['binding']['offset']
    try:settings['custom_lineup_name']=decode_fixed_utf16(raw[off:off+spec['dimensions'][0]*2]) or None;settings['custom_name_status']='OBSERVED_UTF16' if settings['custom_lineup_name'] else 'EMPTY_NATIVE_NAME'
    except UnicodeDecodeError:settings['custom_lineup_name']=None;settings['custom_name_status']='INVALID_UTF16_PREFIX'
    pointers={}
    for name in ('LineupPlayer',)+LINEUP_KINDS:
        spec=PROFILE['arrays'][name];off=spec['binding']['offset'];pointers[name]=[{'slot_index':i,**resolve_lineup_pointer(struct.unpack_from('<Q',raw,off+i*8)[0],player_descriptor,players,owner)} for i in range(spec['dimensions'][0])]
    spec=PROFILE['arrays']['AdvancedRotationPlayerId'];dims=spec['dimensions'];strides=spec['dimension_strides'];settings.update(advanced_axis0_count=dims[0],advanced_axis1_count=dims[1])
    advanced=[{'axis0_index':i,'axis1_index':j,'native_player_id_raw':struct.unpack_from('<H',raw,spec['binding']['offset']+i*strides[0]+j*strides[1])[0],'namespace_status':'UNVERIFIED_NATIVE_PLAYER_ID_NAMESPACE'} for i in range(dims[0]) for j in range(dims[1])]
    return {'settings':settings,'lineup_player_slots':pointers.pop('LineupPlayer'),'named_lineups':pointers,'advanced_slots':advanced}


def team_lineup_ranges():
    intervals=[(f['offset'],f['offset']+f['size']) for f in list(PROFILE['team_flags'].values())+list(PROFILE['team_counts'].values())]
    for spec in PROFILE['arrays'].values():
        size=math.prod(spec['dimensions'])*(8 if spec['binding']['size']==1264 else 2);off=spec['binding']['offset'];intervals.append((off,off+size))
    for spec in PROFILE['team_identity'].values():
        f=spec['binding'];intervals.append((f['offset'],f['offset']+f['size']*spec.get('extent',1)))
    merged=[]
    for a,b in sorted(intervals):
        if not 0<=a<b<=4696:raise ValueError('lineup field outside TEAM')
        if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else:merged.append((a,b))
    return merged


def collect_lineups(reader):
    mode,blobs=collect_game_mode(reader);mode_blobs=dict(blobs);metadata=verify_lineup_metadata(reader)
    roster_pointer=reader.read(reader.module_base+ROSTER_RVA,8,'LINEUP_INITIAL_ROSTER_POINTER')
    pool,pool_blobs=collect_public_player_pool(reader,ranges=lineup_player_ranges(),metadata=metadata);blobs.update(pool_blobs)
    if pool['season_year']!=mode['season_year']:raise ValueError('lineup source game-season mismatch')
    pd=pool['descriptors'][1];td=pool['descriptors'][8];players=pool['players'];controls=[];teams=[];ranges=team_lineup_ranges();projection=pool_blobs['player-detail-public-projections.bin'];stride=pool['projection_stride'];rotations=[]
    for i in range(len(players)):
        raw=reconstruct_projection(projection[i*stride:(i+1)*stride],pool['projection_ranges']);code=native_unsigned(raw,PROFILE['player_fields']['ForceNonStarter'])
        rotations.append({'source_player_index':i,'playing_time_raw':native_unsigned(raw,PROFILE['player_fields']['PlayingTime']),'force_non_starter_raw':code,'force_non_starter_label':PROFILE['enum_labels']['PLAYERDATA_FORCE_NON_STARTER_TYPE'].get(str(code),{}).get('label')})
    for address,tid in sorted(pool['core_team_pointer_map'].items(),key=lambda item:item[1]):
        raw=bytearray(4696);parts=[];index=(address-td['address'])//4696
        for a,b in ranges:
            value=reader.read(address+a,b-a,f'LINEUP_TEAM:{tid}:{a}');raw[a:b]=value;parts.append(value);controls.append((address+a,value,f'LINEUP_TEAM_RECHECK:{tid}:{a}'))
        if native_unsigned(raw,PROFILE['team_identity']['Id']['binding'])!=tid:raise ValueError('lineup TEAM identity changed')
        names={}
        for native,column in (('UnlocalizedTeamName','name'),('UnlocalizedCityName','city')):
            spec=PROFILE['team_identity'][native];off=spec['binding']['offset'];names[column]=decode_fixed_utf16(raw[off:off+2*spec['extent']])
            if not names[column]:raise ValueError('lineup TEAM identity name absent')
        teams.append({'native_team_id':tid,'pool_index':index,**names,**decode_team_lineups(raw,pd,players,tid)});blobs[f'team-{tid}.lineup-projection.bin']=b''.join(parts)
        roster=pool_blobs[f'team-{tid}.roster.bin'];controls.append((address,roster,f'LINEUP_ROSTER_RECHECK:{tid}'))
    if {t['native_team_id'] for t in teams}!=CORE_IDS:raise ValueError('lineup core TEAM set incomplete')
    for i in range(len(players)):
        raw=reconstruct_projection(projection[i*stride:(i+1)*stride],pool['projection_ranges'])
        for a,b in pool['projection_ranges']:
            if reader.read(pd['address']+i*1264+a,b-a,f'LINEUP_PLAYER_FINAL_RECHECK:{i}:{a}')!=raw[a:b]:raise ValueError('lineup PLAYER subject changed')
    for address,value,label in controls:
        if reader.read(address,len(value),label)!=value:raise ValueError('lineup TEAM or roster source changed')
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'LINEUP_FINAL_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    if pointer!=roster_pointer:raise ValueError('lineup roster root changed')
    for slot,directory in ((1,pd),(8,td)):
        if reader.read(root+slot*16,16,'LINEUP_FINAL_DESCRIPTOR:'+str(slot))!=struct.pack('<QQ',directory['count'],directory['address']):raise ValueError('lineup directory changed')
    after,after_blobs=collect_game_mode(reader)
    if after['season_year']!=mode['season_year'] or after['observation']!=mode['observation'] or after_blobs!=mode_blobs:raise ValueError('lineup game-mode context changed')
    pool.update(teams=teams,player_rotation_rows=rotations,game_mode=mode['observation'],team_projection_ranges=ranges,team_projection_bytes=sum(b-a for a,b in ranges),getter_invocations=0)
    return pool,blobs


def lineup_payload(binding,m,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='native-lineups:'+token;players=m['players'];uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER');source_ids={};linked={};sid=f'season:native-year:{m["season_year"]}'
    descriptor=m['descriptors'].get(1,m['descriptors'].get('1'))
    if m.get('game_writes') is not False or m.get('restricted_player_bytes_read')!=0 or len(players)!=descriptor['count'] or {p['source_player_index'] for p in players}!=set(range(len(players))):raise ValueError('incomplete/nonpublic Native lineup subjects')
    if len(m['player_rotation_rows'])!=len(players) or {r['source_player_index'] for r in m['player_rotation_rows']}!=set(range(len(players))):raise ValueError('incomplete Native PLAYER rotation rows')
    facts={name:[] for name in ('teams','native_player_sources','native_player_rotation_observations','team_rotation_slots','team_lineup_observations','team_lineup_slots','team_advanced_rotation_slots')}
    facts['game_mode_observations']=[{'season_id':sid,**m['game_mode']}]
    for p in players:
        i=p['source_player_index'];candidate='player:native:'+str(p['preserved_id_raw']);linked[i]=candidate if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(candidate)==p['observed_name'] else None;source_ids[i]=f'{unit}:player:{i}'
        facts['native_player_sources'].append({'player_source_id':source_ids[i],**p,'player_id':linked[i],'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked[i] else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    rotation={r['source_player_index']:r for r in m['player_rotation_rows']}
    for i,r in rotation.items():facts['native_player_rotation_observations'].append({'source_player_id':source_ids[i],'player_id':linked[i],**{k:v for k,v in r.items() if k!='source_player_index'}})
    def subject(row):
        i=row['source_player_index'];return {'source_player_id':source_ids[i] if i is not None else None,'player_id':linked[i] if i is not None else None,'pointer_status':row['pointer_status'],'slot_index':row['slot_index']}
    if len(m['teams'])!=30 or {t['native_team_id'] for t in m['teams']}!=CORE_IDS:raise ValueError('incomplete Native lineup teams')
    for t in m['teams']:
        tid='team:native:'+str(t['native_team_id']);facts['teams'].append({'team_id':tid,'native_team_id':str(t['native_team_id']),'display_name':t['city']+' '+t['name'],'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
        facts['team_lineup_observations'].append({'team_id':tid,'observation_season_id':sid,**t['settings']})
        if len(t['lineup_player_slots'])!=13 or {r['slot_index'] for r in t['lineup_player_slots']}!=set(range(13)):raise ValueError('incomplete Native global lineup slots')
        for r in t['lineup_player_slots']:
            i=r['source_player_index'];facts['team_rotation_slots'].append({'team_id':tid,**subject(r),'source_kind':'LineupPlayer','native_playing_time_raw':rotation[i]['playing_time_raw'] if i is not None else None,'planned_minutes':None,'role_code':None})
        if set(t['named_lineups'])!=set(LINEUP_KINDS):raise ValueError('incomplete Native named lineup groups')
        for name,slots in t['named_lineups'].items():
            if len(slots)!=5 or {r['slot_index'] for r in slots}!=set(range(5)):raise ValueError('incomplete Native named lineup slots')
            facts['team_lineup_slots'].extend({'team_id':tid,'lineup_kind':name,**subject(r)} for r in slots)
        if len(t['advanced_slots'])!=240 or {(r['axis0_index'],r['axis1_index']) for r in t['advanced_slots']}!={(i,j) for i in range(48) for j in range(5)}:raise ValueError('incomplete Native advanced rotation array')
        facts['team_advanced_rotation_slots'].extend({'team_id':tid,**r} for r in t['advanced_slots'])
    facts['field_gaps']=[{'affected_domain':'RES-T','target_field':target,'reason':reason,'impact':impact} for target,reason,impact in (
        ('PLAYING_TIME_UI_MINUTES_AND_ACTIVE_LINEUPS',PROFILE['playing_time_units'],'planned_minutes and role_code remain NULL; stored flags/arrays are not played-game effects'),
        ('ADVANCED_ROTATION_AXIS_AND_ID_NAMESPACE',PROFILE['advanced_axes']+'; '+PROFILE['advanced_player_namespace'],'Retain every array coordinate/raw ID; no inferred period/minute/position or canonical player assignment'),
        ('LINEUP_REFERENT_LIFECYCLE','Exact current PLAYER pointers and qualified reciprocal roster aliases are observations, not historical identity proof','Null/outside/misaligned/other-roster references remain explicit; no forced canonical match'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_TEAM_LINEUPS_AND_PLAYER_ROTATION','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':sid,'season_code':f'NATIVE_YEAR:{m["season_year"]}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_lineups(pid,save_directory,loaded_filename,new_output_directory):
    binding,bhash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_lineups(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'lineup-manifest.json',m);_json(out/'lineup-report.json',{'status':'COMPLETE_NATIVE_TEAM_LINEUPS_AND_PUBLIC_PLAYER_ROTATION_CAPTURED','observed_at':stamp,'pid':pid,'binding_sha256':bhash,'read_trace':reader.trace,'game_writes':False,'getter_invocations':0,'restricted_player_bytes_read':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_NATIVE_LINEUP_AND_PUBLIC_ROTATION_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('game_mode_native_profile.json'),Path(__file__).with_name('calendar_native_profile.json')):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_NATIVE_LINEUP_AND_MODE_LAYOUT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'lineup-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as c:
            canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')};payload=lineup_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(c,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'counts':{k:len(v) for k,v in payload['facts'].items()},'source_grade':'LIVE_READ','game_writes':False,'getter_invocations':0,'restricted_player_bytes_read':0,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'LINEUP_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
