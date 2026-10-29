"""Untrusted auxiliary submission screening. Never imports or executes submissions."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def safe_path(root, name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Invalid relative artifact path')
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} for p in path.parts):
        raise ValueError('Unsafe relative path')
    current = root
    for part in path.parts:
        current = current / part
        attrs = getattr(current.lstat(), 'st_file_attributes', 0)
        if current.is_symlink() or attrs & 0x400:
            raise ValueError('Symlink/reparse entry forbidden')
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError('Expected contained regular file')
    return current


def inventory(root):
    files = set()
    visited = 0
    for base, dirs, names in os.walk(root, followlinks=False):
        visited += len(dirs) + len(names)
        if visited > 128:
            raise ValueError('Submission inventory exceeds traversal budget')
        for name in dirs + names:
            path = Path(base) / name
            attrs = getattr(path.lstat(), 'st_file_attributes', 0)
            if path.is_symlink() or attrs & 0x400:
                raise ValueError('Symlink/reparse entry forbidden')
        files.update((Path(base) / name).relative_to(root).as_posix() for name in names)
    return files


def review(scope_path, manifest_path, bundle_root, submission_root):
    errors, hints = [], []
    try:
        for root in (bundle_root, submission_root):
            if root.is_symlink() or getattr(root.lstat(), 'st_file_attributes', 0) & 0x400:
                raise ValueError('Root symlink/reparse entry forbidden')
        scope = decode(scope_path.read_bytes())
        manifest_raw = manifest_path.read_bytes()
        manifest = decode(manifest_raw)
        if safe_path(bundle_root, 'INPUT_MANIFEST.json').read_bytes() != manifest_raw:
            raise ValueError('Bundle manifest differs from trusted Owner manifest')
        if manifest['packet_id'] != scope['packet_id'] or manifest['target_sha256'] != scope['target_sha256']:
            raise ValueError('Trusted manifest/scope mismatch')
        for row in manifest['files']:
            raw = safe_path(bundle_root, row['path']).read_bytes()
            if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
                raise ValueError('Frozen input changed: ' + row['path'])
        submission_file = safe_path(submission_root, 'submission.json')
        if submission_file.stat().st_size > scope['max_artifact_bytes']:
            raise ValueError('Submission JSON too large')
        obj = decode(submission_file.read_bytes())
        expected = {'schema_version': 'nba2k22.auxiliary_submission.v1', 'packet_id': scope['packet_id'],
                    'target_sha256': scope['target_sha256'], 'owner_source_commit': manifest['owner_source_commit'],
                    'input_manifest_sha256': sha(manifest_raw)}
        for key, value in expected.items():
            if obj.get(key) != value:
                raise ValueError('Submission mismatch: ' + key)
        if obj['producer']['subagents_used'] is not False or not obj['producer']['observed_model']:
            raise ValueError('Producer identity or single-agent declaration missing')
        if obj['status'] not in {'COMPLETE_WITH_GAPS', 'PARTIAL', 'NO_FINDINGS'}:
            raise ValueError('Unsupported submission status')
        tasks = obj['task_results']
        if {r['task_id'] for r in tasks} != set(scope['task_ids']) or len(tasks) != len(scope['task_ids']):
            raise ValueError('Every scoped task needs exactly one disposition')
        for row in tasks:
            if row['status'] not in {'EVIDENCE', 'UNKNOWN', 'NOT_ATTEMPTED'} or not row['reason']:
                raise ValueError('Invalid task disposition')
        artifacts = obj['artifacts']
        if len(artifacts) > scope['max_artifacts']:
            raise ValueError('Too many artifacts')
        names, total = set(), 0
        for row in artifacts:
            name = row['path']
            if name in names or name == 'submission.json':
                raise ValueError('Duplicate/reserved artifact')
            names.add(name)
            path = safe_path(submission_root, name)
            if path.suffix.lower() not in scope['allowed_suffixes']:
                raise ValueError('Unsupported artifact suffix')
            size = path.stat().st_size
            limit = scope['max_binary_bytes'] if path.suffix.lower() == '.bin' else scope['max_artifact_bytes']
            if size > limit:
                raise ValueError('Oversized artifact')
            raw = path.read_bytes()
            total += size
            if row['bytes'] != size or row['sha256'] != sha(raw):
                raise ValueError('Artifact hash/size mismatch: ' + name)
            if row['kind'] not in {'raw_tool_output', 'call_trace', 'reproducer', 'fixture', 'report', 'type_table'}:
                raise ValueError('Unsupported artifact kind')
        if total > scope['max_total_bytes'] or inventory(submission_root) != names | {'submission.json'}:
            raise ValueError('Oversized or unlisted submission files')
        artifact_map = {r['path']: r for r in artifacts}
        trace_name = obj['tool_trace']
        if trace_name not in names or artifact_map[trace_name]['kind'] != 'call_trace':
            raise ValueError('Missing call trace artifact')
        calls = []
        for line in safe_path(submission_root, trace_name).read_bytes().splitlines():
            if not line.strip():
                continue
            call = decode(line)
            if call['target_sha256'] != scope['target_sha256'] or not call['arguments'] or not call['outcome']:
                raise ValueError('Incomplete tool call')
            if not isinstance(call['arguments'], dict) or call['provenance'] not in scope['provenance']:
                raise ValueError('Invalid tool arguments/provenance')
            operation = (call['tool'] + ' ' + call['operation']).lower()
            if any(fragment in operation for fragment in scope['forbidden_tool_name_fragments']):
                raise ValueError('Forbidden operation in trace')
            if call['output_artifact'] not in names or artifact_map[call['output_artifact']]['kind'] != 'raw_tool_output':
                raise ValueError('Tool output is not retained raw evidence')
            calls.append(call)
        claims = obj['claims']
        if len(claims) > scope['max_claims'] or len({r['id'] for r in claims}) != len(claims):
            raise ValueError('Too many/duplicate claims')
        for row in claims:
            if row['task_id'] not in scope['task_ids'] or row['kind'] not in scope['claim_kinds']:
                raise ValueError('Out-of-scope claim')
            if row['evidence_level'] not in scope['evidence_levels'] or row['provenance'] not in scope['provenance']:
                raise ValueError('Unsupported maturity/provenance')
            if not all(row.get(k) for k in ('statement', 'coverage_limit', 'uncertainty')):
                raise ValueError('Claim lacks statement or boundaries')
            refs = row['evidence_refs']
            if not refs or any(ref not in names for ref in refs):
                raise ValueError('Claim evidence missing')
            if not isinstance(row['source_rvas'], list) or any(type(rva) is not int or not 0 <= rva < 0x70000000 for rva in row['source_rvas']):
                raise ValueError('Invalid source_rvas')
            if row['evidence_level'] == 'STATIC_FACT_CANDIDATE':
                if not row['source_rvas'] or not any(artifact_map[ref]['kind'] == 'raw_tool_output' for ref in refs):
                    raise ValueError('Static claim needs RVA and raw output')
                if not any(call['output_artifact'] in refs for call in calls):
                    raise ValueError('Static claim lacks matching trace')
            control = row['counterexample']
            if control['status'] == 'EXECUTED_OFFLINE':
                if control['artifact'] not in names or not control['reason']:
                    raise ValueError('Missing negative-control artifact/reason')
            elif control['status'] == 'NOT_RUN' and control['reason']:
                hints.append({'claim': row['id'], 'hint': 'MISSING_NEGATIVE_CONTROL'})
            else:
                raise ValueError('Invalid negative-control status')
            hints.append({'claim': row['id'], 'hint': 'OWNER_REPLAY_REQUIRED'})
        if any(row['status'] == 'EVIDENCE' and not any(c['task_id'] == row['task_id'] for c in claims) for row in tasks):
            raise ValueError('EVIDENCE task without claim')
    except (ValueError, KeyError, TypeError, OSError, AttributeError) as exc:
        errors.append(str(exc))
    return {'status': 'INVALID_SUBMISSION' if errors else 'READY_FOR_CODEX_TRIAGE',
            'semantic_acceptance': False, 'submitted_code_executed': False,
            'errors': errors, 'triage_hints': hints,
            'limits': 'Structure/hashes only; cannot authenticate tool logs, enforce OS isolation, or prove semantics.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('scope', 'manifest', 'bundle', 'submission'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = review(args.scope, args.manifest, args.bundle, args.submission)
    raw = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(raw, encoding='utf8')
    print(raw, end='')
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
