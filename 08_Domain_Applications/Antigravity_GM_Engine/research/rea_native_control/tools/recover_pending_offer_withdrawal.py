"""Recover original status-clear subset and fixed caller flags from the pinned PE only."""
import argparse,hashlib,json,sys
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
 roots={}
 for name,site in [('period',0xedf010),('pool',0x12b6526)]:
  row=image.instructions(site,site+16)[0];operand=row.operands[-1]
  assert row.mnemonic=='mov' and operand.type==X86_OP_MEM and operand.mem.base==X86_REG_RIP
  roots[name]={'global_rva':row.address+row.size+operand.mem.disp-image.base,
               'source_instruction':image.instruction_rows(site,site+row.size)[0]}
 assert roots['period']['global_rva']==0x632b470 and roots['pool']['global_rva']==0x632b478
 body=image.read(0x12b4040,216);rows=image.instruction_rows(0x12b4040,0x12b4118)
 required={0x12b4069:('and','eax, 0xffc3ffff'),0x12b4073:('mov','dword ptr [rbx + 0x20], eax'),
  0x12b4092:('call','RVA+0xf3f580'),0x12b409f:('test','dword ptr [rbx + 0x20], 0x1c00000'),
  0x12b40a6:('jne','RVA+0x12b4103'),0x12b4108:('mov','eax, 1')}
 for site,expected in required.items():
  row=next(row for row in rows if row['rva']==site)
  assert (row['mnemonic'],row['operands'])==expected
 caller=image.instruction_rows(0x12bb8f4,0x12bb902)
 assert [(row['mnemonic'],row['operands']) for row in caller]==[
  ('xor','edx, edx'),('lea','rcx, [rdi + 0x1727a8]'),('call','RVA+0x12b4040')]
 return {'source_kind':'PINNED_PE_PENDING_OFFER_WITHDRAWAL_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
  'game_access':False,'roots':roots,'native_abi':{'rva':0x12b4040,'return_type':'int',
   'parameters':['game-owned selected44-byte offer pointer','int0 from original caller'],
   'original_fixed_flag_callsite_rva':0x12bb8fd,'caller_window':caller},
  'qualified_subset':{'Status':1,'Type':2,'IsArchived':0,'matching_active_records_required':1,
   'expected_registered_fields_required':25,'runtime_native_period':22,'host_subscene':'FA_SIGNING_OFFERS'},
  'effect':{'status_word_offset':32,'status_mask':0x3c0000,'resulting_status':0,
   'other_record_bytes_preserved_in_selected_branch':True,'original_player_lookup_rva':0xf3f580,
   'draft_type_only_cleanup_skipped_for_free_agent_type':True,'caller_decision_required':True},
  'service_extent':{'entry_rva':0x12b4040,'span_bytes':216,'body_sha256':hashlib.sha256(body).hexdigest(),
   'instructions':rows},
  'code_signatures':[{'rva':rva,'bytes':size,'fnv32':fnv(image.read(rva,size))} for rva,size in
   [(0x12b4040,216),(0xedf010,11),(0x12b6520,295),(0x12ba5a0,223)]],
  'limits':['Native status-clear semantics; exact current UI label and current save are unverified',
   'Clearing one pending offer is not rejection/acceptance or final signing',
   'No refund/quota or negotiation/player-response rollback is certified',
   'Other statuses/types and whole-pool response/selection services remain outside this qualified action']}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out)
 if out.exists():raise SystemExit('Existing evidence is immutable; select a new output')
 data=recover(Image());out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'original_service':hex(data['native_abi']['rva']),'status_mask':hex(data['effect']['status_mask']),
  'direct_backend_game_calls':3,'game_access':False}))
