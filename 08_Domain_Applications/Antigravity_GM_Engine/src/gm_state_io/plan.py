"""Sparse offline intent -> canonical, generation-bound physical block plan."""
import json
from .common import binding, canonical, digest, now
from .codec import decode, encode_patch, normalized_value, validate_value
from .store import connect, register
from .workspace import Workspaces, lifecycle_lock
import save_context


def object_key(selector):
    return digest(selector)


def build_plan(proposal, source, registry, workspace):
    allowed = {'change_set_id','decision_id','version','origin_model','reason','changes','operation','event'}
    if set(proposal)-allowed:
        raise ValueError('EXACT_INTENT_CONTRACT_REQUIRED_NO_AUTHORITY_OR_ADDRESSES')
    operation = proposal.get('operation','GM_STATE_CHANGE')
    if operation not in ('GM_STATE_CHANGE','TEAM_BOOK_REBIND') or (operation == 'GM_STATE_CHANGE' and 'event' in proposal):
        raise ValueError('INVALID_OPERATION_OR_EVENT')
    if binding(source) != binding(workspace):
        raise ValueError('STALE_OR_CROSS_SAVE_OBSERVATION')
    if source['registry_version'] != registry.version:
        raise ValueError('SOURCE_REGISTRY_VERSION_MISMATCH')
    if not isinstance(proposal.get('decision_id'), str) or not proposal['decision_id'].strip():
        raise ValueError('DECISION_ID_REQUIRED')
    if type(proposal.get('version')) is not int or proposal['version'] < 1:
        raise ValueError('DECISION_VERSION_REQUIRED')
    if not proposal.get('reason') or not isinstance(proposal.get('changes'),list) or not proposal['changes']:
        raise ValueError('SPARSE_CHANGES_AND_REASON_REQUIRED')
    objects = {o['object_key']:o for o in source['objects']}
    if len(objects) != len(source['objects']):
        raise ValueError('DUPLICATE_SOURCE_OBJECT')
    groups, actions, ids, logical = {}, [], set(), set()
    unchanged = 0
    for intent in proposal['changes']:
        if set(intent) != {'action_id','object_key','field_key','target_value','reason'}:
            raise ValueError('EXACT_SPARSE_CHANGE_CONTRACT_REQUIRED')
        aid, key, name = intent['action_id'], intent['object_key'], intent['field_key']
        if not isinstance(aid,str) or not aid or aid in ids or not isinstance(intent['reason'],str) or not intent['reason'].strip():
            raise ValueError('DUPLICATE_ACTION_OR_MISSING_REASON')
        ids.add(aid)
        if (key,name) in logical:
            raise ValueError('DUPLICATE_LOGICAL_FIELD')
        logical.add((key,name))
        field = registry.field(name)
        if name.startswith('overall.'):
            raise PermissionError('OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL')
        if name == 'coach.PlaybookID' and operation != 'TEAM_BOOK_REBIND':
            raise PermissionError('ORDINARY_GM_BOOK_SWITCH_DISABLED_USE_TEAM_BOOK_REBIND')
        rebind = name == 'coach.PlaybookID' and operation == 'TEAM_BOOK_REBIND'
        if (not field['gm_enabled'] and not rebind) or field['write_capability'] != 'MEMORY_WRITE_VERIFIED':
            raise PermissionError('FIELD_READ_ONLY_OR_BLOCKED_SOURCE:'+name)
        validate_value(intent['target_value'],field,source.get('loaded_playbooks',[]))
        if key not in objects:
            raise ValueError('OBJECT_NOT_OBSERVED_IN_SOURCE_BATCH')
        obj = objects[key]
        if operation == 'TEAM_BOOK_REBIND':
            from copy import deepcopy
            from .team_book import validate_rebind
            if not rebind or len(proposal['changes']) != 1:
                raise PermissionError('TEAM_BOOK_REBIND_REQUIRES_SEPARATE_SINGLE_BINDING_ACTION')
            obj = deepcopy(obj)
            obj['team_book_rebind'] = validate_rebind(proposal,source,obj,intent['target_value'])
        if field['target_kind'] == 'PLAYBOOK_SLOT':
            from .team_book import validate_slot
            validate_slot(source,obj)
        if field['target_kind']=='PLAYBOOK_SLOT' and intent['target_value'] not in source.get('loaded_play_crcs',[]):
            raise ValueError('PLAY_CRC_NOT_IN_OBSERVED_LOADED_CATALOG')
        if (field['target_kind'] != obj['selector']['target_kind'] or name not in obj['field_keys']
            or obj.get('source_status') != 'OBSERVED_SAME_SESSION'):
            raise ValueError('FIELD_OBJECT_IDENTITY_OR_SOURCE_MISMATCH')
        targets = obj.get('members') or [obj]
        prior = [decode(bytes.fromhex(t['raw']), field) for t in targets]
        if all(v == normalized_value(intent['target_value'],field) for v in prior):
            # Validate even no-op inputs; bool/int coercion must not bypass type rules.
            validate_value(intent['target_value'],field,source.get('loaded_playbooks',[]))
            unchanged += 1
        actions.append(dict(intent, expected_observed_raw=prior, selector=obj['selector'], identity=obj['identity'],
                            domain=field['domain']))
        for target in targets:
            physical = target['object_key']
            group = groups.setdefault(physical, dict(object=target, changes={}, action_ids=[]))
            if name in group['changes']:
                raise ValueError('OVERLAPPING_OVERALL_PERSONAL_FIELDS')
            group['changes'][name] = intent['target_value']
            group['action_ids'].append(aid)
        if obj.get('commit_object'):
            commit = obj['commit_object']
            groups.setdefault(commit['object_key'], dict(object=commit,changes={},action_ids=[]))
    scopes = {(a['selector'].get('team_id'),a['selector'].get('opponent_team_id'),a['selector']['target_kind']) for a in actions}
    for tid, opp, kind in scopes:
        if kind=='OVERALL_DEFENSE' and (tid,opp,'PERSONAL_DEFENSE') in scopes:
            raise ValueError('BLOCKED_UNVERIFIED_OVERALL_PERSONAL_ORDER_SPLIT_APPROVED_BATCHES')
    if any(a['field_key']=='coach.PlaybookID' for a in actions) and any(a['selector']['target_kind']=='PLAYBOOK_SLOT' for a in actions):
        raise ValueError('PLAYBOOK_SWITCH_AND_SLOT_EDIT_REQUIRE_SEPARATE_ORDERED_APPROVED_BATCHES')
    blocks = []
    used_objects = []
    commit_groups=[]
    for key, group in sorted(groups.items()):
        obj = group['object']
        raw = bytes.fromhex(obj['raw'])
        used_objects.append(obj)
        if obj['selector']['target_kind'] == 'GAMEPLAN_COMMIT':
            commit_groups.append(group)
            continue
        else:
            encoded = encode_patch(raw,group['changes'],registry,source.get('loaded_playbooks',[]))
        for block in encoded:
            if block['before'] != block['after']:
                blocks.append(dict(block,object_key=key,selector=obj['selector'],identity=obj['identity'],
                                   storage_target_key=key+':'+str(block['offset'])+':'+str(block['size']),
                                   action_ids=sorted(group['action_ids'])))
    for group in commit_groups:
        obj=group['object']
        s=obj['selector']
        if obj['raw']=='00' and any(b['selector']['target_kind']=='DEFENSE_BLOCK' and b['selector']['team_id']==s['team_id']
                                   and b['selector']['opponent_team_id']==s['opponent_team_id'] for b in blocks):
            blocks.append(dict(offset=0,size=1,before='00',after='01',mask=255,fields=['IsInUse'],
                               object_key=obj['object_key'],selector=s,identity=obj['identity'],
                               storage_target_key=obj['object_key']+':0:1',action_ids=[]))
    # UI commit flags are applied after fields, never before the bulk edit.
    blocks.sort(key=lambda b:(b['selector']['target_kind']=='GAMEPLAN_COMMIT', b['object_key'], b['offset']))
    plan = dict(**binding(workspace), source_batch_id=source['source_batch_id'],source_snapshot_id=source['source_snapshot_id'],
                registry_version=registry.version,decision_id=proposal['decision_id'],version=proposal['version'],
                reason=proposal['reason'],origin_model=proposal.get('origin_model'),
                actions=sorted(actions,key=lambda a:a['action_id']),objects=used_objects,blocks=blocks,
                process_binding=source['process_binding'],source_context=source.get('source_context'),
                actions_requested=len(actions),actions_effective=len(actions)-unchanged,unchanged=unchanged,
                native_blocks_planned=len(blocks),status='VALIDATED_PENDING_APPROVAL',
                approval_required=True,result_is_game_observation=False)
    plan['operation'] = operation
    if operation == 'TEAM_BOOK_REBIND':
        plan['event'] = proposal['event']
        plan['event_evidence'] = 'REQUIRES_FOREGROUND_HUMAN_CONFIRMATION_NOT_MODEL_ATTESTED'
    plan['digest'] = digest(plan)
    plan['change_set_id'] = proposal.get('change_set_id') or ('cs_'+plan['digest'][:24])
    if not isinstance(plan['change_set_id'],str) or not plan['change_set_id'].replace('_','').replace('-','').isalnum():
        raise ValueError('INVALID_CHANGE_SET_ID')
    return plan


def stage(proposal, source, registry):
    with lifecycle_lock():
        w = Workspaces().active(source['save_id'],source)
        if w['lifecycle_status'] != 'CAPTURED':
            raise ValueError('ACTIVE_GENERATION_NOT_CAPTURED')
        plan = build_plan(proposal,source,registry,w)
        path = save_context.save_paths(w['save_id'])['control_db_path']
        with connect(path) as c:
            register(c,registry)
            row = c.execute('SELECT plan_json FROM desired_change_sets WHERE change_set_id=?',(plan['change_set_id'],)).fetchone()
            if row:
                if json.loads(row[0]) != plan:
                    raise ValueError('IMMUTABLE_CHANGE_SET_CONFLICT')
                return plan
            c.execute('INSERT INTO desired_change_sets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (plan['change_set_id'],w['save_id'],w['save_instance_id'],w['generation_id'],
                       plan['source_batch_id'],plan['source_snapshot_id'],registry.version,plan['decision_id'],plan['version'],
                       plan['status'],now(),plan['digest'],plan['origin_model'],plan['reason'],canonical(plan)))
            c.executemany('INSERT INTO desired_changes VALUES (?,?,?,?,?,?,?,?)',
                          [(plan['change_set_id'],a['action_id'],a['object_key'],a['field_key'],canonical(a['expected_observed_raw']),
                            canonical(a['target_value']),a['reason'],'[]') for a in plan['actions']])
        return plan


def load_plan(change_set_id, registry, career=None):
    w = Workspaces().active(career)
    with connect(save_context.save_paths(w['save_id'])['control_db_path']) as c:
        row = c.execute('SELECT plan_json FROM desired_change_sets WHERE change_set_id=?',(change_set_id,)).fetchone()
    if not row:
        raise ValueError('CHANGE_SET_NOT_IN_ACTIVE_GENERATION')
    plan = json.loads(row[0])
    if binding(plan) != binding(w) or registry.version != plan['registry_version']:
        raise ValueError('STALE_PLAN_GENERATION_OR_PROFILE')
    content = {k:v for k,v in plan.items() if k not in ('digest','change_set_id')}
    if digest(content) != plan['digest']:
        raise ValueError('PLAN_DIGEST_CHANGED')
    return plan
