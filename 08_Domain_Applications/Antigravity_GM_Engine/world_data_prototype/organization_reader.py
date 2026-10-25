"""Read-only TEAM, reciprocal STAFF, current totals and coaching sources.

No legacy GameMemory attachment/executor is imported. The existing native coach
metadata verifier is reused through a bounded read-only adapter. PLAYER records
and hidden player Potential are never read by this source unit.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib,importlib.util,json,struct,sys,zlib
from pathlib import Path
from engine import connect,ingest_capture
from family_codec import extract_unsigned,decode_fixed_utf16
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import read_binding,bound_database,_json,_AcquisitionReceipt
from schedule_reader import collect_schedule,bounded_block
from readers import _module
from schema_model import DOMAIN,PROFILE,COACH_FIELD_COLUMNS

COACH_PROFILE_PATH=DOMAIN/'config/coach_tactics_profile.json'
COACH_PROFILE=json.loads(COACH_PROFILE_PATH.read_bytes())
CORE_IDS=set(range(7))|set(range(8,30))|{31}
TEAM_STRIDE=4696;STAFF_STRIDE=352
ROLE_SLOTS={role:0xCE8+role*8 for role in range(8)}
COACH_COLUMNS=COACH_FIELD_COLUMNS
FINANCE_OFFSETS={'total_salary_raw':0xCBC,'payroll_raw':0xFF4,'budget_raw':0x1014,'staff_budget_raw':0x1018,
    'cash_raw':0x1010,'gate_revenue_raw':0xFD8,'merch_revenue_raw':0xFDC,'media_revenue_raw':0xFE4}
TOTAL_MAP={'w':'wins','l':'losses','points':'points','pa':'opponent_points','made':'fg_made','attempted':'fg_attempted',
    '3pt_made':'three_made','3pt_attempted':'three_attempted','free_throws_made':'ft_made','free_throws_attempted':'ft_attempted',
    'offensive_rebounds':'offensive_rebounds','defensive_rebounds':'defensive_rebounds','assists':'assists',
    'steals':'steals','blocks':'blocks','foul':'fouls','turnover':'turnovers','poss':'possessions_raw',
    'pts_to':'points_off_turnovers','2ndpts':'second_chance_points','pip':'paint_points','bench':'bench_points','pace':'pace_raw',
    'ofgm':'opponent_fg_made','ofga':'opponent_fg_attempted','o3pm':'opponent_three_made','o3pa':'opponent_three_attempted'}


def registered_fields(raw,kind):
    return {f['name']:extract_unsigned(raw,f) for f in PROFILE['fields'][kind] if f['name']!='potential'}


def coach_values(raw):
    values={}
    for name,f in COACH_PROFILE['fields'].items():
        size=f['storage_bytes'];off=f['offset']
        if len(raw[off:off+size])!=size:raise ValueError('truncated coach field '+name)
        value=(int.from_bytes(raw[off:off+size],'little')>>f['start_bit'])&((1<<f['width'])-1)
        values[COACH_COLUMNS[name]]=str(value) if name.startswith('FreelanceType') else value
    return values


def verify_staff_assignment(raw,team_address,role):
    fields=registered_fields(raw,'STAFF')
    if struct.unpack_from('<Q',raw,0x18)[0]!=team_address or fields['position']!=role:
        raise ValueError('STAFF lacks reciprocal TEAM/role proof')
    return fields


class _ReadAdapter:
    def __init__(self,reader):self.reader=reader;self.pid=reader.pid;self.base_address=reader.module_base
    def read_bytes(self,address,size):return bounded_block(self.reader,address,size,'ORG_NATIVE_METADATA')


def native_metadata(reader):
    src=DOMAIN/'src';sys.path.insert(0,str(src))
    try:
        spec=importlib.util.spec_from_file_location('world_org_coach_locator',src/'coach_locator.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        locator=mod.CoachLocator(_ReadAdapter(reader),COACH_PROFILE)
        evidence=locator.verify_native()
        return evidence,locator.native_fields.get(zlib.crc32(b'UniqueId')),locator
    finally:sys.path.remove(str(src))


def reconcile_team(raw,season,team_id):
    totals=registered_fields(raw,'TEAM_STATS');year=1900+raw[4]
    if totals['points']!=2*totals['made']+totals['3pt_made']+totals['free_throws_made']:
        raise ValueError('TEAM_STATS scoring identity failed for '+str(team_id))
    decoder=_module('boxscore_decoder').BoxScoreDecoder;wins=losses=points=opponent=0;games=0
    for i,entry in enumerate(season['manifest']['entries']):
        if entry['status']!=2 or team_id not in (entry['home_team_id'],entry['away_team_id']):continue
        g=decoder.decode_game_header(season['games'][i*60:(i+1)*60])
        own,other=(g['home_score'],g['away_score']) if team_id==g['home_team_id'] else (g['away_score'],g['home_score'])
        if own==other:raise ValueError('final source has tied game')
        games+=1;wins+=own>other;losses+=own<other;points+=own;opponent+=other
    compared={'wins':(totals['w'],wins),'losses':(totals['l'],losses),'points':(totals['points'],points),'opponent_points':(totals['pa'],opponent)}
    if any(a!=b for a,b in compared.values()):raise ValueError('TEAM_STATS/schedule totals mismatch '+str(team_id)+': '+str(compared))
    if games!=totals['w']+totals['l']:raise ValueError('TEAM_STATS games mismatch')
    return {'season_year':year,'values':totals,'schedule_reconciliation':compared,'games':games}


def collect_organization(reader):
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'ORG_ROSTER_POINTER');root=struct.unpack('<Q',pointer)[0]
    specs={8:(1024,TEAM_STRIDE),19:(4096,STAFF_STRIDE),28:(10000,62)};descriptors={};decoded={}
    for slot,(maximum,stride) in specs.items():
        raw=reader.read(root+slot*16,16,f'ORG_SLOT{slot}_DESCRIPTOR');count,address=struct.unpack('<QQ',raw)
        if not 1<=count<=maximum:raise ValueError('descriptor outside organization envelope')
        descriptors[slot]=raw;decoded[slot]={'count':count,'address':address,'stride':stride}
    evidence,uid_field,locator=native_metadata(reader)
    season=collect_schedule(reader)
    if season['manifest']['errors'] or season['manifest']['duplicate_game_ids']:raise ValueError('current schedule does not pass source checks')
    blobs={};teams=[];staff=[];totals=[];controls=[];gaps=[]
    td=decoded[8];sd=decoded[19];ts=decoded[28]
    for i in range(td['count']):
        address=td['address']+i*TEAM_STRIDE;raw=bounded_block(reader,address,TEAM_STRIDE,f'ORG_TEAM:{i}')
        tid=int.from_bytes(raw[0xCA8:0xCAA],'little')
        if tid not in CORE_IDS:continue
        if any(t['native_team_id']==tid for t in teams):raise ValueError('duplicate core TEAM ID')
        name=decode_fixed_utf16(raw[0x2B4:0x2DC]);city=decode_fixed_utf16(raw[0x2E6:0x30A]);abb=decode_fixed_utf16(raw[0x30A:0x314])
        if not name or not city or not abb:raise ValueError('missing core TEAM public identity')
        team={'native_team_id':tid,'pool_index':i,'address':address,'name':name,'city':city,'abbreviation':abb,
              'finance':{key:int.from_bytes(raw[off:off+4],'little') for key,off in FINANCE_OFFSETS.items()},
              'chemistry_raw':struct.unpack_from('<f',raw,0xEC4)[0],'fan_interest_raw':struct.unpack_from('<f',raw,0xF7C)[0]}
        teams.append(team);blobs[f'team-{i}.bin']=raw;controls.append((address,raw,f'ORG_TEAM:{i}:RECHECK'))
        idx=int.from_bytes(raw[0xE80:0xE82],'little');team['current_stats_index']=idx
        if idx!=65535 and idx<ts['count']:
            stat=reader.read(ts['address']+idx*62,62,f'ORG_TEAM:{i}:CURRENT_STATS')
            total=reconcile_team(stat,season,tid);total.update({'native_team_id':tid,'stats_index':idx});totals.append(total)
            blobs[f'team-{i}.stats.bin']=stat;controls.append((ts['address']+idx*62,stat,f'ORG_TEAM:{i}:STATS_RECHECK'))
        else:gaps.append({'target':'TEAM_CURRENT_TOTAL:'+str(tid),'reason':'Current TEAM_STATS index absent/outside descriptor'})
        for role,off in ROLE_SLOTS.items():
            target=struct.unpack_from('<Q',raw,off)[0];index,rem=divmod(target-sd['address'],STAFF_STRIDE)
            if target==0:
                gaps.append({'target':f'TEAM_STAFF:{tid}:{role}','reason':'Null native role pointer'});continue
            if rem or not 0<=index<sd['count']:raise ValueError('TEAM staff role pointer outside STAFF descriptor')
            staff_raw=reader.read(target,STAFF_STRIDE,f'ORG_STAFF:{index}')
            values=verify_staff_assignment(staff_raw,address,role)
            first=decode_fixed_utf16(staff_raw[0x30:0x58]);last=decode_fixed_utf16(staff_raw[0x58:0x80])
            if not (first+' '+last).strip():raise ValueError('assigned STAFF name absent')
            uid=None
            if uid_field:
                width=(uid_field['format']>>8)&255;shift=(uid_field['format']>>16)&255
                if not 1<=width<=64:raise ValueError('STAFF native unique ID field width invalid')
                uid=(int.from_bytes(staff_raw[uid_field['offset']:uid_field['offset']+max(uid_field['size'],(shift+width+7)//8)],'little')>>shift)&((1<<width)-1)
            if any(s['pool_index']==index for s in staff):raise ValueError('STAFF record assigned to multiple current roles')
            staff.append({'pool_index':index,'native_staff_id':uid,'native_team_id':tid,'role_code':str(role),'first_name':first,'last_name':last,
                'fields':values,'coach_values':coach_values(staff_raw) if role==0 else None,
                'identity_status':'RECIPROCAL_CURRENT_TEAM_ROLE; NATIVE_LIFECYCLE_NOT_CERTIFIED'})
            blobs[f'staff-{index}.bin']=staff_raw;controls.append((target,staff_raw,f'ORG_STAFF:{index}:RECHECK'))
    if {t['native_team_id'] for t in teams}!=CORE_IDS:raise ValueError('current core TEAM set incomplete')
    years={t['season_year'] for t in totals}
    if len(years)!=1:raise ValueError('one native current season year not established')
    # Actual native PLAYBOOKDATA metadata verifies the 360-byte layout. Coach
    # PlaybookID is its loaded enum code, not the +0x3e native unique ID.
    n=COACH_PROFILE['native'];book_count=reader.read(root+n['playbook_count_offset'],8,'ORG_PLAYBOOK_COUNT')
    book_pointer=reader.read(root+n['playbook_pointer_offset'],8,'ORG_PLAYBOOK_POINTER')
    count=int.from_bytes(book_count,'little');base=int.from_bytes(book_pointer,'little')
    if not 1<=count<=4096:raise ValueError('playbook count outside bounded directory')
    enum=locator.enum_table(reader.module_base+COACH_PROFILE['fields']['PlaybookID']['enum_rva']);books=[]
    for i in range(count):
        raw=reader.read(base+i*360,360,f'ORG_PLAYBOOK:{i}')
        book={'pool_index':i,'name':decode_fixed_utf16(raw[:0x38]),'native_book_id':int.from_bytes(raw[0x3E:0x40],'little'),
              'enum_id':raw[0x54]&127,'play_crc_slots':list(struct.unpack_from('<68I',raw,0x58))}
        if book['enum_id'] not in enum or any(b['enum_id']==book['enum_id'] for b in books):raise ValueError('loaded playbook enum ambiguous or unknown')
        books.append(book);blobs[f'playbook-{i}.bin']=raw;controls.append((base+i*360,raw,f'ORG_PLAYBOOK:{i}:RECHECK'))
    for s in staff:
        if s['role_code']=='0' and not any(b['enum_id']==s['coach_values']['playbook_code_raw'] for b in books):
            raise ValueError('head coach playbook code not present in loaded directory')
    for address,data,label in controls:
        if bounded_block(reader,address,len(data),label)!=data:raise ValueError('organization source changed during acquisition')
    after=collect_schedule(reader)
    if any(season[k]!=after[k] for k in ('header','games','native_index','boxes')):raise ValueError('schedule changed during organization acquisition')
    for slot,data in descriptors.items():
        if reader.read(root+slot*16,16,f'ORG_SLOT{slot}_RECHECK')!=data:raise ValueError('organization descriptor changed')
    if reader.read(reader.module_base+ROSTER_RVA,8,'ORG_ROSTER_RECHECK')!=pointer:raise ValueError('roster context changed')
    if reader.read(root+n['playbook_count_offset'],8,'ORG_PLAYBOOK_COUNT_RECHECK')!=book_count or reader.read(root+n['playbook_pointer_offset'],8,'ORG_PLAYBOOK_POINTER_RECHECK')!=book_pointer:
        raise ValueError('playbook directory changed')
    for key in ('header','games','native_index'):blobs['schedule-'+key+'.bin']=season[key]
    for i,data in season['boxes'].items():blobs[f'schedule-box-{i}.bin']=data
    manifest={'descriptors':decoded,'teams':teams,'staff':staff,'team_totals':totals,'gaps':gaps,
        'native_metadata':evidence,'native_staff_uid_field':uid_field,'season_year':next(iter(years)),
        'schedule_status_counts':season['manifest']['status_counts'],'staff_uid_duplicates':{str(k):v for k,v in Counter(s['native_staff_id'] for s in staff).items() if v>1},
        'playbooks':books,'game_writes':False,'player_struct_reads':0,'player_potential_bytes_read':0}
    return manifest,blobs


def probe_organization(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_organization(reader);reader.close()
        for name,data in blobs.items():(out/name).write_bytes(data)
        _json(out/'organization-manifest.json',manifest)
        report.update({'status':'ORGANIZATION_SOURCE_CAPTURED','read_trace':reader.trace,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'ORGANIZATION_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
                       'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'organization-report.json',report);return report


def organization_payload(binding,manifest,artifacts,observed_at,token):
    """Typed transform; research-grade until the direct reader supplies receipt."""
    year=manifest['season_year'];season={'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'}
    tid=lambda n:'team:native:'+str(n)
    uid_counts=Counter(s['native_staff_id'] for s in manifest['staff'])
    if None in uid_counts or any(count!=1 for count in uid_counts.values()):raise ValueError('assigned STAFF native identity not unique')
    facts={name:[] for name in ('teams','team_seasons','team_finance_observations','team_state_observations','team_season_totals',
        'staff_members','staff_team_assignments','staff_contract_observations','staff_skill_observations','coach_preferences','team_tactic_settings','team_playbook_slots')}
    for t in manifest['teams']:
        team=tid(t['native_team_id'])
        facts['teams'].append({'team_id':team,'native_team_id':str(t['native_team_id']),
            'display_name':(t['city']+' '+t['name']).strip(),'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
        facts['team_seasons'].append({'team_id':team,'season_id':season['season_id'],'team_name':t['name']})
        facts['team_finance_observations'].append({'team_id':team,**t['finance']})
        facts['team_state_observations'].append({'team_id':team,'chemistry_raw':t['chemistry_raw'],'fan_interest_raw':t['fan_interest_raw']})
    for t in manifest['team_totals']:
        facts['team_season_totals'].append({'team_id':tid(t['native_team_id']),'season_id':season['season_id'],'is_final':0,
            'phase_code':None,**{new:t['values'][old] for old,new in TOTAL_MAP.items()}})
    books={b['enum_id']:b for b in manifest.get('playbooks',[])}
    for s in manifest['staff']:
        sid='staff:native:'+str(s['native_staff_id']);team=tid(s['native_team_id']);fields=s['fields']
        facts['staff_members'].append({'staff_id':sid,'native_staff_id':str(s['native_staff_id']),
            'display_name':(s['first_name']+' '+s['last_name']).strip(),'identity_state':'UNIQUE_ASSIGNED_NATIVE_ID_AND_RECIPROCAL_TEAM_ROLE'})
        facts['staff_team_assignments'].append({'staff_id':sid,'team_id':team,'role_code':s['role_code']})
        facts['staff_contract_observations'].append({'staff_id':sid,'salary_raw':fields['salary'],'years_left':fields['years_left']})
        facts['staff_skill_observations'].append({'staff_id':sid,**{k+'_raw':fields[k] for k in ('offense','defense','contracts','trading','scouting','training','business')}})
        if s['role_code']=='0':
            coach=s['coach_values'];facts['coach_preferences'].append({'staff_id':sid,'preferred_system_raw':coach['preferred_system_raw'],'active_system_raw':coach['active_system_raw']})
            facts['team_tactic_settings'].append({'team_id':team,**coach})
            if coach['playbook_code_raw'] not in books:raise ValueError('coach playbook missing from current loaded directory')
            book=books[coach['playbook_code_raw']]
            facts['team_playbook_slots'].extend({'team_id':team,'slot_index':i,'play_code':f'{crc:08x}',
                'play_name':None,'playbook_native_id':str(book['native_book_id'])} for i,crc in enumerate(book['play_crc_slots']))
    facts['field_gaps']=[{'affected_domain':domain,'target_field':target,'reason':reason,'impact':impact} for domain,target,reason,impact in (
        ('RES-M','FINANCE_UI_UNITS_AND_CASH_SIGN','Registered TEAM uint32 fields read; current UI meaning/sign not observed','Keep unsigned raw values; no spending/cap inference'),
        ('RES-M','CAP_SPACE_LUXURY_TAX_AND_HARD_CAP','No accepted current source offset in this adapter','Fields remain NULL; no external CBA arithmetic substituted'),
        ('RES-C','PLAY_NAMES_FROM_NATIVE_CRCS','Ordered loaded book CRC slots observed, text labels not acquired','Keep native CRC text and NULL play_name'),
        ('RES-C','TEAM_TRAINING_AND_MENTORSHIP','This unit reads assigned staff/default tactics, not training/mentor objects','No fabricated settings or relations'),
        ('RES-C','STAFF_MARKET_AND_LIFECYCLE','Current assigned unique IDs/reciprocal roles proved; unassigned pool availability and lifecycle not certified','No free-agent status inferred from missing team'))]
    facts['field_gaps'].extend({'affected_domain':'RES-C','target_field':g['target'],'reason':g['reason'],'impact':'Missing source family stays unobserved'} for g in manifest['gaps'])
    unit='organization:'+token
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_CORE_ORGANIZATION',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'CORE_ORGANIZATION_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':season,'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_organization(pid,save_directory,loaded_filename,new_output_directory):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_organization(reader);reader.close()
        for name,data in blobs.items():(out/name).write_bytes(data)
        _json(out/'organization-manifest.json',manifest)
        report={'status':'ORGANIZATION_LIVE_SOURCE_CAPTURED','observed_at':stamp,'pid':pid,'save_id':binding['save_id'],
            'native_save_filename':loaded_filename,'binding_sha256':binding_hash,'read_trace':reader.trace,'game_writes':False,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'organization-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'ACTUAL_ORGANIZATION_WINDOWS_SOURCE','source_version':'CORE_ORGANIZATION_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (COACH_PROFILE_PATH,DOMAIN/'config/memory_field_profile.json',DOMAIN/'src/config.py',DOMAIN/'src/coach_locator.py'):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'REGISTERED_OR_NATIVE_METADATA_VERIFIER','source_version':'CORE_ORGANIZATION_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'organization-report.json').read_bytes()).hexdigest()[:24]
        payload=organization_payload(binding,manifest,artifacts,stamp,token);payload['evidence_grade']='LIVE_READ'
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'native_save_filename':loaded_filename,
            'source_grade':'LIVE_READ','counts':{k:len(v) for k,v in payload['facts'].items()},
            'native_metadata':manifest['native_metadata'],'team_totals_reconciled':len(manifest['team_totals']),
            'loaded_playbooks':len(manifest['playbooks']),'game_writes':False,'player_struct_reads':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'ORGANIZATION_CAPTURE_OR_INGEST_FAILED','reason':str(error),'error_type':type(error).__name__,
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_organization(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status']=='ORGANIZATION_SOURCE_CAPTURED' else 2)
