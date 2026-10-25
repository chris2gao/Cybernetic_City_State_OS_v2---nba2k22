"""Observe registered global settings and complete USER/CPU slider tables.

Targets, defaults and recommendations in old catalogs are never read as state
or applied. Global setting words are unrelated to hidden PLAYER Potential.
Unmapped slider names and actual UI/effect semantics remain explicit gaps.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,math,struct
from pathlib import Path
from schema_model import DOMAIN
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json,read_binding,bound_database,_AcquisitionReceipt
from schedule_reader import bounded_block
from engine import connect,ingest_capture

CATALOG_DIR=DOMAIN/'config/state_io_native'
CATALOGS={name:json.loads((CATALOG_DIR/(name+'.json')).read_bytes()) for name in ('world','settings','court')}
SLIDER_RVA=int(CATALOGS['court']['slot_sliders_rva'],16)
SLIDER_COUNT=(CATALOGS['court']['struct_size']-4)//16


def catalog_layout():
    """One location/type -> all source aliases; exclude desired/default content."""
    cells={}
    for catalog_name in ('world','settings'):
        catalog=CATALOGS[catalog_name]
        for group,fields in catalog['fields'].items():
            for name,f in fields.items():
                if f.get('type') not in ('uint32','float') or f.get('slot') not in catalog['slots']:continue
                rva=int(catalog['slots'][f['slot']]['rva'],16);offset=int(f['offset'],16);encoding=f['type']
                alias={'catalog':catalog_name,'group':group,'name':name,'slot':f['slot'],'encoding':encoding,
                       **{k:f[k] for k in ('min','max','unit','name_zh','status') if k in f}}
                cells.setdefault((rva,offset,encoding),[]).append(alias)
    for name,f in CATALOGS['court']['modified_sliders'].items():
        for side,delta in (('USER',0),('CPU',4)):
            offset=4+f['table_index']*8+delta
            cells.setdefault((SLIDER_RVA,offset,'float'),[]).append({'catalog':'court','group':'gameplay_sliders',
                'name':name,'side':side,'native_token':f['native_token'],'slot':'SLOT_SLIDERS','encoding':'float'})
    return cells


def decode_word(raw,encoding):
    if len(raw)!=4:raise ValueError('setting word must be four bytes')
    word=int.from_bytes(raw,'little')
    if encoding=='uint32':return {'integer_value':word,'raw_word_u32':word,'value_status':'OBSERVED_UINT32'}
    if encoding!='float':raise ValueError('unsupported setting word encoding')
    value=struct.unpack('<f',raw)[0]
    if not math.isfinite(value):return {'text_value':f'NONFINITE_NATIVE_FLOAT_WORD:{word:08x}','raw_word_u32':word,'value_status':'NONFINITE_FLOAT_NOT_NORMALIZED'}
    return {'real_value':value,'raw_word_u32':word,'value_status':'OBSERVED_FINITE_FLOAT32'}


def range_status(value,aliases):
    numeric=value.get('integer_value',value.get('real_value'))
    if numeric is None:return 'NOT_NUMERIC_FINITE'
    ranges=[(a.get('min'),a.get('max')) for a in aliases if 'min' in a or 'max' in a]
    if not ranges:return 'NO_REGISTERED_RANGE; GAME_RANGE_UNKNOWN'
    valid=all((low is None or numeric>=low) and (high is None or numeric<=high) for low,high in ranges)
    return 'WITHIN_REGISTERED_CANDIDATES_NOT_UI_CERTIFICATION' if valid else 'OUTSIDE_REGISTERED_CANDIDATE; RAW_RETAINED'


def slider_location(offset):
    if offset==0:return ('PRESET',None,None)
    for bank,start in (('CURRENT',4),('CUSTOM',1012)):
        if start<=offset<start+SLIDER_COUNT*8 and (offset-start)%4==0:
            i,rem=divmod(offset-start,8);return (bank,i,'USER' if rem==0 else 'CPU')
    return None


def collect_settings(reader):
    layout=catalog_layout();rvas=sorted({key[0] for key in layout}|{SLIDER_RVA});roots={};pointers={};blobs={};controls=[];gaps=[]
    for rva in rvas:
        raw=reader.read(reader.module_base+rva,8,f'SETTINGS_ROOT:{rva:x}');pointers[rva]=raw;roots[rva]=int.from_bytes(raw,'little')
        if roots[rva]==0:gaps.append({'target':f'SLOT:{rva:x}','reason':'Native global slot is NULL'})
    rows=[];covered=set()
    if roots[SLIDER_RVA]:
        table=bounded_block(reader,roots[SLIDER_RVA],2020,'SETTINGS_TUNEDATA_SAVED')
        blobs['tunedata-saved.bin']=table;controls.append((roots[SLIDER_RVA],table,'SETTINGS_TUNEDATA_RECHECK'))
        preset_aliases=layout.get((SLIDER_RVA,0,'uint32'),[])
        rows.append({'logical_key':'tunedata.preset','scope_code':'GLOBAL_PRESET','pointer_rva':SLIDER_RVA,'source_offset':0,
            'encoding':'uint32','aliases':preset_aliases,'semantic_status':'REGISTERED_PRESET_CODE_UI_LABEL_UNVERIFIED',**decode_word(table[:4],'uint32')})
        covered.add((SLIDER_RVA,0,'uint32'))
        for bank,start in (('CURRENT',4),('CUSTOM',1012)):
            for index in range(SLIDER_COUNT):
                for side,delta in (('USER',0),('CPU',4)):
                    offset=start+index*8+delta;aliases=layout.get((SLIDER_RVA,offset,'float'),[])
                    rows.append({'logical_key':f'tunedata.index_{index:03d}','scope_code':bank+':'+side,
                        'pointer_rva':SLIDER_RVA,'source_offset':offset,'encoding':'float','aliases':aliases,
                        'semantic_status':'REGISTERED_ALIAS_LAYOUT' if aliases else 'UNNAMED_SLIDER_INDEX_LAYOUT_ONLY',
                        **decode_word(table[offset:offset+4],'float')})
                    covered.add((SLIDER_RVA,offset,'float'))
    for (rva,offset,encoding),aliases in sorted(layout.items()):
        if (rva,offset,encoding) in covered or not roots[rva]:continue
        if not 0<=offset<=0x10000:raise ValueError('registered setting offset outside bounded envelope')
        raw=reader.read(roots[rva]+offset,4,f'SETTINGS_WORD:{rva:x}:{offset:x}:{encoding}')
        name=f'word-{rva:x}-{offset:x}-{encoding}.bin';blobs[name]=raw;controls.append((roots[rva]+offset,raw,'SETTINGS_WORD_RECHECK:'+name))
        rows.append({'logical_key':f'global.{rva:x}.{offset:x}.{encoding}','scope_code':'GLOBAL',
            'pointer_rva':rva,'source_offset':offset,'encoding':encoding,'aliases':aliases,
            'semantic_status':'REGISTERED_ALIAS_LAYOUT_NOT_CURRENT_UI_ACCEPTANCE',**decode_word(raw,encoding)})
    if not rows:raise ValueError('no settings source available')
    # Read actual native season code from a current TEAM_STATS control, not from
    # old profile targets or a game calendar guess.
    roster_pointer=reader.read(reader.module_base+ROSTER_RVA,8,'SETTINGS_ROSTER_POINTER');root=int.from_bytes(roster_pointer,'little')
    tdesc=reader.read(root+8*16,16,'SETTINGS_TEAM_DESCRIPTOR');sdesc=reader.read(root+28*16,16,'SETTINGS_TEAM_STATS_DESCRIPTOR')
    count,teams=struct.unpack('<QQ',tdesc);stats_count,stats=struct.unpack('<QQ',sdesc)
    if not 1<=count<=1024 or not 1<=stats_count<=10000:raise ValueError('season control descriptor invalid')
    season_control=None
    for i in range(count):
        addr=teams+i*4696;ident=reader.read(addr+0xCA8,2,'SETTINGS_TEAM_CONTROL_ID')
        if int.from_bytes(ident,'little')!=0:continue
        idxraw=reader.read(addr+0xE80,2,'SETTINGS_TEAM_CONTROL_STATS_INDEX');idx=int.from_bytes(idxraw,'little')
        if idx>=stats_count:raise ValueError('current TEAM stats index outside descriptor')
        season_control=reader.read(stats+idx*62,62,'SETTINGS_SEASON_CONTROL')
        controls.extend(((addr+0xCA8,ident,'SETTINGS_TEAM_CONTROL_ID_RECHECK'),(addr+0xE80,idxraw,'SETTINGS_TEAM_CONTROL_INDEX_RECHECK'),(stats+idx*62,season_control,'SETTINGS_SEASON_RECHECK')));break
    if season_control is None:raise ValueError('current season control unavailable')
    blobs['season-control.bin']=season_control;year=1900+season_control[4]
    for row in rows:row['registered_range_status']=range_status(row,row['aliases'])
    physical_types={}
    for row in rows:physical_types.setdefault((row['pointer_rva'],row['source_offset']),set()).add(row['encoding'])
    conflicts=[{'pointer_rva':rva,'offset':offset,'encodings':sorted(values)} for (rva,offset),values in physical_types.items() if len(values)>1]
    for address,raw,label in controls:
        if bounded_block(reader,address,len(raw),label)!=raw:raise ValueError('setting source changed during acquisition')
    for rva,raw in pointers.items():
        if reader.read(reader.module_base+rva,8,f'SETTINGS_ROOT_RECHECK:{rva:x}')!=raw:raise ValueError('setting root changed')
    for address,raw,label in ((reader.module_base+ROSTER_RVA,roster_pointer,'SETTINGS_ROSTER_RECHECK'),(root+8*16,tdesc,'SETTINGS_TEAM_DESCRIPTOR_RECHECK'),(root+28*16,sdesc,'SETTINGS_STATS_DESCRIPTOR_RECHECK')):
        if reader.read(address,len(raw),label)!=raw:raise ValueError('setting season context changed')
    return {'season_year':year,'roots':roots,'rows':rows,'missing_sources':gaps,'physical_type_conflicts':conflicts,
        'slider_pairs_per_bank':SLIDER_COUNT,'native_type_metadata_status':'REGISTERED_LAYOUT_ONLY_CURRENT_TYPE_DESCRIPTOR_NOT_YET_RESOLVED',
        'targets_defaults_applied':False,'game_writes':False,'player_struct_reads':0},blobs


def probe_settings(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_settings(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'settings-manifest.json',manifest)
        report.update({'status':'SETTINGS_SOURCE_CAPTURED','read_trace':reader.trace,'artifact_sha256':{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'SETTINGS_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'settings-report.json',report);return report


def settings_payload(binding,manifest,artifacts,observed_at,token):
    """Actual words, separately qualified layout aliases and season rule view.

    Float interpretation is not a normalized UI value. The global contract
    factor whose registered name contains 'potential' is an ordinary league
    setting; it carries no PLAYER value or PLAYER source read.
    """
    rows=manifest['rows'];year=manifest['season_year'];unit='settings:'+token
    if manifest.get('targets_defaults_applied') is not False or manifest.get('game_writes') is not False:
        raise ValueError('settings capture must be observation only')
    if manifest.get('player_struct_reads')!=0:raise ValueError('settings adapter cannot acquire PLAYER structs')
    identities=[(r['logical_key'],r['scope_code']) for r in rows]
    if len(identities)!=len(set(identities)):raise ValueError('duplicate setting identity/scope')
    layout=[{k:r[k] for k in ('logical_key','scope_code','pointer_rva','source_offset','encoding','aliases')} for r in rows]
    layout_hash=hashlib.sha256(json.dumps(layout,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:20]
    metadata={};facts={'native_fields':[],'game_setting_observations':[],'league_rule_observations':[],'field_gaps':[]}
    for row in rows:
        key=row['logical_key'];field_id=f'settings:{layout_hash}:{key}'
        meta=metadata.setdefault(key,{'field_id':field_id,'source_group':'RES-S','native_key':key,
            'evidence_grade':'REGISTERED_LAYOUT_OBSERVED_BYTES_UI_NOT_CERTIFIED','visibility':'GM_PUBLIC',
            'table_name':'game_setting_observations','codec':row['encoding']+'_LITTLE_ENDIAN_NO_SCALING',
            'layout_version':'REGISTERED_SETTINGS_V1:'+layout_hash,
            'source_ref':'config/state_io_native/world.json;settings.json;court.json; actual bounded word acquisition',
            'unit':'native uint32 word' if row['encoding']=='uint32' else 'native IEEE754 float32 without UI scaling',
            'legal_range_state':'UNKNOWN; registered candidates are not certified native/UI ranges',
            'null_meaning':'NOT_OBSERVED; nonfinite float uses diagnostic text and retains raw word'})
        if meta['codec']!=row['encoding']+'_LITTLE_ENDIAN_NO_SCALING':raise ValueError('conflicting logical setting codec')
        typed={k:row[k] for k in ('integer_value','real_value','text_value') if k in row}
        expected=decode_word(int(row['raw_word_u32']).to_bytes(4,'little'),row['encoding'])
        if typed!={k:expected[k] for k in ('integer_value','real_value','text_value') if k in expected} or row['value_status']!=expected['value_status']:
            raise ValueError('setting decoded value does not match raw word')
        if row['registered_range_status']!=range_status(typed,row['aliases']):raise ValueError('setting range annotation mismatch')
        aliases=[{k:v for k,v in a.items() if k in ('catalog','group','name','slot','encoding','min','max','unit','name_zh','status','side','native_token')} for a in row['aliases']]
        obs_id=f'{unit}:setting:{len(facts["game_setting_observations"])}'
        facts['game_setting_observations'].append({'setting_obs_id':obs_id,'field_id':field_id,'scope_code':row['scope_code'],
            'logical_key':key,'raw_word_u32':row['raw_word_u32'],'value_status':row['value_status'],
            'semantic_status':row['semantic_status'],'registered_range_status':row['registered_range_status'],
            'aliases_json':json.dumps(aliases,sort_keys=True,ensure_ascii=False,separators=(',',':')),**typed})
        if row['scope_code']=='GLOBAL' and any(a.get('slot')=='SLOT_TRADE' for a in aliases):
            facts['league_rule_observations'].append({'season_id':f'season:native-year:{year}',
                'rule_key':key,'setting_obs_id':obs_id,**typed})
    facts['native_fields']=list(metadata.values())
    gaps=[('RES-S','GLOBAL_SETTINGS_NATIVE_TYPES','Registered global slots read successfully; current NativeType descriptors not resolved','No current descriptor-level layout certification'),
        ('RES-S','UNNAMED_SLIDER_INDICES','Complete current/custom USER/CPU word tables acquired; most native index names unresolved','Unmapped indices are retained without invented labels'),
        ('RES-S','SETTINGS_UI_SCALE_RANGE_AND_EFFECT','Catalog candidates and raw native words are distinct; no current UI/effect or persistence acceptance','No clamping, scaling, optimal-value choice, or execution'),
        ('RES-L','LEAGUE_RULE_FULL_UI_COVERAGE','Only registered SLOT_TRADE words acquired; not every league/calendar rule has a mapped source','No inference from configured targets or external CBA rules')]
    if any('OUTSIDE_REGISTERED' in r['registered_range_status'] for r in rows):
        gaps.append(('RES-S','OBSERVED_WORD_OUTSIDE_REGISTERED_CANDIDATE','At least one actual word lies outside its catalog candidate range','Keep actual bytes/value; investigate candidate range or layout before claiming UI meaning'))
    for gap in manifest['missing_sources']:gaps.append(('RES-S',gap['target'],gap['reason'],'Source observations absent; never replaced with defaults'))
    if manifest['physical_type_conflicts']:gaps.append(('RES-S','REGISTERED_PHYSICAL_TYPE_CONFLICT','Multiple registered encodings for one physical word','Interpretations qualified separately; no authoritative UI type'))
    facts['field_gaps']=[dict(affected_domain=d,target_field=t,reason=r,impact=i) for d,t,r,i in gaps]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_SETTINGS_AND_RULES',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'REGISTERED_SETTINGS_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},
        'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_settings(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_settings(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'settings-manifest.json',manifest)
        report={'status':'SETTINGS_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,
            'game_writes':False,'player_struct_reads':0,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()},
            'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        _json(out/'settings-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'BOUNDED_SETTINGS_WORDS_OR_CONTROL','source_version':'REGISTERED_SETTINGS_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in [CATALOG_DIR/(name+'.json') for name in CATALOGS]+[Path(__file__)]:
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'REGISTERED_LAYOUT_OR_EXECUTED_READER','source_version':'REGISTERED_SETTINGS_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'settings-report.json').read_bytes()).hexdigest()[:24]
        payload=settings_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as c:status=ingest_capture(c,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'counts':{name:len(values) for name,values in payload['facts'].items()},'game_writes':False,'player_struct_reads':0,
            'native_type_metadata_status':manifest['native_type_metadata_status'],'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'SETTINGS_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_settings(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status']=='SETTINGS_SOURCE_CAPTURED' else 2)
