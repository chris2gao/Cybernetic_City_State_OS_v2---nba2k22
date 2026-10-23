"""OS managed checks: bounded output, no game process APIs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RUN = ROOT/'01_os/07_content/_runs/run-20261023-native-ingredients-codex-r02'
BASE = '407e2134bd2f595477099b2c6e3484c818059fd9'


def command(argv):
    p = subprocess.run(argv, cwd=ROOT, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stdout.decode('utf-8', errors='replace')[-2000:]+p.stderr.decode('utf-8', errors='replace')[-2000:])
    return p.stdout


def checks(which):
    if which in ('FIXTURE_AND_IDENTITY_REGRESSIONS', 'OFFLINE_POLICY_NEGATIVE_CONTROLS'):
        import test_research
        cls = test_research.FixtureRegressions if which == 'FIXTURE_AND_IDENTITY_REGRESSIONS' else test_research.PolicyNegatives
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise AssertionError('Regression or negative-control failure')
        print('tests', result.testsRun)
    elif which == 'STATIC_IMAGE_REPLAY':
        from static_evidence import replay
        image = os.environ.get('NBA2K22_R02_STATIC_IMAGE')
        if not image:
            raise ValueError('Authorized disk-image input missing; not a successful skip')
        print('replayed_spans', replay(json.loads((HERE/'static_capture.json').read_text(encoding='utf-8')), image))
    elif which == 'DELIVERY_SCOPE_AND_MWU':
        manifest = json.loads((HERE/'source_manifest.json').read_text(encoding='utf-8'))
        for f in manifest['sources']:
            assert hashlib.sha256((HERE/f['local_path']).read_bytes()).hexdigest() == f['sha256']
        claims = json.loads((HERE/'corrected_claims.json').read_text(encoding='utf-8'))['claims']
        assert len(claims) == 14
        assert all(not c['evidence_axes']['PRODUCTION_READY'] and not c['evidence_axes']['SAVE_BOUND'] and not c['evidence_axes']['UI_BOUND'] for c in claims)
        plan = json.loads((HERE/'next_round_plan.json').read_text(encoding='utf-8'))
        assert len(plan['items']) == 3
        assert sum(t['target_byte_ceiling'] for t in plan['items'])+1208 == 3058
        for item in plan['items']:
            assert sum(r['bytes'] for r in item['target_ranges']) == item['target_byte_ceiling']
            assert item['standalone_ceiling_with_bootstrap'] == item['target_byte_ceiling']+1208
            assert item['target_ranges'] and item['ui_controls'] and item['acceptance']
        command([sys.executable, '-B', '01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py',
                 'artifact', str((RUN/'completion_pointer.json').relative_to(ROOT)), '--root', '.', '--require-mwu'])
        prefixes = [HERE.relative_to(ROOT).as_posix()+'/', RUN.relative_to(ROOT).as_posix()+'/']
        paths = command(['git', 'diff', '--name-only', '-z', BASE, 'HEAD']).decode().split('\0')
        dirty = command(['git', 'status', '--porcelain=v1', '-z', '--untracked-files=all']).decode().split('\0')
        paths += [p[3:] for p in dirty if p]
        assert all(any(p.startswith(prefix) for prefix in prefixes) for p in paths if p)
        print('source hashes,14 claims,3 proposals,3058B ceiling,MWU,changed scope PASS')
    else:
        raise ValueError('Unknown check')
    print(which, 'PASS')


if __name__ == '__main__':
    checks(sys.argv[1])
