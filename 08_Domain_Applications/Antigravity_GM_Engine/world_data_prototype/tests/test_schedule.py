"""Whole-window identities, unplayed null semantics and final-value history."""
import copy,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from test_live_reader import FixtureReader
from schedule_reader import collect_schedule,index_relationship,schedule_facts
from live_reader import ROSTER_RVA,GAME_OFFSET,STATBANK_OFFSET,SEASON_RVA
from engine import create_database,connect,ingest_synthetic_capture,ingest_or_quarantine
from cli import synthetic_payload
from readers import _module
from schema_model import VERSION
from family_codec import decode_fixed_utf16


class ScheduleMemory(FixtureReader):
    root=0x30000000;index=0x40000000
    def __init__(self,changed=False):
        super().__init__();self.changed=changed
        future=bytearray(self.game);struct.pack_into('<I',future,8,2);struct.pack_into('<I',future,56,0)
        future[20:56]=b'\0'*36
        self.games=self.game+bytes(future);self.index_raw=b''
        h,a=struct.unpack_from('<HH',self.game,12)
        self.context={'teams':[{'address':0x50000000,'native_team_id':h},{'address':0x50001258,'native_team_id':a}]}
        for raw in (self.game,bytes(future)):
            date=struct.unpack_from('<I',raw)[0]&~31
            self.index_raw+=struct.pack('<IIQQII',date,0,0x50000000,0x50001258,0,0)
    def read(self,address,size,label):
        self.calls.append((address,size,label))
        if label=='SCHEDULE_GAMES_RECHECK' + ':0' and self.changed:return b'\xff'*size
        if address==self.module_base+SEASON_RVA:return struct.pack('<Q',self.season)
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',self.root)
        if address==self.root+10*16:return struct.pack('<QQ',2,self.index)
        if address==self.season:return self.header
        if self.season+GAME_OFFSET<=address and address+size<=self.season+GAME_OFFSET+len(self.games):
            off=address-self.season-GAME_OFFSET;return self.games[off:off+size]
        if self.index<=address and address+size<=self.index+len(self.index_raw):
            off=address-self.index;return self.index_raw[off:off+size]
        start=int.from_bytes(self.game[20:22],'little')
        if address==self.season+STATBANK_OFFSET+start*24:return self.bank[:size]
        raise AssertionError('unexpected source address '+label)


class ScheduleTests(unittest.TestCase):
    def test_uninitialized_name_padding_is_not_part_of_utf16_text(self):
        self.assertEqual(decode_fixed_utf16('Chris'.encode('utf-16le')+b'\0\0'+b'\0\xd8'),'Chris')
        with self.assertRaises(UnicodeDecodeError):decode_fixed_utf16(b'\0\xd8'+b'\0\0')
    def test_all_record_index_relationship_and_unplayed_absence(self):
        reader=ScheduleMemory();found=collect_schedule(reader)
        relation=index_relationship(found,reader.context)
        self.assertEqual(relation['all_record_matches'],{'date_except_low5':2,'home_team_pointer':2,'away_team_pointer':2})
        self.assertEqual(found['manifest']['status_counts'],{'2':1,'0':1})
        full=_module('boxscore_decoder').BoxScoreDecoder.decode_full_boxscore(reader.game,found['boxes'][0])
        ids={p['player_id'] for s in ('home_players','away_players') for p in full[s]}
        facts=schedule_facts(found,{'season_id':'s'},ids)
        self.assertEqual(len(facts['games']),2);self.assertEqual(len(facts['player_game_boxes']),26)
        future=facts['game_state_observations'][1]
        self.assertEqual(future['is_final'],0);self.assertNotIn('home_points',future)
        self.assertTrue(all(g['game_date'] is None for g in facts['games']))
        self.assertTrue(all(b['game_id'].endswith(':game:1') for b in facts['player_game_boxes']))

    def test_equal_count_with_different_team_pointer_is_rejected(self):
        r=ScheduleMemory();found=collect_schedule(r)
        changed=bytearray(found['native_index']);struct.pack_into('<Q',changed,8,0xDEADBEEF);found['native_index']=bytes(changed)
        with self.assertRaisesRegex(ValueError,'identity mismatch'):index_relationship(found,r.context)

    def test_mid_capture_schedule_change_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'schedule changed'):collect_schedule(ScheduleMemory(changed=True))

    def test_scheduled_inprogress_final_repeat_and_final_conflict(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'s')
            for run,status,final,points in (('a','0',0,None),('b','1',0,10),('c','2',1,22),('d','2',1,22)):
                p=synthetic_payload('s',run,run,'2026-10-24T00:00:00Z')
                p['game_state']={'status_code':status,'is_final':final}
                if points is None:p['boxes']=[]
                else:p['boxes']=[{'player_id':'player-a','team_id':'team-a','points':points}]
                with connect(db) as c:ingest_synthetic_capture(c,p)
            with connect(db,True) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM game_state_observations').fetchone()[0],4)
                self.assertEqual(c.execute('SELECT count(*) FROM player_game_boxes').fetchone()[0],3)
                self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],VERSION)
            p=synthetic_payload('s','e','e','2026-10-24T00:00:00Z');p['game_state']={'status_code':'2','is_final':1}
            p['boxes']=[{'player_id':'player-a','team_id':'team-a','points':23}]
            import sqlite3
            with connect(db) as c:
                with self.assertRaisesRegex(sqlite3.IntegrityError,'frozen game'):ingest_synthetic_capture(c,p)


if __name__=='__main__':unittest.main()
