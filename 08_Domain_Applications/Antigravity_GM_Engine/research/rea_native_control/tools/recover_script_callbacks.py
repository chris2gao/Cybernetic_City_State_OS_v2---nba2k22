"""Recover selected script declarations and adjacent callback registration sites.

Static PE only. A declaration is not proof of ABI, lifecycle or safe role action.
Only the observed xor-r9/lea-r8/lea-rdx/mov-rcx/call pattern is accepted.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image


def recover(image, pattern, limit):
    rdata=image.section('.rdata')
    selected={}
    matched=0
    for m in re.finditer(rb'[\x20-\x7e]{5,240}\x00',image.data[rdata['raw']:rdata['raw']+rdata['size']]):
        name=m.group()[:-1].decode('ascii')
        if not pattern.search(name): continue
        matched+=1
        if len(selected)<limit: selected[rdata['rva']+m.start()]=name
    text=image.read(image.text['rva'],image.text['size'])
    refs=[]
    for m in re.finditer(rb'\x48\x8d\x15....',text,re.S):
        site=image.text['rva']+m.start()
        target=site+7+struct.unpack_from('<i',m.group(),3)[0]
        if target not in selected or site<image.text['rva']+10: continue
        window=image.instruction_rows(site-10,site+15)
        expected=['xor','lea','lea','mov','call']
        if [r['mnemonic'] for r in window]!=expected: continue
        if window[0]['operands']!='r9d, r9d' or not window[1]['operands'].startswith('r8, [rip '): continue
        if not window[2]['operands'].startswith('rdx, [rip ') or window[3]['operands']!='rcx, rbx': continue
        if window[4]['operands']!='RVA+0x1fbaf0': continue
        previous=image.read(site-7,7)
        if previous[:3]!=b'\x4c\x8d\x05': continue
        callback=site+struct.unpack_from('<i',previous,3)[0]
        section=next((s['name'] for s in image.sections if s['rva']<=callback<s['rva']+s['size']),None)
        if section!='.text': continue
        chain=image.unwind_chain(callback)
        refs.append({'declaration':selected[target],'declaration_rva':target,
                     'registration_rva':site,'callback_rva':callback,
                     'callback_unwind_chain':chain,'registration_window':window,
                     'qualification':'STATIC_CALLBACK_CANDIDATE_NOT_ABI_OR_ROLE_EXECUTION_PROOF'})
    return {'source_kind':'PINNED_PE_CALLBACK_REGISTRATION_NOT_REA_PROVIDER',
            'game_build_sha256':image.sha256,'query':pattern.pattern,'string_limit':limit,
            'matching_string_count':matched,'string_selection_truncated':matched>limit,
            'registration_pattern':'xor r9d,r9d; lea r8,callback; lea rdx,declaration; mov rcx,rbx; call0x1fbaf0',
            'game_access_performed':False,'callbacks':refs,
            'limitations':['Other registration templates are not covered','Callback may depend on UI globals, VM context or original editor state',
                           'Printed declaration does not independently prove actual ABI or safe Native business commit']}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--query',required=True)
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    if not 1<=args.limit<=160: raise ValueError('Bounded declaration selection required')
    output=Path(args.out)
    if output.exists(): raise SystemExit('Existing evidence is immutable; use a new output path')
    result=recover(Image(),re.compile(args.query),args.limit)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'strings':result['matching_string_count'],'selected_limit':args.limit,
                      'truncated':result['string_selection_truncated'],'callbacks':len(result['callbacks'])}))
    for row in result['callbacks']: print(row['declaration'],hex(row['callback_rva']))
