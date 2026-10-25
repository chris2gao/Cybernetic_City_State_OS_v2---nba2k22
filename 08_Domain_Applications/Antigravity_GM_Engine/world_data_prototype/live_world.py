"""Operator-bound save -> bounded Windows reads -> typed world facts.

The operator supplies the loaded save filename. File metadata and process
pointers describe this acquisition; neither replaces that declaration. Only
capture_live can mint the in-process receipt used for LIVE_READ ingestion.
Public PLAYER reads skip the Potential byte entirely, including in artifacts.
"""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import struct
from engine import create_database,connect,ingest_capture,migrate_database,_digest
from family_codec import public_player_families,decode_fixed_utf16
from live_reader import ReadOnlyGameProcess,collect_known_game,ROSTER_RVA,SEASON_RVA,GAME_OFFSET,GAME_STRIDE,STATBANK_OFFSET
from owner_capture import STAT_MAP
from readers import _module
from schema_model import PROFILE,DOMAIN,VERSION as SCHEMA_VERSION

VERSION='OPERATOR_BOUND_WORLD_READ_V1'
PLAYER_STRIDE=1264
TEAM_STRIDE=4696
POTENTIAL=next(d['offset'] for d in PROFILE['fields']['PLAYER'] if d['name']=='potential')
# Current PLAYERDATA metadata also exposes original, minimum/maximum and
# previous storage. Skip their actual physical byte intervals, not just the
# main PotentialRaw byte. None is decoded into the public field families.
RESTRICTED_PLAYER_RANGES=((785,786),(880,882),(930,931),(1089,1090))


def _json(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')


def initialize_save(save_directory,save_id,native_save_file):
    """One operator-declared native file and one facts DB, no game-file writes."""
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',save_id):raise ValueError('simple save_id required')
    native=Path(native_save_file).resolve()
    if not native.is_file():raise ValueError('declared native save file does not exist')
    directory=Path(save_directory).resolve();directory.mkdir(parents=True,exist_ok=False)
    binding={'save_id':save_id,'native_save_file':str(native),'native_save_filename':native.name,
             'identity_basis':'HUMAN_DECLARED_LOADED_SAVE_FILE',
             'created_at':datetime.now(timezone.utc).isoformat(),
             'switch_contract':'Human announces loaded filename before switching. Reopen uses the same save_id.',
             'native_file_hash_is_identity':False}
    _json(directory/'save.json',binding)
    create_database(directory/'world.sqlite',save_id)
    return binding


def read_binding(save_directory,loaded_filename):
    directory=Path(save_directory).resolve();raw=(directory/'save.json').read_bytes();binding=json.loads(raw)
    if binding.get('identity_basis')!='HUMAN_DECLARED_LOADED_SAVE_FILE':raise ValueError('unsupported save binding')
    if binding['native_save_filename']!=loaded_filename:raise ValueError('loaded save filename differs from bound database')
    native=Path(binding['native_save_file'])
    if not native.is_file() or native.name!=loaded_filename:raise ValueError('bound native save file unavailable')
    with connect(bound_database(directory,binding),True) as c:
        if c.execute('SELECT save_id FROM saves').fetchone()[0]!=binding['save_id']:raise ValueError('save binding/database mismatch')
    return binding,hashlib.sha256(raw).hexdigest()


def bound_database(save_directory,binding):
    name=binding.get('database_file','world.sqlite')
    if not isinstance(name,str) or Path(name).name!=name or not name.endswith('.sqlite'):
        raise ValueError('save binding requires a local SQLite filename')
    return Path(save_directory).resolve()/name


def upgrade_bound_save(save_directory,loaded_filename):
    """Copy facts, retain old DB/declaration, atomically point to new schema."""
    directory=Path(save_directory).resolve();binding,_=read_binding(directory,loaded_filename)
    old=bound_database(directory,binding)
    with connect(old,True) as conn:old_version=conn.execute('PRAGMA user_version').fetchone()[0]
    target=directory/f'world-v{SCHEMA_VERSION}.sqlite'
    migrate_database(old,target)
    original=(directory/'save.json').read_bytes()
    backup=directory/f'save.before-v{SCHEMA_VERSION}.json'
    with backup.open('xb') as f:f.write(original)
    binding['database_file']=target.name
    pending=directory/'save.pending.json';_json(pending,binding);pending.replace(directory/'save.json')
    return {'save_id':binding['save_id'],'source_schema':old_version,'schema_version':SCHEMA_VERSION,
            'database_file':target.name,'original_database_retained':old.name}


def _utf(raw):return decode_fixed_utf16(raw)


def _public_raw(reader,address,label):
    # Excluded bytes are never requested from Windows. Zero placeholders only
    # preserve public fixed-offset decoding; no private value is reconstructed.
    parts=[];start=0
    for low,high in RESTRICTED_PLAYER_RANGES:
        if start<low:parts.append(reader.read(address+start,low-start,label+':public-segment:'+str(start)))
        parts.append(bytes(high-low));start=high
    if start<PLAYER_STRIDE:parts.append(reader.read(address+start,PLAYER_STRIDE-start,label+':public-segment:'+str(start)))
    return b''.join(parts)


def collect_world(reader,game_index,*,target_native_ids=None):
    found=collect_known_game(reader,game_index)
    if not found['score_conservation_passed']:raise ValueError('rejected Box layout')
    full=found['decoded'];targets={p['player_id'] for side in ('home_players','away_players') for p in full[side] if p['in_use']}
    if target_native_ids is not None:
        if not isinstance(target_native_ids,set) or not 1<=len(target_native_ids)<=8192 or any(type(n) is not int or not 0<=n<=65535 for n in target_native_ids):
            raise ValueError('explicit bounded native player target set required')
        targets.update(target_native_ids)
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'WORLD_ROSTER_POINTER');root=struct.unpack('<Q',pointer)[0]
    specs={1:(8192,1264),8:(1024,4696),24:(65535,48)};descriptors={};decoded_desc={}
    for slot,(maximum,stride) in specs.items():
        raw=reader.read(root+slot*16,16,f'WORLD_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum or not 0x10000<=address<0x00007FFFFFFFFFFF:raise ValueError('invalid bounded directory descriptor')
        descriptors[slot]=raw;decoded_desc[slot]={'count':count,'address':address,'stride':stride}
    teams=[];team_by_pointer={};team_by_id={}
    td=decoded_desc[8]
    for i in range(td['count']):
        address=td['address']+i*TEAM_STRIDE
        ident=reader.read(address+0xCA8,2,f'TEAM:{i}:native-id')
        name=reader.read(address+0x2B4,40,f'TEAM:{i}:name')
        city=reader.read(address+0x2E6,36,f'TEAM:{i}:city')
        t={'pool_index':i,'address':address,'native_team_id':int.from_bytes(ident,'little'),
           'name':_utf(name),'city':_utf(city),'control_hex':{'id':ident.hex(),'name':name.hex(),'city':city.hex()}}
        teams.append(t);team_by_pointer[address]=t;team_by_id.setdefault(t['native_team_id'],[]).append(t)
    for native_id in (full['home_team_id'],full['away_team_id']):
        if len(team_by_id.get(native_id,[]))!=1:raise ValueError('game native team ID is not unique in current TEAM pool')
    pd=decoded_desc[1];sd=decoded_desc[24];hits={native_id:[] for native_id in targets}
    for i in range(pd['count']):
        ident=reader.read(pd['address']+i*PLAYER_STRIDE+0x2F8,2,'WORLD_PLAYER_NATIVE_ID_ONLY')
        native_id=int.from_bytes(ident,'little')
        if native_id in hits:hits[native_id].append(i)
    stats_decoder=_module('season_stats_decoder').SeasonStatsDecoder
    links=[];blobs={};controls=[]
    for native_id,indices in sorted(hits.items()):
        candidates=[]
        for i in indices[:8]:
            address=pd['address']+i*PLAYER_STRIDE;label=f'PLAYER:{i}'
            raw=_public_raw(reader,address,label);idx=int.from_bytes(raw[0xFC:0xFE],'little')
            current_team=struct.unpack_from('<Q',raw,0x60)[0];contract_team=struct.unpack_from('<Q',raw,0xA8)[0]
            try:
                name=(_utf(raw[40:80])+' '+_utf(raw[:40])).strip();name_status='DECODED_UTF16LE'
            except UnicodeDecodeError:
                name=None;name_status='REJECTED_INVALID_UTF16LE'
            c={'pool_index':i,'native_player_id':native_id,'name':name,'name_status':name_status,
               'current_slot24_index':idx,'current_team_pointer':hex(current_team),
               'current_team_id':team_by_pointer[current_team]['native_team_id'] if current_team in team_by_pointer else None,
               'contract_team_id':team_by_pointer[contract_team]['native_team_id'] if contract_team in team_by_pointer else None}
            blobs[f'player-{i}.public.bin']=raw;controls.append((address,raw,label))
            if idx<sd['count'] and idx not in (65535,32756):
                stat=reader.read(sd['address']+idx*48,48,f'PLAYER:{i}:current-slot24')
                totals=stats_decoder.decode_player_stats_record(stat);c['totals']=totals
                blobs[f'player-{i}.slot24.bin']=stat
                controls.append((sd['address']+idx*48,stat,f'PLAYER:{i}:current-slot24-recheck'))
                c['active_context_candidate']=bool(current_team in team_by_pointer and c['name'] and
                    1900<=totals['season_year']<=2100 and totals['scoring_identity_valid'] and
                    totals['games_started']<=totals['games_played'] and
                    all(totals[a]<=totals[b] for a,b in (('fgm','fga'),('tpm','tpa'),('ftm','fta'))))
            else:
                # A player with no current season total can still be present in
                # a game (e.g. a zero-minute roster participant). A single Native
                # ID in this pool plus its valid TEAM pointer is a narrower,
                # explicit mapping basis; no missing cumulative row is invented.
                c['active_context_candidate']=bool(len(indices)==1 and current_team in team_by_pointer and c['name'])
            candidates.append(c)
        eligible=[c for c in candidates if c['active_context_candidate']]
        selected=eligible[0]['pool_index'] if len(eligible)==1 and len(indices)<=8 else None
        basis='UNRESOLVED'
        if selected is not None:
            basis='UNIQUE_TEAM_POINTER_AND_VALID_CURRENT_SLOT24' if 'totals' in eligible[0] else 'UNIQUE_NATIVE_ID_AND_TEAM_POINTER; NO_CURRENT_TOTAL'
        links.append({'native_player_id':native_id,'matched_indices':indices,'candidates':candidates,
                      'selected_pool_index':selected,'mapping_basis':basis})
    # A changed source is an interrupted acquisition, never a mixed observation.
    for address,raw,label in controls:
        actual=_public_raw(reader,address,label+':recheck') if len(raw)==PLAYER_STRIDE else reader.read(address,len(raw),label)
        if actual!=raw:raise ValueError('source record changed during capture: '+label)
    for t in teams:
        for key,offset in (('id',0xCA8),('name',0x2B4),('city',0x2E6)):
            raw=bytes.fromhex(t['control_hex'][key])
            if reader.read(t['address']+offset,len(raw),f'TEAM:{t["pool_index"]}:{key}:recheck')!=raw:raise ValueError('TEAM record changed during capture')
    if reader.read(reader.module_base+ROSTER_RVA,8,'WORLD_ROSTER_RECHECK')!=pointer:raise ValueError('roster root changed during capture')
    for slot,raw in descriptors.items():
        if reader.read(root+slot*16,16,f'WORLD_SLOT{slot}_RECHECK')!=raw:raise ValueError('roster descriptor changed during capture')
    season=int(found['season_pointer'],16);meta=full['boxscore_meta']
    for address,raw,label in ((reader.module_base+SEASON_RVA,struct.pack('<Q',season),'WORLD_SEASON_POINTER_RECHECK'),
        (season,found['header'],'WORLD_HEADER_RECHECK'),
        (season+GAME_OFFSET+game_index*GAME_STRIDE,found['game'],'WORLD_GAME_RECHECK'),
        (season+STATBANK_OFFSET+meta['stat_lines_index']*24,found['box'],'WORLD_BOX_RECHECK')):
        if reader.read(address,len(raw),label)!=raw:raise ValueError('game source changed during capture')
    manifest={'teams':teams,'player_links':links,'descriptors':decoded_desc,
              'excluded_player_bytes':[{'offset':POTENTIAL,'length':1,'status':'NOT_READ; ZERO_PLACEHOLDER_IN_PUBLIC_ARTIFACT'}],
              'identity_scope':'CURRENT_OPERATOR_BOUND_SAVE; NATIVE_ID_CANDIDATE_WITH_COLLISION_REJECTION',
              'ui_field_validation':'NOT_OBSERVED','consistency':'REPEATED_SELECTED_BYTES_AND_DIRECTORY_CONTROLS_EQUAL'}
    return found,manifest,blobs


def world_payload(binding,found,manifest,blobs,artifacts,observed_at,token):
    """Pure transform, initially research-grade. Direct driver supplies live receipt."""
    full=found['decoded'];selected={}
    for link in manifest['player_links']:
        if link['selected_pool_index'] is not None:
            selected[link['native_player_id']]=next(c for c in link['candidates'] if c['pool_index']==link['selected_pool_index'])
    years={c['totals']['season_year'] for c in selected.values() if 'totals' in c}
    if len(years)!=1:raise ValueError('a single current native season year is not established')
    year=next(iter(years));season={'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'}
    tid=lambda n:'team:native:'+str(n)
    pid=lambda n:'player:native:'+str(n)
    gid=season['season_id']+':game:'+str(full['game_id']);facts={}
    team_ids={full['home_team_id'],full['away_team_id']}
    team_ids.update(c['current_team_id'] for c in selected.values())
    team_ids.update(c['contract_team_id'] for c in selected.values() if c['contract_team_id'] is not None)
    teams={}
    for n in team_ids:
        matches=[t for t in manifest['teams'] if t['native_team_id']==n]
        if len(matches)!=1:raise ValueError('selected TEAM native identity collision')
        teams[n]=matches[0]
    facts['teams']=[{'team_id':tid(n),'native_team_id':str(n),'display_name':(t['city']+' '+t['name']).strip(),
                     'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'} for n,t in sorted(teams.items())]
    facts['team_seasons']=[{'team_id':tid(n),'season_id':season['season_id'],'team_name':t['name']} for n,t in sorted(teams.items())]
    facts['players']=[]
    for table in ('player_attribute_snapshots','player_tendency_snapshots','player_vitals_observations',
                  'player_contract_observations','player_play_type_slots','roster_memberships','player_season_totals'):
        facts[table]=[]
    for native_id,c in sorted(selected.items()):
        key=pid(native_id);families=public_player_families(blobs[f'player-{c["pool_index"]}.public.bin'])
        facts['players'].append({'player_id':key,'native_player_id':str(native_id),'display_name':c['name'],'native_identity_status':'UNVERIFIED'})
        for family,table in (('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots'),('vitals','player_vitals_observations')):
            facts[table].append({'player_id':key,**families[family]})
        facts['player_contract_observations'].append({'player_id':key,'team_id':tid(c['contract_team_id']) if c['contract_team_id'] is not None else None,**families['contracts']})
        facts['player_play_type_slots'].extend({'player_id':key,**r} for r in families['play_types'])
        facts['roster_memberships'].append({'player_id':key,'team_id':tid(c['current_team_id']),
                                          'roster_status':'CURRENT_NATIVE_TEAM_POINTER'})
        stats=c.get('totals');mapping={**STAT_MAP,'foul':'fouls','games_played':'games_played','games_started':'games_started',
                                   'double_doubles':'double_doubles','triple_doubles':'triple_doubles'}
        if stats is not None:
            facts['player_season_totals'].append({'player_id':key,'season_id':season['season_id'],'team_id':None,
                'team_scope':'NATIVE_CURRENT_RECORD; TEAM_SPLIT_NOT_ASSERTED','phase_code':None,'is_final':0,
                **{new:stats[old] for old,new in mapping.items() if old in stats}})
    facts['games']=[{'game_id':gid,'season_id':season['season_id'],'native_game_id':str(full['game_id']),
                    'home_team_id':tid(full['home_team_id']),'away_team_id':tid(full['away_team_id']),'game_date':None}]
    facts['game_state_observations']=[{'game_id':gid,'status_code':str(full['status']),'is_final':1,
        'overtime_count':full['overtime_count'],'attendance':full['attendance'],'was_simulated':int(full['was_simulated']),
        'score_provenance':'NATIVE_PERIOD_AND_DERIVED_BOX_CONSERVATION; TOTAL_FIELD_NOT_OBSERVED'}]
    facts['game_period_scores']=[];facts['team_game_boxes']=[];facts['player_game_boxes']=[];facts['native_box_observations']=[]
    for side in ('home','away'):
        n=full[side+'_team_id'];team=tid(n)
        for q in range(1,5):facts['game_period_scores'].append({'game_id':gid,'team_id':team,'period_index':q,'period_points':full['linescore'][side]['q'+str(q)]})
        facts['team_game_boxes'].append({'game_id':gid,'team_id':team,**{new:int(full['boxscore_meta'][side+'_'+old]) for old,new in
            (('fastbreak','fastbreak_points'),('paint','paint_points'),('2nd_chance','second_chance_points'),('pts_off_to','points_off_turnovers'),('lead','largest_lead'),('possessions','possessions_raw'))}})
        for i,p in enumerate(full[side+'_players']):
            stats={new:p[old] for old,new in STAT_MAP.items()}
            facts['native_box_observations'].append({'game_id':gid,'side':side.upper(),'row_index':i,
                'native_player_id':p['player_id'],'native_team_id':n,'in_use':int(p['in_use']),**stats,
                'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM',
                'identity_status':'CURRENT_CONTEXT_RESOLVED' if p['player_id'] in selected and p['in_use'] else 'UNRESOLVED_CANONICAL_PLAYER'})
            if p['in_use'] and p['player_id'] in selected:
                facts['player_game_boxes'].append({'game_id':gid,'player_id':pid(p['player_id']),'team_id':team,**stats,
                    'defensive_fg_made':p['def_fgm'],'defensive_fg_attempted':p['def_fga'],'defensive_points':p['def_pts'],
                    'is_starter':int(p['is_starter']),'in_use':1,'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM'})
    facts['field_gaps']=[{'affected_domain':domain,'target_field':target,'reason':reason,'impact':impact} for domain,target,reason,impact in (
        ('RES-G','SCHEDULE_DATE_UI_ENCODING','Target UI calendar encoding not observed','Canonical game_date is NULL; native bytes retained'),
        ('RES-P','BADGE_TIERS','Encoding/tier correspondence not established','No badge facts invented'),
        ('RES-D','CROSS_SESSION_NATIVE_ID_STABILITY','Unique active context is observed; lifecycle across reload/retirement not yet certified','Identity collisions reject ingestion; no name-based merge'),
        ('RES-L','SEASON_PHASE_AND_TEAM_SPLITS','Current Slot24 observed; phase/team split semantics not separately established','No finalization or split labels inferred'))]
    unresolved=[link['native_player_id'] for link in manifest['player_links'] if link['selected_pool_index'] is None]
    if unresolved:facts['field_gaps'].append({'affected_domain':'RES-P','target_field':'UNRESOLVED_BOX_PLAYER_IDS',
        'reason':json.dumps(unresolved),'impact':'Their native rows retained; canonical Boxes omitted'})
    missing_totals=[n for n,c in selected.items() if 'totals' not in c]
    if missing_totals:facts['field_gaps'].append({'affected_domain':'RES-L','target_field':'UNOBSERVED_CURRENT_PLAYER_TOTALS',
        'reason':json.dumps(missing_totals),'impact':'Players and game Boxes retained; no zero cumulative total substituted'})
    unit='live-world:'+token
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_GAME_PLAYER_WORLD',
            'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':VERSION,
            'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
            'season':season,'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


class _AcquisitionReceipt:
    """Non-serializable acquisition-path capability, not a general signature API."""
    def __init__(self,payload,reader):
        if type(reader) is not ReadOnlyGameProcess or not reader.trace or reader.trace[0].get('success') is not True:
            raise ValueError('receipt requires actual Windows reader')
        self.digest=_digest(payload)
    def matches(self,payload):return self.digest==_digest(payload)


def capture_live(pid,save_directory,loaded_filename,new_output_directory,game_index=0):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False)
    stamp=datetime.now(timezone.utc).isoformat();reader=None
    report={'observed_at':stamp,'pid':pid,'save_id':binding['save_id'],'binding_sha256':binding_hash,
            'native_save_filename':loaded_filename,'game_writes':False,'status':'ACQUISITION_STARTED'}
    try:
        reader=ReadOnlyGameProcess(pid)
        found,manifest,blobs=collect_world(reader,game_index)
        report.update({'module_base':hex(reader.module_base),'module_size':reader.module_size,'read_trace':reader.trace,
                       'status':'BOUNDED_WINDOWS_READS_AND_CONSISTENCY_CONTROLS_PASSED',
                       'source_semantics':'REGISTERED_RESEARCH_CODECS; TARGET_UI_NOT_OBSERVED'})
        reader.close()
        blobs.update({'header.bin':found['header'],'game.bin':found['game'],'box.bin':found['box']})
        for name,data in blobs.items():(out/name).write_bytes(data)
        _json(out/'world-manifest.json',manifest)
        report['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
        _json(out/'acquisition-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,
                    'payload_kind':'ACTUAL_BOUNDED_WINDOWS_READ' if p.suffix=='.bin' else 'ACQUISITION_CONTROL',
                    'source_version':VERSION,'payload_ref':out.name+'/'+p.name,'restricted':1}
                   for p in sorted(out.iterdir()) if p.is_file()]
        for path in (DOMAIN/'config/memory_field_profile.json',DOMAIN/'config/state_io_native/player.json'):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,
                'payload_kind':'REGISTERED_DECODER_LAYOUT','source_version':VERSION,'payload_ref':str(path.relative_to(DOMAIN)),'restricted':1})
        token=hashlib.sha256((out/'acquisition-report.json').read_bytes()).hexdigest()[:24]
        payload=world_payload(binding,found,manifest,blobs,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'save_id':binding['save_id'],'native_save_filename':loaded_filename,'unit_id':payload['unit_id'],
                'source_grade':'LIVE_READ','field_semantics':'REGISTERED_CODECS_NOT_UI_CERTIFICATION',
                'counts':{t:len(rows) for t,rows in payload['facts'].items()},'game_id':payload['facts']['games'][0]['game_id'],
                'game_writes':False,'potential_bytes_read':0}
        _json(out/'ingest-result.json',result);return result
    except (OSError,ValueError,RuntimeError) as error:
        _json(out/'failure.json',{'status':'ACQUISITION_OR_INGEST_FAILED','error_type':type(error).__name__,
            'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False})
        raise
    finally:
        if reader:reader.close()
