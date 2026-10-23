import dataclasses
import hashlib
import json
from pathlib import Path
import struct
import unittest

from build_evidence import build
from decoders import (Pool, decode_history_slice, draft, history_index, linked_prefix,
                      player_names, signed_round, stat_value, walk_fixture)
from offline_policy import Binding, Denied, MockBackend, Policy, Reader

HERE = Path(__file__).resolve().parent


class FixtureRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((HERE/'decoded_fixtures.json').read_text(encoding='utf-8'))
        cls.static = json.loads((HERE/'static_capture.json').read_text(encoding='utf-8'))
        cls.dispatch = cls.static['stat_dispatch']

    def test_exact_source_hashes(self):
        for source in json.loads((HERE/'source_manifest.json').read_text(encoding='utf-8'))['sources']:
            self.assertEqual(hashlib.sha256((HERE/source['local_path']).read_bytes()).hexdigest(), source['sha256'])

    def test_historical_fixture_recomputation(self):
        self.assertEqual(build(), self.fixtures)
        self.assertEqual([r['native_stat83_low7'] for r in self.fixtures['player_stats']],
                         [16, 58, 57, 79, 81, 16, 57, 64, 74, 70, 44, 2])

    def test_gp_neighbor_bits_not_games(self):
        for gp in (0, 1, 16, 82, 127):
            for flags in (0, 1, 0xffff, 0x1ffffff):
                raw = bytearray(48)
                struct.pack_into('<I', raw, 8, gp | (flags << 7))
                self.assertEqual(stat_value(raw, 83, self.dispatch), gp)
        self.assertEqual(self.dispatch['by_stat_id']['83'], '0xeece01')
        self.assertEqual(self.dispatch['by_stat_id']['84'], '0xeece5c')

    def test_all_simple_cases_against_load_width(self):
        for target, expr in self.dispatch['simple_cases'].items():
            ids = [int(i) for i, t in self.dispatch['by_stat_id'].items() if t == target]
            for raw in [bytes(48), bytes([255])*48, bytes(range(48))]:
                v = int.from_bytes(raw[expr['offset']:expr['offset']+expr['load_bits']//8], 'little', signed=expr['signed'])
                want = v if expr['signed'] else (v >> expr['shift']) & expr['mask']
                for i in ids:
                    self.assertEqual(stat_value(raw, i, self.dispatch), want)
        with self.assertRaises(ValueError):
            stat_value(bytes(47), 83, self.dispatch)
        self.assertEqual(stat_value(bytes(48), 252, self.dispatch), 0)

    def test_history_zero_holes_negative_and_bound(self):
        self.assertEqual(history_index(0, 1), 0)
        for v in (0x8000, 0xfffe, 0xffff, 100):
            self.assertIsNone(history_index(v, 100))
        words = [0, 0xffff, 73]+[0xffff]*21
        out = decode_history_slice(struct.pack('<24H', *words), 100)
        self.assertEqual(out[:3], [0, None, 73])
        self.assertEqual(len(decode_history_slice(struct.pack('<25H', *(words+[99])), 100, 25)), 25)
        with self.assertRaises(ValueError):
            decode_history_slice(bytes(44), 100)

    def test_gm_team_and_chain_identity(self):
        rows = self.fixtures['gm_records']
        self.assertEqual([r['decoded']['owner_team_index'] for r in rows[:3]], [4, 4, 9])
        self.assertEqual(rows[1]['decoded']['next_record_index'], 0)
        self.assertEqual(rows[4]['decoded']['next_record_index'], 2)
        pools = self.fixtures['pools']
        def p(k):
            x = pools[k]
            return Pool(int(x['base'], 16), x['stride'], x['count'])
        dc, team = p('DeadCap'), p('Team')
        raw = {int(r['address'], 16): bytes.fromhex(r['prefix16_hex']) for r in rows[:3]}
        self.assertEqual(walk_fixture(dc.base+136, raw, dc, team, 4), [1, 0])
        with self.assertRaises(ValueError):
            linked_prefix(struct.pack('<QQ', team.base, dc.base), dc, team)
        with self.assertRaises(ValueError):
            linked_prefix(struct.pack('<QQ', dc.base+1, team.base), dc, team)
        with self.assertRaises(ValueError):
            linked_prefix(struct.pack('<QQ', 0, team.base+1), dc, team)

    def test_chain_cycles_cross_owner_missing(self):
        records, teams = Pool(0x1000, 136, 3), Pool(0x8000, 4696, 2)
        for nodes in [
            {0x1000: struct.pack('<QQ', 0x1000, 0x8000)},
            {0x1000: struct.pack('<QQ', 0x1088, 0x8000)},
            {0x1000: struct.pack('<QQ', 0, 0x8000+4696)},
        ]:
            with self.assertRaises(ValueError):
                walk_fixture(0x1000, nodes, records, teams, 0)

    def test_signed_round_all_bit_patterns_native_fixed_width(self):
        for low in range(256):
            for high in (0, 0xffffff00):
                meta = high | low
                shifted = (meta << 24) & 0xffffffff
                signed = shifted-(1 << 32) if shifted & 0x80000000 else shifted
                self.assertEqual(signed_round(meta), signed >> 27)
        for bits, want in [(15, 15), (16, -16), (31, -1)]:
            self.assertEqual(signed_round(bits << 3), want)
        self.assertEqual([r['decoded']['signed_round'] for r in self.fixtures['draft_records']], [0]*6)

    def test_draft_not_a_traded_asset_classifier(self):
        row = self.fixtures['draft_records'][1]
        self.assertTrue(row['decoded']['references_differ'])
        self.assertEqual(row['decoded']['legal_traded_asset'], 'UNKNOWN')
        self.assertEqual(row['decoded']['protection_or_swap'], 'UNKNOWN')

    def test_name_boundaries_multilingual_surrogate_and_missing(self):
        def field(text):
            return text.encode('utf-16le').ljust(40, b'\0')
        for last, first in [('Simmons', 'Ben'), ('Curry', 'Stephen'), ('高', '明'), ('𠀋', 'A')]:
            out = player_names(field(last)+field(first))
            self.assertEqual((out['surname'], out['given_name']), (last, first))
        out = player_names(field('X'*20)+field('Y'*20))
        self.assertEqual(out['given_name'], 'Y'*20)
        for row in self.fixtures['player_names']:
            with self.assertRaises(ValueError):
                player_names(bytes.fromhex(row['prefix16_hex']))
        with self.assertRaises(ValueError):
            player_names(bytes(64))
        with self.assertRaises(UnicodeDecodeError):
            player_names(b'\x00\xd8'+bytes(78))

    def test_record_type_does_not_encode_stat_or_global_identity(self):
        rows = self.fixtures['record_book']
        self.assertEqual({r['native_type_filter'] for r in rows}, {4})
        self.assertTrue(any(r['value'] == 36.0 for r in rows))
        self.assertTrue(all(r['full_stat_category'] == r['token_namespace'] == 'UNKNOWN' for r in rows))


class PolicyNegatives(unittest.TestCase):
    def setUp(self):
        self.path = HERE/'mock_policy.json'
        self.pin = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.policy = Policy.load(self.path, self.pin)
        self.backend = MockBackend(self.policy.binding, {0x1000: bytes(8), 0x2000: bytes(48), 0x3000: bytes(16)})
        self.reader = Reader(self.policy, self.backend)

    def read(self, **kw):
        args = dict(key='stat', phase='STATS', address=0x2000, size=48, binding=self.policy.binding)
        args.update(kw)
        return self.reader.read(**args)

    def assert_denied_without_backend(self, **kw):
        before = len(self.backend.calls)
        with self.assertRaises(Denied):
            self.read(**kw)
        self.assertEqual(len(self.backend.calls), before)

    def test_exact_success_audited(self):
        self.assertEqual(len(self.read()), 48)
        self.assertEqual(self.reader.used['STATS'], 48)
        self.assertEqual(self.reader.audit[-1]['status'], 'MOCK_SUCCESS')

    def test_cannot_self_register_or_mutate_policy(self):
        with self.assertRaises(AttributeError):
            self.reader.register_allowed_range('STATS', 0x9999, 48, 'arbitrary')
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.policy.permits[0].address = 0x9999
        with self.assertRaises(TypeError):
            self.reader.permits['extra'] = self.policy.permits[0]
        self.assert_denied_without_backend(key='arbitrary', address=0x9999)

    def test_changed_range_length_or_unknown_phase(self):
        for kw in [dict(address=0x2001), dict(size=49), dict(size=1), dict(phase='OTHER')]:
            self.assert_denied_without_backend(**kw)

    def test_wrong_pid_creation_build_module_and_context(self):
        for kw in [dict(pid=102), dict(creation_token='REUSED_PID'), dict(image_sha256='0'*64),
                   dict(module_base=0x150000000), dict(context='NEW_SAVE')]:
            self.assert_denied_without_backend(binding=dataclasses.replace(self.policy.binding, **kw))
        self.backend.binding = dataclasses.replace(self.policy.binding, pid=102)
        self.assert_denied_without_backend()

    def test_phase_no_transfer_or_repeated_request(self):
        self.read()
        self.assert_denied_without_backend()  # calls2 allowed but phase budget consumed
        self.assertEqual(self.reader.used['BIND'], 0)
        self.assert_denied_without_backend(phase='BIND')
        self.assertEqual(self.reader.used['STATS'], 48)

    def test_sensitive_denial_overrides_explicit_permit(self):
        self.assert_denied_without_backend(key='forbidden_overlap', phase='SENSITIVE_TEST', address=0x3000, size=16)

    def test_implicit_helper_read_no_permit(self):
        def helper():
            return self.reader.read('hidden_count', 'STATS', 0x1ff8, 8, self.policy.binding)
        with self.assertRaises(Denied):
            helper()
        self.assertEqual(self.backend.calls, [])

    def test_failed_short_read_charged_and_stopped(self):
        self.backend.fixtures = {0x2000: bytes(4)}
        with self.assertRaises(Denied):
            self.read()
        self.assertEqual(self.reader.used['STATS'], 48)
        self.assertEqual(len(self.backend.calls), 1)
        self.assert_denied_without_backend()

    def test_wrong_external_pin_and_live_adapter_denied(self):
        with self.assertRaises(Denied):
            Policy.load(self.path, '0'*64)
        with self.assertRaises(Denied):
            Reader(self.policy, object())


if __name__ == '__main__':
    unittest.main()
