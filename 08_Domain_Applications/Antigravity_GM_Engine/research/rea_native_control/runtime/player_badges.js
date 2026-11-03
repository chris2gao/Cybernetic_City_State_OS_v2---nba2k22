// Original flag0 Badge setter, exact caller-approved coupled before/after states.
function executeAction(){
 const p=request.parameters,layout=bindingSpecs['player.badge_context'].input_layout;
 const fields=layout.catalog.fields,field=fields[p.field_id];
 if(!field||field.sentinel_name||!Number.isInteger(p.value)||p.value<0||p.value>field.maximum)
  throw Error('UNQUALIFIED_BADGE_FIELD_OR_VALUE');
 const group=layout.catalog.coupled_groups.find(group=>group.includes(p.field_id))||[p.field_id];
 for(const key of ['expected_before','expected_after']){
  const values=p[key];
  if(!values||Array.isArray(values)||Object.keys(values).sort().join('|')!==[...group].sort().join('|')||
    group.some(name=>!Number.isInteger(values[name])||values[name]<0||values[name]>fields[name].maximum))
   throw Error('EXACT_COUPLED_BADGE_STATE_REQUIRED');
 }
 if(p.expected_after[p.field_id]!==p.value)throw Error('BADGE_REQUEST_AFTER_DISAGREEMENT');
 const delegate=ptrAt(read(base.add(layout.root_rva),8));
 if(delegate.isNull())throw Error('BADGE_DELEGATE_NOT_READY');
 const vtable=ptrAt(read(delegate,8));
 if(!Object.entries(layout.required_slots).every(([slot,rva])=>ptrAt(read(vtable.add(Number(slot)),8)).equals(base.add(rva))))
  throw Error('UNRECOVERED_BADGE_DELEGATE');
 const t=team(p.team_id),player=rosterPlayer(t,p.player_id);
 const before=new Uint8Array(read(player.add(0x41f),196)),expected=Uint8Array.from(before);
 const flagsBefore=u32(read(player.add(0x31c),4)),probes=[5,21,24];
 const modifiers=snapshotPlayerModifiers(player,layout.catalog,probes,layout);
 const raw=index=>{const spec=layout.catalog.by_id[index];return (before[spec.byte_offset-0x41f]>>>spec.shift)&spec.mask;};
 const effective={};
 for(const index of probes){
  effective[index]=modifiers.effective(index,raw(index));
 }
 for(const name of group)if(raw(fields[name].badge_id)!==p.expected_before[name])throw Error('BADGE_EXPECTED_BEFORE_MISMATCH');
 const predicted={...p.expected_before},changed=raw(field.badge_id)!==p.value;
 if(changed){
  if(p.value>0&&layout.catalog.exclusive_groups.some(group=>group.includes(p.field_id))){
   if(field.badge_id===5&&effective[21]>0)throw Error('BADGE_ORIGINAL_RULE_BLOCKS_REQUEST');
   for(const name of group)predicted[name]=name===p.field_id?p.value:0;
  }else if(p.value>0&&[21,24,25].includes(field.badge_id)){
   const state=field.badge_id===21?(effective[24]>0?3:2):field.badge_id===24?(effective[21]>0?3:1):4;
   if((state===2||state===3)&&effective[5]>0)throw Error('BADGE_ORIGINAL_TRAIT_ASSERTION_PRECONDITION');
   for(const name of group)predicted[name]=0;
   if(state===1||state===3)predicted.Unpredictable=1;
   if(state===2||state===3)predicted.Expressive=1;
   if(state===4)predicted.LaidBack=1;
  }else predicted[p.field_id]=p.value;
 }
 if(group.some(name=>predicted[name]!==p.expected_after[name]))throw Error('BADGE_EXPLICIT_AFTER_DIFFERS_FROM_ORIGINAL_RULES');
 for(const name of group){const spec=fields[name],at=spec.byte_offset-0x41f;expected[at]=(expected[at]&~(spec.mask<<spec.shift))|(predicted[name]<<spec.shift);}
 function stable(){
  if(!rosterPlayer(t,p.player_id).equals(player)||
    !ptrAt(read(base.add(layout.root_rva),8)).equals(delegate)||!ptrAt(read(delegate,8)).equals(vtable)||
    !Object.entries(layout.required_slots).every(([slot,rva])=>ptrAt(read(vtable.add(Number(slot)),8)).equals(base.add(rva))))throw Error('BADGE_CONTEXT_CHANGED');
  modifiers.assertStable();
 }
 stable();
 for(const index of probes)if(call('player.badge_effective_level',player,index,0)!==effective[index])throw Error('BADGE_EFFECTIVE_GETTER_MODEL_MISMATCH');
 stable();
 if(!equal(read(player.add(0x41f),196),before.buffer)||u32(read(player.add(0x31c),4))!==flagsBefore)throw Error('BADGE_STATE_CHANGED_DURING_PREFLIGHT');
 call('player.set_badge',player,field.badge_id,p.value,0);
 stable();
 if(!equal(read(player.add(0x41f),196),expected.buffer))throw Error('BADGE_ASSIGNED_OR_UNREQUESTED_FIELD_MISMATCH');
 const expectedFlags=changed?(flagsBefore&0xffffffbf)>>>0:flagsBefore;
 if(u32(read(player.add(0x31c),4))!==expectedFlags)throw Error('BADGE_CACHE_FLAG_MISMATCH');
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  team_id:p.team_id,player_id:p.player_id,field_id:p.field_id,value:p.value,
  observed_before_values:p.expected_before,observed_after_values:predicted,
  original_rule_flag:0,explicit_coupled_state_matched:true,unrequested_player_stat_badge_bits_preserved:true,
  modifier_nodes_observed:modifiers.count,original_unchanged_primary_return:!changed,
  observation_scope:'Same-handler field and modifier readback only; independent effect, UI, mode semantics and Save/Reload unverified'
 });
}
