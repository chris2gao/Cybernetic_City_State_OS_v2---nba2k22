"""Join selected pure stat Getter paths to independently recovered Setter fields."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL.parent/'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_IMM,X86_OP_MEM,X86_REG_RCX,X86_REG_RIP


def recover(image,catalog):
    table=struct.unpack('<159I',image.read(0x978af8,159*4))
    rows=[];constants={}
    for family,fields in catalog['families'].items():
        for name,field in fields.items():
            if not field['callable']:continue
            pending=[table[field['native_index']]];visited=set();loads=set();instructions=[]
            while pending:
                at=pending.pop()
                if at in visited:continue
                if len(visited)>=128 or not 0x97838d<=at<0x978af8:
                    raise ValueError('Selected Getter path escaped bounded code')
                visited.add(at)
                instruction=image.instructions(at,at+15)[0]
                instructions.append({'rva':at,'mnemonic':instruction.mnemonic,'operands':instruction.op_str})
                if instruction.mnemonic=='call':raise ValueError('Expected pure stat Getter, found call')
                if instruction.operands and instruction.operands[0].type==X86_OP_MEM:
                    raise ValueError('Expected pure stat Getter, found memory destination')
                for operand in instruction.operands:
                    if operand.type!=X86_OP_MEM:continue
                    if operand.mem.base==X86_REG_RCX and operand.size==1:loads.add(operand.mem.disp)
                    if operand.mem.base==X86_REG_RIP:
                        target=instruction.address+instruction.size+operand.mem.disp-image.base
                        if operand.size!=4:raise ValueError('Unqualified Getter constant width')
                        raw=image.read(target,4)
                        constants[target]={'rva':target,'bytes_hex':raw.hex(),'float32':struct.unpack('<f',raw)[0]}
                if instruction.mnemonic=='ret':continue
                if instruction.mnemonic.startswith('j'):
                    if instruction.operands[0].type!=X86_OP_IMM:raise ValueError('Indirect branch in selected Getter leaf')
                    pending.append(instruction.operands[0].imm-image.base)
                    if instruction.mnemonic=='jmp':continue
                pending.append(at+instruction.size)
            if loads!={field['offset']}:raise ValueError('Getter/Setter field correspondence changed: '+name)
            rows.append({'family':family,'field_id':name,'native_index':field['native_index'],
                'byte_offset':field['offset'],'getter_case_rva':table[field['native_index']],
                'instructions':sorted(instructions,key=lambda row:row['rva'])})
    return {'source_kind':'PINNED_PE_SELECTED_READ_GETTER_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
        'game_access':False,'entry_rva':0x978360,'return_type':'int',
        'parameters':['PLAYER*','native_stat_index:int'],'table_rva':0x978af8,'table_entries':159,
        'selected_fields':rows,'float_constants':list(constants.values()),
        'code_and_table_range_rva':[0x978360,0x978af8+159*4],
        'code_and_table_sha256':hashlib.sha256(image.read(0x978360,0x978af8+159*4-0x978360)).hexdigest(),
        'limitations':['Potential and unclassified indices are not exposed',
            'Selected paths are pure reads; no game invocation, UI or persistence is proved',
            'Float conversion uses original Native Getter and its current runtime rounding mode, not a guessed Python/JS conversion']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    output=Path(args.out)
    if output.exists():raise SystemExit('Existing evidence is immutable; select a new output')
    result=recover(Image(),json.loads((CONTROL/'data/player_stat_fields.json').read_text(encoding='utf8')))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'selected_pure_field_paths':len(result['selected_fields']),'float_constants':result['float_constants'],'game_access':False}))
