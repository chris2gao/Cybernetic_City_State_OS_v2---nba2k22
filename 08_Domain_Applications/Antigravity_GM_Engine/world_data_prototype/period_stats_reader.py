"""Current Native selector -> complete public player pool -> referenced stat rows."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from award_reader import PROFILE_PATH as STAT_PROFILE_PATH,AWARD_COLUMNS,decode_stat_record,read_native_fields
from game_mode_reader import collect_game_mode,PROFILE_PATH as MODE_PROFILE_PATH
from stat_reference import verify_native_reference_contract,PROFILE_PATH as REFERENCE_PROFILE_PATH
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import RESTRICTED_PLAYER_RANGES,read_binding,bound_database,_json,_AcquisitionReceipt
from engine import connect,ingest_acquired_capture as ingest_capture
from schema_model import NATIVE_PLAYER_STAT_MAP

STAT_PROFILE=json.loads(STAT_PROFILE_PATH.read_bytes());LAYOUT='CURRENT_NATIVE_SELECTED_PERIOD_PLAYER_STATS_V1'

def period_projection_ranges(position):
    if type(position) is not int or position not in (0,24):raise ValueError('verified current stat array position must be0 or24')
    start=STAT_PROFILE['player_fields']['SeasonStats']['offset']+position*2
    return sorted(((0,80),(96,104),(244,246),(760,764),(start,start+2)))

def ordinary_stat_record(raw):
    return {key:value for key,value in decode_stat_record(raw,STAT_PROFILE['stat_fields']).items() if key not in AWARD_COLUMNS}

def verify_period_stat_metadata(reader):
    contract=verify_native_reference_contract(reader);metadata=[]
    for name,size in (('PLAYERDATA',1264),('PLAYERSTATDATA',48)):
        entry=next(t for t in STAT_PROFILE['types'] if t['name']==name);value=read_native_fields(reader,entry,size,read_enums=False);actual={f['name_crc']:f for f in value['fields']}
        expected=STAT_PROFILE['player_fields' if name=='PLAYERDATA' else 'stat_fields']
        for field in expected.values():
            found=actual[field['name_crc']]
            if any(found[k]!=field[k] for k in ('offset','size','format','width','start_bit')):raise ValueError('Native selected-period stat field changed')
        if name=='PLAYERDATA':
            for field_name in ('UnlocalizedFirstName','UnlocalizedLastName'):
                field=actual[zlib.crc32(field_name.encode())];w=field['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'PERIOD_STAT_NAME_DIMENSION:'+field_name)
                if w[5]>>16!=1 or struct.unpack_from('<I',raw)[0]!=20:raise ValueError('Native stat subject name extent changed')
                if reader.read(ptr,24,'PERIOD_STAT_NAME_DIMENSION_RECHECK:'+field_name)!=raw:raise ValueError('Native stat subject name extent unstable')
        metadata.append(value)
    return {'reference_contract':contract,'metadata':metadata}

def collect_period_stats(reader):
    mode,mode_blobs=collect_game_mode(reader)
    if mode['observation']['mode_label']!='FRANCHISE':raise ValueError('operator-bound MyLEAGUE stat source requires Native FRANCHISE mode')
    position=mode['observation']['current_stat_array_position'];verified=verify_period_stat_metadata(reader);ranges=period_projection_ranges(position)
    manifest,blobs=collect_public_player_pool(reader,ranges=ranges,metadata=verified['metadata']);raw=blobs.pop('player-detail-public-projections.bin');blobs.update(mode_blobs);blobs['selected-period-public-projections.bin']=raw
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'PERIOD_STAT_ROSTER_POINTER');root=int.from_bytes(pointer,'little');descriptor=reader.read(root+24*16,16,'PERIOD_STAT_SLOT24_DESCRIPTOR');count,address=struct.unpack('<QQ',descriptor)
    if not 1<=count<=65535 or address<0x10000:raise ValueError('selected-period stat bank outside bounded envelope')
    stride=manifest['projection_stride'];start=STAT_PROFILE['player_fields']['SeasonStats']['offset']+position*2;links=[];records={};native_rows={}
    for player in manifest['players']:
        index=player['source_player_index'];projection=reconstruct_projection(raw[index*stride:(index+1)*stride],ranges);stat_index=int.from_bytes(projection[start:start+2],'little')
        status='NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER' if stat_index>=32768 else 'OUTSIDE_CURRENT_NATIVE_STAT_COUNT' if stat_index>=count else 'CURRENT_PERIOD_NATIVE_GETTER_INDEX_CANDIDATE'
        links.append({'source_player_index':index,'history_slot_index':position,'native_stat_index_raw':stat_index,'link_status':status})
        if status=='CURRENT_PERIOD_NATIVE_GETTER_INDEX_CANDIDATE' and stat_index not in records:
            row=reader.read(address+stat_index*48,48,f'PERIOD_STAT_RECORD:{stat_index}');native_rows[stat_index]=row;records[stat_index]={'source_stat_index':stat_index,**ordinary_stat_record(row)};blobs[f'stat-{stat_index}.bin']=row
    for index,row in native_rows.items():
        if reader.read(address+index*48,48,f'PERIOD_STAT_RECORD_RECHECK:{index}')!=row:raise ValueError('selected-period stat record changed')
    pd=manifest['descriptors'][1]
    for player in manifest['players']:
        index=player['source_player_index'];projection=reconstruct_projection(raw[index*stride:(index+1)*stride],ranges)
        for low,high in ranges:
            if reader.read(pd['address']+index*1264+low,high-low,f'PERIOD_STAT_SUBJECT_RECHECK:{index}:{low}')!=projection[low:high]:raise ValueError('selected-period stat subject changed')
    for team_address,team in manifest['core_team_pointer_map'].items():
        if reader.read(team_address,200,'PERIOD_STAT_ROSTER_RECHECK')!=blobs[f'team-{team}.roster.bin'] or int.from_bytes(reader.read(team_address+0xCA8,2,'PERIOD_STAT_TEAM_ID_RECHECK'),'little')!=team:raise ValueError('selected-period roster changed')
    for slot in (1,8):
        old=manifest['descriptors'][slot]
        if reader.read(root+slot*16,16,'PERIOD_STAT_PUBLIC_DIRECTORY_RECHECK')!=struct.pack('<QQ',old['count'],old['address']):raise ValueError('selected-period player/team directory changed')
    if reader.read(root+24*16,16,'PERIOD_STAT_BANK_RECHECK')!=descriptor or reader.read(reader.module_base+ROSTER_RVA,8,'PERIOD_STAT_ROOT_RECHECK')!=pointer:raise ValueError('selected-period stat directory changed')
    after,after_blobs=collect_game_mode(reader)
    if after['observation']!=mode['observation'] or after_blobs!=mode_blobs or manifest['season_year']!=mode['season_year'] or after['season_year']!=mode['season_year']:raise ValueError('Native mode/date/selector/year changed during selected-period acquisition')
    manifest.update({'game_mode':mode,'stat_metadata':verified,'stat_bank_descriptor':{'count':count,'address':address,'stride':48},'selected_array_position':position,'stat_links':links,'stat_records':list(records.values()),
                     'annual_award_columns_withheld':list(AWARD_COLUMNS),'source_coverage':'COMPLETE_NATIVE_PUBLIC_PLAYER_POOL_ONE_SELECTED_PERIOD_REFERENCE_PER_SOURCE; ALLOCATION_AND_LIFECYCLE_NOT_ASSERTED','getter_invocations':0,'annual_history_refreshed':False})
    return manifest,blobs

def period_stats_payload(binding,m,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='native-period-stats:'+token;players=m['players'];position=m['selected_array_position'];year=m['season_year'];descriptor=m['descriptors'].get(1,m['descriptors'].get('1'));bank=m['stat_bank_descriptor'];stats=m['stat_records'];links=m['stat_links']
    if position not in (0,24) or m['game_mode']['observation']['current_stat_array_position']!=position or m['game_mode']['season_year']!=year:raise ValueError('stat selection differs from its Native mode context')
    if m['restricted_player_bytes_read']!=0 or m['game_writes'] is not False or {p['source_player_index'] for p in players}!=set(range(descriptor['count'])):raise ValueError('incomplete/private selected-period source')
    if len(links)!=len(players) or {r['source_player_index'] for r in links}!={p['source_player_index'] for p in players} or any(r['history_slot_index']!=position for r in links):raise ValueError('incomplete/duplicate selected-period references')
    for link in links:
        index=link['native_stat_index_raw'];expected='NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER' if index>=32768 else 'OUTSIDE_CURRENT_NATIVE_STAT_COUNT' if index>=bank['count'] else 'CURRENT_PERIOD_NATIVE_GETTER_INDEX_CANDIDATE'
        if type(index) is not int or not 0<=index<=65535 or link['link_status']!=expected:raise ValueError('invalid Native current-period reference')
    wanted={r['native_stat_index_raw'] for r in links if r['link_status']=='CURRENT_PERIOD_NATIVE_GETTER_INDEX_CANDIDATE'}
    if len({s['source_stat_index'] for s in stats})!=len(stats) or {s['source_stat_index'] for s in stats}!=wanted:raise ValueError('selected-period record coverage mismatch')
    facts={'native_player_sources':[],'native_player_stat_links':[],'native_player_stat_observations':[],'game_mode_observations':[{'season_id':f'season:native-year:{year}',**m['game_mode']['observation']}]};ids={p['source_player_index']:f'{unit}:player:{p["source_player_index"]}' for p in players};stat_ids={i:f'{unit}:stat:{i}' for i in wanted}
    uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    for player in players:
        candidate='player:native:'+str(player['preserved_id_raw']);linked=candidate if player['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[player['native_unique_id_raw']]==1 and preserved[player['preserved_id_raw']]==1 and player['preserved_id_raw']<=65535 and canonical.get(candidate)==player['observed_name'] else None
        facts['native_player_sources'].append({'player_source_id':ids[player['source_player_index']],**player,'player_id':linked,'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for stat in stats:
        if any(key in stat for key in AWARD_COLUMNS):raise ValueError('ordinary period source must withhold annual award columns')
        if set(stat)!=({'source_stat_index','stat_year','scoring_identity_status'}|set(NATIVE_PLAYER_STAT_MAP.values())-set(AWARD_COLUMNS)):raise ValueError('incomplete ordinary stat columns')
        if stat['stat_year']!=1900+stat['compact_year_raw'] or stat['scoring_identity_status']!=('CONSISTENT' if stat['points_raw']==2*stat['fg_made_raw']+stat['three_made_raw']+stat['ft_made_raw'] else 'INCONSISTENT_SOURCE_WORDS_RETAINED'):raise ValueError('selected-period stat codec annotations differ')
        facts['native_player_stat_observations'].append({'stat_observation_id':stat_ids[stat['source_stat_index']],**stat})
    for link in links:facts['native_player_stat_links'].append({'player_source_id':ids[link['source_player_index']],'history_slot_index':position,'native_stat_index_raw':link['native_stat_index_raw'],'link_status':link['link_status'],'stat_observation_id':stat_ids.get(link['native_stat_index_raw'])})
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_CURRENT_PERIOD_PLAYER_STATS','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}

def capture_period_stats(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_period_stats(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'period-stats-manifest.json',m);_json(out/'period-stats-report.json',{'status':'COMPLETE_NATIVE_SELECTED_PERIOD_PUBLIC_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'getter_invocations':0,'restricted_player_bytes_read':0,'annual_history_refreshed':False})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'NATIVE_SELECTED_PERIOD_PACKED_SOURCE; ANNUAL_AWARD_BITS_NOT_IMPORTED','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (STAT_PROFILE_PATH,MODE_PROFILE_PATH,REFERENCE_PROFILE_PATH):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_NATIVE_REFERENCE_STAT_AND_MODE_CONTRACT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'period-stats-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as c:
            canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')};payload=period_stats_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(c,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'selected_array_position':m['selected_array_position'],'period_label':m['game_mode']['observation']['period_label'],'game_writes':False,'annual_history_refreshed':False,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'SELECTED_PERIOD_CAPTURE_OR_INGEST_FAILED','reason':str(error),'error_type':type(error).__name__,'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
