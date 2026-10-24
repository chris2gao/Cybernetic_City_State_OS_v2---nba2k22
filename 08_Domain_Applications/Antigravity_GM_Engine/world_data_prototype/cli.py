"""Minimal synthetic-only world-data prototype command line."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import create_database,connect,ingest_synthetic_capture,summarize


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
    parser=argparse.ArgumentParser(description='Isolated NBA2K22 synthetic SQLite prototype (NO game access)')
    sub=parser.add_subparsers(dest='action',required=True)
    init=sub.add_parser('init');init.add_argument('database');init.add_argument('save_id')
    sub.add_parser('smoke')
    demo=sub.add_parser('demo');demo.add_argument('database');demo.add_argument('save_id')
    args=parser.parse_args()
    if args.action=='smoke': print(json.dumps(smoke(),sort_keys=True));return
    if args.action=='init':create_database(args.database,args.save_id);print(json.dumps(summarize(args.database)));return
    create_database(args.database,args.save_id)
    with connect(args.database) as conn:
        ingest_synthetic_capture(conn,synthetic_payload(save_id=args.save_id))
    print(json.dumps(summarize(args.database),sort_keys=True))

if __name__=='__main__':main()
