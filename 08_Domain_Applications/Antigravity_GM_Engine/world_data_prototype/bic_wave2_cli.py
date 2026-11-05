"""One-shot offline diagnosis and capability-plan JSON report."""
import argparse
import json
from pathlib import Path

from bic_baseline import player_baseline, team_baseline
from bic_diagnostics import diagnose_and_plan, diagnose_team
from bic_plans import native_capabilities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    parser.add_argument('player_id')
    parser.add_argument('--save-id', required=True)
    parser.add_argument('--season-id', required=True)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--team-id')
    parser.add_argument('--max-age-seconds', type=float, default=86400)
    parser.add_argument('--request', type=Path, help='JSON role_requirements and intents; optional candidate assumptions')
    args = parser.parse_args()
    scope = dict(save_id=args.save_id, season_id=args.season_id, as_of=args.as_of,
                 max_age_seconds=args.max_age_seconds)
    try:
        request = json.loads(args.request.read_bytes()) if args.request else {}
        player = player_baseline(args.database, args.player_id, **scope)
        try:
            catalog = native_capabilities(Path(__file__).resolve().parents[3])
        except FileNotFoundError:
            catalog = None
        result = {'player': diagnose_and_plan(player, catalog=catalog,
                  role_requirements=request.get('role_requirements', ()), intents=request.get('intents', ()),
                  required_play_codes=request.get('required_play_codes', ()))}
        if args.team_id:
            team = team_baseline(args.database, args.team_id, **scope)
            result['team'] = diagnose_team(team, [player], roles={args.player_id: request.get('role_requirements', ())},
                                           team_requirements=request.get('team_requirements', ()))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    except (ValueError, PermissionError, FileNotFoundError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
