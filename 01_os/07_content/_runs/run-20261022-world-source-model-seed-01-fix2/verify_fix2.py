"""Offline semantic/source/queue regressions. Never imports business executors."""
import collections, copy, hashlib, json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
DOM='08_Domain_Applications/Antigravity_GM_Engine/'
DEV=DOM+'docs/development/'
RUN='01_os/07_content/_runs/run-20261022-world-source-model-seed-01-fix2/'
OLD='01_os/07_content/_runs/run-20261022-world-source-model-seed-01/'
BASE='8cdbfaefbcb001c6ca0612017957c6414876eea4'
SEED='142531f2d60813bce5b90254c5e347050c40b406'
CAT='GAME_UI_FIELD_CATALOG_V0.json';HINT='GAME_NATIVE_OBJECT_HINTS_V0.json';QUEUE='FLASH_R00_PRIORITY_QUEUE_V0.json'
def git(*args): return subprocess.check_output(['git','--no-optional-locks',*args],cwd=ROOT)
def load(p): return json.loads((ROOT/p).read_bytes())
def old(p): return json.loads(git('show',BASE+':'+p))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v,msg):
    if not v: raise AssertionError(msg)
def resolve(ref):
    path,sep,fragment=ref.partition('#')
    full=path if path.startswith(('08_Domain_Applications/','01_os/')) else (DEV+path if path.startswith(('GAME_','FLASH_')) else DOM+path)
    p=ROOT/full
    require(p.is_file(),'missing source '+ref)
    if fragment.startswith('/'):
        body=load(full)
        for part in fragment[1:].split('/'):
            part=part.replace('~1','/').replace('~0','~')
            body=body[int(part)] if isinstance(body,list) else body[part]
        return body
    require(not sep or not fragment,'unsupported anchor '+ref)
    return p.read_bytes()
def data(): return load(DEV+CAT),load(DEV+HINT),load(DEV+QUEUE)
def expected_entities(c):
    """Independent semantic assertions selected from raw-source and audit counterexamples."""
    expected={}
    for f in c['fields']:
        fid=f['field_id'];leaf=fid.rsplit('.',1)[-1]
        if fid.startswith('PROFILE.PLAYER_STATS.') or fid.startswith('AG01D.UI.SEASON_STATS_AND_LEADERBOARDS.'):
            expected[fid]='SeasonTotals'
        elif fid.startswith('AG01D.UI.ROOKIE_REPORT.'):
            expected[fid]={'draft_pick_original_team':'DraftPick','draft_pick_owner_team':'PickOwnership',
               'draft_pick_round':'DraftPick','draft_pick_year':'DraftPick','draft_prospect_pool':'NativeObject','is_rookie':'PlayerIncarnation'}[leaf]
        elif fid.startswith('DRAFT_ASSET.'):
            expected[fid]='PickOwnership' if leaf=='current_owner_ptr' else 'DraftPick'
        elif fid.startswith('OPS.TRADE_MENU.'):expected[fid]='StateObservation'
        elif fid in ('PLAYER.current_team_ptr','PLAYER.contract_team_ptr'):
            expected[fid]='RosterMembership' if leaf=='current_team_ptr' else 'Contract'
        elif fid.startswith('AG01D.UI.SINGLE_GAME_BOXSCORE.'):
            if leaf in ('player_statline','player_points_conservation','player_advanced_analytics'):expected[fid]='PlayerGameStatline'
            if leaf in ('final_score','linescore_quarters','linescore_overtime','team_advanced_stats'):expected[fid]='TeamGameResult'
    return expected
def invariants(c,h,q):
    before=old(DEV+CAT);prev=before['fields'];cur=c['fields']
    require(len(cur)==888 and len({f['field_id'] for f in cur})==888,'888 original unique rows')
    require([x['field_id'] for x in prev]==[x['field_id'] for x in cur],'field order/id changed')
    require(c['coverage']==before['coverage'] and c['semantics']==before['semantics'],'coverage/age/world rule changed')
    require(c['semantics']['age_formula_candidate']=='original_draft_year - birth_year + years_pro','age formula')
    require(c['semantics']['world_branching'] is False,'independent save/no branching')
    mutable={'entity','discovery_group_ref','next_probe','adjacent_fields_or_regions'}
    touched=set(expected_entities(c))
    for a,b in zip(prev,cur):
        for k,v in a.items():
            if k not in mutable:require(b.get(k)==v,f'original {a["field_id"]}/{k} changed')
        require(b['current_save_live_verified'] is False and b['full_enumeration_certified'] is False,'maturity promoted')
        if a['field_id'] not in touched and not (a['field_id']=='AG01D.UI.PLAYER_CARD.player_tendencies' or a['field_id'].startswith('PLAYER.TENDENCY.BYTE_')):
            require(a==b,'unrelated row changed '+a['field_id'])
    actions=load(DEV+'GAME_ACTION_DISCOVERY_SEED_V0.json')['entries']
    require(len(actions)==207,'action count')
    for x in actions:
        require(all(x[k] is False for k in ['current_task_real_write','current_task_readback_verified','current_task_save_reload_verified','production_enabled_by_this_catalog']),'action enabled')
    require(len(h['slot_inventory_historical'])==75 and len(q['items'])==12,'source structure changed')
    require(q['status']=='NOT_DISPATCHED' and all(x['status']=='NOT_RUN' for x in q['items']),'Flash dispatched')
def semantics(c,h,q):
    expected=expected_entities(c);require(len(expected)==74,'affected source rule set incomplete')
    actual={f['field_id']:f for f in c['fields']}
    for fid,entity in expected.items():
        f=actual[fid];require(f['entity']==entity,'wrong semantic entity '+fid)
        b=f['semantic_binding'];require(b['target_semantic_entity']==entity and b['raw_source_ref']==f['source_refs'][0],'raw/semantic relation '+fid)
        require(b['raw_source_object'] and b['record_grain'] and b['relations'],'missing object/grain/relations '+fid)
        time=b['identity_and_time']
        require(time['scope']==['independent_game_save','technical_binding','capture_batch'],'scope '+fid)
        require(time['resolved_identity_values']=='UNKNOWN' and time['game_effective_time']=='UNKNOWN' and time['observed_at']=='UNKNOWN','invented identity/time '+fid)
        require(all(r['status']=='UNKNOWN' for r in b['relations']),'unknown relation promoted '+fid)
        roles=time['candidate_key_roles']
        if entity=='SeasonTotals':
            require({'player_uid','season_uid','optional_team_stint_uid'}<=set(roles) and 'game_uid' not in roles,'season grain '+fid)
            require(b['not_game_event'] is True and time['stint_status'].startswith('UNKNOWN'),'stint inference '+fid)
        if entity=='PlayerGameStatline':
            require({'player_uid','team_uid','game_uid','season_uid'}<=set(roles) and b['not_season_accumulator'] is True,'box grain '+fid)
        if entity in ('DraftPick','PickOwnership'):
            require({'draft_pick_uid','draft_season','round','original_franchise_uid'}<=set(roles),'draft asset scope '+fid)
            require(b['ownership_change_event'].startswith('UNKNOWN'),'fabricated transaction '+fid)
    # The raw matrices themselves establish source object and record grain, without current-layout certification.
    m=load(DOM+'research/native_access/AG_NATIVE_01D/ui_native_source_matrix.json')['screens']
    require(m['ROOKIE_REPORT']['fields']['draft_pick_owner_team']['native_source']=='Slot 36 DRAFT_ASSETS','raw pick source')
    require(m['SEASON_STATS_AND_LEADERBOARDS']['fields']['season_points']['native_source']=='Slot 24 PLAYER_STATS','raw season source')
    require(actual['AG01D.UI.SINGLE_GAME_BOXSCORE.player_statline']['semantic_binding']['raw_source_object']=='BOXSCORE_STATBANK','raw Box source')
def sources(c,h,q):
    refs=[]
    for f in c['fields']:
        if 'semantic_binding' in f:
            refs.append(f['semantic_binding']['raw_source_ref'])
            require(resolve(refs[-1]) is not None,'empty semantic source')
    for row in q['items']:
        refs+=row['source_refs']+row['root_refs']+row['field_refs']+[x['ref'] for x in row['start_points']]
        refs+=row.get('setting_field_refs',[])
        refs.append(row['failure_escalation']['contract_ref'])
    for candidate in h['historical_layout_conflicts'][0]['candidates']:refs+=candidate['source_refs']
    for r in refs:resolve(r)
    actions=load(DEV+'GAME_ACTION_DISCOVERY_SEED_V0.json')['entries']
    for a in q['items'][11]['action_refs']:
        x=resolve(a['entry_ref'])
        require(x['action_id']==a['action_id'] and x['source_ref']==a['original_source_ref'] and x['known_read_source']==a['known_read_source_raw'],'action/source mismatch')
        resolve(a['original_source_ref']);resolve(a['resolved_read_source_ref'])
        require(a['execution_allowed'] is False,'action source resolution authorized execution')
    require(len(actions)==207,'actions accidentally replaced')
def conflict(c,h,q):
    x=h['historical_layout_conflicts'][0]
    require(x['id']=='PLAYER_TENDENCIES_OFFSET_BUILD_CONFLICT','missing conflict id')
    require({a['offset_range'] for a in x['candidates']}=={'0x170..0x260','0x458..0x4BA'},'lost historical location')
    require(x['selected_candidate'] is None and x['canonical_equivalence_proven'] is False,'arbitrary location selection')
    require(all(a['build_status']=='UNKNOWN' and a['object_base_equivalence']=='UNKNOWN' and a['current_save_verified'] is False for a in x['candidates']),'unproved location acceptance')
    a=next(f for f in c['fields'] if f['field_id']=='AG01D.UI.PLAYER_CARD.player_tendencies')
    require(a['native_offset_or_getter_hint']=='0x170..0x260' and a['original_source_status']=='NATIVE_VERIFIED','source history overwritten')
    affected=[f for f in c['fields'] if f['field_id'].startswith('PLAYER.TENDENCY.BYTE_') or f is a]
    require(len(affected)==100,'not all tendency slots linked')
    for f in affected:
        require(f['discovery_group_ref']=='NH_TENDENCIES' and 'NH_CAREER' not in f['next_probe'],'wrong tendency neighborhood')
        require(resolve(f['offset_conflict_ref'])['id']==x['id'],'broken conflict ref')
        require(f['current_save_live_verified'] is False,'tendency verified without evidence')
    require(not any('CAREER' in a['region'] or '0xFC' in a['region'] for a in a['adjacent_fields_or_regions']),'career adjacency retained')
    require(resolve(x['investigation_entry'])['id']=='R00-04','wrong conflict investigation')
def human(c,h,q):
    reg=c['source_reference_registry']['HUMAN_DECISION_20261022']
    require(reg['commit_sha']==SEED and reg['path']==OLD+'human_task.md','not original Human digest')
    raw=git('show',reg['commit_sha']+':'+reg['path'])
    require(hashlib.sha256(raw).hexdigest()==reg['sha256'],'Human source hash')
    require(reg['line_start']==3 and reg['line_end']==3,'imprecise Human digest location')
    text=raw.decode('utf-8').splitlines()[2]
    require('original_draft_year - birth_year + years_pro' in text and 'not a certified engine formula' in text and 'independent per NBA2K22 save' in text,'Human content changed')
    ids={f['field_id'] for f in c['fields'] if 'HUMAN_DECISION_20261022' in f['source_refs']}
    require(ids==set(reg['referencing_field_ids'])=={'PLAYER.age_derived','PLAYER.birth_year','PLAYER.original_draft_year','PLAYER.world_draft_season','PLAYER.display_age_observed','PLAYER.years_pro'},'six ref map incomplete')
    require('not engine behavior' in reg['authority_scope'],'Human rule promoted to engine algorithm')
def queue(c,h,q):
    rows=q['items'];require([x['id'] for x in rows]==[f'R00-{i:02d}' for i in range(1,13)],'R00 IDs')
    for key in ('read_only_method','object_scope','expected_evidence','stop_condition'):
        require(len({x[key] for x in rows})==12,'generic reused row '+key)
    require(len({x['negative_control']['case'] for x in rows})==12,'generic negative controls')
    for row in rows:
        require(row['start_points'] and all(p['ref'] and p['role'] for p in row['start_points']),'missing objective anchor '+row['id'])
        b=row['max_investigation']
        require(0<b['max_minutes']<=20 and 0<b['max_sample_records']<=3 and b['max_distinct_failed_paths']==2 and b['expansion_allowed'] is False,'unbounded investigation '+row['id'])
        require(b['allowed_regions_or_records'] and row['positive_control']['case'] and row['negative_control']['case'],'no counterexamples')
        require(row['unknown_result']['status']=='HOLD_UNKNOWN' and row['failure_escalation']['after_distinct_failed_paths']==2,'unknown or escalation removed')
        require(row['game_write_authorized'] is False and row['status']=='NOT_RUN','row grants execution')
        require('never UNKNOWN-count reduction' in row['evidence_contract']['acceptance_basis'],'wrong readiness metric')
    # Direct source requirements for late tasks, not merely nonempty references.
    ten=rows[9];require(not ten['field_refs'],'world identity inferred from draft season')
    require({'src/save_context.py','src/gm_state_io/workspace.py','docs/DEV14_STATE_IO_RUNBOOK.md'}<={x['ref'] for x in ten['start_points']},'missing actual save binding sources')
    require('software binding alone cannot independently identify' in ten['read_only_method'] and 'world_draft_season is never' in ten['negative_control']['case'],'actual-save limit missing')
    eleven=rows[10]
    require('config/state_io_native/world.json#/slots' in eleven['root_refs'],'settings root missing')
    slots=resolve('config/state_io_native/world.json#/slots')
    require(set(slots)=={'SLOT_SETTINGS','SLOT_TRADE','SLOT_SLIDERS','SLOT_FRANCHISE'},'four world slots')
    require(len(eleven['setting_field_refs'])==2 and 'default=1' in eleven['negative_control']['case'] and 'v1_target=0' in eleven['negative_control']['case'],'defaults confused with observations')
    require('observed_value UNKNOWN unless evidenced' in eleven['expected_evidence'],'default-fill permitted')
    twelve=rows[11]
    require({a['action_id'] for a in twelve['action_refs']}=={'COACH.FIELD.POEDefense','WORLD.SETTING.world.trade_and_draft_rules.cpu_cpu_trades','TRADE.MENU.016'},'concrete action list missing')
    require(all(a['execution_allowed'] is False for a in twelve['action_refs']) and q['bounded_fix2']['all_207_actions_execution_prohibited'] is True,'action authority enlarged')
def scope(c,h,q):
    allowed={DEV+x for x in [CAT,HINT,QUEUE]}
    changed=set(git('diff','--name-only',BASE,'HEAD','-z').decode('utf-8').strip('\0').split('\0'))-{''}
    dirty=git('status','--porcelain','-z','--untracked-files=all').decode('utf-8')
    # managed_verify is run only after committing the candidate and closure evidence.
    require(not dirty,'verification source dirty')
    require(all(p in allowed or p.startswith(RUN) for p in changed),'scope escape '+str(changed-allowed))
    require(not git('diff',BASE,'HEAD','--',OLD),'original run/review changed')
    before=load(RUN+'preservation_baseline.json')
    attempt=before['original_attempt_manifest']
    parent=pathlib.Path(next(iter(attempt))).parent
    require({str(p):digest(p) for p in parent.iterdir() if p.is_file()}==attempt,'B-03 original attempt changed')
    for p,sha in before['main_untracked_sha256'].items():require(digest(pathlib.Path(p))==sha,'preexisting main file changed')
    for name,sha in before['review_report_sha256'].items():require(hashlib.sha256(git('show','HEAD:'+OLD+name)).hexdigest()==sha,'review report changed')
    # Business assets outside the three-file repair remain byte-for-byte Git-identical.
    for name in ['GAME_ACTION_DISCOVERY_SEED_V0.json','GAME_DOMAIN_SOURCE_MODEL_V0.md','GAME_FIELD_LIFECYCLE_RULES_V0.md','FLASH_DISCOVERY_FILL_CONTRACT_V0.md']:
        require(git('show','HEAD:'+DEV+name)==git('show',BASE+':'+DEV+name),'unrelated V0 asset changed')
    require(git('diff','--check',BASE,'HEAD')==b'','whitespace failure')
def adversarial(c,h,q):
    cases=[]
    def reject(label,fn,mutate):
        cc,hh,qq=copy.deepcopy((c,h,q));mutate(cc,hh,qq)
        try:fn(cc,hh,qq)
        except (AssertionError,KeyError,IndexError,ValueError):cases.append(label)
        else:raise AssertionError('negative regression accepted '+label)
    def field(c,fid):return next(x for x in c['fields'] if x['field_id']==fid)
    reject('pick-as-transaction',semantics,lambda c,h,q:field(c,'AG01D.UI.ROOKIE_REPORT.draft_pick_owner_team').update(entity='TransactionEvent'))
    reject('season-as-game',semantics,lambda c,h,q:field(c,'PROFILE.PLAYER_STATS.points').update(entity='Game'))
    reject('box-as-season',semantics,lambda c,h,q:field(c,'AG01D.UI.SINGLE_GAME_BOXSCORE.player_statline').update(entity='SeasonTotals'))
    reject('stint-invented',semantics,lambda c,h,q:field(c,'PROFILE.PLAYER_STATS.points')['semantic_binding']['identity_and_time'].update(stint_status='VERIFIED'))
    reject('missing-source-pointer',sources,lambda c,h,q:q['items'][10]['start_points'][0].update(ref='config/state_io_native/world.json#/slots/NO_SLOT'))
    reject('selected-tendency-offset',conflict,lambda c,h,q:h['historical_layout_conflicts'][0].update(selected_candidate='0x458..0x4BA'))
    reject('wrong-tendency-neighborhood',conflict,lambda c,h,q:field(c,'AG01D.UI.PLAYER_CARD.player_tendencies').update(discovery_group_ref='NH_CAREER'))
    reject('bad-human-digest-location',human,lambda c,h,q:c['source_reference_registry']['HUMAN_DECISION_20261022'].update(line_start=1))
    reject('generic-R00-method',queue,lambda c,h,q:q['items'][10].update(read_only_method=q['items'][0]['read_only_method']))
    reject('world-identity-from-draft-season',queue,lambda c,h,q:q['items'][9].update(field_refs=['GAME_UI_FIELD_CATALOG_V0.json#/fields/473']))
    reject('default-as-observed',queue,lambda c,h,q:q['items'][10].update(expected_evidence='observed_value equals default'))
    reject('unbounded-R00',queue,lambda c,h,q:q['items'][5]['max_investigation'].update(max_sample_records=1232))
    reject('action-enabled',queue,lambda c,h,q:q['items'][11]['action_refs'][0].update(execution_allowed=True))
    reject('wrong-action-source',sources,lambda c,h,q:q['items'][11]['action_refs'][0].update(action_id='TRADE.MENU.016'))
    reject('age-formula-rewritten',invariants,lambda c,h,q:c['semantics'].update(age_formula_candidate='current_year - birth_year'))
    reject('native-maturity-promoted',invariants,lambda c,h,q:c['fields'][0].update(current_save_live_verified=True))
    print('Negative semantic/source/queue mutations rejected:',len(cases))
CHECKS={'invariants':invariants,'semantics':semantics,'sources':sources,'conflict':conflict,'human':human,'queue':queue,'scope':scope,'adversarial':adversarial}
if __name__=='__main__':
    try:
        c,h,q=data();CHECKS[sys.argv[1]](c,h,q)
        print('PASS',sys.argv[1],'OFFLINE_ONLY; no live game/production/independent acceptance claim')
    except Exception as e:
        print('FAIL',sys.argv[1],type(e).__name__,str(e));raise SystemExit(1)
