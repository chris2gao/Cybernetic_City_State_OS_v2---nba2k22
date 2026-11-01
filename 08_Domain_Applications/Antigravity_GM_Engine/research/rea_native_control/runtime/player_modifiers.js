// Shared read-only modifier snapshot for original effective Badge Getter checks.
function snapshotPlayerModifiers(player,catalog,indices,layout){
 const root=ptrAt(read(player.add(0xd8),8)),stage=u32(read(player.add(0x354),4));
 const nodes=[],seen=new Set(),sums=Object.fromEntries(indices.map(index=>[index,0]));
 let node=root;
 while(!node.isNull()){
  const identity=node.toString();
  if(seen.has(identity)||nodes.length>=layout.maximum_modifier_nodes)throw Error('PLAYER_MODIFIER_CYCLE_OR_INSPECTION_BOUND');
  seen.add(identity);
  const bytes=read(node,layout.modifier_node_bytes),meta=u32(bytes,0x18);
  nodes.push({pointer:node,bytes});
  if(((meta>>>13)&7)<=(stage&7)&&(meta&0x1fff)===0x1fff){
   for(const index of indices){
    const field=catalog.by_id[index].signed_modifier_field;
    sums[index]+=(u32(bytes,field.dword_offset)<<field.shift_left)>>field.arithmetic_shift_right;
   }
  }
  node=ptrAt(bytes,8);
 }
 return {count:nodes.length,
  effective(index,raw){
   if(!Object.prototype.hasOwnProperty.call(sums,index))throw Error('MODIFIER_FIELD_NOT_OBSERVED');
   return sums[index]===0?raw:Math.max(0,Math.min(4,((sums[index]+raw)<<24)>>24));
  },
  assertStable(){
   if(!ptrAt(read(player.add(0xd8),8)).equals(root)||u32(read(player.add(0x354),4))!==stage)throw Error('PLAYER_MODIFIER_CONTEXT_CHANGED');
   for(const snapshot of nodes)if(!equal(read(snapshot.pointer,layout.modifier_node_bytes),snapshot.bytes))throw Error('PLAYER_MODIFIER_SOURCE_CHANGED');
  }
 };
}
