"""Read-only Git inventory; writes generated task evidence, never merges a branch."""
from __future__ import annotations
import argparse
import collections
import datetime
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                            encoding='utf-8', errors='strict')
    if check and result.returncode:
        raise RuntimeError(f'Git {args[0]} exited {result.returncode}: {result.stderr[-1500:]}')
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    args = parser.parse_args()
    base = git('rev-parse', '--verify', args.base + '^{commit}').stdout.strip()
    remote_lines = git('-c', 'core.sshCommand=ssh -o ConnectTimeout=20 -o BatchMode=yes',
                       'ls-remote', '--heads', 'origin').stdout.splitlines()
    remote = {line.split()[1]: line.split()[0] for line in remote_lines}
    if remote.get('refs/heads/master') != base:
        raise RuntimeError('Live remote master is not the requested inventory baseline')
    refs = []
    for line in git('for-each-ref', '--format=%(refname)%09%(objectname)', 'refs/heads').stdout.splitlines():
        name, sha = line.split('\t')
        refs.append({'source': 'local', 'name': name.removeprefix('refs/heads/'), 'head': sha})
    for name, sha in remote.items():
        git('cat-file', '-e', sha + '^{commit}')
        refs.append({'source': 'remote', 'name': name.removeprefix('refs/heads/'), 'head': sha})
    groups = {}
    merged = []
    for ref in refs:
        result = git('merge-base', '--is-ancestor', ref['head'], base, check=False)
        if result.returncode == 0:
            merged.append(ref)
        elif result.returncode == 1:
            groups.setdefault(ref['head'], []).append(ref)
        else:
            raise RuntimeError(result.stderr)
    rows = []
    for sha, names in groups.items():
        logs = git('log', '--reverse', '--format=%H%x09%cI%x09%s', base + '..' + sha).stdout.splitlines()
        commits = []
        for line in logs:
            oid, date, subject = line.split('\t', 2)
            commits.append({'sha': oid, 'committer_date': date, 'subject': subject})
        times = [datetime.datetime.fromisoformat(c['committer_date']) for c in commits]
        paths = git('diff', '--name-only', '-z', base, sha).stdout.rstrip('\0').split('\0')
        paths = [p for p in paths if p]
        cherry = git('cherry', base, sha).stdout.splitlines()
        run_records = []
        for path in paths:
            if path.startswith('01_os/_runs/') and path.endswith('/run.yml'):
                content = git('show', sha + ':' + path, check=False)
                if content.returncode == 0:
                    fields = [line for line in content.stdout.splitlines()
                              if line.startswith(('task_id:', 'status:', 'lifecycle:', 'current_phase:'))]
                    run_records.append({'path': path, 'fields': fields})
        folders = collections.Counter('/'.join(p.split('/')[:3]) for p in paths)
        rows.append({'head': sha, 'refs': names, 'first_unique_commit_time': min(times).isoformat(),
                     'latest_unique_commit_time': max(times).isoformat(),
                     'unmerged_commit_count': len(commits), 'commits': commits,
                     'patch_new': sum(c.startswith('+ ') for c in cherry),
                     'patch_equivalent_in_master': sum(c.startswith('- ') for c in cherry),
                     'net_changed_path_count': len(paths), 'changed_paths': paths,
                     'top_path_groups': folders.most_common(8), 'run_records': run_records})
    rows.sort(key=lambda r: (datetime.datetime.fromisoformat(r['first_unique_commit_time']), r['head']))
    for row in rows:
        row['contained_by'] = [other['head'] for other in rows
                               if other is not row and row['head'] in {c['sha'] for c in other['commits']}]
    result = {'baseline_master': base, 'live_remote_ref_count': len(remote),
              'local_ref_count': sum(r['source'] == 'local' for r in refs),
              'unmerged_ref_count': sum(len(r['refs']) for r in rows),
              'distinct_unmerged_heads': len(rows), 'merged_refs': merged, 'branches': rows,
              'method': 'All local heads and freshly read live remote heads; strict ancestry plus Git cherry patch equivalence. No stale remote-tracking-only refs. Dates use earliest unmerged committer timestamp; not inferred task completion time.'}
    target = Path(__file__).resolve().parents[1] / '02_信息收集'
    target.mkdir(exist_ok=True)
    (target / '未合并分支快照_v1.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    md = ['# 未合并分支清单（供 Human 逐项决定）', '', f'比较基准 master：`{base}`。', '',
          f'枚举 {len(remote)} 个实时远端分支和 {result["local_ref_count"]} 个本地分支；'
          f'{result["unmerged_ref_count"]} 个引用尚非 master 祖先，合并相同 HEAD 后为 {len(rows)} 组。', '',
          '按最早未合入提交的 committer 时间排序；不是任务完成日期，也不是自动合并建议。',
          '“工作”来自 Git 提交与该 tip 内的 run 状态，不代表本轮验收通过。共同未合入祖先可能在多组出现。',
          'Git cherry 的等价补丁数不等于整条分支已合并；实际是否采用由 Human 决定。未执行任何其他分支合并或删除。', '']
    for index, row in enumerate(rows, 1):
        md += [f'## {index:02d}. ' + ' / '.join(r['source'] + ':' + r['name'] for r in row['refs']), '',
               f'- 精确 HEAD：`{row["head"]}`',
               f'- 未合入提交时间：{row["first_unique_commit_time"]} 至 {row["latest_unique_commit_time"]}',
               f'- 未合入提交 {row["unmerged_commit_count"]}；相对 master 净变更路径 {row["net_changed_path_count"]}；'
               f'新补丁 {row["patch_new"]}，master 等价补丁 {row["patch_equivalent_in_master"]}。']
        if row['contained_by']:
            md += ['- 此 HEAD 已包含于清单中其他 tip：' + ', '.join('`' + s[:12] + '`' for s in row['contained_by']) + '。']
        md += ['- 涉及区域：' + '; '.join(f'{p} ({n})' for p, n in row['top_path_groups']), '', '提交记录所载工作：', '']
        seen = set()
        for commit in row['commits']:
            subject = commit['subject']
            if subject not in seen:
                md.append('- `' + commit['sha'][:12] + '` ' + subject)
                seen.add(subject)
        if row['run_records']:
            md += ['', '分支内任务记录（历史 tip 自述，非本轮审核结论）：', '']
            for record in row['run_records']:
                md += ['- `' + record['path'] + '`：' + '; '.join(record['fields'])]
        md += ['', 'Human 决定：待定。', '']
    (target / '未合并分支清单_v1.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('baseline_master', 'live_remote_ref_count', 'local_ref_count', 'unmerged_ref_count', 'distinct_unmerged_heads')}, ensure_ascii=False))
    for i, row in enumerate(rows, 1):
        print(f'{i:02d}\t{row["head"][:12]}\t' + ', '.join(r['source'] + ':' + r['name'] for r in row['refs']) + f'\t{row["unmerged_commit_count"]} commits; {row["patch_new"]} new patches')

if __name__ == '__main__':
    main()
