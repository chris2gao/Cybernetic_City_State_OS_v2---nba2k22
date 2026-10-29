"""Recover raw Badge bit fields, per-ID limits and selected coupling tables offline.

This is selected dispatch reconstruction from the pinned PE, not execution or a
complete safe-edit contract. Effective Badge getters additionally use modifiers.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RCX, X86_REG_RIP


def recover(image):
    getter_table = struct.unpack('<99I', image.read(0x97c700, 99 * 4))
    setter_table = struct.unpack('<99I', image.read(0x994e70, 99 * 4))
    maximum_remap = image.read(0x1950124, 99)
    maximum_targets = struct.unpack('<2I', image.read(0x195011c, 8))
    modifier_table = struct.unpack('<99I', image.read(0x969f1c, 99 * 4))
    name_pointers = struct.unpack('<99Q', image.read(0x24c6970, 99 * 8))
    maxima = {}
    for target in set(maximum_targets):
        instructions = image.instructions(target, target + 3)
        if len(instructions) != 2 or instructions[0].mnemonic != 'mov' or instructions[1].mnemonic != 'ret':
            raise ValueError('Unqualified badge maximum branch')
        maxima[target] = instructions[0].operands[1].imm
    fields = []
    for index, start in enumerate(getter_table):
        address, offset, shift, mask = start, None, 0, None
        path = []
        for _ in range(24):
            if address == 0x97c6e1:
                break
            if not 0x97c0e6 <= address < 0x97c6e1:
                raise ValueError('Getter dispatch escaped selected field path')
            ins = image.instructions(address, address + 15)[0]
            path.append({'rva': address, 'mnemonic': ins.mnemonic, 'operands': ins.op_str})
            operands = ins.operands
            if ins.mnemonic == 'movzx' and operands[1].type == X86_OP_MEM:
                if operands[1].mem.base != X86_REG_RCX or operands[1].size != 1:
                    raise ValueError('Unexpected raw Badge object load')
                offset = operands[1].mem.disp
            elif ins.mnemonic == 'shr':
                shift += operands[1].imm
            elif ins.mnemonic == 'and':
                mask = operands[1].imm if operands[1].type == X86_OP_IMM else 1
            elif ins.mnemonic not in {'mov', 'jmp'}:
                raise ValueError('Unknown instruction in raw Badge field path')
            address = operands[0].imm - image.base if ins.mnemonic == 'jmp' else address + ins.size
        else:
            raise ValueError('Selected field path exceeded instruction budget')
        if mask is None and shift:
            mask = (1 << (8 - shift)) - 1
        if offset is None or mask not in {1, 7} or not 0x4bb <= offset <= 0x4e2:
            raise ValueError('Incomplete raw Badge bit field ' + repr((index, offset, shift, mask, path)))
        remap = maximum_remap[index]
        if remap >= len(maximum_targets):
            raise ValueError('Unexpected maximum dispatch remap')
        maximum = maxima[maximum_targets[remap]]
        if maximum not in {1, 4} or (mask == 1) != (maximum == 1):
            raise ValueError('Raw bit field and maximum class disagree')
        setter_start = setter_table[index]
        starts = sorted(set(setter_table) | {0x994df6})
        setter_end = next(value for value in starts if value > setter_start)
        if not 0x993118 <= setter_start < setter_end <= 0x994df6:
            raise ValueError('Setter dispatch outside selected switch')
        setter_instructions = image.instructions(setter_start, setter_end)
        clears = [ins.operands[1].imm & 0xff for ins in setter_instructions
                  if ins.mnemonic == 'and' and ins.operands[0].type == X86_OP_MEM
                  and ins.operands[0].mem.disp == offset and ins.operands[0].size == 1]
        expected_clear = (~(mask << shift)) & 0xff
        if clears != [expected_clear]:
            raise ValueError('Raw getter and setter preservation mask disagree for Badge ' + str(index))
        name_rva = name_pointers[index] - image.base
        name_text = image.read(name_rva, 256).decode('utf-16-le')
        if '\0' not in name_text:
            raise ValueError('Internal badge name exceeds selected UTF16 string bound')
        name = name_text.split('\0', 1)[0]
        if not name or len(name) > 100 or not name.isascii():
            raise ValueError('Unqualified internal badge name')
        modifier_start = modifier_table[index]
        modifier_instructions = []
        for instruction in image.instructions(modifier_start, modifier_start + 32):
            modifier_instructions.append(instruction)
            if instruction.mnemonic == 'ret':
                break
        if not modifier_instructions or modifier_instructions[-1].mnemonic != 'ret':
            raise ValueError('Unclosed selected modifier field leaf')
        load = modifier_instructions[0]
        if load.mnemonic != 'mov' or load.operands[1].type != X86_OP_MEM or load.operands[1].mem.base != X86_REG_RCX:
            raise ValueError('Unexpected signed Badge modifier field load')
        left = next((instruction.operands[1].imm for instruction in modifier_instructions if instruction.mnemonic == 'shl'), 0)
        right = next((instruction.operands[1].imm for instruction in modifier_instructions if instruction.mnemonic == 'sar'), None)
        if right not in {28, 30} or any(instruction.mnemonic not in {'mov', 'shl', 'sar', 'ret'} for instruction in modifier_instructions):
            raise ValueError('Unqualified signed Badge modifier encoding')
        fields.append({'badge_id': index, 'internal_name': name, 'internal_name_rva': name_rva,
                       'ui_label_verified': False, 'sentinel_name': name == 'NONE', 'byte_offset': offset,
                       'shift': shift, 'mask': mask, 'minimum': 0, 'maximum': maximum,
                       'getter_case_rva': start, 'getter_path': path,
                       'setter_case_rva': setter_start, 'setter_clear_mask': clears[0],
                       'signed_modifier_field': {'getter_case_rva': modifier_start,
                           'dword_offset': load.operands[1].mem.disp, 'shift_left': left,
                           'arithmetic_shift_right': right, 'signed_width': 32-right,
                           'instructions': image.instruction_rows(modifier_start, modifier_instructions[-1].address + modifier_instructions[-1].size-image.base)}})
    occupied = set()
    for field in fields:
        bits = {(field['byte_offset'], bit) for bit in range(8) if (field['mask'] << field['shift']) & (1 << bit)}
        if occupied & bits:
            raise ValueError('Distinct raw Badge fields overlap')
        occupied |= bits
    groups = []
    for source in (0x992dc5, 0x992e62, 0x992ed5, 0x992f48):
        instruction = image.instructions(source, source + 15)[0]
        operand = instruction.operands[1]
        if instruction.mnemonic != 'lea' or operand.type != X86_OP_MEM or operand.mem.base != X86_REG_RIP:
            raise ValueError('Expected exact selected coupling-array reference')
        target = instruction.address + instruction.size + operand.mem.disp - image.base
        ids = list(struct.unpack('<3I', image.read(target, 12)))
        if any(value > 98 for value in ids):
            raise ValueError('Coupling array contains unknown ID class')
        groups.append({'reference_rva': source, 'table_rva': target, 'badge_ids': ids,
                       'effect': 'Normal positive-level request selects one group member at native maximum and clears other nonzero members; zero entries are skipped'})
    code_ranges = [(0x97c0c0, 0x97c700), (0x19500f0, 0x195011c), (0x969b30, 0x969f1c)]
    return {'source_kind': 'PINNED_PE_SELECTED_BADGE_DISPATCH_NOT_REA_PROVIDER',
            'game_build_sha256': image.sha256, 'game_access': False,
            'raw_getter': {'entry_rva': 0x97c0c0, 'arguments': ['PLAYER*', 'badge_id:int', 'normalize_boolean:int'],
                           'raw_flag': 0, 'normalization': 'With flag nonzero, positive one-bit badges return3 rather than raw1'},
            'effective_getter': {'entry_rva': 0x97b870,
                'extra_state': 'Walks PLAYER+0xd8 linked modifiers gated by PLAYER+0x354 low3 bits; calls0x969b30 and adds/clamps signed adjustments',
                'coupling_uses_this_getter': True,
                'modifier_encoding': 'Recovered per-ID signed2/4-bit deltas; modifier provenance/lifetime and complete list invariants remain unqualified',
                'gating': 'Raw packed bytes alone are insufficient to predict effective-level coupling guards'},
            'fields': fields, 'coupling_groups': groups,
            'coupling_dispatch_5_through_25': list(image.read(0x994e58, 21)),
            'coupling_case_targets': list(struct.unpack('<6I', image.read(0x994e40, 24))),
            'getter_and_maximum_code': [{'range_rva': [lo, hi],
                'sha256': hashlib.sha256(image.read(lo, hi-lo)).hexdigest(),
                'instructions': image.instruction_rows(lo, hi)} for lo, hi in code_ranges],
            'limits': ['Internal enum names are recovered from the original assertion name table, not independently verified UI labels or role permissions',
                       'Badge0 has internal sentinel name NONE; its technical bit must not be presented as a normal editable Badge',
                       'Coupling arrays are partial logic; effective-level modifiers and trait-helper assertions need qualification',
                       'Normal original UI setter flag0 must be preserved; recursive flag1 is not an approved bypass',
                       'No callable runtime, game execution, UI or persistence acceptance follows from this evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise SystemExit('Existing evidence is immutable; select a new output')
    result = recover(Image())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'raw_badge_fields': len(result['fields']),
        'maximum1': sum(field['maximum']==1 for field in result['fields']),
        'maximum4': sum(field['maximum']==4 for field in result['fields']),
        'native_internal_names': sum(bool(field['internal_name']) for field in result['fields']),
        'coupling_groups': [group['badge_ids'] for group in result['coupling_groups']],
        'game_access': False, 'callable_promoted': False}))
