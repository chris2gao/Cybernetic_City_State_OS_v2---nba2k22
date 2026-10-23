"""Offline research decoders. No process backend, production DTO or identity join."""
from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class Pool:
    base: int
    stride: int
    count: int

    def index(self, pointer):
        if type(pointer) is not int or pointer <= 0 or self.stride <= 0 or self.count <= 0:
            return None
        delta = pointer-self.base
        return delta//self.stride if 0 <= delta < self.stride*self.count and delta % self.stride == 0 else None


def linked_prefix(raw, records, teams):
    if len(raw) < 16:
        raise ValueError('Need both complete pointer words')
    nxt, owner = struct.unpack_from('<QQ', raw)
    next_index, team_index = records.index(nxt), teams.index(owner)
    if nxt and next_index is None:
        raise ValueError('Next pointer is not an aligned record in the same pool')
    if team_index is None:
        raise ValueError('Owner is not an aligned Team; never reinterpret as Player')
    return dict(next_pointer=hex(nxt), next_record_index=next_index,
                owner_team_pointer=hex(owner), owner_team_index=team_index,
                active_state='UNKNOWN_NOT_CAPTURED', entity_player_id='UNKNOWN')


def walk_fixture(head, raw_by_pointer, records, teams, team_index):
    """Closed fixture traversal only. Missing node is unknown, never a live read."""
    seen, indices = set(), []
    while head:
        if head in seen:
            raise ValueError('Cycle')
        if len(seen) >= records.count or head not in raw_by_pointer:
            raise ValueError('Missing fixture node or bound exceeded')
        index = records.index(head)
        if index is None:
            raise ValueError('Unaligned node')
        seen.add(head)
        row = linked_prefix(raw_by_pointer[head], records, teams)
        if row['owner_team_index'] != team_index:
            raise ValueError('Cross-Team chain')
        indices.append(index)
        head = int(row['next_pointer'], 16)
    return indices


def stat_value(raw, stat_id, dispatch):
    if len(raw) != 48:
        raise ValueError('Slot24 record must be exactly 48 bytes')
    target = dispatch['by_stat_id'].get(str(stat_id))
    if target is None or target == dispatch['default']:
        return 0  # native default for unsupported enum, not missing-data imputation
    expr = dispatch['simple_cases'].get(target)
    if expr is None:
        raise ValueError('Compound native case requires a separate decoder')
    value = int.from_bytes(raw[expr['offset']:expr['offset']+expr['load_bits']//8], 'little', signed=expr['signed'])
    # Preserve signed movsx cases; the extracted mask describes the load width.
    if expr['signed'] and not expr['shift'] and expr['mask'] == (1 << expr['load_bits'])-1:
        return value
    return (value >> expr['shift']) & expr['mask']


def history_index(word, count):
    if type(word) is not int or type(count) is not int or not 0 <= word <= 0xffff or count < 0:
        raise ValueError('Bad index input')
    return word if word < 0x8000 and word < count else None


def decode_history_slice(raw, count, entries=24):
    if entries not in (24, 25) or len(raw) != entries*2:
        raise ValueError('Require complete 24-index slice or 25 including special entry')
    return [history_index(word, count) for word in struct.unpack('<'+'H'*entries, raw)]


def utf16_field(raw):
    if len(raw) != 40:
        raise ValueError('Native name field is 20 UTF16 code units')
    end = next((i for i in range(0, 40, 2) if raw[i:i+2] == b'\0\0'), 40)
    return raw[:end].decode('utf-16le', errors='strict')


def player_names(raw):
    if len(raw) != 80:
        raise ValueError('Full name pair not retained; refuse fabricated given name')
    return dict(surname=utf16_field(raw[:40]), given_name=utf16_field(raw[40:80]),
                identity_binding='UNKNOWN_WITHOUT_UI_AND_SAVE')


def signed_round(meta):
    if type(meta) is not int or not 0 <= meta <= 0xffffffff:
        raise ValueError('uint32 metadata required')
    bits = (meta >> 3) & 31
    return bits-32 if bits & 16 else bits


def draft(raw, teams):
    if len(raw) != 32:
        raise ValueError('Need all 32 DraftData bytes')
    pick_team, original_team, player_ref, token, meta = struct.unpack('<QQQII', raw)
    pick_index, original_index = teams.index(pick_team), teams.index(original_team)
    if pick_index is None or original_index is None:
        raise ValueError('Invalid Team relation')
    return dict(pick_team_index=pick_index, original_team_index=original_index,
                references_differ=pick_team != original_team, signed_round=signed_round(meta),
                group=meta & 7, pick_sequence=(meta >> 8) & 255,
                bit17_raw=(meta >> 17) & 1, token_raw=hex(token),
                player_reference_raw=hex(player_ref), metadata_raw=hex(meta),
                legal_traded_asset='UNKNOWN', protection_or_swap='UNKNOWN')


def record_metadata(packed, token, team):
    return dict(native_type_filter=(packed >> 21) & 7, full_stat_category='UNKNOWN',
                raw_tail_token=token, token_namespace='UNKNOWN', raw_team_word=team,
                current_save_player_id='UNKNOWN')
