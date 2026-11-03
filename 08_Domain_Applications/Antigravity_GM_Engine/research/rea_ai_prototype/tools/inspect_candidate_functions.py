import argparse,hashlib,json,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);a=p.parse_args();root=Path(a.dir)
base=json.loads((root/'static_ai_seams.json').read_text());data=Path('E:/Games/NBA 2K22/NBA2K22.exe').read_bytes();assert hashlib.sha256(data).hexdigest()==base['exe_sha256']
references=base['references']+json.loads((root/'static_ai_followup.json').read_text())['references']
selected=[x for x in references if x['literal'].endswith(('::GetException','::GetExceptionAmount','::LinkMentor','::SetMentorsInCurrentTeam','::GetOpponentGameplanIndex','::AddGameplan'))]
selected=list({tuple(x['unwind_range_rva']):x for x in selected}.values())
rows=[];decoder=Cs(CS_ARCH_X86,CS_MODE_64)
for ref in selected[:8]:
 start,end=ref['unwind_range_rva']
 if end-start>4096:continue
 # .text has raw RVA delta2560 in this pinned PE; validate section before translation.
 pe=struct.unpack_from('<I',data,60)[0];opt=struct.unpack_from('<H',data,pe+20)[0];h=pe+24+opt
 assert data[h:h+5]==b'.text';rv,raw=struct.unpack_from('<I',data,h+12)[0],struct.unpack_from('<I',data,h+20)[0]
 offset=raw+start-rv;body=data[offset:offset+end-start];instructions=[]
 for i in decoder.disasm(body,0x140000000+start):
  operands=re.sub(r'0x(14[0-9a-f]{7})\b',lambda m:'RVA+'+hex(int(m.group(1),16)-0x140000000),i.op_str)
  operands=operands.replace('0xffffffffffffffff','-1')
  instructions.append({'rva':i.address-0x140000000,'mnemonic':i.mnemonic,'operands':operands})
 rows.append({'mechanism':ref['mechanism'],'referenced_literal':ref['literal'],'unwind_range_rva':[start,end],'body_sha256':hashlib.sha256(body).hexdigest(),'instruction_count':len(instructions),'instructions':instructions,'classification':'STATIC_CANDIDATE_FRAGMENT_NOT_AI_CALLSITE','raw_bytes_published':False})
result={'source_kind':'STATIC_BINARY','game_build_sha256':base['exe_sha256'],'functions':rows,'limits':{'max_ranges':8,'max_range_bytes':4096},'operand_normalization':'image references rendered as RVA; u64 all-bits-set immediates rendered as signed -1','limitations':['unwind fragments and log/assert literals do not recover function signature or AI controller dispatch','trade exception accessors are not transaction validator or commit','no game call or attach']}
(root/'candidate_function_fragments.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'candidate_fragments':[{'mechanism':r['mechanism'],'literal':r['referenced_literal'],'rva_range':r['unwind_range_rva'],'instruction_count':r['instruction_count']} for r in rows]}))
