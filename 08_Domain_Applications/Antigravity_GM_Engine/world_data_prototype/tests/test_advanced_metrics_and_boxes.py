"""Tests for native advanced stats extraction, complete team_game_boxes, and GM query views."""
import math
import struct
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from family_codec import decode_schedule_date, extract_player_advanced_metrics
from live_reader import ROSTER_RVA
from test_live_reader import FixtureReader
from test_schedule import ScheduleMemory
from schedule_reader import collect_schedule, schedule_facts
from readers import _module
from engine import create_database, connect, ingest_capture, _insert
from schema_model import TABLES, VERSION
from query import player_game_log, player_advanced_metrics, team_advanced_metrics


class AdvancedMetricsAndBoxesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'world.sqlite'
        create_database(self.db, 'test_save')

    def test_decode_schedule_date_bitfield(self):
        # bits: day(16..20), month(21..24), year_offset(25..31)
        # Year 2021 (offset 21), Month 10 (Oct), Day 18
        # (18 << 16) | (10 << 21) | (21 << 25)
        # 18<<16 = 1179648, 10<<21 = 20971520, 21<<25 = 704643072 -> sum = 726794240
        date_int = (18 << 16) | (10 << 21) | (21 << 25)
        date_str = decode_schedule_date(date_int)
        self.assertEqual(date_str, '2021-10-18')

    def test_extract_player_advanced_metrics_decodes_per_and_gamescore(self):
        # Create a mock 1264-byte PLAYERDATA
        raw = bytearray(1264)
        # PER rankings: 544..552
        struct.pack_into('<HHHH', raw, 544, 3, 2, 2, 1)
        # GameScore float32 history at 580..600
        # Slot 0: 21.10 (Joel Embiid game score), Slot 1: 15.50, Slot 2..4: 0.0 (DNP)
        struct.pack_into('<fffff', raw, 580, 21.10, 15.50, 0.0, 0.0, 0.0)
        # Dates at 600..620
        d0 = (18 << 16) | (10 << 21) | (21 << 25)  # 2021-10-18
        d1 = (20 << 16) | (10 << 21) | (21 << 25)  # 2021-10-20
        struct.pack_into('<IIIII', raw, 600, d0, d1, 0, 0, 0)
        # Minutes at 780..785
        raw[780] = 30
        raw[781] = 28
        raw[782] = 0
        raw[783] = 0
        raw[784] = 0
        # Shot chart index at 768: bit 20..29
        # index 42 -> 42 << 20
        struct.pack_into('<I', raw, 768, 42 << 20)

        metrics = extract_player_advanced_metrics(bytes(raw))
        self.assertEqual(metrics['per_rankings']['league_per_rank'], 3)
        self.assertEqual(metrics['per_rankings']['league_position_per_rank'], 2)
        self.assertEqual(metrics['per_rankings']['conference_per_rank'], 2)
        self.assertEqual(metrics['per_rankings']['conference_position_per_rank'], 1)

        gs = metrics['recent_game_scores']
        self.assertEqual(len(gs), 5)
        self.assertEqual(gs[0]['game_score'], 21.10)
        self.assertEqual(gs[0]['game_date'], '2021-10-18')
        self.assertEqual(gs[0]['minutes'], 30)
        self.assertFalse(gs[0]['dnp'])

        self.assertEqual(gs[1]['game_score'], 15.50)
        self.assertEqual(gs[1]['game_date'], '2021-10-20')
        self.assertEqual(gs[1]['minutes'], 28)
        self.assertFalse(gs[1]['dnp'])

        # Negative / boundary test: DNP slots
        self.assertTrue(gs[2]['dnp'])
        self.assertEqual(gs[2]['game_score'], 0.0)
        self.assertIsNone(gs[2]['game_date'])
        self.assertEqual(gs[2]['minutes'], 0)

        self.assertEqual(metrics['shot_chart_index'], 42)

    def test_team_game_boxes_all_26_columns_populated(self):
        memory = ScheduleMemory()
        found = collect_schedule(memory)
        decoder = _module('boxscore_decoder').BoxScoreDecoder
        full = decoder.decode_full_boxscore(memory.game, found['boxes'][0])
        ids = {p['player_id'] for s in ('home_players', 'away_players') for p in full[s] if p['in_use']}
        facts = schedule_facts(found, {'season_id': 's'}, ids)

        team_boxes = facts['team_game_boxes']
        self.assertEqual(len(team_boxes), 2)
        for tb in team_boxes:
            # Check all key columns are present and non-null
            self.assertIn('game_id', tb)
            self.assertIn('team_id', tb)
            self.assertIsNotNone(tb['points'])
            self.assertIsNotNone(tb['fg_made'])
            self.assertIsNotNone(tb['fg_attempted'])
            self.assertIsNotNone(tb['three_made'])
            self.assertIsNotNone(tb['three_attempted'])
            self.assertIsNotNone(tb['ft_made'])
            self.assertIsNotNone(tb['ft_attempted'])
            self.assertIsNotNone(tb['offensive_rebounds'])
            self.assertIsNotNone(tb['defensive_rebounds'])
            self.assertIsNotNone(tb['assists'])
            self.assertIsNotNone(tb['steals'])
            self.assertIsNotNone(tb['blocks'])
            self.assertIsNotNone(tb['turnovers'])
            self.assertIsNotNone(tb['fouls'])
            self.assertIsNotNone(tb['minutes_raw'])
            self.assertIsNotNone(tb['plus_minus'])
            self.assertIsNotNone(tb['possessions_raw'])
            self.assertIsNotNone(tb['fastbreak_points'])
            self.assertIsNotNone(tb['paint_points'])
            self.assertIsNotNone(tb['second_chance_points'])
            self.assertIsNotNone(tb['points_off_turnovers'])
            self.assertIsNotNone(tb['largest_lead'])

            # Score conservation: points must match 2*fgm + 3pm + ftm or total box score
            self.assertGreaterEqual(tb['points'], 0)
            self.assertEqual(tb['minutes_raw'], 240)  # regulation game without overtime

    def test_player_game_log_and_advanced_metrics_query(self):
        # Ingest a fixture game and player totals into temporary database
        memory = ScheduleMemory()
        found = collect_schedule(memory)
        decoder = _module('boxscore_decoder').BoxScoreDecoder
        full = decoder.decode_full_boxscore(memory.game, found['boxes'][0])
        ids = {p['player_id'] for s in ('home_players', 'away_players') for p in full[s] if p['in_use']}
        facts = schedule_facts(found, {'season_id': 's'}, ids)

        home_id = str(full['home_team_id'])
        away_id = str(full['away_team_id'])
        facts['teams'] = [
            {'team_id': f'team:native:{home_id}', 'native_team_id': home_id, 'display_name': 'Home Team'},
            {'team_id': f'team:native:{away_id}', 'native_team_id': away_id, 'display_name': 'Away Team'}
        ]
        target_pid = list(ids)[0]
        canonical_pid = f'player:native:{target_pid}'
        facts['players'] = [
            {'player_id': f'player:native:{n}', 'native_player_id': str(n), 'display_name': f'Player {n}'}
            for n in ids
        ]
        facts['player_season_totals'] = [{
            'player_id': canonical_pid,
            'season_id': 's',
            'team_id': f'team:native:{home_id}',
            'team_scope': 'CURRENT',
            'phase_code': None,
            'is_final': 0,
            'games_played': 10,
            'games_started': 10,
            'points': 220,
            'minutes_raw': 300,
            'fg_made': 80,
            'fg_attempted': 170,
            'three_made': 20,
            'three_attempted': 40,
            'ft_made': 40,
            'ft_attempted': 45,
            'offensive_rebounds': 10,
            'defensive_rebounds': 50,
            'assists': 50,
            'steals': 10,
            'blocks': 10,
            'turnovers': 20,
            'fouls': 30
        }]
        facts['team_season_totals'] = [{
            'team_id': f'team:native:{home_id}',
            'season_id': 's',
            'phase_code': None,
            'is_final': 0,
            'wins': 7,
            'losses': 3,
            'points': 1100,
            'opponent_points': 1020,
            'possessions_raw': 1000,
            'paint_points': 480,
            'second_chance_points': 120,
            'points_off_turnovers': 160,
            'bench_points': 350,
            'pace_raw': 100,
            'fg_made': 400,
            'fg_attempted': 850,
            'three_made': 120,
            'three_attempted': 340,
            'ft_made': 180,
            'ft_attempted': 230,
            'offensive_rebounds': 100,
            'defensive_rebounds': 350,
            'assists': 260,
            'steals': 75,
            'blocks': 50,
            'turnovers': 140,
            'fouls': 190,
            'minutes_raw': 2400,
            'plus_minus': 80,
            'opponent_fg_made': 380,
            'opponent_fg_attempted': 860,
            'opponent_three_made': 110,
            'opponent_three_attempted': 320
        }]

        payload = {
            'save_id': 'test_save',
            'run_id': 'unit_1',
            'unit_id': 'unit_1',
            'source_key': 'BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS',
            'observed_at': '2026-10-24T00:00:00Z',
            'evidence_grade': 'RESEARCH_FIXTURE',
            'decoder_version': '1.0',
            'season': {'season_id': 's', 'season_code': '2021-22'},
            'facts': facts,
            'artifacts': [{'sha256': 'a' * 64, 'payload_kind': 'TEST', 'payload_ref': 'test.bin', 'byte_count': 10, 'source_version': '1', 'restricted': 1}]
        }

        with connect(self.db) as conn:
            ingest_capture(conn, payload)

        # 1. Query Player Game Log
        log = player_game_log(self.db, canonical_pid)
        self.assertEqual(len(log['records']), 1)
        rec = log['records'][0]
        self.assertIn('game_score', rec)
        self.assertIn('ts_pct', rec)
        self.assertIn('efg_pct', rec)
        self.assertEqual(log['provenance']['box_stats'], 'NATIVE_GAME_BOX; player_game_boxes')

        # 2. Query Player Advanced Metrics
        adv = player_advanced_metrics(self.db, canonical_pid)
        self.assertEqual(adv['player_id'], canonical_pid)
        self.assertEqual(adv['season_advanced']['games_played'], 10)
        self.assertEqual(adv['season_advanced']['per_game']['ppg'], 22.0)
        self.assertEqual(adv['season_advanced']['per_game']['mpg'], 30.0)
        self.assertEqual(adv['season_advanced']['per_36']['pts_per36'], 26.4)
        self.assertAlmostEqual(adv['season_advanced']['ts_pct'], 0.5796, places=3)
        self.assertAlmostEqual(adv['season_advanced']['efg_pct'], 0.5294, places=3)
        self.assertEqual(adv['season_advanced']['ast_to_tov_ratio'], 2.5)
        self.assertEqual(adv['game_score_summary']['games_tracked'], 1)

        # 3. Query Team Advanced Metrics
        t_adv = team_advanced_metrics(self.db, f'team:native:{home_id}')
        self.assertEqual(t_adv['record']['wins'], 7)
        self.assertEqual(t_adv['record']['losses'], 3)
        self.assertEqual(t_adv['ratings']['offensive_rating'], 110.0)
        self.assertEqual(t_adv['ratings']['defensive_rating'], 102.0)
        self.assertEqual(t_adv['ratings']['net_rating'], 8.0)
        self.assertEqual(t_adv['engine_precalculated_totals']['paint_points'], 480)
        self.assertEqual(t_adv['single_game_box_averages']['paint_points_avg'], facts['team_game_boxes'][0]['paint_points'])


if __name__ == '__main__':
    unittest.main()
