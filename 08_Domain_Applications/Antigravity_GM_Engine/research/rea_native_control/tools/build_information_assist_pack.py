"""Freeze a new auxiliary workspace from explicit Git blobs. No game access."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

D = '08_Domain_Applications/Antigravity_GM_Engine/'
C = D + 'research/rea_native_control/'
R = '01_os/07_content/_runs/run-20261028-role-native-execution-system-001/'
PACKAGE = C + 'auxiliary/gemini_information_20261028/'
WORLD = 'a3927fb150a213201e404cca043ced4f57409bd1'


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, check=True).stdout


def build(repo, destination, source, manifest_out, skill_root):
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('Explicit full source commit required')
    if destination.exists() or manifest_out.exists():
        raise ValueError('Destination and retained manifest must be new')
    if destination.resolve().is_relative_to(repo.resolve()):
        raise ValueError('Auxiliary workspace must be outside main checkout')
    if git(repo, 'rev-parse', source + '^{commit}').decode().strip() != source:
        raise ValueError('Not a commit')
    entries = []

    def blob(commit, origin, target):
        raw = git(repo, 'show', commit + ':' + origin)
        blob_id = git(repo, 'rev-parse', commit + ':' + origin).decode().strip()
        entries.append((target, raw, {'kind': 'git_blob', 'commit': commit, 'path': origin, 'blob': blob_id}))

    for name in ('AGENTS.md', 'SCOPE.json', 'REA_STATIC_LEARNING_GUIDE_ZH.md', 'GEMINI_PROMPT_ZH.md', 'README.md'):
        blob(source, PACKAGE + name, name)
    blob(source, C + 'tools/review_aux_submission.py', 'tools/review_aux_submission.py')
    blob(source, C + 'DECISION_INFORMATION_DISCOVERY_20261028.md', 'inputs/DECISION_INFORMATION_DISCOVERY_20261028.md')
    for name in ('recover_functions.py', 'recover_entry_windows.py', 'recover_enum_registration.py', 'recover_rip_targets.py'):
        blob(source, C + 'tools/' + name, 'inputs/research/rea_native_control/tools/' + name)
    blob(source, D + 'research/rea_native_action/pe_local.py', 'inputs/research/rea_native_action/pe_local.py')
    # Exact named retained files; no unrelated captures or private data.
    evidence = ('decision_information_discovery_001.json', 'decision_information_native_bodies_002.json',
                'decision_information_discovery_refined_003.json', 'decision_information_shotchart_types_004.json',
                'decision_information_player_shot_callers_005.json', 'decision_information_shot_entity_consumers_006.json',
                'decision_information_shot_enum_refs_007.json')
    for name in evidence:
        blob(source, R + 'static/' + name, 'inputs/static/' + name)
    for name in ('competition_views.py', 'query.py', 'schedule_reader.py', 'period_stats_reader.py',
                 'stat_reference_native_profile.json', 'DIFFICULT_ITEMS.md', 'BASELINE_HANDOFF.md',
                 'REVIEW_FIXES_F01_F02_F03.md'):
        blob(WORLD, D + 'world_data_prototype/' + name, 'inputs/world_data_reference_only/' + name)
    for name in ('SKILL.md', 'references/connection-and-recovery.md', 'references/native-and-artifacts.md'):
        path = skill_root / name
        raw = path.read_bytes()
        entries.append(('inputs/rea_skill_v49/' + name, raw, {'kind': 'local_skill_snapshot', 'path': str(path)}))
    scope = json.loads(next(raw for path, raw, _ in entries if path == 'SCOPE.json'))
    template = {'schema_version': 'nba2k22.auxiliary_submission.v1', 'packet_id': scope['packet_id'],
                'target_sha256': scope['target_sha256'], 'owner_source_commit': source,
                'input_manifest_sha256': 'REPLACE_WITH_ACTUAL_INPUT_MANIFEST_SHA256',
                'producer': {'observed_model': 'UNKNOWN', 'subagents_used': False}, 'status': 'NO_FINDINGS',
                'task_results': [{'task_id': task, 'status': 'NOT_ATTEMPTED', 'reason': 'Template only; not executed'}
                                 for task in scope['task_ids']],
                'claims': [], 'tool_trace': 'tool_calls.jsonl',
                'artifacts': [{'path': 'tool_calls.jsonl', 'kind': 'call_trace', 'bytes': 0,
                               'sha256': hashlib.sha256(b'').hexdigest()}],
                'template_notice': 'Scaffold only. Write real outputs before changing task dispositions.'}
    entries.append(('SUBMISSION_TEMPLATE.json', encoded(template), {'kind': 'builder_generated_scaffold', 'source_commit': source}))
    claim = {'id': 'REPLACE_UNIQUE_ID', 'task_id': 'A01_SHOT_ENUMS', 'kind': 'UNKNOWN',
             'statement': 'Replace with bounded conclusion', 'evidence_level': 'UNKNOWN',
             'provenance': 'OWNER_INPUT_REVIEW', 'source_rvas': [], 'evidence_refs': ['report.md'],
             'coverage_limit': 'Replace with exact inspected scope', 'uncertainty': 'Replace with remaining gaps',
             'counterexample': {'status': 'NOT_RUN', 'reason': 'Replace with actual reason'}}
    entries.append(('CLAIM_TEMPLATE.json', encoded(claim), {'kind': 'builder_generated_scaffold', 'source_commit': source}))
    rows = [{'path': path, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'source': origin}
            for path, raw, origin in entries]
    manifest = {'schema_version': 'nba2k22.auxiliary_input_manifest.v1', 'packet_id': scope['packet_id'],
                'target_sha256': scope['target_sha256'], 'owner_source_commit': source,
                'world_reference_commit': WORLD, 'game_access': False, 'files': rows,
                'isolation': 'Directory convention, not OS sandbox; no auxiliary process started'}
    destination.mkdir(parents=True, exist_ok=False)
    for path, raw, origin in entries:
        output = destination / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
    for name in ('work', 'submissions'):
        (destination / name).mkdir()
    manifest_raw = encoded(manifest)
    (destination / 'INPUT_MANIFEST.json').write_bytes(manifest_raw)
    manifest_out.write_bytes(manifest_raw)
    return {'destination': str(destination), 'owner_source_commit': source,
            'input_files': len(rows), 'manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
            'gemini_started': False, 'game_access': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('repo', 'destination', 'manifest-out', 'skill-root'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.repo, args.destination, args.source, args.manifest_out, args.skill_root), ensure_ascii=False))
