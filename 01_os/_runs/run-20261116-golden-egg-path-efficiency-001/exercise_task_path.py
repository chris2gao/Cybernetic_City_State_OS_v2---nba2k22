"""One bounded task exercise: existing CLI chooses the actual engineering check.

This is run evidence, not a scheduler or a second production runner. No retries,
no arbitrary dispatch, no game actions, and no source writes during verification.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNNER = ROOT / '01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'


def main():
    selected = subprocess.run(
        [sys.executable, '-B', str(RUNNER), 'next-business-action',
         str(HERE / 'engineering_task_decision.json')], cwd=ROOT,
        capture_output=True, text=True, encoding='utf-8', timeout=30, check=True)
    decision = json.loads(selected.stdout)
    if decision['status'] != 'READY' or decision['step_id'] != 'engineering':
        raise RuntimeError('Engineering check was not selected ahead of optional documentation')
    plan = json.loads((HERE / 'verification_plan.json').read_text(encoding='utf-8'))
    check = next(item for item in plan['checks'] if item['id'] == decision['step_id'])
    argv = check['argv']
    if argv[0] != '@python':
        raise RuntimeError('This task exercise is limited to the declared Python check')
    started = datetime.now(timezone.utc).isoformat()
    actual = subprocess.run([sys.executable, *argv[1:]], cwd=ROOT,
                            capture_output=True, timeout=check['timeout_seconds'])
    # Include the actual check output in managed verification's retained streams.
    sys.stderr.buffer.write(actual.stdout + actual.stderr)
    print(json.dumps(dict(entry='next-business-action CLI -> selected plan check -> real subprocess',
                          selection=decision, selected_check_argv=argv,
                          started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
                          exit_code=actual.returncode,
                          stdout_sha256=hashlib.sha256(actual.stdout).hexdigest(),
                          stderr_sha256=hashlib.sha256(actual.stderr).hexdigest())))
    return actual.returncode


if __name__ == '__main__':
    raise SystemExit(main())
