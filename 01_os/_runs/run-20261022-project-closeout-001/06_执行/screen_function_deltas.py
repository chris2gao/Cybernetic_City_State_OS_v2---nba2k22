"""Read-only first-pass source/contract comparison, not semantic acceptance."""
import collections
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGET = Path(__file__).resolve().parents[1] / '02_信息收集'

def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8', errors='replace')[-1500:])
    return r.stdout

def tree(ref):
    result = {}
    for record in git('ls-tree', '-r', '-z', ref).split(b'\0'):
        if record:
            meta, path = record.split(b'\t', 1)
            mode, kind, sha = meta.split()
            if kind == b'blob' and mode in (b'100644', b'100755'):
                result[path.decode('utf-8')] = sha.decode()
    return result

def canonical(path):
    if path.startswith('08_os/'):
        return '01_os/' + path[6:]
    return path

def relevant(path):
    normalized = canonical(path)
    if not normalized.startswith('01_os/'):
        return False
    if any('/' + part + '/' in normalized for part in ('_runs', '_communication', '_dev', 'fixtures')):
        return False
    return normalized.endswith(('.py', '.ps1', '.sh', '.yml', '.yaml', '.json'))

def main():
    inventory = json.loads((TARGET / '未合并分支快照_v1.json').read_text(encoding='utf-8'))
    base = git('rev-parse', 'HEAD').decode().strip()
    current = tree(base)
    names = collections.defaultdict(list)
    for path in current:
        names[Path(path).name].append(path)
    live = git('-c', 'core.sshCommand=ssh -o ConnectTimeout=20 -o BatchMode=yes',
               'ls-remote', '--heads', 'origin').decode().splitlines()
    remote_by_sha = collections.defaultdict(list)
    for line in live:
        sha, ref = line.split()
        remote_by_sha[sha].append(ref.removeprefix('refs/heads/'))
    rows = []
    for row in inventory['branches']:
        sha = row['head']
        common = git('merge-base', base, sha).decode().strip()
        candidate = tree(sha)
        changed = [p.decode('utf-8') for p in git('diff', '--name-only', '-z', common, sha).split(b'\0') if p]
        comparisons = []
        for path in changed:
            if path not in candidate or not relevant(path):
                continue
            counterpart = canonical(path)
            state = 'same_blob' if current.get(counterpart) == candidate[path] else ('different_blob' if counterpart in current else 'no_direct_counterpart')
            comparisons.append({'branch_path': path, 'canonical_path': counterpart,
                                'state': state, 'branch_blob': candidate[path],
                                'master_blob': current.get(counterpart),
                                'basename_candidates': names[Path(path).name] if counterpart not in current else []})
        counts = dict(collections.Counter(c['state'] for c in comparisons))
        result = {'id': row['id'], 'head': sha, 'refs': row['refs'],
                  'work_summary': row['work_summary'], 'online_branches_at_exact_head': remote_by_sha.get(sha, []),
                  'scoped_source_or_contract_counts': counts, 'comparisons': comparisons}
        rows.append(result)
        missing = [c['canonical_path'] for c in comparisons if c['state'] == 'no_direct_counterpart']
        print(json.dumps({'id': row['id'], 'online': bool(result['online_branches_at_exact_head']),
                          'counts': counts, 'missing_sample': missing[:4]}, ensure_ascii=False), flush=True)
    output = {'master': base, 'mapping': '08_os prefix to 01_os only; filename matches are possibilities, not equivalence',
              'limits': 'Counts are source/contract comparison clues, never proof of functionality missing or completed. Fixtures and traffic excluded; other historical root namespaces are not automatically mapped.',
              'live_remote_heads': {line.split()[1]: line.split()[0] for line in live}, 'branches': rows}
    (TARGET / '功能差异与线上版本初筛_v1.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Completed; offline candidate heads: ' + str(sum(not r['online_branches_at_exact_head'] for r in rows)))

if __name__ == '__main__':
    main()
