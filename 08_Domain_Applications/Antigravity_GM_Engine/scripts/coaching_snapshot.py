"""Explicit coaching-only read; never runs the production full capture pipeline."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("career-id","source-batch-id","game-season"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--game-date",help="Player-confirmed ISO date; required for formal snapshots")
    p.add_argument("--isolated-test",action="store_true")
    p.add_argument("--output",required=True,help="Local _exports JSON path")
    args=p.parse_args()
    from coaching_cli import export_path, write_json
    from gm_core.coaching import validate_context
    context=dict(career_id=args.career_id,source_batch_id=args.source_batch_id,
                 game_season=args.game_season,game_date=args.game_date,policy_id="PLAYER_RULES_20261017_V3")
    validate_context(context,args.isolated_test)
    output=export_path(args.output)
    from coach_locator import live_memory,CoachLocator
    from coaching_reader import coaching_snapshot
    mem=live_memory(read_only=True)
    try:
        snapshot=coaching_snapshot(CoachLocator(mem).calibrate(),context,
                    "ISOLATED_TEST" if args.isolated_test else "FORMAL_READ_ONLY")
        write_json(output,snapshot)
        print(json.dumps(dict(output=str(output),teams=len(snapshot["teams"]),
                              playbooks=len(snapshot["playbooks"]),status="OBSERVED_LIVE_READ_ONLY")))
    finally:
        mem.close()

if __name__=="__main__":
    main()
