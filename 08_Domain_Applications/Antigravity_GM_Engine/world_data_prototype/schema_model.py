"""Executable, typed catalog. Native ranges stay UNKNOWN until evidenced.

The SQL and complete field cards are generated from this module; persisted facts
are relational columns, never an EAV/JSON substitute for the domain model.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
DOMAIN = BASE.parent
VERSION = 3
PROFILE_REF = 'config/memory_field_profile.json'
PROFILE = json.loads((DOMAIN / PROFILE_REF).read_text(encoding='utf-8'))
PLAYER_CONFIG = json.loads((DOMAIN / 'config/state_io_native/player.json').read_text(encoding='utf-8'))


def ident(name):
    if not re.fullmatch(r'[a-z][a-z0-9_]*', name):
        raise ValueError('invalid SQL identifier: ' + name)
    return '"' + name + '"'


@dataclass
class Column:
    name: str
    kind: str = 'TEXT'
    meaning: str = ''
    required: bool = False
    ref: str | None = None
    source: str = 'UNKNOWN: native mapping or UI semantics not yet evidenced'
    unit: str = 'UNKNOWN/native representation'
    check: str | None = None
    default: str | None = None
    visibility: str = 'GM_PUBLIC'

    def sql(self):
        parts = [ident(self.name), self.kind]
        if self.required: parts.append('NOT NULL')
        if self.ref: parts.append('REFERENCES ' + self.ref + ' ON DELETE RESTRICT')
        if self.default is not None: parts.append('DEFAULT ' + self.default)
        if self.check: parts.append('CHECK (' + self.check + ')')
        return ' '.join(parts)


@dataclass
class Table:
    name: str
    key: str
    domain: str
    grain: str
    columns: list[Column]
    unique: list[tuple[str, ...]] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    source: str = 'UNKNOWN'
    observation: bool = True
    public: bool = True


TABLES: dict[str, Table] = {}


def col(name, kind='TEXT', **kw):
    return Column(name, kind, **kw)


def ref(name, table, key=None, required=True):
    return col(name, required=required, ref=f'{table}({key or name})',
               source='ENGINEERING_IDENTITY_CONTRACT', unit='save-local identifier',
               meaning='Reference to the evidenced ' + table + ' record')


def fields(names, kind='INTEGER', source='UNKNOWN', unit='native raw value'):
    return [col(n, kind, meaning=n.replace('_', ' '), source=source, unit=unit) for n in names.split()]


def table(name, key, domain, grain, columns, *, unique=(), checks=(), source='UNKNOWN', observation=True, public=True):
    TABLES[name] = Table(name, key, domain, grain, [col(key, required=True,
        source='ENGINEERING_IDENTITY_CONTRACT', unit='save-local immutable row identifier', meaning=grain + ' identity')] + columns,
        list(unique), list(checks), source, observation, public)


U = lambda: ref('unit_id', 'capture_units')
P = lambda: ref('player_id', 'players')
T = lambda required=True: ref('team_id', 'teams', required=required)
S = lambda: ref('season_id', 'seasons')
F = lambda: ref('staff_id', 'staff_members')
G = lambda: ref('game_id', 'games')
SAVE = lambda: ref('save_id', 'saves')
STATS = 'points fg_made fg_attempted three_made three_attempted ft_made ft_attempted offensive_rebounds defensive_rebounds assists steals blocks turnovers fouls minutes_raw plus_minus possessions_raw'
STATS_SOURCE = 'AG_NATIVE_01D/decoders: research layout; fixture replay only, not current live acceptance'

table('saves', 'singleton', 'RES-D', 'one independent game save per SQLite file', [
    col('save_id', required=True, source='HUMAN_OR_EVIDENCED_SAVE_BINDING', unit='opaque save identity'),
    col('schema_version', 'INTEGER', required=True, check='schema_version=3', source='ENGINEERING_SCHEMA_VERSION'),
    col('created_at', required=True, source='SYSTEM_UTC_CLOCK', unit='ISO8601 UTC'),
    col('source_grade', required=True, default="'SYNTHETIC_ONLY'", source='EVIDENCE_CLASSIFICATION'),
    col('game_build'), col('native_save_fingerprint', visibility='OWNER_ONLY')],
    unique=[('save_id',)], checks=['singleton=1'], observation=False, public=False)
TABLES['saves'].columns[0].kind = 'INTEGER'
table('seasons', 'season_id', 'RES-L', 'one save-local season', [col('season_code', required=True), col('save_id', ref='saves(save_id)')], unique=[('season_code',)], observation=False)
table('teams', 'team_id', 'RES-T', 'stable save-local team identity', [col('display_name'), col('native_team_id'), col('native_identity_status', default="'UNKNOWN'")], observation=False)
table('players', 'player_id', 'RES-P', 'stable save-local player instance', [col('display_name', required=True), col('native_player_id'), col('native_identity_status', default="'UNVERIFIED'", check="native_identity_status IN ('UNKNOWN','UNVERIFIED','VERIFIED')")], observation=False)
table('staff_members', 'staff_id', 'RES-C', 'save-local staff identity', [col('display_name'), col('native_staff_id'), col('identity_state', default="'UNKNOWN'")], observation=False)
table('games', 'game_id', 'RES-G', 'one identified season game, not its changing observed state', [S(), ref('home_team_id', 'teams', 'team_id'), ref('away_team_id', 'teams', 'team_id'), col('game_date'), col('native_game_id'), col('game_kind')], checks=['home_team_id<>away_team_id'], observation=False, source='SEASON_GAME 60-byte candidate')
table('capture_runs', 'run_id', 'RES-D', 'one acquisition session', [S(), col('observed_at', required=True, unit='ISO8601 UTC', source='ACQUISITION_CLOCK'), col('source_grade', required=True, check="source_grade IN ('SYNTHETIC_FIXTURE','RESEARCH_FIXTURE','LIVE_READ')"), col('game_date'), col('decoder_version'), col('save_binding_ref')], public=False)
table('capture_units', 'unit_id', 'RES-D', 'one immutable atomic source consistency unit', [ref('run_id','capture_runs'), col('source_key', required=True), col('payload_sha256', required=True), col('unit_status', required=True, check="unit_status IN ('success','failed')"), col('observed_at', required=True, unit='ISO8601 UTC'), col('effective_at'), col('layout_version'), col('completeness', default="'PARTIAL'", check="completeness IN ('COMPLETE','PARTIAL','FAILED')")], unique=[('run_id','source_key')], observation=False, public=False)
table('source_artifacts', 'artifact_id', 'RES-D', 'one bounded source artifact hash, no public raw bytes', [U(), col('sha256', required=True), col('payload_kind', required=True), col('restricted','INTEGER',required=True,default='1',check='restricted IN (0,1)'), col('source_version'), col('payload_ref', visibility='OWNER_ONLY'), col('byte_count','INTEGER',check='byte_count>=0')], public=False)
table('native_fields', 'field_id', 'RES-D', 'versioned source-field mapping metadata', [col('source_group',required=True), col('native_key',required=True), col('ui_label'), col('evidence_grade',required=True,default="'UNKNOWN'"), col('visibility',required=True,default="'UNKNOWN'"), col('min_native_value','INTEGER'),col('max_native_value','INTEGER'),col('table_name'),col('column_name'),col('codec'),col('layout_version'),col('source_ref'),col('unit'),col('legal_range_state',default="'UNKNOWN'"),col('null_meaning',default="'NOT_OBSERVED'")], checks=['min_native_value IS NULL OR max_native_value IS NULL OR min_native_value<=max_native_value'], public=False)
table('field_gaps', 'gap_id', 'RES-D', 'one unresolved target-field gap or Human exception', [ref('field_id','native_fields',required=False),col('affected_domain',required=True),col('reason',required=True),col('impact',required=True),col('human_exception_ref'),col('target_field'),col('alternative'),col('status',default="'OPEN'",check="status IN ('OPEN','RESOLVED','HUMAN_EXCEPTION')")],public=False)
table('fact_conflicts','conflict_id','RES-D','one quarantined conflict with an existing fact',[col('object_ref',required=True),col('evidence_a',required=True),col('evidence_b',required=True),col('review_status',default="'PENDING_HUMAN'"),col('human_decision_ref'),U()],public=False)
table('team_seasons','team_season_id','RES-T','team participation in one season',[T(),S(),U(),col('conference'),col('division'),col('team_name')],unique=[('team_id','season_id','unit_id')])
table('roster_memberships','membership_id','RES-T','observed player team membership; not a transfer event',[P(),T(False),U(),col('roster_status'),col('native_roster_slot','INTEGER')],unique=[('player_id','unit_id')])
table('team_rotation_slots','slot_id','RES-T','one ordered team rotation setting',[T(),ref('player_id','players',required=False),U(),col('slot_index','INTEGER',required=True,check='slot_index>=0'),col('planned_minutes','INTEGER'),col('role_code')],unique=[('team_id','unit_id','slot_index')])
table('player_vitals_observations','observation_id','RES-P','one actual vitals observation',[P(),U()]+fields('first_name last_name nickname birth_date college country primary_position secondary_position handedness jersey_number','TEXT')+fields('height_raw weight_raw age_raw years_pro'),unique=[('player_id','unit_id')])

ATTR_FIELDS = [r for r in PROFILE['fields']['PLAYER'] if r['group']=='attributes' and r['name']!='potential']
attribute_cols = fields('overall_raw',source='UNKNOWN: overall field source not certified')
for r in ATTR_FIELDS:
    attribute_cols += fields(('three_point_shot' if r['name']=='3pt_shot' else r['name'])+'_raw', source=f'{PROFILE_REF} PLAYER +{r["offset"]} bytes={r["bytes"]}; REGISTRY_ONLY')
table('player_attribute_snapshots','snapshot_id','RES-P','one player successful typed attribute family observation',[P(),U()]+attribute_cols,unique=[('player_id','unit_id')],source=PROFILE_REF)
TENDENCY_FIELDS = PLAYER_CONFIG['TENDENCY_OFFSETS']
tendency_cols = fields('shot_tendency_raw drive_tendency_raw',source='UNKNOWN: legacy synthetic aliases; not native-certified')
for name, offset in TENDENCY_FIELDS.items():
    clean = re.sub('[^a-z0-9_]', '_',name.lower())+'_raw'
    existing=next((c for c in tendency_cols if c.name==clean),None)
    if existing:
        existing.source=f'config/state_io_native/player.json TENDENCY_OFFSETS.{name}={offset}; RESEARCH_LEAD'
    else:
        tendency_cols += fields(clean,source=f'config/state_io_native/player.json TENDENCY_OFFSETS.{name}={offset}; RESEARCH_LEAD')
table('player_tendency_snapshots','snapshot_id','RES-P','one player named tendency family observation',[P(),U()]+tendency_cols,unique=[('player_id','unit_id')])
table('player_badge_values','badge_observation_id','RES-P','one enumerated badge observation; absence is not unowned',[P(),U(),col('badge_key',required=True),col('native_code','INTEGER'),col('tier_label'),col('owned_state',required=True,check="owned_state IN ('owned','not_owned','unknown')")],unique=[('player_id','unit_id','badge_key')],source='Badge bit encoding UNKNOWN; source research conflicts retained')
table('player_play_type_slots','play_type_observation_id','RES-P','one ordered player play type slot',[P(),U(),col('slot_index','INTEGER',required=True,check='slot_index>=0'),col('native_play_code')],unique=[('player_id','unit_id','slot_index')],source='config/state_io_native/player.json PLAY_TYPE_NAMES; research only')
contract_cols=[]
for r in PROFILE['fields']['PLAYER']:
    if r['group']=='contract':
        contract_cols += fields(r['name']+'_raw',source=f'{PROFILE_REF} PLAYER +{r["offset"]} bit={r.get("start_bit",0)} width={r.get("bits",r.get("bytes",0)*8)}; REGISTERED_LAYOUT_NOT_CURRENT_UI_ACCEPTANCE',unit='raw integer; salary units UNKNOWN' if r['name'].startswith('contract_year') else 'native raw code')
table('player_contract_observations','contract_obs_id','RES-M','one actual contract observation, not inferred signing event',[P(),T(False),U()]+contract_cols,unique=[('player_id','unit_id')])
table('player_health_observations','health_id','RES-P','observed health separate from attribute durability',[P(),U()]+fields('injury_code body_part severity availability recovery_text','TEXT')+fields('fatigue_raw energy_raw recovery_days'),unique=[('player_id','unit_id')])
table('player_morale_observations','morale_id','RES-P','observed native morale/role, not AI personality',[P(),U(),col('role_code'),col('morale_raw','INTEGER'),col('role_satisfaction_raw','INTEGER')],unique=[('player_id','unit_id')])
table('player_training_observations','training_id','RES-P','observed personal training settings',[P(),U(),T(False),col('focus_code'),col('intensity_raw','INTEGER'),col('schedule_code')],unique=[('player_id','unit_id')])
table('game_state_observations','observation_id','RES-G','observed status and native score if actually available',[G(),U(),col('status_code',required=True)]+fields('home_points away_points overtime_count attendance was_simulated')+[col('score_provenance',default="'UNKNOWN'"),col('is_final','INTEGER',default='0',check='is_final IN (0,1)')],unique=[('game_id','unit_id')],source=STATS_SOURCE)
table('game_period_scores','period_score_id','RES-G','one team one actual period score observation',[G(),T(),U(),col('period_index','INTEGER',required=True,check='period_index>=1'),col('period_points','INTEGER',required=True,check='period_points>=0')],unique=[('game_id','team_id','period_index','unit_id')],source='SEASON_GAME +44..51; OT byte is aggregate, not individually split')
table('team_game_boxes','box_id','RES-G','one game team native box observation',[G(),T(),U()]+fields(STATS,source=STATS_SOURCE)+fields('fastbreak_points paint_points second_chance_points points_off_turnovers largest_lead',source=STATS_SOURCE),unique=[('game_id','team_id','unit_id')])
table('player_game_boxes','box_id','RES-G','one game player native box observation',[G(),P(),T(),U()]+fields(STATS,source=STATS_SOURCE)+fields('defensive_fg_made defensive_fg_attempted defensive_points is_starter in_use',source=STATS_SOURCE)+[col('points_provenance',default="'UNKNOWN'")],unique=[('game_id','player_id','unit_id')],checks=['fg_made IS NULL OR fg_attempted IS NULL OR fg_made<=fg_attempted'])
table('playoff_series','series_id','RES-G','one identified native playoff series',[S(),ref('team_a_id','teams','team_id'),ref('team_b_id','teams','team_id'),col('round_code'),U()],checks=['team_a_id<>team_b_id'])
table('playoff_series_games','series_game_id','RES-G','evidenced series-to-game association',[ref('series_id','playoff_series'),G(),col('sequence_no','INTEGER'),U()],unique=[('series_id','game_id','unit_id')])
table('player_season_totals','total_id','RES-L','native cumulative player season totals observation',[P(),S(),U(),T(False),col('team_scope'),col('phase_code'),col('is_final','INTEGER',default='0',check='is_final IN (0,1)')]+fields('games_played games_started '+STATS+' double_doubles triple_doubles',source='AG_NATIVE_01D Slot24 48-byte PLAYER_STATS candidate'),unique=[('player_id','season_id','unit_id')])
table('team_season_totals','total_id','RES-L','native cumulative team season observation',[T(),S(),U(),col('phase_code'),col('is_final','INTEGER',default='0',check='is_final IN (0,1)')]+fields('wins losses '+STATS+' opponent_points',source='memory_field_profile.json TEAM_STATS; registry only'),unique=[('team_id','season_id','unit_id')])
table('staff_team_assignments','assignment_id','RES-C','evidenced actual staff role assignment',[F(),T(False),U(),col('role_code',required=True)],unique=[('staff_id','unit_id','role_code')])
table('staff_contract_observations','contract_obs_id','RES-C','one staff contract observation',[F(),U()]+fields('salary_raw years_left'),unique=[('staff_id','unit_id')])
table('staff_skill_observations','skill_obs_id','RES-C','one staff typed skill family observation',[F(),U()]+fields('offense_raw defense_raw contracts_raw trading_raw scouting_raw training_raw business_raw',source='memory_field_profile.json STAFF; packed-bit fields require decoder'),unique=[('staff_id','unit_id')])
table('coach_preferences','pref_id','RES-C','one coach preferences observation',[F(),U()]+fields('preferred_system_raw active_system_raw')+[col('personal_style')],unique=[('staff_id','unit_id')])
table('team_tactic_settings','tactic_id','RES-C','one team actual tactics settings observation',[T(),U()]+fields('poe_code ace_code preferred_system_raw run_plays_raw help_defense_raw zone_usage_raw tempo_raw crash_offensive_glass_raw crash_defensive_glass_raw bench_depth_raw')+fields('freelance_slot_1 freelance_slot_2 freelance_slot_3 freelance_slot_4','TEXT'),unique=[('team_id','unit_id')])
table('team_playbook_slots','slot_id','RES-C','one ordered actual team playbook entry',[T(),U(),col('slot_index','INTEGER',required=True,check='slot_index>=0'),col('play_code'),col('play_name'),col('playbook_native_id')],unique=[('team_id','unit_id','slot_index')])
table('team_training_settings','training_id','RES-C','one team actual training settings',[T(),U(),col('focus_code'),col('intensity_raw','INTEGER'),col('schedule_code')],unique=[('team_id','unit_id')])
table('mentorship_relations','mentor_id','RES-C','observed actual mentor association',[P(),ref('mentor_player_id','players','player_id',False),T(False),U()],checks=['player_id<>mentor_player_id'],unique=[('player_id','unit_id')])
table('team_finance_observations','finance_id','RES-M','native financial snapshot, not external CBA inference',[T(),U()]+fields('payroll_raw cap_space_raw luxury_tax_raw budget_raw salary_cap_raw hard_cap_raw'),unique=[('team_id','unit_id')])
table('market_state_observations','market_id','RES-M','native or external market state with explicit origin',[ref('player_id','players',required=False),ref('staff_id','staff_members',required=False),U(),col('market_status',required=True),col('origin_type',required=True,check="origin_type IN ('NATIVE','EXTERNAL')")])
table('external_transaction_events','transaction_id','RES-M','explicit completed external transaction, never roster-diff inference',[SAVE(),U(),col('event_type',required=True),col('occurred_at'),col('source_ref',required=True),col('status',required=True),col('producer_event_id',required=True)],unique=[('source_ref','producer_event_id')],public=False)
table('draft_pick_assets','pick_id','RES-M','one actual draft pick identity',[SAVE(),col('draft_year','INTEGER',required=True),col('draft_round','INTEGER',required=True),ref('original_team_id','teams','team_id'),col('native_pick_id')],unique=[('draft_year','draft_round','original_team_id')],observation=False)
table('transaction_components','component_id','RES-M','one evidenced external transaction component',[ref('transaction_id','external_transaction_events'),U(),ref('from_team_id','teams','team_id',False),ref('to_team_id','teams','team_id',False),ref('player_id','players',required=False),ref('staff_id','staff_members',required=False),ref('pick_id','draft_pick_assets',required=False),col('component_kind',required=True),col('salary_raw','INTEGER')],public=False)
table('draft_pick_ownerships','ownership_id','RES-M','observed or explicit event-backed pick ownership',[ref('pick_id','draft_pick_assets'),ref('owner_team_id','teams','team_id'),U(),ref('event_ref','external_transaction_events','transaction_id',False),col('origin_type',required=True,check="origin_type IN ('NATIVE','EXTERNAL')")],unique=[('pick_id','unit_id')])
table('draft_prospects','prospect_id','RES-M','one evidenced prospect, separate from player instance',[SAVE(),col('draft_year','INTEGER',required=True),col('native_prospect_id'),col('display_name'),U()])
table('draft_results','result_id','RES-M','actual source-backed draft result',[ref('prospect_id','draft_prospects',required=False),ref('pick_id','draft_pick_assets',required=False),T(),ref('player_id','players',required=False),U(),col('source_ref',required=True),col('selection_number','INTEGER')])
table('worldline_config_versions','config_id','RES-S','versioned desired configuration, never actual game state',[SAVE(),U(),col('config_version',required=True),col('config_hash',required=True),col('approval_ref')],unique=[('config_version',)],public=False)
table('game_setting_observations','setting_obs_id','RES-S','one actual native setting, using typed value alternatives',[U(),ref('field_id','native_fields'),col('scope_code',required=True),col('integer_value','INTEGER'),col('real_value','REAL'),col('text_value'),col('display_value')],unique=[('unit_id','field_id','scope_code')],checks=['(integer_value IS NOT NULL)+(real_value IS NOT NULL)+(text_value IS NOT NULL)=1'])
table('startup_config_checks','check_id','RES-S','desired-vs-observed configuration check',[ref('config_id','worldline_config_versions',required=False),ref('setting_obs_id','game_setting_observations',required=False),U(),col('result',required=True),col('dependency_ref')],public=False)
table('league_rule_observations','rule_id','RES-L','one actual season rule observation',[S(),U(),col('rule_key',required=True),col('integer_value','INTEGER'),col('text_value'),col('display_value')],unique=[('season_id','unit_id','rule_key')])
table('season_award_instances','award_id','RES-H','actual awarded honor; leaders are not winners',[S(),U(),col('award_code',required=True),col('award_type',required=True),col('is_final','INTEGER',required=True,check='is_final=1')],unique=[('season_id','award_code','award_type')])
table('award_recipients','recipient_id','RES-H','one actual award recipient',[ref('award_id','season_award_instances'),ref('player_id','players',required=False),T(False),col('rank_index','INTEGER'),U()],checks=['player_id IS NOT NULL OR team_id IS NOT NULL'])
table('season_record_entries','record_id','RES-H','one actual record holder/value, no fabricated honors',[S(),U(),col('record_key',required=True),ref('holder_player_id','players','player_id',False),ref('holder_team_id','teams','team_id',False),col('value_raw',required=True),col('source_ref',required=True),col('occurred_at')])
table('external_execution_receipts','receipt_id','RES-D','external executor report, not proof of readback',[SAVE(),ref('transaction_id','external_transaction_events',required=False),U(),col('attempted_at',required=True),col('write_status',required=True),col('source_ref',required=True),col('approval_ref')],public=False)
table('external_readback_checks','check_id','RES-D','separate observed readback reconciliation',[ref('receipt_id','external_execution_receipts'),U(),col('expected_state',required=True),col('observed_state'),col('reconcile_status',required=True)],public=False)
table('native_identity_links','link_id','RES-D','one versioned native ID to actual save-local entity link',[SAVE(),U(),col('entity_type',required=True,check="entity_type IN ('player','team','game','staff')"),col('entity_id',required=True),col('native_id'),col('valid_from'),col('identity_state',required=True)],public=False)
table('player_restricted_observations','observation_id','RES-P','restricted external-storage metadata; raw Potential never in world facts',[P(),U(),col('restricted_field_key',required=True,visibility='OWNER_ONLY'),col('protected_value_ref',required=True,visibility='OWNER_ONLY'),col('authorization_scope',required=True,visibility='OWNER_ONLY')],public=False)
table('game_news_entries','news_id','RES-H','one source-observed native news item',[ref('season_id','seasons',required=False),U(),col('native_news_id'),col('text_body'),col('occurrence_time')],public=False)
# Added to the 59-table proposal: explicit season freeze boundary instead of
# treating the last observed cumulative snapshot as an accepted final season.
table('season_finalizations','finalization_id','RES-D','explicit evidenced season closure boundary',[S(),U(),col('source_ref',required=True),col('finalized_at',required=True)],unique=[('season_id',)],public=False)
table('native_box_observations','box_observation_id','RES-D','one captured Box row before canonical player identity is proven',
      [G(),U(),col('side',required=True,check="side IN ('HOME','AWAY')"),
       col('row_index','INTEGER',required=True,check='row_index>=0'),col('native_player_id','INTEGER',required=True),
       col('native_team_id','INTEGER',required=True),col('in_use','INTEGER',required=True,check='in_use IN (0,1)')]+
      fields(STATS,source='OWNER_CAPTURED_24_BYTE_BOX_RECORD; candidate decode, not canonical identity')+
      [col('points_provenance',required=True),col('identity_status',required=True,default="'UNRESOLVED'")],
      unique=[('game_id','unit_id','side','row_index')],public=False)

# Field-level evidence annotations for the implemented sample adapter. Never
# promote a native legal game/UI range from its packed integer storage width.
for name in ('player_game_boxes','team_game_boxes','player_season_totals','team_season_totals'):
    for c in TABLES[name].columns:
        if c.name in STATS.split() or c.name in ('games_played','games_started'):
            c.unit='minutes (research decoder)' if c.name=='minutes_raw' else 'count or signed count; native/UI range UNKNOWN'
            if c.name not in ('plus_minus',):
                c.check=f'{ident(c.name)} IS NULL OR {ident(c.name)}>=0'
for c in TABLES['player_game_boxes'].columns:
    if c.name=='points':c.source='DERIVED_WITH_FORMULA: 2*fg_made+three_made+ft_made; AG01D fixture replay'
for c in TABLES['game_period_scores'].columns:
    if c.name=='period_points':c.source='AG_NATIVE_01D SEASON_GAME +44..51 bytes; regulation periods only; RESEARCH_FIXTURE'


def schema_sql():
    out=['-- Generated: 59 proposed tables + game states + season finalizations + typed unresolved Native Box staging.\nPRAGMA foreign_keys=ON;']
    for t in TABLES.values():
        definitions=[c.sql()+(' PRIMARY KEY' if c.name==t.key else '') for c in t.columns]
        definitions += ['UNIQUE ('+','.join(map(ident, cols))+')' for cols in t.unique]
        definitions += ['CHECK ('+expr+')' for expr in t.checks]
        out.append(f'CREATE TABLE {ident(t.name)} (\n  '+',\n  '.join(definitions)+'\n) STRICT;')
        for c in t.columns:
            if c.ref: out.append(f'CREATE INDEX "idx_{t.name}_{c.name}" ON {ident(t.name)} ({ident(c.name)});')
        for op in ['UPDATE','DELETE']:
            out.append(f'CREATE TRIGGER "{t.name}_no_{op.lower()}" BEFORE {op} ON {ident(t.name)} BEGIN SELECT RAISE(ABORT,\'immutable history\'); END;')
        if t.observation and any(c.name=='unit_id' for c in t.columns):
            out.append(f'CREATE TRIGGER "{t.name}_successful_unit" BEFORE INSERT ON {ident(t.name)} WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status=\'success\') BEGIN SELECT RAISE(ABORT,\'capture unit is not successful\'); END;')
    for name in ['player_game_boxes','team_game_boxes','game_period_scores']:
        out.append(f'CREATE TRIGGER "{name}_participant" BEFORE INSERT ON {name} WHEN NOT EXISTS (SELECT 1 FROM games WHERE game_id=NEW.game_id AND NEW.team_id IN (home_team_id,away_team_id)) BEGIN SELECT RAISE(ABORT,\'team is not a game participant\'); END;')
    # Once a game is final, fill formerly unobserved fields but never silently
    # accept a different value for an already observed historical stat.
    for name, keys in [('player_game_boxes',['game_id','player_id']),('team_game_boxes',['game_id','team_id']),('game_period_scores',['game_id','team_id','period_index']),('game_state_observations',['game_id'])]:
        spec=TABLES[name]
        compare=[c.name for c in spec.columns if c.name not in {spec.key,'unit_id',*keys}]
        match=' AND '.join(f'old.{ident(k)}=NEW.{ident(k)}' for k in keys)
        diff=' OR '.join(f'(old.{ident(k)} IS NOT NULL AND NEW.{ident(k)} IS NOT NULL AND old.{ident(k)}<>NEW.{ident(k)})' for k in compare)
        out.append(f'CREATE TRIGGER "{name}_frozen_conflict" BEFORE INSERT ON {name} WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM {name} old WHERE {match} AND ({diff})) BEGIN SELECT RAISE(ABORT,\'frozen game conflict; quarantine required\'); END;')
    for kind, target, key in [('player','players','player_id'),('team','teams','team_id'),('game','games','game_id'),('staff','staff_members','staff_id')]:
        out.append(f'CREATE TRIGGER "identity_{kind}_fk" BEFORE INSERT ON native_identity_links WHEN NEW.entity_type=\'{kind}\' AND NOT EXISTS(SELECT 1 FROM {target} WHERE {key}=NEW.entity_id) BEGIN SELECT RAISE(ABORT,\'unresolved native identity\'); END;')
    for name, entities in [('player_season_totals',['player_id','season_id']),('team_season_totals',['team_id','season_id'])]:
        where=' AND '.join(f'{c}=NEW.{c}' for c in entities)
        out.append(f'CREATE TRIGGER "{name}_final_once" BEFORE INSERT ON {name} WHEN EXISTS (SELECT 1 FROM {name} WHERE {where} AND is_final=1) OR EXISTS(SELECT 1 FROM season_finalizations WHERE season_id=NEW.season_id) BEGIN SELECT RAISE(ABORT,\'season totals already finalized; quarantine conflict\'); END;')
    out += [
        '''CREATE VIEW gm_player_observations AS SELECT p.player_id,p.display_name,a.*,u.observed_at,r.source_grade FROM player_attribute_snapshots a JOIN players p USING(player_id) JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE u.unit_status='success';''',
        '''CREATE VIEW gm_game_box AS SELECT g.game_id,g.season_id,g.game_date,p.display_name,b.*,u.observed_at,r.source_grade FROM player_game_boxes b JOIN games g USING(game_id) JOIN players p USING(player_id) JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE u.unit_status='success';''',
        '''CREATE VIEW derived_game_scores AS SELECT game_id,unit_id,team_id,SUM(period_points) AS regulation_points,'DERIVED_SUM_PERIODS' AS provenance FROM game_period_scores GROUP BY game_id,unit_id,team_id;''',
        '''CREATE VIEW derived_player_box_metrics AS SELECT box_id,CASE WHEN fg_attempted>0 THEN 1.0*(fg_made+0.5*three_made)/fg_attempted END AS efg_pct,CASE WHEN fg_attempted+0.44*ft_attempted>0 THEN points/(2.0*(fg_attempted+0.44*ft_attempted)) END AS ts_pct,'DERIVED_WITH_FORMULA_V1' AS provenance FROM player_game_boxes;'''
    ]
    return '\n\n'.join(out)+'\n'


def dictionary():
    result={'schema_version':VERSION,'table_count':len(TABLES),'evidence_policy':'Native legal ranges UNKNOWN unless separately certified; registration and fixture replay are not live acceptance', 'tables':[]}
    for t in TABLES.values():
        row={'name':t.name,'domain':t.domain,'grain':t.grain,'reason_for_table':t.grain+'; independent identity/lifecycle or consistency unit',
             'primary_key':t.key,'unique_keys':[list(u) for u in t.unique],'checks':t.checks,'append_only':True,'gm_queryable':t.public,
             'source_status':t.source,'v1_mapping':'EXTEND_PRESERVE' if t.name in LEGACY_TABLES else 'ADD', 'columns':[]}
        for c in t.columns:
            row['columns'].append({'name':c.name,'sqlite_type':c.kind,'meaning':c.meaning or c.name.replace('_',' '),
                'required':c.required,'default':c.default,'null_meaning':None if c.required else 'NOT_OBSERVED in this unit; not zero or previous value',
                'unit':c.unit,'foreign_key':c.ref,'sql_constraint':c.check,'legal_game_range':'NOT_APPLICABLE' if c.source.startswith(('ENGINEERING_','SYSTEM_','ACQUISITION_','EVIDENCE_','HUMAN_')) else 'UNKNOWN',
                'source':c.source,'visibility':c.visibility if t.public else 'OWNER_ONLY',
                'time_semantics':'observation time from unit_id; effective game time separately recorded' if t.observation else 'immutable identity or metadata'})
        result['tables'].append(row)
    return result


LEGACY_TABLES = set('saves seasons teams players games capture_runs capture_units source_artifacts native_fields field_gaps game_state_observations player_game_boxes player_attribute_snapshots player_tendency_snapshots player_badge_values player_play_type_slots'.split())


if __name__=='__main__':
    (BASE/'schema.sql').write_text(schema_sql(),encoding='utf-8',newline='\n')
    (BASE/'field_dictionary.json').write_text(json.dumps(dictionary(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    cards=['# Executable world table cards (development candidate)', '',
        'Generated from `schema_model.py`. Column-level types, constraints, units, null semantics, visibility and source evidence are in `field_dictionary.json`.',
        '',f'Actual tables: **{len(TABLES)}**. Every table is STRICT and append-only. A SQLite owner can still replace a database; ordinary roles receive query results, never direct file access.','',
        '| Table | Domain | One row / reason | Primary key | Foreign keys | v1 mapping |','|---|---|---|---|---|---|']
    for t in TABLES.values():
        fks='; '.join(c.name+' -> '+c.ref for c in t.columns if c.ref)
        cards.append(f'| `{t.name}` | {t.domain} | {t.grain} | `{t.key}` | {fks} | '+('EXTEND/PRESERVE' if t.name in LEGACY_TABLES else 'ADD')+' |')
    (BASE/'TABLE_CARDS.md').write_text('\n'.join(cards)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'tables':len(TABLES),'columns':sum(len(t.columns) for t in TABLES.values())}))
