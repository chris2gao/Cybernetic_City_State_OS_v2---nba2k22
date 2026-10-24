"""Deterministic probe boundary tests; these do not prove a live memory call."""
import json
from pathlib import Path
import struct
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from live_reader import collect_known_game,probe,SEASON_RVA,GAME_OFFSET,STATBANK_OFFSET
from readers import NATIVE


class FixtureReader:
    module_base=0x140000000
    module_size=0x08000000
    season=0x20000000
    def __init__(self):
        self.calls=[]
        self.header=(NATIVE/'fixtures/sample_season_header.bin').read_bytes()
        self.game=(NATIVE/'fixtures/sample_games_slice.bin').read_bytes()[:60]
        self.bank=(NATIVE/'fixtures/sample_statbank_slice.bin').read_bytes()
    def read(self,address,size,label):
        self.calls.append((address,size,label))
        if address==self.module_base+SEASON_RVA:return struct.pack('<Q',self.season)
        if address==self.season:return self.header
        if address==self.season+GAME_OFFSET:return self.game
        idx=int.from_bytes(self.game[20:22],'little')
        if address==self.season+STATBANK_OFFSET+idx*24:return self.bank[:size]
        raise AssertionError('unexpected source address')


class LiveReaderBoundaryTests(unittest.TestCase):
    def test_known_fixture_shape_and_conservation_without_live_claim(self):
        reader=FixtureReader();result=collect_known_game(reader,0)
        self.assertEqual(len(reader.calls),4)
        self.assertTrue(all(size<=1248 for _,size,_ in reader.calls))
        self.assertEqual(result['save_binding'],'UNKNOWN_NOT_INFERRED_FROM_PID')
        self.assertEqual(result['active_schedule_window'],'NOT_PROVEN')
        self.assertTrue(result['decoded']['conservation']['home_score_exact'])
        self.assertTrue(result['decoded']['conservation']['away_score_exact'])

    def test_outside_capacity_does_not_read(self):
        r=FixtureReader()
        with self.assertRaises(ValueError):collect_known_game(r,1232)
        self.assertEqual(r.calls,[])

    def test_invalid_participant_count_does_not_read_statbank(self):
        r=FixtureReader();game=bytearray(r.game);game[22]=255;r.game=bytes(game)
        with self.assertRaisesRegex(ValueError,'participant count'):collect_known_game(r,0)
        self.assertEqual(len(r.calls),3)

    def test_access_denial_stays_unavailable_and_no_facts(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'probe'
            with patch('live_reader.ReadOnlyGameProcess',side_effect=PermissionError('test access denied')):
                result=probe(123,out,0)
            self.assertEqual(result['status'],'SOURCE_UNAVAILABLE')
            self.assertFalse(result['source_facts_ingested'])
            self.assertEqual(result['artifact_sha256'],{})
            self.assertFalse(list(out.glob('*.bin')))
            self.assertEqual(json.loads((out/'live-probe-report.json').read_text())['save_binding'],'UNKNOWN')


if __name__=='__main__':unittest.main()
