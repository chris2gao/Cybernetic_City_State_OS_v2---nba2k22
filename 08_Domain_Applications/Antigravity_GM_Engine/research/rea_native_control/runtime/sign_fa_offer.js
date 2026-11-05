// Submit exact decided terms through original OfferContract once in Native FA_SIGNING.
function executeAction(){
 const p=request.parameters,layout=bindingSpecs['sign.fa_offer_context'].input_layout,schema=layout.schema,c=p.contract;
 const expectedKeys=['annual_wages_native','contract_type','distribution','no_trade_clause','option_type','signing_type','years_native'];
 if(!c||typeof c!=='object'||Array.isArray(c))throw Error('EXACT_SUPPORTED_FA_OFFER_TERMS_REQUIRED');
 const optionValue=Object.keys(schema.enums.OptionType).find(key=>schema.enums.OptionType[key]===c.option_type);
 const contractValue=Object.keys(schema.enums.ContractType).find(key=>schema.enums.ContractType[key]===c.contract_type);
 const optionYears={0:0,1:1,2:1,3:2};
 if(Object.keys(p).sort().join('|')!=='contract|player_id|team_id'||
   !Number.isInteger(p.player_id)||p.player_id<0||p.player_id>=65535||!Number.isInteger(p.team_id)||p.team_id<0||p.team_id>=65535||
   !c||Object.keys(c).sort().join('|')!==expectedKeys.join('|')||c.signing_type!=='FREE_AGENT'||!['NORMAL','HARDSHIP'].includes(c.contract_type)||
   c.distribution!=='CUSTOM'||typeof c.no_trade_clause!=='boolean'||optionValue===undefined||
   !Number.isInteger(c.years_native)||c.years_native<1||c.years_native>6||c.years_native<optionYears[optionValue]||
   !Array.isArray(c.annual_wages_native)||c.annual_wages_native.length!==6||c.annual_wages_native.some((value,index)=>
    !Number.isInteger(value)||(index<c.years_native?value<=0||value>2147483647:value!==0)))throw Error('EXACT_SUPPORTED_FA_OFFER_TERMS_REQUIRED');
 const roots={};
 function root(name){return ptrAt(read(base.add(layout.roots[name].global_rva),8));}
 for(const name of ['period','pool','rules','tuning','delegate']){roots[name]=root(name);if(roots[name].isNull())throw Error('FA_OFFER_CONTEXT_ROOT_UNAVAILABLE');}
 const delegateTable=ptrAt(read(roots.delegate,8));
 const profile=layout.delegate_profiles.find(row=>delegateTable.equals(base.add(row.static_vtable_rva)));
 if(!profile)throw Error('FA_OFFER_DELEGATE_UNQUALIFIED');
 const tuning=read(roots.tuning.add(0x5a5e2c),12),tuningView=new DataView(tuning);
 if(!Number.isFinite(tuningView.getFloat32(0,true))||!Number.isFinite(tuningView.getFloat32(8,true))||
   tuningView.getFloat32(8,true)<=tuningView.getFloat32(0,true))throw Error('FA_OFFER_TUNING_RANGE_UNQUALIFIED');
 function stable(){
  for(const name of Object.keys(roots))if(!root(name).equals(roots[name]))throw Error('FA_OFFER_CONTEXT_CHANGED');
  if(u32(read(roots.period.add(12),4))!==22||u32(read(roots.rules.add(0x208),4))!==1)throw Error('NATIVE_FA_SIGNING_PERIOD_AND_RULES_REQUIRED');
  if(!ptrAt(read(roots.delegate,8)).equals(delegateTable)||!equal(read(roots.tuning.add(0x5a5e2c),12),tuning))throw Error('FA_OFFER_CONTEXT_CHANGED');
  for(const [slot,target] of Object.entries(profile.required_slots))if(!ptrAt(read(delegateTable.add(Number(slot)),8)).equals(base.add(target)))throw Error('FA_OFFER_DELEGATE_CHANGED');
 }
 stable();
 const availableCount=call('sign.fa_available_count');
 if(!Number.isInteger(availableCount)||availableCount<1||availableCount>1000)throw Error('NATIVE_FA_AVAILABLE_POOL_UNQUALIFIED');
 const available=call('sign.fa_available_pool',0);
 if(available.isNull())throw Error('NATIVE_FA_AVAILABLE_POOL_UNQUALIFIED');
 const availableBefore=read(available,0x1f48);
 if(u16(availableBefore,0x1f40)!==availableCount)throw Error('NATIVE_FA_AVAILABLE_POOL_CHANGED');
 const target=team(p.team_id),player=call('player.by_id',p.player_id);
 if(player.isNull())throw Error('PLAYER_UID_NOT_FOUND');
 const playerBefore=read(player,1264);
 if(u16(playerBefore,0xf4)!==p.player_id)throw Error('PLAYER_UID_RESOLUTION_MISMATCH');
 let membership=0;for(let i=0;i<availableCount;i++)if(ptrAt(availableBefore,i*8).equals(player))membership++;
 if(membership!==1)throw Error('PLAYER_NOT_UNIQUELY_IN_NATIVE_FA_AVAILABLE_POOL');
 if(((u32(playerBefore,0x32c)>>>18)&31)!==0||((u32(playerBefore,0x340)>>>15)&7)!==0)throw Error('PLAYER_HAS_EXISTING_BASE_OR_EXTENSION_YEARS');
 if(call('sign.default_type',player,target)!==2)throw Error('NATIVE_SIGNING_TYPE_IS_NOT_FREE_AGENT');
 function decode(raw){
  const values={};for(const field of schema.fields){const items=[];
   for(let index=0;index<field.count;index++){
    const at=field.offset+index*4;let word=0;for(let n=0;n<4&&at+n<44;n++)word=(word|(new Uint8Array(raw)[at+n]<<(n*8)))>>>0;
    let value=field.width===32?word:(word>>>field.shift)&(2**field.width-1);
    if(field.signed&&value>=2**(field.width-1))value-=2**field.width;items.push(value);
   }values[field.name]=field.count===1?items[0]:items;
  }return values;
 }
 const pool=roots.pool.add(schema.pool.offset),before=[];let empty=-1;
 function eligible(fields){return fields.Status!==0&&fields.IsArchived===0&&fields.Type!==3&&fields.PlayerId===p.player_id&&fields.TeamId===p.team_id;}
 for(let i=0;i<1000;i++){
  const raw=read(pool.add(i*44),44),fields=decode(raw);before.push(raw);
  if(eligible(fields))throw Error('FRESH_OFFER_WOULD_REPLACE_EXISTING_RECORD');
  if(fields.Status===0&&empty<0)empty=i;
 }
 if(empty<0)throw Error('FRESH_OFFER_POOL_HAS_NO_EMPTY_RECORD');
 // Private field construction, preserving the same unregistered tail as the original POD reset.
 const raw=new ArrayBuffer(44),view=new DataView(raw),wages=c.annual_wages_native;
 view.setUint16(0,p.player_id,true);view.setUint16(2,p.team_id,true);view.setUint32(4,wages[0],true);
 for(let i=0;i<6;i++)view.setUint32(8+i*4,wages[i],true);
 view.setUint32(32,(3<<8)|(Number(c.no_trade_clause)<<12)|(1<<18)|(2<<22)|(Number(optionValue)<<28)|(Number(contractValue)<<30),true);
 view.setUint32(40,(u32(before[empty],40)&0xffffe000)|(c.years_native<<8),true);
 const proposal=Memory.alloc(44);proposal.writeByteArray(raw);const expected=decode(raw);
 for(let i=0;i<1000;i++)if(!equal(read(pool.add(i*44),44),before[i]))throw Error('FA_OFFER_POOL_CHANGED_BEFORE_CALL');
 if(!team(p.team_id).equals(target))throw Error('FA_OFFER_TEAM_CHANGED_BEFORE_CALL');
 if(!equal(read(available,0x1f48),availableBefore))throw Error('NATIVE_FA_AVAILABLE_POOL_CHANGED');
 if(!equal(read(player,1264),playerBefore))throw Error('FA_OFFER_PLAYER_CHANGED_BEFORE_CALL');
 stable();
 const returned=call('sign.offer_fa_phase',proposal,ptr(0),0,0);
 if(returned!==0&&returned!==1)throw Error('NATIVE_OFFER_RETURN_UNQUALIFIED');
 stable();
 const playerAgain=call('player.by_id',p.player_id),playerAfter=read(player,1264);
 const availableAgain=call('sign.fa_available_pool',0);
 if(!availableAgain.equals(available)||!equal(read(available,0x1f48),availableBefore))throw Error('NATIVE_FA_AVAILABLE_POOL_CHANGED');
 if(!playerAgain.equals(player)||u16(playerAfter,0xf4)!==p.player_id||[0x60,0xa0,0xa8].some(at=>!ptrAt(playerBefore,at).equals(ptrAt(playerAfter,at))))throw Error('FA_OFFER_PLAYER_CONTEXT_CHANGED');
 function contractRaw(bytes){return layout.contract_fields.map(field=>{const n=Math.ceil((field.start_bit+field.bits)/8);let value=0;
  for(let i=0;i<n;i++)value+=new Uint8Array(bytes)[field.offset+i]*2**(8*i);return Math.floor(value/2**field.start_bit)%2**field.bits;});}
 if(JSON.stringify(contractRaw(playerBefore))!==JSON.stringify(contractRaw(playerAfter)))throw Error('FA_OFFER_PHYSICAL_CONTRACT_SUBSET_CHANGED');
 const termFields=['PlayerId','TeamId','Wage','ForcedWage','NoTradeClause','Type','Distribution','OptionType','ContractType','Years'];
 function exactTerms(value){return termFields.every(name=>JSON.stringify(value[name])===JSON.stringify(expected[name]));}
 const privateAfter=decode(read(proposal,44));if(!exactTerms(privateAfter))throw Error('FA_OFFER_NATIVE_CHANGED_DECIDED_TERMS');
 const created=[];
 for(let i=0;i<1000;i++){
  const fields=decode(read(pool.add(i*44),44));
  if(decode(before[i]).Status===0&&fields.Status!==0&&fields.PlayerId===p.player_id&&fields.TeamId===p.team_id)created.push({record_index:i,fields});
 }
 if(created.length>1||created.some(row=>!exactTerms(row.fields)))throw Error('FA_OFFER_RECORD_OBSERVATION_UNQUALIFIED');
 const observed=created.length?created[0]:null;
 if(returned===1&&(!observed||observed.fields.Status!==1))throw Error('FA_OFFER_RETURN_AND_PENDING_STATUS_DISAGREE');
 if(returned===0&&observed&&observed.fields.Status!==4)throw Error('FA_OFFER_REJECTION_STATUS_UNQUALIFIED');
 stable();
 result(returned===0?'REJECTED_BY_GAME':'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  native_return:returned,submission_only:true,signing_completed:false,period_name:'FA_SIGNING',
  observation:{player_id:p.player_id,team_id:p.team_id,record_index:observed?observed.record_index:null,
   status_value:observed?observed.fields.Status:null,status_name:observed?schema.enums.Status[observed.fields.Status]:null,
   decided_terms_preserved:true,physical_contract_subset_unchanged:true},
  verification_scope:'Same-handler return and offer observations only; independent acceptance/UI/persistence and final signing remain unproven',
  generated_prices_used:false,direct_pool_or_player_writes:false,automatic_process_or_retry:false
 });
}
