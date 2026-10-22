"""Resolve only validated coaching targets in a freshly calibrated locator."""
import hashlib
import json
from coach_locator import read_exact


def process_binding(pid,creation_time):
    return hashlib.sha256(json.dumps([pid,str(creation_time)],separators=(',',':')).encode()).hexdigest()


def validate_session(locator,snapshot):
    mem=locator.mem
    if snapshot.get('process_binding'):
        valid=process_binding(mem.pid,mem.creation_time)==snapshot['process_binding']
    else:
        valid=mem.pid==snapshot.get('process_pid') and mem.creation_time==snapshot.get('process_creation_time')
    if not valid:
        raise RuntimeError('STALE_PID')
    if locator.evidence!=snapshot['native_evidence']:
        raise RuntimeError('MODULE_OR_NATIVE_EVIDENCE_CHANGED')
    if locator.context_identity()!=snapshot['context_identity']:
        raise RuntimeError('WRONG_SAVE_COACH_OR_ROSTER')
    if locator.playbooks!=snapshot['playbooks']:
        raise RuntimeError('LOADED_PLAYBOOK_DIRECTORY_CHANGED')


def resolve_target(locator,action,block,snapshot):
    tid=action['team_id']
    if action['scope']=='COACH_DEFAULT':
        return locator.coaches[tid]['address']+block['offset']
    if action['scope']!='VS_OPPONENT_DEFENSE':
        raise RuntimeError('UNSUPPORTED_BATCH_SCOPE')
    from coaching_reader import defensive_catalog
    if defensive_catalog(locator)!=snapshot['defensive_field_catalog']:
        raise RuntimeError('DEFENSIVE_NATIVE_ENUM_OR_MASK_CHANGED')
    selector=locator.profile['opponent_overall_defense']['record_selector']
    if not selector:
        raise RuntimeError('OVERALL_RECORD_SELECTOR_NOT_VERIFIED')
    native=locator.profile['native']
    matches=[]
    for index in range(native['gameplan_capacity']):
        address=locator.managers[tid]+native['gameplan_start']+index*native['gameplan_stride']
        header=read_exact(locator.mem,address,6)
        if int.from_bytes(header[2:4],'little')==tid and int.from_bytes(header[4:6],'little')==action['opponent_team_id']:
            matches.append((address,header))
    if len(matches)!=1:
        raise RuntimeError('INVALID_OR_AMBIGUOUS_OPPONENT')
    address,header=matches[0]
    team=next(t for t in snapshot['teams'] if t['team_id']==tid)
    source=next(g for g in team['gameplans'] if g['opponent_team_id']==action['opponent_team_id'])
    overall=source['overall_defense']
    expected_header=bytes.fromhex(overall['header_signature'])
    # The approved operation may set the observed UI commit flag after all
    # settings writes. It never changes IsTainted, owner or opponent IDs.
    if header[1:]!=expected_header[1:] or header[0] not in {expected_header[0],1}:
        raise RuntimeError('GAMEPLAN_HEADER_OR_INHERITANCE_CHANGED')
    from coaching_overall import overall_from_raw
    current=overall_from_raw(read_exact(locator.mem,address,native['gameplan_stride']),
        locator.profile['opponent_overall_defense'],snapshot['defensive_field_catalog'])
    if current['identity']!=overall['identity']:
        raise RuntimeError('OVERALL_RECORD_IDENTITY_CHANGED')
    if block.get('target_kind')=='GAMEPLAN_UI_COMMIT_FLAG':
        if expected_header[0]!=0 or block['offset']!=0 or block['size']!=1:
            raise RuntimeError('OUTSIDE_VERIFIED_COMMIT_FLAG')
        return address
    allowed={b['settings_offset']:b['identity'] for b in current['blocks']}
    if (block.get('target_kind')!='OVERALL_MATCHUP_SETTINGS' or block['size']!=8
        or allowed.get(block['offset'])!=block.get('identity')):
        raise RuntimeError('OUTSIDE_VERIFIED_OVERALL_BLOCK')
    return address+block['offset']
