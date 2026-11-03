"""Bounded native draft assets, prospect templates and waived-salary sources.

This observes source state; it never infers draft results, trades or free-agent
availability. Prospect/PLAYER public reads exclude the hidden Potential byte.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib,importlib.util,json,struct
from pathlib import Path
from engine import connect,ingest_capture
from schema_model import DOMAIN
from family_codec import decode_fixed_utf16,public_player_families
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _public_raw,_json,read_binding,bound_database,_AcquisitionReceipt
from organization_reader import CORE_IDS,_ReadAdapter
from schedule_reader import bounded_block

DRAFT_PROFILE_PATH=DOMAIN/'config/draft_asset_profile.json'
DRAFT_PROFILE=json.loads(DRAFT_PROFILE_PATH.read_bytes())


def draft_codec():
    spec=importlib.util.spec_from_file_location('world_native_draft_assets',DOMAIN/'src/draft_assets.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def decode_waived_record(raw,index,team_ids):
    if len(raw)!=136:raise ValueError('waived source record must be 136 bytes')
    owner=int.from_bytes(raw[8:16],'little')
    # Current raw controls expose two inline 40-byte UTF16 fields. The first Q
    # word can link another waived record; it is NOT treated as a PLAYER pointer.
    try:
        name=(decode_fixed_utf16(raw[96:136])+' '+decode_fixed_utf16(raw[56:96])).strip()
        text_status='OBSERVED_INLINE_UTF16_CANDIDATE' if name else 'NO_INLINE_NAME'
    except UnicodeDecodeError:name=None;text_status='INVALID_UTF16_PREFIX'
    return {'source_row_index':index,'native_team_id':team_ids.get(owner),
        'owner_mapping_status':'CORE_TEAM_POINTER' if owner in team_ids else 'UNMAPPED_OR_EMPTY',
        'native_player_id':None,'observed_player_name':name or None,'player_mapping_status':'CANONICAL_PLAYER_NOT_ESTABLISHED',
        'name_source_status':text_status,'salary_year_1_raw':int.from_bytes(raw[16:20],'little'),
        'salary_year_2_raw':int.from_bytes(raw[20:24],'little'),'salary_year_3_raw':int.from_bytes(raw[24:28],'little')}


def decode_prospect_slot(raw,index):
    if len(raw)!=1264:raise ValueError('prospect source record must be 1264 public bytes')
    row={'source_row_index':index,'native_prospect_id':int.from_bytes(raw[0x2F8:0x2FA],'little'),
        'draft_year':None,'class_year_status':'UNVERIFIED_NOT_INFERRED_FROM_FUTURE_PICK_BASE'}
    try:
        name=(decode_fixed_utf16(raw[40:80])+' '+decode_fixed_utf16(raw[:40])).strip()
        row['display_name']=name or None
        if not name:
            row['decode_status']='UNINITIALIZED_NO_NAME';return row
        row['families']=public_player_families(raw);row['decode_status']='NAMED_PUBLIC_PROSPECT_TEMPLATE'
    except UnicodeDecodeError:
        row['display_name']=None;row['decode_status']='INVALID_UTF16_NAME_PREFIX_NO_PROFILE_INGEST'
    return row


def collect_market(reader):
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'MARKET_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    specs={1:(8192,1264),4:(4096,1264),8:(1024,4696),28:(10000,62),42:(4096,32),61:(4096,136)}
    descriptors={};tables={}
    for slot,(maximum,stride) in specs.items():
        raw=reader.read(root+slot*16,16,f'MARKET_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 0<=count<=maximum or (count and address<0x10000):raise ValueError('market descriptor outside bounded envelope')
        descriptors[slot]=raw;tables[slot]={'count':count,'address':address,'stride':stride}
    teams=[];blobs={};controls=[]
    for i in range(tables[8]['count']):
        address=tables[8]['address']+i*4696;ident=reader.read(address+0xCA8,2,'MARKET_TEAM_NATIVE_ID')
        tid=int.from_bytes(ident,'little')
        if tid not in CORE_IDS:continue
        if any(t['native_team_id']==tid for t in teams):raise ValueError('duplicate core TEAM identity')
        name=reader.read(address+0x2B4,40,f'MARKET_TEAM:{tid}:NAME');city=reader.read(address+0x2E6,36,f'MARKET_TEAM:{tid}:CITY')
        stats_idx=reader.read(address+0xE80,2,f'MARKET_TEAM:{tid}:STATS_INDEX')
        teams.append({'native_team_id':tid,'address':address,'pool_index':i,'name':decode_fixed_utf16(name),
            'city':decode_fixed_utf16(city),'stats_index':int.from_bytes(stats_idx,'little')})
        for off,data,label in ((0xCA8,ident,'ID'),(0x2B4,name,'NAME'),(0x2E6,city,'CITY'),(0xE80,stats_idx,'STATS_INDEX')):
            controls.append((address+off,data,f'MARKET_TEAM:{tid}:{label}:RECHECK'))
    if {t['native_team_id'] for t in teams}!=CORE_IDS:raise ValueError('core TEAM set not complete')
    team_ids={t['address']:t['native_team_id'] for t in teams};first=teams[0];idx=first['stats_index']
    if idx>=tables[28]['count'] or idx==65535:raise ValueError('native season year source absent')
    current=reader.read(tables[28]['address']+idx*62,62,'MARKET_NATIVE_SEASON_CONTROL')
    year=1900+current[4];blobs['season-control.bin']=current
    controls.append((tables[28]['address']+idx*62,current,'MARKET_NATIVE_SEASON_RECHECK'))
    for i,item in enumerate(DRAFT_PROFILE['code_evidence']):
        raw=reader.read(reader.module_base+item['module_rva'],len(bytes.fromhex(item['expected_hex'])),f'MARKET_DRAFT_CODE:{i}')
        if raw.hex()!=item['expected_hex']:raise ValueError('draft native getter code changed: '+item['name'])
        blobs[f'draft-code-{i}.bin']=raw;controls.append((reader.module_base+item['module_rva'],raw,f'MARKET_DRAFT_CODE:{i}:RECHECK'))
    codec=draft_codec();observations,next_year=codec.read_assets(_ReadAdapter(reader),{'draft_assets':tables[42]},team_ids,year)
    assets=[]
    for index,row,raw in observations:
        meta=int.from_bytes(raw[28:32],'little')
        assets.append({'source_row_index':index,**row,'native_year_offset':meta&7,'native_round_code':(meta>>3)&31,
            'native_pick_index':(meta>>8)&255,'assigned_player_pointer_present':bool(int.from_bytes(raw[16:24],'little'))})
        blobs[f'draft-asset-{index}.bin']=raw;controls.append((tables[42]['address']+index*32,raw,f'MARKET_DRAFT_ASSET:{index}:RECHECK'))
    waived=[]
    for index in range(tables[61]['count']):
        address=tables[61]['address']+index*136;raw=reader.read(address,136,f'MARKET_WAIVED:{index}')
        row=decode_waived_record(raw,index,team_ids)
        waived.append(row);blobs[f'waived-{index}.bin']=raw;controls.append((address,raw,f'MARKET_WAIVED:{index}:RECHECK'))
    prospects=[];prospect_controls=[]
    for index in range(tables[4]['count']):
        address=tables[4]['address']+index*1264;raw=_public_raw(reader,address,f'MARKET_PROSPECT:{index}')
        row=decode_prospect_slot(raw,index)
        prospects.append(row);blobs[f'prospect-{index}.public.bin']=raw;prospect_controls.append((address,raw,index))
    for address,raw,label in controls:
        if bounded_block(reader,address,len(raw),label)!=raw:raise ValueError('market source changed during acquisition')
    for address,raw,index in prospect_controls:
        if _public_raw(reader,address,f'MARKET_PROSPECT:{index}:RECHECK')!=raw:raise ValueError('prospect source changed during acquisition')
    for slot,raw in descriptors.items():
        if reader.read(root+slot*16,16,f'MARKET_SLOT{slot}_RECHECK')!=raw:raise ValueError('market descriptor changed')
    if reader.read(reader.module_base+ROSTER_RVA,8,'MARKET_ROSTER_RECHECK')!=pointer:raise ValueError('market roster context changed')
    return {'descriptors':tables,'teams':teams,'season_year':year,'next_future_pick_year':next_year,'draft_assets':assets,
        'waived_salaries':waived,'prospects':prospects,'future_pick_count':sum(a['mapping_status']==codec.VERIFIED for a in assets),
        'prospect_id_duplicates':{str(k):v for k,v in Counter(p['native_prospect_id'] for p in prospects).items() if v>1},
        'game_writes':False,'potential_bytes_read':0,'source_scope':'DRAFT_FUTURE_PICKS; PROSPECT_TEMPLATES_YEAR_UNKNOWN; WAIVED_RAW_OBSERVATIONS'},blobs


def probe_market(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_market(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'market-manifest.json',manifest)
        report.update({'status':'MARKET_SOURCE_CAPTURED','read_trace':reader.trace,'artifact_sha256':{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'MARKET_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'market-report.json',report);return report


def market_payload(binding,manifest,artifacts,observed_at,token):
    year=manifest['season_year'];unit='market:'+token
    facts={name:[] for name in ('teams','draft_pick_assets','draft_pick_ownerships','waived_salary_observations',
        'draft_pool_slot_observations','draft_prospects','draft_prospect_attribute_snapshots','draft_prospect_tendency_snapshots','draft_prospect_play_type_slots')}
    tid=lambda n:'team:native:'+str(n)
    for t in manifest['teams']:
        facts['teams'].append({'team_id':tid(t['native_team_id']),'native_team_id':str(t['native_team_id']),
            'display_name':(t['city']+' '+t['name']).strip(),'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
    for row in manifest['draft_assets']:
        if row['mapping_status']!='VERIFIED_SIMPLE_FUTURE_PICK':continue
        key=f'pick:{row["draft_year"]}:{row["draft_round"]}:original:{row["original_owner_team_id"]}'
        facts['draft_pick_assets'].append({'pick_id':key,'draft_year':row['draft_year'],'draft_round':row['draft_round'],
            'original_team_id':tid(row['original_owner_team_id']),'native_pick_id':None})
        facts['draft_pick_ownerships'].append({'pick_id':key,'owner_team_id':tid(row['current_owner_team_id']),'origin_type':'NATIVE',
            'source_row_index':row['source_row_index'],'native_pick_index_raw':row['native_pick_index'],
            'protection_status':'UNKNOWN','swap_status':'UNKNOWN'})
    for row in manifest['waived_salaries']:
        facts['waived_salary_observations'].append({**{k:v for k,v in row.items() if k!='native_team_id'},
            'team_id':tid(row['native_team_id']) if row['native_team_id'] is not None else None,'player_id':None})
    for row in manifest['prospects']:
        facts['draft_pool_slot_observations'].append({'source_row_index':row['source_row_index'],'slot_state':row['decode_status'],
            'native_prospect_id':str(row['native_prospect_id']),'display_name':row.get('display_name'),
            'draft_year':row['draft_year'],'class_year_status':row['class_year_status']})
        if row['decode_status']!='NAMED_PUBLIC_PROSPECT_TEMPLATE':continue
        key=f'{unit}:prospect-slot:{row["source_row_index"]}'
        facts['draft_prospects'].append({'prospect_id':key,'native_prospect_id':str(row['native_prospect_id']),
            'display_name':row['display_name'],'draft_year':row['draft_year'],'class_year_status':row['class_year_status']})
        family=row['families']
        facts['draft_prospect_attribute_snapshots'].append({'prospect_id':key,**family['attributes']})
        facts['draft_prospect_tendency_snapshots'].append({'prospect_id':key,**family['tendencies']})
        facts['draft_prospect_play_type_slots'].extend({'prospect_id':key,**slot} for slot in family['play_types'])
    facts['field_gaps']=[{'affected_domain':'RES-M','target_field':target,'reason':reason,'impact':impact} for target,reason,impact in (
        ('PICK_PROTECTION_AND_SWAPS','Simple native getters/coverage verify owner/year/round; protection/swap semantics not acquired','Both statuses UNKNOWN; no tradeability assertion'),
        ('NON_FUTURE_DRAFT_RECORDS','Only complete simple future-pick groups accepted; other source records remain raw evidence','No historical draft result inferred'),
        ('PROSPECT_CLASS_YEAR_AND_INITIALIZATION','Allocated draft slots may be unnamed; actual class year not observed','No unnamed prospects or guessed draft_year created'),
        ('WAIVED_CANONICAL_PLAYER_AND_YEAR_UNITS','136-byte source has candidate inline names/three salary buckets; no canonical person/absolute year association','PLAYER FK remains NULL; no cap-space sum or release event inferred'),
        ('MARKET_AVAILABILITY','Pick/prospect/waived records do not establish free-agent or trade availability','No market status invented'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_MARKET_SOURCES',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'NATIVE_MARKET_SOURCES_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_market(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_market(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'market-manifest.json',manifest)
        report={'status':'MARKET_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'market-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'ACTUAL_NATIVE_MARKET_WINDOWS_SOURCE','source_version':'NATIVE_MARKET_SOURCES_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (DRAFT_PROFILE_PATH,DOMAIN/'src/draft_assets.py',DOMAIN/'config/memory_field_profile.json'):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'DRAFT_NATIVE_GETTER_OR_PUBLIC_LAYOUT','source_version':'NATIVE_MARKET_SOURCES_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'market-report.json').read_bytes()).hexdigest()[:24]
        payload=market_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'counts':{name:len(rows) for name,rows in payload['facts'].items()},'next_future_pick_year':manifest['next_future_pick_year'],
            'core_owner_waived_records':sum(w['owner_mapping_status']=='CORE_TEAM_POINTER' for w in manifest['waived_salaries']),
            'draft_slot_states':dict(Counter(p['decode_status'] for p in manifest['prospects'])),
            'game_writes':False,'potential_bytes_read':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'MARKET_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_market(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status']=='MARKET_SOURCE_CAPTURED' else 2)
