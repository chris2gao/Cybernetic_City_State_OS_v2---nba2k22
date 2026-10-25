"""Complete narrow public PLAYER pool projections for contracts/base badges."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct,zlib
from pathlib import Path
from award_reader import read_native_fields
from cadence import observed_game_season_year
from engine import connect,ingest_capture
from family_codec import decode_fixed_utf16
from league_reader import read_native_enum
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _AcquisitionReceipt,_json,read_binding,bound_database,RESTRICTED_PLAYER_RANGES
from player_detail_codec import PROFILE,PROFILE_PATH,LAYOUT,native_contracts,native_badges
from schedule_reader import bounded_block


def projection_ranges():
    intervals=[(0,80),(96,104),(168,176),(244,246),(760,764)]
    intervals.extend((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8) for group in ('contract_fields','badge_fields') for f in PROFILE[group].values())
    merged=[]
    for low,high in sorted(intervals):
        if any(low<b and a<high for a,b in RESTRICTED_PLAYER_RANGES):raise ValueError('public field intersects restricted PLAYER bytes')
        if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
        else:merged.append((low,high))
    return merged


def reconstruct_projection(part,ranges):
    if len(part)!=sum(b-a for a,b in ranges):raise ValueError('incomplete PLAYER detail projection')
    raw=bytearray(1264);at=0
    for low,high in ranges:raw[low:high]=part[at:at+high-low];at+=high-low
    return bytes(raw)


def verify_detail_metadata(reader):
    metadata=[]
    for entry in PROFILE['types']:
        if entry['name']=='PLAYERDATA':
            value=read_native_fields(reader,entry,1264,read_enums=False)
            native={f['name_crc']:f for f in value['fields']}
            ranges=[]
            for name in ('OriginalPotential','PotentialRaw','MinPotential','MaxPotential','PreviousPotentialRaw'):
                f=native[zlib.crc32(name.encode())];ranges.append((f['offset'],f['offset']+(f['start_bit']+f['width']+7)//8))
            merged=[]
            for low,high in sorted(ranges):
                if merged and low<=merged[-1][1]:merged[-1]=(merged[-1][0],max(high,merged[-1][1]))
                else:merged.append((low,high))
            if tuple(merged)!=RESTRICTED_PLAYER_RANGES:raise ValueError('private PLAYER exclusion layout changed')
            for name in ('UnlocalizedFirstName','UnlocalizedLastName'):
                f=native[PROFILE['public_identity_fields'][name]['name_crc']];w=f['words'];ptr=w[6]|w[7]<<32
                raw=reader.read(ptr,24,'PLAYER_DETAIL_NAME_DIMENSION:'+name)
                if (w[5]>>16)!=1 or struct.unpack_from('<I',raw)[0]!=20:raise ValueError('native name extent changed')
                if reader.read(ptr,24,'PLAYER_DETAIL_NAME_DIMENSION_RECHECK:'+name)!=raw:raise ValueError('native name dimensions unstable')
        else:
            value=read_native_enum(reader,entry);expected={(int(code),v['name_crc']) for code,v in PROFILE['enum_labels'][entry['name']].items()}
            if {(v['value'],v['name_crc']) for v in value['values']}!=expected or len(value['values'])!=len(expected):raise ValueError('native player enum changed')
        metadata.append(value)
    dispatch=PROFILE['badge_base_dispatch']
    for key,rva in (('code',dispatch['code_start_rva']),('table',dispatch['table_rva'])):
        raw=bytes.fromhex(dispatch[key+'_hex'])
        if bounded_block(reader,reader.module_base+rva,len(raw),'PLAYER_DETAIL_BADGE_DISPATCH_'+key.upper())!=raw:raise ValueError('native base badge dispatch changed')
    return metadata


def collect_public_player_pool(reader,*,ranges,metadata):
    ranges=[tuple(r) for r in ranges]
    if any(not 0<=low<high<=1264 or high-low>1248 or any(low<b and a<high for a,b in RESTRICTED_PLAYER_RANGES) for low,high in ranges):raise ValueError('invalid/private public PLAYER interval')
    for low,high in ((0,80),(96,104),(244,246),(760,764)):
        if not any(a<=low and high<=b for a,b in ranges):raise ValueError('public projection lacks required identity interval')
    year=observed_game_season_year(reader)
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'PLAYER_DETAIL_ROSTER_POINTER');root=int.from_bytes(pointer,'little');descriptors={};tables={};controls=[];blobs={}
    for slot,maximum,stride in ((1,8192,1264),(8,1024,4696)):
        raw=reader.read(root+slot*16,16,f'PLAYER_DETAIL_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum or address<0x10000:raise ValueError('native public PLAYER descriptor outside bound')
        descriptors[slot]=raw;tables[slot]={'count':count,'address':address,'stride':stride}
    core=set(range(30))-{7};core.add(31);teams={};assigned={}
    for i in range(tables[8]['count']):
        address=tables[8]['address']+i*4696;ident=reader.read(address+0xCA8,2,'PLAYER_DETAIL_TEAM_ID');tid=int.from_bytes(ident,'little')
        if tid not in core:continue
        if tid in teams.values():raise ValueError('duplicate current native core team')
        teams[address]=tid;roster=reader.read(address,200,'PLAYER_DETAIL_CURRENT_ROSTER');blobs[f'team-{tid}.roster.bin']=roster
        controls.extend(((address+0xCA8,ident,'PLAYER_DETAIL_TEAM_ID_RECHECK'),(address,roster,'PLAYER_DETAIL_ROSTER_RECHECK')))
        for pos,p in enumerate(struct.unpack('<25Q',roster)):
            if not p:continue
            index,remainder=divmod(p-tables[1]['address'],1264)
            if remainder or not 0<=index<tables[1]['count'] or index in assigned:raise ValueError('native current roster pointer collision/outside pool')
            assigned[index]=(tid,pos)
    if set(teams.values())!=core:raise ValueError('complete current core-team context absent')
    parts=[];players=[]
    for index in range(tables[1]['count']):
        address=tables[1]['address']+index*1264;pieces=[]
        for low,high in ranges:
            raw=reader.read(address+low,high-low,f'PLAYER_DETAIL_PUBLIC:{index}:{low}');pieces.append(raw);controls.append((address+low,raw,f'PLAYER_DETAIL_PUBLIC_RECHECK:{index}:{low}'))
        projection=b''.join(pieces);parts.append(projection);raw=reconstruct_projection(projection,ranges)
        try:name=(decode_fixed_utf16(raw[40:80])+' '+decode_fixed_utf16(raw[:40])).strip() or None;status='OBSERVED_UTF16_PREFIX' if name else 'NO_PUBLIC_NAME'
        except UnicodeDecodeError:name=None;status='INVALID_UTF16_PREFIX'
        team=teams.get(int.from_bytes(raw[96:104],'little'));current=assigned.get(index)
        if current and (team!=current[0] or not name):raise ValueError('current native player lacks reciprocal roster/name')
        players.append({'source_player_index':index,'native_unique_id_raw':int.from_bytes(raw[244:246],'little'),
            'preserved_id_raw':int.from_bytes(raw[760:764],'little'),'observed_name':name,'name_status':status,
            'native_team_id':team,'current_core_roster_status':'CURRENT_CORE_ROSTER' if current else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':current[1] if current else None})
    blobs['player-detail-public-projections.bin']=b''.join(parts)
    for address,raw,label in controls:
        if reader.read(address,len(raw),label)!=raw:raise ValueError('native player detail or roster changed during capture')
    for slot,raw in descriptors.items():
        if reader.read(root+slot*16,16,f'PLAYER_DETAIL_SLOT{slot}_RECHECK')!=raw:raise ValueError('native player descriptor changed')
    if reader.read(reader.module_base+ROSTER_RVA,8,'PLAYER_DETAIL_ROOT_RECHECK')!=pointer or observed_game_season_year(reader)!=year:raise ValueError('native player context/year changed')
    return {'season_year':year,'descriptors':tables,'metadata':metadata,'players':players,'core_team_pointer_map':teams,
        'projection_ranges':ranges,'projection_stride':sum(b-a for a,b in ranges),'current_core_roster_count':len(assigned),
        'source_coverage':'COMPLETE_NATIVE_PLAYER_POOL_PUBLIC_PROJECTION',
        'excluded_player_byte_ranges':list(RESTRICTED_PLAYER_RANGES),'game_writes':False,'full_player_struct_reads':0,'restricted_player_bytes_read':0},blobs


def collect_player_details(reader):
    manifest,blobs=collect_public_player_pool(reader,ranges=projection_ranges(),metadata=verify_detail_metadata(reader))
    stride=manifest['projection_stride'];ranges=manifest['projection_ranges'];data=blobs['player-detail-public-projections.bin'];contracts=[];badges=[]
    for index in range(len(manifest['players'])):
        raw=reconstruct_projection(data[index*stride:(index+1)*stride],ranges)
        team=manifest['core_team_pointer_map'].get(int.from_bytes(raw[168:176],'little'))
        contracts.append({'source_player_index':index,**native_contracts(raw),'native_contract_team_id_raw':team,
            'contract_team_status':'NATIVE_CORE_TEAM_POINTER_OBSERVED' if team is not None else 'NO_CORE_CONTRACT_TEAM_BINDING'})
        badges.extend({'source_player_index':index,**r} for r in native_badges(raw))
    manifest.update({'contract_rows':contracts,'badge_rows':badges,'source_coverage':'COMPLETE_NATIVE_PLAYER_POOL_PUBLIC_CONTRACT_AND_BASE_BADGES'})
    return manifest,blobs


def detail_payload(binding,manifest,artifacts,stamp,token,canonical=None,known_teams=None):
    canonical=canonical or {};known_teams=known_teams or set();unit='player-detail:'+token;year=manifest['season_year'];players=manifest['players'];count=len(players)
    if manifest.get('game_writes') is not False or manifest.get('restricted_player_bytes_read')!=0:raise ValueError('public detail source must be read-only and private-free')
    descriptor=manifest['descriptors'].get('1',manifest['descriptors'].get(1))
    if descriptor['count']!=count or {p['source_player_index'] for p in players}!=set(range(count)):raise ValueError('incomplete native player detail subjects')
    if len(manifest['contract_rows'])!=count or {r['source_player_index'] for r in manifest['contract_rows']}!=set(range(count)):raise ValueError('incomplete contract family')
    badge_ids={f['badge_id'] for f in PROFILE['badge_fields'].values() if not f['reserved']}
    if len(manifest['badge_rows'])!=count*len(badge_ids) or {(r['source_player_index'],r['native_badge_id']) for r in manifest['badge_rows']}!={(i,b) for i in range(count) for b in badge_ids}:raise ValueError('incomplete/duplicate native base badge family')
    facts={'native_fields':[],'native_player_sources':[],'player_contract_observations':[],'player_badge_values':[]};source_ids={};canonical_ids={}
    uid=Counter(p['native_unique_id_raw'] for p in players);preserved=Counter(p['preserved_id_raw'] for p in players if p['current_core_roster_status']=='CURRENT_CORE_ROSTER')
    for p in players:
        i=p['source_player_index'];key='player:native:'+str(p['preserved_id_raw']);linked=None
        if p['current_core_roster_status']=='CURRENT_CORE_ROSTER' and uid[p['native_unique_id_raw']]==1 and preserved[p['preserved_id_raw']]==1 and p['preserved_id_raw']<=65535 and canonical.get(key)==p['observed_name']:linked=key
        source_ids[i]=f'{unit}:player:{i}';canonical_ids[i]=linked
        facts['native_player_sources'].append({'player_source_id':source_ids[i],**p,'player_id':linked,
            'canonical_link_status':'CURRENT_ROSTER_PRESERVED_ID_AND_NAME_MATCH; UNIQUE_ID_LIFECYCLE_UNVERIFIED' if linked else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD'})
    for family,prefix,target in (('contract_fields','CONTRACT','player_contract_observations'),('badge_fields','BADGE','player_badge_values')):
        for name,f in PROFILE[family].items():
            if f.get('reserved'):continue
            facts['native_fields'].append({'field_id':f'CURRENT_PLAYERDATA_{prefix}_V1:'+str(f['name_crc']),'source_group':'RES-P' if prefix=='BADGE' else 'RES-M',
                'native_key':f['native_name'],'table_name':target,'column_name':'native_code' if prefix=='BADGE' else name+'_raw',
                'evidence_grade':'CURRENT_NATIVE_FIELDS_AND_ENUMS; ALL_BASE_BADGE_ID_DISPATCH_CASES_VERIFIED','visibility':'GM_PUBLIC',
                'min_native_value':0,'max_native_value':(1<<f['width'])-1,'codec':f'unsigned_bit{f["start_bit"]}_width{f["width"]}_at{f["offset"]}',
                'layout_version':LAYOUT,'source_ref':'player_detail_native_profile.json; current metadata/code capture','unit':'native unsigned base storage; UI/salary/effective context separate','legal_range_state':'STORAGE_WIDTH_AND_NATIVE_ENUMS_VERIFIED; UI_RANGE_SEPARATE'})
    for original in manifest['contract_rows']:
        r=dict(original);i=r.pop('source_player_index');tid='team:native:'+str(r['native_contract_team_id_raw'])
        facts['player_contract_observations'].append({'player_id':canonical_ids[i],'source_player_id':source_ids[i],'team_id':tid if tid in known_teams else None,'layout_version':LAYOUT,**r})
    for original in manifest['badge_rows']:
        r=dict(original);i=r.pop('source_player_index');facts['player_badge_values'].append({'player_id':canonical_ids[i],'source_player_id':source_ids[i],**r})
    facts['field_gaps']=[dict(affected_domain=d,target_field=t,reason=r,impact=effect) for d,t,r,effect in (
        ('RES-P','EFFECTIVE_BADGE_CONTEXT_AND_UI','Stored base extraction and enum codes are verified; later native context/boost logic and UI activation remain separate','Do not present stored base badges as effective game-context levels'),
        ('RES-M','CONTRACT_UNITS_SENTINELS_AND_LEGACY_ALIASES','Native widths/options/RosterType verified; salary scale/sentinels/UI duration remain unaccepted','Preserve full raw values; original_contract_years is ContractLength and contract_type is RosterType, without extra semantics'),
        ('RES-P','NATIVE_SOURCE_SUBJECT_LIFECYCLE','Source-only pool subjects and exact current roster matches do not establish cross-session identity','Unbound source rows retained; existing opaque IDs/history unchanged'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_PLAYER_CONTRACT_AND_BASE_BADGES','observed_at':stamp,
        'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_player_details(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename);db=bound_database(save_directory,binding)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_player_details(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'player-detail-manifest.json',manifest)
        report={'status':'COMPLETE_NATIVE_PUBLIC_PLAYER_DETAILS_CAPTURED','observed_at':stamp,'pid':pid,'binding_sha256':binding_hash,
            'read_trace':reader.trace,'game_writes':False,'restricted_player_bytes_read':0,
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),PROFILE_PATH,Path(__file__).with_name('player_detail_codec.py'))},
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'player-detail-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'NATIVE_PLAYER_PUBLIC_DETAIL_OR_CONTROL',
            'source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        token=hashlib.sha256((out/'player-detail-report.json').read_bytes()).hexdigest()[:24]
        with connect(db) as conn:
            canonical={r['player_id']:r['display_name'] for r in conn.execute('SELECT player_id,display_name FROM players')};teams={r[0] for r in conn.execute('SELECT team_id FROM teams')}
            payload=detail_payload(binding,manifest,artifacts,stamp,token,canonical,teams);payload['evidence_grade']='LIVE_READ'
            receipt=_AcquisitionReceipt(payload,reader);status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'source_pid':pid,'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},'game_writes':False,'restricted_player_bytes_read':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'PLAYER_DETAIL_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
