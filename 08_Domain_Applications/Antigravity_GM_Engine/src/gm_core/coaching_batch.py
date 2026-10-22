"""Offline 1–30-team batch contract. Does not import game memory or executors."""
import hashlib
import json
import copy
from coach_codec import load_profile,integer
from defense_codec import encode_defense
from .coaching import CONTEXT,claims_authority,validate_context,validate_plan,propose


def batch_digest(batch):
    return hashlib.sha256(json.dumps(batch,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def normalize_freelance(targets,profile):
    """Array position is priority. A single named slot can also be changed."""
    targets=dict(targets)
    if 'freelance_sets' in targets:
        values=targets.pop('freelance_sets')
        slots=profile['freelance_slot_order']
        if not isinstance(values,list) or len(values)!=4 or any(n in targets for n in slots):
            raise ValueError('EXACT_ORDERED_FOUR_FREELANCE_SETS_REQUIRED')
        targets.update(zip(slots,values))
    return targets


def validate_defense_action(action,snapshot,profile):
    if action.get('scope')!='VS_OPPONENT_DEFENSE' or action.get('defensive_setting_scope')!='OVERALL':
        raise ValueError('OVERALL_DEFENSE_SCOPE_REQUIRED')
    integer(action.get('team_id'),0,65535,'INVALID_TEAM_ID')
    integer(action.get('opponent_team_id'),0,65535,'INVALID_OPPONENT_ID')
    if action['team_id']==action['opponent_team_id']:
        raise ValueError('SELF_GAMEPLAN')
    teams=[t for t in snapshot['teams'] if t['team_id']==action['team_id']]
    if len(teams)!=1 or action.get('verified_coach_identity')!=teams[0]['coach_identity']:
        raise ValueError('WRONG_OR_AMBIGUOUS_COACH_IDENTITY')
    if action['opponent_team_id'] not in {t['team_id'] for t in snapshot['teams']}:
        raise ValueError('OPPONENT_NOT_IN_SOURCE')
    matches=[g for g in teams[0]['gameplans'] if g['opponent_team_id']==action['opponent_team_id']]
    if len(matches)!=1:
        raise ValueError('INVALID_OR_AMBIGUOUS_OPPONENT')
    rule=profile['opponent_overall_defense']
    overall=matches[0].get('overall_defense')
    if not rule.get('record_selector') or not overall or overall.get('status')!='OBSERVED_OVERALL_VERIFIED':
        raise ValueError('OVERALL_RECORD_SELECTOR_NOT_VERIFIED')
    if action.get('verified_overall_identity')!=overall['identity']:
        raise ValueError('WRONG_OVERALL_RECORD_IDENTITY')
    if action.get('old_defense_blocks')!=overall['blocks']:
        raise ValueError('FULL_OLD_DEFENSE_BLOCKS_REQUIRED')
    changes=action.get('changes')
    if not isinstance(changes,list) or not changes:
        raise ValueError('EXACT_DEFENSE_BLOCK_AND_CHANGES_REQUIRED')
    for change in changes:
        if (not isinstance(change,dict) or set(change)!={'field','before_raw','after_raw'}
            or change['field'] not in overall['values']
            or change['before_raw']!=overall['values'][change['field']]):
            raise ValueError('STALE_OR_INVALID_OVERALL_VALUE')
    blocks=[]
    # The caller cannot select one player. Expand the overall action to every
    # observed present entry, keeping unmodified fields and each full preimage.
    for source in overall['blocks']:
        per_entry=[dict(field=c['field'],before_raw=source['values'][c['field']],after_raw=c['after_raw']) for c in changes]
        block=encode_defense(bytes.fromhex(source['raw_block']),per_entry,snapshot['defensive_field_catalog'])
        block.update(offset=source['settings_offset'],target_kind='OVERALL_MATCHUP_SETTINGS',identity=source['identity'])
        blocks.append(block)
    flag=overall['commit_flag_raw']
    if flag not in (0,1) or rule.get('activation_policy')!='SET_IS_IN_USE_1_AFTER_BULK_FIELDS_AS_OBSERVED_ON_UI_EXIT':
        raise ValueError('UNVERIFIED_GAMEPLAN_COMMIT_POLICY')
    if flag==0:
        blocks.append(dict(offset=0,size=1,before='00',after='01',mask=255,fields=['IsInUse'],target_kind='GAMEPLAN_UI_COMMIT_FLAG'))
    return blocks


def validate_batch(batch,snapshot,profile=None):
    profile=profile or load_profile()
    errors=[]
    prepared=[]
    blocked=[]
    try:
        if not isinstance(batch,dict) or claims_authority(batch):
            raise ValueError('PROPOSAL_CANNOT_AUTHORIZE_EXECUTION')
        if batch.get('operation')!='COACHING_BATCH_CHANGE' or batch.get('status')!='PROPOSED':
            raise ValueError('COACHING_BATCH_CHANGE_PROPOSED_REQUIRED')
        for key in ('batch_id','decision_id','snapshot_id'):
            if not isinstance(batch.get(key),str) or not batch[key].strip():
                raise ValueError('REQUIRED_'+key)
        integer(batch.get('version'),1,1000000,'INVALID_VERSION')
        if (snapshot.get('schema_version')!=1 or snapshot.get('observation_status')!='OBSERVED_LIVE_READ_ONLY'
            or snapshot.get('codec_version')!=profile['codec_version']):
            raise ValueError('VERIFIED_COACHING_SNAPSHOT_REQUIRED')
        validate_context(batch,snapshot.get('environment')=='ISOLATED_TEST')
        if any(batch.get(k)!=snapshot.get(k) for k in CONTEXT) or batch['snapshot_id']!=snapshot['snapshot_id']:
            raise ValueError('STALE_OR_WRONG_SOURCE')
        actions=batch.get('actions')
        holds=batch.get('hold_team_ids')
        if not isinstance(actions,list) or not isinstance(holds,list) or (not actions and not holds):
            raise ValueError('SPECIFIC_BATCH_ACTIONS_AND_HOLDS_REQUIRED')
        if any(type(t) is not int for t in holds) or len(holds)!=len(set(holds)):
            raise ValueError('INVALID_OR_DUPLICATE_HOLD')
        valid_ids={t['team_id'] for t in snapshot['teams']}
        participants=set(holds)
        identities=set()
        action_ids=set()
        for action in actions:
            if not isinstance(action,dict) or claims_authority(action):
                raise ValueError('ACTION_CANNOT_AUTHORIZE_EXECUTION')
            aid=action.get('action_id')
            if not isinstance(aid,str) or not aid.strip() or aid in action_ids:
                raise ValueError('INVALID_OR_DUPLICATE_ACTION_ID')
            action_ids.add(aid)
            if any(action.get(k)!=batch.get(k) for k in (*CONTEXT,'decision_id','version','snapshot_id')):
                raise ValueError('ACTION_BATCH_BINDING_MISMATCH')
            if action.get('operation')!='TACTIC_CHANGE' or action.get('status')!='PROPOSED':
                raise ValueError('TACTIC_CHANGE_PROPOSED_REQUIRED')
            if action.get('codec_version')!=profile['codec_version']:
                raise ValueError('WRONG_CODEC_VERSION')
            if not isinstance(action.get('expected_effect'),str) or not action['expected_effect'].strip():
                raise ValueError('SPECIFIC_EXPECTED_EFFECT_REQUIRED')
            if action.get('effect_status')!='SIM_EFFECT_PENDING_PLAYER_MONTH':
                raise ValueError('UNVERIFIED_EFFECT_CLAIM')
            integer(action.get('team_id'),0,65535,'INVALID_TEAM_ID')
            tid=action['team_id']
            participants.add(tid)
            key=(tid,action.get('scope'),action.get('opponent_team_id'))
            if key in identities or tid in holds:
                raise ValueError('DUPLICATE_SCOPE_OR_HOLD_CONFLICT')
            identities.add(key)
            if action.get('scope')=='COACH_DEFAULT':
                result=validate_plan(action,snapshot,profile)
                if not result['valid']:
                    raise ValueError(';'.join(result['errors']))
                fields=[profile['fields'][c['field']] for c in action['changes']]
                if any(f.get('gm_control_enabled') is False for f in fields):
                    raise ValueError('GM_CONTROL_DISABLED')
                if any(not f['writable'] or not f['production_enabled'] for f in fields):
                    blocked.append(aid)
                blocks=result['prepared_blocks']
            elif action.get('scope')=='VS_OPPONENT_DEFENSE':
                blocks=validate_defense_action(action,snapshot,profile)
                if (not profile['opponent_overall_defense']['production_enabled']
                    or any(not profile['defensive_fields'][c['field']]['production_enabled'] for c in action['changes'])):
                    blocked.append(aid)
            else:
                raise ValueError('UNSUPPORTED_BATCH_SCOPE')
            prepared.append(dict(action_id=aid,team_id=tid,scope=action['scope'],
                opponent_team_id=action.get('opponent_team_id'),blocks=blocks))
        if not participants<=valid_ids or not 1<=len(participants)<=30:
            raise ValueError('BATCH_REQUIRES_1_TO_30_VALID_TEAMS')
    except (ValueError,KeyError,TypeError,IndexError,OverflowError) as exc:
        errors.append(str(exc))
    return dict(valid=not errors,executable=not errors and not blocked,errors=errors,
        blocked_action_ids=blocked,prepared_actions=prepared if not errors else [],
        batch_digest=batch_digest(batch) if isinstance(batch,dict) else None,
        execution_authorized=False,mode='OFFLINE_NO_PROCESS_HANDLES')


def propose_batch(snapshot,requests,batch_id,decision_id,version,hold_team_ids=(),profile=None):
    profile=profile or load_profile()
    actions=[]
    for request in requests:
        scope=request.get('scope','COACH_DEFAULT')
        if scope=='VS_OPPONENT_DEFENSE':
            if request.get('defensive_setting_scope')!='OVERALL':
                raise ValueError('OVERALL_DEFENSE_SCOPE_REQUIRED')
            actions.append(propose_overall_defense(snapshot,request['team_id'],request['opponent_team_id'],
                request['targets'],decision_id,version,request['action_id'],request['expected_effect'],profile))
        elif scope=='COACH_DEFAULT':
            actions.append(propose(snapshot,request['team_id'],normalize_freelance(request['targets'],profile),
                decision_id,version,request['action_id'],request['expected_effect'],profile=profile))
        else:raise ValueError('UNSUPPORTED_BATCH_SCOPE')
    actions.sort(key=lambda a:(a['team_id'],a['scope'],a.get('opponent_team_id') or -1))
    batch=dict(**{k:snapshot[k] for k in CONTEXT},operation='COACHING_BATCH_CHANGE',status='PROPOSED',
        batch_id=batch_id,decision_id=decision_id,version=version,snapshot_id=snapshot['snapshot_id'],
        actions=actions,hold_team_ids=sorted(hold_team_ids),execution_authorized=False)
    result=validate_batch(batch,snapshot,profile)
    if not result['valid']:
        raise ValueError(';'.join(result['errors']))
    return batch


def propose_overall_defense(snapshot,team_id,opponent_team_id,targets,decision_id,version,action_id,expected_effect,profile=None):
    profile=profile or load_profile()
    team=next(t for t in snapshot['teams'] if t['team_id']==team_id)
    record=next(g for g in team['gameplans'] if g['opponent_team_id']==opponent_team_id)
    overall=record.get('overall_defense')
    if not overall or overall.get('status')!='OBSERVED_OVERALL_VERIFIED':
        raise ValueError('OVERALL_RECORD_SELECTOR_NOT_VERIFIED')
    action=dict(**{k:snapshot[k] for k in CONTEXT},operation='TACTIC_CHANGE',status='PROPOSED',
        decision_id=decision_id,version=version,action_id=action_id,snapshot_id=snapshot['snapshot_id'],
        codec_version=profile['codec_version'],team_id=team_id,opponent_team_id=opponent_team_id,
        scope='VS_OPPONENT_DEFENSE',defensive_setting_scope='OVERALL',verified_coach_identity=team['coach_identity'],
        verified_overall_identity=copy.deepcopy(overall['identity']),old_defense_blocks=copy.deepcopy(overall['blocks']),
        changes=[dict(field=n,before_raw=overall['values'][n],after_raw=v) for n,v in targets.items()],
        expected_effect=expected_effect,effect_status='SIM_EFFECT_PENDING_PLAYER_MONTH',execution_authorized=False)
    validate_defense_action(action,snapshot,profile)
    return action
