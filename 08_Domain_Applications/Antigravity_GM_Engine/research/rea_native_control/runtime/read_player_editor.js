// Explicit selected-field read. No setter, private input patch or game write.
function executeAction(){
 const p=request.parameters,projection=p.projection,layout=bindingSpecs['player.editor_read_context'].input_layout;
 const families=['attributes','tendencies','badges','play_types'];
 if(!projection||Object.keys(projection).sort().join('|')!==[...families].sort().join('|')||
   families.some(family=>!Array.isArray(projection[family])||new Set(projection[family]).size!==projection[family].length||
    projection[family].some(name=>typeof name!=='string'||(family==='play_types'?!['1','2','3','4'].includes(name):
     family==='badges'?!layout.badges.fields[name]||layout.badges.fields[name].sentinel_name:
     !layout.stats.families[family][name]||!layout.stats.families[family][name].callable)))||
   !families.some(family=>projection[family].length))throw Error('EXACT_NONPROTECTED_PLAYER_READ_PROJECTION_REQUIRED');
 const t=team(p.team_id),player=rosterPlayer(t,p.player_id);
 const bytes=read(player.add(0x41f),196),raw=new Uint8Array(bytes),slots=u32(read(player.add(0x168),4));
 const flags=u32(read(player.add(0x31c),4)),data={team_id:p.team_id,player_id:p.player_id,projection,
  attributes:{},tendencies:{},badges:{},play_types:{}};
 const badgeIndices=projection.badges.map(name=>layout.badges.fields[name].badge_id);
 const modifiers=badgeIndices.length?snapshotPlayerModifiers(player,layout.badges,badgeIndices,layout):null;
 function stable(){
  if(!rosterPlayer(t,p.player_id).equals(player)||!equal(read(player.add(0x41f),196),bytes)||
    u32(read(player.add(0x168),4))!==slots||u32(read(player.add(0x31c),4))!==flags)throw Error('PLAYER_READ_SNAPSHOT_CHANGED');
  if(modifiers)modifiers.assertStable();
 }
 stable();
 for(const family of ['attributes','tendencies'])for(const name of projection[family]){
  const field=layout.stats.families[family][name],value=call('player.get_stat_ui',player,field.native_index);
  if(!Number.isInteger(value)||value<0||value>255)throw Error('PLAYER_STAT_GETTER_VALUE_UNQUALIFIED');
  if(family==='attributes'&&(value<25||value>99))throw Error('PLAYER_ATTRIBUTE_GETTER_RANGE_MISMATCH');
  data[family][name]=value;
 }
 for(const name of projection.badges){
  const field=layout.badges.fields[name],rawLevel=(raw[field.byte_offset-0x41f]>>>field.shift)&field.mask;
  const effective=call('player.badge_effective_level',player,field.badge_id,0);
  if(effective!==modifiers.effective(field.badge_id,rawLevel))throw Error('PLAYER_READ_EFFECTIVE_GETTER_MISMATCH');
  data.badges[name]={raw_level:rawLevel,effective_level:effective};
 }
 for(const slot of projection.play_types)data.play_types[slot]=(slots>>>((Number(slot)-1)*4))&15;
 stable();
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  read_only:true,snapshot_bracket_unchanged:true,data,
  modifier_nodes_observed:modifiers?modifiers.count:null,
  unknown_scope:['Native save/world/phase identity','unclassified stat fields and child objects','per-mode UI meaning','independent effect and persistence'],
  hidden_potential_emitted:false,arbitrary_memory_dump_emitted:false,
  observation_scope:'Selected original Getter values and packed categories only; host must bind save/snapshot context'
 });
}
