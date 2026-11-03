"""Read valid overall caches only; never invoke a Native getter/recomputation."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
from award_reader import read_native_fields
from engine import connect,ingest_capture
from game_mode_reader import collect_game_mode,game_mode_payload
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from player_skill_reader import verify_skill_metadata
from overall_codec import PROFILE,PROFILE_PATH,LAYOUT,decode_overall


def verify_overall_metadata(reader):
    metadata=verify_skill_metadata(reader);player=next(v for v in metadata if v['name']=='PLAYERDATA');fields={f['name_crc']:f for f in player['fields']}
    for name in ('cache_field','valid_field'):
        expected=PROFILE[name];actual=fields[expected['name_crc']]
        if actual['words'][1:6]!=expected['words'][1:6]:raise ValueError('Native overall cache primitive/binding changed')
    for proof in PROFILE['code_windows']:
        raw=bytes.fromhex(proof['code_hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'OVERALL_CACHE_GETTER_CODE')!=raw:raise ValueError('Native overall getter/converter code changed')
    for proof in PROFILE['constants']:
        raw=bytes.fromhex(proof['hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'OVERALL_DISPLAY_CONVERTER_CONSTANT')!=raw:raise ValueError('Native display converter constant changed')
    return metadata


def collect_overall(reader):
    mode,mode_blobs=collect_game_mode(reader);m,blobs=collect_public_player_pool(reader,ranges=PROFILE['projection_ranges'],metadata=verify_overall_metadata(reader));stride=m['projection_stride'];raw=blobs.pop('player-detail-public-projections.bin');blobs['overall-public-projections.bin']=raw;blobs.update(mode_blobs)
    m['overall_rows']=[{'source_player_index':index,**decode_overall(reconstruct_projection(raw[index*stride:(index+1)*stride],m['projection_ranges']))} for index in range(len(m['players']))];after,_=collect_game_mode(reader)
    if m['season_year']!=mode['season_year'] or after['observation']!=mode['observation'] or after['season_year']!=mode['season_year']:raise ValueError('Native game progress changed during overall cache acquisition')
    m.update(game_mode=mode,source_coverage='COMPLETE_PUBLIC_PLAYER_OVERALL_CACHE_AND_VALIDITY; NO_RECOMPUTATION',getter_invocations=0,limits=PROFILE['limits']);return m,blobs


def overall_payload(binding,m,artifacts,stamp,token,canonical):
    players=m['players'];count=len(players);descriptor=m['descriptors'].get('1',m['descriptors'].get(1))
    if m.get('game_writes') is not False or m.get('restricted_player_bytes_read')!=0 or descriptor['count']!=count or {p['source_player_index'] for p in players}!=set(range(count)):raise ValueError('complete private-free overall source directory required')
    if len(m['overall_rows'])!=count or {r['source_player_index'] for r in m['overall_rows']}!=set(range(count)):raise ValueError('complete distinct overall cache family required')
    unit='native-overall:'+token;year=m['season_year'];uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER');sources={};linked={};facts={'native_player_sources':[],'native_player_overall_observations':[]}
    expected=set(decode_overall(bytes(1264)))|{'source_player_index'}
    for p in players:
        index=p['source_player_index'];key='player:native:'+str(p['preserved_id_raw']);accepted=p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(key)==p['observed_name'];sources[index]=f'{unit}:player:{index}';linked[index]=key if accepted else None;facts['native_player_sources'].append({'player_source_id':sources[index],**p,'player_id':linked[index],'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if accepted else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for original in m['overall_rows']:
        if set(original)!=expected:raise ValueError('overall cache row contains missing/unregistered fields')
        row=dict(original);index=row.pop('source_player_index');facts['native_player_overall_observations'].append({'source_player_id':sources[index],'player_id':linked[index],**row})
    facts['game_mode_observations']=game_mode_payload(binding,m['game_mode'],[],stamp,token)['facts']['game_mode_observations'];facts['field_gaps']=[{'affected_domain':'RES-P','target_field':name,'reason':reason,'impact':impact} for name,reason,impact in (
        ('OVERALL_INVALID_CACHE_READ_ONLY_LIMIT','Native getter recomputes when CachedOverallValid is0; this reader never invokes it','Invalid caches remain unavailable rather than becoming previous/cached scores'),
        ('OVERALL_DISPLAY_ROUNDING_AND_UI','Integer helper uses CVTSS2SI and optional float32 multiplication; actual game-thread MXCSR and UI display were not observed','Nearest-even is an explicit candidate; only exact integral input/product yields a rounding-independent Native result; legacy overall_raw stays unchanged'),
        ('OVERALL_SOURCE_LIFECYCLE','Current public source identity/roster links do not prove historical or cross-session person lifecycles','Unmatched sources retain independent observations without invented canonical players'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_PLAYER_OVERALL_CACHE','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':'season:native-year:'+str(year),'season_code':'NATIVE_YEAR:'+str(year)},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_overall(pid,save_directory,loaded_filename,new_output_directory):
    binding,bhash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_overall(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'overall-manifest.json',m);_json(out/'overall-report.json',{'status':'PUBLIC_NATIVE_OVERALL_CACHE_VALIDITY_AND_CODE_CAPTURED','pid':reader.pid,'observed_at':stamp,'binding_sha256':bhash,'read_trace':reader.trace,'getter_invocations':0,'game_writes':False,'restricted_player_bytes_read':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_PUBLIC_OVERALL_CACHE_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('player_skill_native_profile.json')):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_OVERALL_METADATA_AND_CODE','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'overall-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as conn:
            canonical={r['player_id']:r['display_name'] for r in conn.execute('SELECT player_id,display_name FROM players')};payload=overall_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(conn,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'game_writes':False,'getter_invocations':0};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
