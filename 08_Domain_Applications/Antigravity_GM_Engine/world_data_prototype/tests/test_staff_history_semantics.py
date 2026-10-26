"""Derived storage roles preserve raw observations and withhold calendar labels."""
import json,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from staff_history_semantics import PROFILE,reference_roles,verify_semantics_code
from query import native_staff_history
from observation_scope import query_at
from engine import connect
import test_staff_history as fixture


class StorageRolesTests(unittest.TestCase):
    def test_zero_clear_loop_and_last_slot_have_no_invented_calendar_label(self):
        decoder=PROFILE['compatible_source_decoder'];zero=reference_roles(0,65535,decoder);last=reference_roles(39,None,decoder)
        self.assertTrue(zero['native_increment_target']);self.assertTrue(zero['native_clear_loop_visits']);self.assertEqual(zero['next_free_marker_status'],'MATCHES_NATIVE_ALLOCATION_MARKER');self.assertFalse(last['native_increment_target']);self.assertFalse(last['native_clear_loop_visits']);self.assertIn('UNPROVED',last['position_role']);self.assertNotIn('career',last['position_role'].lower())
    def test_foreign_decoder_and_nonmarker_never_claim_allocation_or_year(self):
        self.assertEqual(reference_roles(0,65535,'OTHER_LAYOUT')['position_role'],'UNKNOWN');self.assertIsNone(reference_roles(0,65535,'OTHER_LAYOUT')['native_increment_target']);self.assertIn('REACHABILITY_UNPROVED',reference_roles(2,12,PROFILE['compatible_source_decoder'])['next_free_marker_status'])
        for position in (-1,40,True):
            with self.assertRaises(ValueError):reference_roles(position,None,PROFILE['compatible_source_decoder'])
    def test_exact_code_verification_rejects_changed_bytes_without_any_game_call(self):
        class Reader:
            module_base=0x140000000
            def __init__(self,changed=False):self.changed=changed;self.calls=[]
            def read(self,address,size,label):
                self.calls.append((address,size,label));raw=next(bytes.fromhex(p['code_hex']) for p in PROFILE['code_proofs'] if p['rva']==address-self.module_base);return bytes(size) if self.changed else raw
        reader=Reader();value=verify_semantics_code(reader);self.assertEqual(len(reader.calls),len(PROFILE['code_proofs']));self.assertEqual(value['getter_or_mutator_invocations'],0);self.assertEqual(value['staff_value_reads'],0)
        with self.assertRaises(ValueError):verify_semantics_code(Reader(changed=True))
    def test_position_query_cli_asof_and_stored_rows_remain_unchanged(self):
        helper=fixture.StaffHistoryTests()
        with TemporaryDirectory() as tmp:
            db=helper.db(tmp)
            with connect(db,True) as conn:before=[tuple(r) for r in conn.execute('SELECT * FROM native_staff_stat_links ORDER BY staff_stat_link_id')]
            value=native_staff_history(db,reference_position=2);self.assertEqual(len(value['records'][0]['references']),1);ref=value['records'][0]['references'][0];self.assertEqual(ref['array_position'],2);self.assertEqual(ref['next_free_raw'],65535);self.assertIsNone(ref['stat_year']);self.assertEqual(ref['storage_roles']['next_free_marker_status'],'MATCHES_NATIVE_ALLOCATION_MARKER')
            with self.assertRaises(ValueError):native_staff_history(db,reference_position=40)
            self.assertEqual(query_at(db,'2026-10-25T00:00:00Z','native_staff_history',reference_position=0)['result']['status'],'NOT_OBSERVED')
            import cli
            output=StringIO()
            with patch.object(sys,'argv',['cli.py','staff-history',str(db),'--reference-position','39','--as-of','2026-10-27T00:00:00Z']),redirect_stdout(output):cli.main()
            result=json.loads(output.getvalue())['result'];self.assertEqual(result['reference_position'],39);self.assertIsNone(result['records'][0]['references'][0]['coach_stat_id'])
            with connect(db,True) as conn:self.assertEqual([tuple(r) for r in conn.execute('SELECT * FROM native_staff_stat_links ORDER BY staff_stat_link_id')],before)


if __name__=='__main__':unittest.main()
