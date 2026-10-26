"""One explicitly invoked, serial world refresh over the existing live adapters."""
from contextlib import closing
from datetime import datetime,timezone
import ctypes,hashlib,importlib,json,struct,uuid
from pathlib import Path
from cadence import observed_game_season_year,annual_status
from engine import connect
from live_reader import ReadOnlyGameProcess
from live_world import read_binding,bound_database
from schema_model import VERSION
from process_session import resolve_pid,owner_identity,owner_is_live

# Ordered source dependencies: schedule establishes current player/team identities.
SOURCES={
    'schedule':('schedule_reader','capture_season','BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS',None),
    'game-mode':('game_mode_reader','capture_game_mode','BOUND_NATIVE_GAME_MODE_PERIOD',None),
    'period-stats':('period_stats_reader','capture_period_stats','BOUND_NATIVE_CURRENT_PERIOD_PLAYER_STATS',None),
    'organization':('organization_reader','capture_organization','BOUND_CORE_ORGANIZATION',None),
    'staff':('staff_reader','capture_staff','BOUND_NATIVE_COMPLETE_PUBLIC_STAFF_POOL',None),
    'coach-stats':('current_coach_stat_reader','capture_current_coach_stats','BOUND_NATIVE_CURRENT_COACH_STATS',None),
    'lineups':('lineup_reader','capture_lineups','BOUND_NATIVE_TEAM_LINEUPS_AND_PLAYER_ROTATION',None),
    'finance':('finance_reader','capture_finance','BOUND_NATIVE_TYPED_TEAM_FINANCE',None),
    'market':('market_reader','capture_market','BOUND_NATIVE_MARKET_SOURCES',None),
    'planning':('planning_reader','capture_planning','BOUND_PLANNING_AND_TRAINING',None),
    'settings':('settings_reader','capture_settings','BOUND_SETTINGS_AND_RULES',None),
    'player-details':('player_detail_reader','capture_player_details','BOUND_PLAYER_CONTRACT_AND_BASE_BADGES',None),
    'player-state':('player_state_reader','capture_player_state','BOUND_PLAYER_VITALS_HEALTH_MORALE',None),
    'affiliations':('player_affiliation_reader','capture_player_affiliations','BOUND_PLAYER_AFFILIATION_CLASSIFICATION',None),
    'player-skills':('player_skill_reader','capture_player_skills','BOUND_PUBLIC_PLAYER_SKILLS',None),
    'news':('league_ingest','capture_league','BOUND_NATIVE_NEWS_AND_TRANSACTIONS',None),
    'records':('records_reader','capture_records','BOUND_RECORD_BOOK','RECORD_BOOK'),
    'honors':('award_reader','capture_native_honors','BOUND_NATIVE_HONOR_STATS','NATIVE_HONOR_STATS'),
    'league-history':('league_ingest','capture_league','BOUND_LEAGUE_HISTORY_AND_AWARDS','LEAGUE_HISTORY_AWARDS'),
    'staff-history':('staff_history_reader','capture_staff_history','BOUND_NATIVE_ANNUAL_STAFF_STATS','STAFF_SEASON_HISTORY'),
}

class RefreshFailed(RuntimeError):
    def __init__(self,report):
        self.report=report
        super().__init__('world refresh stopped; completed source units retained; inspect '+report['report_file'])

def _stamp():return datetime.now(timezone.utc).isoformat(timespec='microseconds')

def _write(path,value):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n');temporary.replace(path)

def _context(pid):
    """Fresh read-only handle/root resolution; process creation time detects PID reuse."""
    reader=ReadOnlyGameProcess(pid)
    try:
        from ctypes import wintypes
        times=[wintypes.FILETIME() for _ in range(4)];fn=reader.k.GetProcessTimes
        fn.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;fn.restype=wintypes.BOOL
        if not fn(reader.handle,*(ctypes.byref(value) for value in times)):raise ctypes.WinError(ctypes.get_last_error())
        created=(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime
        reader.trace.append({'operation':'GetProcessTimes','pid':pid,'creation_filetime':created,'success':True})
        dos=reader.read(reader.module_base,64,'REFRESH_DOS_HEADER')
        if dos[:2]!=b'MZ':raise ValueError('unsupported game DOS header')
        offset=struct.unpack_from('<I',dos,60)[0]
        if not 64<=offset<=reader.module_size-24:raise ValueError('game PE header outside module')
        pe=reader.read(reader.module_base+offset,24,'REFRESH_PE_HEADER')
        if pe[:4]!=b'PE\0\0' or struct.unpack_from('<H',pe,4)[0]!=0x8664 or struct.unpack_from('<I',pe,8)[0]!=1652287197:raise ValueError('unsupported game executable build')
        year=observed_game_season_year(reader)
        from game_mode_reader import collect_game_mode
        mode,_=collect_game_mode(reader)
        if mode['season_year']!=year:raise ValueError('game season changed while reconnecting')
        # Public Native date/stage are progress evidence, never loaded-save proof.
        keys=('today_native_iso_date','today_minutes_since_midnight_raw','period_raw','mode_raw','league_raw','current_year_byte_raw','draft_year_byte_raw')
        progress={key:mode['observation'][key] for key in keys if key in mode['observation']}
        if not progress.get('today_native_iso_date'):raise ValueError('current Native game date unavailable')
        return {'epoch':{'pid':reader.pid,'creation_filetime':created,'module_base':hex(reader.module_base),'module_size':reader.module_size,'pe_timestamp':1652287197,'game_season_year':year},'game_progress':progress,'read_trace':reader.trace}
    finally:reader.close()

def _capture(family,pid,save_directory,loaded_filename,directory):
    module,function,_,_=SOURCES[family];kwargs={}
    if family in ('news','league-history'):kwargs['mode']='NEWS_TRANSACTIONS' if family=='news' else 'HISTORY_AWARDS'
    return getattr(importlib.import_module(module),function)(pid,save_directory,loaded_filename,directory,**kwargs)

def _unit_receipt(database,result,family,year):
    """Adapter return strings alone never prove acquisition or annual skip."""
    _,_,source,annual=SOURCES[family];skipped=result.get('status')=='already_refreshed'
    if skipped and annual is None:raise ValueError('ordinary source cannot claim annual skip')
    if not skipped and result.get('status') not in ('ingested','already_applied'):raise ValueError('adapter did not report successful ingestion')
    key=result.get('previous_unit_id' if skipped else 'unit_id')
    with closing(connect(database,True)) as conn:
        unit=conn.execute('''SELECT u.unit_id,u.source_key,u.payload_sha256,u.unit_status,u.observed_at,u.completeness,r.source_grade,r.refresh_family,r.refresh_period_year,s.season_id,s.season_code
            FROM capture_units u JOIN capture_runs r USING(run_id) JOIN seasons s USING(season_id) WHERE u.unit_id=?''',(key,)).fetchone()
        if unit is None or unit['unit_status']!='success' or unit['source_key']!=source or unit['source_grade']!='LIVE_READ':raise ValueError('adapter receipt does not match a committed live source unit')
        if unit['season_id']!='season:native-year:'+str(year):raise ValueError('source unit belongs to another native game season')
        if annual:
            previous=annual_status(conn,annual,year)
            if unit['refresh_family']!=annual or unit['refresh_period_year']!=year or previous is None or previous['previous_unit_id']!=key:raise ValueError('annual receipt does not match the current save/season bucket')
    return dict(unit)

def _recover_child_unit(database,family,directory,source_root,year):
    """Find committed child provenance, including death before result JSON.

    A child result string alone is insufficient. The DB unit must own actual
    child artifacts with matching bytes. No committed facts are changed.
    """
    if not isinstance(directory,str) or Path(directory).name!=directory or directory in ('.','..'):return None
    prefix=directory+'/'
    with closing(connect(database,True)) as conn:
        rows=conn.execute('''SELECT DISTINCT u.unit_id FROM capture_units u JOIN source_artifacts a USING(unit_id)
            WHERE u.source_key=? AND substr(a.payload_ref,1,?)=?''',(SOURCES[family][2],len(prefix),prefix)).fetchall()
        if not rows:return None
        if len(rows)!=1:raise ValueError('ambiguous prior child units; inspect original evidence')
        key=rows[0]['unit_id'];artifacts=conn.execute('SELECT payload_ref,sha256,byte_count FROM source_artifacts WHERE unit_id=? AND substr(payload_ref,1,?)=?',(key,len(prefix),prefix)).fetchall()
    for artifact in artifacts:
        relative=Path(artifact['payload_ref'])
        if len(relative.parts)!=2 or relative.parts[1] in ('.','..'):raise ValueError('invalid committed child artifact reference')
        path=source_root/relative;digest=hashlib.sha256();size=0
        with path.open('rb') as src:
            while block:=src.read(1024*1024):digest.update(block);size+=len(block)
        if digest.hexdigest()!=artifact['sha256'] or size!=artifact['byte_count']:raise ValueError('prior committed child artifact changed or incomplete')
    return _unit_receipt(database,{'status':'ingested','unit_id':key},family,year)


def refresh_world(pid,save_directory,loaded_filename,new_output_directory,*,families=None,resume_report=None,data_updated=False):
    """Fail fast, retain committed units, and permit selective reruns in a NEW directory.

    This is a sequence of independently atomic source observations, not a global
    point-in-time snapshot, season completion, scheduler or acceptance decision.
    """
    if type(data_updated) is not bool:raise ValueError('data_updated must be a boolean declaration')
    requested=list(SOURCES) if families is None else list(families)
    if not requested or len(set(requested))!=len(requested) or any(f not in SOURCES for f in requested):raise ValueError('choose distinct registered refresh families')
    requested=[key for key in SOURCES if key in requested]
    binding,binding_hash=read_binding(save_directory,loaded_filename);database=bound_database(save_directory,binding)
    with closing(connect(database,True)) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0]!=VERSION:raise ValueError('copy-upgrade facts before world refresh')
    prior=None
    if resume_report is not None:
        prior=json.loads(Path(resume_report).read_bytes())
        if prior.get('save_id')!=binding['save_id'] or prior.get('native_save_filename')!=loaded_filename or prior.get('database_file')!=database.name or prior.get('binding_sha256')!=binding_hash:raise ValueError('resume report save/database binding differs')
        if prior.get('status')=='RUNNING' and owner_is_live(prior.get('controller')):raise ValueError('prior refresh controller is still live; do not start another worker')
        if prior.get('status') not in ('RUNNING','STOPPED_PARTIAL','COMPLETED_REQUESTED_SOURCES'):raise ValueError('unsupported resume report status')
        old_plan=prior.get('requested_families')
        if not isinstance(old_plan,list) or not old_plan or len(set(old_plan))!=len(old_plan) or any(f not in SOURCES for f in old_plan):raise ValueError('invalid prior source plan')
        if families is None:requested=[f for f in SOURCES if f in old_plan]
        elif any(f not in old_plan for f in requested):raise ValueError('resume selected sources must belong to prior batch')
        entries=prior.get('sources',[])
        if len(entries)!=len(old_plan) or {e.get('family') for e in entries}!=set(old_plan):raise ValueError('prior source ledger does not match plan')
    pid=resolve_pid(pid)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);token=uuid.uuid4().hex[:12];base=Path(__file__).resolve().parent
    files=sorted(base.glob('*.py'))+sorted(base.glob('*profile.json'))+[base/'schema.sql',base/'field_dictionary.json']
    report={'format_version':2,'batch_id':token,'status':'RUNNING','controller':owner_identity(),'save_id':binding['save_id'],'native_save_filename':loaded_filename,'database_file':database.name,
        'binding_sha256':binding_hash,'started_at':_stamp(),'finished_at':None,'requested_families':requested,'report_file':str(out/'refresh-report.json'),
        'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'sources':[{'family':family,'status':'PENDING','directory':token+'-'+str(i).zfill(2)+'-'+family} for i,family in enumerate(requested)],
        'consistency_scope':'INDEPENDENT_ATOMIC_SOURCE_UNITS_WITHIN_ONE_CHECKED_PROCESS_AND_GAME_SEASON; NOT_ONE_GLOBAL_SNAPSHOT',
        'save_identity_basis':binding['identity_basis'],'data_update_declared':data_updated,'resume_report':str(Path(resume_report).resolve()) if prior else None,
        'game_writes':False,'scheduler_started':False,'full_goal_complete':False}
    path=out/'refresh-report.json';_write(path,report);epoch=None;active=None
    def checkpoint(label):
        current,current_hash=read_binding(save_directory,loaded_filename)
        if current_hash!=binding_hash or bound_database(save_directory,current)!=database:raise ValueError('save binding changed during refresh')
        context=_context(pid);_write(out/(label+'-context.json'),context)
        if epoch is not None and context['epoch']!=epoch:raise ValueError('process/build/game-season context changed during refresh')
        if 'game_progress' in report and context.get('game_progress')!=report['game_progress']:raise ValueError('game date/stage changed during refresh')
        if epoch is None:report['game_progress']=context.get('game_progress')
        return context['epoch']
    try:
        if prior:
            epoch=checkpoint('resume');report['game_season_year']=epoch['game_season_year'];report['process_epoch']=epoch
            progress=report.get('game_progress');old_progress=prior.get('game_progress')
            recapture=data_updated or not progress or not old_progress or progress!=old_progress or prior.get('game_season_year')!=epoch['game_season_year']
            report['resume_policy']='RECAPTURE_REQUESTED_SOURCES' if recapture else 'RETAIN_VERIFIED_PRIOR_OBSERVATIONS_AND_CAPTURE_REMAINDER'
            report['resume_basis']='Native progress comparison and Human update declaration; equal dates do not prove unchanged content'
            if not recapture:
                report['consistency_scope']='INDEPENDENT_SOURCE_OBSERVATIONS_WITH_ORIGINAL_PROCESS_AND_TIMES; RETAINED_UNITS_NOT_REOBSERVED_IN_CURRENT_PROCESS'
                old_entries={e['family']:e for e in prior['sources']}
                for entry in report['sources']:
                    old=old_entries[entry['family']];unit=old.get('unit');claim=old.get('adapter_claim')
                    if unit is not None:
                        claim={'status':'already_refreshed','previous_unit_id':unit['unit_id']} if old.get('status')=='ANNUAL_ALREADY_REFRESHED' else {'status':'ingested','unit_id':unit['unit_id']}
                    if unit is None:
                        recovered=_recover_child_unit(database,entry['family'],old.get('directory'),Path(resume_report).resolve().parent,epoch['game_season_year'])
                        if recovered:claim={'status':'ingested','unit_id':recovered['unit_id']}
                        elif claim is not None:raise ValueError('prior child claim has no matching committed artifact provenance')
                    if claim is not None:
                        receipt=_unit_receipt(database,claim,entry['family'],epoch['game_season_year'])
                        if unit is not None and receipt!=unit:raise ValueError('prior committed receipt changed or does not match database')
                        entry.update({'status':'RETAINED_PRIOR_OBSERVATION','commit_status':'COMMITTED_SUCCESS_VERIFIED','unit':receipt,
                            'origin_batch_id':old.get('origin_batch_id',prior['batch_id']),'origin_process_epoch':old.get('origin_process_epoch',prior.get('process_epoch')),
                            'fresh_native_capture':False,'retention_basis':'VERIFIED_DATABASE_RECEIPT; ORIGINAL_OBSERVATION_TIME_RETAINED'})
            _write(path,report)
        for index,entry in enumerate(report['sources']):
            if entry['status']=='RETAINED_PRIOR_OBSERVATION':continue
            active=entry;entry['started_at']=_stamp();entry['status']='RUNNING';_write(path,report)
            observed=checkpoint(str(index).zfill(2)+'-before')
            if epoch is None:epoch=observed;report['game_season_year']=epoch['game_season_year'];report['process_epoch']=epoch
            entry['commit_status']='UNKNOWN_UNTIL_RECEIPT_VERIFIED';_write(path,report)
            result=_capture(entry['family'],pid,save_directory,loaded_filename,out/entry['directory'])
            entry['adapter_claim']={key:result[key] for key in ('status','unit_id','previous_unit_id') if key in result}
            receipt=_unit_receipt(database,result,entry['family'],epoch['game_season_year'])
            entry.update({'status':'ANNUAL_ALREADY_REFRESHED' if result['status']=='already_refreshed' else 'ACQUIRED','commit_status':'COMMITTED_SUCCESS_VERIFIED','unit':receipt,'counts':result.get('counts',{}),'finished_at':_stamp()})
            _write(path,report);checkpoint(str(index).zfill(2)+'-after')
        report['status']='COMPLETED_REQUESTED_SOURCES';report['finished_at']=_stamp();report['rerun_families']=[];_write(path,report);return report
    except Exception as error:
        if active and active['status']=='RUNNING':active['status']='FAILED';active['finished_at']=_stamp()
        elif active:active['post_capture_context_status']='FAILED_AFTER_VERIFIED_COMMIT'
        report.update({'status':'STOPPED_PARTIAL','finished_at':_stamp(),'failure':{'family':active['family'] if active else None,'error_type':type(error).__name__,'reason':str(error)},
            'rerun_families':[entry['family'] for entry in report['sources'] if entry['status'] in ('FAILED','PENDING')]})
        _write(out/'refresh-failure.json',{'error_type':type(error).__name__,'reason':str(error),'read_trace':getattr(error,'read_trace',[])});_write(path,report)
        raise RefreshFailed(report) from error
