"""Read a disk PE image only; preserve bounded x64/static-resource evidence.

No process enumeration, process handles, live memory access, injection or game
execution. Extracted names corroborate this image's object family, not a save.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, __version__ as CAPSTONE_VERSION


class PE:
    def __init__(self, path):
        self.raw = Path(path).read_bytes()
        if self.raw[:2] != b'MZ':
            raise ValueError('Not a DOS/PE image')
        h = struct.unpack_from('<I', self.raw, 0x3c)[0]
        if self.raw[h:h+4] != b'PE\0\0':
            raise ValueError('Not a PE image')
        machine, count, stamp, _, _, opt_size, _ = struct.unpack_from('<HHIIIHH', self.raw, h+4)
        if machine != 0x8664 or struct.unpack_from('<H', self.raw, h+24)[0] != 0x20b:
            raise ValueError('Expected AMD64 PE32+')
        self.base = struct.unpack_from('<Q', self.raw, h+48)[0]
        self.sections = []
        for index in range(count):
            off = h+24+opt_size+index*40
            name = self.raw[off:off+8].rstrip(b'\0').decode('ascii')
            virtual_size, rva, raw_size, file_offset = struct.unpack_from('<IIII', self.raw, off+8)
            self.sections.append(dict(name=name, rva=rva, virtual_size=virtual_size,
                                      raw_size=raw_size, file_offset=file_offset))
        self.cs = Cs(CS_ARCH_X86, CS_MODE_64)
        self.cs.detail = True
        self.meta = dict(sha256=hashlib.sha256(self.raw).hexdigest(), file_size=len(self.raw),
                         pe_timestamp=stamp, machine='AMD64', preferred_image_base=hex(self.base),
                         capstone_version=CAPSTONE_VERSION, acquisition='STATIC_DISK_FILE_ONLY')

    def bytes(self, rva, size):
        if type(rva) is not int or type(size) is not int or rva < 0 or size < 0:
            raise ValueError('Nonnegative integer RVA and size required')
        for section in self.sections:
            rel = rva-section['rva']
            if 0 <= rel and rel+size <= section['raw_size']:
                off = section['file_offset']+rel
                result = self.raw[off:off+size]
                if len(result) != size:
                    raise ValueError('Truncated section')
                return result
        raise ValueError(f'RVA range not backed by one file section: {rva:#x}+{size}')

    def functions(self):
        section = next(s for s in self.sections if s['name'] == '.pdata')
        raw = self.bytes(section['rva'], section['virtual_size'])
        return sorted((a, b) for a, b, _ in struct.iter_unpack('<III', raw) if b > a > 0)

    def instructions(self, start, size):
        return list(self.cs.disasm(self.bytes(start, size), self.base+start))

    def segment(self, start, size):
        raw = self.bytes(start, size)
        return dict(rva=hex(start), size=size, hex=raw.hex(), sha256=hashlib.sha256(raw).hexdigest(),
                    instructions=[dict(rva=hex(i.address-self.base), bytes=i.bytes.hex(),
                                       mnemonic=i.mnemonic, operands=i.op_str)
                                  for i in self.instructions(start, size)])

    def ascii(self, rva):
        raw = self.bytes(rva, 180).split(b'\0', 1)[0]
        try:
            value = raw.decode('ascii')
        except UnicodeDecodeError:
            return None
        return value if len(value) > 3 and value.isprintable() else None

def named_resources(pe,start,size):
    result=[]
    for ins in pe.instructions(start,size):
        for op in ins.operands:
            if op.type==3 and ins.reg_name(op.mem.base)=='rip':
                target=ins.address+ins.size+op.mem.disp-pe.base
                try:value=pe.ascii(target)
                except ValueError:continue
                if value and any(term in value for term in ['RecordData_','DraftData_','DRAFTDATA::','draftdata.','recorddata.']):
                    result.append(dict(instruction_rva=hex(ins.address-pe.base),string_rva=hex(target),value=value,
                                       null_terminated_hex=(value.encode('ascii')+b'\0').hex()))
    return result


def extract(image):
    pe = PE(image)
    getters = []
    for start, end in pe.functions():
        if not 0xf3a000 <= start < 0xf45000 or end-start > 5000:
            continue
        ins = pe.instructions(start, end-start)
        if not any(i.mnemonic == 'call' and i.op_str == hex(pe.base+0x11d5de0) for i in ins):
            continue
        slots, resources = set(), []
        for i in ins:
            for op in i.operands:
                if op.type != 3:
                    continue
                if i.reg_name(op.mem.base) == 'rax' and i.mnemonic == 'cmp' and 0 <= op.mem.disp < 1200 and op.mem.disp % 16 == 0:
                    slots.add(op.mem.disp//16)
                if i.reg_name(op.mem.base) == 'rip':
                    target = i.address+i.size+op.mem.disp-pe.base
                    try:
                        text = pe.ascii(target)
                    except ValueError:
                        continue
                    if text and text.startswith('ROSTERDATA::'):
                        resources.append(dict(instruction_rva=hex(i.address-pe.base), string_rva=hex(target),
                                              value=text, null_terminated_hex=(text.encode('ascii')+b'\0').hex()))
        # Multi-slot functions and unnamed helper fragments are retained separately,
        # never automatically promoted to a one-to-one slot/name relation.
        if len(slots) == 1 and len(set(r['value'] for r in resources)) == 1:
            getters.append(dict(slot=next(iter(slots)), code=pe.segment(start, end-start), resources=resources))
    extras = {name:pe.segment(start,size) for name,start,size in [
        ('manager_singleton',0x11d5de0,8), ('player_getter',0xf3f4a0,210),
        ('uniform_consumer',0x920e40,58), ('playbook_lookup',0xf3ed00,91),
        ('play_dispatch',0xf1d740,0x1e4), ('play_consumer',0xf26700,227),
        ('draft_by_team_index',0x92a3a0,373), ('draft_group_round_index',0x929c62,64),
        ('draft_link_token',0x947330,141), ('draft_clear_relation',0x929e00,15),
        ('draft_team_pointer_pair',0x61dbf5,50), ('original_team_leaf',0x23efd0,5),
        ('record_type_consumer',0xf32e44,40), ('record_team_index',0xf34c60,100),
    ]}
    original_anchor=9609964
    start,end=next((s,e) for s,e in pe.functions() if s<=original_anchor<e)
    extras['draft_original_team_lookup']=pe.segment(start,end-start)
    consumers=[]
    for start,size in [(0xf32b10,1288),(0xf33fc0,1432),(0xf34c60,272),(0x92a3a0,373),(0x942f91,208),(start,end-start)]:
        consumers.append(dict(code=pe.segment(start,size),resources=named_resources(pe,start,size)))
    table = pe.bytes(0xf1d924,68*4)
    cases=[]
    for index,(target,) in enumerate(struct.iter_unpack('<I',table)):
        segment=pe.segment(target,7)
        first=segment['instructions'][0]
        decoded=pe.instructions(target,7)[0]
        if decoded.mnemonic!='mov' or len(decoded.operands)!=2 or decoded.operands[1].type!=3:
            raise ValueError(f'Unrecognized play dispatch {index}')
        cases.append(dict(index=index,target_rva=hex(target),field_offset=decoded.operands[1].mem.disp,
                          operand=first['operands'],code=segment))
    return dict(schema='triage.static_evidence.v1', image=pe.meta,
                limitations=['Disk image hash does not retroactively bind historical process or save.',
                             'Getter .pdata coverage is bounded, not an exhaustive program call graph.',
                             'Names corroborate object families; per-field/UI/current-save proof is separate.'],
                getter_search_range=['0xf3a000','0xf45000'], getters=getters, extras=extras,consumer_resources=consumers,
                playbook_dispatch=dict(table_rva='0xf1d924',table_hex=table.hex(),cases=cases))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--image',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result=extract(args.image)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(image_sha256=result['image']['sha256'], getter_paths=len(result['getters']),
                          named_slots=len(set(g['slot'] for g in result['getters'])),dispatch_cases=len(result['playbook_dispatch']['cases']))))


if __name__=='__main__':
    main()
