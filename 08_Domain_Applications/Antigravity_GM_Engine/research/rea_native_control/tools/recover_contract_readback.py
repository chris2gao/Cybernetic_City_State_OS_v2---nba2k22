"""Recover selected salary dispatch/leaf paths and remaining-year formula offline."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
CONTROL=Path(__file__).resolve().parents[1]
ROOT=CONTROL.parents[3]
sys.path.insert(0,str(CONTROL.parent/'rea_native_action'))
from pe_local import Image

def fnv(raw):
 value=2166136261
 for byte in raw:value=((value^byte)*16777619)&0xffffffff
 return value

def recover(image):
 paths={};signatures={}
 for kind,entry,table,maximum in [('getter',0x9888b0,0x988914,16),('setter',0x998820,0x998930,48)]:
  targets=struct.unpack('<6I',image.read(table,24));cases=[]
  for index,target in enumerate(targets):
   instructions=image.instructions(target,target+maximum)
   end=next(i for i,row in enumerate(instructions) if row.mnemonic=='ret')
   selected=instructions[:end+1];rows=image.instruction_rows(target,selected[-1].address-image.base+1)
   expected=0x1a4+index*4
   if kind=='getter':
    if [(row['mnemonic'],row['operands']) for row in rows]!=[('mov',f'eax, dword ptr [rcx + {hex(expected)}]'),('btr','eax, 0x1f'),('ret','')]:
     raise ValueError('Selected salary Getter case changed')
   else:
    operands=[row['operands'] for row in rows]
    if f'dword ptr [rcx + {hex(expected)}], 0x80000000' not in operands or 'eax, 0x7fffffff' not in operands or 'eax, edx' not in operands:
     raise ValueError('Selected salary Setter preservation/clamp changed')
   cases.append({'year_index':index,'entry_rva':target,'player_offset':expected,'instructions':rows})
  end=table+24;raw=image.read(entry,end-entry)
  paths[kind]={'entry_rva':entry,'table_rva':table,'targets_rva':list(targets),'cases':cases,
   'raw_sha256':hashlib.sha256(raw).hexdigest()}
  signatures[kind]=[{'rva':entry,'bytes':len(raw),'fnv32':fnv(raw)}]
 years=image.instruction_rows(0x9886c0,0x98879d)
 required=[('mov','ecx, dword ptr [rcx + 0x32c]'),('mov','ebx, dword ptr [r9 + 0x340]'),
  ('shr','ecx, 0x12'),('and','ecx, 0x1f'),('shr','ebx, 0xf'),('and','ebx, 7'),('cmp','ebx, 6')]
 if not all(any((row['mnemonic'],row['operands'])==item for row in years) for item in required):
  raise ValueError('Remaining-year field/formula/assertion changed')
 signatures['remaining_years']=[{'rva':0x9886c0,'bytes':221,'fnv32':fnv(image.read(0x9886c0,221))}]
 return {'source_kind':'PINNED_PE_CONTRACT_CONSUMERS_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
  'game_access':False,'salary_dispatch':paths,'code_signatures':signatures,
  'remaining_year_getter':{'entry_rva':0x9886c0,'instructions':years,
   'parameters':['PLAYER pointer','include_options int0/1'],
   'formula':'((PLAYER[0x32c] >>18)&31) + ((PLAYER[0x340] >>15)&7) + (include_options ? option_years :0)',
   'maximum_before_assertion':6,'option_year_counts':{'0':0,'1':1,'2':1,'3':2}},
  'raw_field_override':{'name':'years_left_on_contract','offset':814,'start_bit':2,'bits':5,
   'meaning':'Stored base non-option years; excludes extension and optional years'},
  'salary_semantics':{'slots':6,'stored_value_bits':31,'upper_bit':'Preserved by original Setter; masked by original Getter',
   'setter_input_above_maximum':'Unsigned clamp to0x7fffffff; proposal uint32 encoding is not exact salary application'},
  'limits':['No code execution, UI labels, currency-unit or persistence proof',
   'Do not call the assertion-bearing years Getter when the expected sum exceeds6',
   'Salary Setter recovery is evidence only; no salary-edit operation is exposed']}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
 output=Path(args.out)
 if output.exists():raise SystemExit('Existing evidence is immutable; select a new output')
 result=recover(Image());output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'salary_cases_per_service':6,'stored_salary_bits':31,'remaining_year_width':5,'game_access':False}))
