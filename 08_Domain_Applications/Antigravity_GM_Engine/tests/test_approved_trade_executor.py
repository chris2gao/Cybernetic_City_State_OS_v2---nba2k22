"""Synthetic executor checks: no real process connection or database access."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from approved_trade_executor import roster_transfer, execute_plan
from roster_associations import describe, active_count_byte


def team_fixture():
    raw = bytearray(0x1258)
    regular = list(range(100,115))
    struct.pack_into('<25Q', raw, 0, *(regular + [0]*6 + [190] + [0]*3))
    # Two outgoing regular members: 105 absent from five-player groups, 106 present.
    struct.pack_into('<13Q', raw, 0xd0, *(regular[:12] + [114]))
    groups = [100,101,102,106,104] * 8
    struct.pack_into('<40Q', raw, 0xd28, *groups)
    raw[0xcbc:0xcc0] = b'cash'
    raw[0xcb1]=15
    raw[0x1047]=0xd1
    return bytes(raw)


class FakeMemory:
    def __init__(self, fail=False, change_before=False):
        self.read_only = False
        self.pid, self.base_address = 7, 0x1000
        self.data = {0x2000: b'aaaaaaaa', 0x2008: b'bbbbbbbb'}
        if change_before:
            self.data[0x2000] = b'changed!'
        self.calls = 0
        self.fail = fail

    def read_bytes(self, address, size):
        return self.data.get(address)

    def write_bytes(self, address, raw):
        self.calls += 1
        if self.fail:
            self.data[address] = raw[:4] + self.data[address][4:]
            return False
        self.data[address] = raw
        return True


def tiny_plan():
    return {'action_id':'SYNTHETIC', 'decision_id':'SYNTHETIC', 'version':1, 'save_id':'SYNTHETIC',
            'process':{'pid':7,'module_base':0x1000}, 'status':'PLANNED',
            'teams':{}, 'players':[], 'picks':[],
            'patches':[{'address':addr,'before':before.hex(),'after':after.hex(),
                        'entity':str(addr),'kind':'SYNTHETIC'} for addr,before,after in
                       ((0x2000,b'aaaaaaaa',b'11111111'),(0x2008,b'bbbbbbbb',b'22222222'))]}


class RosterTransferTests(unittest.TestCase):
    def test_two_for_one_preserves_non_targets_twoway_and_finance(self):
        old = team_fixture()
        new = roster_transfer(old,[105,106],[200],{105:0,106:200})
        before = set(struct.unpack_from('<25Q',old)) - {0}
        after = set(struct.unpack_from('<25Q',new)) - {0}
        self.assertEqual(after,(before-{105,106})|{200})
        self.assertEqual(new[21*8:25*8],old[21*8:25*8])
        self.assertEqual(new[0x138:0xcb1],old[0x138:0xcb1])
        self.assertEqual(new[0xcb2:0xd28],old[0xcb2:0xd28])
        self.assertEqual(new[0xe68:0x1047],old[0xe68:0x1047])
        self.assertEqual(new[0x1048:],old[0x1048:])
        self.assertEqual(new[0xcb1],14)
        self.assertEqual(new[0x1047],0xc1)
        self.assertTrue(describe(new)['valid'])
        self.assertEqual(sum(p != 0 for p in struct.unpack_from('<25Q',new)),15)
        self.assertNotIn(105,struct.unpack_from('<13Q',new,0xd0))
        self.assertNotIn(106,struct.unpack_from('<40Q',new,0xd28))

    def test_unknown_outgoing_reference_rejects_plan(self):
        raw = bytearray(team_fixture())
        struct.pack_into('<Q',raw,0xf00,106)
        with self.assertRaisesRegex(ValueError,'unknown team field'):
            roster_transfer(bytes(raw),[105,106],[200],{105:0,106:200})

    def test_five_player_reference_cannot_be_emptied(self):
        with self.assertRaisesRegex(ValueError,'five-player'):
            roster_transfer(team_fixture(),[106],[],{106:0})

    def test_twoway_transfer_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Two-way'):
            roster_transfer(team_fixture(),[190],[200],{190:200})


class JournalTests(unittest.TestCase):
    def setUp(self):
        # Synthetic in-memory writer only; production remains quarantined.
        self.enabled = patch('approved_trade_executor.EXECUTION_ENABLED',True)
        self.enabled.start()
        self.addCleanup(self.enabled.stop)

    def test_quarantine_prevents_even_an_approved_write(self):
        mem=FakeMemory()
        with tempfile.TemporaryDirectory() as out, patch('approved_trade_executor.EXECUTION_ENABLED',False):
            with self.assertRaisesRegex(PermissionError,'quarantined'):
                execute_plan(mem,tiny_plan(),{},out,True)
        self.assertEqual(mem.calls,0)

    def test_no_approval_never_calls_writer(self):
        mem = FakeMemory()
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(PermissionError):
                execute_plan(mem,tiny_plan(),{},out)
        self.assertEqual(mem.calls,0)

    def test_changed_original_prevents_first_write(self):
        mem = FakeMemory(change_before=True)
        with tempfile.TemporaryDirectory() as out:
            receipt = execute_plan(mem,tiny_plan(),{},out,True)
        self.assertEqual(mem.calls,0)
        self.assertEqual(receipt['status'],'PRECONDITION_FAILED')

    def test_short_write_stops_without_retry_and_preserves_marker(self):
        mem = FakeMemory(fail=True)
        with tempfile.TemporaryDirectory() as out:
            with patch('approved_trade_executor.verify_plan',return_value={'verified':False}):
                receipt = execute_plan(mem,tiny_plan(),{},out,True)
            self.assertEqual(mem.calls,1)
            self.assertEqual(receipt['status'],'WRITE_RESULT_UNKNOWN')
            self.assertEqual(mem.data[0x2008],b'bbbbbbbb')
            saved = (Path(out)/'receipt.json').read_bytes()
            with self.assertRaisesRegex(RuntimeError,'Prior write attempt'):
                execute_plan(mem,tiny_plan(),{},out,True)
            self.assertEqual((Path(out)/'receipt.json').read_bytes(),saved)

    def test_success_journals_every_readback(self):
        mem = FakeMemory()
        with tempfile.TemporaryDirectory() as out:
            with patch('approved_trade_executor.verify_plan',return_value={'verified':True}):
                receipt = execute_plan(mem,tiny_plan(),{},out,True)
            self.assertEqual(receipt['status'],'EXECUTED_VERIFIED')
            self.assertEqual(receipt['write_calls'],2)
            self.assertTrue(all(s['status']=='READBACK_MATCHED' for s in receipt['journal']))
            self.assertEqual(receipt['database'],'NOT_SYNCED')
            self.assertEqual(receipt['persistence'],'PERSISTENCE_NOT_VERIFIED')


class NativeCountTests(unittest.TestCase):
    def raw(self):
        raw=bytearray(team_fixture())
        raw[0xcb1]=15
        raw[0x1047]=0xd1
        return raw

    def test_valid_baseline_counts(self):
        self.assertTrue(describe(bytes(self.raw()))['valid'])

    def test_observed_two_way_member_can_be_active(self):
        raw=self.raw()
        struct.pack_into('<Q',raw,0x130,190)
        self.assertTrue(describe(bytes(raw))['valid'])

    def test_added_white_must_increment_visible_roster_count(self):
        raw=self.raw()
        raw[0xcb1]=14
        result=describe(bytes(raw))
        self.assertFalse(result['valid'])
        self.assertFalse(result['checks']['regular_count_matches'])

    def test_null_last_active_slot_must_decrement_active_count(self):
        raw=self.raw()
        struct.pack_into('<Q',raw,0x130,0)
        self.assertFalse(describe(bytes(raw))['checks']['active_count_matches'])
        raw[0x1047]=active_count_byte(raw[0x1047],12)
        self.assertTrue(describe(bytes(raw))['valid'])

    def test_packed_count_preserves_every_lower_bit_and_rejects_overflow(self):
        for lower in range(16):
            self.assertEqual(active_count_byte(0xd0|lower,12),0xc0|lower)
        with self.assertRaises(ValueError):
            active_count_byte(0xd1,14)


if __name__ == '__main__':
    unittest.main()
