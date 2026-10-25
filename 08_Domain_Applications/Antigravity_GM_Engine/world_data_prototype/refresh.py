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

# Ordered source dependencies: schedule establishes current player/team identities.
SOURCES={
    'schedule':('schedule_reader','capture_season','BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS',None),
    'game-mode':('game_mode_reader','capture_game_mode','BOUND_NATIVE_GAME_MODE_PERIOD',None),
    'organization':('organization_reader','capture_organization','BOUND_CORE_ORGANIZATION',None),
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
        return {'epoch':{'pid':pid,'creation_filetime':created,'module_base':hex(reader.module_base),'module_size':reader.module_size,'pe_timestamp':1652287197,'game_season_year':year},'read_trace':reader.trace}
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

def refresh_world(pid,save_directory,loaded_filename,new_output_directory,*,families=None):
    """Fail fast, retain committed units, and permit selective reruns in a NEW directory.

    This is a sequence of independently atomic source observations, not a global
    point-in-time snapshot, season completion, scheduler or acceptance decision.
    """
    if type(pid) is not int or pid<=0:raise ValueError('positive explicit process ID required')
    requested=list(SOURCES) if families is None else list(families)
    if not requested or len(set(requested))!=len(requested) or any(f not in SOURCES for f in requested):raise ValueError('choose distinct registered refresh families')
    requested=[key for key in SOURCES if key in requested]
    binding,binding_hash=read_binding(save_directory,loaded_filename);database=bound_database(save_directory,binding)
    with closing(connect(database,True)) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0]!=VERSION:raise ValueError('copy-upgrade facts before world refresh')
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);token=uuid.uuid4().hex[:12];base=Path(__file__).resolve().parent
    files=sorted(base.glob('*.py'))+sorted(base.glob('*profile.json'))+[base/'schema.sql',base/'field_dictionary.json']
    report={'format_version':1,'batch_id':token,'status':'RUNNING','save_id':binding['save_id'],'native_save_filename':loaded_filename,'database_file':database.name,
        'binding_sha256':binding_hash,'started_at':_stamp(),'finished_at':None,'requested_families':requested,'report_file':str(out/'refresh-report.json'),
        'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'sources':[{'family':family,'status':'PENDING','directory':token+'-'+str(i).zfill(2)+'-'+family} for i,family in enumerate(requested)],
        'consistency_scope':'INDEPENDENT_ATOMIC_SOURCE_UNITS_WITHIN_ONE_CHECKED_PROCESS_AND_GAME_SEASON; NOT_ONE_GLOBAL_SNAPSHOT',
        'save_identity_basis':binding['identity_basis'],'game_writes':False,'scheduler_started':False,'full_goal_complete':False}
    path=out/'refresh-report.json';_write(path,report);epoch=None;active=None
    def checkpoint(label):
        current,current_hash=read_binding(save_directory,loaded_filename)
        if current_hash!=binding_hash or bound_database(save_directory,current)!=database:raise ValueError('save binding changed during refresh')
        context=_context(pid);_write(out/(label+'-context.json'),context)
        if epoch is not None and context['epoch']!=epoch:raise ValueError('process/build/game-season context changed during refresh')
        return context['epoch']
    try:
        for index,entry in enumerate(report['sources']):
            active=entry;entry['started_at']=_stamp();entry['status']='RUNNING';_write(path,report)
            observed=checkpoint(str(index).zfill(2)+'-before')
            if epoch is None:epoch=observed;report['game_season_year']=epoch['game_season_year']
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
