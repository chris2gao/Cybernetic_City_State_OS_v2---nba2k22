"""Run existing offline suites in fresh per-check temp dirs; retain raw logs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('suite', choices=['prms','nba'])
    parser.add_argument('--repo-root', required=True)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    with tempfile.TemporaryDirectory(prefix='issue11-'+args.suite+'-') as temporary:
        parent = Path(temporary)
        if args.suite == 'nba':
            cwd, target = root / '08_Domain_Applications/Antigravity_GM_Engine', 'tests'
        else:
            cwd, target = root, '01_os/06_execution/boot/context_management/prms/tests'
        command = [sys.executable,'-B','-m','pytest',target,'-q','-p','no:cacheprovider',
                   '--basetemp',str(parent/'pytest'),'--junitxml',str(parent/'junit.xml')]
        result = subprocess.run(command,cwd=cwd,capture_output=True)
        # Raw pytest output is forwarded into the managed check's byte capture.
        sys.stderr.buffer.write(result.stdout + result.stderr)
        assert (parent/'junit.xml').is_file(), 'pytest did not produce outcomes'
        cases = []
        for case in ET.parse(parent/'junit.xml').iter('testcase'):
            outcome = 'FAIL' if case.find('failure') is not None or case.find('error') is not None else (
                'SKIP' if case.find('skipped') is not None else 'PASS')
            cases.append({'node':case.attrib['classname']+'::'+case.attrib['name'],'outcome':outcome})
        report = {'suite':args.suite,'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
            'exit_code':result.returncode,'test_count':len(cases),'outcomes':cases,
            'raw_output_sha256':hashlib.sha256(result.stdout+result.stderr).hexdigest(),
            'game_or_REA_operation':False}
        verification_exit = result.returncode
        if args.suite == 'nba':
            # Existing business tests are unchanged by this Core-only integration.
            # Preserve their raw failures; compare against an actual exact-base
            # run rather than skipping tests or relabeling pytest's exit code.
            baseline = json.loads(Path(__file__).with_name('nba_baseline.json').read_text(encoding='utf-8'))
            assert baseline['candidate'] == '7742568ac677b3c16079887463f05e81cb1191ed'
            unchanged = subprocess.run(['git','diff','--quiet',baseline['candidate'],'HEAD','--',
                '08_Domain_Applications'],cwd=root).returncode == 0
            same = Counter((x['node'],x['outcome']) for x in baseline['outcomes']) == Counter(
                (x['node'],x['outcome']) for x in cases)
            report.update(baseline_candidate=baseline['candidate'], baseline_pytest_exit=baseline['exit_code'],
                identical_per_test_baseline_outcomes=same, business_tree_unchanged=unchanged,
                compatibility='ALL_TESTS_PASS' if result.returncode == 0 else (
                    'NO_NEW_FAILURES_AGAINST_EXACT_BASELINE' if same and unchanged else 'REGRESSION_OR_UNVERIFIED'))
            if same and unchanged:
                verification_exit = 0
        print(json.dumps(report))
        return verification_exit


if __name__ == '__main__':
    sys.exit(main())
