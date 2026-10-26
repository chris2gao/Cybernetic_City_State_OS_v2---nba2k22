"""Complete native public skill pool with physically excluded Potential bytes."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from award_reader import read_native_fields
from engine import connect,ingest_capture
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess
from live_world import _AcquisitionReceipt,_json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from player_skill_codec import PROFILE,PROFILE_PATH,LAYOUT,decode_skills,play_label

def skill_fields():
    return [(group,name,f) for group in ('attributes','tendencies','play_types') for name,f in PROFILE[group].items()]+[('tendencies','is_play_initiator_raw',PROFILE['initiator'])]

def skill_projection_ranges():
    spans=[(0,80),(96,104),(244,246),(760,764)]+[(f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8) for group,name,f in skill_fields()];merged=[]
    for low,high in sorted(spans):
        if any(low<b and a<high for a,b in RESTRICTED_PLAYER_RANGES):raise ValueError('private skill interval')
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    return merged

def verify_skill_metadata(reader):
    metadata=[];enum_entry=next(e for e in PROFILE['types'] if e['name']=='PLAYERDATA_PLAYTYPE')
    for entry in PROFILE['types']:
        if entry['name']=='PLAYERDATA':
            value=read_native_fields(reader,entry,1264,read_enums=False);fields={f['name_crc']:f for f in value['fields']};private=[]
            for group,name,expected in skill_fields():
                f=fields[expected['name_crc']]
                if any(f[k]!=expected[k] for k in ('offset','size','format','width','start_bit')) or f['words'][1]!=expected['words'][1]:raise ValueError('native skill layout/type changed')
                if group=='play_types' and f['enum_pointer']!=reader.module_base+enum_entry['type_rva']:raise ValueError('native play enum binding changed')
            for name in ('OriginalPotential','MinPotential','MaxPotential','PreviousPotentialRaw','PotentialRaw'):
                f=fields[zlib.crc32(name.encode())];private.append((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8))
            merged=[]
            for low,high in sorted(private):
                if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
                else:merged.append((low,high))
            if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('private skill source layout changed')
            for name in ('UnlocalizedFirstName','UnlocalizedLastName'):
                w=fields[zlib.crc32(name.encode())]['words'];pointer=w[6]|w[7]<<32;raw=reader.read(pointer,24,'SKILL_NAME_DIMENSION:'+name)
                if (w[5]>>16)!=1 or struct.unpack_from('<I',raw)[0]!=20:raise ValueError('skill name extent changed')
                if reader.read(pointer,24,'SKILL_NAME_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('skill name extent unstable')
        else:
            value=read_native_enum(reader,entry);expected={(int(code),v['name_crc']) for code,v in PROFILE['play_type_enum'].items()}
            if {(v['value'],v['name_crc']) for v in value['values']}!=expected or len(value['values'])!=len(expected):raise ValueError('skill play enum changed')
        metadata.append(value)
    return metadata

def collect_player_skills(reader):
    m,blobs=collect_public_player_pool(reader,ranges=skill_projection_ranges(),metadata=verify_skill_metadata(reader));raw=blobs.pop('player-detail-public-projections.bin');blobs['player-skill-public-projections.bin']=raw
    stride=m['projection_stride'];m['skill_rows']=[{'source_player_index':i,**decode_skills(reconstruct_projection(raw[i*stride:(i+1)*stride],m['projection_ranges']))} for i in range(len(m['players']))]
    m['source_coverage']='COMPLETE_CURRENT_NATIVE_56_PUBLIC_ATTRIBUTES_99_TENDENCIES_FOUR_PLAYTYPE_SLOTS_AND_INITIATOR'
    return m,blobs

def skill_payload(binding,m,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='player-skill:'+token;players=m['players'];count=len(players);year=m['season_year'];descriptor=m['descriptors'].get('1',m['descriptors'].get(1))
    if m.get('game_writes') is not False or m.get('restricted_player_bytes_read')!=0:raise ValueError('skill source is not read-only/private-free')
    if descriptor['count']!=count or {p['source_player_index'] for p in players}!=set(range(count)):raise ValueError('incomplete skill subjects')
    if len(m['skill_rows'])!=count or {r['source_player_index'] for r in m['skill_rows']}!=set(range(count)):raise ValueError('incomplete/duplicate skill source family')
    facts={'native_fields':[],'native_player_sources':[],'player_attribute_snapshots':[],'player_tendency_snapshots':[],'player_play_type_slots':[]};source_ids={};linked_ids={}
    uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    for p in players:
        i=p['source_player_index'];candidate='player:native:'+str(p['preserved_id_raw']);linked=None
        if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(candidate)==p['observed_name']:linked=candidate
        source_ids[i]=f'{unit}:player:{i}';linked_ids[i]=linked
        facts['native_player_sources'].append({'player_source_id':source_ids[i],**p,'player_id':linked,'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for group,name,f in skill_fields():
        table={'attributes':'player_attribute_snapshots','tendencies':'player_tendency_snapshots','play_types':'player_play_type_slots'}[group];column='native_play_code' if group=='play_types' else name
        facts['native_fields'].append({'field_id':'CURRENT_PUBLIC_SKILL_V1:'+str(f['name_crc']),'source_group':'RES-P','native_key':f['native_name'],'table_name':table,'column_name':column,
            'evidence_grade':'CURRENT_NATIVE_FIELDS_PRIMITIVE_TYPES_AND_PLAYTYPE_ENUM_VERIFIED','visibility':'GM_PUBLIC','min_native_value':0,'max_native_value':(1<<f['width'])-1,
            'codec':f'unsigned_at{f["offset"]}_bit{f["start_bit"]}_width{f["width"]}','layout_version':LAYOUT,'source_ref':'player_skill_native_profile.json; actual capture metadata','unit':'native unsigned storage','legal_range_state':'NATIVE_STORAGE_ONLY; UI_RATING_AND_BEHAVIOR_NOT_ASSERTED'})
    for row in m['skill_rows']:
        i=row['source_player_index'];subject={'player_id':linked_ids[i],'source_player_id':source_ids[i],'layout_version':LAYOUT}
        for group,table in [('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots')]:
            expected=set(PROFILE[group])|({'is_play_initiator_raw'} if group=='tendencies' else set())
            if set(row[group])!=expected:raise ValueError('incomplete skill columns')
            facts[table].append({**subject,**row[group]})
        if len(row['play_types'])!=4 or {slot['slot_index'] for slot in row['play_types']}!=set(range(4)):raise ValueError('incomplete/duplicate ordered play slots')
        for slot in row['play_types']:
            code=slot['native_play_code']
            if not isinstance(code,str) or not code.isdigit() or str(int(code))!=code or not 0<=int(code)<=15 or slot['native_play_label']!=play_label(int(code)):raise ValueError('invalid native play code/label')
            facts['player_play_type_slots'].append({**subject,**slot})
    facts['field_gaps']=[dict(affected_domain='RES-P',target_field=target,reason=reason,impact=impact) for target,reason,impact in (
        ('CURRENT_OVERALL_RATING','HUMAN_DEFERRED_20261026: overall may be omitted from this task; static cache/getter clues retained outside the active app, not live/UI proof; PreviousOverallAbility is a different source','overall_raw remains unfilled by this source; do not synthesize/recompute or resume deep overall work without later Human scheduling'),
        ('SKILL_UI_UNITS_AND_EFFECTS','Exact bytes, field names and play enum are observed; rating transforms/UI acceptance and behavior remain separate','Do not treat byte storage width or sample maxima as UI legal ranges'),
        ('SKILL_SOURCE_LIFECYCLE','Complete native source pool and qualified current links do not prove historical/cross-session identities','Source-only subjects retain observations without new canonical people'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_PUBLIC_PLAYER_SKILLS','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}

def capture_player_skills(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_player_skills(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'skill-manifest.json',m)
        report={'status':'COMPLETE_NATIVE_PUBLIC_SKILLS_CAPTURED','pid':pid,'observed_at':stamp,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'restricted_player_bytes_read':0,
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),PROFILE_PATH,Path(__file__).with_name('player_skill_codec.py'),Path(__file__).with_name('player_detail_reader.py'))},'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'skill-report.json',report);artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'NATIVE_PUBLIC_SKILL_OR_CONTROL','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        token=hashlib.sha256((out/'skill-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as conn:
            canonical={r['player_id']:r['display_name'] for r in conn.execute('SELECT player_id,display_name FROM players')};payload=skill_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(conn,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'source_pid':pid,'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'game_writes':False,'restricted_player_bytes_read':0,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'SKILL_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
