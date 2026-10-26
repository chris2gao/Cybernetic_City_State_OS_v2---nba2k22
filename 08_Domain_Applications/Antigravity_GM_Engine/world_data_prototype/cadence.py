"""Human-selected game-season refresh cadence; no scheduler or gameplay action."""
import struct

ANNUAL_FAMILIES={
    'RECORD_BOOK':'BOUND_RECORD_BOOK',
    'NATIVE_HONOR_STATS':'BOUND_NATIVE_HONOR_STATS',
    'LEAGUE_HISTORY_AWARDS':'BOUND_LEAGUE_HISTORY_AND_AWARDS',
    'STAFF_SEASON_HISTORY':'BOUND_NATIVE_ANNUAL_STAFF_STATS',
}


def validate_period(family,year):
    if family not in ANNUAL_FAMILIES:raise ValueError('unknown annual refresh family')
    if type(year) is not int or not 1<=year<=9999:raise ValueError('game-season refresh year must be an integer 1..9999')


def validate_refresh_metadata(payload):
    family=payload.get('refresh_family');year=payload.get('refresh_period_year')
    if family is None and year is None:
        if any(payload.get(k) is not None for k in ('refresh_kind','refresh_baseline_unit_id','refresh_request_sha256','refresh_evidence_sha256')):raise ValueError('ordinary capture cannot carry annual addition metadata')
        if payload.get('evidence_grade')=='LIVE_READ' and payload['source_key'] in ANNUAL_FAMILIES.values():
            raise ValueError('live historical/award refresh requires annual period metadata')
        return
    validate_period(family,year)
    if payload['source_key']!=ANNUAL_FAMILIES[family]:raise ValueError('annual family/source mismatch')
    kind=payload.get('refresh_kind','BASELINE')
    if kind not in ('BASELINE','ADDITION'):raise ValueError('invalid annual refresh kind')
    if kind=='BASELINE':
        if any(payload.get(k) is not None for k in ('refresh_baseline_unit_id','refresh_request_sha256','refresh_evidence_sha256')):raise ValueError('annual baseline cannot masquerade as an addition')
    else:
        if payload.get('evidence_grade')!='LIVE_READ' or not isinstance(payload.get('refresh_baseline_unit_id'),str) or not payload['refresh_baseline_unit_id']:raise ValueError('annual addition requires verified source and explicit baseline')
        for name in ('refresh_request_sha256','refresh_evidence_sha256'):
            value=payload.get(name)
            if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise ValueError('annual addition needs SHA256 '+name)
        proof=payload.get('annual_addition_scope',{})
        if not isinstance(proof,dict):raise ValueError('annual addition requires a typed acquisition scope')
        if proof.get('format')!='TARGETED_NATIVE_ANNUAL_ADDITION_V1' or type(proof.get('requested_records')) is not int or not 1<=proof['requested_records']<=128 or proof.get('untargeted_history_full_record_reads')!=0:raise ValueError('annual addition requires bounded targeted acquisition evidence')
        if payload['refresh_evidence_sha256'] not in {a.get('sha256') for a in payload.get('artifacts',[])}:raise ValueError('annual addition evidence artifact missing')


def annual_status(conn,family,year):
    validate_period(family,year)
    columns={r[1] for r in conn.execute('PRAGMA table_info(capture_runs)')}
    if not {'refresh_family','refresh_period_year','refresh_kind'}<=columns:raise ValueError('copy-upgrade the fact database before annual refresh')
    row=conn.execute('''SELECT u.unit_id,u.observed_at,r.source_grade FROM capture_runs r
        JOIN capture_units u USING(run_id) WHERE r.refresh_family=? AND r.refresh_period_year=?
        AND r.source_grade='LIVE_READ' AND u.unit_status='success' AND r.refresh_kind='BASELINE'
        ORDER BY u.observed_at,u.unit_id LIMIT 1''',(family,year)).fetchone()
    return None if row is None else {'status':'already_refreshed','refresh_family':family,'refresh_period_year':year,
        'previous_unit_id':row['unit_id'],'previous_observed_at':row['observed_at'],'previous_source_grade':row['source_grade'],
        'full_source_acquisition':False,'game_writes':False}


def observed_game_season_year(reader):
    """Tiny current native season control; no history/award array acquisition."""
    from live_reader import ROSTER_RVA
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'CADENCE_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    team_desc=reader.read(root+8*16,16,'CADENCE_TEAM_DESCRIPTOR');stat_desc=reader.read(root+28*16,16,'CADENCE_TEAM_STAT_DESCRIPTOR')
    count,teams=struct.unpack('<QQ',team_desc);stat_count,stats=struct.unpack('<QQ',stat_desc)
    if not 1<=count<=1024 or not 1<=stat_count<=10000:raise ValueError('annual period season descriptor invalid')
    controls=[];year=None
    for i in range(count):
        address=teams+i*4696;ident=reader.read(address+0xCA8,2,'CADENCE_TEAM_ID')
        if int.from_bytes(ident,'little')!=0:continue
        index_raw=reader.read(address+0xE80,2,'CADENCE_CURRENT_STAT_INDEX');index=int.from_bytes(index_raw,'little')
        if index>=stat_count:raise ValueError('annual period native season index invalid')
        year_address=stats+index*62+4;year_raw=reader.read(year_address,1,'CADENCE_COMPACT_YEAR');year=1900+year_raw[0]
        controls=[(address+0xCA8,ident),(address+0xE80,index_raw),(year_address,year_raw)];break
    if year is None:raise ValueError('annual period native season unavailable')
    controls.extend(((reader.module_base+ROSTER_RVA,pointer),(root+8*16,team_desc),(root+28*16,stat_desc)))
    for address,raw in controls:
        if reader.read(address,len(raw),'CADENCE_CONTEXT_RECHECK')!=raw:raise ValueError('annual period context changed')
    return year


def prepare_annual_capture(reader,database,family):
    """Resolve current game year afresh; fixtures never consume a live period."""
    from engine import connect
    year=observed_game_season_year(reader)
    with connect(database,True) as conn:status=annual_status(conn,family,year)
    return year,status


def attach_annual_period(payload,family,year):
    validate_period(family,year)
    if payload['source_key']!=ANNUAL_FAMILIES[family]:raise ValueError('annual family/source mismatch')
    payload['refresh_family']=family;payload['refresh_period_year']=year
    payload['refresh_kind']='BASELINE'
    return payload
