"""Disk PE extraction/replay. Never opens a process or loads the game binary.

Run with --image <authorized disk image> --output <json>, or --replay <json>.
RVA spans are deliberate bounded basic blocks; .pdata may split a function.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
EXPECTED = '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
SPANS = {
    'deadcap_insert': (0x9cba60, 32),
    'tpe_insert': (0x9cbc90, 36),
    'deadcap_remove': (0x9d1570, 109),
    'tpe_remove': (0x9d15e0, 109),
    'deadcap_clear': (0x9d1440, 299),
    'deadcap_allocate': (0x9214f0, 98),
    'deadcap_release': (0x921560, 216),
    'tpe_allocate': (0x9d6460, 98),
    'tpe_release': (0x9d64d0, 147),
    'tpe_delete_named_consumer': (0x12cc6e0, 178),
    'deadcap_attach_caller': (0x12cc990, 107),
    # Known instruction boundary from complete .pdata fragment disassembly.
    'tpe_player_names_caller': (0x12e9d13, 58),
    'utf16_copy_prefix': (0xfbc080, 160),
    'stats_dispatch_and_cases': (0xeecdd0, 776),
    'player_stat_index': (0xf22220, 71),
    'player_stat_selector': (0xf22270, 179),
    'player_24_index_consumer': (0xf22380, 154),
    'player_25_index_consumer': (0xf22420, 270),
    'draft_original_team': (0x92a210, 390),
    'draft_pick_team': (0x92a3a0, 373),
    'record_type_filter': (0xf32e44, 40),
    'record_team_index': (0xf34c60, 100),
}


def parser():
    spec = importlib.util.spec_from_file_location('r02_prior_pe', HERE/'sources/prior_static_extract.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PE


def extract(image):
    pe = parser()(image)
    if pe.meta['sha256'] != EXPECTED:
        raise ValueError('Disk image build mismatch')
    spans = {name: pe.segment(*pair) for name, pair in SPANS.items()}
    resources = []
    for name, (start, size) in SPANS.items():
        for ins in pe.instructions(start, size):
            for op in ins.operands:
                if op.type != 3 or ins.reg_name(op.mem.base) != 'rip':
                    continue
                target = ins.address+ins.size+op.mem.disp-pe.base
                try:
                    value = pe.ascii(target)
                except ValueError:
                    continue
                if value and any(t in value for t in ['DraftData_', 'TradeException', '.vcc', 'FEATURES_']):
                    resources.append(dict(span=name, rva=hex(target), value=value,
                                          hex=(value.encode('ascii')+b'\0').hex()))
    table = pe.bytes(0xeed0d8, 188)
    mapping = pe.bytes(0xeed194, 251)
    targets = struct.unpack('<47I', table)
    stat_map = {str(i+1): hex(targets[x]) for i, x in enumerate(mapping)}
    # Derive plain load/shift/mask cases from instructions, not a GP plausibility bound.
    simple = {}
    for target in sorted(set(targets)):
        expr = None
        for ins in pe.instructions(target, 40):
            if ins.mnemonic == 'ret':
                break
            ops = ins.operands
            if ins.mnemonic in ('mov', 'movzx', 'movsx') and len(ops) == 2 and ops[1].type == 3:
                if ins.reg_name(ops[1].mem.base) != 'rcx':
                    break
                expr = dict(offset=ops[1].mem.disp, load_bits=ops[1].size*8,
                            signed=ins.mnemonic == 'movsx', shift=0,
                            mask=(1 << (ops[1].size*8))-1)
            elif ins.mnemonic in ('shr', 'and') and expr and ins.reg_name(ops[0].reg) == 'r8d' and ops[1].type == 2:
                if ins.mnemonic == 'shr':
                    expr['shift'] += ops[1].imm
                    expr['mask'] >>= ops[1].imm
                else:
                    expr['mask'] &= ops[1].imm
            elif ins.mnemonic == 'mov' and ins.op_str == 'eax, r8d':
                continue
            else:
                expr = None
                break
        if expr:
            simple[hex(target)] = expr
    return dict(schema='r02.static.v1', image=pe.meta, spans=spans, resources=resources,
                stat_dispatch={'enum_first': 1, 'enum_last': 251, 'default': '0xeed0d4',
                               'case_table_rva': '0xeed0d8', 'case_table_hex': table.hex(),
                               'index_table_rva': '0xeed194', 'index_table_hex': mapping.hex(),
                               'by_stat_id': stat_map, 'simple_cases': simple},
                limits=['Disk build only; no current process association',
                        'Spans are bounded blocks, not exhaustive control-flow coverage',
                        'Native enum numeric identities do not certify UI labels or season/save joins'])


def replay(evidence, image):
    current = extract(image)
    if current != evidence:
        raise AssertionError('Static extraction changed')
    return len(current['spans'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--image', required=True)
    p.add_argument('--output')
    p.add_argument('--replay')
    args = p.parse_args()
    if args.replay:
        print('replayed_spans', replay(json.loads(Path(args.replay).read_text(encoding='utf-8')), args.image))
    elif args.output:
        Path(args.output).write_text(json.dumps(extract(args.image), indent=2)+'\n', encoding='utf-8')
        print('static_capture_complete')
    else:
        p.error('--output or --replay required')
