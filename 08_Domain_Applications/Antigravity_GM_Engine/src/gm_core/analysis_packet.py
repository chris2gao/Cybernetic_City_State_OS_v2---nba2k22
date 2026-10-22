"""Immutable fact packets with caller-supplied, separately validated analysis."""
from copy import deepcopy
import re
from uuid import uuid4
from .analysis_metrics import metrics, interval, temporal_links, VERSION
from .workbench_common import now, reject_authority, require, text_required

ANNOTATIONS = ('diagnosis','talent_gap_evidence','utilization_hypothesis','internal_levers',
               'market_clues','strategy_change_signals','alternatives_explanations')


def require_gm_packet(run):
    if run['source_binding'].get('player_potential_visibility')!='MASKED':
        raise ValueError('UNMASKED_HISTORICAL_BATCH_EXCLUDED_FROM_GM')


def prepare(inputs, season, node_type, previous=None, finance=None, strategies=(), run_id=None,
            history_context=None, code_commit=None):
    if not re.fullmatch(r'\d{4}-\d{4}', season or '') or int(season[-4:])!=int(season[:4])+1 or node_type not in ('BOOTSTRAP','SEASON_INITIALIZATION','CHECKPOINT'):
        raise ValueError('EXPLICIT_SEASON_AND_NODE_TYPE_REQUIRED')
    b = deepcopy(inputs['source_binding'])
    require_gm_packet(dict(source_binding=b))
    context = dict(season=season, node_type=node_type, history_branch_context=history_context,
                   source_context=deepcopy(inputs.get('context',{})))
    comparable = bool(previous and history_context and previous['source_binding']['career_id']==b['career_id']
        and previous.get('history_branch_context')==history_context and previous.get('season')==season
        and previous['source_binding'].get('game_date','') < b.get('game_date',''))
    if finance and finance['source_binding']['career_id'] != b['career_id']:
        raise ValueError('FINANCE_CAREER_MISMATCH')
    for s in strategies:
        if s['career_id'] != b['career_id']:
            raise ValueError('STRATEGY_CAREER_MISMATCH')
    teams = []
    for t in inputs['teams']:
        tid = t['team_id']
        stats = next((s for s in inputs['team_stats'] if s['team_id']==tid), None)
        totals = deepcopy(stats['totals']) if stats else {}
        stat_ref = 'team_stats:'+str(tid)
        # Captured TEAM_STATS uses the ending year (2022 for 2021-2022).
        season_matches = bool(stats and stats['season_year']==int(season[-4:]))
        players = deepcopy([p for p in inputs['players'] if p['team_id']==tid])
        for p in players:
            p['evidence_ref'] = 'player:'+p['identity']
            p['identity_scope'] = 'BATCH_LOCAL_NOT_PERMANENT'
            p['decoded_attributes'] = {k:v.get('value') for k,v in (p.get('attributes') or {}).items()
                if isinstance(v,dict) and k.casefold() not in ('potential','intangibles')}
            p['potential_visibility']=dict(value=None,persisted_placeholder=1,status='MASKED_NOT_GAME_OBSERVED')
            p['unknowns'] = ['IN_GAME_OVR_AGE_AND_CONTRACT_CLASSIFICATION_NOT_CERTIFIED']
        old = next((s for s in previous['team_stats'] if s['team_id']==tid), None) if previous else None
        local_comparable = comparable and season_matches and bool(old and stats and old['season_year']==stats['season_year'])
        team = dict(team_id=tid, team=t['team'], observed_team=t,
            observed_performance=dict(cumulative=metrics(totals if season_matches else {}, stat_ref), raw_totals=totals,
                interval=interval(totals, old['totals'] if old else {}, local_comparable),
                comparability='EXPLICIT_SAME_CONTEXT_ORDERED' if local_comparable else 'NOT_ESTABLISHED'),
            player_supply=dict(source_identity_set=sorted(p['identity'] for p in players), players=players,
                coverage='COMPLETE_SOURCE_ROSTER_NOT_ASSESSED',
                temporal_links=temporal_links(players, previous['players']) if previous else []),
            staff_context=dict(rows=[s for s in inputs['staff'] if s['team_id']==tid],
                appointable_ui_roles=6, native_team_role_slots=8, appointment_effect='UNKNOWN'),
            coaching_context=dict(defaults=[c for c in inputs['coaching'] if c['team_id']==tid], overall=[c for c in inputs['defense'] if c['team_id']==tid]),
            financial_and_assets=dict(finance=[f for f in inputs['finance'] if f['team_id']==tid], picks=[p for p in inputs['picks'] if p['team_id']==tid],
                finance_run_id=finance['run_id'] if finance else None, signing_capacity=None),
            strategy_refs=[dict(state_id=s['state_id'], revision=s['revision'], status=s['status'],
                alignment='SAME_BATCH' if s['source_binding']['batch_id']==b['batch_id'] else 'REFERENCE_ONLY') for s in strategies if s['team_id']==tid],
            annotations=None, source_refs=['team:'+str(tid),stat_ref],
            issues=[] if stats else [dict(code='TEAM_STATS_MISSING', effect='UNKNOWN_METRIC')])
        if not team['staff_context']['rows']:
            team['issues'].append(dict(code='STAFF_SOURCE_GAP', effect='REVIEW_ONLY'))
        if stats and not season_matches:
            team['issues'].append(dict(code='SEASON_ANCHOR_MISMATCH',effect='UNKNOWN_METRIC'))
        for m in team['observed_performance']['interval']['metrics'].values():
            m['input_refs']=[ref.replace('interval:', 'interval:'+str(tid)+':',1) for ref in m['input_refs']]
        teams.append(team)
        if 'native' in inputs:
            attach_tactics(team,inputs)
    ids = [t['team_id'] for t in teams]
    identities = [p['identity'] for t in teams for p in t['player_supply']['players']]
    if len(ids)!=len(set(ids)) or len(identities)!=len(set(identities)) or set(identities)!={p['identity'] for p in inputs['players']}:
        raise ValueError('SOURCE_COVERAGE_IDENTITY_CONFLICT')
    result=dict(analysis_run_id=run_id or uuid4().hex, revision=1, created_at=now(), sealed_at=None,
        source_binding=b, previous_source_binding=deepcopy(previous['source_binding']) if previous else None,
        supersedes_run_id=None,
        context=context, code_commit=code_commit, calculation_version=VERSION, knowledge_version='M2_KNOWLEDGE_V1',
        status='DRAFT_FACTS', authority='ANALYSIS_ONLY', execution_authorized=False,
        expected_team_ids=sorted(ids), read_team_ids=sorted(ids), prepared_team_ids=sorted(ids), annotated_team_ids=[],
        source_access=deepcopy(inputs['source_access']), method_registry=dict(version=VERSION,
            formula_source='gm_core.analysis_metrics', possessions='UNKNOWN', identity='BATCH_LOCAL'),
        finance_run_id=finance['run_id'] if finance else None,
        finance_alignment='NOT_LINKED' if not finance else ('SAME_BATCH' if finance['source_binding']['batch_id']==b['batch_id'] else 'DIFFERENT_BATCH_REVIEW_REQUIRED'),
        issue_index=[dict(team_id=t['team_id'], **i) for t in teams for i in t['issues']], teams=teams)
    if 'native' in inputs:
        result.update(tactical_version='M3_T_V1',native_field_catalog=deepcopy(inputs['native']['field_catalog']),
            native_registry_version=inputs['native']['consumer_registry_version'],potential_mask=deepcopy(inputs['potential_mask']))
    return result


def team(run, key):
    require_gm_packet(run)
    rows = [t for t in run['teams'] if str(t['team_id'])==str(key) or t['team']==str(key).upper()]
    if len(rows)!=1:
        raise ValueError('TEAM_NOT_FOUND')
    return rows[0]


def evidence(run, ref):
    require_gm_packet(run)
    # Only values recoverable from this immutable packet are accepted as fact refs.
    if ref in run.get('reference_evidence',{}):
        return deepcopy(run['reference_evidence'][ref])
    if ref in run.get('supplemental_evidence',{}):
        return deepcopy(run['supplemental_evidence'][ref])
    for t in run['teams']:
        tc=t.get('tactical_context',{})
        if ref=='tactical:'+str(t['team_id']):
            value=tactical_summary(t)
            break
        if ref=='tactical-playbook:'+str(t['team_id']):
            value=tc.get('playbook',dict(status='NOT_OBSERVED'))
            break
        if ref=='tactical-training:team:'+str(t['team_id']):
            value=tc.get('team_training',dict(status='NOT_OBSERVED'))
            break
        if ref in tc.get('evidence',{}):
            value=tc['evidence'][ref]
            break
        if ref=='team:'+str(t['team_id']):
            value=t['observed_team']
            break
        prefix='team_stats:'+str(t['team_id'])
        if ref==prefix or ref.startswith(prefix+':'):
            value=t['observed_performance']['raw_totals']
            if ref!=prefix:
                value=value.get(ref[len(prefix)+1:])
            break
        prefix='metric:'+str(t['team_id'])+':'
        if ref.startswith(prefix) and ref[len(prefix):] in t['observed_performance']['cumulative']:
            value=t['observed_performance']['cumulative'][ref[len(prefix):]]
            break
        prefix='interval:'+str(t['team_id'])+':'
        if ref.startswith(prefix):
            value=t['observed_performance']['interval']['counters'].get(ref[len(prefix):])
            break
        if ref=='coaching:'+str(t['team_id']):
            value=t['coaching_context']['defaults']
            break
        if ref=='finance:'+str(t['team_id']):
            value=t['financial_and_assets']['finance']
            break
        matches=[s for s in t['staff_context']['rows'] if isinstance(s.get('identity'),str) and ref=='staff:'+s['identity']]
        if matches:
            value=matches[0]
            break
        matches=[s for s in t['coaching_context']['overall'] if ref=='defense:'+str(t['team_id'])+':'+str(s['opponent_team_id'])]
        if matches:
            value=matches[0]
            break
        matches=[p for p in t['financial_and_assets']['picks'] if isinstance(p.get('asset_id'),str) and ref=='pick:'+p['asset_id']]
        if matches:
            value=matches[0]
            break
        matches=[p for p in t['player_supply']['players'] if ref==p['evidence_ref']]
        if matches:
            p=matches[0]
            value={k:p[k] for k in ('identity','name','team_id','position','salary','years_left','decoded_attributes','season_totals')}
            break
    else:
        raise ValueError('UNKNOWN_PACKET_EVIDENCE_REF:'+str(ref))
    return dict(ref_id=ref, kind='METRIC' if ref.startswith('metric:') else 'FACT',
        binding=run['source_binding'], run_id=run['analysis_run_id'], value=value, availability='UNKNOWN' if value in (None,{},[]) else 'AVAILABLE', method_version=VERSION)


def validate_refs(run, refs):
    if not isinstance(refs, list) or not refs:
        raise ValueError('EVIDENCE_REFS_REQUIRED')
    for ref in refs:
        evidence(run, ref)


def annotate(run, payload):
    reject_authority(payload)
    if run['sealed_at']:
        raise ValueError('SEALED_ANALYSIS_IMMUTABLE')
    require(payload, ('teams',))
    seen=set()
    for item in payload['teams']:
        require(item, ('team_id','annotations','evidence_refs'))
        if set(item)-{'team_id','annotations','evidence_refs'} or item['team_id'] in seen:
            raise ValueError('ANNOTATION_ONLY_UNIQUE_TEAMS')
        seen.add(item['team_id'])
        t=team(run,item['team_id'])
        require(item['annotations'], ANNOTATIONS)
        for key in ANNOTATIONS:
            v=item['annotations'][key]
            if not isinstance(v,(str,list,dict)) or not v:
                raise ValueError('ANNOTATION_CONCLUSION_OR_REASONED_GAP_REQUIRED:'+key)
        validate_refs(run,item['evidence_refs'])
        t['annotations']=deepcopy(item)
    run['annotated_team_ids']=sorted(t['team_id'] for t in run['teams'] if t['annotations'])
    run['status']='DRAFT_ANNOTATED'
    return run


def seal(run):
    if run['sealed_at']:
        raise ValueError('SEALED_ANALYSIS_IMMUTABLE')
    complete = len(run['expected_team_ids'])==30 and set(run['annotated_team_ids'])==set(run['expected_team_ids'])
    for t in run['teams']:
        ps=t['player_supply']
        if sorted(p['identity'] for p in ps['players']) != ps['source_identity_set']:
            raise ValueError('ROSTER_COVERAGE_MISMATCH')
    run['status']='SEALED_COMPLETE' if complete else 'SEALED_PARTIAL'
    run['sealed_at']=now()
    return run


def summary(run):
    require_gm_packet(run)
    return {**{k:run[k] for k in ('analysis_run_id','revision','status','source_binding','context','sealed_at','finance_alignment')},
        'authority':'ANALYSIS_ONLY','execution_authorized':False,
        'teams':[dict(team_id=t['team_id'], team=t['team'], roster_count=len(t['player_supply']['source_identity_set']),
            annotation_status='ANNOTATED' if t['annotations'] else 'NOT_ASSESSED', issues=t['issues']) for t in run['teams']],
        'access_summary':[dict(entity=a['entity'], read_count=a['read_count'], status=a['status']) for a in run['source_access']]}


def attach_tactics(t, inputs):
    """Normalize DEV14 safe DTOs; no native decoding, threshold diagnoses or effects invented."""
    native=inputs['native'];tid=t['team_id'];metadata=native['context'] or {}
    catalog=native['field_catalog']
    objects={o['object_key']:deepcopy(o) for o in native['objects'] if o['team_id']==tid}
    cells={}
    evidence_index={}
    for row in native['values']:
        if row['team_id']!=tid or row['field_key'] not in catalog:
            continue
        if row['registry_version']!=metadata.get('registry_version') or any(row[k]!=metadata.get(k) for k in ('save_instance_id','generation_id')):
            raise ValueError('MIXED_NATIVE_SOURCE_BINDING')
        cells.setdefault(row['object_key'],{})[row['field_key']]=deepcopy(row)
        evidence_index['native:'+row['identity']]=deepcopy(row)
    for o in objects.values():
        o['field_keys']=[k for k in (o['field_keys'] or []) if k in catalog]
        o['fields']=cells.get(o['object_key'],{})
        o['evidence_ref']='native-object:'+o['object_key']
        evidence_index[o['evidence_ref']]={k:v for k,v in o.items() if k!='fields'}
    by_slot={}
    for o in native['objects']:
        ident=o.get('native_identity') or {}
        if o['target_kind'].startswith('PLAYER_') and ident.get('pool_slot') is not None:
            by_slot.setdefault((o['team_id'],ident['pool_slot']),set()).add(ident.get('identity_tag'))
    for p in t['player_supply']['players']:
        tags=by_slot.get((tid,p.get('pool_slot')),set())-{None}
        tag=next(iter(tags)) if len(tags)==1 else None
        relevant=[o for o in objects.values() if tag and (o['selector'] or {}).get('player_identity')==tag]
        merged={k:r for o in relevant for k,r in o['fields'].items()}
        playtypes=[merged.get('playtype.slot'+str(i),{}).get('value') for i in range(1,5)]
        training={k:r['value'] for k,r in merged.items() if k.startswith('training.')}
        totals=p.get('season_totals') or {};g=totals.get('times');minutes=totals.get('minutes')
        context=dict(status='OBSERVED_PARTIAL' if relevant else 'NOT_OBSERVED',native_player_identity=tag,
            native_player_id=next((o['native_identity'].get('native_player_id') for o in relevant),None),
            play_types=playtypes,play_type_labels=[catalog.get('playtype.slot'+str(i+1),{}).get('enum',{}).get(str(v)) if v is not None else None for i,v in enumerate(playtypes)],
            initiator=merged.get('playtype.initiator',{}).get('value'),
            named_tendencies={k:r['value'] for k,r in merged.items() if k.startswith('tendency.')},
            training=dict(values=training,status='OBSERVED' if training else 'NOT_OBSERVED',position_specific_templates='UNKNOWN',fatigue='NOT_OBSERVED',mentor='NOT_OBSERVED',effect='UNKNOWN'),
            rotation_bias=merged.get('rotation.intangibles',{}).get('value'),
            load=dict(games=g,minutes_total=minutes,minutes_per_game=minutes/g if type(g) in (int,float) and g>0 and type(minutes) in (int,float) else None,
                recent_schedule='NOT_OBSERVED',fatigue='NOT_OBSERVED'),
            objects=[o['object_key'] for o in relevant],field_refs=['native:'+r['identity'] for r in merged.values()],
            role_assignment='GM_RESEARCH_REQUIRED_NO_AUTOMATIC_TOUCH_THRESHOLD',market_value_uses_rotation_bias=False)
        p['tactical_context']=context
        evidence_index['tactical-player:'+p['identity']]=context
        evidence_index['tactical-training:'+p['identity']]=context['training']
    coach=next((o for o in objects.values() if o['target_kind']=='COACH_DEFAULT'),None)
    book=dict(status='NOT_OBSERVED',play_type_coverage='UNKNOWN',crc_semantics='UNKNOWN')
    directory=metadata.get('team_directory') or {}
    if str(tid) in directory and native['books']:
        from gm_state_io.team_book import team_book
        try:
            own=team_book(directory[str(tid)],native['books'])
            loaded=next(b for b in native['books'] if b['enum_id']==own['enum_id'] and b['unique_id']==own['unique_id'])
            book.update(status='OBSERVED_LOADED_TEAM_NAMED_BOOK',identity=own,play_crc_slots=loaded.get('play_crc_slots'),
                current_binding=coach['fields'].get('coach.PlaybookID',{}).get('value') if coach else None)
        except ValueError as exc:
            book.update(status='NOT_OBSERVED',reason=str(exc))
    training={k:r['value'] for o in objects.values() if o['target_kind']=='TEAM_TRAINING' for k,r in o['fields'].items()}
    traits=next((row['traits'] for row in native.get('coach_traits',[]) if row['team_id']==tid and row['traits']),None)
    t['tactical_context']=dict(status='OBSERVED_PARTIAL' if objects else 'NOT_OBSERVED',objects=objects,
        evidence=evidence_index,coach_object_key=coach['object_key'] if coach else None,
        coach_settings={k:r['value'] for k,r in coach['fields'].items()} if coach else {},
        coach_ratings=[dict(identity=s['identity'],attributes=s.get('attributes')) for s in t['staff_context']['rows'] if s['role']=='HEAD_COACH'],
        system_proficiencies=dict(status='STATIC_NATIVE_DECODE' if traits else 'NOT_OBSERVED',values=traits['system_proficiencies'] if traits else None,
            decoder='DEV12_EXISTING_READER_ON_SEALED_DEV14_RECORD',optimal_system_claim='NOT_ESTABLISHED'),
        coach_native_traits=traits,playbook=book,
        team_training=dict(status='OBSERVED' if training else 'NOT_OBSERVED',values=training),
        personal_matchups_requested=[pair for pair in native['defense_matchups'] if pair[0]==tid],
        registry_version=metadata.get('registry_version'),unknowns=deepcopy(native['unknowns']),
        effect_certainty=dict(live_3d='UNKNOWN',calendar_sim='UNKNOWN'))


def tactical_summary(t):
    tc=t.get('tactical_context',{})
    return dict(team_id=t['team_id'],status=tc.get('status','NOT_OBSERVED'),coach_settings=tc.get('coach_settings',{}),
        coach_ratings=tc.get('coach_ratings',[]),system_proficiencies=tc.get('system_proficiencies',{'status':'NOT_OBSERVED'}),
        playbook=tc.get('playbook',{'status':'NOT_OBSERVED'}),team_training=tc.get('team_training',{'status':'NOT_OBSERVED'}),
        object_count=len(tc.get('objects',{})),personal_matchups_requested=tc.get('personal_matchups_requested',[]),
        unknowns=tc.get('unknowns',[]),effect_certainty=tc.get('effect_certainty',{'live_3d':'UNKNOWN','calendar_sim':'UNKNOWN'}))
