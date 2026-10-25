"""Minimal synthetic-only world-data prototype command line."""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import create_database,connect,ingest_synthetic_capture,ingest_capture,summarize,migrate_v1,migrate_database
from readers import replay_ag01d,replay_player_families
from query import player_card,game_box,history,export_jsonl,inspect_source_capture,schedule,team_card,staff_card,market_snapshot,prospect_card,planning_snapshot,gameplan_card,settings_snapshot,rules_snapshot,record_book,native_honors,season_summary,player_seasons
from owner_capture import recorded_game_capture


def synthetic_payload(save_id='demo-alpha',run_id='run-1',unit_id='unit-1',observed_at='2026-10-24T00:00:00Z'):
    return dict(save_id=save_id,run_id=run_id,unit_id=unit_id,source_key='SYNTHETIC_DEMO',
                observed_at=observed_at,evidence_grade='SYNTHETIC_FIXTURE',
                season={'season_id':'season-2021','season_code':'2021-22'},
                teams=[{'team_id':'team-a','display_name':'Synthetic A'},{'team_id':'team-b','display_name':'Synthetic B'}],
                players=[{'player_id':'player-a','display_name':'Synthetic Guard'}],
                game={'game_id':'game-1','home_team_id':'team-a','away_team_id':'team-b','game_date':'2021-10-19'},
                game_state={'status_code':'finished','home_points':102,'away_points':101},
                boxes=[{'player_id':'player-a','team_id':'team-a','points':22,'fg_made':8,'fg_attempted':14}],
                attributes=[{'player_id':'player-a','overall_raw':82,'shot_close_raw':70,'driving_layup_raw':79}],
                tendencies=[{'player_id':'player-a','shot_tendency_raw':72,'drive_tendency_raw':60}],
                badges=[{'player_id':'player-a','badge_key':'SYNTHETIC_FINISHING','native_code':1,'tier_label':'synthetic-tier','owned_state':'owned'}],
                play_types=[{'player_id':'player-a','slot_index':0,'native_play_code':'SYNTHETIC_PNR'}])


def smoke():
    with TemporaryDirectory() as t:
        path=Path(t)/'isolated_demo.sqlite'
        create_database(path,'demo-alpha')
        with connect(path) as c:
            one=ingest_synthetic_capture(c,synthetic_payload())
            same=ingest_synthetic_capture(c,synthetic_payload())
            second=ingest_synthetic_capture(c,synthetic_payload(run_id='run-2',unit_id='unit-2',observed_at='2026-10-25T00:00:00Z'))
            joined=c.execute('SELECT count(*) FROM gm_game_box WHERE game_id=?',('game-1',)).fetchone()[0]
            if (one,same,second,joined)!=('ingested','already_applied','ingested',2):raise RuntimeError('smoke failed')
        return summarize(path)


def main():
    parser=argparse.ArgumentParser(description='Per-save NBA2K22 world facts; fixture replay is NOT live acceptance')
    sub=parser.add_subparsers(dest='action',required=True)
    init=sub.add_parser('init');init.add_argument('database');init.add_argument('save_id')
    sub.add_parser('smoke')
    demo=sub.add_parser('demo');demo.add_argument('database');demo.add_argument('save_id')
    replay=sub.add_parser('replay-ag01d');replay.add_argument('database');replay.add_argument('save_id');replay.add_argument('--observed-at')
    families=sub.add_parser('replay-player-families');families.add_argument('database');families.add_argument('save_id');families.add_argument('--observed-at')
    stats=sub.add_parser('summary');stats.add_argument('database')
    card=sub.add_parser('player');card.add_argument('database');card.add_argument('player_id')
    game=sub.add_parser('game');game.add_argument('database');game.add_argument('game_id');game.add_argument('--unit-id')
    season=sub.add_parser('season');season.add_argument('database');season.add_argument('season_id');season.add_argument('--phase-code');season.add_argument('--limit',type=int,default=1000)
    player_season=sub.add_parser('player-seasons');player_season.add_argument('database');player_season.add_argument('player_id');player_season.add_argument('--season-id');player_season.add_argument('--phase-code');player_season.add_argument('--limit',type=int,default=100)
    hist=sub.add_parser('history');hist.add_argument('database');hist.add_argument('table');hist.add_argument('--entity-key');hist.add_argument('--entity-id');hist.add_argument('--limit',type=int,default=200)
    exp=sub.add_parser('export');exp.add_argument('database');exp.add_argument('table');exp.add_argument('destination');exp.add_argument('--limit',type=int,default=10000)
    mig=sub.add_parser('migrate-v1');mig.add_argument('source');mig.add_argument('new_database')
    upgrade=sub.add_parser('upgrade');upgrade.add_argument('source');upgrade.add_argument('new_database')
    owner=sub.add_parser('replay-owner-capture');owner.add_argument('capture_directory');owner.add_argument('database');owner.add_argument('research_save_id')
    inspect=sub.add_parser('inspect-source');inspect.add_argument('database');inspect.add_argument('unit_id')
    bound=sub.add_parser('init-save');bound.add_argument('save_directory');bound.add_argument('save_id');bound.add_argument('native_save_file')
    live=sub.add_parser('capture-live');live.add_argument('pid',type=int);live.add_argument('save_directory');live.add_argument('loaded_filename');live.add_argument('new_output_directory');live.add_argument('--game-index',type=int,default=0)
    from refresh import SOURCES
    refresh=sub.add_parser('refresh-world');refresh.add_argument('pid',type=int);refresh.add_argument('save_directory');refresh.add_argument('loaded_filename');refresh.add_argument('new_output_directory');refresh.add_argument('--families',nargs='+',choices=list(SOURCES))
    saved_upgrade=sub.add_parser('upgrade-save');saved_upgrade.add_argument('save_directory');saved_upgrade.add_argument('loaded_filename')
    season_capture=sub.add_parser('capture-season');season_capture.add_argument('pid',type=int);season_capture.add_argument('save_directory');season_capture.add_argument('loaded_filename');season_capture.add_argument('new_output_directory');season_capture.add_argument('--recheck-frozen',action='store_true')
    sched=sub.add_parser('schedule');sched.add_argument('database');sched.add_argument('--season-id');sched.add_argument('--status-code');sched.add_argument('--period-code',type=int);sched.add_argument('--game-type-code',type=int);sched.add_argument('--native-date-from');sched.add_argument('--native-date-to');sched.add_argument('--limit',type=int,default=2000)
    calendar=sub.add_parser('calendar');calendar.add_argument('database');calendar.add_argument('--season-id');calendar.add_argument('--limit',type=int,default=20)
    org=sub.add_parser('capture-organization');org.add_argument('pid',type=int);org.add_argument('save_directory');org.add_argument('loaded_filename');org.add_argument('new_output_directory')
    team=sub.add_parser('team');team.add_argument('database');team.add_argument('team_id')
    staff=sub.add_parser('staff');staff.add_argument('database');staff.add_argument('staff_id')
    market=sub.add_parser('capture-market');market.add_argument('pid',type=int);market.add_argument('save_directory');market.add_argument('loaded_filename');market.add_argument('new_output_directory')
    market_read=sub.add_parser('market');market_read.add_argument('database');market_read.add_argument('--team-id');market_read.add_argument('--limit',type=int,default=10000)
    prospect=sub.add_parser('prospect');prospect.add_argument('database');prospect.add_argument('prospect_id')
    capture_plan=sub.add_parser('capture-planning');capture_plan.add_argument('pid',type=int);capture_plan.add_argument('save_directory');capture_plan.add_argument('loaded_filename');capture_plan.add_argument('new_output_directory')
    planning=sub.add_parser('planning');planning.add_argument('database');planning.add_argument('--team-id');planning.add_argument('--limit',type=int,default=5000)
    gp=sub.add_parser('gameplan');gp.add_argument('database');gp.add_argument('team_id');gp.add_argument('opponent_team_id')
    capture_settings_cmd=sub.add_parser('capture-settings');capture_settings_cmd.add_argument('pid',type=int);capture_settings_cmd.add_argument('save_directory');capture_settings_cmd.add_argument('loaded_filename');capture_settings_cmd.add_argument('new_output_directory')
    settings_cmd=sub.add_parser('settings');settings_cmd.add_argument('database');settings_cmd.add_argument('--scope-code');settings_cmd.add_argument('--limit',type=int,default=2000)
    rules_cmd=sub.add_parser('rules');rules_cmd.add_argument('database');rules_cmd.add_argument('--season-id');rules_cmd.add_argument('--limit',type=int,default=2000)
    capture_records_cmd=sub.add_parser('capture-records');capture_records_cmd.add_argument('pid',type=int);capture_records_cmd.add_argument('save_directory');capture_records_cmd.add_argument('loaded_filename');capture_records_cmd.add_argument('new_output_directory')
    records_cmd=sub.add_parser('records');records_cmd.add_argument('database');records_cmd.add_argument('--category-code',type=lambda s:int(s,0));records_cmd.add_argument('--subject-name');records_cmd.add_argument('--unit-id');records_cmd.add_argument('--after-index',type=int,default=-1);records_cmd.add_argument('--limit',type=int,default=200)
    honor_capture=sub.add_parser('capture-honors');honor_capture.add_argument('pid',type=int);honor_capture.add_argument('save_directory');honor_capture.add_argument('loaded_filename');honor_capture.add_argument('new_output_directory')
    honor_query=sub.add_parser('native-honors');honor_query.add_argument('database');honor_query.add_argument('--flag');honor_query.add_argument('--year',type=int);honor_query.add_argument('--subject-name');honor_query.add_argument('--unit-id');honor_query.add_argument('--after-index',type=int,default=-1);honor_query.add_argument('--limit',type=int,default=200)
    for command in ('capture-league-history','capture-news'):
        capture=sub.add_parser(command);capture.add_argument('pid',type=int);capture.add_argument('save_directory');capture.add_argument('loaded_filename');capture.add_argument('new_output_directory')
    award_cmd=sub.add_parser('awards');award_cmd.add_argument('database');award_cmd.add_argument('--year',type=int);award_cmd.add_argument('--award-code');award_cmd.add_argument('--after-key',default='');award_cmd.add_argument('--limit',type=int,default=200)
    history_cmd=sub.add_parser('league-history');history_cmd.add_argument('database');history_cmd.add_argument('--year',type=int);history_cmd.add_argument('--type-label');history_cmd.add_argument('--unit-id');history_cmd.add_argument('--after-index',type=int,default=-1);history_cmd.add_argument('--limit',type=int,default=200)
    news_cmd=sub.add_parser('native-news');news_cmd.add_argument('database');news_cmd.add_argument('--event-label');news_cmd.add_argument('--unit-id');news_cmd.add_argument('--after-index',type=int,default=-1);news_cmd.add_argument('--limit',type=int,default=200)
    tx_cmd=sub.add_parser('native-transactions');tx_cmd.add_argument('database');tx_cmd.add_argument('--unit-id')
    detail_capture=sub.add_parser('capture-player-details');detail_capture.add_argument('pid',type=int);detail_capture.add_argument('save_directory');detail_capture.add_argument('loaded_filename');detail_capture.add_argument('new_output_directory')
    detail_query=sub.add_parser('native-player-details');detail_query.add_argument('database');detail_query.add_argument('--subject-name');detail_query.add_argument('--source-index',type=int);detail_query.add_argument('--unit-id');detail_query.add_argument('--after-index',type=int,default=-1);detail_query.add_argument('--limit',type=int,default=10)
    badge_query=sub.add_parser('player-badges');badge_query.add_argument('database');badge_query.add_argument('player_id')
    state_capture=sub.add_parser('capture-player-state');state_capture.add_argument('pid',type=int);state_capture.add_argument('save_directory');state_capture.add_argument('loaded_filename');state_capture.add_argument('new_output_directory')
    state_query=sub.add_parser('native-player-state');state_query.add_argument('database');state_query.add_argument('--subject-name');state_query.add_argument('--source-index',type=int);state_query.add_argument('--unit-id');state_query.add_argument('--after-index',type=int,default=-1);state_query.add_argument('--limit',type=int,default=20)
    affiliation_capture=sub.add_parser('capture-affiliations');affiliation_capture.add_argument('pid',type=int);affiliation_capture.add_argument('save_directory');affiliation_capture.add_argument('loaded_filename');affiliation_capture.add_argument('new_output_directory')
    affiliation_query=sub.add_parser('native-affiliations');affiliation_query.add_argument('database');affiliation_query.add_argument('--subject-name');affiliation_query.add_argument('--source-index',type=int);affiliation_query.add_argument('--flag');affiliation_query.add_argument('--flag-value',type=int,default=1);affiliation_query.add_argument('--unit-id');affiliation_query.add_argument('--after-index',type=int,default=-1);affiliation_query.add_argument('--limit',type=int,default=20)
    skill_capture=sub.add_parser('capture-player-skills');skill_capture.add_argument('pid',type=int);skill_capture.add_argument('save_directory');skill_capture.add_argument('loaded_filename');skill_capture.add_argument('new_output_directory')
    skill_query=sub.add_parser('native-player-skills');skill_query.add_argument('database');skill_query.add_argument('--subject-name');skill_query.add_argument('--source-index',type=int);skill_query.add_argument('--unit-id');skill_query.add_argument('--after-index',type=int,default=-1);skill_query.add_argument('--limit',type=int,default=20)
    backup=sub.add_parser('backup-facts');backup.add_argument('database');backup.add_argument('new_output_directory')
    restore=sub.add_parser('restore-facts');restore.add_argument('backup_directory');restore.add_argument('new_database');restore.add_argument('--expected-save-id',required=True)
    storage=sub.add_parser('storage-profile');storage.add_argument('database')
    paged=sub.add_parser('history-page');paged.add_argument('database');paged.add_argument('table');paged.add_argument('--entity-key');paged.add_argument('--entity-id');paged.add_argument('--limit',type=int,default=200);paged.add_argument('--cursor-json')
    for read_parser in (card,game,season,player_season,hist,paged,exp,sched,calendar,team,staff,market_read,prospect,planning,gp,settings_cmd,rules_cmd,records_cmd,honor_query,award_cmd,history_cmd,news_cmd,tx_cmd,detail_query,badge_query,state_query,affiliation_query,skill_query):
        read_parser.add_argument('--as-of',help='Timezone-aware acquisition cutoff; this is not a native game date')
    args=parser.parse_args()
    if getattr(args,'as_of',None) is not None:
        from observation_scope import observed_as_of
        with observed_as_of(args.database,args.as_of) as scope:
            output=StringIO()
            with redirect_stdout(output):dispatch(args)
            print(json.dumps({'observation_scope':scope.metadata(),'result':json.loads(output.getvalue())},ensure_ascii=False))
        return
    return dispatch(args)


def dispatch(args):
    if args.action=='calendar':
        from query import league_calendar
        print(json.dumps(league_calendar(args.database,season_id=args.season_id,limit=args.limit),ensure_ascii=False));return
    if args.action=='refresh-world':
        from refresh import refresh_world,RefreshFailed
        try:result=refresh_world(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory,families=args.families)
        except RefreshFailed as error:
            print(json.dumps(error.report,ensure_ascii=False));raise SystemExit(2) from None
        print(json.dumps(result,ensure_ascii=False));return
    if args.action=='history-page':
        from query import history_page
        print(json.dumps(history_page(args.database,args.table,entity_key=args.entity_key,entity_id=args.entity_id,limit=args.limit,cursor=json.loads(args.cursor_json) if args.cursor_json else None),ensure_ascii=False));return
    if args.action=='backup-facts':
        from database_operations import backup_facts
        print(json.dumps(backup_facts(args.database,args.new_output_directory),ensure_ascii=False));return
    if args.action=='restore-facts':
        from database_operations import restore_facts
        print(json.dumps(restore_facts(args.backup_directory,args.new_database,expected_save_id=args.expected_save_id),ensure_ascii=False));return
    if args.action=='storage-profile':
        from database_operations import storage_profile
        print(json.dumps(storage_profile(args.database),ensure_ascii=False));return
    if args.action=='capture-player-skills':
        from player_skill_reader import capture_player_skills
        print(json.dumps(capture_player_skills(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='native-player-skills':
        from query import native_player_skills
        print(json.dumps(native_player_skills(args.database,subject_name=args.subject_name,source_index=args.source_index,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-affiliations':
        from player_affiliation_reader import capture_player_affiliations
        print(json.dumps(capture_player_affiliations(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='native-affiliations':
        from query import native_affiliations
        print(json.dumps(native_affiliations(args.database,subject_name=args.subject_name,source_index=args.source_index,flag=args.flag,flag_value=args.flag_value,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-player-state':
        from player_state_reader import capture_player_state
        print(json.dumps(capture_player_state(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='native-player-state':
        from query import native_player_state
        print(json.dumps(native_player_state(args.database,subject_name=args.subject_name,source_index=args.source_index,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-player-details':
        from player_detail_reader import capture_player_details
        print(json.dumps(capture_player_details(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='native-player-details':
        from query import native_player_details
        print(json.dumps(native_player_details(args.database,subject_name=args.subject_name,source_index=args.source_index,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='player-badges':
        from query import player_badges
        print(json.dumps(player_badges(args.database,args.player_id),ensure_ascii=False));return
    if args.action in ('capture-league-history','capture-news'):
        from league_ingest import capture_league
        print(json.dumps(capture_league(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory,mode='HISTORY_AWARDS' if args.action=='capture-league-history' else 'NEWS_TRANSACTIONS'),ensure_ascii=False));return
    if args.action=='awards':
        from query import awards
        print(json.dumps(awards(args.database,year=args.year,award_code=args.award_code,after_key=args.after_key,limit=args.limit),ensure_ascii=False));return
    if args.action=='league-history':
        from query import league_history
        print(json.dumps(league_history(args.database,year=args.year,type_label=args.type_label,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='native-news':
        from query import native_news
        print(json.dumps(native_news(args.database,event_label=args.event_label,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='native-transactions':
        from query import native_transactions
        print(json.dumps(native_transactions(args.database,unit_id=args.unit_id),ensure_ascii=False));return
    if args.action=='capture-honors':
        from award_reader import capture_native_honors
        print(json.dumps(capture_native_honors(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='native-honors':print(json.dumps(native_honors(args.database,flag=args.flag,year=args.year,subject_name=args.subject_name,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-records':
        from records_reader import capture_records
        print(json.dumps(capture_records(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='records':print(json.dumps(record_book(args.database,category_code=args.category_code,subject_name=args.subject_name,unit_id=args.unit_id,after_index=args.after_index,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-settings':
        from settings_reader import capture_settings
        print(json.dumps(capture_settings(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='settings':print(json.dumps(settings_snapshot(args.database,scope_code=args.scope_code,limit=args.limit),ensure_ascii=False));return
    if args.action=='rules':print(json.dumps(rules_snapshot(args.database,season_id=args.season_id,limit=args.limit),ensure_ascii=False));return
    if args.action=='capture-planning':
        from planning_reader import capture_planning
        print(json.dumps(capture_planning(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='planning':print(json.dumps(planning_snapshot(args.database,team_id=args.team_id,limit=args.limit),ensure_ascii=False));return
    if args.action=='gameplan':print(json.dumps(gameplan_card(args.database,args.team_id,args.opponent_team_id),ensure_ascii=False));return
    if args.action=='capture-market':
        from market_reader import capture_market
        print(json.dumps(capture_market(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='market':print(json.dumps(market_snapshot(args.database,team_id=args.team_id,limit=args.limit),ensure_ascii=False));return
    if args.action=='prospect':print(json.dumps(prospect_card(args.database,args.prospect_id),ensure_ascii=False));return
    if args.action=='capture-organization':
        from organization_reader import capture_organization
        print(json.dumps(capture_organization(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='team':print(json.dumps(team_card(args.database,args.team_id),ensure_ascii=False));return
    if args.action=='staff':print(json.dumps(staff_card(args.database,args.staff_id),ensure_ascii=False));return
    if args.action=='schedule':print(json.dumps(schedule(args.database,season_id=args.season_id,status_code=args.status_code,period_code=args.period_code,game_type_code=args.game_type_code,native_date_from=args.native_date_from,native_date_to=args.native_date_to,limit=args.limit),ensure_ascii=False));return
    if args.action=='upgrade-save':
        from live_world import upgrade_bound_save
        print(json.dumps(upgrade_bound_save(args.save_directory,args.loaded_filename)));return
    if args.action=='capture-season':
        from schedule_reader import capture_season
        print(json.dumps(capture_season(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory,recheck_frozen=args.recheck_frozen),ensure_ascii=False));return
    if args.action=='init-save':
        from live_world import initialize_save
        print(json.dumps(initialize_save(args.save_directory,args.save_id,args.native_save_file),ensure_ascii=False));return
    if args.action=='capture-live':
        from live_world import capture_live
        print(json.dumps(capture_live(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory,args.game_index),ensure_ascii=False));return
    if args.action=='smoke': print(json.dumps(smoke(),sort_keys=True));return
    if args.action=='summary':print(json.dumps(summarize(args.database),sort_keys=True));return
    if args.action=='player':print(json.dumps(player_card(args.database,args.player_id),ensure_ascii=False));return
    if args.action=='game':print(json.dumps(game_box(args.database,args.game_id,unit_id=args.unit_id),ensure_ascii=False));return
    if args.action=='season':print(json.dumps(season_summary(args.database,args.season_id,phase_code=args.phase_code,limit=args.limit),ensure_ascii=False));return
    if args.action=='player-seasons':print(json.dumps(player_seasons(args.database,args.player_id,season_id=args.season_id,phase_code=args.phase_code,limit=args.limit),ensure_ascii=False));return
    if args.action=='inspect-source':print(json.dumps(inspect_source_capture(args.database,args.unit_id),ensure_ascii=False));return
    if args.action=='history':print(json.dumps(history(args.database,args.table,entity_key=args.entity_key,entity_id=args.entity_id,limit=args.limit),ensure_ascii=False));return
    if args.action=='export':print(json.dumps(export_jsonl(args.database,args.destination,args.table,limit=args.limit)));return
    if args.action=='migrate-v1':print(json.dumps({'database':str(migrate_v1(args.source,args.new_database))}));return
    if args.action=='upgrade':print(json.dumps({'database':str(migrate_database(args.source,args.new_database))}));return
    if args.action=='replay-owner-capture':
        payload=recorded_game_capture(args.capture_directory,args.research_save_id)
        create_database(args.database,args.research_save_id)
        with connect(args.database) as conn:ingest_capture(conn,payload)
        print(json.dumps(summarize(args.database),sort_keys=True));return
    if args.action in ('replay-ag01d','replay-player-families'):
        create_database(args.database,args.save_id)
        # Each source unit is independently atomic; a later failure preserves
        # earlier successful units for diagnosis rather than feigning a full batch.
        results=[]
        reader=replay_ag01d if args.action=='replay-ag01d' else replay_player_families
        for payload in reader(args.save_id,observed_at=args.observed_at):
            with connect(args.database) as conn:results.append(ingest_capture(conn,payload))
        print(json.dumps({'units':len(results),**summarize(args.database)},sort_keys=True));return
    if args.action=='init':create_database(args.database,args.save_id);print(json.dumps(summarize(args.database)));return
    create_database(args.database,args.save_id)
    with connect(args.database) as conn:
        ingest_synthetic_capture(conn,synthetic_payload(save_id=args.save_id))
    print(json.dumps(summarize(args.database),sort_keys=True))

if __name__=='__main__':main()
