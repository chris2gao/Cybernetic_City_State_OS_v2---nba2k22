"""Target-specific R00 planning contracts; creates no reader or runtime task."""
import json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[4]
DEV='08_Domain_Applications/Antigravity_GM_Engine/docs/development/'
BASE='8cdbfaefbcb001c6ca0612017957c6414876eea4'
def load(p): return json.loads((ROOT/p).read_bytes())
def main():
    q=json.loads(subprocess.check_output(['git','show',BASE+':'+DEV+'FLASH_R00_PRIORITY_QUEUE_V0.json'],cwd=ROOT))
    c=load(DEV+'GAME_UI_FIELD_CATALOG_V0.json')
    fields={f['field_id']:f'GAME_UI_FIELD_CATALOG_V0.json#/fields/{i}' for i,f in enumerate(c['fields'])}
    ag='research/native_access/AG_NATIVE_01D/'
    matrix=ag+'ui_native_source_matrix.json#/screens/'
    # One explicit object group and falsifiable outcome per row, bounded before dispatch.
    specs=[
      dict(start=[{'ref':'research/native_access/AG_NATIVE_01C/object_catalog.json#/descriptors/1','role':'historic PLAYER descriptor; compare descriptor origin hypotheses'},
                  {'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/roots/0','role':'historic manager RVA, not a current pointer'}],
           scope='One ROSTERDATA manager; Slot1 and Slot24 only. Compare descriptor origin +0 versus +8; do not enumerate all 75 slots.',
           method='Inspect historical descriptor bounds and pointer/count/stride evidence; on separately authorized existing samples, check two descriptors against object lengths. Never dereference an unbound manager.',
           positive='Slot1 and Slot24 descriptors have coherent pointer/count/stride within their source buffer and the same bound manager.',
           negative='Null pointer, zero count with nonempty claim, invalid buffer end, or shifted +8 interpretation must be rejected rather than decoded.',
           evidence='descriptor_origin_comparison: two hypotheses, source bounds, sample lengths and accepted/rejected/UNKNOWN result; no all-slot certification.',
           stop='HOLD_UNKNOWN if manager/build/save or descriptor origin cannot be supported; do not search adjacent memory.',records=2,regions=['ROSTERDATA descriptor[1]','ROSTERDATA descriptor[24]'],fids=[]),
      dict(start=[{'ref':matrix+'PLAYER_CARD/fields','role':'PLAYER identity and historical bytes'},
                  {'ref':'GAME_UI_FIELD_CATALOG_V0.json#/source_reference_registry/HUMAN_DECISION_20261022','role':'exact Human age-input and independent-save rule'}],
           scope='Two player instances in one independently bound save; birth_year, original_draft_year, years_pro and separate UI display age only.',
           method='Associate each historical PLAYER sample with player identity and three separately sourced age inputs. Calculate the Human candidate only if all inputs exist; retain the observed UI value separately.',
           positive='A source-complete player yields a candidate age with three provenance refs and a distinct display_age_observed value, even if they differ.',
           negative='Missing birth/draft year or an input from another save leaves age UNKNOWN; world_draft_season must not substitute original_draft_year.',
           evidence='player_age_input_matrix: identity scope, input provenance, candidate calculation, UI observation and unresolved cases; no engine formula claim.',
           stop='HOLD_UNKNOWN on missing input, cross-save identity or build uncertainty; an independent age slot is not required.',records=2,regions=['PLAYER identity + age input candidates'],fids=['PLAYER.birth_year','PLAYER.original_draft_year','PLAYER.years_pro','PLAYER.age_derived','PLAYER.display_age_observed']),
      dict(start=[{'ref':'config/memory_field_profile.json#/fields/PLAYER','role':'registered rating offsets and widths'},
                  {'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/field_adjacency_groups/0','role':'historical attribute range'}],
           scope='Two already-bound players and two approved visible ratings only; do not dump all 55 ratings or the contiguous range containing Potential.',
           method='Select two non-sensitive registered fields; compare widths and source/UI values independently. Record masked omissions without copying Potential or neighboring raw bytes.',
           positive='The same approved rating in two players has separately identified bytes and UI values within the source layout bounds.',
           negative='Potential at 0x441, an unclassified field, missing UI evidence or unbound player is withheld and cannot pass the visible-rating comparison.',
           evidence='rating_pair_atlas: field refs, bounded source slices without sensitive bytes, UI comparison, omissions and unknown encoding.',
           stop='Stop before any sensitive export, implicit contiguous read or unknown codec; record WITHHELD or UNKNOWN.',records=2,regions=['two explicit non-sensitive profile fields; exclude 0x441'],fids=['PLAYER.attributes.intangibles']),
      dict(start=[{'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/historical_layout_conflicts/0','role':'both contradictory PLAYER tendency locations'},
                  {'ref':'config/state_io_native/player.json#/TENDENCY_OFFSETS','role':'48 named static offsets; no live certification'}],
           scope='Two historical layout candidates and at most two existing player samples; resolve build and object-base compatibility before considering bytes. No range is selected by this task.',
           method='Compare AG01D 0x170..0x260 with R04/Profile 0x458..0x4BA using versioned source identity. Only a future authorized, calibrated sample may test named bytes; never ordinal-match external 99 labels.',
           positive='A candidate with proven build/object-base and two matching player/UI controls may be proposed as a version-specific hypothesis, never globally canonical.',
           negative='Unknown or different build/base, an unnamed byte, or an ordinal external-label match must remain UNKNOWN; neither historical claim wins by status text.',
           evidence='tendency_conflict_matrix: both ranges, source commits, build/base evidence, rejected hypotheses and unresolved byte labels; selected address remains null without proof.',
           stop='HOLD_UNKNOWN before either live range if build/base evidence is missing; two failed distinct paths trigger Codex escalation.',records=2,regions=['candidate 0x170..0x260','candidate 0x458..0x4BA'],fids=['AG01D.UI.PLAYER_CARD.player_tendencies','PLAYER.TENDENCY.BYTE_0x458']),
      dict(start=[{'ref':matrix+'PLAYER_CARD/fields/player_badges','role':'historical badge encoding claim'},
                  {'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/roots/12','role':'candidate region, not an approved read'}],
           scope='One badge across two existing player samples with contrasting displayed states; only the declared candidate region, no badge writes or region expansion.',
           method='Compare the source encoding claim to displayed states and separate enable/unlock-bit evidence. Test whether two bits can support five mutually exclusive levels; do not invent a fifth code.',
           positive='A reproducible state/bit explanation binds both sample identities and UI states; a composite encoding needs separate evidence for each component.',
           negative='Five labels mapped directly to two bits, missing unlock evidence, or absent UI sample falsifies the simple encoding hypothesis.',
           evidence='badge_encoding_hypotheses: raw limited sample provenance, UI labels, rejected 2-bit-only model and UNKNOWN components.',
           stop='HOLD_UNKNOWN on encoding contradiction or missing UI; do not grant badges, infer IDs or widen the candidate region.',records=2,regions=['PLAYER+0x36C..0x3C0 historical candidate'],fids=[]),
      dict(start=[{'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/roots/6','role':'SEASON schedule candidate'},
                  {'ref':matrix+'SEASON_STATS_AND_LEADERBOARDS/fields','role':'separate accumulator grain, not per-game records'}],
           scope='One bound season; at most one known played and one scheduled/unplayed existing record. Actual valid count is distinct from historical capacity 1232.',
           method='Validate source-record length, schedule status/date and game/team association within SEASON+0x28 candidate. Keep Slot24 SeasonTotals as a separate observation, not a synthetic schedule.',
           positive='An existing played record has traceable season/game/teams and explicit status; the accumulator remains keyed to player/season, not game.',
           negative='An unplayed record must not produce final score/player Box facts; out-of-count capacity slots and Slot44 matchup rows are not schedule games.',
           evidence='season_record_grain_matrix: played and unplayed status, valid-bound vs capacity, game scope and separately sourced SeasonTotals.',
           stop='HOLD_UNKNOWN if valid count, status, season or game identity is unresolved; no full-season enumeration.',records=2,regions=['SEASON+0x28: two 60-byte records maximum'],fids=['AG01D.UI.SEASON_STATS_AND_LEADERBOARDS.season_points']),
      dict(start=[{'ref':'GAME_NATIVE_OBJECT_HINTS_V0.json#/roots/3','role':'48-byte PLAYER_STATS candidate'},
                  {'ref':matrix+'PLAYER_CARD/fields/career_history_stats_array','role':'current/career link; fixed decoder loop is not lifetime limit'}],
           scope='One player with existing current/career record and one no-stat/sentinel case; at most two Slot24 records and the declared index chain.',
           method='Follow documented PLAYER current and career index candidates in existing samples, preserving season, native index and optional team metadata. Do not join on name or index alone.',
           positive='An index within source bounds links a player and season to a 48-byte accumulator with provenance; team/stint linkage is separately UNKNOWN until proven.',
           negative='Sentinel/out-of-bounds index, no-stat player or same index in another save must not create a row or cross-save career continuity.',
           evidence='player_stats_link_matrix: player/season/index/binding provenance, optional stint UNKNOWN, sentinel result and historical-loop limit disclosure.',
           stop='HOLD_UNKNOWN on index scope, record boundary or player ambiguity; never turn 20 visited indices into a game lifetime cap.',records=2,regions=['PLAYER+0xFC and +0xFE..0x126','Slot24: two 48-byte records maximum'],fids=['PROFILE.PLAYER_STATS.points','PROFILE.PLAYER_STATS.season']),
      dict(start=[{'ref':matrix+'SINGLE_GAME_BOXSCORE/fields/player_statline','role':'24-byte StatBank player-game candidate'},
                  {'ref':ag+'DISCOVERY.md','role':'Slot44 correction and valid StatBank caveats'}],
           scope='One existing played game, at most two associated player rows and one unplayed header control; no league-wide bank scan.',
           method='Bind schedule game and teams before using stat_idx into the bounded StatBank source. Reconcile only the sampled game/player facts; capacity 45292 is not valid use count.',
           positive='Two source-bounded rows share the proven game/season/team context and independently identified players; player statline is distinct from SeasonTotals.',
           negative='Unplayed header, wrong bank, out-of-range stat_idx, cross-save GameID collision or Slot44 matchup row must not yield a valid player-game statline.',
           evidence='statbank_game_link: sample bounds, game/player/team keys, conservation checks only where applicable, invalid-index and unplayed outcomes.',
           stop='HOLD_UNKNOWN at unknown bank extent, GameID scope or identity; do not claim all 238 games accepted.',records=3,regions=['SEASON+0x1B6AC: two 24-byte rows maximum','one unplayed schedule header'],fids=['AG01D.UI.SINGLE_GAME_BOXSCORE.player_statline']),
      dict(start=[{'ref':'GAME_UI_FIELD_CATALOG_V0.json#/pages','role':'research page kinds and all current UI flags false'},
                  {'ref':matrix+'PLAYER_CARD','role':'historical page candidate, not observation'}],
           scope='One player card and at most two already-visible PC22 tabs or previously authorized screenshots; do not navigate, switch saves or open new game pages under this queue.',
           method='Record actually visible labels/units and distinguish historical AG screen names, virtual research groups and third-party exports from target PC22 pages.',
           positive='A page already visible in authorized evidence gets a source timestamp, game/player scope and observed label list.',
           negative='A virtual research group, third-party HTML tab or an unseen page stays NOT_OBSERVED; no-stats is not proof a page does not exist.',
           evidence='ui_page_manifest: observed and NOT_OBSERVED targets, screenshot/source refs, page-kind distinctions and field links.',
           stop='Stop if UI evidence is unavailable or navigation would be needed; do not manufacture PC22 tabs from source headings.',records=2,regions=['two existing UI tabs/screenshots maximum'],fids=['PLAYER.display_age_observed']),
      dict(start=[{'ref':'src/save_context.py','role':'save_paths: technical save directories, not physical game-save proof'},
                  {'ref':'src/gm_state_io/workspace.py','role':'binding checks, activation and reset manifest semantics'},
                  {'ref':'docs/DEV14_STATE_IO_RUNBOOK.md','role':'actual loaded-save confirmation limitation and reset behavior'},
                  {'ref':'GAME_DOMAIN_SOURCE_MODEL_V0.md','role':'one independent continuous world per actual save; no dynamic inheritance'}],
           scope='Offline comparison of at most three already-existing authorized evidence records: same-save consecutive captures and one different-save or reset binding; do not read/load real saves or create manifests.',
           method='Inspect source contracts and supplied receipt copies for save_id/save_instance_id/generation_id, active/workspace agreement, batch/source time and explicit loaded-save confirmation. Record that software binding alone cannot independently identify the actual loaded game save.',
           positive='Two preexisting observations explicitly confirmed for the same actual save with coherent binding/time can support bounded continuity; technical generation change needs explicit same-save proof.',
           negative='Different actual save, reset into a new world, same names/season/player IDs or absent loaded-save attestation cannot inherit continuity. world_draft_season is never a save/world identity.',
           evidence='save_continuity_matrix: receipt refs, technical tuples, actual-save attestation limits, same/different/reset cases, HOLD_UNKNOWN when samples or continuity proof are absent.',
           stop='HOLD_UNKNOWN if actual save identity/continuity cannot be evidenced; no switching/loading, reset, new world branches or dynamic cross-save history inheritance.',records=3,regions=['offline receipt/workspace copies only; no actual save files'],fids=[]),
      dict(start=[{'ref':'config/state_io_native/world.json#/slots','role':'SLOT_SETTINGS / SLOT_TRADE / SLOT_SLIDERS / SLOT_FRANCHISE historical RVAs'},
                  {'ref':'config/state_io_native/world.json#/fields/gameplay_and_calendar/quarter_length','role':'default and v1_target are configured values, not observations'},
                  {'ref':'config/state_io_native/world.json#/fields/trade_and_draft_rules/cpu_cpu_trades','role':'explicit non-equal default/target contrast'},
                  {'ref':'config/state_io_native/settings.json#/slots','role':'related global-settings source'},
                  {'ref':'config/source_catalog.json#/deterministic_state_io','role':'same-batch observed source and pipeline limits'}],
           scope='Four static slot descriptors; two selected setting definitions and at most two supplied actual observations. No settings/slider dump or parameter change.',
           method='Trace quarter_length and cpu_cpu_trades from slot/type/offset through source_registry to same-bound observed evidence if supplied; keep default, v1_target and observed value in distinct columns.',
           positive='Only a separately timestamped, bound game/UI observation can fill observed_value; the four slot RVAs remain historical candidates until calibrated.',
           negative='cpu_cpu_trades default=1 and v1_target=0 cannot be relabeled as the current game value. Missing root or observation must yield UNKNOWN, never default-fill.',
           evidence='world_settings_source_matrix: four slot refs, two field refs, configured defaults/targets, observed_value UNKNOWN unless evidenced, build/binding/time/side and effect limits.',
           stop='HOLD_UNKNOWN if root, type, build or observed source is missing; stop before any setter, slider change or simulated date advancement.',records=2,regions=['four static slot definitions','two explicit setting fields only'],fids=[]),
      dict(start=[{'ref':'GAME_ACTION_DISCOVERY_SEED_V0.json#/entries/0','role':'COACH.FIELD.POEDefense'},
                  {'ref':'GAME_ACTION_DISCOVERY_SEED_V0.json#/entries/154','role':'WORLD.SETTING.world.trade_and_draft_rules.cpu_cpu_trades'},
                  {'ref':'GAME_ACTION_DISCOVERY_SEED_V0.json#/entries/206','role':'TRADE.MENU.016'}],
           scope='Exactly three named action entries and their raw read-source definitions. No action invocation, Getter call, setter, executor import, transaction, signing or game access.',
           method='Passively resolve each action_id, original source pointer and known-read-source relation from repository text. Describe identity dependencies and possible side effects without evaluating or enabling the action.',
           positive='Each named entry resolves to original coach/world/trade-menu source, with all write/readback/persistence/production flags false and known side effects retained.',
           negative='A default/target, discovered offset, menu name, old executor evidence or approval of this repair cannot authorize execution; unresolved read source remains UNKNOWN.',
           evidence='action_source_matrix: three action IDs, exact source/known-read refs, identity/time dependencies, side effects, unresolved UI associations and prohibition evidence for all 207 entries.',
           stop='Stop before importing executor or invoking any action; HOLD_UNKNOWN for ambiguous source/UI links; discovery never yields execution approval.',records=3,regions=['entries/0','entries/154','entries/206'],fids=[])
    ]
    for i,(row,s) in enumerate(zip(q['items'],specs)):
        row['start_points']=s['start'];row['object_scope']=s['scope'];row['read_only_method']=s['method']
        row['positive_control']={'case':s['positive'],'expected_result':'EVIDENCED_WITH_BOUND_SCOPE_OR_UNKNOWN'}
        row['negative_control']={'case':s['negative'],'expected_result':'REJECT_ASSOCIATION_OR_HOLD_UNKNOWN; no fabricated fact'}
        row['expected_evidence']=s['evidence'];row['stop_condition']=s['stop']
        row['max_investigation']={'max_minutes':20,'max_distinct_failed_paths':2,'max_sample_records':s['records'],'allowed_regions_or_records':s['regions'],'expansion_allowed':False}
        row['failure_escalation']={'contract_ref':'FLASH_DISCOVERY_FILL_CONTRACT_V0.md','after_distinct_failed_paths':2,'recipient_role':'Codex','result':'Freeze failed hypotheses, return UNKNOWN and evidence; no third unbounded investigation.'}
        row['unknown_result']={'status':'HOLD_UNKNOWN','required':['reason','missing_evidence','failed_hypotheses','source_refs','next_bounded_question'],'blocks_claim_not_documentation':True}
        row['evidence_contract']={'required':['build_or_UNKNOWN','save_binding_or_UNKNOWN','capture_batch_or_UNKNOWN','observed_at_or_UNKNOWN','source_commit_and_pointer','hypothesis_vs_observation','positive_case_result','negative_case_result','failed_paths','unresolved_relations'],
                                  'acceptance_basis':'Traceable answer or bounded UNKNOWN with tested counterexample; never UNKNOWN-count reduction.'}
        row['source_refs']=list(dict.fromkeys(row['source_refs']+[x['ref'] for x in s['start']]))
        row['field_refs']=[fields[x] for x in s['fids']]
        row['access_gate']='NOT_DISPATCHED. Any later live/UI sample collection needs a separate Human scope plus freshly calibrated build/save. No runtime authorized by this file.'
    # An explicit action-to-source relation avoids asking Flash to infer a generic domain.
    actions=load(DEV+'GAME_ACTION_DISCOVERY_SEED_V0.json')['entries']
    raw_refs={0:'config/coach_tactics_profile.json#/fields/POEDefense',154:'config/state_io_native/world.json#/fields/trade_and_draft_rules/cpu_cpu_trades',206:'docs/game_mechanics/catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json#/native_trade_menu_research_options/15'}
    q['items'][11]['action_refs']=[{'action_id':actions[i]['action_id'],'entry_ref':f'GAME_ACTION_DISCOVERY_SEED_V0.json#/entries/{i}',
       'original_source_ref':actions[i]['source_ref'],'known_read_source_raw':actions[i]['known_read_source'],
       'resolved_read_source_ref':raw_refs[i],'relation_status':'STATIC_SOURCE_RELATION_NOT_RUNTIME_CERTIFICATION','execution_allowed':False} for i in raw_refs]
    q['items'][10]['root_refs']=[x['ref'] for x in specs[10]['start'][:1]]
    q['items'][10]['setting_field_refs']=[x['ref'] for x in specs[10]['start'][1:3]]
    q['items'][9]['root_refs']=[x['ref'] for x in specs[9]['start'][:2]]
    q['items'][11]['root_refs']=[]
    q['bounded_fix2']={'review_sha':BASE,'finding':'B-01','row_count':12,'status':'TARGETED_PLANNING_CANDIDATE_PENDING_INDEPENDENT_RECHECK',
       'live_access_authorized':False,'Flash_started':False,'all_207_actions_execution_prohibited':True}
    (ROOT/DEV/'FLASH_R00_PRIORITY_QUEUE_V0.json').write_bytes((json.dumps(q,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print('Revised 12 distinct bounded R00 contracts; Flash remains NOT_DISPATCHED; all actions prohibited.')
if __name__=='__main__':main()
