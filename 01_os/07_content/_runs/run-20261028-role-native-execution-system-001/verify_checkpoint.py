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
for slot in range(1, 5):
    row = next(row for row in current['requirements'] if row['capability_id'] == 'PLAYER.EDIT.PLAY_TYPE_' + str(slot))
    assert row['call_logic_available'] and row['role_endpoint'] == 'submit_decided_actions'
    assert row['submission_parameter_schema']['slot_values']['required'] == [str(slot)]
    assert row['new_live_validation'] == 'NOT_RUN'
parent = next(b for b in candidate['bindings'] if b['binding_id'] == 'player.copy_parent_candidate')
assert parent['input_layout']['not_callable'] and parent['unknowns']
assert parent['input_layout']['complete_selected_unwind_extent_bytes'] == 31509
module = next(x for x in modules if x['id'] == 'P07')
assert 'research/rea_native_control/PLAYER_PLAYTYPE_NATIVE_CONTRACT.md' in module['docs']
delta = json.loads((run / 'CHECKPOINT_005_SOURCE_DELTA.json').read_text(encoding='utf8'))['new_consumer_source']
raw = subprocess.run(['git', 'show', delta['source_commit'] + ':' + delta['path']], cwd=root, capture_output=True, check=True).stdout
assert hashlib.sha256(raw).hexdigest() == delta['baseline_blob_sha256']
assert json.loads((root / delta['path']).read_text(encoding='utf8')) == json.loads(raw)
for requirement in ('ATTR_SET', 'ATTR_BATCH', 'TENDENCY_SET', 'TENDENCY_BATCH'):
    row = next(row for row in current['requirements'] if row['capability_id'] == 'PLAYER.EDIT.' + requirement)
    assert row['call_logic_available'] and row['role_endpoint'] == 'submit_decided_actions'
    assert row['new_live_validation'] == 'NOT_RUN'
fields = json.loads((d / 'research/rea_native_control/data/player_stat_fields.json').read_text(encoding='utf8'))['families']
assert sum(field['callable'] for field in fields['attributes'].values()) == 54
assert not fields['attributes']['potential']['callable']
assert len(fields['tendencies']) == 99
assert sum(field['name_known'] for field in fields['tendencies'].values()) == 48
badge = next(b for b in candidate['bindings'] if b['binding_id'] == 'player.badge_set_candidate')
assert badge['input_layout']['not_callable'] and len(badge['parameters']) == 4
assert badge['input_layout']['normal_ui_flag'] == 0
badge_req = next(row for row in current['requirements'] if row['capability_id'] == 'PLAYER.EDIT.BADGE_SET')
assert badge_req['call_logic_available'] and badge_req['role_endpoint'] == 'submit_decided_actions'
assert badge_req['roles'] == ['WORLD_ADMIN'] and badge_req['new_live_validation'] == 'NOT_RUN'
assert badge_req['native_effect_contract']['rights'].startswith('Explicit WORLD_ADMIN')
runtime_badges = json.loads((d / 'research/rea_native_control/data/player_badge_fields.json').read_text(encoding='utf8'))
assert len([field for field in runtime_badges['by_id'] if not field['sentinel_name']]) == 98
context = next(b for b in candidate['bindings'] if b['binding_id'] == 'player.badge_context')
assert context['input_layout']['catalog'] == runtime_badges
setter = next(b for b in candidate['bindings'] if b['binding_id'] == 'player.set_badge')
assert not setter['unknowns'] and setter['input_layout']['normal_ui_flag'] == 0
assert [parameter['type'] for parameter in setter['parameters']] == ['pointer', 'int', 'uint8', 'int']
badge_fields = json.loads((run / 'static/player_badge_names_fields_and_modifiers_025.json').read_text(encoding='utf8'))
assert badge_fields['game_access'] is False and len(badge_fields['fields']) == 99
assert len({field['internal_name'] for field in badge_fields['fields']}) == 99
assert sum(field['maximum'] == 1 for field in badge_fields['fields']) == 19
assert sum(field['maximum'] == 4 for field in badge_fields['fields']) == 80
assert badge_fields['fields'][0]['internal_name'] == 'NONE'
assert all(field['signed_modifier_field']['signed_width'] in (2, 4) for field in badge_fields['fields'])
assert not any(field['ui_label_verified'] for field in badge_fields['fields'])
for mid in ('P04', 'P05', 'P06', 'P07', 'P09', 'P10', 'P12'):
    module = next(x for x in modules if x['id'] == mid)
    assert 'research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md' in module['docs']
for delta in json.loads((run / 'CHECKPOINT_006_SOURCE_DELTA.json').read_text(encoding='utf8'))['new_consumer_sources']:
    raw = subprocess.run(['git', 'show', delta['source_commit'] + ':' + delta['path']], cwd=root, capture_output=True, check=True).stdout
    assert hashlib.sha256(raw).hexdigest() == delta['baseline_blob_sha256']
    assert json.loads((root / delta['path']).read_text(encoding='utf8')) == json.loads(raw)
delta = json.loads((run / 'CHECKPOINT_008_SOURCE_DELTA.json').read_text(encoding='utf8'))['native_field_source']
raw = subprocess.run(['git', 'show', delta['source_commit'] + ':' + delta['path']], cwd=root, capture_output=True, check=True).stdout
assert hashlib.sha256(raw).hexdigest() == delta['baseline_blob_sha256']
assert json.loads((root / delta['path']).read_text(encoding='utf8')) == json.loads(raw)
for mid in ('P04', 'P05', 'P06', 'P07', 'P09', 'P10', 'P12'):
    module = next(x for x in modules if x['id'] == mid)
    assert 'research/rea_native_control/BADGE_NATIVE_CONTRACT.md' in module['docs']
assert current['read_dataset_count'] == 13 and len(current['read_datasets']) == 13
read = next(row for row in current['read_datasets'] if row['dataset_id'] == 'player.editor_state')
assert read['native_call_logic_available'] and read['snapshot_provider'] == 'PlayerEditorSnapshotProvider'
assert read['new_game_capture'] == 'NOT_RUN' and not read['coverage_complete']
delta = json.loads((run / 'CHECKPOINT_009_SOURCE_DELTA.json').read_text(encoding='utf8'))['new_static_source']
raw = (root / delta['path']).read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(raw).hexdigest() == delta['normalized_lf_sha256']
getter_source = json.loads(raw)
assert not getter_source['game_access'] and len(getter_source['selected_fields']) == 153
stat_fields = json.loads((d / 'research/rea_native_control/data/player_stat_fields.json').read_text(encoding='utf8'))['families']
for row in getter_source['selected_fields']:
    field = stat_fields[row['family']][row['field_id']]
    assert field['callable'] and field['native_index'] == row['native_index'] and field['offset'] == row['byte_offset']
getter = next(b for b in candidate['bindings'] if b['binding_id'] == 'player.get_stat_ui')
assert getter['rva'] == 0x978360 and getter['return_type'] == 'int'
assert [p['type'] for p in getter['parameters']] == ['pointer', 'int']
assert {constant['rva'] for constant in getter_source['float_constants']} <= {sig['rva'] for sig in getter['input_layout']['code_signatures']}
for mid in ('P03', 'P04', 'P05', 'P06', 'P07', 'P09', 'P10', 'P12'):
    module = next(x for x in modules if x['id'] == mid)
    assert 'research/rea_native_control/PLAYER_EDITOR_READ_CONTRACT.md' in module['docs']
print('PASS: sources/index,183 dispositions,13 read datasets, selected Player read/provider and original Getter receipts; full M0-M5 completion NOT asserted')
