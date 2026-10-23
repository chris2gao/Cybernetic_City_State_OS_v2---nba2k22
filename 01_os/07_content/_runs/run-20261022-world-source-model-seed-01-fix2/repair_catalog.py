"""Deterministic bounded repair from fixed review input; offline JSON only."""
import copy, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[4]
DOM='08_Domain_Applications/Antigravity_GM_Engine/'
DEV=DOM+'docs/development/'
RUN='01_os/07_content/_runs/run-20261022-world-source-model-seed-01-fix2/'
OLD='01_os/07_content/_runs/run-20261022-world-source-model-seed-01/'
BASE='8cdbfaefbcb001c6ca0612017957c6414876eea4'
SEED='142531f2d60813bce5b90254c5e347050c40b406'
def original(p): return json.loads(subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT))
def write(p,v): (ROOT/p).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

def main():
    c=original(DEV+'GAME_UI_FIELD_CATALOG_V0.json')
    h=original(DEV+'GAME_NATIVE_OBJECT_HINTS_V0.json')
    changed=[]
    # These are source-specific semantic rules, never UI-page-to-entity defaults.
    rookie={'draft_pick_original_team':('DraftPick','DRAFT_PICK_ASSET'),
            'draft_pick_owner_team':('PickOwnership','PICK_OWNERSHIP_OBSERVATION'),
            'draft_pick_round':('DraftPick','DRAFT_PICK_ASSET'),
            'draft_pick_year':('DraftPick','DRAFT_PICK_ASSET'),
            'draft_prospect_pool':('NativeObject','UNRESOLVED_PROSPECT_POOL'),
            'is_rookie':('PlayerIncarnation','PLAYER_STATE_OBSERVATION')}
    draft={'assigned_player_ptr':('DraftPick','DRAFT_PICK_ASSET'),
           'current_owner_ptr':('PickOwnership','PICK_OWNERSHIP_OBSERVATION'),
           'metadata':('DraftPick','DRAFT_PICK_ASSET'),
           'original_owner_ptr':('DraftPick','DRAFT_PICK_ASSET')}
    boxes={'player_advanced_analytics':('PlayerGameStatline','DERIVED_PLAYER_GAME_PROJECTION'),
           'player_points_conservation':('PlayerGameStatline','PLAYER_GAME_CONSERVATION_CHECK'),
           'player_statline':('PlayerGameStatline','PLAYER_GAME_STATLINE'),
           'team_advanced_stats':('TeamGameResult','TEAM_GAME_OBSERVATION'),
           'final_score':('TeamGameResult','TEAM_GAME_OBSERVATION'),
           'linescore_quarters':('TeamGameResult','TEAM_GAME_OBSERVATION'),
           'linescore_overtime':('TeamGameResult','TEAM_GAME_OBSERVATION')}
    for f in c['fields']:
        fid=f['field_id']; leaf=fid.rsplit('.',1)[-1]; choice=None; raw=None
        if fid.startswith('AG01D.UI.ROOKIE_REPORT.'):
            choice=rookie[leaf]
            raw=f['native_object_hint']
        elif fid.startswith('DRAFT_ASSET.'):
            choice=draft[leaf];raw='DRAFT_ASSET (R05D historical pointer-layout candidate; not equated to AG01D Slot36)'
        elif fid.startswith('AG01D.UI.SEASON_STATS_AND_LEADERBOARDS.'):
            choice=('SeasonTotals','DERIVED_SEASON_SPLIT_PROJECTION' if leaf=='splits_additive_equations' else 'PLAYER_SEASON_ACCUMULATOR')
            raw=f['native_object_hint']
        elif fid.startswith('PROFILE.PLAYER_STATS.'):
            choice=('SeasonTotals','PLAYER_SEASON_RECORD_OBSERVATION');raw='PLAYER_STATS / ROSTERDATA Slot24 historical record'
        elif fid.startswith('AG01D.UI.SINGLE_GAME_BOXSCORE.') and leaf in boxes:
            choice=boxes[leaf];raw=f['native_object_hint']
        elif fid=='PLAYER.current_team_ptr':
            choice=('RosterMembership','ROSTER_MEMBERSHIP_OBSERVATION');raw='PLAYER (R05D pointer candidate)'
        elif fid=='PLAYER.contract_team_ptr':
            choice=('Contract','CONTRACT_TEAM_OBSERVATION');raw='PLAYER (R05D pointer candidate)'
        elif fid.startswith('OPS.TRADE_MENU.'):
            choice=('StateObservation','TRADE_MENU_OPTION_RESEARCH');raw='R05B native_trade_menu_research_options; PC22 object UNKNOWN'
        if not choice: continue
        entity,grain=choice
        binding={'raw_source_ref':f['source_refs'][0], 'raw_source_object':raw,
                 'target_semantic_entity':entity,'record_grain':grain,
                 'previous_entity':f['entity'],
                 'identity_and_time':{'scope':['independent_game_save','technical_binding','capture_batch'],
                    'game_effective_time':'UNKNOWN','observed_at':'UNKNOWN','resolved_identity_values':'UNKNOWN'},
                 'relations':[], 'mapping_status':'SEMANTIC_CLASSIFICATION_ONLY_NOT_NATIVE_IDENTITY_VERIFIED',
                 'event_inference':'No TransactionEvent is inferred from ownership, menu, pointer or aggregate observations.'}
        if entity in ('DraftPick','PickOwnership'):
            roles=['draft_pick_uid','draft_season','round','original_franchise_uid']
            binding['identity_and_time']['candidate_key_roles']=roles
            binding['relations']=[{'role':r,'target':t,'status':'UNKNOWN'} for r,t in [
                ('asset','DraftPick'),('original_team','Franchise'),('owner_at_observation','Franchise'),('assigned_player_if_any','PlayerIncarnation')]]
            binding['ownership_change_event']='UNKNOWN: two owner observations alone do not prove a dated trade event.'
        elif entity=='SeasonTotals':
            binding['identity_and_time']['candidate_key_roles']=['player_uid','season_uid','competition_scope','native_record_index','optional_team_stint_uid']
            binding['identity_and_time']['stint_status']='UNKNOWN: last_team/previous_team are candidate metadata, not verified stint keys.'
            binding['relations']=[{'role':r,'target':t,'status':'UNKNOWN'} for r,t in [
                ('subject','PlayerIncarnation'),('season','Season'),('team_stint_if_available','TeamSeason')]]
            binding['not_game_event']=True
            binding['embedded_record_fields']='Awards/packed team metadata retain their raw slot; no independent award event or record partition is inferred.'
            if leaf=='splits_additive_equations':
                binding['projection_inputs']=['PlayerGameStatline','Game']
                binding['projection_condition']='L2 only when observed game coverage, game/player/team identities and split membership are proven; missing games stay NOT_OBSERVED.'
        elif entity in ('PlayerGameStatline','TeamGameResult'):
            binding['identity_and_time']['candidate_key_roles']=['game_uid','season_uid','team_uid']+(['player_uid','native_stat_index'] if entity=='PlayerGameStatline' else ['home_away_side'])
            binding['relations']=[{'role':r,'target':t,'status':'UNKNOWN'} for r,t in [
                ('game','Game'),('season','Season'),('team','TeamSeason')]+([('player','PlayerIncarnation')] if entity=='PlayerGameStatline' else [])]
            binding['not_season_accumulator']=True
        else:
            binding['identity_and_time']['candidate_key_roles']=['player_uid','team_uid'] if entity in ('PlayerIncarnation','RosterMembership','Contract') else ['native_object_or_menu_id']
            binding['relations']=[{'role':'subject_identity','target':'PlayerIncarnation' if entity in ('PlayerIncarnation','RosterMembership','Contract') else 'NativeObject','status':'UNKNOWN'}]
        f['entity']=entity;f['semantic_binding']=binding
        changed.append({'field_id':fid,'previous_entity':binding['previous_entity'],'target_entity':entity,'source_ref':binding['raw_source_ref']})

    conflict_id='PLAYER_TENDENCIES_OFFSET_BUILD_CONFLICT'
    a_ref='research/native_access/AG_NATIVE_01D/ui_native_source_matrix.json#/screens/PLAYER_CARD/fields/player_tendencies'
    r_ref='docs/game_mechanics/catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json#/native_slots'
    p_ref='config/state_io_native/player.json#/TENDENCY_OFFSETS'
    conflict={'id':conflict_id,'object':'PLAYER','status':'UNRESOLVED_HISTORICAL_LAYOUT_CONFLICT',
       'candidates':[{'offset_range':'0x170..0x260','source_refs':[a_ref],'build_status':'UNKNOWN','object_base_equivalence':'UNKNOWN','current_save_verified':False},
                     {'offset_range':'0x458..0x4BA','source_refs':[r_ref,p_ref],'build_status':'UNKNOWN','object_base_equivalence':'UNKNOWN','current_save_verified':False}],
       'selected_candidate':None,'canonical_equivalence_proven':False,
       'investigation_entry':'FLASH_R00_PRIORITY_QUEUE_V0.json#/items/3',
       'stop_condition':'HOLD_UNKNOWN until build/layout version and PLAYER object base are evidenced; never select a range by name or read either live range in this repair.'}
    h['historical_layout_conflicts']=[conflict]
    h['roots'][11]['conflict_ref']='GAME_NATIVE_OBJECT_HINTS_V0.json#/historical_layout_conflicts/0'
    h['roots'][11]['locator_authority']='HISTORICAL_CANDIDATE_ONLY_NOT_SELECTED'
    h['field_adjacency_groups'][1]['conflict_ref']=h['roots'][11]['conflict_ref']
    for f in c['fields']:
        if f['field_id']=='AG01D.UI.PLAYER_CARD.player_tendencies' or f['field_id'].startswith('PLAYER.TENDENCY.BYTE_'):
            f['offset_conflict_ref']=h['roots'][11]['conflict_ref']
            f['discovery_group_ref']='NH_TENDENCIES'
            f['next_probe']='READ_ONLY_GROUP:NH_TENDENCIES; resolve PLAYER_TENDENCIES_OFFSET_BUILD_CONFLICT via R00-04; HOLD_UNKNOWN without build and object-base evidence.'
            if f['field_id']=='AG01D.UI.PLAYER_CARD.player_tendencies':
                f['superseded_discovery_hint']={'group':'NH_CAREER','reason':'career-index neighborhood is not evidence for tendencies; retained as historical attribution error'}
                f['adjacent_fields_or_regions']=[{'scope':'RESEARCH_GROUP_NOT_EXACT_NEIGHBOR','region':'0x170..0x260 versus 0x458..0x4BA; unresolved',
                    'evidence_ref':a_ref,'alternative_evidence_ref':r_ref,'negative_control':'different or unbound build/object base must HOLD_UNKNOWN'}]
    # Resolve, but do not replace or reinterpret, all six original symbolic refs.
    human_path=OLD+'human_task.md'
    human_bytes=subprocess.check_output(['git','show',SEED+':'+human_path],cwd=ROOT)
    c['source_reference_registry']={'HUMAN_DECISION_20261022':{
        'repository':'chris2gao/Cybernetic_City_State_OS_v2---nba2k22','commit_sha':SEED,
        'path':human_path,'line_start':3,'line_end':3,'sha256':hashlib.sha256(human_bytes).hexdigest(),
        'record_kind':'ORIGINAL_DURABLE_HUMAN_TASK_DIGEST','authority_scope':'Human project rule; not engine behavior or runtime approval',
        'referencing_field_ids':[f['field_id'] for f in c['fields'] if 'HUMAN_DECISION_20261022' in f['source_refs']]}}
    c['bounded_fix2']={'review_sha':BASE,'findings':['B-02','B-04','B-05'],
         'semantic_rule':'Classify target entity from raw object and record grain; UI domain remains navigation, not entity authority.',
         'semantic_changes_ref':RUN+'semantic_change_manifest.json','native_certification_changed':False}
    write(DEV+'GAME_UI_FIELD_CATALOG_V0.json',c)
    write(DEV+'GAME_NATIVE_OBJECT_HINTS_V0.json',h)
    write(RUN+'semantic_change_manifest.json',{'review_sha':BASE,'changes':changed,'total':len(changed),
         'unresolved_relations':'UNKNOWN; no new identity, game, ownership-change or transaction facts asserted'})
    print('Applied source-specific semantic corrections:',len(changed),'; registered unresolved tendency conflict and six Human reference mappings.')
if __name__=='__main__':main()
