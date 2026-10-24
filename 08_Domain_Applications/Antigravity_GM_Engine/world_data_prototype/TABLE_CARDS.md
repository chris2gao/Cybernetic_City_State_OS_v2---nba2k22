# Executable world table cards (development candidate)

Generated from `schema_model.py`. Column-level types, constraints, units, null semantics, visibility and source evidence are in `field_dictionary.json`.

Actual tables: **61**. Every table is STRICT and append-only. A SQLite owner can still replace a database; ordinary roles receive query results, never direct file access.

| Table | Domain | One row / reason | Primary key | Foreign keys | v1 mapping |
|---|---|---|---|---|---|
| `saves` | RES-D | one independent game save per SQLite file | `singleton` |  | EXTEND/PRESERVE |
| `seasons` | RES-L | one save-local season | `season_id` | save_id -> saves(save_id) | EXTEND/PRESERVE |
| `teams` | RES-T | stable save-local team identity | `team_id` |  | EXTEND/PRESERVE |
| `players` | RES-P | stable save-local player instance | `player_id` |  | EXTEND/PRESERVE |
| `staff_members` | RES-C | save-local staff identity | `staff_id` |  | ADD |
| `games` | RES-G | one identified season game, not its changing observed state | `game_id` | season_id -> seasons(season_id); home_team_id -> teams(team_id); away_team_id -> teams(team_id) | EXTEND/PRESERVE |
| `capture_runs` | RES-D | one acquisition session | `run_id` | season_id -> seasons(season_id) | EXTEND/PRESERVE |
| `capture_units` | RES-D | one immutable atomic source consistency unit | `unit_id` | run_id -> capture_runs(run_id) | EXTEND/PRESERVE |
| `source_artifacts` | RES-D | one bounded source artifact hash, no public raw bytes | `artifact_id` | unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `native_fields` | RES-D | versioned source-field mapping metadata | `field_id` |  | EXTEND/PRESERVE |
| `field_gaps` | RES-D | one unresolved target-field gap or Human exception | `gap_id` | field_id -> native_fields(field_id) | EXTEND/PRESERVE |
| `fact_conflicts` | RES-D | one quarantined conflict with an existing fact | `conflict_id` | unit_id -> capture_units(unit_id) | ADD |
| `team_seasons` | RES-T | team participation in one season | `team_season_id` | team_id -> teams(team_id); season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
| `roster_memberships` | RES-T | observed player team membership; not a transfer event | `membership_id` | player_id -> players(player_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `team_rotation_slots` | RES-T | one ordered team rotation setting | `slot_id` | team_id -> teams(team_id); player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `player_vitals_observations` | RES-P | one actual vitals observation | `observation_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `player_attribute_snapshots` | RES-P | one player successful typed attribute family observation | `snapshot_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `player_tendency_snapshots` | RES-P | one player named tendency family observation | `snapshot_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `player_badge_values` | RES-P | one enumerated badge observation; absence is not unowned | `badge_observation_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `player_play_type_slots` | RES-P | one ordered player play type slot | `play_type_observation_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `player_contract_observations` | RES-M | one actual contract observation, not inferred signing event | `contract_obs_id` | player_id -> players(player_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `player_health_observations` | RES-P | observed health separate from attribute durability | `health_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `player_morale_observations` | RES-P | observed native morale/role, not AI personality | `morale_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `player_training_observations` | RES-P | observed personal training settings | `training_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id); team_id -> teams(team_id) | ADD |
| `game_state_observations` | RES-G | observed status and native score if actually available | `observation_id` | game_id -> games(game_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `game_period_scores` | RES-G | one team one actual period score observation | `period_score_id` | game_id -> games(game_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `team_game_boxes` | RES-G | one game team native box observation | `box_id` | game_id -> games(game_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `player_game_boxes` | RES-G | one game player native box observation | `box_id` | game_id -> games(game_id); player_id -> players(player_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | EXTEND/PRESERVE |
| `playoff_series` | RES-G | one identified native playoff series | `series_id` | season_id -> seasons(season_id); team_a_id -> teams(team_id); team_b_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `playoff_series_games` | RES-G | evidenced series-to-game association | `series_game_id` | series_id -> playoff_series(series_id); game_id -> games(game_id); unit_id -> capture_units(unit_id) | ADD |
| `player_season_totals` | RES-L | native cumulative player season totals observation | `total_id` | player_id -> players(player_id); season_id -> seasons(season_id); unit_id -> capture_units(unit_id); team_id -> teams(team_id) | ADD |
| `team_season_totals` | RES-L | native cumulative team season observation | `total_id` | team_id -> teams(team_id); season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
| `staff_team_assignments` | RES-C | evidenced actual staff role assignment | `assignment_id` | staff_id -> staff_members(staff_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `staff_contract_observations` | RES-C | one staff contract observation | `contract_obs_id` | staff_id -> staff_members(staff_id); unit_id -> capture_units(unit_id) | ADD |
| `staff_skill_observations` | RES-C | one staff typed skill family observation | `skill_obs_id` | staff_id -> staff_members(staff_id); unit_id -> capture_units(unit_id) | ADD |
| `coach_preferences` | RES-C | one coach preferences observation | `pref_id` | staff_id -> staff_members(staff_id); unit_id -> capture_units(unit_id) | ADD |
| `team_tactic_settings` | RES-C | one team actual tactics settings observation | `tactic_id` | team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `team_playbook_slots` | RES-C | one ordered actual team playbook entry | `slot_id` | team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `team_training_settings` | RES-C | one team actual training settings | `training_id` | team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `mentorship_relations` | RES-C | observed actual mentor association | `mentor_id` | player_id -> players(player_id); mentor_player_id -> players(player_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `team_finance_observations` | RES-M | native financial snapshot, not external CBA inference | `finance_id` | team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `market_state_observations` | RES-M | native or external market state with explicit origin | `market_id` | player_id -> players(player_id); staff_id -> staff_members(staff_id); unit_id -> capture_units(unit_id) | ADD |
| `external_transaction_events` | RES-M | explicit completed external transaction, never roster-diff inference | `transaction_id` | save_id -> saves(save_id); unit_id -> capture_units(unit_id) | ADD |
| `draft_pick_assets` | RES-M | one actual draft pick identity | `pick_id` | save_id -> saves(save_id); original_team_id -> teams(team_id) | ADD |
| `transaction_components` | RES-M | one evidenced external transaction component | `component_id` | transaction_id -> external_transaction_events(transaction_id); unit_id -> capture_units(unit_id); from_team_id -> teams(team_id); to_team_id -> teams(team_id); player_id -> players(player_id); staff_id -> staff_members(staff_id); pick_id -> draft_pick_assets(pick_id) | ADD |
| `draft_pick_ownerships` | RES-M | observed or explicit event-backed pick ownership | `ownership_id` | pick_id -> draft_pick_assets(pick_id); owner_team_id -> teams(team_id); unit_id -> capture_units(unit_id); event_ref -> external_transaction_events(transaction_id) | ADD |
| `draft_prospects` | RES-M | one evidenced prospect, separate from player instance | `prospect_id` | save_id -> saves(save_id); unit_id -> capture_units(unit_id) | ADD |
| `draft_results` | RES-M | actual source-backed draft result | `result_id` | prospect_id -> draft_prospects(prospect_id); pick_id -> draft_pick_assets(pick_id); team_id -> teams(team_id); player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `worldline_config_versions` | RES-S | versioned desired configuration, never actual game state | `config_id` | save_id -> saves(save_id); unit_id -> capture_units(unit_id) | ADD |
| `game_setting_observations` | RES-S | one actual native setting, using typed value alternatives | `setting_obs_id` | unit_id -> capture_units(unit_id); field_id -> native_fields(field_id) | ADD |
| `startup_config_checks` | RES-S | desired-vs-observed configuration check | `check_id` | config_id -> worldline_config_versions(config_id); setting_obs_id -> game_setting_observations(setting_obs_id); unit_id -> capture_units(unit_id) | ADD |
| `league_rule_observations` | RES-L | one actual season rule observation | `rule_id` | season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
| `season_award_instances` | RES-H | actual awarded honor; leaders are not winners | `award_id` | season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
| `award_recipients` | RES-H | one actual award recipient | `recipient_id` | award_id -> season_award_instances(award_id); player_id -> players(player_id); team_id -> teams(team_id); unit_id -> capture_units(unit_id) | ADD |
| `season_record_entries` | RES-H | one actual record holder/value, no fabricated honors | `record_id` | season_id -> seasons(season_id); unit_id -> capture_units(unit_id); holder_player_id -> players(player_id); holder_team_id -> teams(team_id) | ADD |
| `external_execution_receipts` | RES-D | external executor report, not proof of readback | `receipt_id` | save_id -> saves(save_id); transaction_id -> external_transaction_events(transaction_id); unit_id -> capture_units(unit_id) | ADD |
| `external_readback_checks` | RES-D | separate observed readback reconciliation | `check_id` | receipt_id -> external_execution_receipts(receipt_id); unit_id -> capture_units(unit_id) | ADD |
| `native_identity_links` | RES-D | one versioned native ID to actual save-local entity link | `link_id` | save_id -> saves(save_id); unit_id -> capture_units(unit_id) | ADD |
| `player_restricted_observations` | RES-P | restricted external-storage metadata; raw Potential never in world facts | `observation_id` | player_id -> players(player_id); unit_id -> capture_units(unit_id) | ADD |
| `game_news_entries` | RES-H | one source-observed native news item | `news_id` | season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
| `season_finalizations` | RES-D | explicit evidenced season closure boundary | `finalization_id` | season_id -> seasons(season_id); unit_id -> capture_units(unit_id) | ADD |
