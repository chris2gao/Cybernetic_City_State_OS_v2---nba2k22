"""Tests for CalendarSimOrchestrator, post-simulation auto-capture triggers, and G1/G2 gates."""
import json
from pathlib import Path
import struct
import sys
from tempfile import TemporaryDirectory
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from live_world import initialize_save
from calendar_sim_orchestrator import CalendarSimOrchestrator
from engine import create_database, connect, ingest_capture
from schema_model import VERSION
from test_live_reader import FixtureReader
from test_schedule import ScheduleMemory


class CalendarSimOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.loaded_filename = 'MyLEAGUE0003'
        self.save_id = 'test_save'

        # Initialize mock save binding and database via initialize_save
        native_file = self.tmp_path / self.loaded_filename
        native_file.write_bytes(b'SAVEDATA_MOCK')
        self.save_dir = self.tmp_path / 'save_dir'
        initialize_save(str(self.save_dir), self.save_id, str(native_file))
        self.db = self.save_dir / 'world.sqlite'

    def test_liveness_check_with_mock_and_pe_header(self):
        reader = ScheduleMemory()
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        res = orch.inspect_process_liveness(reader)
        self.assertEqual(res['status'], 'LIVENESS_VERIFIED')
        self.assertTrue(res['is_mock_or_custom'])
        self.assertEqual(res['pe_timestamp'], 1652287197)

    def test_inspect_progress_detects_new_final_game_when_db_empty(self):
        reader = ScheduleMemory()
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        progress = orch.inspect_calendar_progress(reader)
        self.assertEqual(progress['status'], 'NEW_FINAL_GAME_DETECTED')
        self.assertTrue(progress['new_final_game_detected'])
        self.assertIsNotNone(progress['latest_memory_game_id'])

    def test_inspect_progress_skips_on_same_state_repeat(self):
        reader = ScheduleMemory()
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        progress_1 = orch.inspect_calendar_progress(reader)
        target_gid = progress_1['latest_memory_game_id']

        # Ingest game into DB
        facts = {
            'teams': [
                {'team_id': 'team:native:1', 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': 'team:native:2', 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'games': [
                {'game_id': target_gid, 'home_team_id': 'team:native:1', 'away_team_id': 'team:native:2',
                 'game_date': '2021-10-24', 'season_id': 's1'}
            ],
            'game_state_observations': [
                {'game_id': target_gid, 'status_code': 'FINAL', 'is_final': 1,
                 'overtime_count': 0, 'attendance': 18000, 'was_simulated': 1, 'score_provenance': 'TEST'}
            ]
        }
        payload = {
            'save_id': self.save_id,
            'run_id': 'unit_run_1',
            'unit_id': 'unit_run_1',
            'source_key': 'BOUND_TEST',
            'observed_at': '2026-10-24T10:00:00Z',
            'evidence_grade': 'RESEARCH_FIXTURE',
            'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'},
            'facts': facts,
            'artifacts': [{'sha256': '1' * 64, 'payload_kind': 'TEST', 'payload_ref': 'test.bin', 'byte_count': 10, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)

        # Inspect again: should detect SAME_STATE_REPEAT
        progress_2 = orch.inspect_calendar_progress(reader)
        self.assertEqual(progress_2['status'], 'SAME_STATE_REPEAT')
        self.assertFalse(progress_2['new_final_game_detected'])
        self.assertEqual(progress_2['latest_memory_game_id'], target_gid)
        self.assertEqual(progress_2['latest_db_game_id'], target_gid)

        # Calling trigger_capture_if_new_game should skip without triggering refresh
        res = orch.trigger_capture_if_new_game(reader)
        self.assertEqual(res['status'], 'SAME_STATE_REPEAT')
        self.assertFalse(res['triggered'])

    def test_inspect_progress_fails_closed_on_game_in_progress(self):
        class MidGameMemory(ScheduleMemory):
            def __init__(self):
                super().__init__()
                # Modify game status to 1 (in-progress) in flags (byte 56, bit 11)
                g = bytearray(self.games[:60])
                flags = struct.unpack_from('<I', g, 56)[0]
                flags = (flags & ~(0x03 << 11)) | (1 << 11)
                struct.pack_into('<I', g, 56, flags)
                self.games = bytes(g) + self.games[60:]

        reader = MidGameMemory()
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        progress = orch.inspect_calendar_progress(reader)
        self.assertEqual(progress['status'], 'INCOMPLETE_GAME_IN_PROGRESS')
        self.assertFalse(progress['new_final_game_detected'])

        # Trigger must reject in-progress game
        res = orch.trigger_capture_if_new_game(reader)
        self.assertEqual(res['status'], 'REJECTED_GAME_IN_PROGRESS')
        self.assertFalse(res['triggered'])

    def test_sql_readback_integrity_verification(self):
        gid = 'game:native:999'
        home_tid = 'team:native:10'
        away_tid = 'team:native:20'

        facts = {
            'teams': [
                {'team_id': home_tid, 'native_team_id': '10', 'display_name': 'Home Team'},
                {'team_id': away_tid, 'native_team_id': '20', 'display_name': 'Away Team'}
            ],
            'players': [
                {'player_id': 'player:native:1', 'native_player_id': '1', 'display_name': 'Player 1'}
            ],
            'games': [
                {'game_id': gid, 'home_team_id': home_tid, 'away_team_id': away_tid,
                 'game_date': '2021-11-05', 'season_id': 's1'}
            ],
            'game_state_observations': [
                {'game_id': gid, 'status_code': 'FINAL', 'is_final': 1,
                 'overtime_count': 0, 'attendance': 19500, 'was_simulated': 1, 'score_provenance': 'TEST'}
            ],
            'game_period_scores': [
                {'game_id': gid, 'team_id': home_tid, 'period_index': 1, 'period_points': 25},
                {'game_id': gid, 'team_id': home_tid, 'period_index': 2, 'period_points': 25},
                {'game_id': gid, 'team_id': home_tid, 'period_index': 3, 'period_points': 25},
                {'game_id': gid, 'team_id': home_tid, 'period_index': 4, 'period_points': 25},
                {'game_id': gid, 'team_id': away_tid, 'period_index': 1, 'period_points': 22},
                {'game_id': gid, 'team_id': away_tid, 'period_index': 2, 'period_points': 22},
                {'game_id': gid, 'team_id': away_tid, 'period_index': 3, 'period_points': 22},
                {'game_id': gid, 'team_id': away_tid, 'period_index': 4, 'period_points': 22},
            ],
            'team_game_boxes': [
                {'game_id': gid, 'team_id': home_tid, 'points': 100, 'minutes_raw': 240,
                 'fg_made': 38, 'fg_attempted': 80, 'three_made': 10, 'three_attempted': 25,
                 'ft_made': 14, 'ft_attempted': 18, 'offensive_rebounds': 8, 'defensive_rebounds': 34,
                 'assists': 22, 'steals': 7, 'blocks': 5, 'turnovers': 12, 'fouls': 16,
                 'plus_minus': 12, 'possessions_raw': 98, 'fastbreak_points': 14, 'paint_points': 46,
                 'second_chance_points': 10, 'points_off_turnovers': 16, 'largest_lead': 15},
                {'game_id': gid, 'team_id': away_tid, 'points': 88, 'minutes_raw': 240,
                 'fg_made': 32, 'fg_attempted': 82, 'three_made': 8, 'three_attempted': 28,
                 'ft_made': 16, 'ft_attempted': 20, 'offensive_rebounds': 9, 'defensive_rebounds': 30,
                 'assists': 18, 'steals': 6, 'blocks': 3, 'turnovers': 15, 'fouls': 18,
                 'plus_minus': -12, 'possessions_raw': 98, 'fastbreak_points': 8, 'paint_points': 38,
                 'second_chance_points': 8, 'points_off_turnovers': 11, 'largest_lead': 4}
            ],
            'player_game_boxes': [
                {'game_id': gid, 'player_id': 'player:native:1', 'team_id': home_tid,
                 'is_starter': 1, 'minutes_raw': 32, 'points': 26, 'fg_made': 10, 'fg_attempted': 20,
                 'three_made': 2, 'three_attempted': 5, 'ft_made': 4, 'ft_attempted': 5,
                 'offensive_rebounds': 2, 'defensive_rebounds': 6, 'assists': 6, 'steals': 2, 'blocks': 1,
                 'turnovers': 3, 'fouls': 2, 'plus_minus': 8}
            ]
        }
        payload = {
            'save_id': self.save_id,
            'run_id': 'unit_ver_1',
            'unit_id': 'unit_ver_1',
            'source_key': 'BOUND_TEST_VER',
            'observed_at': '2026-10-24T12:00:00Z',
            'evidence_grade': 'RESEARCH_FIXTURE',
            'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'},
            'facts': facts,
            'artifacts': [{'sha256': '9' * 64, 'payload_kind': 'TEST', 'payload_ref': 'test.bin', 'byte_count': 10, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)

        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        ver = orch.verify_game_sql_integrity(gid)
        self.assertTrue(ver['verified_in_db'])
        self.assertTrue(ver['score_conservation'])
        self.assertEqual(ver['home_points'], 100)
        self.assertEqual(ver['away_points'], 88)
        self.assertEqual(ver['team_boxes_count'], 2)
        self.assertEqual(ver['player_boxes_count'], 1)

    def test_g2_experiment_contract_structure_and_criteria(self):
        contract_path = Path('01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/06_执行/experiment_settings_metrics_contract.json')
        self.assertTrue(contract_path.exists())
        contract = json.loads(contract_path.read_text(encoding='utf-8'))
        self.assertEqual(len(contract['experiments']), 3)

        exp1 = contract['experiments'][0]
        self.assertEqual(exp1['experiment_id'], 'EXP_01_SHOT_TOUCHES_COACH_RUN_PLAYS')
        self.assertEqual(exp1['metrics_evaluation_contract']['primary_metric']['metric_id'], 'PLAYER_FGA')
        self.assertIn('supported_condition', exp1['falsification_criteria'])
        self.assertIn('refuted_condition', exp1['falsification_criteria'])

        # Check Pilot 2 Tempo contract
        exp2 = contract['experiments'][1]
        self.assertEqual(exp2['experiment_id'], 'EXP_02_COACH_TEMPO_PACE_ROTATION')
        self.assertEqual(exp2['metrics_evaluation_contract']['primary_metric']['metric_id'], 'TEAM_PACE_NATIVE')

    def test_export_vae_standard_datasets_deterministic_pipeline(self):
        gid = 'game:native:888'
        home_tid = 'team:native:1'
        away_tid = 'team:native:2'
        pid = 'player:native:77'

        facts = {
            'teams': [
                {'team_id': home_tid, 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': away_tid, 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'players': [
                {'player_id': pid, 'native_player_id': '77', 'display_name': 'Star Player'}
            ],
            'games': [
                {'game_id': gid, 'home_team_id': home_tid, 'away_team_id': away_tid,
                 'game_date': '2021-11-01', 'season_id': 's1'}
            ],
            'game_state_observations': [
                {'game_id': gid, 'status_code': 'FINAL', 'is_final': 1,
                 'overtime_count': 0, 'attendance': 18500, 'was_simulated': 1, 'score_provenance': 'TEST'}
            ],
            'team_game_boxes': [
                {'game_id': gid, 'team_id': home_tid, 'points': 105, 'possessions_raw': 98, 'fastbreak_points': 14},
                {'game_id': gid, 'team_id': away_tid, 'points': 95, 'possessions_raw': 98, 'fastbreak_points': 8}
            ],
            'player_game_boxes': [
                {'game_id': gid, 'player_id': pid, 'team_id': home_tid, 'minutes_raw': 34,
                 'points': 28, 'fg_attempted': 20, 'fg_made': 11}
            ],
            'team_tactic_settings': [
                {'team_id': home_tid, 'tempo_raw': 65, 'help_defense_raw': 60, 'run_plays_raw': 55}
            ],
            'player_tendency_snapshots': [
                {'player_id': pid, 'shot_tendency_raw': 85, 'touches_tendency_raw': 80}
            ],
            'player_attribute_snapshots': [
                {'player_id': pid, 'overall_raw': 92}
            ]
        }
        payload = {
            'save_id': self.save_id,
            'run_id': 'unit_vae_export_1',
            'unit_id': 'unit_vae_export_1',
            'source_key': 'BOUND_TEST',
            'observed_at': '2026-11-01T10:00:00Z',
            'evidence_grade': 'RESEARCH_FIXTURE',
            'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'},
            'facts': facts,
            'artifacts': [{'sha256': 'a' * 64, 'payload_kind': 'TEST', 'payload_ref': 'test.bin', 'byte_count': 10, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)

        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        export_out = self.tmp_path / 'vae_exports'
        res = orch.export_vae_standard_datasets(export_out)

        self.assertEqual(res['status'], 'FIXTURE_REPLAY_SUCCESS')
        self.assertEqual(res['games_count'], 1)

        # Check all 3 dataset files and manifest exist
        m1 = export_out / 'calendar_sim_completed_game_player_team_metrics.json'
        m2 = export_out / 'vae_setting_context_snapshot.json'
        m3 = export_out / 'vae_experiment_evidence_input.json'
        manifest_file = export_out / 'manifest.json'

        self.assertTrue(m1.exists())
        self.assertTrue(m2.exists())
        self.assertTrue(m3.exists())
        self.assertTrue(manifest_file.exists())

        d1 = json.loads(m1.read_text(encoding='utf-8'))
        self.assertEqual(d1['games_count'], 1)
        self.assertEqual(d1['simulation_mode'], 'CALENDAR_SIM_ONLY')
        self.assertEqual(len(d1['team_boxes']), 2)
        self.assertEqual(len(d1['player_boxes']), 1)

        d2 = json.loads(m2.read_text(encoding='utf-8'))
        self.assertEqual(d2['team_tactics_count'], 1)
        self.assertEqual(d2['player_tendencies_count'], 1)
        self.assertEqual(d2['player_attributes_count'], 1)

        d3 = json.loads(m3.read_text(encoding='utf-8'))
        self.assertEqual(len(d3['pilots']), 3)

        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        self.assertEqual(manifest['schema_version'], 'nba2k22.vae.standard_dataset_manifest.v1')
        self.assertEqual(manifest['metric_dictionary_version'], 'Stage02.M3.Canonical38')
        self.assertEqual(manifest['readiness_levels']['STANDARD_DATASET_EXPORTED'], 'VERIFIED')
        self.assertEqual(manifest['readiness_levels']['POST_CALENDAR_NEW_GAME_VERIFIED'], 'PENDING_HUMAN_GAMEPLAY')
        self.assertEqual(manifest['readiness_levels']['CURRENT_NATIVE_READ'], 'LIVE_VALIDATION_PENDING')

    def test_cli_vae_export_datasets(self):
        from cli import dispatch
        import argparse
        import io
        from contextlib import redirect_stdout

        export_out = self.tmp_path / 'cli_vae_exports'
        parser = argparse.Namespace(
            action='vae-export-datasets',
            save_directory=str(self.save_dir),
            loaded_filename=self.loaded_filename,
            output_directory=str(export_out)
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            dispatch(parser)
        out = buf.getvalue()
        res = json.loads(out)
        self.assertEqual(res['status'], 'EMPTY_DATABASE_INITIALIZED')
        self.assertTrue((export_out / 'manifest.json').exists())

    def test_sql_verification_fails_closed_on_missing_team_box(self):
        gid = 'game:native:missing_box'
        home_tid = 'team:native:1'
        away_tid = 'team:native:2'
        facts = {
            'teams': [
                {'team_id': home_tid, 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': away_tid, 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'players': [{'player_id': 'p1', 'native_player_id': '1', 'display_name': 'P1'}],
            'games': [{'game_id': gid, 'home_team_id': home_tid, 'away_team_id': away_tid, 'game_date': '2021-11-02', 'season_id': 's1'}],
            'game_state_observations': [{'game_id': gid, 'status_code': 'FINAL', 'is_final': 1, 'was_simulated': 1, 'score_provenance': 'TEST'}],
            'game_period_scores': [{'game_id': gid, 'team_id': home_tid, 'period_index': 1, 'period_points': 25}],
            'team_game_boxes': [{'game_id': gid, 'team_id': home_tid, 'points': 25}],  # Missing away_box!
            'player_game_boxes': [{'game_id': gid, 'player_id': 'p1', 'team_id': home_tid, 'points': 25}]
        }
        payload = {
            'save_id': self.save_id, 'run_id': 'u_missing_box', 'unit_id': 'u_missing_box', 'source_key': 'TEST',
            'observed_at': '2026-11-01T10:00:00Z', 'evidence_grade': 'RESEARCH_FIXTURE', 'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'}, 'facts': facts,
            'artifacts': [{'sha256': 'c'*64, 'payload_kind': 'T', 'payload_ref': 'r', 'byte_count': 1, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        ver = orch.verify_game_sql_integrity(gid)
        self.assertFalse(ver['verified_in_db'])
        self.assertIn('missing away team box', ver['reason'])

    def test_sql_verification_fails_closed_on_score_mismatch(self):
        gid = 'game:native:mismatch'
        home_tid = 'team:native:1'
        away_tid = 'team:native:2'
        facts = {
            'teams': [
                {'team_id': home_tid, 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': away_tid, 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'players': [{'player_id': 'p1', 'native_player_id': '1', 'display_name': 'P1'}],
            'games': [{'game_id': gid, 'home_team_id': home_tid, 'away_team_id': away_tid, 'game_date': '2021-11-02', 'season_id': 's1'}],
            'game_state_observations': [{'game_id': gid, 'status_code': 'FINAL', 'is_final': 1, 'was_simulated': 1, 'score_provenance': 'TEST'}],
            'game_period_scores': [
                {'game_id': gid, 'team_id': home_tid, 'period_index': 1, 'period_points': 25},
                {'game_id': gid, 'team_id': away_tid, 'period_index': 1, 'period_points': 20}
            ],
            'team_game_boxes': [
                {'game_id': gid, 'team_id': home_tid, 'points': 25},
                {'game_id': gid, 'team_id': away_tid, 'points': 30}  # Period score was 20, box says 30! Mismatch!
            ],
            'player_game_boxes': [{'game_id': gid, 'player_id': 'p1', 'team_id': home_tid, 'points': 25}]
        }
        payload = {
            'save_id': self.save_id, 'run_id': 'u_mismatch', 'unit_id': 'u_mismatch', 'source_key': 'TEST',
            'observed_at': '2026-11-01T10:00:00Z', 'evidence_grade': 'RESEARCH_FIXTURE', 'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'}, 'facts': facts,
            'artifacts': [{'sha256': 'd'*64, 'payload_kind': 'T', 'payload_ref': 'r', 'byte_count': 1, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        ver = orch.verify_game_sql_integrity(gid)
        self.assertFalse(ver['verified_in_db'])
        self.assertFalse(ver.get('score_conservation', True))
        self.assertIn('score conservation mismatch', ver['reason'])

    def test_vae_export_deduplication_across_multiple_capture_units(self):
        gid = 'game:native:dedup'
        home_tid = 'team:native:1'
        away_tid = 'team:native:2'
        facts1 = {
            'teams': [
                {'team_id': home_tid, 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': away_tid, 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'games': [{'game_id': gid, 'home_team_id': home_tid, 'away_team_id': away_tid, 'game_date': '2021-11-03', 'season_id': 's1'}],
            'game_state_observations': [{'game_id': gid, 'status_code': 'FINAL', 'is_final': 1, 'was_simulated': 1, 'score_provenance': 'TEST'}],
            'team_game_boxes': [
                {'game_id': gid, 'team_id': home_tid, 'points': 100},
                {'game_id': gid, 'team_id': away_tid, 'points': 90}
            ]
        }
        payload1 = {
            'save_id': self.save_id, 'run_id': 'u_dedup_1', 'unit_id': 'u_dedup_1', 'source_key': 'TEST',
            'observed_at': '2026-11-01T10:00:00Z', 'evidence_grade': 'RESEARCH_FIXTURE', 'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'}, 'facts': facts1,
            'artifacts': [{'sha256': 'e'*64, 'payload_kind': 'T', 'payload_ref': 'r', 'byte_count': 1, 'source_version': '1', 'restricted': 1}]
        }
        # Second capture unit re-recording identical game
        facts2 = {
            'game_state_observations': [{'game_id': gid, 'status_code': 'FINAL', 'is_final': 1, 'was_simulated': 1, 'score_provenance': 'TEST'}],
            'team_game_boxes': [
                {'game_id': gid, 'team_id': home_tid, 'points': 100},
                {'game_id': gid, 'team_id': away_tid, 'points': 90}
            ]
        }
        payload2 = {
            'save_id': self.save_id, 'run_id': 'u_dedup_2', 'unit_id': 'u_dedup_2', 'source_key': 'TEST',
            'observed_at': '2026-11-01T11:00:00Z', 'evidence_grade': 'RESEARCH_FIXTURE', 'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'}, 'facts': facts2,
            'artifacts': [{'sha256': 'f'*64, 'payload_kind': 'T', 'payload_ref': 'r', 'byte_count': 1, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload1)
            ingest_capture(conn, payload2)

        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        export_out = self.tmp_path / 'vae_dedup_exports'
        res = orch.export_vae_standard_datasets(export_out)

        d1 = json.loads((export_out / 'calendar_sim_completed_game_player_team_metrics.json').read_text(encoding='utf-8'))
        # Must be exactly 1 game, not duplicated to 2!
        matching_games = [g for g in d1['games'] if g['game_id'] == gid]
        self.assertEqual(len(matching_games), 1)
        matching_boxes = [tb for tb in d1['team_boxes'] if tb['game_id'] == gid]
        self.assertEqual(len(matching_boxes), 2)  # Home + Away, not 4!

    def test_canonical_ids_in_vae_experiment_input(self):
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        export_out = self.tmp_path / 'vae_canon_exports'
        orch.export_vae_standard_datasets(export_out)
        d3 = json.loads((export_out / 'vae_experiment_evidence_input.json').read_text(encoding='utf-8'))

        p1 = d3['pilots'][0]
        self.assertEqual(p1['s1_intervention_candidate']['canonical_id'], 'TENDENCY_NATIVE_001')
        self.assertEqual(p1['s1_intervention_candidate']['associated_metric_field'], 'TENDENCY_NATIVE_066')
        self.assertEqual(p1['s1_intervention_candidate']['coach_play_setting'], 'COACH_DEFAULT_001')
        self.assertNotIn('same seed', p1['matched_control_team'].lower())

        p2 = d3['pilots'][1]
        self.assertEqual(p2['s1_intervention_candidate']['canonical_id'], 'COACH_DEFAULT_014')

        p3 = d3['pilots'][2]
        self.assertEqual(p3['s1_intervention_candidate']['canonical_id'], 'COACH_DEFAULT_015')

    def test_trigger_world_capture_mode_incremental_skip(self):
        reader = ScheduleMemory()
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        progress_1 = orch.inspect_calendar_progress(reader)
        target_gid = progress_1['latest_memory_game_id']

        # Ingest game into DB
        facts = {
            'teams': [
                {'team_id': 'team:native:1', 'native_team_id': '1', 'display_name': 'Team 1'},
                {'team_id': 'team:native:2', 'native_team_id': '2', 'display_name': 'Team 2'}
            ],
            'games': [
                {'game_id': target_gid, 'home_team_id': 'team:native:1', 'away_team_id': 'team:native:2',
                 'game_date': '2021-10-24', 'season_id': 's1'}
            ],
            'game_state_observations': [
                {'game_id': target_gid, 'status_code': 'FINAL', 'is_final': 1,
                 'overtime_count': 0, 'attendance': 18000, 'was_simulated': 1, 'score_provenance': 'TEST'}
            ]
        }
        payload = {
            'save_id': self.save_id, 'run_id': 'unit_run_skip', 'unit_id': 'unit_run_skip',
            'source_key': 'BOUND_TEST', 'observed_at': '2026-10-24T10:00:00Z',
            'evidence_grade': 'RESEARCH_FIXTURE', 'decoder_version': '1.0',
            'season': {'season_id': 's1', 'season_code': '2021-22'}, 'facts': facts,
            'artifacts': [{'sha256': '1' * 64, 'payload_kind': 'TEST', 'payload_ref': 'test.bin', 'byte_count': 10, 'source_version': '1', 'restricted': 1}]
        }
        with connect(self.db) as conn:
            ingest_capture(conn, payload)

        res = orch.trigger_world_capture(reader, mode='INCREMENTAL')
        self.assertEqual(res['status'], 'SAME_STATE_REPEAT')
        self.assertFalse(res['triggered'])

    def test_trigger_world_capture_mode_export_only(self):
        orch = CalendarSimOrchestrator(str(self.save_dir), self.loaded_filename, str(self.db))
        export_out = self.tmp_path / 'export_only_test'
        res = orch.trigger_world_capture(mode='EXPORT_ONLY', output_directory=export_out)
        self.assertEqual(res['status'], 'SUCCESS_EXPORT_ONLY')
        self.assertEqual(res['mode'], 'EXPORT_ONLY')
        self.assertFalse(res['triggered'])
        self.assertTrue((export_out / 'vae_exports' / 'manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
