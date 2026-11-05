// Exact active pending-offer cancellation through the original service; no backend game writes.
function executeAction(){
 const p=request.parameters,layout=bindingSpecs['sign.withdraw_context'].input_layout,schema=layout.schema,e=p.expected_offer;
 if(Object.keys(p).sort().join('|')!=='expected_offer|player_id|team_id'||
  !Number.isInteger(p.player_id)||p.player_id<0||p.player_id>=65535||!Number.isInteger(p.team_id)||p.team_id<0||p.team_id>=65535||
  !e||Array.isArray(e)||Object.keys(e).sort().join('|')!==schema.fields.map(field=>field.name).sort().join('|'))throw Error('EXACT_EXPECTED_PENDING_OFFER_REQUIRED');
 for(const field of schema.fields){
  const values=field.count===1?[e[field.name]]:e[field.name],low=field.signed?-(2**(field.width-1)):0,high=2**(field.width-Number(field.signed))-1;
  if(!Array.isArray(values)||values.length!==field.count||values.some(value=>!Number.isInteger(value)||value<low||value>high))throw Error('EXPECTED_OFFER_FIELD_REPRESENTATION');
 }
 if(e.PlayerId!==p.player_id||e.TeamId!==p.team_id||e.Type!==2||e.Status!==1||e.IsArchived!==0)throw Error('EXACT_OFFERED_FREE_AGENT_RECORD_REQUIRED');
 function root(name){return ptrAt(read(base.add(layout.roots[name].global_rva),8));}
 const period=root('period'),franchise=root('pool');
 if(period.isNull()||franchise.isNull())throw Error('OFFER_WITHDRAW_ROOT_UNAVAILABLE');
 function stable(){
  if(!root('period').equals(period)||!root('pool').equals(franchise))throw Error('OFFER_WITHDRAW_ROOT_CHANGED');
  if(u32(read(period.add(12),4))!==22)throw Error('NATIVE_FA_SIGNING_PERIOD_REQUIRED');
 }
 function decode(raw){const view=new DataView(raw),fields={};
  for(const f of schema.fields){const values=[];
   for(let i=0;i<f.count;i++){
    const at=f.offset+i*4;let word=0;
    for(let n=0;n<4&&at+n<44;n++)word=(word|(view.getUint8(at+n)<<(n*8)))>>>0;
    let value=f.width===32?word:(word>>>f.shift)&(2**f.width-1);
    if(f.signed&&value>=2**(f.width-1))value-=2**f.width;values.push(value);
   }fields[f.name]=f.count===1?values[0]:values;
  }return fields;
 }
 stable();const owner=team(p.team_id),player=call('player.by_id',p.player_id);
 if(player.isNull())throw Error('PLAYER_UID_NOT_FOUND');
 const playerBefore=read(player,1264);if(u16(playerBefore,0xf4)!==p.player_id)throw Error('PLAYER_UID_RESOLUTION_MISMATCH');
 const pool=franchise.add(schema.pool.offset),before=[],matches=[];
 for(let i=0;i<1000;i++){
  const raw=read(pool.add(i*44),44),f=decode(raw);before.push(raw);
  if(f.PlayerId===p.player_id&&f.TeamId===p.team_id&&f.Status!==0&&f.IsArchived===0&&f.Type!==3)matches.push({index:i,fields:f});
 }
 if(matches.length!==1)throw Error('ACTIVE_OFFER_IDENTITY_NOT_UNIQUE');
 const selected=matches[0];
 if(!schema.fields.every(field=>JSON.stringify(selected.fields[field.name])===JSON.stringify(e[field.name])))throw Error('EXPECTED_PENDING_OFFER_CHANGED');
 const afterExpected=before[selected.index].slice(0),view=new DataView(afterExpected);
 view.setUint32(32,(view.getUint32(32,true)&~0x3c0000)>>>0,true);
 for(let i=0;i<1000;i++)if(!equal(read(pool.add(i*44),44),before[i]))throw Error('OFFER_WITHDRAW_POOL_CHANGED_BEFORE_CALL');
 if(!equal(read(player,1264),playerBefore)||!team(p.team_id).equals(owner))throw Error('OFFER_WITHDRAW_IDENTITY_CHANGED_BEFORE_CALL');
 stable();
 const returned=call('sign.cancel_pending_offer',pool.add(selected.index*44),0);
 if(returned!==1)throw Error('OFFER_WITHDRAW_RETURN_UNQUALIFIED');
 stable();
 const playerAgain=call('player.by_id',p.player_id);
 if(!playerAgain.equals(player)||!equal(read(player,1264),playerBefore)||!team(p.team_id).equals(owner))throw Error('OFFER_WITHDRAW_IDENTITY_CHANGED_AFTER_CALL');
 for(let i=0;i<1000;i++)if(!equal(read(pool.add(i*44),44),i===selected.index?afterExpected:before[i]))throw Error('OFFER_WITHDRAW_EFFECT_OUTSIDE_EXACT_STATUS_CLEAR');
 stable();
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  native_return:returned,withdrawal_only:true,signing_completed:false,
  observation:{player_id:p.player_id,team_id:p.team_id,record_index:selected.index,previous_status:'OFFERED',status:'EMPTY',
   registered_terms_preserved:true,other_pool_rows_unchanged:true,player_snapshot_unchanged:true},
  verification_scope:'Same-handler status-clear observation; independent effect/UI/persistence unproven. No quota or response-state restoration is certified',
  direct_game_field_writes:false,automatic_retry:false,other_offer_selection:false
 });
}
