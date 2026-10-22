"""Synthetic research records only; no actual team assessment or game access."""
from copy import deepcopy
from gm_core import analysis_packet as ap, decision_protocol as dp
from gm_core.workbench_common import now


def inputs():
    b=dict(career_id='synthetic',batch_id='SYNTHETIC_B1',snapshot_id='SYNTHETIC_S1',game_date='2021-12-12',player_potential_visibility='MASKED',
           data_updated_at='2026-10-19T00:00:00+00:00',publication_status='LOCAL_AUDITED_NOT_PUBLISHED',audit='PASS_VERIFIED')
    result=dict(source_binding=b,context={'synthetic':True},teams=[],team_stats=[],players=[],staff=[],coaching=[],defense=[],picks=[],finance=[],source_access=[])
    for tid in range(30):
        result['teams'].append(dict(team_id=tid,team='T'+str(tid),total_wins=13,total_losses=12,total_salary=100))
        totals=dict(w=13,l=12,made=760,attempted=1750,**{'3pt_made':240,'3pt_attempted':650},free_throws_attempted=500,
            turnover=200,assists=500,points=2300,pa=2350,offensive_rebounds=200,defensive_rebounds=600,season_year=2022)
        result['team_stats'].append(dict(team_id=tid,team='T'+str(tid),season_year=2022,totals=totals))
        c={f'contract_year_{i+1}':dict(value=(100 if i<3 else 0)) for i in range(6)}
        c.update({k:dict(value=v) for k,v in dict(years_left_on_contract=3,original_contract_years=3,contract_option=0,extension_length=0).items()})
        result['players'].append(dict(identity='s:roster:'+str(tid)+':0',name='Synthetic '+str(tid),team_id=tid,team='T'+str(tid),
            position='PG',face_id=tid,birth_date='2000-01-01',attributes={'3pt_shot':dict(raw=150,value=75)},
            salary=100,years_left=3,contract=c,season_totals={'times':0}))
    return result


def analysis():
    r=ap.prepare(inputs(),'2021-2022','CHECKPOINT',run_id='SYNTHETIC_A')
    annotations=[dict(team_id=t['team_id'],annotations={k:'Synthetic gap; HOLD pending player evidence' for k in ap.ANNOTATIONS},evidence_refs=['team:'+str(t['team_id'])]) for t in r['teams']]
    return ap.seal(ap.annotate(r,dict(teams=annotations)))


def review(a, tid):
    t=ap.team(a,tid); refs=['team:'+str(tid)]
    h=dict(baseline_refs=refs,mechanism_claim='Synthetic no-change baseline',alternative_explanations=['Synthetic sample'],
        expected_direction='No improvement claimed',observation_metrics=['efg'],minimum_evidence_description='Future comparable interval',
        falsification_conditions=['Player observes contradictory mechanism'],confounds=['Roster changes'])
    return dict(team_id=tid,player_assessments=[dict(source_identity=p['identity'],role_assessment='Synthetic reserve role',
        retain_or_research_position='HOLD pending use',key_evidence_refs=[p['evidence_ref']],unknowns=['Synthetic only'],review_depth='NORMAL') for p in t['player_supply']['players']],
        decision_dimensions={k:dict(conclusion='Synthetic reasoned HOLD; effect not established',evidence_refs=refs,unknowns=['Effect unknown'],alternatives=['Retain current configuration']) for k in dp.DIMENSIONS},
        competitive_window=dict(assessment='Synthetic HOLD',evidence_refs=refs,alternatives=['Research later']),
        team_interest_profile=dict(objective_and_window='Synthetic development case',evidence_refs=refs,role_priorities=['Shooting'],
            retain_thresholds=['Retain until better role fit demonstrated'],sell_conditions=['Benefit exceeds internal alternative'],
            pick_commitment_conditions=['Explicit source-bound pick only'],contract_risk_conditions=['No claimed signing capacity'],
            best_internal_alternative_id='internal:'+str(tid),reversal_conditions=['New contrary evidence']),
        evidence_refs=refs,uncertainties=['Synthetic only'],monitoring_hypothesis=h)


def alternatives(tid):
    alts=[]
    for cat in ('HOLD','INTERNAL','MARKET'):
        alts.append(dict(alternative_id=cat.lower()+':'+str(tid),category=cat,status='VIABLE_CANDIDATE' if cat=='HOLD' else 'RESEARCH',
            problem='Synthetic role question',proposed_means='Retain current setup pending evidence',evidence_refs=['team:'+str(tid)],
            benefit_hypotheses=['No benefit assumed'],costs_and_opportunity_costs='Foregone alternative remains unproven',
            reversibility='No action yet',counterevidence=['Small sample'],change_conditions=['New evidence'],selection_reason='Synthetic development HOLD'))
    return dict(team_id=tid,alternatives=alts)


def complete(store, a=None):
    a=a or analysis(); store.save_analysis(a)
    d=store.save_decision(dp.begin(a,'SYNTHETIC_D'))
    for tid in d['expected_team_ids']:
        for command,payload in [('submit-review',review(a,tid)),('submit-alternatives',alternatives(tid))]:
            updated,art=dp.apply(d,a,command,payload); d=store.save_decision(updated,d['revision'],art)
    return a,d


def selection(exclude=()):
    return dict(portfolio_id='P',selected_offer_versions=[],selected_internal_action_versions=[],research_action_ids=[],
        holds=[dict(team_id=t,reason='Synthetic HOLD; no advantage established',evidence_refs=['team:'+str(t)]) for t in range(30) if t not in exclude],
        rejected_alternatives=[],team_combination_reviews=[])


def offer(oid='O', source=0, target=1, identity=None):
    return dict(offer_id=oid,team_ids=[source,target],moves=[dict(kind='TRADE_PLAYER',source_identity=identity or 's:roster:'+str(source)+':0',from_team_id=source,to_team_id=target)],conditions=[],dependency_ids=[])


def response(o,tid,stance='ACCEPT_IN_PRINCIPLE'):
    return dict(response_id=o['offer_id']+':'+str(tid),offer_id=o['offer_id'],terms_revision=o['terms_revision'],terms_digest=o['terms_digest'],
        responding_team_id=tid,team_interest_revision=1,stance=stance,rationale=dict(gain='Synthetic role gain',cost='Synthetic asset cost',
            opportunity_cost='Internal option retained for comparison',why_better_than_hold='Hypothetical role gap filled'),
        alternative_refs=['internal:'+str(tid)],conditions=[],evidence_refs=['team:'+str(tid)])


def coaching_snapshot(binding):
    from coach_codec import load_profile,decode,block_key
    profile=load_profile(); raw=bytearray(0x160)
    for f in profile['fields'].values():
        value=int(next(iter(f['enum']))) if isinstance(f.get('enum'),dict) else (18 if f.get('enum')=='LOADED_PLAYBOOKS' else 50)
        old=int.from_bytes(raw[f['offset']:f['offset']+f['storage_bytes']],'little')
        mask=((1<<f['width'])-1)<<f['start_bit']
        raw[f['offset']:f['offset']+f['storage_bytes']]=((old&~mask)|(value<<f['start_bit'])).to_bytes(f['storage_bytes'],'little')
    blocks={block_key(f['offset'],f['storage_bytes']):raw[f['offset']:f['offset']+f['storage_bytes']].hex() for f in profile['fields'].values()}
    return dict(schema_version=1,snapshot_id=binding['snapshot_id'],environment='ISOLATED_TEST',observation_status='OBSERVED_LIVE_READ_ONLY',
        career_id=binding['career_id'],source_batch_id=binding['batch_id'],game_season='2021-2022',game_date=binding['game_date'],
        data_updated_at=binding['data_updated_at'],policy_id='PLAYER_RULES_20261017_V3',codec_version=profile['codec_version'],
        teams=[dict(team_id=t,abbreviation='T'+str(t),coach_identity=dict(team_id=t,identity_tag='SYNTHETIC_'+str(t)),
                    values={n:decode(raw,f) for n,f in profile['fields'].items()},blocks=deepcopy(blocks),gameplans=[]) for t in range(30)],
        playbooks=[dict(enum_id=18,name='Synthetic Book',play_crc_slots=[0]*68)],loaded_playbook_ids=[18])
