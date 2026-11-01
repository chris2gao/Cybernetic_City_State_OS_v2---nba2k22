"""Join one recovered Native stat switch to existing PLAYER profiles, offline."""
import argparse
import json
import struct
import sys
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL.parent/'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_MEM, X86_REG_RCX, X86_REG_RSI


def recover(image, domain):
    profile=json.loads((domain/'config/memory_field_profile.json').read_text(encoding='utf8'))['fields']['PLAYER']
    known={row['offset']:row for row in profile if row.get('bytes')==1 and row.get('group') in {'attributes','durability'}}
    tendencies=json.loads((domain/'config/state_io_native/player.json').read_text(encoding='utf8'))['TENDENCY_OFFSETS']
    names={offset:name for name,offset in tendencies.items()}
    targets=list(struct.unpack('<156I',image.read(0x991f08,624)))
    starts=sorted(set(targets+[0x991ec8]))
    fields=[]
    for index,start in enumerate(targets):
        end=next((value for value in starts if value>start),0x991ec8)
        if not 0x990a4b<=start<end<=0x991ec8:
            raise ValueError('Pinned indexed setter switch shape changed')
        case=image.instructions(start,end)
        direct=[instruction.operands[0].mem.disp for instruction in case
                if instruction.mnemonic=='mov' and instruction.operands[0].type==X86_OP_MEM
                and instruction.operands[0].mem.base==X86_REG_RSI and instruction.operands[0].size==1]
        calls=[instruction.operands[0].imm-image.base for instruction in case if instruction.mnemonic=='call']
        leaf=[]
        if len(calls)==1:
            extent=image.function_range(calls[0])
            leaf=image.instructions(calls[0],extent[1] if extent and extent[1]-calls[0]<=512 else calls[0]+128)
        stores=[instruction.operands[0].mem.disp for instruction in leaf
                if instruction.mnemonic=='mov' and instruction.operands[0].type==X86_OP_MEM
                and instruction.operands[0].mem.base==X86_REG_RCX and instruction.operands[0].size==1]
        offset=direct[0] if len(set(direct))==1 else stores[0] if len(set(stores))==1 else None
        field=known.get(offset)
        fields.append({'native_index':index,'case_rva':start,'field_offset_candidate':offset,
                       'known_profile_field':field,'tendency_name':names.get(offset),
                       'kind':'TENDENCY' if offset is not None and 0x458<=offset<=0x4ba else 'ATTRIBUTE_PROFILE' if field else 'UNCLASSIFIED',
                       'native_leaf_calls':calls,'case_instructions':image.instruction_rows(start,end),
                       'leaf_instructions':[{'rva':row.address-image.base,'mnemonic':row.mnemonic,'operands':row.op_str} for row in leaf]})
    return {'source_kind':'PINNED_PE_INDEXED_STAT_SWITCH_PROFILE_JOIN_NOT_REA_PROVIDER',
            'game_build_sha256':image.sha256,'game_access':False,'setter_rva':0x990a10,
            'switch_table_rva':0x991f08,'index_count':156,'fields':fields,
            'limitations':['Unclassified fields and unnamed tendencies retain UNKNOWN semantics',
                           'A field join proves neither role authority nor live/GUI/Save effect',
                           'Selected callee windows are not a substitute for checking complete Native call side effects']}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    output=Path(args.out)
    if output.exists():raise SystemExit('Existing evidence is immutable; select a new output')
    result=recover(Image(),CONTROL.parents[1])
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'indices':156,'profile_attributes':sum(row['kind']=='ATTRIBUTE_PROFILE' for row in result['fields']),
                      'tendencies':sum(row['kind']=='TENDENCY' for row in result['fields']),'game_access':False}))
