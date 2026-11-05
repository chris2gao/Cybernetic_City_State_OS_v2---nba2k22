"""One-shot offline JSON entrypoint for BIC WorldData baselines."""
import argparse
import json
from pathlib import Path

from bic_baseline import player_baseline, team_baseline, coverage_report, badge_intelligence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=('player', 'team'))
    parser.add_argument('database', type=Path)
    parser.add_argument('entity_id')
    parser.add_argument('--save-id', required=True)
    parser.add_argument('--season-id', required=True)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--max-age-seconds', type=float, default=86400)
    args = parser.parse_args()
    reader = player_baseline if args.kind == 'player' else team_baseline
    try:
        result = reader(args.database, args.entity_id, save_id=args.save_id,
                        season_id=args.season_id, as_of=args.as_of,
                        max_age_seconds=args.max_age_seconds)
        output = {'baseline': result, 'coverage': coverage_report(result)}
        if args.kind == 'player':
            output['badge_intelligence'] = badge_intelligence(result)
        print(json.dumps(output, ensure_ascii=False, allow_nan=False))
    except (ValueError, PermissionError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
