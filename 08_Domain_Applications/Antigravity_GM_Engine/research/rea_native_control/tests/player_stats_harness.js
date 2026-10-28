// Synthetic memory/Native model; the actual stat handler is evaluated unchanged.
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8')),request=input.request,specs=input.bindings,options=input.options||{};
const blocks=[],calls=[],messages=[];
class Pointer{
 constructor(address){this.address=Number(address);}
 add(n){return new Pointer(this.address+n);}
 equals(other){return this.address===other.address;}
 isNull(){return this.address===0;}
}
function allocate(address,size){blocks.push({address,bytes:new Uint8Array(size)});return new Pointer(address);}
function locate(pointer,n){const block=blocks.find(value=>value.address<=pointer.address&&pointer.address+n<=value.address+value.bytes.length);if(!block)throw Error('SYNTHETIC_RANGE');return {block,offset:pointer.address-block.address};}
function set32(pointer,value){const {block,offset}=locate(pointer,4);new DataView(block.bytes.buffer).setUint32(offset,value,true);}
function set8(pointer,value){const {block,offset}=locate(pointer,1);block.bytes[offset]=value;}
function setPointer(pointer,value){const {block,offset}=locate(pointer,8);new DataView(block.bytes.buffer).setBigUint64(offset,BigInt(value.address),true);}
function read(pointer,n){const {block,offset}=locate(pointer,n);return block.bytes.slice(offset,offset+n).buffer;}
const u32=(value)=>new DataView(value).getUint32(0,true),ptrAt=(value)=>new Pointer(Number(new DataView(value).getBigUint64(0,true)));
const base=new Pointer(0x140000000),delegate=allocate(0x10000,16),vtable=allocate(0x20000,0x1700),player=allocate(0x30000,1264),TEAM={kind:'team20'};
const layout=specs['player.stat_context'].input_layout;
allocate(base.address+layout.root_rva,8);setPointer(base.add(layout.root_rva),delegate);setPointer(delegate,vtable);
for(const [slot,target] of Object.entries(layout.required_slots))setPointer(vtable.add(Number(slot)),base.add(target));
if(options.wrong_delegate)setPointer(vtable.add(4680),base.add(1));
for(let i=0;i<156;i++)set8(player.add(0x41f+i),(i*7+50)&255);
set32(player.add(0x31c),0x123456f1);
const initial=Array.from(new Uint8Array(read(player.add(0x41f),156))),flagsBefore=u32(read(player.add(0x31c),4));
const byIndex={};
for(const [family,fields] of Object.entries(layout.fields))for(const [name,spec] of Object.entries(fields))byIndex[spec.native_index]={family,name,...spec};
const context={request,bindingSpecs:specs,base,Uint8Array,Object,Number,Math,read,ptrAt,u32,
 team(id){if(id!==20)throw Error('TEAM_SUBSTITUTED');return TEAM;},
 rosterPlayer(team,id){if(team!==TEAM||id!==55)throw Error('PLAYER_SUBSTITUTED');return player;},
 call(binding,...args){
  if(binding!=='player.set_stat_ui'||args.length!==3||!args[0].equals(player))throw Error('WRONG_NATIVE_ABI_OR_TARGET');
  const spec=byIndex[args[1]];
  if(!spec||!spec.callable)throw Error('UNQUALIFIED_INDEX');
  const values=request.action_id.startsWith('PLAYER_PATCH_')?request.parameters.values:{[request.parameters.field_id]:request.parameters.value};
  if(args[2]!==values[spec.name])throw Error('VALUE_SUBSTITUTION');
  calls.push({binding,index:args[1],value:args[2],field_id:spec.name});
  set8(player.add(spec.offset),spec.family==='attributes'?args[2]*3-75:args[2]);
  if(spec.family==='attributes'&&!options.missing_invalidation)set32(player.add(0x31c),u32(read(player.add(0x31c),4))&0xffffffbf);
  if(options.corrupt_other_field&&calls.length===1)set8(player.add(0x452),0);
  if(options.fail_after===calls.length)throw Error('SYNTHETIC_INTERRUPTED_NATIVE_CALL');
 },
 result(outcome,details){messages.push({outcome,details});}
};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:1000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({initial,after:Array.from(new Uint8Array(read(player.add(0x41f),156))),flagsBefore,
 flagsAfter:u32(read(player.add(0x31c),4)),calls,messages,error}));
