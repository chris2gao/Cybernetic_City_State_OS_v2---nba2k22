"""Recover the bounded period/roots/POD offer-construction contract from the pinned PE."""
import argparse,hashlib,json,re,struct,sys,zlib
from pathlib import Path
CONTROL=Path(__file__).resolve().parents[1];ROOT=CONTROL.parents[3]
sys.path.insert(0,str(CONTROL.parent/'rea_native_action'))
from pe_local import Image
from capstone.x86 import X86_OP_MEM,X86_REG_RIP

def fnv(raw):
 value=2166136261
 for byte in raw:value=((value^byte)*16777619)&0xffffffff
 return value

def recover(image):
 bank_rva=36840864;bank=image.read(bank_rva,1024);names={}
 for match in re.finditer(rb'[A-Za-z][A-Za-z0-9_]{1,100}\x00',bank):
  name=match.group()[:-1].decode('ascii');names.setdefault(zlib.crc32(name.encode()),{})[name]=bank_rva+match.start()
 rows=[]
 for index,crc in enumerate(struct.unpack('<31I',image.read(0x2a46620,124))):
  matches=names.get(crc,{})
  if len(matches)!=1:raise ValueError('Unique period name in selected literal bank required')
  name,rva=next(iter(matches.items()));rows.append({'value':index,'crc32':crc,'name':name,'literal_rva':rva})
 if rows[22]['name']!='FA_SIGNING' or rows[20]['name']!='CONTRACT_OPTIONS':raise ValueError('Period identity changed')
 roots={}
 for name,site in [('period',0xedf010),('pool',0x12b6526),('rules',0x12b7d6f),('tuning',0x12bd6d0),('delegate',0x12bc909)]:
  instruction=image.instructions(site,site+16)[0];operand=instruction.operands[-1]
  if instruction.mnemonic!='mov' or operand.type!=X86_OP_MEM or operand.mem.base!=X86_REG_RIP:
   raise ValueError('Selected root instruction changed: '+name)
  roots[name]={'global_rva':instruction.address+instruction.size+operand.mem.disp-image.base,
   'source_instruction':image.instruction_rows(site,site+instruction.size)[0]}
 if roots['period']['global_rva']!=0x632b470 or roots['pool']['global_rva']!=0x632b478 or roots['rules']['global_rva']!=0x632b498:
  raise ValueError('Do not conflate distinct period/pool/rules roots')
 signatures=[]
 for rva,length in [(0xedf010,11),(0xee0180,296),(0x2a46620,124),(bank_rva,1024),
  (0x12b6520,295),(0x12ba5a0,223),(0x12b7290,1554),(0x12b7d60,224),(0x12bc4a0,2332),
  (0x9b5bf0,44),(0x9b5bb0,58),(0xf3cf10,204)]:
  raw=image.read(rva,length);signatures.append({'rva':rva,'bytes':length,'fnv32':fnv(raw)})
 original=json.loads((CONTROL/'data/native_bindings.json').read_text(encoding='utf8'))
 delegate=next(row for row in original['bindings'] if row['binding_id']=='rotation.current_delegate')['input_layout']
 profiles=[]
 for row in delegate['allowed_profiles']:
  at=row['static_vtable_candidate_rva'];slots={str(slot):struct.unpack('<Q',image.read(at+slot,8))[0]-image.base for slot in (0x208,0x218,0xf58)}
  if any(not 0<value<image.text['rva']+image.text['size'] for value in slots.values()):raise ValueError('Delegate slot outside pinned text')
  profiles.append({'static_vtable_rva':at,'required_slots':slots})
 return {'source_kind':'PINNED_PE_FA_OFFER_CONTRACT_NOT_REA_PROVIDER','game_build_sha256':image.sha256,'game_access':False,
  'periods':rows,'period_crc_table_rva':0x2a46620,'literal_bank_rva':bank_rva,'roots':roots,
  'code_signatures':signatures,'delegate_profiles':profiles,
  'available_pool':{'count_getter_rva':0x9b5bf0,'resolver_rva':0xf3cf10,'resolver_index':0,
   'record_bytes':0x1f48,'pointer_capacity':1000,'count_offset':0x1f40,
   'source_index_getter_rva':0x9b5bb0,'source_offer_caller_rva':0x12bda50,
   'meaning':'Exact pool0 used by the original FA caller; require supplied Player pointer membership, never choose an alternative'},
  'native_offer_abi':{'rva':0x12bd4c0,'return_type':'int','arguments':['private44-byte record','null context',0,0],
   'observed_fixed_flag_caller_rva':0x12bdccf,'direct_process_called_by_new_backend':False},
  'fresh_input':{'bytes':44,'empty_pool_template_preserves_word40_mask':0xffffe000,
   'status':1,'negotiation_level':3,'type':2,'forced_offer':0,'verbal_deal':0,'existing_offer':0,'user_initiated':0,
   'source_initializer_rva':0x12b7290,'source_prefix_range':[0x12b7290,0x12b733f],
   'source_tail_range':[0x12b7870,0x12b7892],
   'generator_called':False,'allocator_called_by_new_backend':False},
  'guard':{'period':22,'period_name':'FA_SIGNING','rules_offset':0x208,'rules_value':1,
   'pool_offset':0x1727a8,'pool_count':1000,'pool_stride':44,
   'tuning_offsets':{'response_scale_int':0x5a5e3c,'desirability_lower_float':0x5a5e2c,'desirability_upper_float':0x5a5e34}},
  'limits':['Fixed flags are justified by this original caller, not a general interpretation of all modes',
   'Period names are recovered from the indexed debug CRC table; no live phase/save identity is observed',
   'Inherited delegate profiles qualify exact static vtables/used slots only, not current live readiness',
   'Private input construction and Native offer submission do not qualify final signing or deferred completion']}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out)
 if out.exists():raise SystemExit('Existing evidence is immutable; select a new output')
 result=recover(Image());out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'period22':result['periods'][22]['name'],'period20':result['periods'][20]['name'],
  'roots':{key:hex(value['global_rva']) for key,value in result['roots'].items()},'private_input_bytes':44,'game_access':False}))
