"""Checks this intermediate checkpoint only, not M0-M5 completion."""
import hashlib
import json
import sys
import subprocess
from pathlib import Path

run = Path(__file__).resolve().parent
root = run.parents[3]
d = root / '08_Domain_Applications/Antigravity_GM_Engine'
inventory = json.loads((run / 'source_inventory.json').read_text(encoding='utf-8'))
for source in inventory['sources']:
    path = root / source['path']
    assert path.is_file(), source['path']
    raw = subprocess.run(['git','show',inventory['baseline']+':'+source['path']],cwd=root,capture_output=True,check=True).stdout
    assert hashlib.sha256(raw).hexdigest() == source['baseline_blob_sha256'], source['path']
modules = json.loads((d / 'docs/development/PROJECT_MODULE_REGISTRY_V2.json').read_text(encoding='utf-8'))['modules']
for mid in ['P09', 'P10']:
    m = next(x for x in modules if x['id'] == mid)
    assert any('ROLE-NATIVE-EXECUTION-SYSTEM-01' in ref for ref in m['latest_task_refs'])
    assert (d / 'research/rea_native_control/role_capabilities.py').is_file()
assert '尚未完成' in (d / 'PROJECT_INDEX.md').read_text(encoding='utf-8')
sys.path.insert(0, str(d / 'research/rea_native_control/tools'))
from export_role_coverage import coverage
current = json.loads((run / 'coverage_current.json').read_text(encoding='utf-8'))
assert current == coverage(), 'Per-requirement checkpoint is stale'
assert len({r['capability_id'] for r in current['requirements']}) == 183
assert current['game_access_performed'] is False
candidate = json.loads((d / 'research/rea_native_control/data/native_bindings.json').read_text(encoding='utf-8'))
binding = next(b for b in candidate['bindings'] if b['binding_id'] == 'sign.acquire_or_reset_candidate')
assert binding['unknowns'] and binding['input_layout']['not_callable']
minutes = next(row for row in current['requirements'] if row['capability_id'] == 'COACH.ROTATION.PLAYER_MINUTES')
assert minutes['native_action_id'] == 'COACH_ROTATION_SET_PLAYER_MINUTES' and minutes['call_logic_available']
assert minutes['new_live_validation'] == 'NOT_RUN'
binding = next(b for b in candidate['bindings'] if b['binding_id'] == 'rotation.current_delegate')
assert all(profile['slots']['5848'] == 0x11b2bb0 for profile in binding['input_layout']['allowed_profiles'])
for mid in ['P04', 'P06', 'P09', 'P10', 'P12']:
    module = next(x for x in modules if x['id'] == mid)
    assert 'research/rea_native_control/ROTATION_MINUTES_CONTRACT.md' in module['docs']
print('PASS: source hashes, index,183 dispositions, non-callable signing and static-only exact-minute scope; full M0-M5 completion NOT asserted')
