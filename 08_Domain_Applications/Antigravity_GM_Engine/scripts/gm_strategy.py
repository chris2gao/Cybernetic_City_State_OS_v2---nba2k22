"""Explicit strategy candidates, append-only analysis revisions and small exports."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from gm_core.knowledge import Knowledge, read_json
from gm_core.strategy_state import initialize, validate
from gm_data_access.knowledge_inputs import load_context
from gm_data_access.snapshots import identifier
from gm_data_access import AccessError
from gm_workbench.store import Store


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('init', 'save', 'show', 'list', 'export'))
    p.add_argument('--career')
    p.add_argument('--batch')
    p.add_argument('--team')
    p.add_argument('--revision', type=int)
    p.add_argument('--expected-revision', type=int)
    p.add_argument('--input', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--workbench', type=Path)
    p.add_argument('--query-root', type=Path, default=ROOT/'database/query_snapshots')
    p.add_argument('--published-root', type=Path, default=ROOT/'published')
    p.add_argument('--allow-local-audited', action='store_true')
    return p


def new_output(path):
    path = path.resolve()
    if {p.casefold() for p in path.parts}.intersection({'saves', 'query_snapshots', 'published', 'seasons'}):
        raise ValueError('STRATEGY_OUTPUT_MUST_NOT_BE_FACTS_OR_FORMAL_SEASON')
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def brief(s):
    return {k: s[k] for k in ('state_id', 'team_id', 'team_abbr', 'revision', 'supersedes_state_id',
                              'source_binding', 'finance_run_id', 'finance_alignment', 'status', 'created_at')}


def run(a):
    knowledge = Knowledge(ROOT/'web_gm/knowledge')
    state = read_json(a.input) if a.action == 'save' and a.input else None
    career = a.career or (state.get('career_id') if state else None)
    if not career:
        raise ValueError('CAREER_REQUIRED')
    identifier(career)
    path = a.workbench or ROOT/'database/workbench'/career/'gm_workbench.sqlite'
    if a.action == 'init':
        context = load_context(a.query_root, a.published_root, ROOT/'config/coach_tactics_profile.json',
                               career, a.batch, a.allow_local_audited)
        states = initialize(context, knowledge)
        output = new_output(a.output or ROOT/'_exports'/('strategy_candidates_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')))
        for s in states:
            validate(s, knowledge)
            write_json(output/(s['team_abbr']+'.json'), s)
        write_json(output/'index.json', dict(status='UNASSESSED_CANDIDATES_ONLY', source_binding=context['source_binding'],
                                           states=[brief(s) for s in states]))
        return dict(status='UNASSESSED_CANDIDATES_ONLY', candidate_count=len(states), assessed_count=0,
                    output=str(output), source_binding=context['source_binding'])
    if a.action == 'save':
        if state is None or a.expected_revision is None:
            raise ValueError('INPUT_AND_EXPECTED_REVISION_REQUIRED')
        if career != state['career_id']:
            raise ValueError('STRATEGY_CAREER_MISMATCH')
        with Store(path) as store:
            result = store.save_state(state, a.expected_revision, knowledge)
        return dict(status='ANALYSIS_SAVED', state=brief(result))
    with Store(path, readonly=True) as store:
        if a.action == 'show':
            if not a.team:
                raise ValueError('TEAM_REQUIRED')
            return store.load_state(career, a.team, a.revision)
        states = store.list_states(career)
        if a.action == 'list':
            return dict(states=[brief(s) for s in states], count=len(states),
                        assessed_count=sum(s['status'] != 'UNASSESSED' for s in states))
        output = new_output(a.output or ROOT/'_exports'/('strategy_export_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')))
        write_json(output/'summary.json', dict(career_id=career, status='ANALYSIS_ONLY', states=[dict(brief(s),
            tactical_direction=s['tactical_direction'], change_conditions=s['change_conditions'],
            identity_reference=s['identity_reference']) for s in states]))
        return dict(status='ANALYSIS_EXPORT_ONLY', count=len(states), output=str(output), publication='NOT_REQUESTED')


def main():
    try:
        result = run(parser().parse_args())
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, AccessError) as exc:
        print(json.dumps(dict(status='ERROR', error=str(exc)), ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
