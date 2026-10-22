-- Derived intentions and execution receipts, never authoritative game observations.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS control_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS native_field_registry(
 field_key TEXT PRIMARY KEY, registry_version TEXT NOT NULL, definition_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS desired_change_sets(
 change_set_id TEXT PRIMARY KEY, save_id TEXT NOT NULL, save_instance_id TEXT NOT NULL,
 generation_id TEXT NOT NULL, source_batch_id TEXT NOT NULL, source_snapshot_id TEXT NOT NULL,
 registry_version TEXT NOT NULL, decision_id TEXT NOT NULL, version INTEGER NOT NULL,
 status TEXT NOT NULL, created_at TEXT NOT NULL, change_digest TEXT NOT NULL,
 origin_model TEXT, reason TEXT NOT NULL, plan_json TEXT NOT NULL,
 UNIQUE(save_instance_id,generation_id,decision_id,version));
CREATE TABLE IF NOT EXISTS desired_changes(
 change_set_id TEXT NOT NULL REFERENCES desired_change_sets, action_id TEXT NOT NULL,
 object_key TEXT NOT NULL, field_key TEXT NOT NULL, expected_observed_raw TEXT,
 target_value_json TEXT NOT NULL, reason TEXT NOT NULL, dependencies_json TEXT NOT NULL,
 PRIMARY KEY(change_set_id,action_id), UNIQUE(change_set_id,object_key,field_key));
CREATE TABLE IF NOT EXISTS approval_records(
 approval_id TEXT PRIMARY KEY, change_set_id TEXT NOT NULL REFERENCES desired_change_sets,
 approved_digest TEXT NOT NULL, binding_json TEXT NOT NULL, approved_action_ids TEXT NOT NULL,
 player_approval_reference TEXT NOT NULL, approved_at TEXT NOT NULL, operation TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS execution_runs(
 run_id TEXT PRIMARY KEY, change_set_id TEXT NOT NULL REFERENCES desired_change_sets,
 digest TEXT NOT NULL, game_process_fingerprint TEXT, started_at TEXT NOT NULL,
 status TEXT NOT NULL, completed_at TEXT, readback_summary TEXT, error_code TEXT,
 journal_path TEXT NOT NULL, operation TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS execution_blocks(
 run_id TEXT NOT NULL REFERENCES execution_runs, storage_target_key TEXT NOT NULL,
 validated_identity TEXT NOT NULL, byte_mask TEXT NOT NULL, before_raw TEXT NOT NULL,
 expected_after_raw TEXT NOT NULL, readback_raw TEXT, state TEXT NOT NULL,
 PRIMARY KEY(run_id,storage_target_key));
CREATE TABLE IF NOT EXISTS reconciliation_records(
 change_set_id TEXT NOT NULL REFERENCES desired_change_sets, new_snapshot_id TEXT NOT NULL,
 field_target TEXT NOT NULL, expected_applied TEXT, observed_again TEXT,
 comparison_status TEXT NOT NULL, comment TEXT,
 PRIMARY KEY(change_set_id,new_snapshot_id,field_target));
CREATE VIEW IF NOT EXISTS capability_registry AS
 SELECT field_key, json_extract(definition_json,'$.domain') AS domain,
 json_extract(definition_json,'$.read_status') AS read_status,
 json_extract(definition_json,'$.write_capability') AS write_capability,
 json_extract(definition_json,'$.game_save_persisted') AS game_save_persisted,
 json_extract(definition_json,'$.gm_enabled') AS gm_enabled FROM native_field_registry;
PRAGMA user_version=1;
