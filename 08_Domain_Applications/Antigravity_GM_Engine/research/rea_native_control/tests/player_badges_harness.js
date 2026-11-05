// Synthetic Native flag0 rules and modifier memory; actual handler runs unchanged.
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8')),request=input.request,specs=input.bindings,options=input.options||{};
const blocks=[],calls=[],messages=[];
class Pointer{
 constructor(address){this.address=Number(address);}
 add(n){return new Pointer(this.address+n);}
 equals(other){return this.address===other.address;}
 isNull(){return this.address===0;}
 toString(){return this.address.toString(16);}
}
function allocate(address,size){blocks.push({address,bytes:new Uint8Array(size)});return new Pointer(address);}
function locate(pointer,n){const block=blocks.find(block=>block.address<=pointer.address&&pointer.address+n<=block.address+block.bytes.length);if(!block)throw Error('SYNTHETIC_RANGE');return {block,at:pointer.address-block.address};}
function set8(pointer,value){const {block,at}=locate(pointer,1);block.bytes[at]=value;}
function set32(pointer,value){const {block,at}=locate(pointer,4);new DataView(block.bytes.buffer).setUint32(at,value,true);}
function setPointer(pointer,value){const {block,at}=locate(pointer,8);new DataView(block.bytes.buffer).setBigUint64(at,BigInt(value.address),true);}
function read(pointer,n){const {block,at}=locate(pointer,n);return block.bytes.slice(at,at+n).buffer;}
const u32=(value,at=0)=>new DataView(value).getUint32(at,true),ptrAt=(value,at=0)=>new Pointer(Number(new DataView(value).getBigUint64(at,true)));
const equal=(a,b)=>Buffer.from(a).equals(Buffer.from(b));
const base=new Pointer(0x140000000),delegate=allocate(0x10000,16),vtable=allocate(0x20000,0x1700),player=allocate(0x30000,1264),TEAM={kind:'team20'};
const reading=request.action_id==='READ_PLAYER_EDITOR_STATE';
const sourceLayout=specs[reading?'player.editor_read_context':'player.badge_context'].input_layout;
const layout=reading?{...sourceLayout,catalog:sourceLayout.badges}:sourceLayout,fields=layout.catalog.by_id;
if(!reading){allocate(base.address+layout.root_rva,8);setPointer(base.add(layout.root_rva),delegate);setPointer(delegate,vtable);
 for(const [slot,target] of Object.entries(layout.required_slots))setPointer(vtable.add(Number(slot)),base.add(target));
 if(options.wrong_delegate)setPointer(vtable.add(4472),base.add(1));}
for(let i=0;i<156;i++)set8(player.add(0x41f+i),(i*11+17)&255);
const occupied=new Uint8Array(40);
for(const field of fields)occupied[field.byte_offset-0x4bb]|=field.mask<<field.shift;
for(let i=0;i<40;i++)set8(player.add(0x4bb+i),(~occupied[i])&255);
const raw=id=>{const field=fields[id];return new Uint8Array(read(player.add(field.byte_offset),1))[0]>>>field.shift&field.mask;};
function assign(id,value){const field=fields[id],at=player.add(field.byte_offset),old=new Uint8Array(read(at,1))[0];set8(at,(old&~(field.mask<<field.shift))|(value<<field.shift));}
for(const [name,value] of Object.entries(input.initial||{}))assign(layout.catalog.fields[name].badge_id,value);
set32(player.add(0x31c),0x123456f1);set32(player.add(0x354),options.stage||0);
set32(player.add(0x168),options.play_types_word===undefined?0xabcddcba:options.play_types_word);
const statsByIndex={};
if(reading)for(const [family,items] of Object.entries(layout.stats.families))for(const [name,field] of Object.entries(items)){
 statsByIndex[field.native_index]={family,name,...field};
 if(Object.prototype.hasOwnProperty.call(options.stat_raw||{},name))set8(player.add(field.offset),options.stat_raw[name]);
}
const nodeInputs=options.nodes||[],nodes=nodeInputs.map((_,i)=>allocate(0x40000+i*0x100,layout.modifier_node_bytes));
for(let i=0;i<nodes.length;i++){
 const spec=nodeInputs[i];setPointer(nodes[i].add(8),nodes[i+1]||new Pointer(0));
 set32(nodes[i].add(0x18),spec.metadata===undefined?0x1fff:spec.metadata);
 for(const [name,value] of Object.entries(spec.values||{})){
  const field=layout.catalog.fields[name].signed_modifier_field,at=nodes[i].add(field.dword_offset),shift=field.arithmetic_shift_right-field.shift_left,mask=(1<<field.signed_width)-1;
  const old=u32(read(at,4));set32(at,(old&~(mask<<shift))|((value&mask)<<shift));
 }
}
if(options.cycle&&nodes.length)setPointer(nodes[nodes.length-1].add(8),nodes[0]);
setPointer(player.add(0xd8),nodes[0]||new Pointer(0));
function effective(id){
 let sum=0;const name=fields[id].internal_name;
 for(const node of nodeInputs){const meta=node.metadata===undefined?0x1fff:node.metadata;if(((meta>>>13)&7)<=((options.stage||0)&7)&&((meta&0x1fff)===0x1fff))sum+=(node.values||{})[name]||0;}
 if(sum===0)return raw(id);
 const signed=((raw(id)+sum)&255)>127?((raw(id)+sum)&255)-256:((raw(id)+sum)&255);
 return Math.max(0,Math.min(4,signed));
}
const initial=Array.from(new Uint8Array(read(player.add(0x41f),196))),flagsBefore=u32(read(player.add(0x31c),4));
const context={request,bindingSpecs:specs,base,Uint8Array,Object,Number,Math,Set,read,ptrAt,u32,equal,
 team(id){if(id!==20)throw Error('TEAM_SUBSTITUTED');return TEAM;},
 rosterPlayer(team,id){if(team!==TEAM||id!==55)throw Error('PLAYER_SUBSTITUTED');
  const changed=(options.roster_changed_after&&calls.some(row=>row.binding==='player.set_badge'))||
   (options.roster_changed_during_getters&&calls.some(row=>['player.badge_effective_level','player.get_stat_ui'].includes(row.binding)));
  return changed?new Pointer(1):player;},
 call(binding,...args){
  if(!args[0].equals(player))throw Error('WRONG_NATIVE_PLAYER');
  if(binding==='player.get_stat_ui'){
   if(!reading||args.length!==2||!statsByIndex[args[1]])throw Error('WRONG_UI_GETTER_ABI_OR_INDEX');
   const field=statsByIndex[args[1]],raw=new Uint8Array(read(player.add(field.offset),1))[0];
   calls.push({binding,index:args[1]});
   if(options.state_changes_during_getter)set8(player.add(0x452),0);
   if(Object.prototype.hasOwnProperty.call(options.ui_values||{},field.name))return options.ui_values[field.name];
   return field.family==='attributes'?Math.max(25,Math.min(99,Math.round(Math.fround(Math.fround(raw)*Math.fround(1/3))+25))):raw;
  }
  if(binding==='player.badge_effective_level'){
   if(args.length!==3||args[2]!==0)throw Error('WRONG_EFFECTIVE_ABI_OR_NORMALIZATION');
   calls.push({binding,index:args[1]});const value=effective(args[1]);
   if(options.state_changes_during_getter&&calls.length===1)set8(player.add(0x452),0);
   if(options.modifier_changed_during_getter&&nodes.length)set32(nodes[0].add(0x18),0);
   return value+(options.wrong_effective?1:0);
  }
  if(reading)throw Error('READ_ATTEMPTED_MUTATION');
  if(binding!=='player.set_badge'||args.length!==4||args[3]!==0)throw Error('ORIGINAL_RULE_FLAG_OR_ABI_BYPASS');
  const id=args[1],value=args[2];calls.push({binding,index:id,value,flag:args[3]});
  if(raw(id)!==value){
   const exclusive=[[5,8],[9,12],[13,16],[17,20]].find(group=>group.includes(id));
   if(value>0&&exclusive){
    if(id!==5||effective(21)<=0)for(const member of exclusive)assign(member,member===id?value:0);
   }else if(value>0&&[21,24,25].includes(id)){
    const state=id===21?(effective(24)>0?3:2):id===24?(effective(21)>0?3:1):4;
    if((state===2||state===3)&&effective(5)>0)throw Error('ORIGINAL_NATIVE_ASSERTION');
    for(const member of [21,24,25])assign(member,0);
    if(state===1||state===3)assign(24,1);if(state===2||state===3)assign(21,1);if(state===4)assign(25,1);
   }else assign(id,value);
   if(!options.missing_invalidation)set32(player.add(0x31c),flagsBefore&0xffffffbf);
  }
  if(options.corrupt_unrequested)set8(player.add(0x440),0);
  if(options.corrupt_padding)set8(player.add(0x4e2),new Uint8Array(read(player.add(0x4e2),1))[0]^0x80);
  if(options.modifier_changed_after_set&&nodes.length)set32(nodes[0].add(0x18),0);
  if(options.fail_after_set)throw Error('SYNTHETIC_NATIVE_INTERRUPTION');
 },
 result(outcome,details){messages.push({outcome,details});}
};
let error=null;
try{const path=require('path'),helper=path.join(path.dirname(process.argv[2]),'player_modifiers.js');
 vm.runInNewContext(fs.readFileSync(helper,'utf8')+'\n'+fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:1000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({initial,after:Array.from(new Uint8Array(read(player.add(0x41f),196))),flagsBefore,
 flagsAfter:u32(read(player.add(0x31c),4)),calls,messages,error}));
