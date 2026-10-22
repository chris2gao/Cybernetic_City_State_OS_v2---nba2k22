"""Read small snapshot-bound SQLite results. No game, capture or publication.

Examples: team roster --team SAS; staff search --name Popovich; player search
--scope pool --draft-year 1984; sql --select 'SELECT team,COUNT(*) AS n FROM
q_players GROUP BY team ORDER BY team'. Use --help for filters and projections.
"""
import argparse
from datetime import datetime,timezone
import json
import sqlite3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_data_access import AccessError, QUERY_VERSION
from gm_data_access.query import QuerySession,DEFAULTS


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('domain',choices=('status','team','player','staff','coaching','contract','picks','finance','sql','issues',
                                  'world','gameplay','tactics','tendency','training','personal_defense','rotation','native_objects','native_books','native_context'))
    p.add_argument('action',nargs='?',choices=('summary','stats','roster','search','team','semantics','opponent'))
    p.add_argument('--career',required=True)
    p.add_argument('--batch',help='Pin a historical or current batch; default resolves local published/latest')
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    p.add_argument('--published-root',type=Path,default=ROOT/'published',help='Trusted local checkout of published pointers; no network/hash sync')
    p.add_argument('--role',choices=('CODEX_CAPTURE','CODEX_EXECUTION','WEB_ANALYTICS','WEB_GM','WEB_DEVELOPMENT'),default='CODEX_CAPTURE',help='Declared caller role, not proof of Web connection or approval')
    p.add_argument('--team',help='Exact observed abbreviation or team ID')
    p.add_argument('--opponent',help='Exact observed abbreviation or team ID')
    p.add_argument('--name',help='Literal case-insensitive substring; returns all matching identities in bounded pages')
    p.add_argument('--identity',help='Exact batch-scoped identity, not a permanent player ID')
    p.add_argument('--player-identity',help='DEV14 verified player identity within the selected batch')
    p.add_argument('--field-key',help='Exact registered DEV14 native field key')
    p.add_argument('--target-kind',help='Exact observed native object kind, e.g. COACH_DEFAULT')
    p.add_argument('--side',choices=('USER','CPU'),help='Gameplay control side; unrelated to 30-team GM ownership')
    p.add_argument('--scope',choices=('roster','pool'),default='roster')
    p.add_argument('--position')
    p.add_argument('--job',help='Verified assigned role, or observed candidate-position enum with --candidates')
    p.add_argument('--candidates',action='store_true',help='Only staff without a verified current NBA appointment')
    p.add_argument('--unrostered',action='store_true',help='Pool models not on observed NBA rosters; does NOT certify free agency')
    p.add_argument('--draft-year',type=int)
    p.add_argument('--historical-rookie',action='store_true')
    p.add_argument('--years-left',type=int,help='Observed remaining contract years; does NOT certify offseason expiry')
    p.add_argument('--trade-eligible',action='store_true')
    p.add_argument('--fields',help='Explicit comma-separated projection; defaults are small. Unknown/legacy fields fail closed')
    p.add_argument('--limit',type=int,default=20,help='1..50; default 20; response soft cap 20KB')
    p.add_argument('--cursor',help='Opaque query+batch-bound continuation from previous response')
    p.add_argument('--select',help='One SELECT over q_* safe views only; no SELECT * except COUNT(*)')
    p.add_argument('--params',default='[]',help='JSON array of parameters for --select placeholders')
    p.add_argument('--allow-local-audited',action='store_true',help='Explicit development access to unpublished sources; never enables production GM')
    return p


def resolve_team(session, value):
    if value is None:
        return None
    key='team_id' if value.isdigit() else 'team'
    rows=session.query('teams',fields=['team_id'],filters={key:int(value) if value.isdigit() else value.upper()})['rows']
    if len(rows)!=1:
        raise AccessError('INVALID_INPUT','Team identity is not unique in this snapshot')
    return rows[0]['team_id']


def run(a):
    session=QuerySession(a.query_root,a.published_root,a.career,a.batch)
    try:
        if a.role in ('WEB_GM','WEB_ANALYTICS','WEB_DEVELOPMENT'):
            session.require_gm_sanitized()
        if a.domain=='status':
            return dict(status='QUERYABLE_LOCAL',rows=[],row_count=0,source_binding=session.binding,
                        query_version=QUERY_VERSION,next_cursor=None,truncated=False,field_evidence={},
                        views={k:list(v) for k,v in session.columns.items()},
                        observed_source_available=session.available,
                        safety=dict(sqlite_mode='ro',query_only=True,result_limit=50,bytes_budget=20000,sql_seconds=2,
                                    os_consumer_acl='SEPARATE_ACCOUNT_SETUP_REQUIRED_NOT_ATTESTED',
                                    web_connections='DEFERRED_BY_PLAYER_NOT_TESTED'))
        if session.binding['publication_status']=='LOCAL_AUDITED_NOT_PUBLISHED' and not a.allow_local_audited:
            raise AccessError('LOCAL_AUDITED_NOT_PUBLISHED','Explicit --allow-local-audited required; production GM unavailable')
        if a.domain=='issues':
            result=session.query('finance',fields=['team','cash','cash_signed32_hypothesis','financial_eligibility'],limit=4,
                                 sql="SELECT team,cash,cash_signed32_hypothesis,financial_eligibility FROM q_finance WHERE cash>=2147483648 ORDER BY team")
            result['issues']=[dict(issue_id='M0_CASH_SIGNEDNESS',type='FINANCE_SEMANTICS_UNVERIFIED',status='OPEN',
                                  evidence='src/auto_pipeline_ingest.py cash require_uint32 TEAM+0x1010',
                                  resolution='Keep raw; compare native format/UI only when separately authorized'),
                              dict(issue_id='M0_WEB_CONNECTIONS',type='DATA_CONSUMER_UNREADABLE',status='DEFERRED_UNTESTED',
                                   resolution='Player will connect three Web sessions after implementation; no success inferred')]
            return result
        if a.domain=='sql':
            if not a.select:
                raise AccessError('INVALID_INPUT','--select required')
            return session.query('sql',sql=a.select,params=json.loads(a.params),limit=a.limit,cursor=a.cursor)
        routes={('team','summary'):'teams',('team','stats'):'team_stats',('team','roster'):'players',('player','search'):'pool' if a.scope=='pool' else 'players',
                ('staff','team'):'staff',('staff','search'):'staff',('coaching','team'):'coaching',
                ('coaching','opponent'):'defense',('contract','search'):'players',('contract','team'):'players',
                ('picks','team'):'picks',('picks','search'):'picks',('finance','team'):'finance',('finance','semantics'):'finance_semantics'}
        entity=routes.get((a.domain,a.action))
        if a.domain in ('world','gameplay','tactics','tendency','training','personal_defense','rotation','native_objects','native_books','native_context') and a.action in ('search','team',None):
            entity=a.domain
        if not entity:
            raise AccessError('INVALID_INPUT','Unsupported domain/action; use --help')
        filters={}
        team=resolve_team(session,a.team)
        if team is not None:
            filters['team_id']=team
        for arg,key in ((a.player_identity,'player_identity'),(a.field_key,'field_key'),(a.side,'side'),(a.target_kind,'target_kind')):
            if arg is not None:
                filters[key]=arg
        for arg,key in ((a.name,'name'),(a.identity,'identity'),(a.position,'position'),(a.draft_year,'draft_year'),(a.years_left,'years_left')):
            if arg is not None:
                filters[key]=arg
        if a.job:
            filters['candidate_position' if a.candidates else 'role']=a.job
        if a.candidates:
            filters['role']=None
        if a.unrostered:
            filters['roster_status']='NOT_ON_OBSERVED_NBA_ROSTER'
        if a.historical_rookie:
            filters['historical_rookie']=1
        if a.trade_eligible:
            filters['trade_eligible']=1
        if a.opponent:
            filters['opponent_team_id']=resolve_team(session,a.opponent)
        if entity=='defense' and (team is None or not a.opponent):
            raise AccessError('INVALID_INPUT','Opponent defense requires --team and --opponent')
        fields=a.fields.split(',') if a.fields else None
        if a.domain=='contract' and fields is None:
            fields=['identity','name','team','salary','years_left','contract','expiry_status']
        return session.query(entity,fields,filters,a.limit,a.cursor)
    finally:
        session.close()


def main(argv=None):
    a=parser().parse_args(argv)
    try:
        result=run(a)
        result['access_contract']=dict(contract='DATA_ACCESS_CONTRACT_V2',role=a.role,career_id=a.career,
            batch_id=result['source_binding']['batch_id'],query_version=QUERY_VERSION,
            requested_data=a.domain+('/'+a.action if a.action else ''),actual_row_count=result['row_count'],
            field_coverage=list(result['field_evidence']),success=True,error=None,
            verified_by='LOCAL_CLI_EXECUTION_ONLY_NOT_WEB_ATTESTATION',verified_at=datetime.now(timezone.utc).isoformat(),
            tool_used='gm_data_query.py / Python sqlite3',stage='QUERYABLE_LOCAL_NOT_ROLE_ACCEPTED')
        print(json.dumps(result,ensure_ascii=False,allow_nan=False))
        return 0
    except (AccessError,sqlite3.Error,OSError,ValueError,KeyError) as e:
        message='Local SQLite access denied or schema incompatible; see access manual' if isinstance(e,(sqlite3.Error,OSError)) else str(e)[:240]
        result=dict(status=getattr(e,'code','BLOCKED_LOCAL_DB_ACCESS'),rows=[],row_count=0,next_cursor=None,
                    truncated=False,source_binding=None,query_version=QUERY_VERSION,field_evidence={},message=message,
                    access_contract=dict(contract='DATA_ACCESS_CONTRACT_V2',role=a.role,career_id=a.career,batch_id=a.batch,success=False,
                        query_version=QUERY_VERSION,requested_data=a.domain+('/'+a.action if a.action else ''),actual_row_count=0,field_coverage=[],
                        error=getattr(e,'code','BLOCKED_LOCAL_DB_ACCESS'),verified_by='LOCAL_CLI_EXECUTION_ONLY_NOT_WEB_ATTESTATION',
                        verified_at=datetime.now(timezone.utc).isoformat(),tool_used='gm_data_query.py'))
        print(json.dumps(result,ensure_ascii=False))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
