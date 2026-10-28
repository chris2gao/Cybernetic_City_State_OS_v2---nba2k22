"""Checks this intermediate checkpoint only, not M0-M5 completion."""
import hashlib
import json
from pathlib import Path

run = Path(__file__).resolve().parent
root = run.parents[3]
d = root / '08_Domain_Applications/Antigravity_GM_Engine'
inventory = json.loads((run / 'source_inventory.json').read_text(encoding='utf-8'))
for source in inventory['sources']:
    path = root / source['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], source['path']
modules = json.loads((d / 'docs/development/PROJECT_MODULE_REGISTRY_V2.json').read_text(encoding='utf-8'))['modules']
for mid in ['P09', 'P10']:
    m = next(x for x in modules if x['id'] == mid)
    assert any('ROLE-NATIVE-EXECUTION-SYSTEM-01' in ref for ref in m['latest_task_refs'])
    assert (d / 'research/rea_native_control/role_capabilities.py').is_file()
assert '尚未完成' in (d / 'PROJECT_INDEX.md').read_text(encoding='utf-8')
print('PASS: source hashes and intermediate index links; full M0-M5 completion NOT asserted')
