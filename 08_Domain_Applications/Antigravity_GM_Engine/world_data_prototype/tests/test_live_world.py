"""Acquisition consistency and typed routing; simulated memory is not live proof."""
import copy,json,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from live_world import collect_world,world_payload,initialize_save,read_binding,POTENTIAL,RESTRICTED_PLAYER_RANGES
from live_reader import ROSTER_RVA
from test_live_reader import FixtureReader
from engine import create_database,connect,ingest_capture
from readers import NATIVE,_module
from query import game_box,player_card


class WorldMemory(FixtureReader):
    root=0x30000000;players=0x40000000;teams=0x50000000;stats=0x60000000
    def __init__(self,ambiguous=False,changed=False,no_total=False):
        super().__init__();self.segments={};self.excluded_reads=0;self.changed=changed
        decoder=_module('boxscore_decoder').BoxScoreDecoder
        full=decoder.decode_full_boxscore(self.game,self.bank[:624])
        ids=sorted({p['player_id'] for s in ('home_players','away_players') for p in full[s] if p['in_use']})
        source=next(iter(json.loads((NATIVE/'fixtures/sample_player_career_slice.json').read_text()).values()))
        template=bytes.fromhex(source['raw_player_hex']);idx=int.from_bytes(template[0xFC:0xFE],'little')
        stat=bytes.fromhex(source['stats_records_hex'][str(idx)])
        records=[]
        for n in ids:
            for duplicate in range(1 if no_total and n==ids[-1] else 2):
                p=bytearray(template)
                for low,high in RESTRICTED_PLAYER_RANGES:p[low:high]=bytes([0xAB])*(high-low)
                struct.pack_into('<H',p,0x2F8,n);struct.pack_into('<H',p,0xFC,0 if duplicate==0 or ambiguous else 65535)
                if no_total and n==ids[-1]:struct.pack_into('<H',p,0xFC,65535)
                struct.pack_into('<Q',p,0x60,self.teams);struct.pack_into('<Q',p,0xA8,self.teams)
                records.append(bytes(p))
        self.segments[self.module_base+ROSTER_RVA]=struct.pack('<Q',self.root)
        self.segments[self.root+16]=struct.pack('<QQ',len(records),self.players)
        self.segments[self.root+8*16]=struct.pack('<QQ',2,self.teams)
        self.segments[self.root+24*16]=struct.pack('<QQ',1,self.stats)
        self.segments[self.players]=b''.join(records);self.player_count=len(records)
        for i,n in enumerate((full['home_team_id'],full['away_team_id'])):
            team=bytearray(4696);struct.pack_into('<H',team,0xCA8,n)
            team[0x2B4:0x2B4+40]='FixtureTeam'.encode('utf-16le').ljust(40,b'\0')
            team[0x2E6:0x2E6+36]='FixtureCity'.encode('utf-16le').ljust(36,b'\0')
            self.segments[self.teams+i*4696]=bytes(team)
        self.segments[self.stats]=stat
    def read(self,address,size,label):
        if label=='WORLD_GAME_RECHECK' and self.changed:return b'\xff'*size
        for i in range(self.player_count):
            for low,high in RESTRICTED_PLAYER_RANGES:
                start=self.players+i*1264+low;end=self.players+i*1264+high
                if address<end and address+size>start:self.excluded_reads+=1;raise AssertionError('restricted byte requested')
        for start,data in self.segments.items():
            if start<=address and address+size<=start+len(data):
                self.calls.append((address,size,label));return data[address-start:address-start+size]
        return super().read(address,size,label)


class LiveWorldTests(unittest.TestCase):
    def test_active_template_discrimination_routes_public_fields_and_boxes(self):
        reader=WorldMemory();found,manifest,blobs=collect_world(reader,0)
        self.assertEqual(reader.excluded_reads,0)
        self.assertTrue(all(not any(v[low:high]) for k,v in blobs.items() if k.endswith('.public.bin') for low,high in RESTRICTED_PLAYER_RANGES))
        self.assertTrue(all(x['selected_pool_index'] is not None and len(x['matched_indices'])==2 for x in manifest['player_links']))
        payload=world_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},found,manifest,blobs,
            [{'sha256':'0'*64,'payload_kind':'SIMULATED_MEMORY'}],'2026-10-24T00:00:00Z','fixture-1')
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,payload)
            result=game_box(db,payload['facts']['games'][0]['game_id'])
            self.assertEqual(len(result['player_boxes']),26)
            self.assertEqual(sorted(sum(r['points'] for r in result['player_boxes'] if r['team_id']==t['team_id']) for t in payload['facts']['teams']),[106,122])
            self.assertEqual(len(player_card(db,payload['facts']['players'][0]['player_id'])['families']['player_attribute_snapshots']),55)
            with connect(db,True) as c:self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            forged=copy.deepcopy(payload);forged['evidence_grade']='LIVE_READ'
            with connect(db) as c:
                with self.assertRaisesRegex(ValueError,'acquisition adapter'):ingest_capture(c,forged)

    def test_two_active_candidates_are_not_merged(self):
        found,manifest,blobs=collect_world(WorldMemory(ambiguous=True),0)
        self.assertTrue(all(x['selected_pool_index'] is None for x in manifest['player_links']))
        with self.assertRaisesRegex(ValueError,'single current native season'):world_payload(
            {'save_id':'fixture','native_save_filename':'file'},found,manifest,blobs,[],'2026-10-24T00:00:00Z','u')

    def test_source_change_rejects_mixed_observation(self):
        with self.assertRaisesRegex(ValueError,'game source changed'):collect_world(WorldMemory(changed=True),0)

    def test_unique_player_without_cumulative_row_keeps_game_and_no_invented_zero(self):
        found,manifest,blobs=collect_world(WorldMemory(no_total=True),0)
        payload=world_payload({'save_id':'fixture','native_save_filename':'file'},found,manifest,blobs,
            [{'sha256':'0'*64,'payload_kind':'SIMULATED_MEMORY'}],'2026-10-24T00:00:00Z','u')
        self.assertEqual(len(payload['facts']['players']),26)
        self.assertEqual(len(payload['facts']['player_game_boxes']),26)
        self.assertEqual(len(payload['facts']['player_season_totals']),25)
        self.assertTrue(any(g['target_field']=='UNOBSERVED_CURRENT_PLAYER_TOTALS' for g in payload['facts']['field_gaps']))

    def test_operator_filename_binding_survives_reopen_and_rejects_switch(self):
        with TemporaryDirectory() as tmp:
            directory=Path(tmp);native=directory/'MyLEAGUE0003';native.write_bytes(b'fixture, not a game save')
            save=directory/'nba2k22_test_01';initialize_save(save,'nba2k22_test_01',native)
            binding,digest=read_binding(save,'MyLEAGUE0003');self.assertEqual(binding['save_id'],'nba2k22_test_01')
            self.assertEqual(len(digest),64)
            with self.assertRaisesRegex(ValueError,'loaded save filename'):read_binding(save,'MyLEAGUE0004')
            with self.assertRaises(FileExistsError):initialize_save(save,'nba2k22_test_01',native)


if __name__=='__main__':unittest.main()
