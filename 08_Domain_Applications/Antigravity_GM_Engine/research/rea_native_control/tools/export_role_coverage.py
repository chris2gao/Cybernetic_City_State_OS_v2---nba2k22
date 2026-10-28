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
            'native_action_id': native_id,
            'call_sequence': action['call_sequence'] if action else [],
            'source_maturity': desc['source_maturity'], 'native_maturity': desc['native_maturity'],
            'call_logic_available': desc['call_logic_available'],
            'role_endpoint': 'submit_decided_actions' if kind == 'EXTERNAL_REQUEST' or (action and action['kind'] == 'MUTATE') else 'read_role_visible_data',
            'historical_exact_live_evidence': desc['historical_exact_live_evidence'],
            'remaining_gaps': desc['unknowns'],
            'new_live_validation': 'NOT_RUN',
            'phase_target_permission': 'EXPLICIT_HOST_PROFILE_AND_CURRENT_PHASE_ATTESTATION_REQUIRED',
        })
    return {'task_id': 'NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01',
            'status': 'IN_PROGRESS_NOT_M0_M5_COMPLETION',
            'catalog_version': service.version,
            'source_requirement_count': len(service.requirements),
            'historical_mapping_count': service.source_mapping_count,
            'effective_mapping_count': len(service.mapping),
            'game_access_performed': False, 'requirements': rows}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: export_role_coverage.py <output-json>')
    dest = Path(sys.argv[1])
    if dest.exists():
        raise SystemExit('Use a new output file; do not overwrite prior evidence')
    result = coverage()
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'requirements'}))
