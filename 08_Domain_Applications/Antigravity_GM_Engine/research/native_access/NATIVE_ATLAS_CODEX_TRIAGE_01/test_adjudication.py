"""Counterexamples plus independent fixture/operand checks, not live acceptance."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import adjudicate as a
from capstone import Cs,CS_ARCH_X86,CS_MODE_64


class EvidenceTests(unittest.TestCase):
    def test_descriptor_comparison_uses_numeric_null_identity(self):
        old=a.load('sources/ag01c/object_catalog.json')['descriptors']
        new=a.load('sources/wide/native_object_atlas_75.json')['slots']
        self.assertEqual({s['slot_index'] for s in new},set(range(75)))
        self.assertEqual(len(old),75)
        for h,n in zip(old,new):
            self.assertEqual(h['slot_index'],n['slot_index'])
            self.assertEqual(h['count'],n['live_count'])
            self.assertEqual(a.pointer_number(h['pointer_hex']),a.pointer_number(n['live_pdata_hex']))
        self.assertEqual(a.pointer_number('NULL'),a.pointer_number('0x0'))
        raw=(a.ROOT/'sources/ag01b/fixtures/roster_descriptors_raw.bin').read_bytes()
        self.assertEqual(len(raw),75*16)
        for (count,pointer),h in zip(struct.iter_unpack('<QQ',raw),old):
            self.assertEqual(count,h['count'])
            self.assertEqual(pointer,a.pointer_number(h['pointer_hex']))

    def test_slot39_rejects_proposed_leading_player_season(self):
        raw=(a.ROOT/'sources/ag01c/fixtures/sample_record_book_500.bin').read_bytes()
        self.assertEqual(len(raw),500*52)
        first=a.record_fields(raw[:52]);second=a.record_fields(raw[52:104])
        self.assertEqual((first['first_text'],first['last_text'],first['numeric_value']),('Wilt','Chamberlain',100.0))
        self.assertEqual((second['first_text'],second['last_text'],second['numeric_value']),('Kobe','Bryant',81.0))
        self.assertEqual(struct.unpack_from('<HH',raw),(26967,29804))
        self.assertGreater(struct.unpack_from('<H',raw,2)[0],2100)
        # Historical decoder calls this player_id, but it exceeds the observed pool.
        self.assertGreater(first['tail_words_raw'][2],3390)
        self.assertNotIn('player_id',first)
        self.assertNotIn('season_year',first)
        for i in range(500):a.record_fields(raw[i*52:(i+1)*52])
        for n in [0,51,53]:
            with self.assertRaises(ValueError):a.record_fields(bytes(n))

    def test_slot22_grid_counterexample_and_exact_play_dispatch(self):
        with self.assertRaises(ValueError):a.check_layout(360,[(0,48*5*2)])
        a.check_layout(360,[(0,88),(88,68*4)])
        raw=bytearray(360);raw[84]=0xe5
        struct.pack_into('<I',raw,88,0x79215b33);struct.pack_into('<I',raw,356,0x12345678)
        decoded=a.raw_playbook_fields(raw)
        self.assertEqual(len(decoded['play_values_raw']),68)
        self.assertEqual(decoded['play_values_raw'][0],0x79215b33)
        self.assertEqual(decoded['play_values_raw'][67],0x12345678)
        self.assertEqual(decoded['lookup_key_low7'],0x65)
        with self.assertRaises(ValueError):a.raw_playbook_fields(bytes(359))
        static=a.load('static_evidence.json');dispatch=static['playbook_dispatch']
        self.assertEqual(len(dispatch['cases']),68)
        self.assertEqual([c['field_offset'] for c in dispatch['cases']],list(range(88,360,4)))
        self.assertEqual([x[0] for x in struct.iter_unpack('<I',bytes.fromhex(dispatch['table_hex']))],
                         [int(c['target_rva'],16) for c in dispatch['cases']])
        cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
        for case in dispatch['cases']:
            i=next(cs.disasm(bytes.fromhex(case['code']['hex']),0x140000000+int(case['target_rva'],16)))
            self.assertEqual(i.mnemonic,'mov')
            self.assertEqual(i.reg_name(i.operands[1].mem.base),'rcx')
            self.assertEqual(i.operands[1].mem.disp,case['field_offset'])
            self.assertEqual(i.operands[1].size,4)

    def test_slot9_no_float_rounding_or_adjacent_gap_stride(self):
        for count,stride in [(583,60.01),(583,60.0),(True,60),(583,True),(583,0),(-1,60)]:
            with self.assertRaises(ValueError):a.checked_size(count,stride)
        self.assertEqual(a.checked_size(583,60),34980)
        self.assertNotEqual(34984/583,60)
        self.assertEqual(34984-583*60,4)
        src=a.load('sources/ag01b/fixtures/sample_descriptors.json')['descriptors'][9]
        wide=a.load('sources/wide/native_object_atlas_75.json')['slots'][9]
        self.assertEqual(src['inferred_stride'],60.01)
        self.assertEqual(src['inferred_stride'],wide['inferred_stride_bytes'])

    def test_draft_layout_keeps_protection_unknown_and_preserves_full_words(self):
        meta=(123<<22)|(1<<17)|(5<<19)|(27<<8)|(1<<3)|4
        raw=struct.pack('<QQQII',0x123456789,0x987654321,0,0xabcdef01,meta)
        row=a.raw_draft_fields(raw)
        self.assertEqual((row['qword_00'],row['qword_08']),(0x123456789,0x987654321))
        self.assertEqual((row['group_low3'],row['round_code_raw'],row['index_raw']),(4,1,27))
        self.assertTrue(row['alternate_identity_bit17'])
        self.assertEqual(row['metadata_raw'],meta)
        self.assertEqual(row['protection'],'UNKNOWN_NOT_DECODED')
        self.assertEqual(row['swap'],'UNKNOWN_NOT_DECODED')
        with self.assertRaises(ValueError):a.raw_draft_fields(bytes(31))

    def test_source_hashes_and_generated_findings(self):
        for item in a.load('source_manifest.json')['sources']:
            raw=(a.ROOT/item['local_path']).read_bytes()
            self.assertEqual(len(raw),item['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
        expected=a.load('adjudication_75.json')
        self.assertEqual(a.build(),expected)
        self.assertEqual(expected['summary']['matching_historical_pairs'],75)
        self.assertEqual(expected['audit']['explicit_logged_calls'],135)
        self.assertEqual(expected['audit']['explicit_object_sample_bytes'],334)
        self.assertEqual(expected['summary']['new_live_reads_performed'],0)
        for row in expected['slots']:
            self.assertIn('DESCRIPTOR_OBSERVED',row['evidence_labels'])
            self.assertEqual(row['current_save_identity'],'NOT_VERIFIED')

if __name__=='__main__':unittest.main()
