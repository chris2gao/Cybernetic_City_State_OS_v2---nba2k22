"""Recompute only from pinned historical files and captured disk instructions."""
import hashlib
import json
from pathlib import Path
import struct

from decoders import Pool, draft, linked_prefix, record_metadata, stat_value

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE/name).read_text(encoding='utf-8'))


def build():
    data = load('sources/gemini/ingredient_discovery_results.json')
    audit = load('sources/gemini/read_audit_log.json')
    static = load('static_capture.json')
    phase = data['phases']
    descriptors = phase['R01-BIND']['descriptors']
    def pool(slot, stride):
        d = next(d for d in descriptors if d['slot'] == slot)
        return Pool(int(d['pData'], 16), stride, d['count'])
    teams, dc, tpe = pool(8, 4696), pool(61, 136), pool(71, 112)
    def audit_entry(address, size):
        matches = [a for a in audit if int(a['address_hex'], 16) == int(address, 16) and a['requested_size'] == size]
        assert len(matches) == 1
        return matches[0]
    stats = []
    for row in phase['R02-PLAYER-HISTORY']['slot24_career_stats_rows']:
        raw = bytes.fromhex(row['raw_hex'])
        a = audit_entry(row['address'], 48)
        assert hashlib.sha256(raw).hexdigest() == a['sha256']
        stats.append(dict(address=row['address'], index=row['stat_row_index'], player_index=row['player_index'],
                          raw_hex=raw.hex(), audit_call=a['call_index'], sha256=a['sha256'],
                          prior_wrong_u16=row['games_played_word'], native_stat83_low7=stat_value(raw, 83, static['stat_dispatch']),
                          native_stat84=stat_value(raw, 84, static['stat_dispatch']),
                          adjacent_bit7=(raw[8] >> 7) & 1,
                          adjacent_bits8_14=(int.from_bytes(raw[8:12], 'little') >> 8) & 127,
                          season_code_raw=row['season_code_hex'], season_identity='UNKNOWN_UI_SAVE_UNBOUND'))
    drafts = []
    for row in phase['R03-DRAFT-RELATIONS']['draft_records']:
        raw = struct.pack('<QQQII', int(row['owner_team_ptr'], 16), int(row['original_team_ptr'], 16),
                          int(row['player_reference_ptr'], 16), int(row['token_hex'], 16), int(row['metadata_hex'], 16))
        a = audit_entry(row['address'], 32)
        assert hashlib.sha256(raw).hexdigest() == a['sha256']
        drafts.append(dict(index=row['index'], raw_hex=raw.hex(), source_form='RECONSTRUCTED_FIELDS_HASH_MATCH_FULL_AUDIT',
                           audit_call=a['call_index'], sha256=a['sha256'], prior_wrong_signed_round=row['signed_round'],
                           decoded=draft(raw, teams)))
    gm = []
    cap = phase['R05-GM-CAP']
    for kind, rows, records in [('DeadCap', cap['dead_cap_records'], dc), ('TradeException', cap['trade_exception_records'], tpe)]:
        for row in rows:
            # Misnamed historical fields are preserved in sources; only prefix16 is independently retained in audit.
            raw = (struct.pack('<QQ', int(row['team_ptr'], 16), int(row['player_ptr'], 16)) if kind == 'DeadCap'
                   else bytes.fromhex(row['raw_hex'])[:16])
            a = audit_entry(row['address'], records.stride)
            assert raw.hex() == a['safe_preview_hex']
            gm.append(dict(kind=kind, index=row['index'], address=row['address'], prefix16_hex=raw.hex(),
                           audit_call=a['call_index'], source_form='EXACT_AUDIT_PREVIEW16_NOT_FULL_RECORD',
                           decoded=linked_prefix(raw, records, teams)))
    names = []
    for row in phase['R02-PLAYER-HISTORY']['players']:
        a = audit_entry(row['address'], 64)
        raw = bytes.fromhex(a['safe_preview_hex'])
        names.append(dict(player_index=row['player_index'], prefix16_hex=raw.hex(),
                          retained_surname_prefix=raw.decode('utf-16le').split('\0')[0],
                          prior_truncated_name=row['name'], given_name='SOURCE_MISSING', full_name_pair='SOURCE_MISSING',
                          audit_call=a['call_index'], acquired_bytes=64, retained_preview_bytes=len(raw),
                          native_pair_required_bytes=80, missing_indices='R01 retained 22 filtered indices; native ordinary capacity24, special25',
                          full_identity='UNKNOWN'))
    records = [dict(index=r['index'], holder=r['record_holder'], value=r['record_value'],
                    **record_metadata(int(r['packed_dword_hex'], 16), r['historical_player_id'], r['team_id']))
               for r in phase['R06-RECORD-BOOK']['record_book_entries']]
    phases = {k: sum(a['requested_size'] for a in audit if a['phase'] == k) for k in phase}
    assert len(audit) == 52 and sum(phases.values()) == 5172
    return dict(schema='r02.fixture.v1', source_commit='5cef84fb21892266686bd5fd75a06901ea911d12',
                provenance='Historical Gemini acquisition only, PID1828 reported not independently file-bound; SAVE_UNBOUND',
                pools={k: dict(base=hex(p.base), stride=p.stride, count=p.count) for k, p in [('Team', teams), ('DeadCap', dc), ('TradeException', tpe)]},
                historical_explicit_audit=dict(calls=len(audit), bytes=sum(phases.values()), by_phase=phases,
                                               limitation='Self-registered ranges; no proof of implicit reads or effective external authorization'),
                player_stats=stats, draft_records=drafts, gm_records=gm, player_names=names, record_book=records)


if __name__ == '__main__':
    result = build()
    (HERE/'decoded_fixtures.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('fixture evidence:', len(result['player_stats']), 'stats;', len(result['draft_records']), 'draft;', len(result['gm_records']), 'GM prefixes')
