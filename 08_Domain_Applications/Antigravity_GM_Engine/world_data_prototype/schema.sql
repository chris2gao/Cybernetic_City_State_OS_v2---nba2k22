-- Generated: approved catalog + explicit game/finalization/source staging and team state observations.
PRAGMA foreign_keys=ON;

CREATE TABLE "saves" (
  "singleton" INTEGER NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL,
  "schema_version" INTEGER NOT NULL CHECK (schema_version=17),
  "created_at" TEXT NOT NULL,
  "source_grade" TEXT NOT NULL DEFAULT 'SYNTHETIC_ONLY',
  "game_build" TEXT,
  "native_save_fingerprint" TEXT,
  UNIQUE ("save_id"),
  CHECK (singleton=1)
) STRICT;

CREATE TRIGGER "saves_no_update" BEFORE UPDATE ON "saves" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "saves_no_delete" BEFORE DELETE ON "saves" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "seasons" (
  "season_id" TEXT NOT NULL PRIMARY KEY,
  "season_code" TEXT NOT NULL,
  "save_id" TEXT REFERENCES saves(save_id) ON DELETE RESTRICT,
  UNIQUE ("season_code")
) STRICT;

CREATE INDEX "idx_seasons_save_id" ON "seasons" ("save_id");

CREATE TRIGGER "seasons_no_update" BEFORE UPDATE ON "seasons" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "seasons_no_delete" BEFORE DELETE ON "seasons" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "teams" (
  "team_id" TEXT NOT NULL PRIMARY KEY,
  "display_name" TEXT,
  "native_team_id" TEXT,
  "native_identity_status" TEXT DEFAULT 'UNKNOWN'
) STRICT;

CREATE TRIGGER "teams_no_update" BEFORE UPDATE ON "teams" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "teams_no_delete" BEFORE DELETE ON "teams" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "players" (
  "player_id" TEXT NOT NULL PRIMARY KEY,
  "display_name" TEXT NOT NULL,
  "native_player_id" TEXT,
  "native_identity_status" TEXT DEFAULT 'UNVERIFIED' CHECK (native_identity_status IN ('UNKNOWN','UNVERIFIED','VERIFIED'))
) STRICT;

CREATE TRIGGER "players_no_update" BEFORE UPDATE ON "players" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "players_no_delete" BEFORE DELETE ON "players" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "staff_members" (
  "staff_id" TEXT NOT NULL PRIMARY KEY,
  "display_name" TEXT,
  "native_staff_id" TEXT,
  "identity_state" TEXT DEFAULT 'UNKNOWN'
) STRICT;

CREATE TRIGGER "staff_members_no_update" BEFORE UPDATE ON "staff_members" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_members_no_delete" BEFORE DELETE ON "staff_members" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "games" (
  "game_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "home_team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "away_team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "game_date" TEXT,
  "native_game_id" TEXT,
  "game_kind" TEXT,
  CHECK (home_team_id<>away_team_id)
) STRICT;

CREATE INDEX "idx_games_season_id" ON "games" ("season_id");

CREATE INDEX "idx_games_home_team_id" ON "games" ("home_team_id");

CREATE INDEX "idx_games_away_team_id" ON "games" ("away_team_id");

CREATE TRIGGER "games_no_update" BEFORE UPDATE ON "games" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "games_no_delete" BEFORE DELETE ON "games" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "capture_runs" (
  "run_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "observed_at" TEXT NOT NULL,
  "source_grade" TEXT NOT NULL CHECK (source_grade IN ('SYNTHETIC_FIXTURE','RESEARCH_FIXTURE','LIVE_READ')),
  "game_date" TEXT,
  "decoder_version" TEXT,
  "save_binding_ref" TEXT,
  "refresh_family" TEXT CHECK (refresh_family IN ('RECORD_BOOK','NATIVE_HONOR_STATS','LEAGUE_HISTORY_AWARDS')),
  "refresh_period_year" INTEGER CHECK (refresh_period_year BETWEEN 1 AND 9999),
  CHECK ((refresh_family IS NULL)=(refresh_period_year IS NULL))
) STRICT;

CREATE INDEX "idx_capture_runs_season_id" ON "capture_runs" ("season_id");

CREATE TRIGGER "capture_runs_no_update" BEFORE UPDATE ON "capture_runs" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "capture_runs_no_delete" BEFORE DELETE ON "capture_runs" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "capture_units" (
  "unit_id" TEXT NOT NULL PRIMARY KEY,
  "run_id" TEXT NOT NULL REFERENCES capture_runs(run_id) ON DELETE RESTRICT,
  "source_key" TEXT NOT NULL,
  "payload_sha256" TEXT NOT NULL,
  "unit_status" TEXT NOT NULL CHECK (unit_status IN ('success','failed')),
  "observed_at" TEXT NOT NULL,
  "effective_at" TEXT,
  "layout_version" TEXT,
  "completeness" TEXT DEFAULT 'PARTIAL' CHECK (completeness IN ('COMPLETE','PARTIAL','FAILED')),
  UNIQUE ("run_id","source_key")
) STRICT;

CREATE INDEX "idx_capture_units_run_id" ON "capture_units" ("run_id");

CREATE TRIGGER "capture_units_no_update" BEFORE UPDATE ON "capture_units" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "capture_units_no_delete" BEFORE DELETE ON "capture_units" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "source_artifacts" (
  "artifact_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "sha256" TEXT NOT NULL,
  "payload_kind" TEXT NOT NULL,
  "restricted" INTEGER NOT NULL DEFAULT 1 CHECK (restricted IN (0,1)),
  "source_version" TEXT,
  "payload_ref" TEXT,
  "byte_count" INTEGER CHECK (byte_count>=0)
) STRICT;

CREATE INDEX "idx_source_artifacts_unit_id" ON "source_artifacts" ("unit_id");

CREATE TRIGGER "source_artifacts_no_update" BEFORE UPDATE ON "source_artifacts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "source_artifacts_no_delete" BEFORE DELETE ON "source_artifacts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "source_artifacts_successful_unit" BEFORE INSERT ON "source_artifacts" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_fields" (
  "field_id" TEXT NOT NULL PRIMARY KEY,
  "source_group" TEXT NOT NULL,
  "native_key" TEXT NOT NULL,
  "ui_label" TEXT,
  "evidence_grade" TEXT NOT NULL DEFAULT 'UNKNOWN',
  "visibility" TEXT NOT NULL DEFAULT 'UNKNOWN',
  "min_native_value" INTEGER,
  "max_native_value" INTEGER,
  "table_name" TEXT,
  "column_name" TEXT,
  "codec" TEXT,
  "layout_version" TEXT,
  "source_ref" TEXT,
  "unit" TEXT,
  "legal_range_state" TEXT DEFAULT 'UNKNOWN',
  "null_meaning" TEXT DEFAULT 'NOT_OBSERVED',
  CHECK (min_native_value IS NULL OR max_native_value IS NULL OR min_native_value<=max_native_value)
) STRICT;

CREATE TRIGGER "native_fields_no_update" BEFORE UPDATE ON "native_fields" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_fields_no_delete" BEFORE DELETE ON "native_fields" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "field_gaps" (
  "gap_id" TEXT NOT NULL PRIMARY KEY,
  "field_id" TEXT REFERENCES native_fields(field_id) ON DELETE RESTRICT,
  "affected_domain" TEXT NOT NULL,
  "reason" TEXT NOT NULL,
  "impact" TEXT NOT NULL,
  "human_exception_ref" TEXT,
  "target_field" TEXT,
  "alternative" TEXT,
  "status" TEXT DEFAULT 'OPEN' CHECK (status IN ('OPEN','RESOLVED','HUMAN_EXCEPTION'))
) STRICT;

CREATE INDEX "idx_field_gaps_field_id" ON "field_gaps" ("field_id");

CREATE TRIGGER "field_gaps_no_update" BEFORE UPDATE ON "field_gaps" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "field_gaps_no_delete" BEFORE DELETE ON "field_gaps" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "fact_conflicts" (
  "conflict_id" TEXT NOT NULL PRIMARY KEY,
  "object_ref" TEXT NOT NULL,
  "evidence_a" TEXT NOT NULL,
  "evidence_b" TEXT NOT NULL,
  "review_status" TEXT DEFAULT 'PENDING_HUMAN',
  "human_decision_ref" TEXT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX "idx_fact_conflicts_unit_id" ON "fact_conflicts" ("unit_id");

CREATE TRIGGER "fact_conflicts_no_update" BEFORE UPDATE ON "fact_conflicts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "fact_conflicts_no_delete" BEFORE DELETE ON "fact_conflicts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "fact_conflicts_successful_unit" BEFORE INSERT ON "fact_conflicts" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_seasons" (
  "team_season_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "conference" TEXT,
  "division" TEXT,
  "team_name" TEXT,
  UNIQUE ("team_id","season_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_seasons_team_id" ON "team_seasons" ("team_id");

CREATE INDEX "idx_team_seasons_season_id" ON "team_seasons" ("season_id");

CREATE INDEX "idx_team_seasons_unit_id" ON "team_seasons" ("unit_id");

CREATE TRIGGER "team_seasons_no_update" BEFORE UPDATE ON "team_seasons" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_seasons_no_delete" BEFORE DELETE ON "team_seasons" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_seasons_successful_unit" BEFORE INSERT ON "team_seasons" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "roster_memberships" (
  "membership_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "roster_status" TEXT,
  "native_roster_slot" INTEGER,
  UNIQUE ("player_id","unit_id")
) STRICT;

CREATE INDEX "idx_roster_memberships_player_id" ON "roster_memberships" ("player_id");

CREATE INDEX "idx_roster_memberships_team_id" ON "roster_memberships" ("team_id");

CREATE INDEX "idx_roster_memberships_unit_id" ON "roster_memberships" ("unit_id");

CREATE TRIGGER "roster_memberships_no_update" BEFORE UPDATE ON "roster_memberships" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "roster_memberships_no_delete" BEFORE DELETE ON "roster_memberships" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "roster_memberships_successful_unit" BEFORE INSERT ON "roster_memberships" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_rotation_slots" (
  "slot_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL CHECK (slot_index>=0),
  "planned_minutes" INTEGER,
  "role_code" TEXT,
  UNIQUE ("team_id","unit_id","slot_index")
) STRICT;

CREATE INDEX "idx_team_rotation_slots_team_id" ON "team_rotation_slots" ("team_id");

CREATE INDEX "idx_team_rotation_slots_player_id" ON "team_rotation_slots" ("player_id");

CREATE INDEX "idx_team_rotation_slots_unit_id" ON "team_rotation_slots" ("unit_id");

CREATE TRIGGER "team_rotation_slots_no_update" BEFORE UPDATE ON "team_rotation_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_rotation_slots_no_delete" BEFORE DELETE ON "team_rotation_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_rotation_slots_successful_unit" BEFORE INSERT ON "team_rotation_slots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_player_sources" (
  "player_source_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_player_index" INTEGER NOT NULL CHECK (source_player_index>=0),
  "native_unique_id_raw" INTEGER CHECK (native_unique_id_raw BETWEEN 0 AND 65535),
  "preserved_id_raw" INTEGER CHECK (preserved_id_raw BETWEEN 0 AND 4294967295),
  "observed_name" TEXT,
  "name_status" TEXT,
  "native_team_id" INTEGER,
  "current_core_roster_status" TEXT,
  "current_roster_slot" INTEGER,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "canonical_link_status" TEXT,
  UNIQUE ("unit_id","source_player_index")
) STRICT;

CREATE INDEX "idx_native_player_sources_unit_id" ON "native_player_sources" ("unit_id");

CREATE INDEX "idx_native_player_sources_player_id" ON "native_player_sources" ("player_id");

CREATE TRIGGER "native_player_sources_no_update" BEFORE UPDATE ON "native_player_sources" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_sources_no_delete" BEFORE DELETE ON "native_player_sources" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_sources_successful_unit" BEFORE INSERT ON "native_player_sources" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_college_observations" (
  "college_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_object_index" INTEGER NOT NULL CHECK (source_object_index>=0),
  "native_label" TEXT,
  "name_encoding_status" TEXT,
  "localized_name_crc_raw" INTEGER CHECK (localized_name_crc_raw BETWEEN 0 AND 4294967295),
  "appearance_group_raw" INTEGER CHECK (appearance_group_raw BETWEEN 0 AND 65535),
  "appearance_group_label" TEXT,
  "region_id_raw" INTEGER CHECK (region_id_raw BETWEEN 0 AND 127),
  "college_id_raw" INTEGER CHECK (college_id_raw BETWEEN 0 AND 2047),
  "is_high_school_raw" INTEGER CHECK (is_high_school_raw IN (0,1)),
  "source_scope_status" TEXT,
  UNIQUE ("unit_id","source_object_index")
) STRICT;

CREATE INDEX "idx_native_college_observations_unit_id" ON "native_college_observations" ("unit_id");

CREATE TRIGGER "native_college_observations_no_update" BEFORE UPDATE ON "native_college_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_college_observations_no_delete" BEFORE DELETE ON "native_college_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_college_observations_successful_unit" BEFORE INSERT ON "native_college_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_vitals_observations" (
  "observation_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "first_name" TEXT,
  "last_name" TEXT,
  "nickname" TEXT,
  "birth_date" TEXT,
  "college" TEXT,
  "country" TEXT,
  "primary_position" TEXT,
  "secondary_position" TEXT,
  "handedness" TEXT,
  "jersey_number" TEXT,
  "height_raw" INTEGER,
  "weight_raw" INTEGER,
  "age_raw" INTEGER,
  "years_pro" INTEGER,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "birth_year_raw" INTEGER CHECK (birth_year_raw BETWEEN 0 AND 4095),
  "birth_month_raw" INTEGER CHECK (birth_month_raw BETWEEN 0 AND 15),
  "birth_day_raw" INTEGER CHECK (birth_day_raw BETWEEN 0 AND 31),
  "primary_position_raw" INTEGER CHECK (primary_position_raw BETWEEN 0 AND 7),
  "secondary_position_raw" INTEGER CHECK (secondary_position_raw BETWEEN 0 AND 7),
  "tertiary_position_raw" INTEGER CHECK (tertiary_position_raw BETWEEN 0 AND 7),
  "best_hand_raw" INTEGER CHECK (best_hand_raw BETWEEN 0 AND 1),
  "best_dunk_hand_raw" INTEGER CHECK (best_dunk_hand_raw BETWEEN 0 AND 3),
  "jersey_number_raw" INTEGER CHECK (jersey_number_raw BETWEEN 0 AND 127),
  "weight_real" REAL,
  "weight_value_text" TEXT,
  "weight_value_status" TEXT,
  "wingspan_raw" INTEGER CHECK (wingspan_raw BETWEEN 0 AND 32767),
  "height_cm_native_derived" REAL,
  "wingspan_cm_native_derived" REAL,
  "appearance_status" TEXT,
  "tertiary_position" TEXT,
  "best_dunk_hand_label" TEXT,
  "native_college_obs_id" TEXT REFERENCES native_college_observations(college_observation_id) ON DELETE RESTRICT,
  "college_source_status" TEXT,
  "college_country_semantics_status" TEXT,
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_vitals_observations_player_id" ON "player_vitals_observations" ("player_id");

CREATE INDEX "idx_player_vitals_observations_unit_id" ON "player_vitals_observations" ("unit_id");

CREATE INDEX "idx_player_vitals_observations_source_player_id" ON "player_vitals_observations" ("source_player_id");

CREATE INDEX "idx_player_vitals_observations_native_college_obs_id" ON "player_vitals_observations" ("native_college_obs_id");

CREATE TRIGGER "player_vitals_observations_no_update" BEFORE UPDATE ON "player_vitals_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_vitals_observations_no_delete" BEFORE DELETE ON "player_vitals_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_vitals_observations_successful_unit" BEFORE INSERT ON "player_vitals_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_attribute_snapshots" (
  "snapshot_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "overall_raw" INTEGER,
  "driving_layup_raw" INTEGER,
  "post_fadeaway_raw" INTEGER,
  "post_hook_raw" INTEGER,
  "post_moves_raw" INTEGER,
  "draw_foul_raw" INTEGER,
  "shot_close_raw" INTEGER,
  "mid_range_shot_raw" INTEGER,
  "three_point_shot_raw" INTEGER,
  "free_throw_raw" INTEGER,
  "ball_control_raw" INTEGER,
  "passing_iq_raw" INTEGER,
  "passing_accuracy_raw" INTEGER,
  "offensive_rebound_raw" INTEGER,
  "standing_dunk_raw" INTEGER,
  "driving_dunk_raw" INTEGER,
  "shot_iq_raw" INTEGER,
  "passing_vision_raw" INTEGER,
  "hands_raw" INTEGER,
  "defensive_rebound_raw" INTEGER,
  "interior_defense_raw" INTEGER,
  "perimeter_defense_raw" INTEGER,
  "block_raw" INTEGER,
  "steal_raw" INTEGER,
  "shot_contest_raw" INTEGER,
  "lateral_quickness_raw" INTEGER,
  "speed_raw" INTEGER,
  "speed_with_ball_raw" INTEGER,
  "acceleration_raw" INTEGER,
  "vertical_raw" INTEGER,
  "strength_raw" INTEGER,
  "stamina_raw" INTEGER,
  "hustle_raw" INTEGER,
  "head_durability_raw" INTEGER,
  "neck_durability_raw" INTEGER,
  "back_durability_raw" INTEGER,
  "left_shoulder_durability_raw" INTEGER,
  "right_shoulder_durability_raw" INTEGER,
  "left_elbow_durability_raw" INTEGER,
  "right_elbow_durability_raw" INTEGER,
  "left_hip_durability_raw" INTEGER,
  "right_hip_durability_raw" INTEGER,
  "left_knee_durability_raw" INTEGER,
  "right_knee_durability_raw" INTEGER,
  "left_ankle_durability_raw" INTEGER,
  "right_ankle_durability_raw" INTEGER,
  "left_foot_durability_raw" INTEGER,
  "right_foot_durability_raw" INTEGER,
  "misc_durability_raw" INTEGER,
  "pass_perception_raw" INTEGER,
  "defensive_consistency_raw" INTEGER,
  "help_defensive_iq_raw" INTEGER,
  "offensive_consistency_raw" INTEGER,
  "pick_and_roll_defensive_iq_raw" INTEGER,
  "intangibles_raw" INTEGER,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "emotion_raw" INTEGER CHECK (emotion_raw BETWEEN 0 AND 255),
  "reaction_time_raw" INTEGER CHECK (reaction_time_raw BETWEEN 0 AND 255),
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_attribute_snapshots_player_id" ON "player_attribute_snapshots" ("player_id");

CREATE INDEX "idx_player_attribute_snapshots_unit_id" ON "player_attribute_snapshots" ("unit_id");

CREATE INDEX "idx_player_attribute_snapshots_source_player_id" ON "player_attribute_snapshots" ("source_player_id");

CREATE TRIGGER "player_attribute_snapshots_no_update" BEFORE UPDATE ON "player_attribute_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_attribute_snapshots_no_delete" BEFORE DELETE ON "player_attribute_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_attribute_snapshots_successful_unit" BEFORE INSERT ON "player_attribute_snapshots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_tendency_snapshots" (
  "snapshot_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "shot_tendency_raw" INTEGER,
  "drive_tendency_raw" INTEGER,
  "driving_layup_tendency_raw" INTEGER,
  "standing_dunk_tendency_raw" INTEGER,
  "driving_dunk_tendency_raw" INTEGER,
  "flashy_dunk_tendency_raw" INTEGER,
  "alley_oop_tendency_raw" INTEGER,
  "putback_tendency_raw" INTEGER,
  "crash_tendency_raw" INTEGER,
  "spin_layup_tendency_raw" INTEGER,
  "hop_step_layup_tendency_raw" INTEGER,
  "euro_step_layup_tendency_raw" INTEGER,
  "floater_tendency_raw" INTEGER,
  "step_through_shot_tendency_raw" INTEGER,
  "shot_under_basket_tendency_raw" INTEGER,
  "shot_close_tendency_raw" INTEGER,
  "shot_mid_range_tendency_raw" INTEGER,
  "spot_up_shot_mid_range_raw" INTEGER,
  "off_screen_shot_mid_range_raw" INTEGER,
  "shot_three_tendency_raw" INTEGER,
  "spot_up_shot_three_raw" INTEGER,
  "off_screen_shot_three_raw" INTEGER,
  "contested_jumper_three_raw" INTEGER,
  "contested_jumper_mid_range_raw" INTEGER,
  "stepback_jumper_three_raw" INTEGER,
  "stepback_jumper_mid_range_raw" INTEGER,
  "spin_jumper_tendency_raw" INTEGER,
  "transition_pull_up_three_raw" INTEGER,
  "drive_pull_up_three_raw" INTEGER,
  "drive_pull_up_mid_range_raw" INTEGER,
  "spot_up_drive_tendency_raw" INTEGER,
  "off_screen_drive_tendency_raw" INTEGER,
  "attack_strong_on_drive_raw" INTEGER,
  "dish_to_open_man_tendency_raw" INTEGER,
  "touches_tendency_raw" INTEGER,
  "post_up_tendency_raw" INTEGER,
  "roll_vs_pop_tendency_raw" INTEGER,
  "transition_spot_up_raw" INTEGER,
  "play_discipline_tendency_raw" INTEGER,
  "flashy_pass_tendency_raw" INTEGER,
  "alley_oop_pass_tendency_raw" INTEGER,
  "pass_interception_tendency_raw" INTEGER,
  "take_charge_tendency_raw" INTEGER,
  "on_ball_steal_tendency_raw" INTEGER,
  "contest_shot_tendency_raw" INTEGER,
  "block_shot_tendency_raw" INTEGER,
  "foul_tendency_raw" INTEGER,
  "hard_foul_tendency_raw" INTEGER,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "shot_area_close_left_tendency_raw" INTEGER CHECK (shot_area_close_left_tendency_raw BETWEEN 0 AND 255),
  "shot_area_close_center_tendency_raw" INTEGER CHECK (shot_area_close_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_close_right_tendency_raw" INTEGER CHECK (shot_area_close_right_tendency_raw BETWEEN 0 AND 255),
  "shot_area_medium_left_tendency_raw" INTEGER CHECK (shot_area_medium_left_tendency_raw BETWEEN 0 AND 255),
  "shot_area_medium_left_center_tendency_raw" INTEGER CHECK (shot_area_medium_left_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_medium_center_tendency_raw" INTEGER CHECK (shot_area_medium_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_medium_right_center_tendency_raw" INTEGER CHECK (shot_area_medium_right_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_medium_right_tendency_raw" INTEGER CHECK (shot_area_medium_right_tendency_raw BETWEEN 0 AND 255),
  "shot_area_three_left_tendency_raw" INTEGER CHECK (shot_area_three_left_tendency_raw BETWEEN 0 AND 255),
  "shot_area_three_left_center_tendency_raw" INTEGER CHECK (shot_area_three_left_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_three_center_tendency_raw" INTEGER CHECK (shot_area_three_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_three_right_center_tendency_raw" INTEGER CHECK (shot_area_three_right_center_tendency_raw BETWEEN 0 AND 255),
  "shot_area_three_right_tendency_raw" INTEGER CHECK (shot_area_three_right_tendency_raw BETWEEN 0 AND 255),
  "use_glass_tendency_raw" INTEGER CHECK (use_glass_tendency_raw BETWEEN 0 AND 255),
  "drive_right_tendency_raw" INTEGER CHECK (drive_right_tendency_raw BETWEEN 0 AND 255),
  "triple_threat_pump_fake_tendency_raw" INTEGER CHECK (triple_threat_pump_fake_tendency_raw BETWEEN 0 AND 255),
  "triple_threat_jab_step_tendency_raw" INTEGER CHECK (triple_threat_jab_step_tendency_raw BETWEEN 0 AND 255),
  "triple_threat_nothing_tendency_raw" INTEGER CHECK (triple_threat_nothing_tendency_raw BETWEEN 0 AND 255),
  "triple_threat_shoot_tendency_raw" INTEGER CHECK (triple_threat_shoot_tendency_raw BETWEEN 0 AND 255),
  "setup_sizeup_tendency_raw" INTEGER CHECK (setup_sizeup_tendency_raw BETWEEN 0 AND 255),
  "setup_hesitation_tendency_raw" INTEGER CHECK (setup_hesitation_tendency_raw BETWEEN 0 AND 255),
  "setup_nothing_tendency_raw" INTEGER CHECK (setup_nothing_tendency_raw BETWEEN 0 AND 255),
  "dribble_crossover_tendency_raw" INTEGER CHECK (dribble_crossover_tendency_raw BETWEEN 0 AND 255),
  "dribble_spin_tendency_raw" INTEGER CHECK (dribble_spin_tendency_raw BETWEEN 0 AND 255),
  "dribble_step_back_tendency_raw" INTEGER CHECK (dribble_step_back_tendency_raw BETWEEN 0 AND 255),
  "dribble_half_spin_tendency_raw" INTEGER CHECK (dribble_half_spin_tendency_raw BETWEEN 0 AND 255),
  "dribble_double_cross_tendency_raw" INTEGER CHECK (dribble_double_cross_tendency_raw BETWEEN 0 AND 255),
  "dribble_behind_back_tendency_raw" INTEGER CHECK (dribble_behind_back_tendency_raw BETWEEN 0 AND 255),
  "dribble_hesitation_tendency_raw" INTEGER CHECK (dribble_hesitation_tendency_raw BETWEEN 0 AND 255),
  "dribble_in_and_out_tendency_raw" INTEGER CHECK (dribble_in_and_out_tendency_raw BETWEEN 0 AND 255),
  "dribble_nothing_tendency_raw" INTEGER CHECK (dribble_nothing_tendency_raw BETWEEN 0 AND 255),
  "iso_vs_elite_tendency_raw" INTEGER CHECK (iso_vs_elite_tendency_raw BETWEEN 0 AND 255),
  "iso_vs_good_tendency_raw" INTEGER CHECK (iso_vs_good_tendency_raw BETWEEN 0 AND 255),
  "iso_vs_average_tendency_raw" INTEGER CHECK (iso_vs_average_tendency_raw BETWEEN 0 AND 255),
  "iso_vs_poor_tendency_raw" INTEGER CHECK (iso_vs_poor_tendency_raw BETWEEN 0 AND 255),
  "post_shimmy_shot_tendency_raw" INTEGER CHECK (post_shimmy_shot_tendency_raw BETWEEN 0 AND 255),
  "post_face_up_tendency_raw" INTEGER CHECK (post_face_up_tendency_raw BETWEEN 0 AND 255),
  "post_back_down_tendency_raw" INTEGER CHECK (post_back_down_tendency_raw BETWEEN 0 AND 255),
  "post_aggressive_back_down_tendency_raw" INTEGER CHECK (post_aggressive_back_down_tendency_raw BETWEEN 0 AND 255),
  "post_shoot_tendency_raw" INTEGER CHECK (post_shoot_tendency_raw BETWEEN 0 AND 255),
  "post_hook_left_tendency_raw" INTEGER CHECK (post_hook_left_tendency_raw BETWEEN 0 AND 255),
  "post_hook_right_tendency_raw" INTEGER CHECK (post_hook_right_tendency_raw BETWEEN 0 AND 255),
  "post_fade_left_tendency_raw" INTEGER CHECK (post_fade_left_tendency_raw BETWEEN 0 AND 255),
  "post_fade_right_tendency_raw" INTEGER CHECK (post_fade_right_tendency_raw BETWEEN 0 AND 255),
  "post_up_and_under_tendency_raw" INTEGER CHECK (post_up_and_under_tendency_raw BETWEEN 0 AND 255),
  "post_hop_shot_tendency_raw" INTEGER CHECK (post_hop_shot_tendency_raw BETWEEN 0 AND 255),
  "post_stepback_shot_tendency_raw" INTEGER CHECK (post_stepback_shot_tendency_raw BETWEEN 0 AND 255),
  "post_drive_tendency_raw" INTEGER CHECK (post_drive_tendency_raw BETWEEN 0 AND 255),
  "post_spin_tendency_raw" INTEGER CHECK (post_spin_tendency_raw BETWEEN 0 AND 255),
  "post_drop_step_outside_tendency_raw" INTEGER CHECK (post_drop_step_outside_tendency_raw BETWEEN 0 AND 255),
  "post_drop_step_inside_tendency_raw" INTEGER CHECK (post_drop_step_inside_tendency_raw BETWEEN 0 AND 255),
  "is_play_initiator_raw" INTEGER CHECK (is_play_initiator_raw IN (0,1)),
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_tendency_snapshots_player_id" ON "player_tendency_snapshots" ("player_id");

CREATE INDEX "idx_player_tendency_snapshots_unit_id" ON "player_tendency_snapshots" ("unit_id");

CREATE INDEX "idx_player_tendency_snapshots_source_player_id" ON "player_tendency_snapshots" ("source_player_id");

CREATE TRIGGER "player_tendency_snapshots_no_update" BEFORE UPDATE ON "player_tendency_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_tendency_snapshots_no_delete" BEFORE DELETE ON "player_tendency_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_tendency_snapshots_successful_unit" BEFORE INSERT ON "player_tendency_snapshots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_badge_values" (
  "badge_observation_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "badge_key" TEXT NOT NULL,
  "native_code" INTEGER,
  "tier_label" TEXT,
  "owned_state" TEXT NOT NULL CHECK (owned_state IN ('owned','not_owned','unknown')),
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "native_field_id" TEXT REFERENCES native_fields(field_id) ON DELETE RESTRICT,
  "native_badge_id" INTEGER CHECK (native_badge_id BETWEEN 1 AND 98),
  "native_kind" TEXT CHECK (native_kind IN ('BOOLEAN','LEVEL')),
  "native_level_status" TEXT,
  UNIQUE ("player_id","unit_id","badge_key"),
  UNIQUE ("source_player_id","unit_id","badge_key"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_badge_values_player_id" ON "player_badge_values" ("player_id");

CREATE INDEX "idx_player_badge_values_unit_id" ON "player_badge_values" ("unit_id");

CREATE INDEX "idx_player_badge_values_source_player_id" ON "player_badge_values" ("source_player_id");

CREATE INDEX "idx_player_badge_values_native_field_id" ON "player_badge_values" ("native_field_id");

CREATE TRIGGER "player_badge_values_no_update" BEFORE UPDATE ON "player_badge_values" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_badge_values_no_delete" BEFORE DELETE ON "player_badge_values" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_badge_values_successful_unit" BEFORE INSERT ON "player_badge_values" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_play_type_slots" (
  "play_type_observation_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL CHECK (slot_index>=0),
  "native_play_code" TEXT,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "native_play_label" TEXT,
  UNIQUE ("player_id","unit_id","slot_index"),
  UNIQUE ("source_player_id","unit_id","slot_index"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_play_type_slots_player_id" ON "player_play_type_slots" ("player_id");

CREATE INDEX "idx_player_play_type_slots_unit_id" ON "player_play_type_slots" ("unit_id");

CREATE INDEX "idx_player_play_type_slots_source_player_id" ON "player_play_type_slots" ("source_player_id");

CREATE TRIGGER "player_play_type_slots_no_update" BEFORE UPDATE ON "player_play_type_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_play_type_slots_no_delete" BEFORE DELETE ON "player_play_type_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_play_type_slots_successful_unit" BEFORE INSERT ON "player_play_type_slots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_contract_observations" (
  "contract_obs_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "bird_years_raw" INTEGER CHECK (bird_years_raw BETWEEN 0 AND 31),
  "original_contract_years_raw" INTEGER CHECK (original_contract_years_raw BETWEEN 0 AND 7),
  "years_left_on_contract_raw" INTEGER CHECK (years_left_on_contract_raw BETWEEN 0 AND 31),
  "contract_option_raw" INTEGER CHECK (contract_option_raw BETWEEN 0 AND 3),
  "no_trade_raw" INTEGER CHECK (no_trade_raw BETWEEN 0 AND 1),
  "extension_length_raw" INTEGER CHECK (extension_length_raw BETWEEN 0 AND 7),
  "extension_option_raw" INTEGER CHECK (extension_option_raw BETWEEN 0 AND 3),
  "extension_no_trade_raw" INTEGER CHECK (extension_no_trade_raw BETWEEN 0 AND 1),
  "contract_year_1_raw" INTEGER CHECK (contract_year_1_raw BETWEEN 0 AND 2147483647),
  "contract_year_2_raw" INTEGER CHECK (contract_year_2_raw BETWEEN 0 AND 2147483647),
  "contract_year_3_raw" INTEGER CHECK (contract_year_3_raw BETWEEN 0 AND 2147483647),
  "contract_year_4_raw" INTEGER CHECK (contract_year_4_raw BETWEEN 0 AND 2147483647),
  "contract_year_5_raw" INTEGER CHECK (contract_year_5_raw BETWEEN 0 AND 2147483647),
  "contract_year_6_raw" INTEGER CHECK (contract_year_6_raw BETWEEN 0 AND 2147483647),
  "contract_type_raw" INTEGER CHECK (contract_type_raw BETWEEN 0 AND 7),
  "euro_stash_years_left_raw" INTEGER CHECK (euro_stash_years_left_raw BETWEEN 0 AND 7),
  "two_way_days_left_raw" INTEGER CHECK (two_way_days_left_raw BETWEEN 0 AND 63),
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "native_contract_team_id_raw" INTEGER,
  "contract_team_status" TEXT,
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_contract_observations_player_id" ON "player_contract_observations" ("player_id");

CREATE INDEX "idx_player_contract_observations_team_id" ON "player_contract_observations" ("team_id");

CREATE INDEX "idx_player_contract_observations_unit_id" ON "player_contract_observations" ("unit_id");

CREATE INDEX "idx_player_contract_observations_source_player_id" ON "player_contract_observations" ("source_player_id");

CREATE TRIGGER "player_contract_observations_no_update" BEFORE UPDATE ON "player_contract_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_contract_observations_no_delete" BEFORE DELETE ON "player_contract_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_contract_observations_successful_unit" BEFORE INSERT ON "player_contract_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_health_observations" (
  "health_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "injury_code" TEXT,
  "body_part" TEXT,
  "severity" TEXT,
  "availability" TEXT,
  "recovery_text" TEXT,
  "fatigue_raw" INTEGER,
  "energy_raw" INTEGER,
  "recovery_days" INTEGER,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "injury1_type_raw" INTEGER CHECK (injury1_type_raw BETWEEN 0 AND 255),
  "injury2_type_raw" INTEGER CHECK (injury2_type_raw BETWEEN 0 AND 255),
  "original_injury1_type_raw" INTEGER CHECK (original_injury1_type_raw BETWEEN 0 AND 255),
  "original_injury2_type_raw" INTEGER CHECK (original_injury2_type_raw BETWEEN 0 AND 255),
  "injury1_healed_percentage_raw" INTEGER CHECK (injury1_healed_percentage_raw BETWEEN 0 AND 127),
  "injury2_healed_percentage_raw" INTEGER CHECK (injury2_healed_percentage_raw BETWEEN 0 AND 127),
  "wear_and_tear_raw" INTEGER CHECK (wear_and_tear_raw BETWEEN 0 AND 255),
  "injury1_start_date_word_raw" INTEGER CHECK (injury1_start_date_word_raw BETWEEN 0 AND 4294967295),
  "injury2_start_date_word_raw" INTEGER CHECK (injury2_start_date_word_raw BETWEEN 0 AND 4294967295),
  "latest_healed_start_date_word_raw" INTEGER CHECK (latest_healed_start_date_word_raw BETWEEN 0 AND 4294967295),
  "latest_healed_date_word_raw" INTEGER CHECK (latest_healed_date_word_raw BETWEEN 0 AND 4294967295),
  "injury1_duration_minutes_raw" INTEGER CHECK (injury1_duration_minutes_raw BETWEEN 0 AND 1048575),
  "injury2_duration_minutes_raw" INTEGER CHECK (injury2_duration_minutes_raw BETWEEN 0 AND 1048575),
  "injury1_status_raw" INTEGER CHECK (injury1_status_raw BETWEEN 0 AND 7),
  "injury2_status_raw" INTEGER CHECK (injury2_status_raw BETWEEN 0 AND 7),
  "injury1_left_side_raw" INTEGER CHECK (injury1_left_side_raw BETWEEN 0 AND 1),
  "injury2_left_side_raw" INTEGER CHECK (injury2_left_side_raw BETWEEN 0 AND 1),
  "latest_injury_slot_raw" INTEGER CHECK (latest_injury_slot_raw BETWEEN 0 AND 1),
  "career_ended_by_injury_raw" INTEGER CHECK (career_ended_by_injury_raw BETWEEN 0 AND 1),
  "important_injury_recovery_raw" INTEGER CHECK (important_injury_recovery_raw BETWEEN 0 AND 1),
  "had_important_injury_raw" INTEGER CHECK (had_important_injury_raw BETWEEN 0 AND 1),
  "games_missed_injury_raw" INTEGER CHECK (games_missed_injury_raw BETWEEN 0 AND 127),
  "injury1_type_label" TEXT,
  "injury1_status_label" TEXT,
  "injury2_type_label" TEXT,
  "injury2_status_label" TEXT,
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_health_observations_player_id" ON "player_health_observations" ("player_id");

CREATE INDEX "idx_player_health_observations_unit_id" ON "player_health_observations" ("unit_id");

CREATE INDEX "idx_player_health_observations_source_player_id" ON "player_health_observations" ("source_player_id");

CREATE TRIGGER "player_health_observations_no_update" BEFORE UPDATE ON "player_health_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_health_observations_no_delete" BEFORE DELETE ON "player_health_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_health_observations_successful_unit" BEFORE INSERT ON "player_health_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_morale_observations" (
  "morale_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "role_code" TEXT,
  "morale_raw" INTEGER,
  "role_satisfaction_raw" INTEGER,
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "morale_event_type_raw" INTEGER CHECK (morale_event_type_raw BETWEEN 0 AND 255),
  "morale_event_adjustment_raw" INTEGER CHECK (morale_event_adjustment_raw BETWEEN 0 AND 255),
  "org_role_raw" INTEGER CHECK (org_role_raw BETWEEN 0 AND 7),
  "morale_word_raw" INTEGER CHECK (morale_word_raw BETWEEN 0 AND 4294967295),
  "morale_real" REAL,
  "morale_value_text" TEXT,
  "morale_value_status" TEXT,
  "morale_event_adjustment_signed" INTEGER CHECK (morale_event_adjustment_signed BETWEEN -128 AND 127),
  "morale_event_label" TEXT,
  "org_role_label" TEXT,
  UNIQUE ("player_id","unit_id"),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_player_morale_observations_player_id" ON "player_morale_observations" ("player_id");

CREATE INDEX "idx_player_morale_observations_unit_id" ON "player_morale_observations" ("unit_id");

CREATE INDEX "idx_player_morale_observations_source_player_id" ON "player_morale_observations" ("source_player_id");

CREATE TRIGGER "player_morale_observations_no_update" BEFORE UPDATE ON "player_morale_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_morale_observations_no_delete" BEFORE DELETE ON "player_morale_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_morale_observations_successful_unit" BEFORE INSERT ON "player_morale_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_training_observations" (
  "training_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "focus_code" TEXT,
  "intensity_raw" INTEGER,
  "schedule_code" TEXT,
  "position_raw" INTEGER,
  "player_type_raw" INTEGER,
  "injury_recovery_raw" INTEGER,
  "is_intensity_overriden_raw" INTEGER,
  "source_slot_index" INTEGER,
  "identity_status" TEXT,
  UNIQUE ("player_id","unit_id")
) STRICT;

CREATE INDEX "idx_player_training_observations_player_id" ON "player_training_observations" ("player_id");

CREATE INDEX "idx_player_training_observations_unit_id" ON "player_training_observations" ("unit_id");

CREATE INDEX "idx_player_training_observations_team_id" ON "player_training_observations" ("team_id");

CREATE TRIGGER "player_training_observations_no_update" BEFORE UPDATE ON "player_training_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_training_observations_no_delete" BEFORE DELETE ON "player_training_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_training_observations_successful_unit" BEFORE INSERT ON "player_training_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "game_state_observations" (
  "observation_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "status_code" TEXT NOT NULL,
  "home_points" INTEGER,
  "away_points" INTEGER,
  "overtime_count" INTEGER,
  "attendance" INTEGER,
  "was_simulated" INTEGER,
  "score_provenance" TEXT DEFAULT 'UNKNOWN',
  "is_final" INTEGER DEFAULT 0 CHECK (is_final IN (0,1)),
  UNIQUE ("game_id","unit_id")
) STRICT;

CREATE INDEX "idx_game_state_observations_game_id" ON "game_state_observations" ("game_id");

CREATE INDEX "idx_game_state_observations_unit_id" ON "game_state_observations" ("unit_id");

CREATE TRIGGER "game_state_observations_no_update" BEFORE UPDATE ON "game_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_state_observations_no_delete" BEFORE DELETE ON "game_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_state_observations_successful_unit" BEFORE INSERT ON "game_state_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "game_period_scores" (
  "period_score_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "period_index" INTEGER NOT NULL CHECK (period_index>=1),
  "period_points" INTEGER NOT NULL CHECK (period_points>=0),
  UNIQUE ("game_id","team_id","period_index","unit_id")
) STRICT;

CREATE INDEX "idx_game_period_scores_game_id" ON "game_period_scores" ("game_id");

CREATE INDEX "idx_game_period_scores_team_id" ON "game_period_scores" ("team_id");

CREATE INDEX "idx_game_period_scores_unit_id" ON "game_period_scores" ("unit_id");

CREATE TRIGGER "game_period_scores_no_update" BEFORE UPDATE ON "game_period_scores" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_period_scores_no_delete" BEFORE DELETE ON "game_period_scores" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_period_scores_successful_unit" BEFORE INSERT ON "game_period_scores" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_game_boxes" (
  "box_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "points" INTEGER CHECK ("points" IS NULL OR "points">=0),
  "fg_made" INTEGER CHECK ("fg_made" IS NULL OR "fg_made">=0),
  "fg_attempted" INTEGER CHECK ("fg_attempted" IS NULL OR "fg_attempted">=0),
  "three_made" INTEGER CHECK ("three_made" IS NULL OR "three_made">=0),
  "three_attempted" INTEGER CHECK ("three_attempted" IS NULL OR "three_attempted">=0),
  "ft_made" INTEGER CHECK ("ft_made" IS NULL OR "ft_made">=0),
  "ft_attempted" INTEGER CHECK ("ft_attempted" IS NULL OR "ft_attempted">=0),
  "offensive_rebounds" INTEGER CHECK ("offensive_rebounds" IS NULL OR "offensive_rebounds">=0),
  "defensive_rebounds" INTEGER CHECK ("defensive_rebounds" IS NULL OR "defensive_rebounds">=0),
  "assists" INTEGER CHECK ("assists" IS NULL OR "assists">=0),
  "steals" INTEGER CHECK ("steals" IS NULL OR "steals">=0),
  "blocks" INTEGER CHECK ("blocks" IS NULL OR "blocks">=0),
  "turnovers" INTEGER CHECK ("turnovers" IS NULL OR "turnovers">=0),
  "fouls" INTEGER CHECK ("fouls" IS NULL OR "fouls">=0),
  "minutes_raw" INTEGER CHECK ("minutes_raw" IS NULL OR "minutes_raw">=0),
  "plus_minus" INTEGER,
  "possessions_raw" INTEGER CHECK ("possessions_raw" IS NULL OR "possessions_raw">=0),
  "fastbreak_points" INTEGER,
  "paint_points" INTEGER,
  "second_chance_points" INTEGER,
  "points_off_turnovers" INTEGER,
  "largest_lead" INTEGER,
  UNIQUE ("game_id","team_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_game_boxes_game_id" ON "team_game_boxes" ("game_id");

CREATE INDEX "idx_team_game_boxes_team_id" ON "team_game_boxes" ("team_id");

CREATE INDEX "idx_team_game_boxes_unit_id" ON "team_game_boxes" ("unit_id");

CREATE TRIGGER "team_game_boxes_no_update" BEFORE UPDATE ON "team_game_boxes" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_game_boxes_no_delete" BEFORE DELETE ON "team_game_boxes" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_game_boxes_successful_unit" BEFORE INSERT ON "team_game_boxes" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_game_boxes" (
  "box_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "points" INTEGER CHECK ("points" IS NULL OR "points">=0),
  "fg_made" INTEGER CHECK ("fg_made" IS NULL OR "fg_made">=0),
  "fg_attempted" INTEGER CHECK ("fg_attempted" IS NULL OR "fg_attempted">=0),
  "three_made" INTEGER CHECK ("three_made" IS NULL OR "three_made">=0),
  "three_attempted" INTEGER CHECK ("three_attempted" IS NULL OR "three_attempted">=0),
  "ft_made" INTEGER CHECK ("ft_made" IS NULL OR "ft_made">=0),
  "ft_attempted" INTEGER CHECK ("ft_attempted" IS NULL OR "ft_attempted">=0),
  "offensive_rebounds" INTEGER CHECK ("offensive_rebounds" IS NULL OR "offensive_rebounds">=0),
  "defensive_rebounds" INTEGER CHECK ("defensive_rebounds" IS NULL OR "defensive_rebounds">=0),
  "assists" INTEGER CHECK ("assists" IS NULL OR "assists">=0),
  "steals" INTEGER CHECK ("steals" IS NULL OR "steals">=0),
  "blocks" INTEGER CHECK ("blocks" IS NULL OR "blocks">=0),
  "turnovers" INTEGER CHECK ("turnovers" IS NULL OR "turnovers">=0),
  "fouls" INTEGER CHECK ("fouls" IS NULL OR "fouls">=0),
  "minutes_raw" INTEGER CHECK ("minutes_raw" IS NULL OR "minutes_raw">=0),
  "plus_minus" INTEGER,
  "possessions_raw" INTEGER CHECK ("possessions_raw" IS NULL OR "possessions_raw">=0),
  "defensive_fg_made" INTEGER,
  "defensive_fg_attempted" INTEGER,
  "defensive_points" INTEGER,
  "is_starter" INTEGER,
  "in_use" INTEGER,
  "points_provenance" TEXT DEFAULT 'UNKNOWN',
  UNIQUE ("game_id","player_id","unit_id"),
  CHECK (fg_made IS NULL OR fg_attempted IS NULL OR fg_made<=fg_attempted)
) STRICT;

CREATE INDEX "idx_player_game_boxes_game_id" ON "player_game_boxes" ("game_id");

CREATE INDEX "idx_player_game_boxes_player_id" ON "player_game_boxes" ("player_id");

CREATE INDEX "idx_player_game_boxes_team_id" ON "player_game_boxes" ("team_id");

CREATE INDEX "idx_player_game_boxes_unit_id" ON "player_game_boxes" ("unit_id");

CREATE TRIGGER "player_game_boxes_no_update" BEFORE UPDATE ON "player_game_boxes" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_game_boxes_no_delete" BEFORE DELETE ON "player_game_boxes" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_game_boxes_successful_unit" BEFORE INSERT ON "player_game_boxes" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "playoff_series" (
  "series_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "team_a_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "team_b_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "round_code" TEXT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  CHECK (team_a_id<>team_b_id)
) STRICT;

CREATE INDEX "idx_playoff_series_season_id" ON "playoff_series" ("season_id");

CREATE INDEX "idx_playoff_series_team_a_id" ON "playoff_series" ("team_a_id");

CREATE INDEX "idx_playoff_series_team_b_id" ON "playoff_series" ("team_b_id");

CREATE INDEX "idx_playoff_series_unit_id" ON "playoff_series" ("unit_id");

CREATE TRIGGER "playoff_series_no_update" BEFORE UPDATE ON "playoff_series" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "playoff_series_no_delete" BEFORE DELETE ON "playoff_series" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "playoff_series_successful_unit" BEFORE INSERT ON "playoff_series" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "playoff_series_games" (
  "series_game_id" TEXT NOT NULL PRIMARY KEY,
  "series_id" TEXT NOT NULL REFERENCES playoff_series(series_id) ON DELETE RESTRICT,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "sequence_no" INTEGER,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  UNIQUE ("series_id","game_id","unit_id")
) STRICT;

CREATE INDEX "idx_playoff_series_games_series_id" ON "playoff_series_games" ("series_id");

CREATE INDEX "idx_playoff_series_games_game_id" ON "playoff_series_games" ("game_id");

CREATE INDEX "idx_playoff_series_games_unit_id" ON "playoff_series_games" ("unit_id");

CREATE TRIGGER "playoff_series_games_no_update" BEFORE UPDATE ON "playoff_series_games" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "playoff_series_games_no_delete" BEFORE DELETE ON "playoff_series_games" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "playoff_series_games_successful_unit" BEFORE INSERT ON "playoff_series_games" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_season_totals" (
  "total_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "team_scope" TEXT,
  "phase_code" TEXT,
  "is_final" INTEGER DEFAULT 0 CHECK (is_final IN (0,1)),
  "games_played" INTEGER CHECK ("games_played" IS NULL OR "games_played">=0),
  "games_started" INTEGER CHECK ("games_started" IS NULL OR "games_started">=0),
  "points" INTEGER CHECK ("points" IS NULL OR "points">=0),
  "fg_made" INTEGER CHECK ("fg_made" IS NULL OR "fg_made">=0),
  "fg_attempted" INTEGER CHECK ("fg_attempted" IS NULL OR "fg_attempted">=0),
  "three_made" INTEGER CHECK ("three_made" IS NULL OR "three_made">=0),
  "three_attempted" INTEGER CHECK ("three_attempted" IS NULL OR "three_attempted">=0),
  "ft_made" INTEGER CHECK ("ft_made" IS NULL OR "ft_made">=0),
  "ft_attempted" INTEGER CHECK ("ft_attempted" IS NULL OR "ft_attempted">=0),
  "offensive_rebounds" INTEGER CHECK ("offensive_rebounds" IS NULL OR "offensive_rebounds">=0),
  "defensive_rebounds" INTEGER CHECK ("defensive_rebounds" IS NULL OR "defensive_rebounds">=0),
  "assists" INTEGER CHECK ("assists" IS NULL OR "assists">=0),
  "steals" INTEGER CHECK ("steals" IS NULL OR "steals">=0),
  "blocks" INTEGER CHECK ("blocks" IS NULL OR "blocks">=0),
  "turnovers" INTEGER CHECK ("turnovers" IS NULL OR "turnovers">=0),
  "fouls" INTEGER CHECK ("fouls" IS NULL OR "fouls">=0),
  "minutes_raw" INTEGER CHECK ("minutes_raw" IS NULL OR "minutes_raw">=0),
  "plus_minus" INTEGER,
  "possessions_raw" INTEGER CHECK ("possessions_raw" IS NULL OR "possessions_raw">=0),
  "double_doubles" INTEGER,
  "triple_doubles" INTEGER,
  UNIQUE ("player_id","season_id","unit_id")
) STRICT;

CREATE INDEX "idx_player_season_totals_player_id" ON "player_season_totals" ("player_id");

CREATE INDEX "idx_player_season_totals_season_id" ON "player_season_totals" ("season_id");

CREATE INDEX "idx_player_season_totals_unit_id" ON "player_season_totals" ("unit_id");

CREATE INDEX "idx_player_season_totals_team_id" ON "player_season_totals" ("team_id");

CREATE TRIGGER "player_season_totals_no_update" BEFORE UPDATE ON "player_season_totals" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_season_totals_no_delete" BEFORE DELETE ON "player_season_totals" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_season_totals_successful_unit" BEFORE INSERT ON "player_season_totals" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_season_totals" (
  "total_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "phase_code" TEXT,
  "is_final" INTEGER DEFAULT 0 CHECK (is_final IN (0,1)),
  "wins" INTEGER,
  "losses" INTEGER,
  "points" INTEGER CHECK ("points" IS NULL OR "points">=0),
  "fg_made" INTEGER CHECK ("fg_made" IS NULL OR "fg_made">=0),
  "fg_attempted" INTEGER CHECK ("fg_attempted" IS NULL OR "fg_attempted">=0),
  "three_made" INTEGER CHECK ("three_made" IS NULL OR "three_made">=0),
  "three_attempted" INTEGER CHECK ("three_attempted" IS NULL OR "three_attempted">=0),
  "ft_made" INTEGER CHECK ("ft_made" IS NULL OR "ft_made">=0),
  "ft_attempted" INTEGER CHECK ("ft_attempted" IS NULL OR "ft_attempted">=0),
  "offensive_rebounds" INTEGER CHECK ("offensive_rebounds" IS NULL OR "offensive_rebounds">=0),
  "defensive_rebounds" INTEGER CHECK ("defensive_rebounds" IS NULL OR "defensive_rebounds">=0),
  "assists" INTEGER CHECK ("assists" IS NULL OR "assists">=0),
  "steals" INTEGER CHECK ("steals" IS NULL OR "steals">=0),
  "blocks" INTEGER CHECK ("blocks" IS NULL OR "blocks">=0),
  "turnovers" INTEGER CHECK ("turnovers" IS NULL OR "turnovers">=0),
  "fouls" INTEGER CHECK ("fouls" IS NULL OR "fouls">=0),
  "minutes_raw" INTEGER CHECK ("minutes_raw" IS NULL OR "minutes_raw">=0),
  "plus_minus" INTEGER,
  "possessions_raw" INTEGER CHECK ("possessions_raw" IS NULL OR "possessions_raw">=0),
  "opponent_points" INTEGER,
  "points_off_turnovers" INTEGER,
  "second_chance_points" INTEGER,
  "paint_points" INTEGER,
  "bench_points" INTEGER,
  "pace_raw" INTEGER,
  "opponent_fg_made" INTEGER,
  "opponent_fg_attempted" INTEGER,
  "opponent_three_made" INTEGER,
  "opponent_three_attempted" INTEGER,
  UNIQUE ("team_id","season_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_season_totals_team_id" ON "team_season_totals" ("team_id");

CREATE INDEX "idx_team_season_totals_season_id" ON "team_season_totals" ("season_id");

CREATE INDEX "idx_team_season_totals_unit_id" ON "team_season_totals" ("unit_id");

CREATE TRIGGER "team_season_totals_no_update" BEFORE UPDATE ON "team_season_totals" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_season_totals_no_delete" BEFORE DELETE ON "team_season_totals" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_season_totals_successful_unit" BEFORE INSERT ON "team_season_totals" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "staff_team_assignments" (
  "assignment_id" TEXT NOT NULL PRIMARY KEY,
  "staff_id" TEXT NOT NULL REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "role_code" TEXT NOT NULL,
  UNIQUE ("staff_id","unit_id","role_code")
) STRICT;

CREATE INDEX "idx_staff_team_assignments_staff_id" ON "staff_team_assignments" ("staff_id");

CREATE INDEX "idx_staff_team_assignments_team_id" ON "staff_team_assignments" ("team_id");

CREATE INDEX "idx_staff_team_assignments_unit_id" ON "staff_team_assignments" ("unit_id");

CREATE TRIGGER "staff_team_assignments_no_update" BEFORE UPDATE ON "staff_team_assignments" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_team_assignments_no_delete" BEFORE DELETE ON "staff_team_assignments" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_team_assignments_successful_unit" BEFORE INSERT ON "staff_team_assignments" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "staff_contract_observations" (
  "contract_obs_id" TEXT NOT NULL PRIMARY KEY,
  "staff_id" TEXT NOT NULL REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "salary_raw" INTEGER,
  "years_left" INTEGER,
  UNIQUE ("staff_id","unit_id")
) STRICT;

CREATE INDEX "idx_staff_contract_observations_staff_id" ON "staff_contract_observations" ("staff_id");

CREATE INDEX "idx_staff_contract_observations_unit_id" ON "staff_contract_observations" ("unit_id");

CREATE TRIGGER "staff_contract_observations_no_update" BEFORE UPDATE ON "staff_contract_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_contract_observations_no_delete" BEFORE DELETE ON "staff_contract_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_contract_observations_successful_unit" BEFORE INSERT ON "staff_contract_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "staff_skill_observations" (
  "skill_obs_id" TEXT NOT NULL PRIMARY KEY,
  "staff_id" TEXT NOT NULL REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "offense_raw" INTEGER,
  "defense_raw" INTEGER,
  "contracts_raw" INTEGER,
  "trading_raw" INTEGER,
  "scouting_raw" INTEGER,
  "training_raw" INTEGER,
  "business_raw" INTEGER,
  UNIQUE ("staff_id","unit_id")
) STRICT;

CREATE INDEX "idx_staff_skill_observations_staff_id" ON "staff_skill_observations" ("staff_id");

CREATE INDEX "idx_staff_skill_observations_unit_id" ON "staff_skill_observations" ("unit_id");

CREATE TRIGGER "staff_skill_observations_no_update" BEFORE UPDATE ON "staff_skill_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_skill_observations_no_delete" BEFORE DELETE ON "staff_skill_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "staff_skill_observations_successful_unit" BEFORE INSERT ON "staff_skill_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "coach_preferences" (
  "pref_id" TEXT NOT NULL PRIMARY KEY,
  "staff_id" TEXT NOT NULL REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "preferred_system_raw" INTEGER,
  "active_system_raw" INTEGER,
  "personal_style" TEXT,
  UNIQUE ("staff_id","unit_id")
) STRICT;

CREATE INDEX "idx_coach_preferences_staff_id" ON "coach_preferences" ("staff_id");

CREATE INDEX "idx_coach_preferences_unit_id" ON "coach_preferences" ("unit_id");

CREATE TRIGGER "coach_preferences_no_update" BEFORE UPDATE ON "coach_preferences" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "coach_preferences_no_delete" BEFORE DELETE ON "coach_preferences" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "coach_preferences_successful_unit" BEFORE INSERT ON "coach_preferences" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_tactic_settings" (
  "tactic_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "poe_code" INTEGER,
  "ace_code" INTEGER,
  "preferred_system_raw" INTEGER,
  "run_plays_raw" INTEGER,
  "help_defense_raw" INTEGER,
  "zone_usage_raw" INTEGER,
  "tempo_raw" INTEGER,
  "crash_offensive_glass_raw" INTEGER,
  "crash_defensive_glass_raw" INTEGER,
  "bench_depth_raw" INTEGER,
  "freelance_slot_1" TEXT,
  "freelance_slot_2" TEXT,
  "freelance_slot_3" TEXT,
  "freelance_slot_4" TEXT,
  "poe_defense_1_raw" INTEGER,
  "poe_defense_2_raw" INTEGER,
  "poe_defense_3_raw" INTEGER,
  "poe_offense_1_raw" INTEGER,
  "poe_offense_2_raw" INTEGER,
  "poe_offense_3_raw" INTEGER,
  "sim_pace_raw" INTEGER,
  "sim_pressure_raw" INTEGER,
  "sim_help_defense_raw" INTEGER,
  "sim_offensive_rebounds_raw" INTEGER,
  "sim_defensive_rebounds_raw" INTEGER,
  "active_system_raw" INTEGER,
  "playbook_code_raw" INTEGER,
  "bench_utilization_raw" INTEGER,
  UNIQUE ("team_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_tactic_settings_team_id" ON "team_tactic_settings" ("team_id");

CREATE INDEX "idx_team_tactic_settings_unit_id" ON "team_tactic_settings" ("unit_id");

CREATE TRIGGER "team_tactic_settings_no_update" BEFORE UPDATE ON "team_tactic_settings" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_tactic_settings_no_delete" BEFORE DELETE ON "team_tactic_settings" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_tactic_settings_successful_unit" BEFORE INSERT ON "team_tactic_settings" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_playbook_slots" (
  "slot_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL CHECK (slot_index>=0),
  "play_code" TEXT,
  "play_name" TEXT,
  "playbook_native_id" TEXT,
  UNIQUE ("team_id","unit_id","slot_index")
) STRICT;

CREATE INDEX "idx_team_playbook_slots_team_id" ON "team_playbook_slots" ("team_id");

CREATE INDEX "idx_team_playbook_slots_unit_id" ON "team_playbook_slots" ("unit_id");

CREATE TRIGGER "team_playbook_slots_no_update" BEFORE UPDATE ON "team_playbook_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_playbook_slots_no_delete" BEFORE DELETE ON "team_playbook_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_playbook_slots_successful_unit" BEFORE INSERT ON "team_playbook_slots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_training_settings" (
  "training_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "focus_code" TEXT,
  "intensity_raw" INTEGER,
  "schedule_code" TEXT,
  "home_intensity_raw" INTEGER,
  "away_intensity_raw" INTEGER,
  "automate_intensity_raw" INTEGER,
  "rest_before_b2b_raw" INTEGER,
  "rest_after_b2b_raw" INTEGER,
  "injury_recovery_raw" INTEGER,
  UNIQUE ("team_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_training_settings_team_id" ON "team_training_settings" ("team_id");

CREATE INDEX "idx_team_training_settings_unit_id" ON "team_training_settings" ("unit_id");

CREATE TRIGGER "team_training_settings_no_update" BEFORE UPDATE ON "team_training_settings" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_training_settings_no_delete" BEFORE DELETE ON "team_training_settings" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_training_settings_successful_unit" BEFORE INSERT ON "team_training_settings" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "mentorship_relations" (
  "mentor_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "mentor_player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_slot_index" INTEGER,
  "duration_days_raw" INTEGER,
  "compatibility_word_raw" INTEGER,
  "badge_count_raw" INTEGER,
  "association_status" TEXT DEFAULT 'OBSERVED_PAIR_ACTIVITY_NOT_VERIFIED',
  UNIQUE ("player_id","unit_id"),
  CHECK (player_id<>mentor_player_id)
) STRICT;

CREATE INDEX "idx_mentorship_relations_player_id" ON "mentorship_relations" ("player_id");

CREATE INDEX "idx_mentorship_relations_mentor_player_id" ON "mentorship_relations" ("mentor_player_id");

CREATE INDEX "idx_mentorship_relations_team_id" ON "mentorship_relations" ("team_id");

CREATE INDEX "idx_mentorship_relations_unit_id" ON "mentorship_relations" ("unit_id");

CREATE TRIGGER "mentorship_relations_no_update" BEFORE UPDATE ON "mentorship_relations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "mentorship_relations_no_delete" BEFORE DELETE ON "mentorship_relations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "mentorship_relations_successful_unit" BEFORE INSERT ON "mentorship_relations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_finance_observations" (
  "finance_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "payroll_raw" INTEGER,
  "cap_space_raw" INTEGER,
  "luxury_tax_raw" INTEGER,
  "budget_raw" INTEGER,
  "salary_cap_raw" INTEGER,
  "hard_cap_raw" INTEGER,
  "total_salary_raw" INTEGER,
  "staff_budget_raw" INTEGER,
  "cash_raw" INTEGER,
  "gate_revenue_raw" INTEGER,
  "merch_revenue_raw" INTEGER,
  "media_revenue_raw" INTEGER,
  UNIQUE ("team_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_finance_observations_team_id" ON "team_finance_observations" ("team_id");

CREATE INDEX "idx_team_finance_observations_unit_id" ON "team_finance_observations" ("unit_id");

CREATE TRIGGER "team_finance_observations_no_update" BEFORE UPDATE ON "team_finance_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_finance_observations_no_delete" BEFORE DELETE ON "team_finance_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_finance_observations_successful_unit" BEFORE INSERT ON "team_finance_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "team_state_observations" (
  "state_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "chemistry_raw" REAL,
  "fan_interest_raw" REAL,
  UNIQUE ("team_id","unit_id")
) STRICT;

CREATE INDEX "idx_team_state_observations_team_id" ON "team_state_observations" ("team_id");

CREATE INDEX "idx_team_state_observations_unit_id" ON "team_state_observations" ("unit_id");

CREATE TRIGGER "team_state_observations_no_update" BEFORE UPDATE ON "team_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_state_observations_no_delete" BEFORE DELETE ON "team_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "team_state_observations_successful_unit" BEFORE INSERT ON "team_state_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "market_state_observations" (
  "market_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "staff_id" TEXT REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "market_status" TEXT NOT NULL,
  "origin_type" TEXT NOT NULL CHECK (origin_type IN ('NATIVE','EXTERNAL')),
  "source_player_id" TEXT REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "layout_version" TEXT,
  "native_player_type_label" TEXT,
  "g_league_team_label" TEXT,
  "free_agency_type_label" TEXT,
  "availability_interpretation" TEXT,
  "native_player_type_raw" INTEGER CHECK (native_player_type_raw BETWEEN 0 AND 7),
  "is_active_raw" INTEGER CHECK (is_active_raw BETWEEN 0 AND 1),
  "is_hidden_raw" INTEGER CHECK (is_hidden_raw BETWEEN 0 AND 1),
  "is_generated_raw" INTEGER CHECK (is_generated_raw BETWEEN 0 AND 1),
  "is_draft_prospect_raw" INTEGER CHECK (is_draft_prospect_raw BETWEEN 0 AND 1),
  "was_drafted_raw" INTEGER CHECK (was_drafted_raw BETWEEN 0 AND 1),
  "is_historic_raw" INTEGER CHECK (is_historic_raw BETWEEN 0 AND 1),
  "is_d_league_raw" INTEGER CHECK (is_d_league_raw BETWEEN 0 AND 1),
  "is_d_league_send_down_raw" INTEGER CHECK (is_d_league_send_down_raw BETWEEN 0 AND 1),
  "g_league_team_raw" INTEGER CHECK (g_league_team_raw BETWEEN 0 AND 31),
  "free_agency_type_raw" INTEGER CHECK (free_agency_type_raw BETWEEN 0 AND 3),
  "offseason_free_agent_raw" INTEGER CHECK (offseason_free_agent_raw BETWEEN 0 AND 1),
  "offseason_free_agent_extended_raw" INTEGER CHECK (offseason_free_agent_extended_raw BETWEEN 0 AND 1),
  "is_waived_raw" INTEGER CHECK (is_waived_raw BETWEEN 0 AND 1),
  "is_playable_raw" INTEGER CHECK (is_playable_raw BETWEEN 0 AND 1),
  "drafted_round_raw" INTEGER CHECK (drafted_round_raw BETWEEN 0 AND 15),
  "drafted_pick_raw" INTEGER CHECK (drafted_pick_raw BETWEEN 0 AND 63),
  UNIQUE ("source_player_id","unit_id"),
  CHECK (player_id IS NOT NULL OR staff_id IS NOT NULL OR source_player_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_market_state_observations_player_id" ON "market_state_observations" ("player_id");

CREATE INDEX "idx_market_state_observations_staff_id" ON "market_state_observations" ("staff_id");

CREATE INDEX "idx_market_state_observations_unit_id" ON "market_state_observations" ("unit_id");

CREATE INDEX "idx_market_state_observations_source_player_id" ON "market_state_observations" ("source_player_id");

CREATE TRIGGER "market_state_observations_no_update" BEFORE UPDATE ON "market_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "market_state_observations_no_delete" BEFORE DELETE ON "market_state_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "market_state_observations_successful_unit" BEFORE INSERT ON "market_state_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "external_transaction_events" (
  "transaction_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "event_type" TEXT NOT NULL,
  "occurred_at" TEXT,
  "source_ref" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "producer_event_id" TEXT NOT NULL,
  UNIQUE ("source_ref","producer_event_id")
) STRICT;

CREATE INDEX "idx_external_transaction_events_save_id" ON "external_transaction_events" ("save_id");

CREATE INDEX "idx_external_transaction_events_unit_id" ON "external_transaction_events" ("unit_id");

CREATE TRIGGER "external_transaction_events_no_update" BEFORE UPDATE ON "external_transaction_events" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_transaction_events_no_delete" BEFORE DELETE ON "external_transaction_events" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_transaction_events_successful_unit" BEFORE INSERT ON "external_transaction_events" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_pick_assets" (
  "pick_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "draft_year" INTEGER NOT NULL,
  "draft_round" INTEGER NOT NULL,
  "original_team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "native_pick_id" TEXT,
  UNIQUE ("draft_year","draft_round","original_team_id")
) STRICT;

CREATE INDEX "idx_draft_pick_assets_save_id" ON "draft_pick_assets" ("save_id");

CREATE INDEX "idx_draft_pick_assets_original_team_id" ON "draft_pick_assets" ("original_team_id");

CREATE TRIGGER "draft_pick_assets_no_update" BEFORE UPDATE ON "draft_pick_assets" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_pick_assets_no_delete" BEFORE DELETE ON "draft_pick_assets" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TABLE "transaction_components" (
  "component_id" TEXT NOT NULL PRIMARY KEY,
  "transaction_id" TEXT NOT NULL REFERENCES external_transaction_events(transaction_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "from_team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "to_team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "staff_id" TEXT REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "pick_id" TEXT REFERENCES draft_pick_assets(pick_id) ON DELETE RESTRICT,
  "component_kind" TEXT NOT NULL,
  "salary_raw" INTEGER
) STRICT;

CREATE INDEX "idx_transaction_components_transaction_id" ON "transaction_components" ("transaction_id");

CREATE INDEX "idx_transaction_components_unit_id" ON "transaction_components" ("unit_id");

CREATE INDEX "idx_transaction_components_from_team_id" ON "transaction_components" ("from_team_id");

CREATE INDEX "idx_transaction_components_to_team_id" ON "transaction_components" ("to_team_id");

CREATE INDEX "idx_transaction_components_player_id" ON "transaction_components" ("player_id");

CREATE INDEX "idx_transaction_components_staff_id" ON "transaction_components" ("staff_id");

CREATE INDEX "idx_transaction_components_pick_id" ON "transaction_components" ("pick_id");

CREATE TRIGGER "transaction_components_no_update" BEFORE UPDATE ON "transaction_components" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "transaction_components_no_delete" BEFORE DELETE ON "transaction_components" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "transaction_components_successful_unit" BEFORE INSERT ON "transaction_components" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_pick_ownerships" (
  "ownership_id" TEXT NOT NULL PRIMARY KEY,
  "pick_id" TEXT NOT NULL REFERENCES draft_pick_assets(pick_id) ON DELETE RESTRICT,
  "owner_team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "event_ref" TEXT REFERENCES external_transaction_events(transaction_id) ON DELETE RESTRICT,
  "origin_type" TEXT NOT NULL CHECK (origin_type IN ('NATIVE','EXTERNAL')),
  "source_row_index" INTEGER,
  "native_pick_index_raw" INTEGER,
  "protection_status" TEXT DEFAULT 'UNKNOWN',
  "swap_status" TEXT DEFAULT 'UNKNOWN',
  UNIQUE ("pick_id","unit_id")
) STRICT;

CREATE INDEX "idx_draft_pick_ownerships_pick_id" ON "draft_pick_ownerships" ("pick_id");

CREATE INDEX "idx_draft_pick_ownerships_owner_team_id" ON "draft_pick_ownerships" ("owner_team_id");

CREATE INDEX "idx_draft_pick_ownerships_unit_id" ON "draft_pick_ownerships" ("unit_id");

CREATE INDEX "idx_draft_pick_ownerships_event_ref" ON "draft_pick_ownerships" ("event_ref");

CREATE TRIGGER "draft_pick_ownerships_no_update" BEFORE UPDATE ON "draft_pick_ownerships" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_pick_ownerships_no_delete" BEFORE DELETE ON "draft_pick_ownerships" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_pick_ownerships_successful_unit" BEFORE INSERT ON "draft_pick_ownerships" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_prospects" (
  "prospect_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "draft_year" INTEGER,
  "native_prospect_id" TEXT,
  "display_name" TEXT,
  "class_year_status" TEXT DEFAULT 'UNKNOWN',
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX "idx_draft_prospects_save_id" ON "draft_prospects" ("save_id");

CREATE INDEX "idx_draft_prospects_unit_id" ON "draft_prospects" ("unit_id");

CREATE TRIGGER "draft_prospects_no_update" BEFORE UPDATE ON "draft_prospects" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospects_no_delete" BEFORE DELETE ON "draft_prospects" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospects_successful_unit" BEFORE INSERT ON "draft_prospects" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_pool_slot_observations" (
  "pool_slot_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_row_index" INTEGER NOT NULL,
  "slot_state" TEXT NOT NULL,
  "native_prospect_id" TEXT,
  "display_name" TEXT,
  "draft_year" INTEGER,
  "class_year_status" TEXT NOT NULL,
  UNIQUE ("unit_id","source_row_index")
) STRICT;

CREATE INDEX "idx_draft_pool_slot_observations_unit_id" ON "draft_pool_slot_observations" ("unit_id");

CREATE TRIGGER "draft_pool_slot_observations_no_update" BEFORE UPDATE ON "draft_pool_slot_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_pool_slot_observations_no_delete" BEFORE DELETE ON "draft_pool_slot_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_pool_slot_observations_successful_unit" BEFORE INSERT ON "draft_pool_slot_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_prospect_attribute_snapshots" (
  "snapshot_id" TEXT NOT NULL PRIMARY KEY,
  "prospect_id" TEXT NOT NULL REFERENCES draft_prospects(prospect_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "overall_raw" INTEGER,
  "driving_layup_raw" INTEGER,
  "post_fadeaway_raw" INTEGER,
  "post_hook_raw" INTEGER,
  "post_moves_raw" INTEGER,
  "draw_foul_raw" INTEGER,
  "shot_close_raw" INTEGER,
  "mid_range_shot_raw" INTEGER,
  "three_point_shot_raw" INTEGER,
  "free_throw_raw" INTEGER,
  "ball_control_raw" INTEGER,
  "passing_iq_raw" INTEGER,
  "passing_accuracy_raw" INTEGER,
  "offensive_rebound_raw" INTEGER,
  "standing_dunk_raw" INTEGER,
  "driving_dunk_raw" INTEGER,
  "shot_iq_raw" INTEGER,
  "passing_vision_raw" INTEGER,
  "hands_raw" INTEGER,
  "defensive_rebound_raw" INTEGER,
  "interior_defense_raw" INTEGER,
  "perimeter_defense_raw" INTEGER,
  "block_raw" INTEGER,
  "steal_raw" INTEGER,
  "shot_contest_raw" INTEGER,
  "lateral_quickness_raw" INTEGER,
  "speed_raw" INTEGER,
  "speed_with_ball_raw" INTEGER,
  "acceleration_raw" INTEGER,
  "vertical_raw" INTEGER,
  "strength_raw" INTEGER,
  "stamina_raw" INTEGER,
  "hustle_raw" INTEGER,
  "head_durability_raw" INTEGER,
  "neck_durability_raw" INTEGER,
  "back_durability_raw" INTEGER,
  "left_shoulder_durability_raw" INTEGER,
  "right_shoulder_durability_raw" INTEGER,
  "left_elbow_durability_raw" INTEGER,
  "right_elbow_durability_raw" INTEGER,
  "left_hip_durability_raw" INTEGER,
  "right_hip_durability_raw" INTEGER,
  "left_knee_durability_raw" INTEGER,
  "right_knee_durability_raw" INTEGER,
  "left_ankle_durability_raw" INTEGER,
  "right_ankle_durability_raw" INTEGER,
  "left_foot_durability_raw" INTEGER,
  "right_foot_durability_raw" INTEGER,
  "misc_durability_raw" INTEGER,
  "pass_perception_raw" INTEGER,
  "defensive_consistency_raw" INTEGER,
  "help_defensive_iq_raw" INTEGER,
  "offensive_consistency_raw" INTEGER,
  "pick_and_roll_defensive_iq_raw" INTEGER,
  "intangibles_raw" INTEGER,
  UNIQUE ("prospect_id","unit_id")
) STRICT;

CREATE INDEX "idx_draft_prospect_attribute_snapshots_prospect_id" ON "draft_prospect_attribute_snapshots" ("prospect_id");

CREATE INDEX "idx_draft_prospect_attribute_snapshots_unit_id" ON "draft_prospect_attribute_snapshots" ("unit_id");

CREATE TRIGGER "draft_prospect_attribute_snapshots_no_update" BEFORE UPDATE ON "draft_prospect_attribute_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_attribute_snapshots_no_delete" BEFORE DELETE ON "draft_prospect_attribute_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_attribute_snapshots_successful_unit" BEFORE INSERT ON "draft_prospect_attribute_snapshots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_prospect_tendency_snapshots" (
  "snapshot_id" TEXT NOT NULL PRIMARY KEY,
  "prospect_id" TEXT NOT NULL REFERENCES draft_prospects(prospect_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "shot_tendency_raw" INTEGER,
  "drive_tendency_raw" INTEGER,
  "driving_layup_tendency_raw" INTEGER,
  "standing_dunk_tendency_raw" INTEGER,
  "driving_dunk_tendency_raw" INTEGER,
  "flashy_dunk_tendency_raw" INTEGER,
  "alley_oop_tendency_raw" INTEGER,
  "putback_tendency_raw" INTEGER,
  "crash_tendency_raw" INTEGER,
  "spin_layup_tendency_raw" INTEGER,
  "hop_step_layup_tendency_raw" INTEGER,
  "euro_step_layup_tendency_raw" INTEGER,
  "floater_tendency_raw" INTEGER,
  "step_through_shot_tendency_raw" INTEGER,
  "shot_under_basket_tendency_raw" INTEGER,
  "shot_close_tendency_raw" INTEGER,
  "shot_mid_range_tendency_raw" INTEGER,
  "spot_up_shot_mid_range_raw" INTEGER,
  "off_screen_shot_mid_range_raw" INTEGER,
  "shot_three_tendency_raw" INTEGER,
  "spot_up_shot_three_raw" INTEGER,
  "off_screen_shot_three_raw" INTEGER,
  "contested_jumper_three_raw" INTEGER,
  "contested_jumper_mid_range_raw" INTEGER,
  "stepback_jumper_three_raw" INTEGER,
  "stepback_jumper_mid_range_raw" INTEGER,
  "spin_jumper_tendency_raw" INTEGER,
  "transition_pull_up_three_raw" INTEGER,
  "drive_pull_up_three_raw" INTEGER,
  "drive_pull_up_mid_range_raw" INTEGER,
  "spot_up_drive_tendency_raw" INTEGER,
  "off_screen_drive_tendency_raw" INTEGER,
  "attack_strong_on_drive_raw" INTEGER,
  "dish_to_open_man_tendency_raw" INTEGER,
  "touches_tendency_raw" INTEGER,
  "post_up_tendency_raw" INTEGER,
  "roll_vs_pop_tendency_raw" INTEGER,
  "transition_spot_up_raw" INTEGER,
  "play_discipline_tendency_raw" INTEGER,
  "flashy_pass_tendency_raw" INTEGER,
  "alley_oop_pass_tendency_raw" INTEGER,
  "pass_interception_tendency_raw" INTEGER,
  "take_charge_tendency_raw" INTEGER,
  "on_ball_steal_tendency_raw" INTEGER,
  "contest_shot_tendency_raw" INTEGER,
  "block_shot_tendency_raw" INTEGER,
  "foul_tendency_raw" INTEGER,
  "hard_foul_tendency_raw" INTEGER,
  UNIQUE ("prospect_id","unit_id")
) STRICT;

CREATE INDEX "idx_draft_prospect_tendency_snapshots_prospect_id" ON "draft_prospect_tendency_snapshots" ("prospect_id");

CREATE INDEX "idx_draft_prospect_tendency_snapshots_unit_id" ON "draft_prospect_tendency_snapshots" ("unit_id");

CREATE TRIGGER "draft_prospect_tendency_snapshots_no_update" BEFORE UPDATE ON "draft_prospect_tendency_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_tendency_snapshots_no_delete" BEFORE DELETE ON "draft_prospect_tendency_snapshots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_tendency_snapshots_successful_unit" BEFORE INSERT ON "draft_prospect_tendency_snapshots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_prospect_play_type_slots" (
  "slot_id" TEXT NOT NULL PRIMARY KEY,
  "prospect_id" TEXT NOT NULL REFERENCES draft_prospects(prospect_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL CHECK (slot_index>=0),
  "native_play_code" TEXT,
  UNIQUE ("prospect_id","unit_id","slot_index")
) STRICT;

CREATE INDEX "idx_draft_prospect_play_type_slots_prospect_id" ON "draft_prospect_play_type_slots" ("prospect_id");

CREATE INDEX "idx_draft_prospect_play_type_slots_unit_id" ON "draft_prospect_play_type_slots" ("unit_id");

CREATE TRIGGER "draft_prospect_play_type_slots_no_update" BEFORE UPDATE ON "draft_prospect_play_type_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_play_type_slots_no_delete" BEFORE DELETE ON "draft_prospect_play_type_slots" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_prospect_play_type_slots_successful_unit" BEFORE INSERT ON "draft_prospect_play_type_slots" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "waived_salary_observations" (
  "waived_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_row_index" INTEGER NOT NULL,
  "owner_mapping_status" TEXT NOT NULL,
  "native_player_id" INTEGER,
  "observed_player_name" TEXT,
  "player_mapping_status" TEXT NOT NULL,
  "name_source_status" TEXT NOT NULL,
  "salary_year_1_raw" INTEGER,
  "salary_year_2_raw" INTEGER,
  "salary_year_3_raw" INTEGER,
  UNIQUE ("unit_id","source_row_index")
) STRICT;

CREATE INDEX "idx_waived_salary_observations_team_id" ON "waived_salary_observations" ("team_id");

CREATE INDEX "idx_waived_salary_observations_player_id" ON "waived_salary_observations" ("player_id");

CREATE INDEX "idx_waived_salary_observations_unit_id" ON "waived_salary_observations" ("unit_id");

CREATE TRIGGER "waived_salary_observations_no_update" BEFORE UPDATE ON "waived_salary_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "waived_salary_observations_no_delete" BEFORE DELETE ON "waived_salary_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "waived_salary_observations_successful_unit" BEFORE INSERT ON "waived_salary_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "draft_results" (
  "result_id" TEXT NOT NULL PRIMARY KEY,
  "prospect_id" TEXT REFERENCES draft_prospects(prospect_id) ON DELETE RESTRICT,
  "pick_id" TEXT REFERENCES draft_pick_assets(pick_id) ON DELETE RESTRICT,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_ref" TEXT NOT NULL,
  "selection_number" INTEGER
) STRICT;

CREATE INDEX "idx_draft_results_prospect_id" ON "draft_results" ("prospect_id");

CREATE INDEX "idx_draft_results_pick_id" ON "draft_results" ("pick_id");

CREATE INDEX "idx_draft_results_team_id" ON "draft_results" ("team_id");

CREATE INDEX "idx_draft_results_player_id" ON "draft_results" ("player_id");

CREATE INDEX "idx_draft_results_unit_id" ON "draft_results" ("unit_id");

CREATE TRIGGER "draft_results_no_update" BEFORE UPDATE ON "draft_results" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_results_no_delete" BEFORE DELETE ON "draft_results" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "draft_results_successful_unit" BEFORE INSERT ON "draft_results" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "worldline_config_versions" (
  "config_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "config_version" TEXT NOT NULL,
  "config_hash" TEXT NOT NULL,
  "approval_ref" TEXT,
  UNIQUE ("config_version")
) STRICT;

CREATE INDEX "idx_worldline_config_versions_save_id" ON "worldline_config_versions" ("save_id");

CREATE INDEX "idx_worldline_config_versions_unit_id" ON "worldline_config_versions" ("unit_id");

CREATE TRIGGER "worldline_config_versions_no_update" BEFORE UPDATE ON "worldline_config_versions" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "worldline_config_versions_no_delete" BEFORE DELETE ON "worldline_config_versions" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "worldline_config_versions_successful_unit" BEFORE INSERT ON "worldline_config_versions" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "game_setting_observations" (
  "setting_obs_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "field_id" TEXT NOT NULL REFERENCES native_fields(field_id) ON DELETE RESTRICT,
  "scope_code" TEXT NOT NULL,
  "integer_value" INTEGER,
  "real_value" REAL,
  "text_value" TEXT,
  "display_value" TEXT,
  "logical_key" TEXT,
  "raw_word_u32" INTEGER CHECK (raw_word_u32 BETWEEN 0 AND 4294967295),
  "value_status" TEXT,
  "semantic_status" TEXT,
  "registered_range_status" TEXT,
  "aliases_json" TEXT,
  UNIQUE ("unit_id","field_id","scope_code"),
  CHECK ((integer_value IS NOT NULL)+(real_value IS NOT NULL)+(text_value IS NOT NULL)=1)
) STRICT;

CREATE INDEX "idx_game_setting_observations_unit_id" ON "game_setting_observations" ("unit_id");

CREATE INDEX "idx_game_setting_observations_field_id" ON "game_setting_observations" ("field_id");

CREATE TRIGGER "game_setting_observations_no_update" BEFORE UPDATE ON "game_setting_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_setting_observations_no_delete" BEFORE DELETE ON "game_setting_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_setting_observations_successful_unit" BEFORE INSERT ON "game_setting_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "startup_config_checks" (
  "check_id" TEXT NOT NULL PRIMARY KEY,
  "config_id" TEXT REFERENCES worldline_config_versions(config_id) ON DELETE RESTRICT,
  "setting_obs_id" TEXT REFERENCES game_setting_observations(setting_obs_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "result" TEXT NOT NULL,
  "dependency_ref" TEXT
) STRICT;

CREATE INDEX "idx_startup_config_checks_config_id" ON "startup_config_checks" ("config_id");

CREATE INDEX "idx_startup_config_checks_setting_obs_id" ON "startup_config_checks" ("setting_obs_id");

CREATE INDEX "idx_startup_config_checks_unit_id" ON "startup_config_checks" ("unit_id");

CREATE TRIGGER "startup_config_checks_no_update" BEFORE UPDATE ON "startup_config_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "startup_config_checks_no_delete" BEFORE DELETE ON "startup_config_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "startup_config_checks_successful_unit" BEFORE INSERT ON "startup_config_checks" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "league_rule_observations" (
  "rule_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "rule_key" TEXT NOT NULL,
  "integer_value" INTEGER,
  "text_value" TEXT,
  "display_value" TEXT,
  "real_value" REAL,
  "setting_obs_id" TEXT REFERENCES game_setting_observations(setting_obs_id) ON DELETE RESTRICT,
  UNIQUE ("season_id","unit_id","rule_key")
) STRICT;

CREATE INDEX "idx_league_rule_observations_season_id" ON "league_rule_observations" ("season_id");

CREATE INDEX "idx_league_rule_observations_unit_id" ON "league_rule_observations" ("unit_id");

CREATE INDEX "idx_league_rule_observations_setting_obs_id" ON "league_rule_observations" ("setting_obs_id");

CREATE TRIGGER "league_rule_observations_no_update" BEFORE UPDATE ON "league_rule_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "league_rule_observations_no_delete" BEFORE DELETE ON "league_rule_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "league_rule_observations_successful_unit" BEFORE INSERT ON "league_rule_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_league_history_observations" (
  "history_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_row_index" INTEGER NOT NULL CHECK (source_row_index>=0),
  "native_type_code" INTEGER NOT NULL CHECK (native_type_code BETWEEN 0 AND 4294967295),
  "primary_team_id_raw" INTEGER NOT NULL CHECK (primary_team_id_raw BETWEEN 0 AND 65535),
  "secondary_team_id_raw" INTEGER NOT NULL CHECK (secondary_team_id_raw BETWEEN 0 AND 65535),
  "next_free_raw" INTEGER NOT NULL CHECK (next_free_raw BETWEEN 0 AND 65535),
  "player_id_raw" INTEGER NOT NULL CHECK (player_id_raw BETWEEN 0 AND 65535),
  "native_year_raw" INTEGER NOT NULL CHECK (native_year_raw BETWEEN 0 AND 4095),
  "primary_team_name" TEXT,
  "primary_team_city" TEXT,
  "secondary_team_name" TEXT,
  "secondary_team_city" TEXT,
  "player_first_name" TEXT,
  "player_last_name" TEXT,
  "native_type_label" TEXT,
  "primary_stat_word_raw" INTEGER NOT NULL CHECK (primary_stat_word_raw BETWEEN 0 AND 4294967295),
  "primary_stat_real" REAL,
  "primary_stat_text" TEXT NOT NULL,
  "secondary_stat_word_raw" INTEGER NOT NULL CHECK (secondary_stat_word_raw BETWEEN 0 AND 4294967295),
  "secondary_stat_real" REAL,
  "secondary_stat_text" TEXT NOT NULL,
  "source_state" TEXT NOT NULL,
  "text_status" TEXT NOT NULL,
  "award_id" TEXT REFERENCES season_award_instances(award_id) ON DELETE RESTRICT,
  "award_link_status" TEXT NOT NULL,
  UNIQUE ("unit_id","source_row_index")
) STRICT;

CREATE INDEX "idx_native_league_history_observations_unit_id" ON "native_league_history_observations" ("unit_id");

CREATE INDEX "idx_native_league_history_observations_award_id" ON "native_league_history_observations" ("award_id");

CREATE TRIGGER "native_league_history_observations_no_update" BEFORE UPDATE ON "native_league_history_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_league_history_observations_no_delete" BEFORE DELETE ON "native_league_history_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_league_history_observations_successful_unit" BEFORE INSERT ON "native_league_history_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "season_award_instances" (
  "award_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "award_code" TEXT NOT NULL,
  "award_type" TEXT NOT NULL,
  "is_final" INTEGER NOT NULL CHECK (is_final=1),
  "source_year_raw" INTEGER CHECK (source_year_raw BETWEEN 1 AND 4095),
  "source_fingerprint" TEXT,
  "finality_basis" TEXT,
  UNIQUE ("season_id","award_code","award_type")
) STRICT;

CREATE INDEX "idx_season_award_instances_season_id" ON "season_award_instances" ("season_id");

CREATE INDEX "idx_season_award_instances_unit_id" ON "season_award_instances" ("unit_id");

CREATE TRIGGER "season_award_instances_no_update" BEFORE UPDATE ON "season_award_instances" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_award_instances_no_delete" BEFORE DELETE ON "season_award_instances" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_award_instances_successful_unit" BEFORE INSERT ON "season_award_instances" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "award_recipients" (
  "recipient_id" TEXT NOT NULL PRIMARY KEY,
  "award_id" TEXT NOT NULL REFERENCES season_award_instances(award_id) ON DELETE RESTRICT,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "rank_index" INTEGER,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "staff_id" TEXT REFERENCES staff_members(staff_id) ON DELETE RESTRICT,
  "source_history_id" TEXT REFERENCES native_league_history_observations(history_observation_id) ON DELETE RESTRICT,
  "source_subject_type" TEXT CHECK (source_subject_type IN ('PLAYER','TEAM','STAFF')),
  CHECK (player_id IS NOT NULL OR team_id IS NOT NULL OR staff_id IS NOT NULL OR source_history_id IS NOT NULL)
) STRICT;

CREATE INDEX "idx_award_recipients_award_id" ON "award_recipients" ("award_id");

CREATE INDEX "idx_award_recipients_player_id" ON "award_recipients" ("player_id");

CREATE INDEX "idx_award_recipients_team_id" ON "award_recipients" ("team_id");

CREATE INDEX "idx_award_recipients_unit_id" ON "award_recipients" ("unit_id");

CREATE INDEX "idx_award_recipients_staff_id" ON "award_recipients" ("staff_id");

CREATE INDEX "idx_award_recipients_source_history_id" ON "award_recipients" ("source_history_id");

CREATE TRIGGER "award_recipients_no_update" BEFORE UPDATE ON "award_recipients" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "award_recipients_no_delete" BEFORE DELETE ON "award_recipients" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "award_recipients_successful_unit" BEFORE INSERT ON "award_recipients" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_social_message_observations" (
  "message_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "bank_index" INTEGER NOT NULL CHECK (bank_index BETWEEN 0 AND 1),
  "source_slot_index" INTEGER NOT NULL CHECK (source_slot_index BETWEEN 0 AND 1999),
  "data1_raw" INTEGER NOT NULL CHECK (data1_raw BETWEEN 0 AND 65535),
  "data2_raw" INTEGER NOT NULL CHECK (data2_raw BETWEEN 0 AND 65535),
  "data3_raw" INTEGER NOT NULL CHECK (data3_raw BETWEEN 0 AND 65535),
  "data4_raw" INTEGER NOT NULL CHECK (data4_raw BETWEEN 0 AND 65535),
  "data5_raw" INTEGER NOT NULL CHECK (data5_raw BETWEEN 0 AND 65535),
  "team_id1_raw" INTEGER NOT NULL CHECK (team_id1_raw BETWEEN 0 AND 65535),
  "team_id2_raw" INTEGER NOT NULL CHECK (team_id2_raw BETWEEN 0 AND 65535),
  "sender_index_raw" INTEGER NOT NULL CHECK (sender_index_raw BETWEEN 0 AND 65535),
  "message_index_raw" INTEGER NOT NULL CHECK (message_index_raw BETWEEN 0 AND 65535),
  "game_id_raw" INTEGER NOT NULL CHECK (game_id_raw BETWEEN 0 AND 4294967295),
  "player_index1_raw" INTEGER NOT NULL CHECK (player_index1_raw BETWEEN 0 AND 65535),
  "player_index2_raw" INTEGER NOT NULL CHECK (player_index2_raw BETWEEN 0 AND 65535),
  "data_u32_raw" INTEGER NOT NULL CHECK (data_u32_raw BETWEEN 0 AND 4294967295),
  "sender_index_override_raw" INTEGER NOT NULL CHECK (sender_index_override_raw BETWEEN 0 AND 65535),
  "event_code" INTEGER NOT NULL CHECK (event_code BETWEEN 0 AND 1023),
  "sender_type_raw" INTEGER NOT NULL CHECK (sender_type_raw BETWEEN 0 AND 7),
  "unread_raw" INTEGER NOT NULL CHECK (unread_raw BETWEEN 0 AND 1),
  "sender_active_raw" INTEGER NOT NULL CHECK (sender_active_raw BETWEEN 0 AND 1),
  "score_raw" INTEGER NOT NULL CHECK (score_raw BETWEEN 0 AND 255),
  "random_shares_raw" INTEGER NOT NULL CHECK (random_shares_raw BETWEEN 0 AND 255),
  "sender_location_raw" INTEGER NOT NULL CHECK (sender_location_raw BETWEEN 0 AND 65535),
  "date_word_raw" INTEGER NOT NULL CHECK (date_word_raw BETWEEN 0 AND 4294967295),
  "date_id_raw" INTEGER NOT NULL CHECK (date_id_raw BETWEEN 0 AND 31),
  "date_minutes_raw" INTEGER NOT NULL CHECK (date_minutes_raw BETWEEN 0 AND 2047),
  "date_day_raw" INTEGER NOT NULL CHECK (date_day_raw BETWEEN 0 AND 31),
  "date_month_raw" INTEGER NOT NULL CHECK (date_month_raw BETWEEN 0 AND 15),
  "date_year_offset_raw" INTEGER NOT NULL CHECK (date_year_offset_raw BETWEEN 0 AND 127),
  "event_label" TEXT,
  "sender_type_label" TEXT,
  "string1_fragment" TEXT,
  "string2_fragment" TEXT,
  "text_status" TEXT NOT NULL,
  "source_state" TEXT NOT NULL,
  "active_prefix_status" TEXT NOT NULL,
  UNIQUE ("unit_id","bank_index","source_slot_index")
) STRICT;

CREATE INDEX "idx_native_social_message_observations_unit_id" ON "native_social_message_observations" ("unit_id");

CREATE TRIGGER "native_social_message_observations_no_update" BEFORE UPDATE ON "native_social_message_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_social_message_observations_no_delete" BEFORE DELETE ON "native_social_message_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_social_message_observations_successful_unit" BEFORE INSERT ON "native_social_message_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_transaction_observations" (
  "native_transaction_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_slot_index" INTEGER NOT NULL CHECK (source_slot_index BETWEEN 0 AND 249),
  "native_type_code" INTEGER NOT NULL CHECK (native_type_code BETWEEN 0 AND 15),
  "data_count_raw" INTEGER NOT NULL CHECK (data_count_raw BETWEEN 0 AND 255),
  "date_word_raw" INTEGER NOT NULL CHECK (date_word_raw BETWEEN 0 AND 4294967295),
  "date_id_raw" INTEGER NOT NULL CHECK (date_id_raw BETWEEN 0 AND 31),
  "date_minutes_raw" INTEGER NOT NULL CHECK (date_minutes_raw BETWEEN 0 AND 2047),
  "date_day_raw" INTEGER NOT NULL CHECK (date_day_raw BETWEEN 0 AND 31),
  "date_month_raw" INTEGER NOT NULL CHECK (date_month_raw BETWEEN 0 AND 15),
  "date_year_offset_raw" INTEGER NOT NULL CHECK (date_year_offset_raw BETWEEN 0 AND 127),
  "native_type_label" TEXT,
  "active_prefix_status" TEXT NOT NULL,
  UNIQUE ("unit_id","source_slot_index")
) STRICT;

CREATE INDEX "idx_native_transaction_observations_unit_id" ON "native_transaction_observations" ("unit_id");

CREATE TRIGGER "native_transaction_observations_no_update" BEFORE UPDATE ON "native_transaction_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_transaction_observations_no_delete" BEFORE DELETE ON "native_transaction_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_transaction_observations_successful_unit" BEFORE INSERT ON "native_transaction_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_transaction_item_observations" (
  "item_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "native_transaction_id" TEXT NOT NULL REFERENCES native_transaction_observations(native_transaction_id) ON DELETE RESTRICT,
  "source_item_index" INTEGER NOT NULL CHECK (source_item_index BETWEEN 0 AND 38),
  "integer_word_raw" INTEGER NOT NULL CHECK (integer_word_raw BETWEEN 0 AND 4294967295),
  "native_type_code" INTEGER NOT NULL CHECK (native_type_code BETWEEN 0 AND 7),
  UNIQUE ("unit_id","native_transaction_id","source_item_index")
) STRICT;

CREATE INDEX "idx_native_transaction_item_observations_unit_id" ON "native_transaction_item_observations" ("unit_id");

CREATE INDEX "idx_native_transaction_item_observations_native_transaction_id" ON "native_transaction_item_observations" ("native_transaction_id");

CREATE TRIGGER "native_transaction_item_observations_no_update" BEFORE UPDATE ON "native_transaction_item_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_transaction_item_observations_no_delete" BEFORE DELETE ON "native_transaction_item_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_transaction_item_observations_successful_unit" BEFORE INSERT ON "native_transaction_item_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_award_matrix_observations" (
  "matrix_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "award_slot_index" INTEGER NOT NULL CHECK (award_slot_index BETWEEN 0 AND 14),
  "recipient_slot_index" INTEGER NOT NULL CHECK (recipient_slot_index BETWEEN 0 AND 4),
  "native_player_index_raw" INTEGER NOT NULL CHECK (native_player_index_raw BETWEEN 0 AND 65535),
  UNIQUE ("unit_id","award_slot_index","recipient_slot_index")
) STRICT;

CREATE INDEX "idx_native_award_matrix_observations_unit_id" ON "native_award_matrix_observations" ("unit_id");

CREATE TRIGGER "native_award_matrix_observations_no_update" BEFORE UPDATE ON "native_award_matrix_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_award_matrix_observations_no_delete" BEFORE DELETE ON "native_award_matrix_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_award_matrix_observations_successful_unit" BEFORE INSERT ON "native_award_matrix_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_league_capture_controls" (
  "control_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_mode" TEXT NOT NULL CHECK (source_mode IN ('HISTORY_AWARDS','NEWS_TRANSACTIONS')),
  "observation_year" INTEGER NOT NULL,
  "history_slot_count" INTEGER,
  "manager_first_free_candidate" INTEGER,
  "free_chain_status" TEXT,
  "free_chain_count" INTEGER,
  "social_active_count0" INTEGER,
  "social_active_count1" INTEGER,
  "transaction_count" INTEGER,
  "matrix_cell_count" INTEGER,
  UNIQUE ("unit_id")
) STRICT;

CREATE INDEX "idx_native_league_capture_controls_unit_id" ON "native_league_capture_controls" ("unit_id");

CREATE TRIGGER "native_league_capture_controls_no_update" BEFORE UPDATE ON "native_league_capture_controls" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_league_capture_controls_no_delete" BEFORE DELETE ON "native_league_capture_controls" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_league_capture_controls_successful_unit" BEFORE INSERT ON "native_league_capture_controls" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "season_record_entries" (
  "record_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "record_key" TEXT NOT NULL,
  "holder_player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "holder_team_id" TEXT REFERENCES teams(team_id) ON DELETE RESTRICT,
  "value_raw" TEXT NOT NULL,
  "source_ref" TEXT NOT NULL,
  "occurred_at" TEXT,
  "observed_in_season_id" TEXT REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "source_row_index" INTEGER CHECK (source_row_index>=0),
  "source_first_name" TEXT,
  "source_last_name" TEXT,
  "native_value_word_u32" INTEGER CHECK (native_value_word_u32 BETWEEN 0 AND 4294967295),
  "native_value_real" REAL,
  "packed_date_raw" INTEGER CHECK (packed_date_raw BETWEEN 0 AND 65535),
  "native_category_code" INTEGER CHECK (native_category_code BETWEEN 0 AND 65535),
  "category_label_candidate" TEXT,
  "native_player_id_raw" INTEGER CHECK (native_player_id_raw BETWEEN 0 AND 65535),
  "flags_raw" INTEGER CHECK (flags_raw BETWEEN 0 AND 65535),
  "decode_status" TEXT,
  "name_encoding_status" TEXT,
  "record_date_candidate" TEXT,
  "date_interpretation_status" TEXT,
  "source_scope_status" TEXT,
  UNIQUE ("unit_id","source_row_index")
) STRICT;

CREATE INDEX "idx_season_record_entries_season_id" ON "season_record_entries" ("season_id");

CREATE INDEX "idx_season_record_entries_unit_id" ON "season_record_entries" ("unit_id");

CREATE INDEX "idx_season_record_entries_holder_player_id" ON "season_record_entries" ("holder_player_id");

CREATE INDEX "idx_season_record_entries_holder_team_id" ON "season_record_entries" ("holder_team_id");

CREATE INDEX "idx_season_record_entries_observed_in_season_id" ON "season_record_entries" ("observed_in_season_id");

CREATE TRIGGER "season_record_entries_no_update" BEFORE UPDATE ON "season_record_entries" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_record_entries_no_delete" BEFORE DELETE ON "season_record_entries" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_record_entries_successful_unit" BEFORE INSERT ON "season_record_entries" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "external_execution_receipts" (
  "receipt_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "transaction_id" TEXT REFERENCES external_transaction_events(transaction_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "attempted_at" TEXT NOT NULL,
  "write_status" TEXT NOT NULL,
  "source_ref" TEXT NOT NULL,
  "approval_ref" TEXT
) STRICT;

CREATE INDEX "idx_external_execution_receipts_save_id" ON "external_execution_receipts" ("save_id");

CREATE INDEX "idx_external_execution_receipts_transaction_id" ON "external_execution_receipts" ("transaction_id");

CREATE INDEX "idx_external_execution_receipts_unit_id" ON "external_execution_receipts" ("unit_id");

CREATE TRIGGER "external_execution_receipts_no_update" BEFORE UPDATE ON "external_execution_receipts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_execution_receipts_no_delete" BEFORE DELETE ON "external_execution_receipts" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_execution_receipts_successful_unit" BEFORE INSERT ON "external_execution_receipts" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "external_readback_checks" (
  "check_id" TEXT NOT NULL PRIMARY KEY,
  "receipt_id" TEXT NOT NULL REFERENCES external_execution_receipts(receipt_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "expected_state" TEXT NOT NULL,
  "observed_state" TEXT,
  "reconcile_status" TEXT NOT NULL
) STRICT;

CREATE INDEX "idx_external_readback_checks_receipt_id" ON "external_readback_checks" ("receipt_id");

CREATE INDEX "idx_external_readback_checks_unit_id" ON "external_readback_checks" ("unit_id");

CREATE TRIGGER "external_readback_checks_no_update" BEFORE UPDATE ON "external_readback_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_readback_checks_no_delete" BEFORE DELETE ON "external_readback_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "external_readback_checks_successful_unit" BEFORE INSERT ON "external_readback_checks" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_identity_links" (
  "link_id" TEXT NOT NULL PRIMARY KEY,
  "save_id" TEXT NOT NULL REFERENCES saves(save_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "entity_type" TEXT NOT NULL CHECK (entity_type IN ('player','team','game','staff')),
  "entity_id" TEXT NOT NULL,
  "native_id" TEXT,
  "valid_from" TEXT,
  "identity_state" TEXT NOT NULL
) STRICT;

CREATE INDEX "idx_native_identity_links_save_id" ON "native_identity_links" ("save_id");

CREATE INDEX "idx_native_identity_links_unit_id" ON "native_identity_links" ("unit_id");

CREATE TRIGGER "native_identity_links_no_update" BEFORE UPDATE ON "native_identity_links" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_identity_links_no_delete" BEFORE DELETE ON "native_identity_links" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_identity_links_successful_unit" BEFORE INSERT ON "native_identity_links" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_restricted_observations" (
  "observation_id" TEXT NOT NULL PRIMARY KEY,
  "player_id" TEXT NOT NULL REFERENCES players(player_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "restricted_field_key" TEXT NOT NULL,
  "protected_value_ref" TEXT NOT NULL,
  "authorization_scope" TEXT NOT NULL
) STRICT;

CREATE INDEX "idx_player_restricted_observations_player_id" ON "player_restricted_observations" ("player_id");

CREATE INDEX "idx_player_restricted_observations_unit_id" ON "player_restricted_observations" ("unit_id");

CREATE TRIGGER "player_restricted_observations_no_update" BEFORE UPDATE ON "player_restricted_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_restricted_observations_no_delete" BEFORE DELETE ON "player_restricted_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_restricted_observations_successful_unit" BEFORE INSERT ON "player_restricted_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "game_news_entries" (
  "news_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "native_news_id" TEXT,
  "text_body" TEXT,
  "occurrence_time" TEXT,
  "source_message_id" TEXT REFERENCES native_social_message_observations(message_observation_id) ON DELETE RESTRICT,
  "content_status" TEXT
) STRICT;

CREATE INDEX "idx_game_news_entries_season_id" ON "game_news_entries" ("season_id");

CREATE INDEX "idx_game_news_entries_unit_id" ON "game_news_entries" ("unit_id");

CREATE INDEX "idx_game_news_entries_source_message_id" ON "game_news_entries" ("source_message_id");

CREATE TRIGGER "game_news_entries_no_update" BEFORE UPDATE ON "game_news_entries" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_news_entries_no_delete" BEFORE DELETE ON "game_news_entries" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_news_entries_successful_unit" BEFORE INSERT ON "game_news_entries" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "season_finalizations" (
  "finalization_id" TEXT NOT NULL PRIMARY KEY,
  "season_id" TEXT NOT NULL REFERENCES seasons(season_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_ref" TEXT NOT NULL,
  "finalized_at" TEXT NOT NULL,
  UNIQUE ("season_id")
) STRICT;

CREATE INDEX "idx_season_finalizations_season_id" ON "season_finalizations" ("season_id");

CREATE INDEX "idx_season_finalizations_unit_id" ON "season_finalizations" ("unit_id");

CREATE TRIGGER "season_finalizations_no_update" BEFORE UPDATE ON "season_finalizations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_finalizations_no_delete" BEFORE DELETE ON "season_finalizations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "season_finalizations_successful_unit" BEFORE INSERT ON "season_finalizations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_box_observations" (
  "box_observation_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "side" TEXT NOT NULL CHECK (side IN ('HOME','AWAY')),
  "row_index" INTEGER NOT NULL CHECK (row_index>=0),
  "native_player_id" INTEGER NOT NULL,
  "native_team_id" INTEGER NOT NULL,
  "in_use" INTEGER NOT NULL CHECK (in_use IN (0,1)),
  "points" INTEGER,
  "fg_made" INTEGER,
  "fg_attempted" INTEGER,
  "three_made" INTEGER,
  "three_attempted" INTEGER,
  "ft_made" INTEGER,
  "ft_attempted" INTEGER,
  "offensive_rebounds" INTEGER,
  "defensive_rebounds" INTEGER,
  "assists" INTEGER,
  "steals" INTEGER,
  "blocks" INTEGER,
  "turnovers" INTEGER,
  "fouls" INTEGER,
  "minutes_raw" INTEGER,
  "plus_minus" INTEGER,
  "possessions_raw" INTEGER,
  "points_provenance" TEXT NOT NULL,
  "identity_status" TEXT NOT NULL DEFAULT 'UNRESOLVED',
  UNIQUE ("game_id","unit_id","side","row_index")
) STRICT;

CREATE INDEX "idx_native_box_observations_game_id" ON "native_box_observations" ("game_id");

CREATE INDEX "idx_native_box_observations_unit_id" ON "native_box_observations" ("unit_id");

CREATE TRIGGER "native_box_observations_no_update" BEFORE UPDATE ON "native_box_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_box_observations_no_delete" BEFORE DELETE ON "native_box_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_box_observations_successful_unit" BEFORE INSERT ON "native_box_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "game_source_checks" (
  "check_id" TEXT NOT NULL PRIMARY KEY,
  "game_id" TEXT NOT NULL REFERENCES games(game_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "header_sha256" TEXT NOT NULL CHECK (length(header_sha256)=64),
  "box_sha256" TEXT CHECK (box_sha256 IS NULL OR length(box_sha256)=64),
  "box_mode" TEXT NOT NULL CHECK (box_mode IN ('FULL_NATIVE_BOX','REUSED_FROZEN_BOX','HEADER_ONLY_NOT_FINAL')),
  "prior_full_unit_id" TEXT REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "game_status_raw" INTEGER NOT NULL CHECK (game_status_raw IN (0,1,2)),
  "reuse_basis" TEXT NOT NULL,
  UNIQUE ("game_id","unit_id"),
  CHECK ((box_mode='FULL_NATIVE_BOX' AND box_sha256 IS NOT NULL AND prior_full_unit_id IS NULL AND game_status_raw=2) OR (box_mode='REUSED_FROZEN_BOX' AND box_sha256 IS NULL AND prior_full_unit_id IS NOT NULL AND game_status_raw=2) OR (box_mode='HEADER_ONLY_NOT_FINAL' AND box_sha256 IS NULL AND prior_full_unit_id IS NULL AND game_status_raw IN (0,1)))
) STRICT;

CREATE INDEX "idx_game_source_checks_game_id" ON "game_source_checks" ("game_id");

CREATE INDEX "idx_game_source_checks_unit_id" ON "game_source_checks" ("unit_id");

CREATE INDEX "idx_game_source_checks_prior_full_unit_id" ON "game_source_checks" ("prior_full_unit_id");

CREATE TRIGGER "game_source_checks_no_update" BEFORE UPDATE ON "game_source_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_source_checks_no_delete" BEFORE DELETE ON "game_source_checks" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "game_source_checks_successful_unit" BEFORE INSERT ON "game_source_checks" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_player_stat_observations" (
  "stat_observation_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_stat_index" INTEGER NOT NULL CHECK (source_stat_index>=0),
  "stat_year" INTEGER,
  "scoring_identity_status" TEXT,
  "primary_team_id_raw" INTEGER CHECK (primary_team_id_raw BETWEEN 0 AND 65535),
  "secondary_team_id_raw" INTEGER CHECK (secondary_team_id_raw BETWEEN 0 AND 65535),
  "jersey_number_raw" INTEGER CHECK (jersey_number_raw BETWEEN 0 AND 255),
  "compact_year_raw" INTEGER CHECK (compact_year_raw BETWEEN 0 AND 255),
  "next_free_raw" INTEGER CHECK (next_free_raw BETWEEN 0 AND 65535),
  "games_played_raw" INTEGER CHECK (games_played_raw BETWEEN 0 AND 127),
  "mvp_raw" INTEGER CHECK (mvp_raw BETWEEN 0 AND 1),
  "triple_doubles_raw" INTEGER CHECK (triple_doubles_raw BETWEEN 0 AND 127),
  "fg_attempted_raw" INTEGER CHECK (fg_attempted_raw BETWEEN 0 AND 8191),
  "all_nba_rank_raw" INTEGER CHECK (all_nba_rank_raw BETWEEN 0 AND 3),
  "all_defensive_rank_raw" INTEGER CHECK (all_defensive_rank_raw BETWEEN 0 AND 3),
  "games_started_raw" INTEGER CHECK (games_started_raw BETWEEN 0 AND 127),
  "minutes_raw" INTEGER CHECK (minutes_raw BETWEEN 0 AND 8191),
  "fg_made_raw" INTEGER CHECK (fg_made_raw BETWEEN 0 AND 4095),
  "steals_raw" INTEGER CHECK (steals_raw BETWEEN 0 AND 2047),
  "blocks_raw" INTEGER CHECK (blocks_raw BETWEEN 0 AND 2047),
  "fouls_raw" INTEGER CHECK (fouls_raw BETWEEN 0 AND 1023),
  "ft_made_raw" INTEGER CHECK (ft_made_raw BETWEEN 0 AND 2047),
  "ft_attempted_raw" INTEGER CHECK (ft_attempted_raw BETWEEN 0 AND 2047),
  "offensive_rebounds_raw" INTEGER CHECK (offensive_rebounds_raw BETWEEN 0 AND 1023),
  "three_attempted_raw" INTEGER CHECK (three_attempted_raw BETWEEN 0 AND 2047),
  "assists_raw" INTEGER CHECK (assists_raw BETWEEN 0 AND 2047),
  "three_made_raw" INTEGER CHECK (three_made_raw BETWEEN 0 AND 1023),
  "defensive_rebounds_raw" INTEGER CHECK (defensive_rebounds_raw BETWEEN 0 AND 32767),
  "turnovers_raw" INTEGER CHECK (turnovers_raw BETWEEN 0 AND 32767),
  "champion_raw" INTEGER CHECK (champion_raw BETWEEN 0 AND 1),
  "finals_mvp_raw" INTEGER CHECK (finals_mvp_raw BETWEEN 0 AND 1),
  "points_raw" INTEGER CHECK (points_raw BETWEEN 0 AND 65535),
  "plus_minus_word_raw" INTEGER CHECK (plus_minus_word_raw BETWEEN 0 AND 65535),
  "points_allowed_raw" INTEGER CHECK (points_allowed_raw BETWEEN 0 AND 65535),
  "possessions_raw" INTEGER CHECK (possessions_raw BETWEEN 0 AND 65535),
  "defensive_fg_made_raw" INTEGER CHECK (defensive_fg_made_raw BETWEEN 0 AND 4095),
  "defensive_fg_attempted_raw" INTEGER CHECK (defensive_fg_attempted_raw BETWEEN 0 AND 8191),
  "double_doubles_raw" INTEGER CHECK (double_doubles_raw BETWEEN 0 AND 127),
  "forty_point_games_raw" INTEGER CHECK (forty_point_games_raw BETWEEN 0 AND 127),
  "fifty_point_games_raw" INTEGER CHECK (fifty_point_games_raw BETWEEN 0 AND 127),
  "all_rookie_rank_raw" INTEGER CHECK (all_rookie_rank_raw BETWEEN 0 AND 3),
  "all_star_starter_raw" INTEGER CHECK (all_star_starter_raw BETWEEN 0 AND 1),
  "all_star_reserve_raw" INTEGER CHECK (all_star_reserve_raw BETWEEN 0 AND 1),
  "rookie_of_year_raw" INTEGER CHECK (rookie_of_year_raw BETWEEN 0 AND 1),
  "sixth_man_raw" INTEGER CHECK (sixth_man_raw BETWEEN 0 AND 1),
  "defensive_player_raw" INTEGER CHECK (defensive_player_raw BETWEEN 0 AND 1),
  "most_improved_raw" INTEGER CHECK (most_improved_raw BETWEEN 0 AND 1),
  "reference_count_raw" INTEGER CHECK (reference_count_raw BETWEEN 0 AND 255),
  UNIQUE ("unit_id","source_stat_index")
) STRICT;

CREATE INDEX "idx_native_player_stat_observations_unit_id" ON "native_player_stat_observations" ("unit_id");

CREATE TRIGGER "native_player_stat_observations_no_update" BEFORE UPDATE ON "native_player_stat_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_stat_observations_no_delete" BEFORE DELETE ON "native_player_stat_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_stat_observations_successful_unit" BEFORE INSERT ON "native_player_stat_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_player_stat_links" (
  "stat_link_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "player_source_id" TEXT NOT NULL REFERENCES native_player_sources(player_source_id) ON DELETE RESTRICT,
  "history_slot_index" INTEGER NOT NULL CHECK (history_slot_index>=0),
  "native_stat_index_raw" INTEGER NOT NULL CHECK (native_stat_index_raw BETWEEN 0 AND 65535),
  "stat_observation_id" TEXT REFERENCES native_player_stat_observations(stat_observation_id) ON DELETE RESTRICT,
  "link_status" TEXT NOT NULL,
  UNIQUE ("unit_id","player_source_id","history_slot_index")
) STRICT;

CREATE INDEX "idx_native_player_stat_links_unit_id" ON "native_player_stat_links" ("unit_id");

CREATE INDEX "idx_native_player_stat_links_player_source_id" ON "native_player_stat_links" ("player_source_id");

CREATE INDEX "idx_native_player_stat_links_stat_observation_id" ON "native_player_stat_links" ("stat_observation_id");

CREATE TRIGGER "native_player_stat_links_no_update" BEFORE UPDATE ON "native_player_stat_links" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_stat_links_no_delete" BEFORE DELETE ON "native_player_stat_links" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_player_stat_links_successful_unit" BEFORE INSERT ON "native_player_stat_links" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "gameplan_observations" (
  "plan_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "opponent_team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_slot_index" INTEGER NOT NULL,
  "is_in_use_raw" INTEGER NOT NULL,
  "is_tainted_raw" INTEGER NOT NULL,
  "poe_offense_1_raw" INTEGER,
  "poe_offense_2_raw" INTEGER,
  "poe_offense_3_raw" INTEGER,
  "poe_defense_1_raw" INTEGER,
  "poe_defense_2_raw" INTEGER,
  "poe_defense_3_raw" INTEGER,
  "help_defense_raw" INTEGER,
  "run_plays_raw" INTEGER,
  "zone_usage_raw" INTEGER,
  "bench_depth_raw" INTEGER,
  "bench_utilization_raw" INTEGER,
  "lineup_form_factor_raw" INTEGER,
  "playbook_code_raw" INTEGER,
  "freelance_code_raw" INTEGER,
  UNIQUE ("team_id","opponent_team_id","unit_id"),
  CHECK (team_id<>opponent_team_id)
) STRICT;

CREATE INDEX "idx_gameplan_observations_team_id" ON "gameplan_observations" ("team_id");

CREATE INDEX "idx_gameplan_observations_opponent_team_id" ON "gameplan_observations" ("opponent_team_id");

CREATE INDEX "idx_gameplan_observations_unit_id" ON "gameplan_observations" ("unit_id");

CREATE TRIGGER "gameplan_observations_no_update" BEFORE UPDATE ON "gameplan_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_observations_no_delete" BEFORE DELETE ON "gameplan_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_observations_successful_unit" BEFORE INSERT ON "gameplan_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "gameplan_rotation_observations" (
  "rotation_id" TEXT NOT NULL PRIMARY KEY,
  "plan_id" TEXT NOT NULL REFERENCES gameplan_observations(plan_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL,
  "native_rotation_id_raw" INTEGER NOT NULL,
  "player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "rotation_spot_raw" INTEGER,
  "playing_time_raw" INTEGER,
  "identity_status" TEXT NOT NULL,
  UNIQUE ("plan_id","slot_index","unit_id")
) STRICT;

CREATE INDEX "idx_gameplan_rotation_observations_plan_id" ON "gameplan_rotation_observations" ("plan_id");

CREATE INDEX "idx_gameplan_rotation_observations_unit_id" ON "gameplan_rotation_observations" ("unit_id");

CREATE INDEX "idx_gameplan_rotation_observations_player_id" ON "gameplan_rotation_observations" ("player_id");

CREATE TRIGGER "gameplan_rotation_observations_no_update" BEFORE UPDATE ON "gameplan_rotation_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_rotation_observations_no_delete" BEFORE DELETE ON "gameplan_rotation_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_rotation_observations_successful_unit" BEFORE INSERT ON "gameplan_rotation_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "gameplan_defense_observations" (
  "defense_id" TEXT NOT NULL PRIMARY KEY,
  "plan_id" TEXT NOT NULL REFERENCES gameplan_observations(plan_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "slot_index" INTEGER NOT NULL,
  "native_matchup_id_raw" INTEGER NOT NULL,
  "native_defender_id_raw" INTEGER NOT NULL,
  "opponent_player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "defender_player_id" TEXT REFERENCES players(player_id) ON DELETE RESTRICT,
  "slot_status" TEXT NOT NULL,
  "identity_status" TEXT NOT NULL,
  "pressure_onball_raw" INTEGER,
  "pressure_offball_raw" INTEGER,
  "force_direction_raw" INTEGER,
  "screen_defense_onball_raw" INTEGER,
  "screen_defense_hedge_raw" INTEGER,
  "offball_screen_defense_raw" INTEGER,
  "post_defense_raw" INTEGER,
  "double_team_perimeter_raw" INTEGER,
  "double_team_post_raw" INTEGER,
  "screen_defense_onball5_raw" INTEGER,
  "screen_defense_hedge5_raw" INTEGER,
  "switch_rule_raw" INTEGER,
  "onball_help_raw" INTEGER,
  "screen_help_raw" INTEGER,
  "extend_pressure_raw" INTEGER,
  "tag_on_roll_raw" INTEGER,
  "stay_attached_raw" INTEGER,
  "pre_rotate_raw" INTEGER,
  UNIQUE ("plan_id","slot_index","unit_id")
) STRICT;

CREATE INDEX "idx_gameplan_defense_observations_plan_id" ON "gameplan_defense_observations" ("plan_id");

CREATE INDEX "idx_gameplan_defense_observations_unit_id" ON "gameplan_defense_observations" ("unit_id");

CREATE INDEX "idx_gameplan_defense_observations_opponent_player_id" ON "gameplan_defense_observations" ("opponent_player_id");

CREATE INDEX "idx_gameplan_defense_observations_defender_player_id" ON "gameplan_defense_observations" ("defender_player_id");

CREATE TRIGGER "gameplan_defense_observations_no_update" BEFORE UPDATE ON "gameplan_defense_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_defense_observations_no_delete" BEFORE DELETE ON "gameplan_defense_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "gameplan_defense_observations_successful_unit" BEFORE INSERT ON "gameplan_defense_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "player_training_slot_observations" (
  "training_slot_id" TEXT NOT NULL PRIMARY KEY,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_slot_index" INTEGER NOT NULL,
  "native_player_id_raw" INTEGER NOT NULL,
  "identity_status" TEXT NOT NULL,
  "position_raw" INTEGER,
  "player_type_raw" INTEGER,
  "intensity_raw" INTEGER,
  "injury_recovery_raw" INTEGER,
  "is_intensity_overriden_raw" INTEGER,
  UNIQUE ("unit_id","source_slot_index")
) STRICT;

CREATE INDEX "idx_player_training_slot_observations_unit_id" ON "player_training_slot_observations" ("unit_id");

CREATE TRIGGER "player_training_slot_observations_no_update" BEFORE UPDATE ON "player_training_slot_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_training_slot_observations_no_delete" BEFORE DELETE ON "player_training_slot_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "player_training_slot_observations_successful_unit" BEFORE INSERT ON "player_training_slot_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "mentor_manager_observations" (
  "manager_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "franchise_slot" INTEGER,
  "header_team_id_raw" INTEGER,
  "first_badge_raw" INTEGER,
  "relation_count_raw" INTEGER,
  "layout_status" TEXT NOT NULL,
  UNIQUE ("team_id","unit_id")
) STRICT;

CREATE INDEX "idx_mentor_manager_observations_team_id" ON "mentor_manager_observations" ("team_id");

CREATE INDEX "idx_mentor_manager_observations_unit_id" ON "mentor_manager_observations" ("unit_id");

CREATE TRIGGER "mentor_manager_observations_no_update" BEFORE UPDATE ON "mentor_manager_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "mentor_manager_observations_no_delete" BEFORE DELETE ON "mentor_manager_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "mentor_manager_observations_successful_unit" BEFORE INSERT ON "mentor_manager_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TABLE "native_mentor_relation_observations" (
  "native_relation_id" TEXT NOT NULL PRIMARY KEY,
  "team_id" TEXT NOT NULL REFERENCES teams(team_id) ON DELETE RESTRICT,
  "unit_id" TEXT NOT NULL REFERENCES capture_units(unit_id) ON DELETE RESTRICT,
  "source_slot_index" INTEGER,
  "mentee_id_raw" INTEGER,
  "mentor_id_raw" INTEGER,
  "duration_days_raw" INTEGER,
  "compatibility_word_raw" INTEGER,
  "badge_count_raw" INTEGER,
  "identity_status" TEXT NOT NULL,
  UNIQUE ("team_id","unit_id","source_slot_index")
) STRICT;

CREATE INDEX "idx_native_mentor_relation_observations_team_id" ON "native_mentor_relation_observations" ("team_id");

CREATE INDEX "idx_native_mentor_relation_observations_unit_id" ON "native_mentor_relation_observations" ("unit_id");

CREATE TRIGGER "native_mentor_relation_observations_no_update" BEFORE UPDATE ON "native_mentor_relation_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_mentor_relation_observations_no_delete" BEFORE DELETE ON "native_mentor_relation_observations" BEGIN SELECT RAISE(ABORT,'immutable history'); END;

CREATE TRIGGER "native_mentor_relation_observations_successful_unit" BEFORE INSERT ON "native_mentor_relation_observations" WHEN NOT EXISTS (SELECT 1 FROM capture_units WHERE unit_id=NEW.unit_id AND unit_status='success') BEGIN SELECT RAISE(ABORT,'capture unit is not successful'); END;

CREATE TRIGGER "league_rule_setting_same_unit" BEFORE INSERT ON league_rule_observations WHEN NEW.setting_obs_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM game_setting_observations s WHERE s.setting_obs_id=NEW.setting_obs_id AND s.unit_id=NEW.unit_id AND s.integer_value IS NEW.integer_value AND s.real_value IS NEW.real_value AND s.text_value IS NEW.text_value) BEGIN SELECT RAISE(ABORT,'rule lacks same-unit matching setting word'); END;

CREATE TRIGGER native_stat_link_source_unit BEFORE INSERT ON native_player_stat_links WHEN NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.player_source_id AND p.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,'cross-unit native player source'); END;

CREATE TRIGGER native_stat_link_record_unit BEFORE INSERT ON native_player_stat_links WHEN NEW.stat_observation_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_stat_observations s WHERE s.stat_observation_id=NEW.stat_observation_id AND s.unit_id=NEW.unit_id AND s.source_stat_index=NEW.native_stat_index_raw) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native stat record'); END;

CREATE TRIGGER annual_refresh_once BEFORE INSERT ON capture_units WHEN NEW.unit_status='success' AND EXISTS(SELECT 1 FROM capture_runs n JOIN capture_runs r ON r.refresh_family=n.refresh_family AND r.refresh_period_year=n.refresh_period_year JOIN capture_units u ON u.run_id=r.run_id AND u.unit_status='success' WHERE n.run_id=NEW.run_id AND n.refresh_family IS NOT NULL AND n.source_grade='LIVE_READ' AND r.source_grade='LIVE_READ') BEGIN SELECT RAISE(ABORT,'annual refresh already captured for this save family and game-season year'); END;

CREATE TRIGGER game_source_reuse_origin BEFORE INSERT ON game_source_checks WHEN NEW.box_mode='REUSED_FROZEN_BOX' AND NOT EXISTS(SELECT 1 FROM game_source_checks o JOIN game_state_observations s ON s.game_id=o.game_id AND s.unit_id=o.unit_id JOIN capture_units u ON u.unit_id=o.unit_id WHERE o.game_id=NEW.game_id AND o.unit_id=NEW.prior_full_unit_id AND o.box_mode='FULL_NATIVE_BOX' AND o.header_sha256=NEW.header_sha256 AND s.is_final=1 AND u.unit_status='success') BEGIN SELECT RAISE(ABORT,'game reuse lacks matching frozen full source'); END;

CREATE TRIGGER native_award_recipient_source BEFORE INSERT ON award_recipients WHEN NEW.source_history_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_league_history_observations h JOIN season_award_instances a ON a.award_id=NEW.award_id WHERE h.history_observation_id=NEW.source_history_id AND h.unit_id=NEW.unit_id AND a.unit_id=NEW.unit_id AND h.award_id=a.award_id AND h.native_type_label=a.award_code AND h.native_year_raw=a.source_year_raw AND a.award_type='NATIVE_ROSTER_HISTORY') BEGIN SELECT RAISE(ABORT,'award recipient lacks matching same-unit native history'); END;

CREATE TRIGGER native_transaction_item_source BEFORE INSERT ON native_transaction_item_observations WHEN NOT EXISTS(SELECT 1 FROM native_transaction_observations p WHERE p.native_transaction_id=NEW.native_transaction_id AND p.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,'cross-unit native transaction item'); END;

CREATE TRIGGER native_news_message_source BEFORE INSERT ON game_news_entries WHEN NEW.source_message_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_social_message_observations m WHERE m.message_observation_id=NEW.source_message_id AND m.unit_id=NEW.unit_id AND m.event_code>0) BEGIN SELECT RAISE(ABORT,'news lacks same-unit nonzero native message'); END;

CREATE TRIGGER player_badge_values_native_source_unit BEFORE INSERT ON player_badge_values WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_contract_observations_native_source_unit BEFORE INSERT ON player_contract_observations WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_vitals_observations_native_source_unit BEFORE INSERT ON player_vitals_observations WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_health_observations_native_source_unit BEFORE INSERT ON player_health_observations WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_morale_observations_native_source_unit BEFORE INSERT ON player_morale_observations WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER market_state_observations_native_source_unit BEFORE INSERT ON market_state_observations WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_attribute_snapshots_native_source_unit BEFORE INSERT ON player_attribute_snapshots WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_tendency_snapshots_native_source_unit BEFORE INSERT ON player_tendency_snapshots WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_play_type_slots_native_source_unit BEFORE INSERT ON player_play_type_slots WHEN NEW.source_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_player_sources p WHERE p.player_source_id=NEW.source_player_id AND p.unit_id=NEW.unit_id AND p.player_id IS NEW.player_id) BEGIN SELECT RAISE(ABORT,'cross-unit or mismatched native player detail subject'); END;

CREATE TRIGGER player_vitals_college_source_unit BEFORE INSERT ON player_vitals_observations WHEN NEW.native_college_obs_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM native_college_observations c WHERE c.college_observation_id=NEW.native_college_obs_id AND c.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,'cross-unit native college referent'); END;

CREATE TRIGGER "gameplan_rotation_observations_same_unit" BEFORE INSERT ON gameplan_rotation_observations WHEN NOT EXISTS(SELECT 1 FROM gameplan_observations p WHERE p.plan_id=NEW.plan_id AND p.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,'cross-unit gameplan child'); END;

CREATE TRIGGER "gameplan_defense_observations_same_unit" BEFORE INSERT ON gameplan_defense_observations WHEN NOT EXISTS(SELECT 1 FROM gameplan_observations p WHERE p.plan_id=NEW.plan_id AND p.unit_id=NEW.unit_id) BEGIN SELECT RAISE(ABORT,'cross-unit gameplan child'); END;

CREATE TRIGGER "gameplan_rotation_observations_player_id_roster" BEFORE INSERT ON gameplan_rotation_observations WHEN NEW.player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM gameplan_observations p JOIN roster_memberships r ON r.unit_id=NEW.unit_id AND r.team_id=p.team_id AND r.player_id=NEW.player_id WHERE p.plan_id=NEW.plan_id) BEGIN SELECT RAISE(ABORT,'gameplan player lacks same-unit roster owner'); END;

CREATE TRIGGER "gameplan_defense_observations_opponent_player_id_roster" BEFORE INSERT ON gameplan_defense_observations WHEN NEW.opponent_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM gameplan_observations p JOIN roster_memberships r ON r.unit_id=NEW.unit_id AND r.team_id=p.opponent_team_id AND r.player_id=NEW.opponent_player_id WHERE p.plan_id=NEW.plan_id) BEGIN SELECT RAISE(ABORT,'gameplan player lacks same-unit roster owner'); END;

CREATE TRIGGER "gameplan_defense_observations_defender_player_id_roster" BEFORE INSERT ON gameplan_defense_observations WHEN NEW.defender_player_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM gameplan_observations p JOIN roster_memberships r ON r.unit_id=NEW.unit_id AND r.team_id=p.team_id AND r.player_id=NEW.defender_player_id WHERE p.plan_id=NEW.plan_id) BEGIN SELECT RAISE(ABORT,'gameplan player lacks same-unit roster owner'); END;

CREATE TRIGGER "player_game_boxes_participant" BEFORE INSERT ON player_game_boxes WHEN NOT EXISTS (SELECT 1 FROM games WHERE game_id=NEW.game_id AND NEW.team_id IN (home_team_id,away_team_id)) BEGIN SELECT RAISE(ABORT,'team is not a game participant'); END;

CREATE TRIGGER "team_game_boxes_participant" BEFORE INSERT ON team_game_boxes WHEN NOT EXISTS (SELECT 1 FROM games WHERE game_id=NEW.game_id AND NEW.team_id IN (home_team_id,away_team_id)) BEGIN SELECT RAISE(ABORT,'team is not a game participant'); END;

CREATE TRIGGER "game_period_scores_participant" BEFORE INSERT ON game_period_scores WHEN NOT EXISTS (SELECT 1 FROM games WHERE game_id=NEW.game_id AND NEW.team_id IN (home_team_id,away_team_id)) BEGIN SELECT RAISE(ABORT,'team is not a game participant'); END;

CREATE TRIGGER "player_game_boxes_frozen_conflict" BEFORE INSERT ON player_game_boxes WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM player_game_boxes old WHERE old."game_id"=NEW."game_id" AND old."player_id"=NEW."player_id" AND (EXISTS(SELECT 1 FROM game_state_observations fs WHERE fs.game_id=old.game_id AND fs.unit_id=old.unit_id AND fs.is_final=1)) AND ((old."team_id" IS NOT NULL AND NEW."team_id" IS NOT NULL AND old."team_id"<>NEW."team_id") OR (old."points" IS NOT NULL AND NEW."points" IS NOT NULL AND old."points"<>NEW."points") OR (old."fg_made" IS NOT NULL AND NEW."fg_made" IS NOT NULL AND old."fg_made"<>NEW."fg_made") OR (old."fg_attempted" IS NOT NULL AND NEW."fg_attempted" IS NOT NULL AND old."fg_attempted"<>NEW."fg_attempted") OR (old."three_made" IS NOT NULL AND NEW."three_made" IS NOT NULL AND old."three_made"<>NEW."three_made") OR (old."three_attempted" IS NOT NULL AND NEW."three_attempted" IS NOT NULL AND old."three_attempted"<>NEW."three_attempted") OR (old."ft_made" IS NOT NULL AND NEW."ft_made" IS NOT NULL AND old."ft_made"<>NEW."ft_made") OR (old."ft_attempted" IS NOT NULL AND NEW."ft_attempted" IS NOT NULL AND old."ft_attempted"<>NEW."ft_attempted") OR (old."offensive_rebounds" IS NOT NULL AND NEW."offensive_rebounds" IS NOT NULL AND old."offensive_rebounds"<>NEW."offensive_rebounds") OR (old."defensive_rebounds" IS NOT NULL AND NEW."defensive_rebounds" IS NOT NULL AND old."defensive_rebounds"<>NEW."defensive_rebounds") OR (old."assists" IS NOT NULL AND NEW."assists" IS NOT NULL AND old."assists"<>NEW."assists") OR (old."steals" IS NOT NULL AND NEW."steals" IS NOT NULL AND old."steals"<>NEW."steals") OR (old."blocks" IS NOT NULL AND NEW."blocks" IS NOT NULL AND old."blocks"<>NEW."blocks") OR (old."turnovers" IS NOT NULL AND NEW."turnovers" IS NOT NULL AND old."turnovers"<>NEW."turnovers") OR (old."fouls" IS NOT NULL AND NEW."fouls" IS NOT NULL AND old."fouls"<>NEW."fouls") OR (old."minutes_raw" IS NOT NULL AND NEW."minutes_raw" IS NOT NULL AND old."minutes_raw"<>NEW."minutes_raw") OR (old."plus_minus" IS NOT NULL AND NEW."plus_minus" IS NOT NULL AND old."plus_minus"<>NEW."plus_minus") OR (old."possessions_raw" IS NOT NULL AND NEW."possessions_raw" IS NOT NULL AND old."possessions_raw"<>NEW."possessions_raw") OR (old."defensive_fg_made" IS NOT NULL AND NEW."defensive_fg_made" IS NOT NULL AND old."defensive_fg_made"<>NEW."defensive_fg_made") OR (old."defensive_fg_attempted" IS NOT NULL AND NEW."defensive_fg_attempted" IS NOT NULL AND old."defensive_fg_attempted"<>NEW."defensive_fg_attempted") OR (old."defensive_points" IS NOT NULL AND NEW."defensive_points" IS NOT NULL AND old."defensive_points"<>NEW."defensive_points") OR (old."is_starter" IS NOT NULL AND NEW."is_starter" IS NOT NULL AND old."is_starter"<>NEW."is_starter") OR (old."in_use" IS NOT NULL AND NEW."in_use" IS NOT NULL AND old."in_use"<>NEW."in_use") OR (old."points_provenance" IS NOT NULL AND NEW."points_provenance" IS NOT NULL AND old."points_provenance"<>NEW."points_provenance"))) BEGIN SELECT RAISE(ABORT,'frozen game conflict; quarantine required'); END;

CREATE TRIGGER "team_game_boxes_frozen_conflict" BEFORE INSERT ON team_game_boxes WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM team_game_boxes old WHERE old."game_id"=NEW."game_id" AND old."team_id"=NEW."team_id" AND (EXISTS(SELECT 1 FROM game_state_observations fs WHERE fs.game_id=old.game_id AND fs.unit_id=old.unit_id AND fs.is_final=1)) AND ((old."points" IS NOT NULL AND NEW."points" IS NOT NULL AND old."points"<>NEW."points") OR (old."fg_made" IS NOT NULL AND NEW."fg_made" IS NOT NULL AND old."fg_made"<>NEW."fg_made") OR (old."fg_attempted" IS NOT NULL AND NEW."fg_attempted" IS NOT NULL AND old."fg_attempted"<>NEW."fg_attempted") OR (old."three_made" IS NOT NULL AND NEW."three_made" IS NOT NULL AND old."three_made"<>NEW."three_made") OR (old."three_attempted" IS NOT NULL AND NEW."three_attempted" IS NOT NULL AND old."three_attempted"<>NEW."three_attempted") OR (old."ft_made" IS NOT NULL AND NEW."ft_made" IS NOT NULL AND old."ft_made"<>NEW."ft_made") OR (old."ft_attempted" IS NOT NULL AND NEW."ft_attempted" IS NOT NULL AND old."ft_attempted"<>NEW."ft_attempted") OR (old."offensive_rebounds" IS NOT NULL AND NEW."offensive_rebounds" IS NOT NULL AND old."offensive_rebounds"<>NEW."offensive_rebounds") OR (old."defensive_rebounds" IS NOT NULL AND NEW."defensive_rebounds" IS NOT NULL AND old."defensive_rebounds"<>NEW."defensive_rebounds") OR (old."assists" IS NOT NULL AND NEW."assists" IS NOT NULL AND old."assists"<>NEW."assists") OR (old."steals" IS NOT NULL AND NEW."steals" IS NOT NULL AND old."steals"<>NEW."steals") OR (old."blocks" IS NOT NULL AND NEW."blocks" IS NOT NULL AND old."blocks"<>NEW."blocks") OR (old."turnovers" IS NOT NULL AND NEW."turnovers" IS NOT NULL AND old."turnovers"<>NEW."turnovers") OR (old."fouls" IS NOT NULL AND NEW."fouls" IS NOT NULL AND old."fouls"<>NEW."fouls") OR (old."minutes_raw" IS NOT NULL AND NEW."minutes_raw" IS NOT NULL AND old."minutes_raw"<>NEW."minutes_raw") OR (old."plus_minus" IS NOT NULL AND NEW."plus_minus" IS NOT NULL AND old."plus_minus"<>NEW."plus_minus") OR (old."possessions_raw" IS NOT NULL AND NEW."possessions_raw" IS NOT NULL AND old."possessions_raw"<>NEW."possessions_raw") OR (old."fastbreak_points" IS NOT NULL AND NEW."fastbreak_points" IS NOT NULL AND old."fastbreak_points"<>NEW."fastbreak_points") OR (old."paint_points" IS NOT NULL AND NEW."paint_points" IS NOT NULL AND old."paint_points"<>NEW."paint_points") OR (old."second_chance_points" IS NOT NULL AND NEW."second_chance_points" IS NOT NULL AND old."second_chance_points"<>NEW."second_chance_points") OR (old."points_off_turnovers" IS NOT NULL AND NEW."points_off_turnovers" IS NOT NULL AND old."points_off_turnovers"<>NEW."points_off_turnovers") OR (old."largest_lead" IS NOT NULL AND NEW."largest_lead" IS NOT NULL AND old."largest_lead"<>NEW."largest_lead"))) BEGIN SELECT RAISE(ABORT,'frozen game conflict; quarantine required'); END;

CREATE TRIGGER "game_period_scores_frozen_conflict" BEFORE INSERT ON game_period_scores WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM game_period_scores old WHERE old."game_id"=NEW."game_id" AND old."team_id"=NEW."team_id" AND old."period_index"=NEW."period_index" AND (EXISTS(SELECT 1 FROM game_state_observations fs WHERE fs.game_id=old.game_id AND fs.unit_id=old.unit_id AND fs.is_final=1)) AND ((old."period_points" IS NOT NULL AND NEW."period_points" IS NOT NULL AND old."period_points"<>NEW."period_points"))) BEGIN SELECT RAISE(ABORT,'frozen game conflict; quarantine required'); END;

CREATE TRIGGER "game_state_observations_frozen_conflict" BEFORE INSERT ON game_state_observations WHEN EXISTS(SELECT 1 FROM game_state_observations WHERE game_id=NEW.game_id AND is_final=1) AND EXISTS(SELECT 1 FROM game_state_observations old WHERE old."game_id"=NEW."game_id" AND (old.is_final=1) AND ((old."status_code" IS NOT NULL AND NEW."status_code" IS NOT NULL AND old."status_code"<>NEW."status_code") OR (old."home_points" IS NOT NULL AND NEW."home_points" IS NOT NULL AND old."home_points"<>NEW."home_points") OR (old."away_points" IS NOT NULL AND NEW."away_points" IS NOT NULL AND old."away_points"<>NEW."away_points") OR (old."overtime_count" IS NOT NULL AND NEW."overtime_count" IS NOT NULL AND old."overtime_count"<>NEW."overtime_count") OR (old."attendance" IS NOT NULL AND NEW."attendance" IS NOT NULL AND old."attendance"<>NEW."attendance") OR (old."was_simulated" IS NOT NULL AND NEW."was_simulated" IS NOT NULL AND old."was_simulated"<>NEW."was_simulated") OR (old."score_provenance" IS NOT NULL AND NEW."score_provenance" IS NOT NULL AND old."score_provenance"<>NEW."score_provenance") OR (old."is_final" IS NOT NULL AND NEW."is_final" IS NOT NULL AND old."is_final"<>NEW."is_final"))) BEGIN SELECT RAISE(ABORT,'frozen game conflict; quarantine required'); END;

CREATE TRIGGER "identity_player_fk" BEFORE INSERT ON native_identity_links WHEN NEW.entity_type='player' AND NOT EXISTS(SELECT 1 FROM players WHERE player_id=NEW.entity_id) BEGIN SELECT RAISE(ABORT,'unresolved native identity'); END;

CREATE TRIGGER "identity_team_fk" BEFORE INSERT ON native_identity_links WHEN NEW.entity_type='team' AND NOT EXISTS(SELECT 1 FROM teams WHERE team_id=NEW.entity_id) BEGIN SELECT RAISE(ABORT,'unresolved native identity'); END;

CREATE TRIGGER "identity_game_fk" BEFORE INSERT ON native_identity_links WHEN NEW.entity_type='game' AND NOT EXISTS(SELECT 1 FROM games WHERE game_id=NEW.entity_id) BEGIN SELECT RAISE(ABORT,'unresolved native identity'); END;

CREATE TRIGGER "identity_staff_fk" BEFORE INSERT ON native_identity_links WHEN NEW.entity_type='staff' AND NOT EXISTS(SELECT 1 FROM staff_members WHERE staff_id=NEW.entity_id) BEGIN SELECT RAISE(ABORT,'unresolved native identity'); END;

CREATE TRIGGER "player_season_totals_final_once" BEFORE INSERT ON player_season_totals WHEN EXISTS (SELECT 1 FROM player_season_totals WHERE player_id=NEW.player_id AND season_id=NEW.season_id AND is_final=1) OR EXISTS(SELECT 1 FROM season_finalizations WHERE season_id=NEW.season_id) BEGIN SELECT RAISE(ABORT,'season totals already finalized; quarantine conflict'); END;

CREATE TRIGGER "team_season_totals_final_once" BEFORE INSERT ON team_season_totals WHEN EXISTS (SELECT 1 FROM team_season_totals WHERE team_id=NEW.team_id AND season_id=NEW.season_id AND is_final=1) OR EXISTS(SELECT 1 FROM season_finalizations WHERE season_id=NEW.season_id) BEGIN SELECT RAISE(ABORT,'season totals already finalized; quarantine conflict'); END;

CREATE VIEW gm_player_observations AS SELECT p.player_id,p.display_name,a.*,u.observed_at,r.source_grade FROM player_attribute_snapshots a JOIN players p USING(player_id) JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE u.unit_status='success';

CREATE VIEW gm_game_box AS SELECT g.game_id,g.season_id,g.game_date,p.display_name,b.*,u.observed_at,r.source_grade FROM player_game_boxes b JOIN games g USING(game_id) JOIN players p USING(player_id) JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE u.unit_status='success';

CREATE VIEW derived_game_scores AS SELECT game_id,unit_id,team_id,SUM(period_points) AS regulation_points,'DERIVED_SUM_PERIODS' AS provenance FROM game_period_scores GROUP BY game_id,unit_id,team_id;

CREATE VIEW derived_player_box_metrics AS SELECT box_id,CASE WHEN fg_attempted>0 THEN 1.0*(fg_made+0.5*three_made)/fg_attempted END AS efg_pct,CASE WHEN fg_attempted+0.44*ft_attempted>0 THEN points/(2.0*(fg_attempted+0.44*ft_attempted)) END AS ts_pct,'DERIVED_WITH_FORMULA_V1' AS provenance FROM player_game_boxes;
