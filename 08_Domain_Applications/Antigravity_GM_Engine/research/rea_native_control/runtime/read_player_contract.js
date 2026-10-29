// Original contract Getters only; no offer, selection mark or mutation.
function executeAction(){
 const p=request.parameters,layout=bindingSpecs['player.contract_read_context'].input_layout;
 if(Object.keys(p).join('|')!=='player_id'||!Number.isInteger(p.player_id)||p.player_id<0||p.player_id>=65535)
  throw Error('EXACT_CONTRACT_PLAYER_QUERY_REQUIRED');
 const player=call('player.by_id',p.player_id);
 if(player.isNull())throw Error('PLAYER_UID_NOT_FOUND');
 const before=read(player,1264);
 if(u16(before,0xf4)!==p.player_id)throw Error('PLAYER_UID_RESOLUTION_MISMATCH');
 const current=ptrAt(before,0x60),owner=ptrAt(before,0xa8);
 const currentId=current.isNull()?null:u16(read(current.add(0xca8),2));
 const ownerId=owner.isNull()?null:u16(read(owner.add(0xca8),2));
 const raw={};const selected=new Set();
 for(const field of layout.fields){
  const n=field.bits?Math.ceil((field.start_bit+field.bits)/8):field.bytes;let value=0;
  for(let i=0;i<n;i++){value+=new Uint8Array(before)[field.offset+i]*2**(8*i);selected.add(field.offset+i);}
  raw[field.name]=field.bits?Math.floor(value/2**field.start_bit)%2**field.bits:value;
 }
 const wages=[];
 for(let i=0;i<6;i++){
  const value=call('player.get_salary',player,i);
  if(!Number.isInteger(value)||value<0||value>2147483647||value!==raw['contract_year_'+(i+1)])throw Error('ORIGINAL_SALARY_GETTER_MISMATCH');
  wages.push(value);
 }
 const option=raw.contract_option,optionYears=layout.option_year_counts[option];
 const total=raw.years_left_on_contract+raw.extension_length,years={};
 for(const [name,flag,expected] of [['without_options',0,total],['with_options',1,total+optionYears]]){
  if(expected>6){years[name]={value:null,status:'BLOCKED_NATIVE_ASSERTION_SUM_GT6'};continue;}
  const value=call('player.get_remaining_contract_years',player,flag);
  if(value!==expected)throw Error('ORIGINAL_REMAINING_YEARS_GETTER_MISMATCH');
  years[name]={value,status:'ORIGINAL_NATIVE_GETTER_OBSERVED'};
 }
 const again=call('player.by_id',p.player_id),after=read(player,1264);
 if(!again.equals(player)||u16(after,0xf4)!==p.player_id||!ptrAt(after,0x60).equals(current)||!ptrAt(after,0xa8).equals(owner)||
   [...selected].some(offset=>new Uint8Array(before)[offset]!==new Uint8Array(after)[offset])||
   ((u32(before,0x130)^u32(after,0x130))&0x600)!==0||
   (!current.isNull()&&u16(read(current.add(0xca8),2))!==currentId)||
   (!owner.isNull()&&u16(read(owner.add(0xca8),2))!==ownerId))throw Error('PLAYER_CONTRACT_SNAPSHOT_CHANGED');
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  read_only:true,snapshot_bracket_unchanged:true,
  data:{player_id:p.player_id,current_team_id:currentId,contract_team_id:ownerId,contract_raw:raw,
   wages_native:wages,option:{value:option,name:layout.option_names[option],year_count:optionYears},
   remaining_years:years,selection_mark_raw:(u32(before,0x130)>>>9)&1,response_flag_raw:(u32(before,0x130)>>>10)&1},
  unknown_scope:['Native save/world/phase identity','UI/currency and current contract eligibility','atomicity/ABA','independent signing completion and persistence'],
  arbitrary_memory_dump_emitted:false,hidden_potential_emitted:false,
  observation_scope:'Original contract Getters and scoped raw fields; host must bind identity, provenance and role visibility'
 });
}
