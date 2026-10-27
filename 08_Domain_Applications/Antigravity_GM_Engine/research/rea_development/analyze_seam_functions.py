import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
p=argparse.ArgumentParser();p.add_argument('--dir',required=True);a=p.parse_args();root=Path(a.dir)
seams=json.loads((root/'native-seams.json').read_text());data=Path('E:/Games/NBA 2K22/NBA2K22.exe').read_bytes()
decoder=Cs(CS_ARCH_X86,CS_MODE_64)
targets={tuple(x['function_range']):[] for x in seams['xrefs'] if x['function_range'] and any(s in x['string'] for s in ['LinkMentor','SetMentorsInCurrentTeam','GetBadgeLevelByIndex','GetBadgeLevelCost','EnqueueTask','ActiveScorebug'])}
for x in seams['xrefs']:
 k=tuple(x['function_range']) if x['function_range'] else None
 if k in targets and x['string'] not in targets[k]:targets[k].append(x['string'])
rows=[]
for (start,end),labels in targets.items():
 if end-start>20000:continue
 raw=data[start-2560:end-2560]
 ins=[dict(rva=i.address-0x140000000,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in decoder.disasm(raw,0x140000000+start)]
 if not ins:continue
 rows.append(dict(range=[start,end],labels=labels,instructions=ins,decoded_through_rva=ins[-1]['rva']+len(bytes.fromhex(ins[-1]['bytes'])),body_sha256=__import__('hashlib').sha256(raw).hexdigest(),limitations=['pdata range may be one unwind fragment','labels are assertion/log references, not recovered symbol identity','comparison operands are not semantic growth thresholds without dataflow and mode proof']))
(root/'seam-function-candidates.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([dict(range=r['range'],labels=r['labels'],instruction_count=len(r['instructions']),comparisons=[i for i in r['instructions'] if i['mnemonic'].startswith(('cmp','test','ucom','com'))][:12],calls=[i['operands'] for i in r['instructions'] if i['mnemonic']=='call'][:14]) for r in rows]))
