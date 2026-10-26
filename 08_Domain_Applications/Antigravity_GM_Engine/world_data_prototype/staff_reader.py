"""Complete bounded COACHDATA public source pool; no game writes or PLAYER reads."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from award_reader import read_native_fields
from league_reader import read_native_enum
from game_mode_reader import collect_game_mode
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from family_codec import decode_fixed_utf16
from engine import connect,ingest_capture

PROFILE_PATH=Path(__file__).with_name('staff_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout'];CORE_IDS=set(range(7))|set(range(8,30))|{31}


def bit_value(raw,f):
    off,shift,width=f['offset'],f['start_bit'],f['width'];size=(shift+width+7)//8
    if not 1<=width<=32 or off+size>len(raw):raise ValueError('staff field outside source')
    return int.from_bytes(raw[off:off+size],'little')>>shift&((1<<width)-1)


def staff_projection_ranges():
    ranges=[(24,48),(48,128),(216,218)]
    for spec in PROFILE['fields'].values():ranges.append(tuple(spec['byte_range']))
    for name in ('PersonType','Status'):
        f=PROFILE['identity'][name];ranges.append((f['offset']+f['start_bit']//8,f['offset']+(f['start_bit']+f['width']+7)//8))
    merged=[]
    for a,b in sorted(ranges):
        if not 0<=a<b<=352 or any(a<hi and lo<b for lo,hi in PROFILE['excluded_staff_byte_ranges']):raise ValueError('staff projection includes omitted growth/max-grade bytes')
        if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else:merged.append((a,b))
    if any(a<216 and 136<b for a,b in merged):raise ValueError('ordinary staff source must not acquire annual SeasonStats references')
    return merged


def decode_staff_fields(raw):
    if len(raw)!=352:raise ValueError('staff decoder requires reconstructed352-byte source')
    result={'profile':{},'tactics':{}}
    for spec in PROFILE['fields'].values():
        f=spec['binding'];value=bit_value(raw,f);column=spec['column'];row=result[spec['group']]
        if spec['primitive']=='int':row[column+'_bits_raw']=value;row[column+'_signed']=value-(1<<f['width']) if value&(1<<(f['width']-1)) else value
        else:row[column+'_raw']=value
        if spec['enum']:row[column+'_label']=PROFILE['enum_labels'][spec['enum']].get(str(value),{}).get('label')
    return result


def verify_staff_metadata(reader):
    evidence=[]
    for entry in PROFILE['types']:
        name=entry['name']
        if name in PROFILE['enum_labels']:
            value=read_native_enum(reader,entry);expected={(int(k),v['name_crc']) for k,v in PROFILE['enum_labels'][name].items()}
            if len(value['values'])!=len(expected) or {(v['value'],v['name_crc']) for v in value['values']}!=expected:raise ValueError('Native staff enum changed')
        else:
            value=read_native_fields(reader,entry,352 if name=='COACHDATA' else 4696,read_enums=False);native={f['name_crc']:f for f in value['fields']}
            specs=PROFILE['identity']|{n:s['binding'] for n,s in PROFILE['fields'].items()}|PROFILE['excluded_staff_grade_fields'] if name=='COACHDATA' else {n:s['binding'] for n,s in PROFILE['team_identity'].items()}|{'Coach_Internal':PROFILE['team_coach_array']}
            for field_name,old in specs.items():
                current=native[old['name_crc']]
                if current['words'][1]!=old['words'][1]:raise ValueError('Native staff primitive changed')
                if old['enum_pointer'] and current['enum_pointer']!=reader.module_base+old['enum_pointer']-0x140000000:raise ValueError('Native staff nested binding changed')
                extent=PROFILE['name_extents'].get(field_name) if name=='COACHDATA' else PROFILE['team_identity'].get(field_name,{}).get('extent')
                if extent is not None or field_name=='Coach_Internal':
                    w=current['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'STAFF_ARRAY_DIMENSION:'+field_name);expected_extent=8 if field_name=='Coach_Internal' else extent;expected_stride=8 if field_name=='Coach_Internal' else 2
                    if w[5]>>16!=1 or struct.unpack_from('<I',raw)[0]!=expected_extent or struct.unpack_from('<Q',raw,8)[0]!=expected_stride:raise ValueError('Native staff name/role array extent or stride changed')
                    if reader.read(ptr,24,'STAFF_ARRAY_DIMENSION_RECHECK:'+field_name)!=raw:raise ValueError('Native staff array control changed')
                    current['runtime_dimension_control_hex']=raw.hex()
            if name=='COACHDATA':
                omitted=[]
                for old in PROFILE['excluded_staff_grade_fields'].values():
                    f=native[old['name_crc']];omitted.append((f['offset']+f['start_bit']//8,f['offset']+(f['start_bit']+f['width']+7)//8))
                merged=[]
                for a,b in sorted(omitted):
                    if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
                    else:merged.append((a,b))
                if merged!=[tuple(x) for x in PROFILE['excluded_staff_byte_ranges']]:raise ValueError('omitted staff grade-byte layout changed')
        evidence.append(value)
    return evidence


def resolve_pool_pointer(pointer,directory,stride):
    if pointer==0:return None,'NULL_POINTER'
    index,remainder=divmod(pointer-directory['address'],stride)
    if not 0<=index<directory['count']:return None,'OUTSIDE_CURRENT_POOL'
    if remainder:return None,'MISALIGNED_POOL_POINTER'
    return index,'CURRENT_POOL_REFERENT'


def classify_staff_assignments(staff,slots):
    references=defaultdict(list)
    for slot in slots:
        i=slot['source_staff_index'];slot['reciprocal_status']='NO_ACCEPTED_STAFF_REFERENT'
        if i is None:continue
        references[i].append(slot);row=staff[i];same=row['current_team_core_id']==slot['native_team_id'] and row['person_type_raw']==slot['role_slot_index'];slot['reciprocal_status']='RECIPROCAL_CURRENT_TEAM_ROLE' if same else 'CURRENT_STAFF_REFERENT_WITH_TEAM_OR_TYPE_MISMATCH'
    for i,row in enumerate(staff):
        refs=references[i];row.update(core_slot_reference_count=len(refs),assigned_core_team_id=None,assigned_role_slot=None)
        if len(refs)>1:row['assignment_status']='MULTIPLE_CORE_ROLE_REFERENCES_CANONICAL_WITHHELD'
        elif len(refs)==1 and refs[0]['reciprocal_status']=='RECIPROCAL_CURRENT_TEAM_ROLE':row.update(assignment_status='RECIPROCAL_CURRENT_TEAM_ROLE',assigned_core_team_id=refs[0]['native_team_id'],assigned_role_slot=refs[0]['role_slot_index'])
        elif refs:row['assignment_status']='CORE_ROLE_REFERENCE_WITH_TEAM_OR_TYPE_MISMATCH'
        else:row['assignment_status']='NO_CORE_ROLE_REFERENCE'


def collect_staff(reader):
    mode,blobs=collect_game_mode(reader);mode_blobs=dict(blobs);metadata=verify_staff_metadata(reader);controls=[]
    def read(address,size,label):
        value=reader.read(address,size,label);controls.append((address,value,label));return value
    pointer=read(reader.module_base+ROSTER_RVA,8,'STAFF_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    if root<0x10000:raise ValueError('staff roster root absent')
    directories={}
    for slot,maximum,stride in ((8,1024,4696),(19,4096,352)):
        raw=read(root+slot*16,16,f'STAFF_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 0<=count<=maximum or count and address<0x10000:raise ValueError('staff directory outside bounded envelope')
        directories[slot]={'count':count,'address':address,'stride':stride}
    td=directories[8];sd=directories[19];team_ids={};core={};teams=[];slots=[]
    for i in range(td['count']):
        address=td['address']+i*4696;tid=int.from_bytes(read(address+3240,2,f'STAFF_TEAM_ID:{i}'),'little');team_ids[i]=tid
        if tid not in CORE_IDS:continue
        if tid in core:raise ValueError('duplicate current core TEAM ID')
        core[tid]=i;names={}
        for native,key in (('UnlocalizedTeamName','name'),('UnlocalizedCityName','city')):
            spec=PROFILE['team_identity'][native];raw=read(address+spec['binding']['offset'],spec['extent']*2,f'STAFF_TEAM_NAME:{tid}:{key}');names[key]=decode_fixed_utf16(raw)
            if not names[key]:raise ValueError('staff team public identity name absent')
        role_bytes=read(address+PROFILE['team_coach_array']['offset'],64,f'STAFF_CORE_ROLE_ARRAY:{tid}');blobs[f'team-{tid}.staff-roles.bin']=role_bytes
        for role,target in enumerate(struct.unpack('<8Q',role_bytes)):
            index,status=resolve_pool_pointer(target,sd,352);slots.append({'native_team_id':tid,'role_slot_index':role,'source_staff_index':index,'pointer_status':status})
        teams.append({'native_team_id':tid,'pool_index':i,**names})
    if set(core)!=CORE_IDS:raise ValueError('staff current core team set incomplete')
    def team_reference(target):
        index,status=resolve_pool_pointer(target,td,4696);tid=None if index is None else team_ids[index];core_id=tid if tid in core and core[tid]==index else None
        return {'native_team_id':tid,'core_id':core_id,'pointer_status':status if index is None else ('CURRENT_CORE_TEAM_POINTER' if core_id is not None else 'CURRENT_NONCORE_TEAM_POOL_POINTER')}
    ranges=staff_projection_ranges();staff=[];parts=[]
    for i in range(sd['count']):
        raw=bytearray(352);pieces=[]
        for a,b in ranges:
            value=read(sd['address']+i*352+a,b-a,f'STAFF_PUBLIC_PROJECTION:{i}:{a}');raw[a:b]=value;pieces.append(value)
        parts.append(b''.join(pieces));names={};bad=False
        for name,key in (('FirstName','first_name'),('LastName','last_name')):
            off=PROFILE['identity'][name]['offset']
            try:names[key]=decode_fixed_utf16(raw[off:off+40]) or None
            except UnicodeDecodeError:names[key]=None;bad=True
        observed=' '.join(n for n in (names['first_name'],names['last_name']) if n) or None;refs={name:team_reference(struct.unpack_from('<Q',raw,PROFILE['identity'][native]['offset'])[0]) for name,native in (('current_team','CurrentTeam_Internal'),('previous_team','PreviousTeam'),('myteam_team','MyTeamTeam'))};person=bit_value(raw,PROFILE['identity']['PersonType']);status=bit_value(raw,PROFILE['identity']['Status'])
        staff.append({'source_staff_index':i,'native_staff_id_raw':bit_value(raw,PROFILE['identity']['UniqueId']),**names,'observed_name':observed,'name_status':'INVALID_UTF16_PREFIX' if bad else 'OBSERVED_UTF16' if observed else 'EMPTY_NATIVE_NAME','person_type_raw':person,'person_type_label':PROFILE['enum_labels']['COACHDATA_PERSONTYPE'].get(str(person),{}).get('label'),'status_raw':status,'status_label':PROFILE['enum_labels']['COACHDATA_STATUS'].get(str(status),{}).get('label'),**{name+'_native_id_raw':ref['native_team_id'] for name,ref in refs.items()},**{name+'_pointer_status':ref['pointer_status'] for name,ref in refs.items()},'current_team_core_id':refs['current_team']['core_id'],**decode_staff_fields(raw)})
    classify_staff_assignments(staff,slots);blobs['staff-public-projections.bin']=b''.join(parts)
    for address,value,label in controls:
        if reader.read(address,len(value),label+':RECHECK')!=value:raise ValueError('staff source/role/directory changed during capture')
    after,after_blobs=collect_game_mode(reader)
    if after['season_year']!=mode['season_year'] or after['observation']!=mode['observation'] or after_blobs!=mode_blobs:raise ValueError('staff game-mode context changed')
    return {'season_year':mode['season_year'],'game_mode':mode['observation'],'metadata':metadata,'directories':directories,'teams':teams,'team_pool_native_ids':team_ids,'staff':staff,'team_slots':slots,'projection_ranges':ranges,'projection_bytes':sum(b-a for a,b in ranges),'excluded_staff_byte_ranges':PROFILE['excluded_staff_byte_ranges'],'staff_annual_stat_references_read':0,'player_value_reads':0,'game_writes':False,'getter_invocations':0},blobs


def staff_payload(binding,m,artifacts,stamp,token,canonical=None):
    canonical=canonical or {};unit='native-staff:'+token;staff=m['staff'];directory=m['directories'].get(19,m['directories'].get('19'));uid=Counter(s['native_staff_id_raw'] for s in staff);source_ids={};linked={};sid=f'season:native-year:{m["season_year"]}'
    if m.get('game_writes') is not False or m.get('player_value_reads')!=0 or m.get('staff_annual_stat_references_read')!=0 or len(staff)!=directory['count'] or {s['source_staff_index'] for s in staff}!=set(range(len(staff))):raise ValueError('incomplete/nonpublic staff source')
    if len(m['teams'])!=30 or {t['native_team_id'] for t in m['teams']}!=CORE_IDS or len(m['team_slots'])!=240 or {(r['native_team_id'],r['role_slot_index']) for r in m['team_slots']}!={(tid,slot) for tid in CORE_IDS for slot in range(8)}:raise ValueError('incomplete current TEAM staff slot context')
    facts={name:[] for name in ('teams','native_staff_sources','native_staff_profile_observations','native_staff_tactic_observations','native_staff_team_slots')};facts['game_mode_observations']=[{'season_id':sid,**m['game_mode']}]
    for team in m['teams']:facts['teams'].append({'team_id':'team:native:'+str(team['native_team_id']),'native_team_id':str(team['native_team_id']),'display_name':team['city']+' '+team['name'],'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
    for row in staff:
        i=row['source_staff_index'];candidate='staff:native:'+str(row['native_staff_id_raw']);accepted=row['assignment_status']=='RECIPROCAL_CURRENT_TEAM_ROLE' and uid[row['native_staff_id_raw']]==1 and row['name_status']=='OBSERVED_UTF16' and canonical.get(candidate)==row['observed_name'];linked[i]=candidate if accepted else None;source_ids[i]=f'{unit}:staff:{i}'
        source={k:v for k,v in row.items() if k not in ('profile','tactics','current_team_core_id','assigned_core_team_id')};source.update(staff_source_id=source_ids[i],staff_id=linked[i],current_core_team_id='team:native:'+str(row['current_team_core_id']) if row['current_team_core_id'] is not None else None,assigned_core_team_id='team:native:'+str(row['assigned_core_team_id']) if row['assigned_core_team_id'] is not None else None,canonical_link_status='CURRENT_RECIPROCAL_ROLE_UNIQUE_NATIVE_ID_AND_EXACT_NAME; LIFECYCLE_UNPROVED' if accepted else 'SOURCE_ONLY_CANONICAL_LINK_WITHHELD');facts['native_staff_sources'].append(source)
        for group,table in (('profile','native_staff_profile_observations'),('tactics','native_staff_tactic_observations')):
            expected=set()
            for spec in PROFILE['fields'].values():
                if spec['group']!=group:continue
                column=spec['column'];expected.update((column+'_bits_raw',column+'_signed') if spec['primitive']=='int' else (column+'_raw',))
                if spec['enum']:expected.add(column+'_label')
            if set(row[group])!=expected:raise ValueError('incomplete Native staff '+group+' fields')
            facts[table].append({'source_staff_id':source_ids[i],**row[group]})
    for slot in m['team_slots']:
        i=slot['source_staff_index'];facts['native_staff_team_slots'].append({'team_id':'team:native:'+str(slot['native_team_id']),'role_slot_index':slot['role_slot_index'],'source_staff_id':source_ids[i] if i is not None else None,'pointer_status':slot['pointer_status'],'reciprocal_status':slot['reciprocal_status']})
    facts['field_gaps']=[{'affected_domain':'RES-C','target_field':target,'reason':reason,'impact':impact} for target,reason,impact in (
        ('STAFF_POOL_ALLOCATION_LIFECYCLE_AND_HIRING','Descriptor slots, Native status enums, team pointers and role slots are independently observed','No unnamed slot is invented as a person; no absent core slot or NORMAL/RELEASED status is declared legally hireable'),
        ('STAFF_UI_WAGES_GRADES_AND_BEHAVIOR',PROFILE['units'],'Raw fields/labels and signed-width interpretations remain separate from UI scale, sentinel meaning and game effects'),
        ('STAFF_GROWTH_AND_SHARED_BYTE_PUBLIC_SCOPE',PROFILE['privacy_scope'],'No Potential-key ingestion exception is introduced; omitted max/growth fields and shared TightLipped are not reconstructed'),
        ('ANNUAL_STAFF_SEASON_STATS',PROFILE['ordinary_annual_separation'],'No ordinary source acquires/repopulates the annual historical stats family'),
        ('STAFF_REFERENCED_PLAYER_AND_SIGNATURE_NAMESPACES','Stored player/signature/graphic/audio identifiers are raw Native values without accepted person/object namespace bindings','No name-based or numeric-only PLAYER link, rendered signature or portrait is fabricated'))]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_NATIVE_COMPLETE_PUBLIC_STAFF_POOL','observed_at':stamp,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':LAYOUT,'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],'season':{'season_id':sid,'season_code':f'NATIVE_YEAR:{m["season_year"]}'},'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_staff(pid,save_directory,loaded_filename,new_output_directory):
    binding,bhash=read_binding(save_directory,loaded_filename);out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);m,blobs=collect_staff(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'staff-manifest.json',m);_json(out/'staff-report.json',{'status':'COMPLETE_NATIVE_PUBLIC_STAFF_POOL_AND_ROLE_POINTERS_CAPTURED','observed_at':stamp,'pid':pid,'binding_sha256':bhash,'read_trace':reader.trace,'game_writes':False,'getter_invocations':0,'player_value_reads':0,'staff_annual_stat_references_read':0})
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'ACTUAL_NATIVE_PUBLIC_STAFF_POOL_SOURCE','source_version':LAYOUT,'payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        for p in (PROFILE_PATH,Path(__file__).with_name('game_mode_native_profile.json'),Path(__file__).with_name('calendar_native_profile.json')):artifacts.append({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,'payload_kind':'REGISTERED_NATIVE_STAFF_AND_MODE_LAYOUT','source_version':LAYOUT,'payload_ref':'world_data_prototype/'+p.name})
        token=hashlib.sha256((out/'staff-report.json').read_bytes()).hexdigest()[:24]
        with connect(bound_database(save_directory,binding)) as c:
            canonical={r['staff_id']:r['display_name'] for r in c.execute('SELECT staff_id,display_name FROM staff_members')};payload=staff_payload(binding,m,artifacts,stamp,token,canonical);payload['evidence_grade']='LIVE_READ';status=ingest_capture(c,payload,_live_receipt=_AcquisitionReceipt(payload,reader))
        result={'status':status,'unit_id':payload['unit_id'],'counts':{k:len(v) for k,v in payload['facts'].items()},'source_grade':'LIVE_READ','game_writes':False,'getter_invocations':0,'player_value_reads':0,'annual_history_refreshed':False,'full_goal_complete':False};_json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'STAFF_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
