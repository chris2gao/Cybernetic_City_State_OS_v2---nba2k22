"""Minimal synthetic-only world-data prototype command line."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import create_database,connect,ingest_synthetic_capture,ingest_capture,summarize,migrate_v1,migrate_database
from readers import replay_ag01d,replay_player_families
from query import player_card,game_box,history,export_jsonl,inspect_source_capture,schedule
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
    game=sub.add_parser('game');game.add_argument('database');game.add_argument('game_id')
    hist=sub.add_parser('history');hist.add_argument('database');hist.add_argument('table');hist.add_argument('--entity-key');hist.add_argument('--entity-id');hist.add_argument('--limit',type=int,default=200)
    exp=sub.add_parser('export');exp.add_argument('database');exp.add_argument('table');exp.add_argument('destination');exp.add_argument('--limit',type=int,default=10000)
    mig=sub.add_parser('migrate-v1');mig.add_argument('source');mig.add_argument('new_database')
    upgrade=sub.add_parser('upgrade');upgrade.add_argument('source');upgrade.add_argument('new_database')
    owner=sub.add_parser('replay-owner-capture');owner.add_argument('capture_directory');owner.add_argument('database');owner.add_argument('research_save_id')
    inspect=sub.add_parser('inspect-source');inspect.add_argument('database');inspect.add_argument('unit_id')
    bound=sub.add_parser('init-save');bound.add_argument('save_directory');bound.add_argument('save_id');bound.add_argument('native_save_file')
    live=sub.add_parser('capture-live');live.add_argument('pid',type=int);live.add_argument('save_directory');live.add_argument('loaded_filename');live.add_argument('new_output_directory');live.add_argument('--game-index',type=int,default=0)
    saved_upgrade=sub.add_parser('upgrade-save');saved_upgrade.add_argument('save_directory');saved_upgrade.add_argument('loaded_filename')
    season_capture=sub.add_parser('capture-season');season_capture.add_argument('pid',type=int);season_capture.add_argument('save_directory');season_capture.add_argument('loaded_filename');season_capture.add_argument('new_output_directory')
    sched=sub.add_parser('schedule');sched.add_argument('database');sched.add_argument('--season-id');sched.add_argument('--status-code');sched.add_argument('--limit',type=int,default=2000)
    args=parser.parse_args()
    if args.action=='schedule':print(json.dumps(schedule(args.database,season_id=args.season_id,status_code=args.status_code,limit=args.limit),ensure_ascii=False));return
    if args.action=='upgrade-save':
        from live_world import upgrade_bound_save
        print(json.dumps(upgrade_bound_save(args.save_directory,args.loaded_filename)));return
    if args.action=='capture-season':
        from schedule_reader import capture_season
        print(json.dumps(capture_season(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory),ensure_ascii=False));return
    if args.action=='init-save':
        from live_world import initialize_save
        print(json.dumps(initialize_save(args.save_directory,args.save_id,args.native_save_file),ensure_ascii=False));return
    if args.action=='capture-live':
        from live_world import capture_live
        print(json.dumps(capture_live(args.pid,args.save_directory,args.loaded_filename,args.new_output_directory,args.game_index),ensure_ascii=False));return
    if args.action=='smoke': print(json.dumps(smoke(),sort_keys=True));return
    if args.action=='summary':print(json.dumps(summarize(args.database),sort_keys=True));return
    if args.action=='player':print(json.dumps(player_card(args.database,args.player_id),ensure_ascii=False));return
    if args.action=='game':print(json.dumps(game_box(args.database,args.game_id),ensure_ascii=False));return
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
