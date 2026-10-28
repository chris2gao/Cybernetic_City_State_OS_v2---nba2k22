// Exact supplied slot edits through the game's four dedicated Native setters.
function executeAction(){
 const p=request.parameters,slots=p.slot_values;
 if(!slots||Array.isArray(slots)||typeof slots!=='object')throw Error('PLAYTYPE_SLOT_OBJECT_REQUIRED');
 const keys=Object.keys(slots).sort();
 if(!keys.length||keys.some(key=>!['1','2','3','4'].includes(key)||
  !Number.isInteger(slots[key])||slots[key]<0||slots[key]>15))throw Error('EXACT_PLAYTYPE_SLOT_AND_ENUM_REQUIRED');
 const t=team(p.team_id),player=rosterPlayer(t,p.player_id);
 const before=u32(read(player.add(0x168),4));
 let expected=before;
 for(const key of keys){
  const shift=(Number(key)-1)*4,mask=15<<shift;
  expected=((expected&~mask)|(slots[key]<<shift))>>>0;
 }
 for(const key of keys)call('player.set_playtype_'+key,player,slots[key]);
 if(!rosterPlayer(t,p.player_id).equals(player))throw Error('PLAYTYPE_PLAYER_IDENTITY_CHANGED');
 const after=u32(read(player.add(0x168),4));
 if(after!==expected)throw Error('PLAYTYPE_NATIVE_VALUE_OR_NEIGHBOR_MISMATCH');
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  team_id:p.team_id,player_id:p.player_id,requested_slots:slots,
  observed_before_slots:Object.fromEntries(keys.map(key=>[key,(before>>>((Number(key)-1)*4))&15])),
  observed_after_slots:Object.fromEntries(keys.map(key=>[key,(after>>>((Number(key)-1)*4))&15])),
  unrequested_slots_and_flags_preserved:true,parent_editor_copy_used:false,
  observation_scope:'Same-handler assigned-slot readback; independent effect, UI and Save/Reload not established'
 });
}
