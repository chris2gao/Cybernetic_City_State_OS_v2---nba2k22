"""Explicit allowlist staging for this task; never commits or publishes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

root = Path.cwd().resolve()
sys.path.insert(0, str(root / '01_os/06_execution/task_discipline/path_ledger'))
from changed_path_ledger import build
from task_packet_input import read_packet

parser = argparse.ArgumentParser()
parser.add_argument('--stage', action='store_true')
parser.add_argument('--record', required=True)
args = parser.parse_args()
packet_path = root / '01_os/_runs/run-20260907-os-execution-foundation-001/01_任务/task_packet.yml'
packet = read_packet(packet_path).body

def git(*argv):
    return subprocess.run(['git', '-c', 'core.untrackedCache=false', '-c', 'core.fsmonitor=false', *argv],
                          cwd=root, capture_output=True, check=True).stdout

branch = git('branch', '--show-current').decode().strip()
if branch != packet['branch'] or branch == 'master':
    raise SystemExit('wrong_task_branch')
report = build(root, packet['exact_base_sha'], 'HEAD', packet_path)
if report['outside_allowlist']:
    raise SystemExit('out_of_scope_paths')
record_path = Path(args.record).resolve()
if record_path == root or root in record_path.parents:
    raise SystemExit('record_must_be_external')
if record_path.exists():
    raise SystemExit('record_already_exists')
git('diff', '--check')
if args.stage:
    git('add', '--', *report['paths'])
    staged = sorted(p for p in git('diff', '--cached', '--name-only', '-z').decode('utf-8').split('\0') if p)
    if staged != report['paths']:
        raise SystemExit('staged_set_mismatch')
    git('diff', '--cached', '--check')
report['staging_performed'] = args.stage
with record_path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
print(json.dumps({'paths': report['path_count'], 'out_of_scope': len(report['outside_allowlist']), 'staged': args.stage}))
