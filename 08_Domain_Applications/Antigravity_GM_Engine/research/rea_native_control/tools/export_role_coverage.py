"""Export exact source-backed requirement dispositions; never mark UNKNOWN done."""
import json
import sys
from pathlib import Path

CONTROL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONTROL))
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


def coverage():
    service = RoleCapabilityService()
    # An empty-permission profile for metadata only, no game/snapshot assertion.
    profile = RoleCapabilityProfile('WORLD_ADMIN', 'metadata-only', (), 'NOT_BOUND',
               'NOT_BOUND', 'NOT_BOUND', 'NOT_BOUND', 'NOT_BOUND', 'NOT_BOUND')
    rows = []
    for key, req in service.requirements.items():
        desc = service.describe_action(key, profile)
        native_id = desc['executor_action_id']
        action = service.registry.get(native_id) if native_id else None
        kind = 'EXTERNAL_REQUEST' if desc['is_external_request'] else 'WORLD_EDIT' if desc['world_editor_only'] else action['kind'] if action else 'REQUIREMENT_UNBOUND'
        rows.append({
            'capability_id': key, 'meaning': desc['meaning'], 'roles': desc['role_candidates'],
            'kind': kind, 'requirement_inputs': desc['required_role_inputs'],
            'submission_parameter_schema': desc['native_parameter_schema'],
            'allowed_values': service.get_allowed_values(key, profile),
            'known_effect': desc['known_effect'], 'required_phase': desc['phase_requirement'],
            'native_effect_contract': desc['native_effect_contract'],
            'native_action_id': native_id,
            'call_sequence': action['call_sequence'] if action else [],
            'source_maturity': desc['source_maturity'], 'native_maturity': desc['native_maturity'],
            'requirement_origin': desc['requirement_origin'],
            'call_logic_available': desc['call_logic_available'],
            'role_endpoint': ('submit_decided_actions' if kind == 'EXTERNAL_REQUEST' else
                              'read_role_visible_data' if action and action['kind'] == 'READ' else
                              'submit_decided_actions' if action and desc['call_logic_available'] else None),
            'historical_exact_live_evidence': desc['historical_exact_live_evidence'],
            'remaining_gaps': desc['unknowns'],
            'new_live_validation': 'NOT_RUN',
            'phase_target_permission': 'EXPLICIT_HOST_PROFILE_AND_CURRENT_PHASE_ATTESTATION_REQUIRED',
        })
    readers = []
    read_catalog = json.loads((service.registry.root / 'data/read_catalog.json').read_text(encoding='utf8'))
    for dataset in read_catalog['datasets']:
        action = service.registry.get(dataset['action_id'])
        readers.append({'dataset_id': dataset['dataset_id'], 'native_action_id': dataset['action_id'],
            'available_scope': dataset['available_scope'], 'input_schema': action['input_schema'],
            'native_maturity': action['capability'], 'native_call_logic_available': service._callable(action),
            'coverage_complete': dataset['coverage_complete'], 'remaining_gaps': service._gaps(action),
            'technical_entry': 'NativeReadFacade.read', 'role_entry': 'read_role_visible_data',
            'snapshot_provider': 'PlayerEditorSnapshotProvider' if dataset['dataset_id'] == 'player.editor_state' else 'Explicit sanitized host provider required',
            'permission': 'EXPLICIT_HOST_DATASET_FIELD_READ_GRANTS_AND_CONTEXT_REQUIRED',
            'new_game_capture': 'NOT_RUN'})
    return {'task_id': 'NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01',
            'status': 'IN_PROGRESS_NOT_M0_M5_COMPLETION',
            'catalog_version': service.version,
            'source_requirement_count': len(service.source_requirement_ids),
            'supplemental_requirement_count': len(service.supplemental_requirement_ids),
            'total_requirement_count': len(service.requirements),
            'historical_mapping_count': service.source_mapping_count,
            'effective_mapping_count': len(service.mapping),
            'game_access_performed': False, 'requirements': rows,
            'read_dataset_count': len(readers), 'read_datasets': readers}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: export_role_coverage.py <output-json>')
    dest = Path(sys.argv[1])
    if dest.exists():
        raise SystemExit('Use a new output file; do not overwrite prior evidence')
    result = coverage()
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in {'requirements', 'read_datasets'}}))
