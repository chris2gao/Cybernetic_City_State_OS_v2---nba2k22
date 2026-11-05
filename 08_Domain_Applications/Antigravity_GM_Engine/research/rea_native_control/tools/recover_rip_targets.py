"""Selected RIP-relative LEA references, confirmed from bounded unwind entries."""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image


def recover(image,targets,limit=24,radius=0):
    if not 1<=len(targets)<=16:raise ValueError('Select1..16 target RVAs')
    if not 0<=radius<=128:raise ValueError('Selected target radius must be0..128')
    text=image.read(image.text['rva'],image.text['size'])
    pattern=rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....'
    rows=[];unconfirmed=[];cache={};truncated=False
    for match in re.finditer(pattern,text,re.DOTALL):
        site=image.text['rva']+match.start()
        target=site+7+struct.unpack_from('<i',match.group(),3)[0]
        requested=min(targets,key=lambda value:abs(value-target))
        if abs(requested-target)>radius:continue
        chain=image.unwind_chain(site)
        if not chain or chain[0]['end']-chain[0]['begin']>24576:
            if len(unconfirmed)<limit:unconfirmed.append({'site_candidate_rva':site,'target_rva':target,
                'requested_target_rva':requested,'instruction_boundary_confirmed':False,
                'reason':'NO_UNWIND_OR_OVERSIZED_FRAGMENT','window_from_pattern_candidate':image.instruction_rows(site,site+96)})
            else:truncated=True
            continue
        fragment=chain[0]
        key=(fragment['begin'],fragment['end'])
        if key not in cache:cache[key]=image.instruction_rows(*key)
        instructions=cache[key]
        at=next((i for i,row in enumerate(instructions) if row['rva']==site and row['mnemonic']=='lea'),None)
        if at is None:continue
        if len(rows)>=limit:truncated=True;break
        rows.append({'site_rva':site,'target_rva':target,'requested_target_rva':requested,'primary_rva':chain[-1]['begin'],
            'unwind_chain':chain,'instruction_boundary_confirmed':True,
            'window':instructions[max(0,at-10):at+20]})
    return {'source_kind':'PINNED_PE_SELECTED_RIP_LEA_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
        'game_access':False,'targets_rva':sorted(targets),'radius_bytes':radius,'references':rows,'unconfirmed_candidates':unconfirmed,'reference_limit':limit,'truncated':truncated,
        'limitations':['Only selected7-byte RIP-relative LEA forms are searched',
            'No-unwind/oversized-fragment candidates are separate unconfirmed leads; windows are not entry or ABI proof',
            'Reference windows do not prove a complete function ABI or game effect']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--target',nargs='+',type=lambda x:int(x,0),required=True)
    parser.add_argument('--out',required=True);parser.add_argument('--radius',type=int,default=0);args=parser.parse_args();out=Path(args.out)
    if out.exists():raise SystemExit('Existing evidence is immutable; select a new output')
    result=recover(Image(),set(args.target),radius=args.radius)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'references':[{'site':hex(row['site_rva']),'target':hex(row['target_rva']),'primary':hex(row['primary_rva'])} for row in result['references']],
        'unconfirmed_candidates':[{'site':hex(row['site_candidate_rva']),'target':hex(row['target_rva'])} for row in result['unconfirmed_candidates']],
        'truncated':result['truncated'],'game_access':False}))
