"""Decode selected four-LEA enum registration thunks and their static rows."""
import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_MEM,X86_REG_RIP


def recover(image,entries):
    if not 1<=len(entries)<=16:raise ValueError('Select1..16 enum thunks')
    enums=[]
    for entry in entries:
        instructions=image.instructions(entry,entry+33)
        if [instruction.mnemonic for instruction in instructions]!=['lea','lea','lea','lea','jmp']:
            raise ValueError('Selected enum registration shape changed')
        refs={}
        for instruction in instructions[:4]:
            operand=instruction.operands[1]
            if operand.type!=X86_OP_MEM or operand.mem.base!=X86_REG_RIP:raise ValueError('Expected RIP-relative enum argument')
            refs[instruction.reg_name(instruction.operands[0].reg)]=instruction.address+instruction.size+operand.mem.disp-image.base
        if set(refs)!={'rcx','rdx','r8','r9'}:raise ValueError('Expected exact four registration arguments')
        name=image.read(refs['r9'],128).split(b'\0',1)[0].decode('ascii')
        info=struct.unpack('<6I',image.read(refs['rdx'],24))
        if info[0]!=zlib.crc32(name.encode()) or info[1]!=7 or info[5]!=4 or not 1<=info[4]<=128:
            raise ValueError('Unqualified enum info/name/count contract')
        # Bounded neighboring literal bank, not a global name guess or external catalog.
        bank=image.read(refs['r9'],4096)
        names={}
        for match in re.finditer(rb'[A-Za-z][A-Za-z0-9_]{0,127}\x00',bank):
            value=match.group()[:-1].decode('ascii');names.setdefault(zlib.crc32(value.encode()),set()).add(value)
        rows=[]
        for index in range(info[4]):
            crc,value,flags=struct.unpack('<IiI',image.read(refs['r8']+index*12,12))
            candidates=sorted(names.get(crc,()))
            rows.append({'name_crc':crc,'value':value,'flags_raw':flags,'name_candidates':candidates,
                'name':candidates[0] if len(candidates)==1 else None})
        pointer=struct.pack('<Q',image.base+entry);pointer_refs=[]
        for section in image.sections:
            if section['name'] not in {'.rdata','.data','.CRT'}:continue
            raw=image.data[section['raw']:section['raw']+section['size']];start=0
            while len(pointer_refs)<16:
                at=raw.find(pointer,start)
                if at<0:break
                pointer_refs.append({'section':section['name'],'reference_rva':section['rva']+at});start=at+1
        enums.append({'name':name,'registration_entry_rva':entry,'descriptor_rva':refs['rcx'],
            'static_info_rva':refs['rdx'],'static_rows_rva':refs['r8'],'name_bank_rva':refs['r9'],
            'info_raw':list(info),'rows':rows,'registration_code':image.instruction_rows(entry,entry+33),
            'registration_sha256':hashlib.sha256(image.read(entry,33)).hexdigest(),
            'absolute_entry_pointer_references':pointer_refs,
            'entry_caution':'No unwind entry required for this exact tail thunk; pointer references corroborate entry, not business-call safety'})
    return {'source_kind':'PINNED_PE_ENUM_REGISTRATION_TABLES_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
        'game_access':False,'enums':enums,'limitations':['CRC matches are qualified only when unique in the selected literal bank',
            'Internal enum names/values do not prove UI availability or current-game state',
            'Registration thunks are not invoked or exposed as business operations']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--entry',nargs='+',type=lambda value:int(value,0),required=True)
    parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out)
    if out.exists():raise SystemExit('Existing evidence is immutable; select a new output')
    result=recover(Image(),args.entry);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'enums':[{'name':row['name'],'values':{str(value['value']):value['name'] for value in row['rows']},
        'entry_pointer_refs':len(row['absolute_entry_pointer_references'])} for row in result['enums']],'game_access':False}))
