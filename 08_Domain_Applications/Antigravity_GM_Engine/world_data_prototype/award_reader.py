"""Verify native season-stat award metadata before interpreting any award bit."""
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json,RESTRICTED_PLAYER_RANGES,_public_raw,read_binding,bound_database,_AcquisitionReceipt
from engine import connect,ingest_capture
from schedule_reader import bounded_block
from family_codec import decode_fixed_utf16
from collections import Counter
from schema_model import NATIVE_PLAYER_STAT_MAP

PROFILE_PATH=Path(__file__).with_name('award_native_profile.json')
STAT_COLUMNS=NATIVE_PLAYER_STAT_MAP
AWARD_COLUMNS=tuple(STAT_COLUMNS[n] for n in ('MVP','Champion','FinalsMVP','AllNBATeamRank','AllDefensiveTeamRank','AllRookieTeamRank','AllStarStarter','AllStarReserve','RookieOfTheYear','SixthManOfTheYear','DefensivePlayerOfTheYear','MostImprovedPlayer'))


def decode_stat_record(raw,bindings):
    if len(raw)!=48:raise ValueError('native PLAYERSTATDATA must be 48 bytes')
    values={}
    for name,column in STAT_COLUMNS.items():
        f=bindings[name];width=f['width'];shift=f['start_bit'];size=f['size'];offset=f['offset']
        if not 1<=width<=64 or shift+width>size*8 or offset+size>48:raise ValueError('native stat field outside row')
        values[column]=(int.from_bytes(raw[offset:offset+size],'little')>>shift)&((1<<width)-1)
    values['stat_year']=1900+values['compact_year_raw']
    values['scoring_identity_status']='CONSISTENT' if values['points_raw']==2*values['fg_made_raw']+values['three_made_raw']+values['ft_made_raw'] else 'INCONSISTENT_SOURCE_WORDS_RETAINED'
    return values


def classify_stat_link(index,slot,count,after_sentinel=False):
    if index==65535:return 'SENTINEL_NO_ACCEPTED_LINK'
    if index>=count:return 'OUTSIDE_NATIVE_STAT_COUNT'
    if slot>0 and index==0:return 'ZERO_HISTORY_SLOT_UNVERIFIED'
    if after_sentinel:return 'HISTORY_INDEX_AFTER_EMPTY_SLOT'
    return 'CURRENT_INDEX_CANDIDATE' if slot==0 else 'HISTORY_INDEX_CANDIDATE'


def read_native_fields(reader,entry,expected_size=None,*,read_enums=True):
    code=bytes.fromhex(entry['initializer_hex'])
    actual=reader.read(reader.module_base+entry['initializer_rva'],len(code),'AWARD_TYPE_INITIALIZER:'+entry['name'])
    if actual!=code:raise ValueError('native type initializer changed')
    if entry['constructor_rva']!=0x1e53f30:raise ValueError('candidate is not the verified native fields constructor')
    header=reader.read(reader.module_base+entry['type_rva'],64,'AWARD_TYPE_HEADER:'+entry['name']);h=struct.unpack('<8Q',header)
    if not 0<h[0]<=2000:raise ValueError('native field count outside bounded metadata envelope')
    name=reader.read(h[5],len(entry['name'])+1,'AWARD_TYPE_NAME:'+entry['name'])
    if name!=entry['name'].encode()+b'\0':raise ValueError('current native type name mismatch')
    schema=reader.read(h[4],40,'AWARD_TYPE_SCHEMA:'+entry['name']);size=struct.unpack('<10I',schema)[5]
    if expected_size is not None and size!=expected_size:raise ValueError('current native type size mismatch')
    raw=bounded_block(reader,h[1],h[0]*40,'AWARD_TYPE_FIELDS:'+entry['name']);fields=[];enums={}
    kinds=json.loads(PROFILE_PATH.read_bytes()).get('referenced_type_kinds',{})
    for i in range(h[0]):
        w=struct.unpack_from('<10I',raw,i*40);enum=w[8]|w[9]<<32
        field={'name_crc':w[0],'offset':w[2],'size':w[3],'format':w[4],'width':(w[4]>>8)&255,
            'start_bit':(w[4]>>16)&255,'enum_pointer':enum,'words':list(w)}
        if entry['name']=='PLAYERDATA' and w[0]==zlib.crc32(b'SeasonStats'):
            dim=w[6]|w[7]<<32;field['array_dimension_control_hex']=reader.read(dim,8,'AWARD_NATIVE_SEASON_STATS_ARRAY_DIMENSION').hex()
        fields.append(field)
        if enum and str(enum) not in enums:
            if not read_enums:
                enums[str(enum)]={'status':'REFERENCED_TYPE_NOT_ACQUIRED_FIELD_METADATA_ONLY','values':[]};continue
            kind=kinds.get(str(enum-reader.module_base))
            if not kind or kind['constructor_rva']!=0x1e53e90:
                enums[str(enum)]={'status':'NESTED_OR_UNRESOLVED_NATIVE_TYPE_NOT_ENUM','candidate_type_name':kind['name'] if kind else None,'values':[]};continue
            init=bytes.fromhex(kind['initializer_hex'])
            if reader.read(reader.module_base+kind['initializer_rva'],len(init),'AWARD_ENUM_INITIALIZER:'+kind['name'])!=init:raise ValueError('referenced enum initializer changed')
            eraw=reader.read(enum,48,'AWARD_ENUM_HEADER:'+entry['name']);eh=struct.unpack('<6Q',eraw)
            if not 0<eh[2]<=300:raise ValueError('verified native enum count outside bounded envelope')
            values=bounded_block(reader,eh[3],eh[2]*12,'AWARD_ENUM_VALUES:'+entry['name'])
            enums[str(enum)]={'status':'NATIVE_ENUM_CONSTRUCTOR_AND_TABLE_VERIFIED','candidate_type_name':kind['name'],
                'header_hex':eraw.hex(),'values':[{'name_crc':c,'value':v,'aux':a} for c,v,a in struct.iter_unpack('<IiI',values)]}
            if reader.read(enum,48,'AWARD_ENUM_HEADER_RECHECK:'+entry['name'])!=eraw or bounded_block(reader,eh[3],eh[2]*12,'AWARD_ENUM_VALUES_RECHECK:'+entry['name'])!=values:raise ValueError('native enum changed during metadata verification')
    for address,data,label in ((reader.module_base+entry['type_rva'],header,'HEADER'),(h[5],name,'NAME'),(h[4],schema,'SCHEMA'),(h[1],raw,'FIELDS')):
        if bounded_block(reader,address,len(data),'AWARD_TYPE_RECHECK:'+entry['name']+':'+label)!=data:raise ValueError('native metadata changed')
    signature=sorted((f['name_crc'],f['offset'],f['size'],f['format'],f['words'][5]) for f in fields)
    if entry.get('expected_field_count') is not None and (entry['expected_field_count']!=len(fields) or entry['field_signature_sha256']!=hashlib.sha256(json.dumps(signature,separators=(',',':')).encode()).hexdigest()):raise ValueError('native field signature changed')
    return {'name':entry['name'],'type_rva':entry['type_rva'],'field_count':h[0],'struct_size':size,'fields':fields,
        'enums':enums,'header_hex':header.hex(),'schema_hex':schema.hex(),'field_array_hex':raw.hex(),
        'status':'CURRENT_NATIVE_NAME_SCHEMA_FIELDS_AND_INITIALIZER_VERIFIED'}


def probe_award_metadata(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False,'player_struct_reads':0}
    try:
        profile=json.loads(PROFILE_PATH.read_bytes());reader=ReadOnlyGameProcess(pid);metadata=[]
        sizes={'PLAYERSTATDATA':48,'TEAMSTATDATA':62,'PLAYERDATA':1264}
        for entry in profile['types']:
            if entry['name'] not in sizes:continue
            metadata.append(read_native_fields(reader,entry,sizes[entry['name']],read_enums=False))
        reader.close();_json(out/'award-native-metadata.json',metadata)
        report.update({'status':'AWARD_NATIVE_METADATA_CAPTURED','read_trace':reader.trace,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'AWARD_NATIVE_METADATA_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'award-metadata-report.json',report);return report


def collect_native_honors(reader):
    profile=json.loads(PROFILE_PATH.read_bytes());metadata=[]
    for entry in profile['types']:
        metadata.append(read_native_fields(reader,entry,{'PLAYERDATA':1264,'PLAYERSTATDATA':48,'TEAMSTATDATA':62}[entry['name']],read_enums=False))
    for group,key in (('PLAYERSTATDATA','stat_fields'),('PLAYERDATA','player_fields')):
        fields={f['name_crc']:f for t in metadata if t['name']==group for f in t['fields']}
        for name,expected in profile[key].items():
            actual=fields.get(zlib.crc32(name.encode()))
            if actual is None or any(actual[k]!=expected[k] for k in ('offset','size','width','start_bit','format')):raise ValueError('current native field layout changed: '+name)
    pmeta=next(t for t in metadata if t['name']=='PLAYERDATA')
    field_by_crc={f['name_crc']:f for f in pmeta['fields']};spans=[]
    for name in ('OriginalPotential','MinPotential','MaxPotential','PreviousPotentialRaw','PotentialRaw'):
        f=field_by_crc[zlib.crc32(name.encode())];spans.append((f['offset']+f['start_bit']//8,f['offset']+(f['start_bit']+f['width']+7)//8))
    merged=[]
    for low,high in sorted(spans):
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('current restricted PLAYER storage does not match physical exclusion ranges')
    dim=next(f['array_dimension_control_hex'] for f in pmeta['fields'] if f['name_crc']==zlib.crc32(b'SeasonStats'))
    history_count=int.from_bytes(bytes.fromhex(dim)[:4],'little')
    if dim!=profile['season_stats_array_dimension_control_hex'] or not 1<=history_count<=64:raise ValueError('native stat reference array dimension changed')
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'HONORS_ROSTER_POINTER');root=int.from_bytes(pointer,'little');descriptors={};tables={};controls=[];blobs={}
    for slot,maximum,stride in ((1,8192,1264),(8,1024,4696),(24,65535,48),(28,10000,62)):
        raw=reader.read(root+slot*16,16,f'HONORS_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum or address<0x10000:raise ValueError('native honors descriptor outside bounded envelope')
        descriptors[slot]=raw;tables[slot]={'count':count,'address':address,'stride':stride}
    teams={};core=set(range(30))-{7};core.add(31);assigned={};season=None
    for i in range(tables[8]['count']):
        address=tables[8]['address']+i*4696;ident=reader.read(address+0xCA8,2,'HONORS_TEAM_ID');tid=int.from_bytes(ident,'little')
        if tid not in core:continue
        teams[address]=tid;roster=reader.read(address,200,'HONORS_CURRENT_TEAM_ROSTER');blobs[f'team-{tid}.roster.bin']=roster
        controls.extend(((address+0xCA8,ident,'HONORS_TEAM_ID_RECHECK'),(address,roster,'HONORS_TEAM_ROSTER_RECHECK')))
        for pos,p in enumerate(struct.unpack('<25Q',roster)):
            if not p:continue
            index,rem=divmod(p-tables[1]['address'],1264)
            if rem or not 0<=index<tables[1]['count']:raise ValueError('current roster player pointer outside native pool')
            if index in assigned:raise ValueError('native source player assigned to multiple current roster positions')
            assigned[index]=(tid,pos)
        if tid==0:
            idxraw=reader.read(address+0xE80,2,'HONORS_TEAM_STATS_INDEX');idx=int.from_bytes(idxraw,'little')
            if idx>=tables[28]['count']:raise ValueError('observation season stats index invalid')
            target=tables[28]['address']+idx*62;season=reader.read(target,62,'HONORS_OBSERVATION_SEASON')
            controls.extend(((address+0xE80,idxraw,'HONORS_SEASON_INDEX_RECHECK'),(target,season,'HONORS_OBSERVATION_SEASON_RECHECK')))
    if set(teams.values())!=core or season is None:raise ValueError('complete current core-team context absent')
    blobs['season-control.bin']=season
    stat_parts=[]
    for start in range(0,tables[24]['count'],1000):stat_parts.append(bounded_block(reader,tables[24]['address']+start*48,min(1000,tables[24]['count']-start)*48,f'HONORS_STAT_TABLE:{start}'))
    statraw=b''.join(stat_parts);blobs['player-stat-bank.bin']=statraw
    statrows=[dict(source_stat_index=i,**decode_stat_record(statraw[i*48:(i+1)*48],profile['stat_fields'])) for i in range(tables[24]['count'])]
    projections=[];players=[];links=[];pfields=profile['player_fields'];stats_offset=pfields['SeasonStats']['offset']
    for i in range(tables[1]['count']):
        address=tables[1]['address']+i*1264;pieces=[]
        for offset,size,label in ((0,80,'NAME'),(244,2,'UNIQUE_ID'),(760,4,'PRESERVED_ID'),(96,8,'TEAM'),(stats_offset,history_count*2,'STAT_INDICES')):
            raw=reader.read(address+offset,size,'HONORS_PLAYER_PUBLIC:'+label);pieces.append(raw);controls.append((address+offset,raw,'HONORS_PLAYER_PUBLIC_RECHECK:'+label))
        names,uid,preserved,owner,indices=pieces;projections.append(b''.join(pieces))
        try:display=(decode_fixed_utf16(names[40:80])+' '+decode_fixed_utf16(names[:40])).strip() or None;name_status='OBSERVED_UTF16_PREFIX' if display else 'NO_PUBLIC_NAME'
        except UnicodeDecodeError:display=None;name_status='INVALID_UTF16_PREFIX'
        team=teams.get(int.from_bytes(owner,'little'));current=assigned.get(i)
        if current is not None and (team!=current[0] or not display):raise ValueError('current source roster owner/name failed reciprocal check')
        players.append({'source_player_index':i,'native_unique_id_raw':int.from_bytes(uid,'little'),
            'preserved_id_raw':int.from_bytes(preserved,'little'),'observed_name':display,'name_status':name_status,
            'native_team_id':team,'current_core_roster_status':'CURRENT_CORE_ROSTER' if current else 'NOT_CURRENT_CORE_ROSTER',
            'current_roster_slot':current[1] if current else None})
        after=False
        for slot,index in enumerate(struct.unpack('<'+'H'*history_count,indices)):
            status=classify_stat_link(index,slot,tables[24]['count'],after)
            links.append({'source_player_index':i,'history_slot_index':slot,'native_stat_index_raw':index,'link_status':status})
            if slot>0 and status in ('SENTINEL_NO_ACCEPTED_LINK','ZERO_HISTORY_SLOT_UNVERIFIED'):after=True
    blobs['player-public-projection.bin']=b''.join(projections)
    sample_index=min(assigned);sample=_public_raw(reader,tables[1]['address']+sample_index*1264,'HONORS_PUBLIC_FAMILY_PRIVACY_PROBE')
    blobs['public-family-privacy-probe.bin']=sample
    for start in range(0,tables[24]['count'],1000):
        off=start*48;size=min(1000,tables[24]['count']-start)*48
        if bounded_block(reader,tables[24]['address']+off,size,f'HONORS_STAT_TABLE_RECHECK:{start}')!=statraw[off:off+size]:raise ValueError('native stat bank changed during acquisition')
    for address,raw,label in controls:
        if bounded_block(reader,address,len(raw),label)!=raw:raise ValueError('native honors subject or context changed')
    if reader.read(reader.module_base+ROSTER_RVA,8,'HONORS_ROOT_RECHECK')!=pointer:raise ValueError('native honors root changed')
    for slot,raw in descriptors.items():
        if reader.read(root+slot*16,16,f'HONORS_SLOT{slot}_RECHECK')!=raw:raise ValueError('native honors directory changed')
    return {'season_year':1900+season[4],'descriptors':tables,'metadata':metadata,'players':players,'stat_records':statrows,'stat_links':links,
        'season_stats_array_count':history_count,'source_coverage':'COMPLETE_NATIVE_PLAYER_POOL_AND_STAT_BANK',
        'current_core_roster_count':len(assigned),'link_status_counts':dict(Counter(r['link_status'] for r in links)),
        'privacy_probe_source_player_index':sample_index,'excluded_player_byte_ranges':list(RESTRICTED_PLAYER_RANGES),
        'game_writes':False,'full_player_struct_reads':0,'restricted_player_bytes_read':0,
        'identity_status':'UNIQUE_ID_AND_PRESERVED_ID_DISTINCT; CANONICAL_LIFECYCLE_NOT_INFERRED'},blobs


def probe_native_honors(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_native_honors(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'honors-manifest.json',manifest)
        report.update({'status':'NATIVE_HONORS_SOURCE_CAPTURED','read_trace':reader.trace,
            'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'NATIVE_HONORS_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'honors-report.json',report);return report


def honors_payload(binding,manifest,artifacts,observed_at,token,canonical_legacy_map=None):
    unit='native-honors:'+token;canonical_legacy_map=canonical_legacy_map or {};year=manifest['season_year']
    if manifest.get('game_writes') is not False or manifest.get('restricted_player_bytes_read')!=0:raise ValueError('honor source must be read only and exclude restricted PLAYER bytes')
    tables=manifest['descriptors'];tables={int(k):v for k,v in tables.items()};players=manifest['players'];stats=manifest['stat_records'];links=manifest['stat_links']
    pi=[p['source_player_index'] for p in players];si=[s['source_stat_index'] for s in stats]
    if len(pi)!=len(set(pi)) or len(si)!=len(set(si)):raise ValueError('duplicate native source index')
    if any(not 0<=i<tables[1]['count'] for i in pi) or any(not 0<=i<tables[24]['count'] for i in si):raise ValueError('native source index outside descriptor')
    if manifest['source_coverage']=='COMPLETE_NATIVE_PLAYER_POOL_AND_STAT_BANK':
        if set(pi)!=set(range(tables[1]['count'])) or set(si)!=set(range(tables[24]['count'])):raise ValueError('incomplete native pool coverage')
    elif manifest['source_coverage']!='CURATED_RESEARCH_SUBSET':raise ValueError('native source coverage must be explicit')
    facts={k:[] for k in ('native_fields','native_player_stat_observations','native_player_sources','native_player_stat_links','native_identity_links','field_gaps')}
    bindings=json.loads(PROFILE_PATH.read_bytes())['stat_fields']
    for name,column in STAT_COLUMNS.items():
        f=bindings[name]
        facts['native_fields'].append({'field_id':'CURRENT_PLAYERSTATDATA_V1:'+str(f['name_crc']),'source_group':'RES-H',
            'native_key':name,'table_name':'native_player_stat_observations','column_name':column,
            'evidence_grade':'CURRENT_NATIVE_HEADER_FIELDS_INITIALIZER_AND_LITERAL_IDENTIFIER_CRC_VERIFIED',
            'visibility':'GM_PUBLIC','min_native_value':0,'max_native_value':(1<<f['width'])-1,
            'codec':f'unsigned_le_size{f["size"]}_bit{f["start_bit"]}_width{f["width"]}',
            'layout_version':'NATIVE_PLAYERSTATDATA_48_V1','source_ref':'award_native_profile.json; current capture native metadata',
            'unit':'native unsigned storage value','legal_range_state':'STORAGE_WIDTH_VERIFIED; GAME_UI_RANGE_NOT_CERTIFIED'})
    stat_ids={s['source_stat_index']:f'{unit}:stat:{s["source_stat_index"]}' for s in stats}
    for s in stats:
        if s['stat_year']!=1900+s['compact_year_raw']:raise ValueError('native CompactYear must use all eight bits')
        expected='CONSISTENT' if s['points_raw']==2*s['fg_made_raw']+s['three_made_raw']+s['ft_made_raw'] else 'INCONSISTENT_SOURCE_WORDS_RETAINED'
        if s['scoring_identity_status']!=expected:raise ValueError('native score conservation annotation mismatch')
        facts['native_player_stat_observations'].append({'stat_observation_id':stat_ids[s['source_stat_index']],**s})
    uid_counts=Counter(p['native_unique_id_raw'] for p in players);roster_preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    source_ids={p['source_player_index']:f'{unit}:player-source:{p["source_player_index"]}' for p in players}
    for p in players:
        canonical=None;candidate='player:native:'+str(p['preserved_id_raw'])
        if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid_counts[p['native_unique_id_raw']]==1 and roster_preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical_legacy_map.get(candidate)==p['observed_name']:
            canonical=candidate
        facts['native_player_sources'].append({'player_source_id':source_ids[p['source_player_index']],**p,'player_id':canonical,
            'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if canonical else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
        if canonical:facts['native_identity_links'].append({'entity_type':'player','entity_id':canonical,
            'native_id':'PLAYERDATA.UniqueId:'+str(p['native_unique_id_raw']),'valid_from':observed_at,
            'identity_state':'CURRENT_NATIVE_UNIQUE_ID_OBSERVED; LIFECYCLE_UNVERIFIED'})
    lookup={(r['source_player_index'],r['history_slot_index']):r for r in links}
    if len(lookup)!=len(links) or set(lookup)!={(i,slot) for i in pi for slot in range(manifest['season_stats_array_count'])}:raise ValueError('incomplete/duplicate native stat reference array')
    for i in pi:
        after=False
        for slot in range(manifest['season_stats_array_count']):
            r=lookup[i,slot];status=classify_stat_link(r['native_stat_index_raw'],slot,tables[24]['count'],after)
            if status!=r['link_status']:raise ValueError('native stat link classification mismatch')
            stat=stat_ids.get(r['native_stat_index_raw']) if status in ('CURRENT_INDEX_CANDIDATE','HISTORY_INDEX_CANDIDATE','HISTORY_INDEX_AFTER_EMPTY_SLOT') else None
            facts['native_player_stat_links'].append({'player_source_id':source_ids[i],'history_slot_index':slot,
                'native_stat_index_raw':r['native_stat_index_raw'],'stat_observation_id':stat,'link_status':status})
            if slot>0 and status in ('SENTINEL_NO_ACCEPTED_LINK','ZERO_HISTORY_SLOT_UNVERIFIED'):after=True
    facts['field_gaps']=[dict(affected_domain=d,target_field=t,reason=r,impact=i) for d,t,r,i in (
        ('RES-H','NATIVE_AWARD_FLAGS_VS_ACCEPTED_INSTANCES','Native winner/selection fields are observed, but canonical subjects and final award-instance semantics need separate acceptance','No final award/recipient instances fabricated from incomplete identity or allocation semantics'),
        ('RES-P','UNIQUE_ID_VS_PRESERVED_ID','Current PLAYERDATA.UniqueId is +244; old adapters used low16 of +760 PreservedId','Keep legacy opaque entity keys and history; append exact current-ID evidence only on matched current roster names'),
        ('RES-H','STAT_REFERENCE_ARRAY_SCOPE','Native SeasonStats has 25 fixed slots, including gaps and after-empty references','Preserve every position; no first-empty truncation or invented chronological order'),
        ('RES-H','NATIVE_STAT_ALLOCATION_AND_SHARED_OWNERS','ReferenceCount and shared/unowned source records are observed','Keep all source records; no arbitrary subject choice or unallocated-as-current inference'),
        ('RES-H','NATIVE_NEWS_SOURCE','Native stat flags are not a news source','News remains unobserved by this adapter'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_HONOR_STATS',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'NATIVE_PLAYERSTATDATA_FIELDS_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},
        'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_native_honors(pid,save_directory,loaded_filename,new_output_directory):
    from cadence import prepare_annual_capture,attach_annual_period
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid)
        refresh_year,previous=prepare_annual_capture(reader,bound_database(save_directory,binding),'NATIVE_HONOR_STATS')
        if previous is not None:
            previous.update({'save_id':binding['save_id'],'read_trace':reader.trace})
            _json(out/'ingest-result.json',previous);return previous
        manifest,blobs=collect_native_honors(reader);reader.close()
        if manifest['season_year']!=refresh_year:raise ValueError('game season changed during annual honor acquisition')
        if manifest['source_coverage']!='COMPLETE_NATIVE_PLAYER_POOL_AND_STAT_BANK':raise ValueError('live adapter requires complete bounded source pools')
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'honors-manifest.json',manifest)
        report={'status':'NATIVE_HONORS_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,
            'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'profile_sha256':hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'honors-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'NATIVE_STAT_BANK_PUBLIC_SUBJECT_PROJECTION_OR_CONTROL','source_version':'NATIVE_PLAYERSTATDATA_FIELDS_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (Path(__file__),PROFILE_PATH,Path(__file__).with_name('live_world.py')):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'EXECUTED_NATIVE_LAYOUT_OR_PUBLIC_READ_SOURCE','source_version':'NATIVE_PLAYERSTATDATA_FIELDS_V1','payload_ref':str(path.name)})
        token=hashlib.sha256((out/'honors-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as c:
            canonical={r['player_id']:r['display_name'] for r in c.execute('SELECT player_id,display_name FROM players')}
            payload=honors_payload(binding,manifest,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ'
            attach_annual_period(payload,'NATIVE_HONOR_STATS',refresh_year)
            receipt=_AcquisitionReceipt(payload,reader);status=ingest_capture(c,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'refresh_family':'NATIVE_HONOR_STATS','refresh_period_year':refresh_year,
            'counts':{name:len(values) for name,values in payload['facts'].items()},'game_writes':False,'restricted_player_bytes_read':0,
            'source_pid':pid,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'NATIVE_HONORS_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');p.add_argument('--source',action='store_true');a=p.parse_args()
    r=(probe_native_honors if a.source else probe_award_metadata)(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status'] in ('AWARD_NATIVE_METADATA_CAPTURED','NATIVE_HONORS_SOURCE_CAPTURED') else 2)
