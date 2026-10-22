"""Bounded, offline verification for the fixed FINAL-CODEX documentation audit.

Default: Git blobs + report JSON/Markdown only, no game or database imports.
Optional --run-existing-tests: export eight pinned files into a fresh temp
directory, with no memory.py, production databases or upload modules available.
"""
import argparse
import ast
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = '0eaf44f4ff06e7f2cf3c9d078b8f4b064fd2e1f5'
CANDIDATE = 'b4e17e1419b1cf9105f0a68dba7719e4d407104b'
SEALED = '4b995e70e20659ce7d6198da16bde21b8a606001'
PREFIX = 'docs/development_reviews/FINAL_CODEX_'
MATRIX = PREFIX + 'CAPABILITY_MATRIX_20261021_V1.json'
MAIN = PREFIX + 'NATIVE_IO_COVERAGE_AUDIT_20261021_V1.md'
GAPS = PREFIX + 'DEV28_GAP_REGISTER_20261021_V1.md'
MATCH = PREFIX + 'MATCH_HISTORY_BRANCH_AUDIT_20261021_V1.md'
ALLOWED = {MATRIX, MAIN, GAPS, MATCH,
           'docs/33_DEVELOPMENT_BASELINE_PROMPT.md',
           'tools/audits/verify_final_codex_20261021.py'}
REQUIRED = {'family_id', 'research_reference', 'game_information_or_action',
            'native_profile_paths', 'code_implementation_paths',
            'ui_evidence_status', 'static_registry_status',
            'existing_runtime_evidence', 'formal_batch_capture_status',
            'model_query_status', 'bounded_execution_status', 'save_reload_status',
            'evidence_refs', 'current_blocker', 'dev28_candidate_package',
            'priority', 'confidence'}
EXPECTED = {'UNMERGED_BRANCH_CANDIDATE': 3, 'PRIOR_BATCH_PARTIAL': 16,
            'IMPLEMENTED_UNPUBLISHED': 7, 'SOURCE_ONLY_BLOCKED': 1,
            'REFERENCE_OR_UNKNOWN': 13}
TEST_FILES = ('src/match_history_reader.py', 'src/coach_locator.py',
              'src/coach_codec.py', 'src/config.py', 'src/save_context.py',
              'scripts/query_match_history.py', 'tests/test_match_history.py',
              'database/match_history_schema.sql')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                          check=True).stdout


def blob(commit, path):
    return git('show', commit + ':' + path)


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def verify():
    m = load(MATRIX)
    assert m['audit_base_commit'] == BASE
    assert m['candidate_branch_commit'] == CANDIDATE
    assert m['candidate_sealed_commit'] == SEALED
    assert m['status'] == 'FINAL_CODEX_AUDIT_COMPLETED_PENDING_PLAYER_REVIEW'
    assert m['task_status'] == 'TASK_CLOSED'
    assert not m['live_game_access_performed']
    families = m['families']
    ids = [f['family_id'] for f in families]
    assert len(ids) == len(set(ids)) == 40
    assert set(ids) == {f'F{i:02}' for i in range(1, 41)}
    distribution = dict(Counter(f['audit_category'] for f in families))
    assert distribution == EXPECTED == m['status_distribution']
    research_path = 'docs/game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json'
    research = json.loads(blob(BASE, research_path))
    source_groups = {f['id']: f for f in research['capability_groups']}
    gaps_path = 'docs/game_mechanics/catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json'
    gaps = json.loads(blob(BASE, gaps_path))['open_gaps']
    mapped = m['inherited_gap_mapping']
    assert len(mapped) == len({g['gap_id'] for g in mapped}) == 20
    assert {g['gap_id'] for g in mapped} == {g['id'] for g in gaps}
    for g, entry in zip(gaps, mapped):
        assert entry['gap_id'] == g['id']
        assert entry['source_priority'] == g['priority']
        assert entry['source_status'] == g['status']
        assert entry['families'] == [f['family_id'] for f in families
                                     if g['id'] in f['research_reference']['inherited_gap_ids']]
    path_checks = 0
    symbol_checks = 0
    for f in families:
        assert not REQUIRED - set(f)
        ref = f['research_reference']
        sf = source_groups[f['family_id']]
        assert ref['anchors'] == sf['reference_anchors']
        assert ref['inherited_gap_ids'] == sf['unknown_and_handoff_gaps']
        for p in f['native_profile_paths']:
            assert blob(BASE, p)
            path_checks += 1
        entries = f['implementation_entry_points']
        assert len(entries) == len(f['code_implementation_paths'])
        for coded, e in zip(f['code_implementation_paths'], entries):
            path, sep, commit = coded.partition('@')
            commit = commit if sep else BASE
            assert e['path'] == path and e['commit'] == commit
            data = blob(commit, path)
            path_checks += 1
            if path.endswith('.py'):
                tree = ast.parse(data.decode('utf-8-sig'))
                symbols = [{'symbol': n.name, 'line': n.lineno} for n in tree.body
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                assert symbols == e['static_symbols']
                symbol_checks += len(symbols)
        for key in f['evidence_refs']:
            assert key in m['evidence_catalog']
    for e in m['evidence_catalog'].values():
        if e.get('commit') and e.get('line'):
            lines = blob(e['commit'], e['path']).decode('utf-8-sig').splitlines()
            assert e['symbol_or_key'] in lines[e['line'] - 1]
    main_text = (ROOT / MAIN).read_text(encoding='utf-8')
    assert re.findall(r'^\| (F\d{2}) \|', main_text, flags=re.M) == ids
    gap_text = (ROOT / GAPS).read_text(encoding='utf-8')
    assert re.findall(r'^\| (D06-G\d{2}) /', gap_text, flags=re.M) == [g['id'] for g in gaps]
    for path in (MAIN, GAPS, MATCH):
        text = (ROOT / path).read_text(encoding='utf-8')
        assert m['status'] in text and 'TASK_CLOSED' in text
    for key, count in distribution.items():
        assert f'{key}={count}' in main_text
    assert git('diff', '--name-only', CANDIDATE, SEALED) == b''
    changed = git('diff', '--name-only', BASE, '--').decode('utf-8').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').decode('utf-8').splitlines()
    assert not (set(changed) | set(untracked)) - ALLOWED, (changed, untracked)
    for path in ALLOWED:
        assert (ROOT / path).is_file(), path
    tests = m['existing_test_evidence']
    assert tests['source_commit'] == CANDIDATE and tests['returncode'] == 0
    assert '4 passed in 0.08s' in tests['stdout']
    return {'status': 'PASS_STATIC_AUDIT_ARTIFACT_CONSISTENCY',
            'families': len(families), 'gaps': len(gaps),
            'status_distribution': distribution,
            'pinned_path_checks': path_checks,
            'static_symbol_checks': symbol_checks,
            'candidate_seal_content_diff': 'EMPTY',
            'changed_paths_within_allowed_scope': True,
            'historical_tests': '4 passed; evidence retained, not rerun',
            'game_access': False, 'database_access': False}


def run_existing_tests():
    directory = Path(tempfile.mkdtemp(prefix='final_codex_pinned_four_'))
    for name in TEST_FILES:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob(CANDIDATE, name))
    env = os.environ.copy()
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONUTF8='1')
    env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-q', '-p',
                             'no:cacheprovider', 'tests/test_match_history.py'],
                            cwd=directory, env=env, capture_output=True,
                            text=True, encoding='utf-8')
    return {'temp_directory': str(directory), 'source_commit': CANDIDATE,
            'returncode': result.returncode, 'stdout': result.stdout,
            'stderr': result.stderr}


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-existing-tests', action='store_true')
    args = parser.parse_args()
    report = verify()
    if args.run_existing_tests:
        report['new_test_run'] = run_existing_tests()
        if report['new_test_run']['returncode']:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            raise SystemExit(1)
    print(json.dumps(report, ensure_ascii=False, indent=2))
