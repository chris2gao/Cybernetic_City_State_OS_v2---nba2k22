"""Native group codec and mixed-value semantics; synthetic bytes only."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from coach_codec import load_profile
from coaching_overall import overall_from_raw
from defense_codec import encode_defense


class OverallTests(unittest.TestCase):
    def setUp(self):
        profile=load_profile()
        self.rule=profile['opponent_overall_defense']
        self.catalog=profile['defensive_fields']
        self.raw=bytearray(0x370)
        self.raw[2:6]=bytes([0,0,20,0])
        for index in range(23):
            at=0x64+index*12
            self.raw[at:at+4]=b'\xff'*4
        for index,mid in enumerate((42,43)):
            at=0x64+index*12
            self.raw[at:at+2]=mid.to_bytes(2,'little')
            self.raw[at+4:at+12]=(0xabcd000000000000).to_bytes(8,'little')
    def read(self):return overall_from_raw(bytes(self.raw),self.rule,self.catalog)
    def test_group_excludes_empty_slots_and_preserves_assignment_ids(self):
        result=self.read()
        self.assertEqual(result['identity']['entry_count'],2)
        self.assertEqual([b['identity']['matchup_id'] for b in result['blocks']],[42,43])
        self.assertTrue(all(b['identity']['defender_id']==65535 for b in result['blocks']))
    def test_mixed_source_is_explicit_unknown_not_a_fabricated_common_value(self):
        self.raw[0x74]=1
        result=self.read()
        self.assertIsNone(result['values']['PressureOnball'])
        self.assertEqual(result['mixed_fields'],['PressureOnball'])
    def test_all_native_enum_values_and_boolean_roundtrip_with_reserved_bits(self):
        for name,field in self.catalog.items():
            values=(0,1) if field.get('native_boolean') else map(int,field['native_enum_name_crc32'])
            for target in values:
                raw=self.read()['blocks'][0]['raw_block']
                result=encode_defense(bytes.fromhex(raw),[dict(field=name,before_raw=0,after_raw=target)],self.catalog)
                # Compare byte-order independent integer masks.
                old=int.from_bytes(bytes.fromhex(raw),'little')
                new=int.from_bytes(bytes.fromhex(result['after']),'little')
                self.assertEqual((old^new)&~result['mask'],0)
                changed=copy.copy(self.raw)
                changed[0x68:0x70]=bytes.fromhex(result['after'])
                observed=overall_from_raw(bytes(changed),self.rule,self.catalog)
                self.assertEqual(observed['blocks'][0]['values'][name],target)
                self.assertEqual(observed['blocks'][1]['raw_block'],self.read()['blocks'][1]['raw_block'])
    def test_duplicate_ids_unknown_flags_and_unverified_layout_fail_closed(self):
        self.raw[0x70:0x72]=(42).to_bytes(2,'little')
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):self.read()
        self.raw[0x70:0x72]=(43).to_bytes(2,'little')
        self.raw[0]=2
        with self.assertRaisesRegex(ValueError,'COMMIT_FLAG'):self.read()


if __name__=='__main__':unittest.main()
