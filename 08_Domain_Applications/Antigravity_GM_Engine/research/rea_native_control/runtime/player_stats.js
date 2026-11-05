// Native indexed stat setter only; never copy or write the game PLAYER directly.
function executeAction(){
 const p=request.parameters,layout=bindingSpecs['player.stat_context'].input_layout;
 const family=request.action_id.includes('ATTRIBUTE')?'attributes':'tendencies';
 const values=request.action_id.startsWith('PLAYER_PATCH_')?p.values:{[p.field_id]:p.value};
 const fields=layout.fields[family],keys=Object.keys(values).sort();
 if(!keys.length||keys.some(key=>!fields[key]||!fields[key].callable||
  !Number.isInteger(values[key])||values[key]<fields[key].minimum||values[key]>fields[key].maximum))
  throw Error('UNQUALIFIED_PLAYER_STAT_OR_VALUE');
 const delegate=ptrAt(read(base.add(layout.root_rva),8));
 if(delegate.isNull())throw Error('PLAYER_STAT_DELEGATE_NOT_READY');
 const vtable=ptrAt(read(delegate,8));
 if(!Object.entries(layout.required_slots).every(([slot,rva])=>ptrAt(read(vtable.add(Number(slot)),8)).equals(base.add(rva))))
  throw Error('UNRECOVERED_PLAYER_STAT_DELEGATE');
 function stableDelegate(){
  if(!ptrAt(read(base.add(layout.root_rva),8)).equals(delegate)||!ptrAt(read(delegate,8)).equals(vtable)||
   !Object.entries(layout.required_slots).every(([slot,rva])=>ptrAt(read(vtable.add(Number(slot)),8)).equals(base.add(rva))))
   throw Error('PLAYER_STAT_DELEGATE_CHANGED');
 }
 const t=team(p.team_id),player=rosterPlayer(t,p.player_id);
 const before=new Uint8Array(read(player.add(0x41f),156)),expected=Uint8Array.from(before);
 const flagsBefore=u32(read(player.add(0x31c),4)),oldValues={};
 for(const key of keys){
  const spec=fields[key],at=spec.offset-0x41f;
  oldValues[key]=call('player.get_stat_ui',player,spec.native_index);
  if(!Number.isInteger(oldValues[key])||oldValues[key]<0||oldValues[key]>255||
    (family==='attributes'&&(oldValues[key]<25||oldValues[key]>99)))throw Error('PLAYER_STAT_BEFORE_GETTER_UNQUALIFIED');
  expected[at]=family==='attributes'?values[key]*3-75:values[key];
 }
 if(!rosterPlayer(t,p.player_id).equals(player)||!equal(read(player.add(0x41f),156),before.buffer)||u32(read(player.add(0x31c),4))!==flagsBefore)
  throw Error('PLAYER_STAT_CHANGED_DURING_GETTER_PREFLIGHT');
 stableDelegate();
 for(const key of keys)call('player.set_stat_ui',player,fields[key].native_index,values[key]);
 if(!rosterPlayer(t,p.player_id).equals(player))throw Error('PLAYER_STAT_TARGET_CHANGED');
 const after=new Uint8Array(read(player.add(0x41f),156));
 if(!after.every((value,index)=>value===expected[index]))throw Error('PLAYER_STAT_VALUE_OR_OTHER_FIELD_MISMATCH');
 const flagsAfter=u32(read(player.add(0x31c),4));
 const expectedFlags=family==='attributes'?(flagsBefore&0xffffffbf)>>>0:flagsBefore;
 if(flagsAfter!==expectedFlags)throw Error('PLAYER_STAT_CACHE_FLAG_MISMATCH');
 const observedAfter={};
 for(const key of keys){
  observedAfter[key]=call('player.get_stat_ui',player,fields[key].native_index);
  if(observedAfter[key]!==values[key])throw Error('PLAYER_STAT_AFTER_GETTER_MISMATCH');
 }
 if(!rosterPlayer(t,p.player_id).equals(player)||!equal(read(player.add(0x41f),156),expected.buffer)||u32(read(player.add(0x31c),4))!==expectedFlags)
  throw Error('PLAYER_STAT_CHANGED_DURING_GETTER_READBACK');
 stableDelegate();
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  team_id:p.team_id,player_id:p.player_id,field_family:family,
  requested_values:values,observed_before_values:oldValues,observed_after_values:observedAfter,
  original_native_getter_used:true,
  unrequested_stat_bytes_preserved:true,native_cache_flag_effect_observed:family==='attributes',
  parent_editor_copy_used:false,automatic_clamping:false,
  observation_scope:'Same-handler assigned values only; independent effect, UI, simulation and Save/Reload remain unverified'
 });
}
