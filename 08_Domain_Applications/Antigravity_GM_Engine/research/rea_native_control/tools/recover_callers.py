"""Bounded direct caller recovery from the pinned PE; no process access.

Raw opcode candidates are confirmed at decoded instruction boundaries from their
unwind fragment entry. Register arguments still need dataflow/caller analysis.
"""
import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'rea_native_action'))
from pe_local import Image


def recover(image, target, limit=24):
    text = image.read(image.text['rva'], image.text['size'])
    rows, count, truncated = [], 0, False
    for offset, opcode in enumerate(text[:-4]):
        if opcode not in (0xe8, 0xe9):
            continue
        site = image.text['rva'] + offset
        if site + 5 + struct.unpack_from('<i', text, offset + 1)[0] != target:
            continue
        chain = image.unwind_chain(site)
        if not chain:
            continue
        fragment = chain[0]
        if fragment['end'] - fragment['begin'] > 24576:
            continue
        decoded = image.instruction_rows(fragment['begin'], fragment['end'])
        indexes = [i for i, instruction in enumerate(decoded)
                   if instruction['rva'] == site and instruction['mnemonic'] in {'call', 'jmp'}]
        if not indexes:
            continue
        count += 1
        if len(rows) >= limit:
            truncated = True
            break
        index = indexes[0]
        # Predecessor window is explicitly partial, not a complete ABI proof.
        rows.append({'callsite_rva': site, 'primary_rva': chain[-1]['begin'],
                     'unwind_chain': chain, 'instruction_boundary_confirmed': True,
                     'window': decoded[max(0, index - 28):index + 13],
                     'window_is_complete_caller': False})
    return {'game_build_sha256': image.sha256, 'target_rva': target,
            'source_kind': 'STATIC_PINNED_PE_CAPSTONE_NOT_REA_PROVIDER',
            'game_access_performed': False, 'target_execution_performed': False,
            'caller_limit': limit, 'confirmed_candidates_examined': count,
            'truncated': truncated, 'direct_call_or_tailjump_refs': rows,
            'limitations': ['Indirect callers are not enumerated',
                           'Unwind fragments and linear decode do not prove all control-flow paths',
                           'Argument meanings, lifecycle and live effects are not inferred from names']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True, type=lambda x: int(x, 0))
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise SystemExit('Refusing to overwrite an existing evidence file')
    result = recover(Image(), args.target)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in {'direct_call_or_tailjump_refs', 'limitations'}}))
    print(json.dumps([{'site': hex(r['callsite_rva']), 'primary': hex(r['primary_rva'])}
                      for r in result['direct_call_or_tailjump_refs']]))
