-- NBA2K22 World Data: ISOLATED INITIAL ENGINEERING PROTOTYPE, v0.1.
-- One real game save => one independent SQLite FACT database file.
-- Synthetic fixture only. Not compatible with or a migration of database/schema.sql.
PRAGMA foreign_keys = ON;

CREATE TABLE saves (
  singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
  save_id TEXT NOT NULL UNIQUE,
  schema_version INTEGER NOT NULL CHECK (schema_version = 1),
  created_at TEXT NOT NULL,
  source_grade TEXT NOT NULL DEFAULT 'SYNTHETIC_ONLY'
    CHECK (source_grade = 'SYNTHETIC_ONLY')
);
CREATE TABLE seasons (
  season_id TEXT PRIMARY KEY,
  season_code TEXT NOT NULL UNIQUE
);
CREATE TABLE teams (
  team_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL
);
CREATE TABLE players (
  player_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  native_player_id TEXT,
  native_identity_status TEXT NOT NULL DEFAULT 'UNVERIFIED'
    CHECK(native_identity_status IN ('UNVERIFIED','VERIFIED','UNKNOWN'))
);
CREATE TABLE games (
  game_id TEXT PRIMARY KEY,
  season_id TEXT NOT NULL REFERENCES seasons(season_id),
  home_team_id TEXT NOT NULL REFERENCES teams(team_id),
  away_team_id TEXT NOT NULL REFERENCES teams(team_id),
  game_date TEXT,
  CHECK (home_team_id <> away_team_id)
);
CREATE TABLE capture_runs (
  run_id TEXT PRIMARY KEY,
  season_id TEXT NOT NULL REFERENCES seasons(season_id),
  observed_at TEXT NOT NULL,
  source_grade TEXT NOT NULL CHECK(source_grade = 'SYNTHETIC_FIXTURE')
);
CREATE TABLE capture_units (
  unit_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES capture_runs(run_id),
  source_key TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  unit_status TEXT NOT NULL CHECK(unit_status IN ('success','failed')),
  observed_at TEXT NOT NULL,
  UNIQUE(run_id,source_key)
);
CREATE TABLE source_artifacts (
  artifact_id TEXT PRIMARY KEY,
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  sha256 TEXT NOT NULL,
  payload_kind TEXT NOT NULL,
  restricted INTEGER NOT NULL DEFAULT 0 CHECK(restricted IN (0,1))
);
CREATE TABLE native_fields (
  field_id TEXT PRIMARY KEY,
  source_group TEXT NOT NULL,
  native_key TEXT NOT NULL,
  ui_label TEXT,
  evidence_grade TEXT NOT NULL DEFAULT 'RESEARCH_LEAD'
    CHECK(evidence_grade IN ('RESEARCH_LEAD','UNKNOWN','NATIVE_VERIFIED')),
  visibility TEXT NOT NULL DEFAULT 'UNKNOWN'
    CHECK(visibility IN ('GM_PUBLIC','RESTRICTED','UNKNOWN')),
  min_native_value INTEGER,
  max_native_value INTEGER,
  CHECK(min_native_value IS NULL OR max_native_value IS NULL OR min_native_value<=max_native_value)
);
CREATE TABLE field_gaps (
  gap_id TEXT PRIMARY KEY,
  field_id TEXT REFERENCES native_fields(field_id),
  affected_domain TEXT NOT NULL,
  reason TEXT NOT NULL,
  impact TEXT NOT NULL,
  human_exception_ref TEXT
);
CREATE TABLE game_state_observations (
  observation_id TEXT PRIMARY KEY,
  game_id TEXT NOT NULL REFERENCES games(game_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  status_code TEXT NOT NULL,
  home_points INTEGER CHECK(home_points IS NULL OR home_points>=0),
  away_points INTEGER CHECK(away_points IS NULL OR away_points>=0),
  UNIQUE(game_id,unit_id)
);
CREATE TABLE player_game_boxes (
  box_id TEXT PRIMARY KEY,
  game_id TEXT NOT NULL REFERENCES games(game_id),
  player_id TEXT NOT NULL REFERENCES players(player_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  points INTEGER CHECK(points IS NULL OR points>=0),
  fg_made INTEGER CHECK(fg_made IS NULL OR fg_made>=0),
  fg_attempted INTEGER CHECK(fg_attempted IS NULL OR fg_attempted>=0),
  CHECK(fg_made IS NULL OR fg_attempted IS NULL OR fg_made<=fg_attempted),
  UNIQUE(game_id,player_id,unit_id)
);
CREATE TABLE player_attribute_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL REFERENCES players(player_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  overall_raw INTEGER,
  shot_close_raw INTEGER,
  driving_layup_raw INTEGER,
  UNIQUE(player_id,unit_id)
);
CREATE TABLE player_tendency_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL REFERENCES players(player_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  shot_tendency_raw INTEGER,
  drive_tendency_raw INTEGER,
  UNIQUE(player_id,unit_id)
);
CREATE TABLE player_badge_values (
  badge_observation_id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL REFERENCES players(player_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  badge_key TEXT NOT NULL,
  native_code INTEGER,
  tier_label TEXT,
  owned_state TEXT NOT NULL CHECK(owned_state IN ('owned','not_owned','unknown')),
  UNIQUE(player_id,unit_id,badge_key)
);
CREATE TABLE player_play_type_slots (
  play_type_observation_id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL REFERENCES players(player_id),
  unit_id TEXT NOT NULL REFERENCES capture_units(unit_id),
  slot_index INTEGER NOT NULL CHECK(slot_index>=0),
  native_play_code TEXT,
  UNIQUE(player_id,unit_id,slot_index)
);

CREATE INDEX idx_capture_units_run ON capture_units(run_id);
CREATE INDEX idx_game_boxes_game ON player_game_boxes(game_id,unit_id);
CREATE INDEX idx_attributes_player ON player_attribute_snapshots(player_id,unit_id);
CREATE INDEX idx_badges_player ON player_badge_values(player_id,unit_id);
CREATE INDEX idx_playtypes_player ON player_play_type_slots(player_id,unit_id);
CREATE INDEX idx_game_states_game ON game_state_observations(game_id,unit_id);

-- These views have no hidden Potential column. Restricted fields are never
-- written to this early GM-facing prototype. SQLite has no row-level ACLs.
CREATE VIEW gm_player_observations AS
 SELECT p.player_id,p.display_name,a.snapshot_id,a.unit_id,u.observed_at,
        a.overall_raw,a.shot_close_raw,a.driving_layup_raw
 FROM players p JOIN player_attribute_snapshots a USING(player_id)
 JOIN capture_units u USING(unit_id) WHERE u.unit_status='success';
CREATE VIEW gm_game_box AS
 SELECT g.game_id,g.season_id,g.game_date,p.player_id,p.display_name,
        b.team_id,b.points,b.fg_made,b.fg_attempted,u.observed_at
 FROM player_game_boxes b JOIN games g USING(game_id)
 JOIN players p USING(player_id) JOIN capture_units u USING(unit_id)
 WHERE u.unit_status='success';

-- Prevent later edits/deletes of accepted observations and their capture identity.
-- This protects ordinary SQL paths within this prototype; a file owner may still
-- replace the entire DB, which remains an operational backup/access concern.
CREATE TRIGGER saves_no_update BEFORE UPDATE ON saves BEGIN SELECT RAISE(ABORT,'save identity is immutable'); END;
CREATE TRIGGER saves_no_delete BEFORE DELETE ON saves BEGIN SELECT RAISE(ABORT,'save identity is immutable'); END;
CREATE TRIGGER units_no_update BEFORE UPDATE ON capture_units BEGIN SELECT RAISE(ABORT,'capture unit is immutable'); END;
CREATE TRIGGER units_no_delete BEFORE DELETE ON capture_units BEGIN SELECT RAISE(ABORT,'capture unit is immutable'); END;

-- Observations are only valid when the source consistency unit succeeded.
CREATE TRIGGER game_state_obser_require_success BEFORE INSERT ON game_state_observations
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER game_state_obser_immutable_update BEFORE UPDATE ON game_state_observations
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER game_state_obser_immutable_delete BEFORE DELETE ON game_state_observations
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_game_boxe_require_success BEFORE INSERT ON player_game_boxes
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER player_game_boxe_immutable_update BEFORE UPDATE ON player_game_boxes
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_game_boxe_immutable_delete BEFORE DELETE ON player_game_boxes
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_attribute_require_success BEFORE INSERT ON player_attribute_snapshots
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER player_attribute_immutable_update BEFORE UPDATE ON player_attribute_snapshots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_attribute_immutable_delete BEFORE DELETE ON player_attribute_snapshots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_tendency__require_success BEFORE INSERT ON player_tendency_snapshots
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER player_tendency__immutable_update BEFORE UPDATE ON player_tendency_snapshots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_tendency__immutable_delete BEFORE DELETE ON player_tendency_snapshots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_badge_val_require_success BEFORE INSERT ON player_badge_values
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER player_badge_val_immutable_update BEFORE UPDATE ON player_badge_values
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_badge_val_immutable_delete BEFORE DELETE ON player_badge_values
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_play_type_require_success BEFORE INSERT ON player_play_type_slots
WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success')
BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;
CREATE TRIGGER player_play_type_immutable_update BEFORE UPDATE ON player_play_type_slots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
CREATE TRIGGER player_play_type_immutable_delete BEFORE DELETE ON player_play_type_slots
BEGIN SELECT RAISE(ABORT,'observation is immutable'); END;
