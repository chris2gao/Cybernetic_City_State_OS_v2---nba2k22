"""Selected displacement writers, with decoded boundaries and explicit budgets.

A matching offset does not identify an object type or qualify a Native action.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_MEM, X86_REG_RSP, X86_REG_RBP, X86_REG_RIP


def recover(image, offsets):
    if not 1 <= len(offsets) <= 8 or any(not 0 <= value <= 65535 for value in offsets):
        raise ValueError('Select1..8 bounded field offsets')
    code = image.read(image.text['rva'], image.text['size'])
    candidates, cache, literal_counts = {}, {}, {}
    decoded_bytes, skipped_large = 0, 0
    for displacement in offsets:
        sites = [image.text['rva'] + match.start()
                 for match in re.finditer(re.escape(struct.pack('<I', displacement)), code)]
        literal_counts[str(displacement)] = len(sites)
        for site in sites:
            extent = image.function_range(site)
            if extent:
                start, end = extent
                if end-start > 65536:
                    skipped_large += 1
                    continue
            else:
                if site < image.text['rva'] + 96:
                    continue
                pads = list(re.finditer(rb'\xcc{2,}', image.read(site-96, 96)))
                if not pads:
                    continue
                start, end = site-96+pads[-1].end(), site+96
            if start not in cache:
                if decoded_bytes + end-start > 16*1024*1024:
                    raise ValueError('Selected decode budget16MiB reached; refine offsets')
                cache[start] = image.instructions(start, end)
                decoded_bytes += end-start
            for index, instruction in enumerate(cache[start]):
                if not instruction.address-image.base <= site < instruction.address-image.base+instruction.size:
                    continue
                if not instruction.operands or instruction.operands[0].type != X86_OP_MEM:
                    continue
                memory = instruction.operands[0].mem
                if memory.disp != displacement or memory.base in (X86_REG_RSP, X86_REG_RBP, X86_REG_RIP):
                    continue
                if instruction.mnemonic not in {'mov', 'and', 'or', 'xor', 'bts', 'btr', 'btc'}:
                    continue
                chain = image.unwind_chain(site)
                entry = chain[-1]['begin'] if chain else start
                sequence = cache[start][max(0, index-4):index+5]
                candidates[(entry, instruction.address-image.base)] = {
                    'entry_candidate_rva': entry, 'fragment_rva': start,
                    'fragment_bytes': end-start, 'has_unwind': bool(chain),
                    'field_instruction_rva': instruction.address-image.base,
                    'window': [{'rva': row.address-image.base, 'mnemonic': row.mnemonic,
                                'operands': row.op_str} for row in sequence]}
    return {'source_kind': 'PINNED_PE_DECODED_FIELD_WRITER_CANDIDATES_NOT_REA_PROVIDER',
            'game_build_sha256': image.sha256, 'game_access': False,
            'selected_offsets': offsets, 'literal_counts': literal_counts,
            'decoded_bytes': decoded_bytes, 'skipped_large_fragments': skipped_large,
            'candidates': list(candidates.values()),
            'limitations': ['An offset match does not prove object identity, ABI or a safe business operation',
                           'No-unwind padding starts are candidates, not complete branched control flow',
                           'Only selected32-bit displacement encodings and stated decode bounds were examined']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offset', nargs='+', type=lambda value: int(value, 0), required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise SystemExit('Existing evidence is immutable; select a new output')
    result = recover(Image(), args.offset)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'writer_instructions': len(result['candidates']),
                      'candidate_entries': len({row['entry_candidate_rva'] for row in result['candidates']}),
                      'decoded_bytes': result['decoded_bytes'], 'game_access': False}))
