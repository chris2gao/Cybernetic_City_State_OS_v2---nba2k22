"""Bounded read-only opponent plans and current training fields.

GAMEPLAN bytes are decoded separately from packed COACHDATA. Training history
arrays are deliberately not acquired: only native ID and registered flag bytes
are requested. Native plan IDs remain raw until their namespaces are proven.
"""
from collections import Counter
from datetime import datetime,timezone
from functools import lru_cache
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
from schema_model import DOMAIN,GAMEPLAN_HEADER_MAP,DEFENSE_COLUMN_MAP
from family_codec import decode_fixed_utf16
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json,read_binding,bound_database,_AcquisitionReceipt
from organization_reader import native_metadata,CORE_IDS,COACH_PROFILE
from schedule_reader import bounded_block
from engine import connect,ingest_acquired_capture as ingest_capture

TRAINING_PROFILE_PATH=DOMAIN/'config/state_io_native/training.json'
TRAINING_PROFILE=json.loads(TRAINING_PROFILE_PATH.read_bytes())
DEFENSE_NAMES=('PressureOnball','PressureOffball','ForceDirection','ScreenDefenseOnBall','ScreenDefenseHedge',
    'OffballScreenDefense','PostDefense','DoubleTeamPerimeter','DoubleTeamPost','ScreenDefenseOnBall5',
    'ScreenDefenseHedge5','SwitchRule','OnballHelp','ScreenHelp','ExtendPressure','TagOnRoll','StayAttached','PreRotate')


@lru_cache(maxsize=None)
def source_module(name):
    src=DOMAIN/'src';sys.path.insert(0,str(src))
    try:
        spec=importlib.util.spec_from_file_location('world_planning_'+name,src/(name+'.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    finally:sys.path.remove(str(src))


def decode_plan(raw,catalog):
    header=source_module('gameplan_codec').decode_header(raw)
    rotations=[];defenses=[]
    for i in range((0x64-6)//4):
        off=6+i*4
        rotations.append({'slot_index':i,'native_rotation_id_raw':int.from_bytes(raw[off:off+2],'little'),
            'rotation_spot_raw':raw[off+2],'playing_time_raw':raw[off+3],
            'identity_status':'NATIVE_NAMESPACE_UNVERIFIED_NOT_CANONICAL_PLAYER'})
    for i in range(23):
        off=0x64+i*12;matchup,defender=struct.unpack_from('<HH',raw,off);part=raw[off+4:off+12]
        values={};unknown=[]
        if matchup!=65535:
            for name in DEFENSE_NAMES:
                f=catalog[name];shift=f['offset']*8+f['start_bit'];value=(int.from_bytes(part,'little')>>shift)&((1<<f['width'])-1)
                legal={'0','1'} if f.get('native_boolean') else set(f['native_enum_name_crc32'])
                if str(value) not in legal:unknown.append(name)
                values[name]=value
        defenses.append({'slot_index':i,'native_matchup_id_raw':matchup,'native_defender_id_raw':defender,
            'slot_status':'EMPTY_SENTINEL' if matchup==65535 else ('UNKNOWN_ENUM_CODE' if unknown else 'NATIVE_VALUES_OBSERVED'),
            'values':values,'unknown_enum_fields':unknown})
    return {'header':header,'rotations':rotations,'defenses':defenses}


def training_team_values(raw):
    if len(raw)!=88:raise ValueError('TEAM_TRAINING must be 88 bytes')
    result={}
    fields=TRAINING_PROFILE['structures']['team_training']['offsets']
    for name in ('home_intensity','away_intensity','automate_intensity','rest_before_b2b','rest_after_b2b','injury_recovery'):
        f=fields[name];result[name+'_raw']=(raw[int(f['offset'],16)]>>f['start_bit'])&((1<<f['width'])-1)
    return result


def training_player_values(raw):
    if len(raw)!=4:raise ValueError('PLAYER_TRAINING flags must be four bytes')
    flags=TRAINING_PROFILE['structures']['player_training']['offsets']['flags'];word=int.from_bytes(raw,'little')
    return {name+'_raw':(word>>flags[name]['start_bit'])&((1<<flags[name]['width'])-1)
        for name in ('position','player_type','intensity','injury_recovery','is_intensity_overriden')}


def classify_training_slots(slots,roster_ids):
    counts=Counter(p['native_player_id_raw'] for p in slots)
    result=[]
    for original in slots:
        p=dict(original);key=p['native_player_id_raw']
        p['identity_status']='EMPTY_SENTINEL' if key in (0,0xFFFFFFFF) else ('DUPLICATE_NATIVE_ID' if counts[key]!=1 else
            ('UNIQUE_CURRENT_ROSTER_ID' if key in roster_ids else 'NOT_IN_CURRENT_CORE_ROSTER'))
        result.append(p)
    return result


def collect_planning(reader):
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'PLAN_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    descriptors={};tables={}
    for slot,stride,maximum in ((1,1264,8192),(8,4696,1024),(28,62,10000)):
        raw=reader.read(root+slot*16,16,f'PLAN_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum:raise ValueError('planning descriptor outside envelope')
        descriptors[slot]=raw;tables[slot]={'count':count,'address':address,'stride':stride}
    evidence,_,locator=native_metadata(reader)
    if locator.rip_pointer(COACH_PROFILE['native']['roster_getter_rva'],'488b05',True)!=root:raise ValueError('active roster getter and slot disagree')
    franchise=locator.rip_pointer(COACH_PROFILE['native']['franchise_load_rva'],'488b1d');locator.franchise=franchise
    training_rva=int(TRAINING_PROFILE['system_info']['slot_training'],16)
    training_pointer=reader.read(reader.module_base+training_rva,8,'PLAN_TRAINING_POINTER');training=int.from_bytes(training_pointer,'little')
    franchise_pointer=reader.read(reader.module_base+int(TRAINING_PROFILE['system_info']['slot_franchise'],16),8,'PLAN_FRANCHISE_POINTER')
    if int.from_bytes(franchise_pointer,'little')!=franchise:raise ValueError('franchise getter and profile slot disagree')
    blobs={};controls=[];teams=[];players=[];td=tables[8];pd=tables[1]
    for i in range(td['count']):
        address=td['address']+i*4696;rawid=reader.read(address+0xCA8,2,'PLAN_TEAM_NATIVE_ID');tid=int.from_bytes(rawid,'little')
        if tid not in CORE_IDS:continue
        if any(t['native_team_id']==tid for t in teams):raise ValueError('duplicate current TEAM ID')
        roster=reader.read(address,200,f'PLAN_TEAM:{tid}:ROSTER');name=reader.read(address+0x2B4,40,f'PLAN_TEAM:{tid}:NAME')
        city=reader.read(address+0x2E6,36,f'PLAN_TEAM:{tid}:CITY');stats=reader.read(address+0xE80,2,f'PLAN_TEAM:{tid}:STATS_INDEX')
        teams.append({'native_team_id':tid,'address':address,'pool_index':i,'name':decode_fixed_utf16(name),'city':decode_fixed_utf16(city),'stats_index':int.from_bytes(stats,'little')})
        for off,data,label in ((0,roster,'roster'),(0xCA8,rawid,'id'),(0x2B4,name,'name'),(0x2E6,city,'city'),(0xE80,stats,'stats')):
            blobs[f'team-{tid}.{label}.bin']=data;controls.append((address+off,data,f'PLAN_TEAM:{tid}:{label}:RECHECK'))
        for roster_slot in range(25):
            ptr=struct.unpack_from('<Q',roster,roster_slot*8)[0]
            if not ptr:continue
            index,rem=divmod(ptr-pd['address'],1264)
            if rem or not 0<=index<pd['count']:raise ValueError('roster member outside current PLAYER descriptor')
            public=reader.read(ptr,80,f'PLAN_PLAYER:{index}:NAME');ident=reader.read(ptr+0x2F8,2,f'PLAN_PLAYER:{index}:ID')
            owner=reader.read(ptr+0x60,8,f'PLAN_PLAYER:{index}:TEAM')
            if int.from_bytes(owner,'little')!=address:raise ValueError('PLAYER/TEAM roster pointers do not reciprocate')
            display=(decode_fixed_utf16(public[40:80])+' '+decode_fixed_utf16(public[:40])).strip()
            native_id=int.from_bytes(ident,'little')
            if not display or any(p['native_player_id']==native_id for p in players):raise ValueError('empty or duplicate assigned PLAYER identity')
            players.append({'native_player_id':native_id,'display_name':display,'native_team_id':tid,'pool_index':index,'roster_slot':roster_slot})
            for off,data,label in ((0,public,'name'),(0x2F8,ident,'id'),(0x60,owner,'team')):
                blobs[f'player-{index}.{label}.bin']=data;controls.append((ptr+off,data,f'PLAN_PLAYER:{index}:{label}:RECHECK'))
    if {t['native_team_id'] for t in teams}!=CORE_IDS:raise ValueError('core TEAM set incomplete')
    locator.teams={t['native_team_id']:t for t in teams};locator.resolve_managers()
    catalog=source_module('coaching_reader').defensive_catalog(locator)
    plans=[];other_plan_slots=[];team_training=[];mentor_managers=[];mentor_relations=[];native=COACH_PROFILE['native']
    for tid,manager in sorted(locator.managers.items()):
        franchise_slot,rem=divmod(manager-(franchise+native['franchise_teams_offset']),native['franchise_team_stride'])
        if rem or not 0<=franchise_slot<native['franchise_capacity']:raise ValueError('franchise owner slot invalid')
        opponents=set()
        for i in range(native['gameplan_capacity']):
            address=manager+native['gameplan_start']+i*native['gameplan_stride']
            raw=reader.read(address,880,f'PLAN_GAMEPLAN:{tid}:{i}');header=source_module('gameplan_codec').decode_header(raw)
            blobs[f'gameplan-{tid}-{i}.bin']=raw;controls.append((address,raw,f'PLAN_GAMEPLAN:{tid}:{i}:RECHECK'))
            owner,opp=header['team_id'],header['opponent_team_id']
            if owner==65535 or opp not in CORE_IDS:
                other_plan_slots.append({'native_team_id':tid,'source_slot_index':i,**header});continue
            if owner!=tid or opp==tid or opp in opponents:raise ValueError('gameplan owner/opponent relation invalid')
            opponents.add(opp);decoded=decode_plan(raw,catalog)
            plans.append({'native_team_id':tid,'native_opponent_team_id':opp,'source_slot_index':i,'franchise_slot':franchise_slot,**decoded})
        if opponents!=CORE_IDS-{tid}:raise ValueError('current core opponent plan set incomplete')
        address=training+franchise_slot*88;raw=reader.read(address,88,f'PLAN_TEAM_TRAINING:{tid}')
        team_training.append({'native_team_id':tid,'franchise_slot':franchise_slot,'values':training_team_values(raw)})
        blobs[f'team-training-{tid}.bin']=raw;controls.append((address,raw,f'PLAN_TEAM_TRAINING:{tid}:RECHECK'))
        spec=TRAINING_PROFILE['structures']['mentorship_manager'];address=manager+int(spec['relative_team_offset'],16)
        raw=reader.read(address,12,f'PLAN_MENTOR_HEADER:{tid}');owner,first,count=struct.unpack('<III',raw)
        valid=owner==tid and count<=(spec['size']-12)//spec['relation_entry']['stride']
        mentor_managers.append({'native_team_id':tid,'franchise_slot':franchise_slot,'header_team_id_raw':owner,'first_badge_raw':first,
            'relation_count_raw':count,'layout_status':'OWNER_AND_COUNT_PLAUSIBLE' if valid else 'UNVERIFIED_HEADER_OR_LAYOUT'})
        blobs[f'mentor-header-{tid}.bin']=raw;controls.append((address,raw,f'PLAN_MENTOR_HEADER:{tid}:RECHECK'))
        if valid:
            for i in range(count):
                at=address+12+i*204;raw=reader.read(at,24,f'PLAN_MENTOR_RELATION:{tid}:{i}')
                mentor_relations.append({'native_team_id':tid,'source_slot_index':i,'mentee_id_raw':int.from_bytes(raw[:4],'little'),
                    'mentor_id_raw':int.from_bytes(raw[4:8],'little'),'duration_days_raw':int.from_bytes(raw[8:12],'little'),
                    'compatibility_word_raw':int.from_bytes(raw[12:16],'little'),'badge_count_raw':int.from_bytes(raw[20:24],'little')})
                blobs[f'mentor-relation-{tid}-{i}.header.bin']=raw;controls.append((at,raw,f'PLAN_MENTOR_RELATION:{tid}:{i}:RECHECK'))
    pt=TRAINING_PROFILE['structures']['player_training'];player_training=[];ids=bytearray();flagbytes=bytearray()
    for i in range(pt['max_players']):
        address=training+int(pt['array_offset'],16)+i*pt['stride']
        ident=reader.read(address,4,f'PLAN_PLAYER_TRAINING:{i}:ID');flags=reader.read(address+int(pt['offsets']['flags']['offset'],16),4,f'PLAN_PLAYER_TRAINING:{i}:FLAGS')
        player_training.append({'source_slot_index':i,'native_player_id_raw':int.from_bytes(ident,'little'),'values':training_player_values(flags)})
        ids+=ident;flagbytes+=flags;controls.extend(((address,ident,f'PLAN_PLAYER_TRAINING:{i}:ID_RECHECK'),
            (address+int(pt['offsets']['flags']['offset'],16),flags,f'PLAN_PLAYER_TRAINING:{i}:FLAGS_RECHECK')))
    player_training=classify_training_slots(player_training,{p['native_player_id'] for p in players})
    blobs['training-id-projection.bin']=bytes(ids);blobs['training-flags-projection.bin']=bytes(flagbytes)
    first=teams[0];idx=first['stats_index']
    if not 0<=idx<tables[28]['count']:raise ValueError('current native season control missing')
    raw=reader.read(tables[28]['address']+idx*62,62,'PLAN_SEASON_CONTROL');season_year=1900+raw[4]
    blobs['season-control.bin']=raw;controls.append((tables[28]['address']+idx*62,raw,'PLAN_SEASON_RECHECK'))
    for address,data,label in controls:
        if bounded_block(reader,address,len(data),label)!=data:raise ValueError('planning source changed during acquisition')
    for slot,data in descriptors.items():
        if reader.read(root+slot*16,16,f'PLAN_SLOT{slot}_RECHECK')!=data:raise ValueError('planning descriptor changed')
    for address,data,label in ((reader.module_base+ROSTER_RVA,pointer,'PLAN_ROSTER_RECHECK'),
        (reader.module_base+training_rva,training_pointer,'PLAN_TRAINING_RECHECK'),
        (reader.module_base+int(TRAINING_PROFILE['system_info']['slot_franchise'],16),franchise_pointer,'PLAN_FRANCHISE_RECHECK')):
        if reader.read(address,len(data),label)!=data:raise ValueError('planning root context changed')
    return {'teams':teams,'players':players,'descriptors':tables,'season_year':season_year,'native_metadata':evidence,'defense_catalog':catalog,
        'franchise_root':franchise,'training_root':training,'plans':plans,'other_plan_slots':other_plan_slots,'team_training':team_training,
        'player_training_slots':player_training,'mentor_managers':mentor_managers,'mentor_relations':mentor_relations,
        'training_window_scope':'PROFILE_CAPACITY_BOUND_NOT_PROVEN_ACTIVE_COUNT','training_history_arrays_read':False,'potential_bytes_read':0,'game_writes':False},blobs


def probe_planning(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_planning(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'planning-manifest.json',manifest)
        report.update({'status':'PLANNING_SOURCE_CAPTURED','read_trace':reader.trace,'artifact_sha256':{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'PLANNING_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'planning-report.json',report);return report


def planning_payload(binding,manifest,artifacts,observed_at,token):
    unit='planning:'+token;year=manifest['season_year'];tid=lambda n:'team:native:'+str(n);pid=lambda n:'player:native:'+str(n)
    roster={p['native_player_id']:p for p in manifest['players']}
    if len(roster)!=len(manifest['players']):raise ValueError('duplicate current assigned native player ID')
    def link(native_id,owner):
        return pid(native_id) if native_id in roster and roster[native_id]['native_team_id']==owner else None
    facts={name:[] for name in ('teams','players','roster_memberships','gameplan_observations','gameplan_rotation_observations',
        'gameplan_defense_observations','team_training_settings','player_training_slot_observations','player_training_observations',
        'mentor_manager_observations','native_mentor_relation_observations','mentorship_relations')}
    for t in manifest['teams']:
        facts['teams'].append({'team_id':tid(t['native_team_id']),'native_team_id':str(t['native_team_id']),
            'display_name':(t['city']+' '+t['name']).strip(),'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
    for p in manifest['players']:
        facts['players'].append({'player_id':pid(p['native_player_id']),'native_player_id':str(p['native_player_id']),
            'display_name':p['display_name'],'native_identity_status':'UNVERIFIED'})
        facts['roster_memberships'].append({'player_id':pid(p['native_player_id']),'team_id':tid(p['native_team_id']),
            'roster_status':'RECIPROCAL_CURRENT_TEAM_ROSTER_POINTER','native_roster_slot':p['roster_slot']})
    for p in manifest['plans']:
        owner,opp=p['native_team_id'],p['native_opponent_team_id'];plan=f'{unit}:plan:{owner}:{opp}';header=p['header']
        facts['gameplan_observations'].append({'plan_id':plan,'team_id':tid(owner),'opponent_team_id':tid(opp),
            'source_slot_index':p['source_slot_index'],'is_in_use_raw':header['is_in_use'],'is_tainted_raw':header['is_tainted'],
            **{column:header['values'][name] for name,column in GAMEPLAN_HEADER_MAP.items()}})
        for r in p['rotations']:
            player=link(r['native_rotation_id_raw'],owner)
            facts['gameplan_rotation_observations'].append({**{k:v for k,v in r.items() if k!='identity_status'},
                'plan_id':plan,'player_id':player,'identity_status':'CURRENT_OWN_ROSTER_UID_MATCH' if player else
                ('EMPTY_SENTINEL' if r['native_rotation_id_raw']==65535 else 'NOT_CURRENT_OWN_ROSTER')})
        for d in p['defenses']:
            target=link(d['native_matchup_id_raw'],opp);defender=link(d['native_defender_id_raw'],owner)
            facts['gameplan_defense_observations'].append({'plan_id':plan,'slot_index':d['slot_index'],
                'native_matchup_id_raw':d['native_matchup_id_raw'],'native_defender_id_raw':d['native_defender_id_raw'],
                'opponent_player_id':target,'defender_player_id':defender,'slot_status':d['slot_status'],
                'identity_status':'CURRENT_OPPONENT_ROSTER_UID_MATCH' if target else
                    ('EMPTY_SENTINEL' if d['native_matchup_id_raw']==65535 else 'NOT_CURRENT_OPPONENT_ROSTER'),
                **{DEFENSE_COLUMN_MAP[name]:value for name,value in d['values'].items()}})
    for t in manifest['team_training']:
        facts['team_training_settings'].append({'team_id':tid(t['native_team_id']),**t['values']})
    classified=classify_training_slots(manifest['player_training_slots'],set(roster))
    if any(actual['identity_status']!=declared['identity_status'] for actual,declared in zip(classified,manifest['player_training_slots'])):
        raise ValueError('training slot classification mismatch')
    for p in classified:
        facts['player_training_slot_observations'].append({k:v for k,v in p.items() if k!='values'}|p['values'])
        if p['identity_status']=='UNIQUE_CURRENT_ROSTER_ID':
            native_id=p['native_player_id_raw']
            if native_id not in roster:raise ValueError('accepted training ID not in reciprocal current roster')
            facts['player_training_observations'].append({'player_id':pid(native_id),'team_id':tid(roster[native_id]['native_team_id']),
                'source_slot_index':p['source_slot_index'],'identity_status':p['identity_status'],**p['values']})
    for m in manifest['mentor_managers']:
        facts['mentor_manager_observations'].append({'team_id':tid(m['native_team_id']),**{k:v for k,v in m.items() if k!='native_team_id'}})
    mentee_counts=Counter(r['mentee_id_raw'] for r in manifest['mentor_relations'])
    for r in manifest['mentor_relations']:
        child=link(r['mentee_id_raw'],r['native_team_id']);parent=link(r['mentor_id_raw'],r['native_team_id'])
        matched=bool(child and parent and child!=parent and mentee_counts[r['mentee_id_raw']]==1)
        facts['native_mentor_relation_observations'].append({'team_id':tid(r['native_team_id']),
            **{k:v for k,v in r.items() if k!='native_team_id'},'identity_status':'BOTH_CURRENT_OWN_ROSTER_UID_MATCH' if matched else 'UNRESOLVED_OR_AMBIGUOUS'})
        if matched:
            facts['mentorship_relations'].append({'player_id':child,'mentor_player_id':parent,'team_id':tid(r['native_team_id']),
                **{k:r[k] for k in ('source_slot_index','duration_days_raw','compatibility_word_raw','badge_count_raw')},
                'association_status':'OBSERVED_PAIR_ACTIVITY_NOT_VERIFIED'})
    facts['field_gaps']=[{'affected_domain':domain,'target_field':target,'reason':reason,'impact':impact} for domain,target,reason,impact in (
        ('RES-C','GAMEPLAN_COMMIT_VS_EFFECT','Most source plans have native commit flag0; field observation is not a played-game effect','Retain flags; no activation or performance inference'),
        ('RES-C','STALE_PLAN_PLAYER_IDS','Some stored plan IDs are not in the current corresponding roster','Keep raw IDs and NULL canonical player FK'),
        ('RES-P','TRAINING_HISTORY_ARRAYS','Only native ID and five flag fields acquired; history may contain restricted attribute information','No training attribute/overall history read or exported'),
        ('RES-P','TRAINING_SLOT_ACTIVE_COUNT','786 is a registered read bound, not a proven active count; duplicates/unmapped IDs cannot link','All slots classified; only unique current-roster IDs accepted'),
        ('RES-C','MENTOR_ACTIVITY_AND_BADGE_EFFECT','Owner/header and current-roster pair IDs observed; badge slots/activity and outcome not acquired','Association only; no badge tier, consent or development-effect assertion'),
        ('RES-C','GLOBAL_ROTATION_AND_TRAINING_FOCUS','Opponent plans and registered training flags are not global rotation/focus schedules','Legacy focus/schedule/global rotation fields remain unobserved'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_PLANNING_AND_TRAINING',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'PLANNING_AND_TRAINING_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_planning(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_planning(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'planning-manifest.json',manifest)
        report={'status':'PLANNING_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'planning-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'BOUNDED_PLANNING_NATIVE_FIELDS_OR_CONTROL','source_version':'PLANNING_AND_TRAINING_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (TRAINING_PROFILE_PATH,DOMAIN/'config/coach_tactics_profile.json',DOMAIN/'src/gameplan_codec.py',DOMAIN/'src/coach_locator.py'):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'REGISTERED_OR_CURRENT_NATIVE_LAYOUT_SOURCE','source_version':'PLANNING_AND_TRAINING_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'planning-report.json').read_bytes()).hexdigest()[:24]
        payload=planning_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'counts':{name:len(rows) for name,rows in payload['facts'].items()},
            'native_commit_flag_counts':dict(Counter(p['header']['is_in_use'] for p in manifest['plans'])),
            'training_slot_identity_counts':dict(Counter(p['identity_status'] for p in manifest['player_training_slots'])),
            'game_writes':False,'potential_bytes_read':0,'training_history_arrays_read':False,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'PLANNING_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_planning(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status']=='PLANNING_SOURCE_CAPTURED' else 2)
