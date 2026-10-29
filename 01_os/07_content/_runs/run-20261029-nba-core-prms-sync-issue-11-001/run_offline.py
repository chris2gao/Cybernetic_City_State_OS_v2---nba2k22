"""Run existing offline suites in fresh per-check temp dirs; retain raw logs."""
import argparse
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
        print(json.dumps(report))
        return result.returncode


if __name__ == '__main__':
    sys.exit(main())
