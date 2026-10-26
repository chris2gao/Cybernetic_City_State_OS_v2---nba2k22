"""Code-derived storage-role annotations over immutable annual observations."""
import hashlib,json
from pathlib import Path
PROFILE_PATH=Path(__file__).with_name('staff_history_semantics_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes())


def reference_roles(position,next_free_raw,source_decoder):
    if type(position) is not int or not 0<=position<40:raise ValueError('staff reference position0..39 required')
    if source_decoder!=PROFILE['compatible_source_decoder']:
        return {'basis':'UNSUPPORTED_SOURCE_DECODER; STORAGE_ROLES_WITHHELD','position_role':'UNKNOWN','native_increment_target':None,'native_clear_loop_visits':None,'next_free_marker_status':'UNKNOWN'}
    role='NATIVE_INCREMENT_TARGET_POSITION' if position==PROFILE['increment_target_position'] else 'NATIVE_CLEAR_LOOP_POSITION; CALENDAR_ROLE_UNPROVED' if position in PROFILE['clear_function_positions'] else 'OUTSIDE_NATIVE_CLEAR_LOOP; SEMANTIC_ROLE_UNPROVED'
    marker='NOT_OBSERVED' if next_free_raw is None else 'MATCHES_NATIVE_ALLOCATION_MARKER' if next_free_raw==PROFILE['next_free_allocation_marker'] else 'DIFFERS_FROM_NATIVE_ALLOCATION_MARKER; FREE_LIST_REACHABILITY_UNPROVED'
    return {'basis':'CODE_DERIVED:'+PROFILE['rule'],'position_role':role,'native_increment_target':position==PROFILE['increment_target_position'],'native_clear_loop_visits':position in PROFILE['clear_function_positions'],'next_free_marker_status':marker}


def verify_semantics_code(reader):
    checks=[]
    for proof in PROFILE['code_proofs']:
        raw=bytes.fromhex(proof['code_hex'])
        if hashlib.sha256(raw).hexdigest()!=proof['sha256']:raise ValueError('staff storage-role profile hash mismatch')
        observed=reader.read(reader.module_base+proof['rva'],len(raw),'STAFF_HISTORY_STORAGE_ROLE_CODE')
        if observed!=raw:raise ValueError('Native staff history storage-role code changed')
        checks.append({'rva':proof['rva'],'bytes':len(raw),'sha256':proof['sha256']})
    return {'status':'CURRENT_NATIVE_STAFF_STORAGE_ROLE_CODE_VERIFIED','rule':PROFILE['rule'],'code_windows':checks,'game_writes':False,'getter_or_mutator_invocations':0,'staff_value_reads':0}
