"""Executable, typed catalog. Native ranges stay UNKNOWN until evidenced.

The SQL and complete field cards are generated from this module; persisted facts
are relational columns, never an EAV/JSON substitute for the domain model.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
DOMAIN = BASE.parent
VERSION = 7
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
    col('schema_version', 'INTEGER', required=True, check=f'schema_version={VERSION}', source='ENGINEERING_SCHEMA_VERSION'),
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
COACH_FIELD_COLUMNS={'POEDefense':'poe_defense_1_raw','POEDefense2':'poe_defense_2_raw','POEDefense3':'poe_defense_3_raw',
    'POEOffense':'poe_offense_1_raw','POEOffense2':'poe_offense_2_raw','POEOffense3':'poe_offense_3_raw',
    'SimPace':'sim_pace_raw','SimPress':'sim_pressure_raw','SimHelpDef':'sim_help_defense_raw',
    'SimOffReb':'sim_offensive_rebounds_raw','SimDefReb':'sim_defensive_rebounds_raw',
    'PreferredSystem':'preferred_system_raw','ActiveSystem':'active_system_raw','PlaybookID':'playbook_code_raw',
    'BenchDepth':'bench_depth_raw','RunPlayTendency':'run_plays_raw','ZoneUsage':'zone_usage_raw',
    'BenchUtilization':'bench_utilization_raw','Tempo':'tempo_raw','HelpDefense':'help_defense_raw',
    'FreelanceType':'freelance_slot_1','FreelanceType2':'freelance_slot_2','FreelanceType3':'freelance_slot_3','FreelanceType4':'freelance_slot_4'}
coach_profile=json.loads((DOMAIN/'config/coach_tactics_profile.json').read_bytes())
for native_name,column_name in COACH_FIELD_COLUMNS.items():
    spec=TABLES['team_tactic_settings'];existing=next((c for c in spec.columns if c.name==column_name),None)
    if existing is None:
        existing=col(column_name,'TEXT' if native_name.startswith('FreelanceType') else 'INTEGER',meaning='Observed native '+native_name)
        spec.columns.append(existing)
    f=coach_profile['fields'][native_name]
    existing.source=f'config/coach_tactics_profile.json {native_name} offset={f["offset"]} bit={f["start_bit"]} width={f["width"]}; current COACHDATA metadata checked by adapter'
    existing.unit='native code; target UI observation and effect separate'
table('team_playbook_slots','slot_id','RES-C','one ordered actual team playbook entry',[T(),U(),col('slot_index','INTEGER',required=True,check='slot_index>=0'),col('play_code'),col('play_name'),col('playbook_native_id')],unique=[('team_id','unit_id','slot_index')])
table('team_training_settings','training_id','RES-C','one team actual training settings',[T(),U(),col('focus_code'),col('intensity_raw','INTEGER'),col('schedule_code')],unique=[('team_id','unit_id')])
table('mentorship_relations','mentor_id','RES-C','observed actual mentor association',[P(),ref('mentor_player_id','players','player_id',False),T(False),U()],checks=['player_id<>mentor_player_id'],unique=[('player_id','unit_id')])
table('team_finance_observations','finance_id','RES-M','native financial snapshot, not external CBA inference',[T(),U()]+fields('payroll_raw cap_space_raw luxury_tax_raw budget_raw salary_cap_raw hard_cap_raw'),unique=[('team_id','unit_id')])
for name,offset in {'total_salary_raw':0xCBC,'payroll_raw':0xFF4,'budget_raw':0x1014,'staff_budget_raw':0x1018,
    'cash_raw':0x1010,'gate_revenue_raw':0xFD8,'merch_revenue_raw':0xFDC,'media_revenue_raw':0xFE4}.items():
    spec=TABLES['team_finance_observations'];c=next((c for c in spec.columns if c.name==name),None)
    if c is None:
        c=col(name,'INTEGER',meaning='Observed native '+name);spec.columns.append(c)
    c.source=f'src/config.py and src/dump_teams_info.py TEAM +{offset:#x} uint32; registered meaning not target UI acceptance'
    c.unit='unsigned native integer; no signed reinterpretation or CBA inference'
table('team_state_observations','state_id','RES-T','one team observed native chemistry/fan state',[T(),U()]+
    [col('chemistry_raw','REAL',source='src/config.py TEAM +0xEC4 float32',unit='native float; UI scale not newly observed'),
     col('fan_interest_raw','REAL',source='src/config.py TEAM +0xF7C float32',unit='native float; no percentage conversion')],unique=[('team_id','unit_id')])
TABLES['team_season_totals'].columns+=fields('points_off_turnovers second_chance_points paint_points bench_points pace_raw opponent_fg_made opponent_fg_attempted opponent_three_made opponent_three_attempted',
    source='config/memory_field_profile.json TEAM_STATS 62-byte raw registry; current wins/losses/points/PA reconciled with schedule')
for table_name,field_map in {
    'staff_contract_observations':{'salary_raw':'salary','years_left':'years_left'},
    'staff_skill_observations':{name+'_raw':name for name in ('offense','defense','contracts','trading','scouting','training','business')}
}.items():
    definitions={f['name']:f for f in PROFILE['fields']['STAFF']}
    for c in TABLES[table_name].columns:
        if c.name not in field_map:continue
        f=definitions[field_map[c.name]]
        c.source=f'config/memory_field_profile.json STAFF {f["name"]} +{f["offset"]} bit={f.get("start_bit",0)} width={f["bits"]}; current reciprocal TEAM role source'
        c.unit='native grade code' if table_name=='staff_skill_observations' else 'native raw contract integer; UI units separate'
for c in TABLES['coach_preferences'].columns:
    if c.name in ('preferred_system_raw','active_system_raw'):
        name='PreferredSystem' if c.name=='preferred_system_raw' else 'ActiveSystem'
        c.source=f'config/coach_tactics_profile.json {name}; actual COACHDATA metadata uses four bits; old STAFF three-bit registration not used'
for c in TABLES['staff_team_assignments'].columns:
    if c.name=='role_code':c.source='STAFF +0x10E bit2 width3 plus TEAM +0xCE8+8*role reciprocal pointers; profile role labels 0..7'
for c in TABLES['staff_members'].columns:
    if c.name=='native_staff_id':c.source='Current COACHDATA UniqueId metadata field (observed +0xD8 uint16); unique in assigned source set'
for c in TABLES['team_playbook_slots'].columns:
    if c.name=='slot_index':c.source='PLAYBOOKDATA +0x58, ordered array of 68 uint32 CRCs';c.unit='zero-based native slot index'
    elif c.name=='play_code':c.source='Native uint32 CRC from loaded PLAYBOOKDATA ordered slot';c.unit='eight lowercase hexadecimal digits, no decoded play name inferred'
    elif c.name=='playbook_native_id':c.source='PLAYBOOKDATA +0x3E uint16 unique ID; differs from loaded enum code at +0x54'
table('market_state_observations','market_id','RES-M','native or external market state with explicit origin',[ref('player_id','players',required=False),ref('staff_id','staff_members',required=False),U(),col('market_status',required=True),col('origin_type',required=True,check="origin_type IN ('NATIVE','EXTERNAL')")])
table('external_transaction_events','transaction_id','RES-M','explicit completed external transaction, never roster-diff inference',[SAVE(),U(),col('event_type',required=True),col('occurred_at'),col('source_ref',required=True),col('status',required=True),col('producer_event_id',required=True)],unique=[('source_ref','producer_event_id')],public=False)
table('draft_pick_assets','pick_id','RES-M','one actual draft pick identity',[SAVE(),col('draft_year','INTEGER',required=True),col('draft_round','INTEGER',required=True),ref('original_team_id','teams','team_id'),col('native_pick_id')],unique=[('draft_year','draft_round','original_team_id')],observation=False)
table('transaction_components','component_id','RES-M','one evidenced external transaction component',[ref('transaction_id','external_transaction_events'),U(),ref('from_team_id','teams','team_id',False),ref('to_team_id','teams','team_id',False),ref('player_id','players',required=False),ref('staff_id','staff_members',required=False),ref('pick_id','draft_pick_assets',required=False),col('component_kind',required=True),col('salary_raw','INTEGER')],public=False)
table('draft_pick_ownerships','ownership_id','RES-M','observed or explicit event-backed pick ownership',[ref('pick_id','draft_pick_assets'),ref('owner_team_id','teams','team_id'),U(),ref('event_ref','external_transaction_events','transaction_id',False),col('origin_type',required=True,check="origin_type IN ('NATIVE','EXTERNAL')")],unique=[('pick_id','unit_id')])
TABLES['draft_pick_ownerships'].columns+=fields('source_row_index native_pick_index_raw',source='DRAFT_ASSETS 32-byte actual descriptor index and +28 metadata bits8..15; not a selection result')+[
    col('protection_status',default="'UNKNOWN'",source='Protection semantics not decoded; absence is not unprotected'),
    col('swap_status',default="'UNKNOWN'",source='Swap semantics not decoded; absence is not no swap')]
table('draft_prospects','prospect_id','RES-M','one named prospect source observation, separate from PLAYER instance',[SAVE(),
    col('draft_year','INTEGER',source='UNKNOWN unless actual class year source is acquired; never infer from next future-pick year'),
    col('native_prospect_id',source='Public prospect record +0x2F8 uint16; not assumed unique in pool'),col('display_name'),
    col('class_year_status',default="'UNKNOWN'"),U()])
table('draft_pool_slot_observations','pool_slot_id','RES-M','one actual draft-pool slot observation, including uninitialized slots',[
    U(),col('source_row_index','INTEGER',required=True),col('slot_state',required=True),col('native_prospect_id'),
    col('display_name'),col('draft_year','INTEGER'),col('class_year_status',required=True)],unique=[('unit_id','source_row_index')],
    source='ROSTERDATA Slot4 count/pointer, 1264-byte public template excluding Potential; allocated slots are not necessarily people')
table('draft_prospect_attribute_snapshots','snapshot_id','RES-P','one named prospect public attribute observation',[
    ref('prospect_id','draft_prospects'),U()]+[replace(c) for c in attribute_cols],unique=[('prospect_id','unit_id')])
table('draft_prospect_tendency_snapshots','snapshot_id','RES-P','one named prospect registered tendency observation',[
    ref('prospect_id','draft_prospects'),U()]+[replace(c) for c in tendency_cols if c.name in {name.lower()+'_raw' for name in TENDENCY_FIELDS}],unique=[('prospect_id','unit_id')])
table('draft_prospect_play_type_slots','slot_id','RES-P','one named prospect ordered native play-type observation',[
    ref('prospect_id','draft_prospects'),U(),col('slot_index','INTEGER',required=True,check='slot_index>=0'),col('native_play_code')],unique=[('prospect_id','unit_id','slot_index')])
table('waived_salary_observations','waived_id','RES-M','one observed 136-byte native waived-salary source record; not an inferred release event',[
    T(False),ref('player_id','players',required=False),U(),col('source_row_index','INTEGER',required=True),
    col('owner_mapping_status',required=True),col('native_player_id','INTEGER'),col('observed_player_name'),
    col('player_mapping_status',required=True),col('name_source_status',required=True)]+
    fields('salary_year_1_raw salary_year_2_raw salary_year_3_raw',source='WAIVED_SALARY +16/+20/+24 uint32 research candidate, relative buckets; absolute season mapping and UI units unknown'),
    unique=[('unit_id','source_row_index')],source='ROSTERDATA Slot61 stride136; TEAM pointer+8; candidate inline UTF16 surname+56/given+96')
market_column_sources={
    'draft_pick_assets':{'draft_year':'DRAFT_ASSETS +28 bits22..31 +2000; checked native getter profile and complete groups',
        'draft_round':'DRAFT_ASSETS +28 bits3..7 +1; only verified future round codes0/1 accepted',
        'original_team_id':'DRAFT_ASSETS +8 TEAM pointer; current named getter bytes checked',
        'native_pick_id':'UNKNOWN: no stable unique Native pick ID is asserted from array index'},
    'draft_pick_ownerships':{'owner_team_id':'DRAFT_ASSETS +0 TEAM pointer; current named getter bytes checked',
        'origin_type':'EVIDENCE_CLASSIFICATION: observed native owner state, not a completed transaction'},
    'draft_pool_slot_observations':{'source_row_index':'ENGINEERING_ARRAY_INDEX: actual Slot4 descriptor-bounded index',
        'slot_state':'EVIDENCE_CLASSIFICATION: aligned UTF16 prefix presence; blank slot is not a person',
        'native_prospect_id':'Slot4 public template +0x2F8 uint16; zero/duplicate IDs not promoted to identity',
        'display_name':'Slot4 +0..39 surname and +40..79 given-name UTF16 candidate prefixes',
        'draft_year':'UNKNOWN: actual class year not inferred from future pick base',
        'class_year_status':'EVIDENCE_CLASSIFICATION: actual class year source missing'},
    'waived_salary_observations':{'team_id':'WAIVED_SALARY +8 exact current TEAM pointer mapping; not economic active-status proof',
        'source_row_index':'ENGINEERING_ARRAY_INDEX: actual Slot61 descriptor-bounded index',
        'owner_mapping_status':'EVIDENCE_CLASSIFICATION: CORE_TEAM_POINTER or UNMAPPED_OR_EMPTY',
        'native_player_id':'UNKNOWN: no Native person ID inferred from the first Q word or inline name',
        'observed_player_name':'WAIVED_SALARY candidate inline UTF16 surname+56..95/given+96..135; no canonical association',
        'player_mapping_status':'EVIDENCE_CLASSIFICATION: canonical PLAYER link not established',
        'name_source_status':'EVIDENCE_CLASSIFICATION: candidate inline text decoding only'}}
for table_name,mapping in market_column_sources.items():
    for c in TABLES[table_name].columns:
        if c.name in mapping:c.source=mapping[c.name]
for table_name in ('draft_prospect_attribute_snapshots','draft_prospect_tendency_snapshots'):
    for c in TABLES[table_name].columns:
        if c.name.endswith('_raw'):c.source='Slot4 TEMPLATE_CANDIDATE; named initialized-class Native acceptance outstanding; '+c.source
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

GAMEPLAN_HEADER_MAP={'POEOffense':'poe_offense_1_raw','POEOffense2':'poe_offense_2_raw','POEOffense3':'poe_offense_3_raw',
    'POEDefense':'poe_defense_1_raw','POEDefense2':'poe_defense_2_raw','POEDefense3':'poe_defense_3_raw',
    'HelpDefense':'help_defense_raw','RunPlayTendency':'run_plays_raw','ZoneUsage':'zone_usage_raw','BenchDepth':'bench_depth_raw',
    'BenchUtilization':'bench_utilization_raw','LineupFormFactor':'lineup_form_factor_raw','PlaybookID':'playbook_code_raw','FreelanceType':'freelance_code_raw'}
DEFENSE_COLUMN_MAP={'PressureOnball':'pressure_onball_raw','PressureOffball':'pressure_offball_raw','ForceDirection':'force_direction_raw',
    'ScreenDefenseOnBall':'screen_defense_onball_raw','ScreenDefenseHedge':'screen_defense_hedge_raw','OffballScreenDefense':'offball_screen_defense_raw',
    'PostDefense':'post_defense_raw','DoubleTeamPerimeter':'double_team_perimeter_raw','DoubleTeamPost':'double_team_post_raw',
    'ScreenDefenseOnBall5':'screen_defense_onball5_raw','ScreenDefenseHedge5':'screen_defense_hedge5_raw','SwitchRule':'switch_rule_raw',
    'OnballHelp':'onball_help_raw','ScreenHelp':'screen_help_raw','ExtendPressure':'extend_pressure_raw','TagOnRoll':'tag_on_roll_raw',
    'StayAttached':'stay_attached_raw','PreRotate':'pre_rotate_raw'}
table('gameplan_observations','plan_id','RES-C','one stored owner/opponent GAMEPLAN observation; commit flag is not game-effect proof',[
    T(),ref('opponent_team_id','teams','team_id'),U(),col('source_slot_index','INTEGER',required=True),
    col('is_in_use_raw','INTEGER',required=True),col('is_tainted_raw','INTEGER',required=True)]+
    fields(' '.join(GAMEPLAN_HEADER_MAP.values()),source='src/gameplan_codec.py unpacked GAMEPLAN +0x17E..0x18B; native type metadata anchors checked; distinct from packed COACHDATA'),
    unique=[('team_id','opponent_team_id','unit_id')],checks=['team_id<>opponent_team_id'])
table('gameplan_rotation_observations','rotation_id','RES-C','one stored plan ordered rotation entry, including sentinel slots',[
    ref('plan_id','gameplan_observations'),U(),col('slot_index','INTEGER',required=True),col('native_rotation_id_raw','INTEGER',required=True),
    ref('player_id','players',required=False),col('rotation_spot_raw','INTEGER'),col('playing_time_raw','INTEGER'),col('identity_status',required=True)],
    unique=[('plan_id','slot_index','unit_id')],source='GAMEPLAN +6, 23 four-byte entries; canonical link only to exact current own roster UID')
table('gameplan_defense_observations','defense_id','RES-C','one stored plan defensive row, including empty sentinel rows',[
    ref('plan_id','gameplan_observations'),U(),col('slot_index','INTEGER',required=True),col('native_matchup_id_raw','INTEGER',required=True),
    col('native_defender_id_raw','INTEGER',required=True),ref('opponent_player_id','players','player_id',False),ref('defender_player_id','players','player_id',False),
    col('slot_status',required=True),col('identity_status',required=True)]+
    fields(' '.join(DEFENSE_COLUMN_MAP.values()),source='Current GAMEPLAN_MATCHUP_DEFENSIVE_SETTINGS native metadata; packed eight-byte row +0x64+12*i+4'),
    unique=[('plan_id','slot_index','unit_id')])
training_flags='position_raw player_type_raw intensity_raw injury_recovery_raw is_intensity_overriden_raw'
table('player_training_slot_observations','training_slot_id','RES-P','one profile-bounded training slot; window capacity is not active player count',[
    U(),col('source_slot_index','INTEGER',required=True),col('native_player_id_raw','INTEGER',required=True),col('identity_status',required=True)]+
    fields(training_flags,source='training.json PLAYER_TRAINING ID+0 / flags+0x318; stride796 bound786; history arrays not read'),unique=[('unit_id','source_slot_index')])
TABLES['team_training_settings'].columns+=fields('home_intensity_raw away_intensity_raw automate_intensity_raw rest_before_b2b_raw rest_after_b2b_raw injury_recovery_raw',
    source='training.json TEAM_TRAINING flags+0x53/+0x54; current franchise slot maps to training root +88*slot')
TABLES['player_training_observations'].columns+=fields('position_raw player_type_raw injury_recovery_raw is_intensity_overriden_raw source_slot_index',
    source='training.json PLAYER_TRAINING +0x318 packed flags; exact unique current roster UID match')+[col('identity_status')]
table('mentor_manager_observations','manager_id','RES-C','one observed mentorship header per current franchise team',[
    T(),U(),col('franchise_slot','INTEGER'),col('header_team_id_raw','INTEGER'),col('first_badge_raw','INTEGER'),
    col('relation_count_raw','INTEGER'),col('layout_status',required=True)],unique=[('team_id','unit_id')],source='training.json franchise manager +0x132A8 first12 bytes; owner/count plausibility separate from effect')
table('native_mentor_relation_observations','native_relation_id','RES-C','one native mentorship relation header before canonical/effect claims',[
    T(),U(),col('source_slot_index','INTEGER'),col('mentee_id_raw','INTEGER'),col('mentor_id_raw','INTEGER'),
    col('duration_days_raw','INTEGER'),col('compatibility_word_raw','INTEGER'),col('badge_count_raw','INTEGER'),col('identity_status',required=True)],
    unique=[('team_id','unit_id','source_slot_index')],source='training.json relation entry204 first24 bytes; badge slots not read')
TABLES['mentorship_relations'].columns+=fields('source_slot_index duration_days_raw compatibility_word_raw badge_count_raw',
    source='Current native mentorship relation header plus both exact own-roster UID links; compatibility word not converted')+[
    col('association_status',default="'OBSERVED_PAIR_ACTIVITY_NOT_VERIFIED'",source='EVIDENCE_CLASSIFICATION: association source/identity only, not actor consent or badge effect')]

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
    out=['-- Generated: approved catalog + explicit game/finalization/source staging and team state observations.\nPRAGMA foreign_keys=ON;']
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
    for name in ('gameplan_rotation_observations','gameplan_defense_observations'):
        out.append(f'CREATE TRIGGER "{name}_same_unit" BEFORE INSERT ON {name} WHEN NOT EXISTS(SELECT 1 FROM gameplan_observations p WHERE p.plan_id=NEW.plan_id AND p.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,\'cross-unit gameplan child\'); END;')
    for name,column,owner in [('gameplan_rotation_observations','player_id','team_id'),('gameplan_defense_observations','opponent_player_id','opponent_team_id'),('gameplan_defense_observations','defender_player_id','team_id')]:
        out.append(f'CREATE TRIGGER "{name}_{column}_roster" BEFORE INSERT ON {name} WHEN NEW.{column} IS NOT NULL AND NOT EXISTS(SELECT 1 FROM gameplan_observations p JOIN roster_memberships r ON r.unit_id=NEW.unit_id AND r.team_id=p.{owner} AND r.player_id=NEW.{column} WHERE p.plan_id=NEW.plan_id) BEGIN SELECT RAISE(ABORT,\'gameplan player lacks same-unit roster owner\'); END;')
    for name in ['player_game_boxes','team_game_boxes','game_period_scores']:
        out.append(f'CREATE TRIGGER "{name}_participant" BEFORE INSERT ON {name} WHEN NOT EXISTS (SELECT 1 FROM games WHERE game_id=NEW.game_id AND NEW.team_id IN (home_team_id,away_team_id)) BEGIN SELECT RAISE(ABORT,\'team is not a game participant\'); END;')
    # Once a game is final, fill formerly unobserved fields but never silently
    # accept a different value for an already observed historical stat.
    for name, keys in [('player_game_boxes',['game_id','player_id']),('team_game_boxes',['game_id','team_id']),('game_period_scores',['game_id','team_id','period_index']),('game_state_observations',['game_id'])]:
        spec=TABLES[name]
        compare=[c.name for c in spec.columns if c.name not in {spec.key,'unit_id',*keys}]
        match=' AND '.join(f'old.{ident(k)}=NEW.{ident(k)}' for k in keys)
        diff=' OR '.join(f'(old.{ident(k)} IS NOT NULL AND NEW.{ident(k)} IS NOT NULL AND old.{ident(k)}<>NEW.{ident(k)})' for k in compare)
        # Scheduled/in-progress observations remain historical observations;
        # only a final observation is an immutable final-value baseline.
        final_old='old.is_final=1' if name=='game_state_observations' else 'EXISTS(SELECT 1 FROM game_state_observations fs WHERE fs.game_id=old.game_id AND fs.unit_id=old.unit_id AND fs.is_final=1)'
        out.append(f'CREATE TRIGGER "{name}_frozen_conflict" BEFORE INSERT ON {name} WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM {name} old WHERE {match} AND ({final_old}) AND ({diff})) BEGIN SELECT RAISE(ABORT,\'frozen game conflict; quarantine required\'); END;')
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
