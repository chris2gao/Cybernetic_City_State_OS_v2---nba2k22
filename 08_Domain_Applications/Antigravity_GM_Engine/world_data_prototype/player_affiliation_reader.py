"""Read native classification flags and narrow pointed school/catalog sources."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from award_reader import read_native_fields
from cadence import observed_game_season_year
from engine import connect,ingest_capture
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _AcquisitionReceipt,_json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_reader import collect_public_player_pool,reconstruct_projection
from player_affiliation_codec import PROFILE,PROFILE_PATH,LAYOUT,decode_classification,decode_college,reconstruct_college_projection

def affiliation_projection_ranges():
    intervals=[(0,80),(96,104),(120,128),(244,246),(760,764)]
    intervals.extend((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8) for f in PROFILE['player_fields'].values())
    merged=[]
    for low,high in sorted(intervals):
        if any(low<b and a<high for a,b in RESTRICTED_PLAYER_RANGES):raise ValueError('affiliation field intersects private PLAYER bytes')
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    return merged

def verify_affiliation_metadata(reader):
    metadata=[]
    for entry in PROFILE['types']:
        if entry['constructor_rva']==0x1e53e90:
            value=read_native_enum(reader,entry);expected={(int(code),v['name_crc']) for code,v in PROFILE['enum_labels'][entry['name']].items()}
            if {(v['value'],v['name_crc']) for v in value['values']}!=expected or len(value['values'])!=len(expected):raise ValueError('affiliation enum changed')
        else:
            value=read_native_fields(reader,entry,entry['expected_size'],read_enums=False);fields={f['name_crc']:f for f in value['fields']}
            if entry['name']=='PLAYERDATA':
                spans=[]
                for name in ('OriginalPotential','MinPotential','MaxPotential','PreviousPotentialRaw','PotentialRaw'):
                    f=fields[zlib.crc32(name.encode())];spans.append((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8))
                merged=[]
                for low,high in sorted(spans):
                    if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
                    else:merged.append((low,high))
                if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('private PLAYER layout changed')
                names=[('UnlocalizedFirstName',20),('UnlocalizedLastName',20)]
            else:names=[('UnlocalizedName',PROFILE['college_fields']['native_label']['array_extent'])]
            for name,expected_size in names:
                words=fields[zlib.crc32(name.encode())]['words'];pointer=words[6]|words[7]<<32;raw=reader.read(pointer,24,'AFFILIATION_NAME_DIMENSION:'+name)
                if (words[5]>>16)!=1 or int.from_bytes(raw[:4],'little')!=expected_size:raise ValueError('affiliation name extent changed')
                if reader.read(pointer,24,'AFFILIATION_NAME_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('affiliation name dimensions unstable')
        metadata.append(value)
    return metadata

def collect_player_affiliations(reader):
    m,blobs=collect_public_player_pool(reader,ranges=affiliation_projection_ranges(),metadata=verify_affiliation_metadata(reader))
    data=blobs.pop('player-detail-public-projections.bin');blobs['player-affiliation-public-projections.bin']=data;stride=m['projection_stride'];ranges=m['projection_ranges']
    pd=m['descriptors'][1];base=pd['address'];pool_end=base+pd['count']*1264;cache={};college_rows=[];links=[];classifications=[];pointers=[]
    for i,p in enumerate(m['players']):
        raw=reconstruct_projection(data[i*stride:(i+1)*stride],ranges);pointer=int.from_bytes(raw[120:128],'little');pointers.append(pointer);ordinal=None
        if not pointer:status='NO_NATIVE_COLLEGE_POINTER'
        elif pointer<0x10000:status='INVALID_LOW_COLLEGE_POINTER'
        elif base<pointer+60 and pointer<pool_end:status='INVALID_COLLEGE_ALIAS_TO_PLAYER_POOL'
        else:
            if pointer not in cache:
                parts=[reader.read(pointer+low,high-low,'AFFILIATION_COLLEGE_PUBLIC:'+str(low)) for low,high in PROFILE['college_public_ranges']]
                packed=b''.join(parts);ordinal=len(cache);cache[pointer]=(ordinal,packed)
                college_rows.append({'source_object_index':ordinal,**decode_college(reconstruct_college_projection(packed))})
            ordinal=cache[pointer][0];status='NATIVE_COLLEGEDATA_REFERENT_OBSERVED'
        classifications.append({'source_player_index':i,**decode_classification(raw)})
        links.append({'source_player_index':i,'college_source_status':status,'source_object_index':ordinal})
    packed_colleges=[]
    for pointer,(ordinal,packed) in cache.items():
        at=0
        for low,high in PROFILE['college_public_ranges']:
            part=packed[at:at+high-low]
            if reader.read(pointer+low,high-low,'AFFILIATION_COLLEGE_RECHECK:'+str(low))!=part:raise ValueError('college referent changed')
            at+=high-low
        packed_colleges.append((ordinal,packed))
    for i,pointer in enumerate(pointers):
        if reader.read(base+i*1264+120,8,'AFFILIATION_COLLEGE_POINTER_RECHECK')!=pointer.to_bytes(8,'little'):raise ValueError('college pointer association changed')
    root=reader.read(reader.module_base+ROSTER_RVA,8,'AFFILIATION_FINAL_ROOT')
    if reader.read(int.from_bytes(root,'little')+16,16,'AFFILIATION_FINAL_PLAYER_DESCRIPTOR')!=struct.pack('<QQ',pd['count'],pd['address']) or observed_game_season_year(reader)!=m['season_year']:raise ValueError('affiliation root/year changed')
    blobs['college-public-projections.bin']=b''.join(packed for ordinal,packed in sorted(packed_colleges))
    m.update({'classification_rows':classifications,'college_rows':college_rows,'college_links':links,'college_pointer_values_owner_only':pointers,
        'college_object_pointers_owner_only':{str(ordinal):pointer for pointer,(ordinal,packed) in cache.items()},
        'college_projection_ranges':PROFILE['college_public_ranges'],'college_projection_stride':sum(b-a for a,b in PROFILE['college_public_ranges']),
        'source_coverage':'COMPLETE_NATIVE_POOL_CLASSIFICATION_AND_COLLEGE_REFERENTS','college_status_counts':dict(Counter(link['college_source_status'] for link in links))})
    return m,blobs

def affiliation_payload(binding,m,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='player-affiliation:'+token;players=m['players'];count=len(players);year=m['season_year'];descriptor=m['descriptors'].get('1',m['descriptors'].get(1))
    if m.get('game_writes') is not False or m.get('restricted_player_bytes_read')!=0:raise ValueError('affiliation source must be observation/private-free')
    if descriptor['count']!=count or {p['source_player_index'] for p in players}!=set(range(count)):raise ValueError('incomplete affiliation subjects')
    for name in ('classification_rows','college_links'):
        if len(m[name])!=count or {r['source_player_index'] for r in m[name]}!=set(range(count)):raise ValueError('incomplete/duplicate affiliation family')
    colleges={r['source_object_index']:r for r in m['college_rows']}
    if len(colleges)!=len(m['college_rows']) or set(colleges)!=set(range(len(colleges))):raise ValueError('invalid college object ordinals')
    facts={'native_fields':[],'native_player_sources':[],'native_college_observations':[],'market_state_observations':[],'player_vitals_observations':[]};source_ids={};linked_ids={}
    uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    for p in players:
        i=p['source_player_index'];candidate='player:native:'+str(p['preserved_id_raw']);linked=None
        if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(candidate)==p['observed_name']:linked=candidate
        source_ids[i]=f'{unit}:player:{i}';linked_ids[i]=linked
        facts['native_player_sources'].append({'player_source_id':source_ids[i],**p,'player_id':linked,'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for name,f in PROFILE['player_fields'].items():
        facts['native_fields'].append({'field_id':'CURRENT_PLAYER_AFFILIATION_V1:'+str(f['name_crc']),'source_group':'RES-M','native_key':f['native_name'],'table_name':'market_state_observations','column_name':name,
            'evidence_grade':'CURRENT_NATIVE_HEADER_FIELDS_ENUM_CODES_AND_LITERAL_CRCS_VERIFIED','visibility':'GM_PUBLIC','min_native_value':0,'max_native_value':(1<<f['width'])-1,
            'codec':f'unsigned_at{f["offset"]}_bit{f["start_bit"]}_width{f["width"]}','layout_version':LAYOUT,'source_ref':'player_affiliation_native_profile.json; actual capture metadata',
            'unit':'native independent flag/code','legal_range_state':'NATIVE_STORAGE_VERIFIED; SIGNABILITY_NOT_INFERRED'})
    for ordinal,r in sorted(colleges.items()):facts['native_college_observations'].append({'college_observation_id':f'{unit}:college:{ordinal}',**r})
    for original in m['classification_rows']:
        r=dict(original);i=r.pop('source_player_index');facts['market_state_observations'].append({'player_id':linked_ids[i],'source_player_id':source_ids[i],
            'market_status':'NATIVE_CLASSIFICATION_OBSERVED','origin_type':'NATIVE','layout_version':LAYOUT,
            'availability_interpretation':'SIGNABILITY_AND_CURRENT_FREE_AGENT_AVAILABILITY_NOT_ESTABLISHED',**r})
    for link in m['college_links']:
        i=link['source_player_index'];ordinal=link['source_object_index']
        if ordinal is not None and ordinal not in colleges:raise ValueError('college link references absent object')
        if (ordinal is not None)!=(link['college_source_status']=='NATIVE_COLLEGEDATA_REFERENT_OBSERVED'):raise ValueError('college source/link status mismatch')
        facts['player_vitals_observations'].append({'player_id':linked_ids[i],'source_player_id':source_ids[i],'layout_version':LAYOUT,
            'native_college_obs_id':f'{unit}:college:{ordinal}' if ordinal is not None else None,'college_source_status':link['college_source_status'],
            'college_country_semantics_status':'NATIVE_REFERENT_LABEL_OBSERVED; SCHOOL_COUNTRY_CATEGORY_AND_CANONICAL_NATIONALITY_UNVERIFIED'})
    facts['field_gaps']=[dict(affected_domain=d,target_field=t,reason=r,impact=impact) for d,t,r,impact in (
        ('RES-P','NATIVE_COLLEGE_COUNTRY_CATEGORY','COLLEGEDATA label, packed IDs and appearance-group enum are observed; category/nationality mapping not proven','Keep native referent separate from canonical college/country; no geography inferred from appearance group'),
        ('RES-M','NATIVE_FLAGS_VS_SIGNABILITY','Historic/active/hidden/G League/draft/waived/agency flags are independent source properties','Do not label unrostered or unrestricted-coded subjects as currently signable'),
        ('RES-M','G_LEAGUE_ASSIGNMENT_AND_TEAM_LIFECYCLE','Native GLeagueTeam enum and IsDLeague/SendDown flags are observed','Keep flags/code separate; no NBA-team FK or active assignment inferred solely from a nonzero code'),
        ('RES-P','AFFILIATION_SUBJECT_LIFECYCLE','Source IDs and qualified current roster links are not historical lifecycle proof','Preserve source-only subjects without creating canonical retired/generated players'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_PLAYER_AFFILIATION_CLASSIFICATION','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},
        'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}

def capture_player_affiliations(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_player_affiliations(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'affiliation-manifest.json',m)
        report={'status':'COMPLETE_NATIVE_AFFILIATIONS_CAPTURED','pid':pid,'observed_at':stamp,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,'restricted_player_bytes_read':0,
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),PROFILE_PATH,Path(__file__).with_name('player_affiliation_codec.py'),Path(__file__).with_name('player_detail_reader.py'))},
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'affiliation-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'NATIVE_AFFILIATION_OR_CONTROL','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        token=hashlib.sha256((out/'affiliation-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as conn:
            canonical={r['player_id']:r['display_name'] for r in conn.execute('SELECT player_id,display_name FROM players')}
            payload=affiliation_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';receipt=_AcquisitionReceipt(payload,reader)
            status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'source_pid':pid,'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},
            'college_status_counts':m['college_status_counts'],'game_writes':False,'restricted_player_bytes_read':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'AFFILIATION_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
