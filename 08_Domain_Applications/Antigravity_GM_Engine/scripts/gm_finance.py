"""Explicit derived finance runs; never capture, approve or execute game actions."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from gm_data_access import AccessError
from gm_data_access.snapshots import identifier
from gm_data_access.finance_inputs import load_inputs
from gm_core.finance_projection import project
from gm_core.finance_scenarios import compare
from gm_workbench.store import Store


def read_input(path):
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise ValueError('INPUT_TOO_LARGE')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def summary(run, team=None):
    teams = [t for t in run['teams'] if team is None or str(t['team_id']) == team or t['team'] == team.upper()]
    if team is not None and not teams:
        raise ValueError('TEAM_NOT_FOUND')
    return dict(status='ANALYSIS_ONLY', run_id=run['run_id'], source_binding=run['source_binding'],
        calculation_version=run['calculation_version'], base_season=run['base_season'],
        horizon_seasons=run['horizon_seasons'], season_anchor_evidence=run['season_anchor_evidence'],
        default_projection_assumption='SLOT1_BASE_SEASON_THEN_SEQUENTIAL_NOT_CERTIFIED',
        teams=[dict(team_id=t['team_id'], team=t['team'], years=[dict(season=y['season'],
            projected_salary=y['projected_salary_total']['value'], known_salary_subtotal=y['known_salary_subtotal']['value'],
            projected_known_subtotal=y['projected_known_subtotal']['value'], coverage=y['projected_salary_total']['coverage'],
            uncertain_contract_count=y['uncertain_contract_count'], finance_eligibility=y['finance_eligibility']['status'],
            signing_capacity=None) for y in t['years']]) for t in teams],
        scenarios=[dict(scenario_id=s['scenario_id'], kind=s['kind'], executor_readiness=s['executor_readiness']) for s in run.get('scenarios', [])])


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('project', 'compare', 'show', 'export', 'list'))
    p.add_argument('--career', required=True)
    p.add_argument('--batch')
    p.add_argument('--query-root', type=Path, default=ROOT/'database/query_snapshots')
    p.add_argument('--published-root', type=Path, default=ROOT/'published')
    p.add_argument('--workbench', type=Path, help='Derived gm_workbench.sqlite only; default database/workbench/<career>')
    p.add_argument('--run', help='Immutable finance run ID; optional new ID for project')
    p.add_argument('--base-season', help='YYYY-YYYY; default snapshot context')
    p.add_argument('--horizon', type=int, default=3)
    p.add_argument('--assumptions', type=Path, help='Explicit slot/year overrides, reference_lines and phase')
    p.add_argument('--policy', type=Path, help='External scenario policy; declared confirmation never authorizes game writes')
    p.add_argument('--scenario', help='compare: input JSON path; show: stored scenario ID')
    p.add_argument('--team')
    p.add_argument('--contracts', action='store_true', help='show: one team/season bounded contract drilldown')
    p.add_argument('--season')
    p.add_argument('--offset', type=int, default=0)
    p.add_argument('--limit', type=int, default=20)
    p.add_argument('--output', type=Path, help='export: directory; refuses overwrite')
    p.add_argument('--allow-local-audited', action='store_true')
    return p


def run(a):
    identifier(a.career)
    path = a.workbench or ROOT/'database/workbench'/a.career/'gm_workbench.sqlite'
    if not 1 <= a.limit <= 50 or not 0 <= a.offset <= 10000:
        raise ValueError('INVALID_RESULT_WINDOW')
    if a.action == 'project':
        inputs = load_inputs(a.query_root, a.published_root, a.career, a.batch, a.allow_local_audited)
        result = project(inputs, a.base_season, a.horizon,
                         read_input(a.assumptions) if a.assumptions else None,
                         read_input(a.policy) if a.policy else None, a.run)
        with Store(path) as store:
            store.save_run(result)
        return summary(result)
    with Store(path, readonly=a.action != 'compare') as store:
        if a.action == 'list':
            return dict(status='ANALYSIS_ONLY', runs=store.list_runs(a.career))
        if not a.run:
            raise ValueError('RUN_ID_REQUIRED')
        result = store.load_run(a.run)
        if result['source_binding']['career_id'] != a.career:
            raise ValueError('CAREER_DIFFERS_FROM_FINANCE_RUN')
        if a.action == 'compare':
            if not a.scenario:
                raise ValueError('SCENARIO_FILE_REQUIRED')
            scenario = compare(result, read_input(a.scenario))
            store.save_scenario(scenario)
            return dict(status='ANALYSIS_ONLY', source_binding=result['source_binding'], run_id=a.run,
                        scenario_id=scenario['scenario_id'], alternatives=scenario['alternatives'],
                        executor_readiness=scenario['executor_readiness'], approval_status='NOT_REQUESTED',
                        affected_team_years=len(scenario['team_year_deltas']),
                        next_step='show --scenario ID [--team TEAM] for bounded year deltas')
        if a.action == 'show':
            if a.scenario:
                matches = [s for s in result['scenarios'] if s['scenario_id'] == a.scenario]
                if not matches:
                    raise ValueError('SCENARIO_NOT_FOUND')
                s = matches[0]
                rows = [y for y in s['team_year_deltas'] if a.team is None or y['team'] == a.team.upper() or str(y['team_id']) == a.team]
                return dict(status='ANALYSIS_ONLY', source_binding=result['source_binding'], scenario_id=a.scenario,
                            approval_status='NOT_REQUESTED', executor_readiness=s['executor_readiness'],
                            unknown_reasons=s['unknown_reasons'], opportunity_cost=s['opportunity_cost'],
                            rows=rows[a.offset:a.offset+a.limit], next_offset=a.offset+a.limit if len(rows)>a.offset+a.limit else None)
            if a.contracts:
                if not a.team or not a.season:
                    raise ValueError('CONTRACT_DRILLDOWN_REQUIRES_TEAM_AND_SEASON')
                teams = [t for t in result['teams'] if t['team'] == a.team.upper() or str(t['team_id']) == a.team]
                rows = [y for t in teams for y in t['years'] if y['season'] == a.season]
                if len(rows) != 1:
                    raise ValueError('TEAM_SEASON_NOT_FOUND')
                entries = rows[0]['observed_slot_amounts']
                return dict(status='ANALYSIS_ONLY', source_binding=result['source_binding'],
                            rows=entries[a.offset:a.offset+a.limit], total_rows=len(entries),
                            next_offset=a.offset+a.limit if len(entries)>a.offset+a.limit else None)
            return summary(result, a.team)
        output = a.output or ROOT/'_exports/finance'/a.run
        output = output.resolve()
        if output.exists():
            raise ValueError('EXPORT_DIRECTORY_EXISTS')
        if any(p.casefold() in {'saves','query_snapshots','published','seasons'} for p in output.parts):
            raise ValueError('EXPORT_CANNOT_TARGET_FACTS')
        output.mkdir(parents=True)
        compact = summary(result)
        (output/'summary.json').write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = ['# Finance analysis '+a.run, '', 'ANALYSIS_ONLY — slot-sequence scenarios; signing capacity UNKNOWN.', '',
                 'Batch: '+result['source_binding']['batch_id'], '', '| Team | Season | Projected salary | Coverage |', '| --- | --- | ---: | --- |']
        for team in compact['teams']:
            lines.extend(f"| {team['team']} | {y['season']} | {y['projected_salary']} | {y['coverage']} |" for y in team['years'])
        (output/'summary.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
        return dict(status='EXPORTED_ANALYSIS_ONLY', output=str(output), source_binding=result['source_binding'])


def main():
    try:
        print(json.dumps(run(parser().parse_args()), ensure_ascii=False, allow_nan=False))
        return 0
    except (AccessError, ValueError, KeyError, TypeError, OSError, sqlite3.Error) as e:
        print(json.dumps(dict(status=getattr(e, 'code', 'FINANCE_INPUT_OR_STORE_ERROR'), message=str(e)[:220]), ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
