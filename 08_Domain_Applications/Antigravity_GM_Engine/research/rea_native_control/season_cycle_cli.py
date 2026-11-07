#!/usr/bin/env python3
"""Command-Line Interface for NBA2K22 Human-Controlled Season Closed Loop.

Provides clear, human-invocable commands conforming to human_trigger_playbook.md:
- init
- cycle
- seal
- authorize
- advance-check
- status
- pause
- resume
"""

import argparse
import json
from pathlib import Path
import sys

_DIR = Path(__file__).resolve().parent
_WD_DIR = _DIR.parents[1] / "world_data_prototype"
if str(_WD_DIR) not in sys.path:
    sys.path.insert(0, str(_WD_DIR))
if str(_DIR) not in sys.path:
    sys.path.append(str(_DIR))

from season_cycle_host import SeasonCycleHost


def main():
    parser = argparse.ArgumentParser(description="NBA2K22 Human Season Host CLI")
    parser.add_argument("--approved-role-manifest-sha256",
                        help="Digest of the exact role manifest approved separately by the Human")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize season binding and baseline capture")
    p_init.add_argument("--save-dir", required=True, help="Path to save directory containing save.json")
    p_init.add_argument("--filename", default="MyLEAGUE0003", help="Declared loaded filename")
    p_init.add_argument("--pid", default="auto", help="Game process PID or auto")
    p_init.add_argument("--mock-date", default=None, help="Mock in-game date for offline testing")
    p_init.add_argument("--force-new-worldline", action="store_true", help="Force new worldline branch DB")

    # cycle
    p_cycle = subparsers.add_parser("cycle", help="Start decision cycle and gather candidate intents")
    p_cycle.add_argument("--cycle-id", required=True, help="Cycle identifier (e.g. cycle-001)")
    p_cycle.add_argument("--force", action="store_true", help="Force cycle even if calendar hasn't moved")
    p_cycle.add_argument("--mock-date", default=None, help="Mock in-game date for offline testing")
    p_cycle.add_argument("--intents-file", default=None, help="Optional JSON file containing candidate intents")

    # seal
    p_seal = subparsers.add_parser("seal", help="Preflight CAS, bridge batch, and freeze/seal decisions into digest")
    p_seal.add_argument("--cycle-id", required=True, help="Cycle identifier")

    # authorize
    p_auth = subparsers.add_parser("authorize", help="Authorize execution with exact plan_digest")
    p_auth.add_argument("--cycle-id", required=True, help="Cycle identifier")
    p_auth.add_argument("--digest", required=True, help="Exact plan_digest returned by seal")
    p_auth.add_argument("--live-batch-approval", type=Path, help="Private Human receipt for the exact live batch")
    p_auth.add_argument("--approved-live-batch-sha256", help="Receipt digest supplied separately by the Human")

    # advance-check
    p_adv = subparsers.add_parser("advance-check", help="Verify game calendar advance after in-game sim")
    p_adv.add_argument("--next-cycle-id", required=True, help="Next cycle identifier")
    p_adv.add_argument("--mock-date", default=None, help="Mock advanced date")

    # status
    p_status = subparsers.add_parser("status", help="Inspect current host lifecycle and outbox status")

    # pause
    p_pause = subparsers.add_parser("pause", help="Pause season closed loop")

    # resume
    p_resume = subparsers.add_parser("resume", help="Resume season closed loop")

    args = parser.parse_args()
    host = SeasonCycleHost(approved_role_manifest_sha256=args.approved_role_manifest_sha256)

    try:
        if args.command == "init":
            res = host.initialize_season(
                save_directory=args.save_dir,
                loaded_filename=args.filename,
                pid=args.pid,
                mock_game_date=args.mock_date,
                force_new_worldline=args.force_new_worldline
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "cycle":
            candidate_intents = None
            if args.intents_file:
                candidate_intents = json.loads(Path(args.intents_file).read_text(encoding="utf-8"))
            res = host.start_cycle(
                cycle_id=args.cycle_id,
                force=args.force,
                mock_game_date=args.mock_date,
                candidate_intents=candidate_intents
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "seal":
            res = host.seal_cycle_decisions(cycle_id=args.cycle_id)
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "authorize":
            res = host.authorize_and_execute(
                cycle_id=args.cycle_id,
                plan_digest=args.digest,
                live_batch_approval=args.live_batch_approval,
                approved_live_batch_sha256=args.approved_live_batch_sha256,
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "advance-check":
            res = host.advance_calendar_check(
                next_cycle_id=args.next_cycle_id,
                mock_advanced_date=args.mock_date
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "status":
            res = host.get_status()
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "pause":
            res = host.pause()
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.command == "resume":
            res = host.resume()
            print(json.dumps(res, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"status": "ERROR", "error_type": type(e).__name__, "reason": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
