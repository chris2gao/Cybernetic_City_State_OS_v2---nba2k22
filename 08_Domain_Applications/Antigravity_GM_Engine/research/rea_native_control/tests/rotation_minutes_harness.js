// Synthetic memory and Native-call model. The real deferred JS handler is run.
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const request=input.request,specs=input.bindings,options=input.options||{};
const blocks=[],calls=[],messages=[];
class Pointer{
 constructor(address){this.address=Number(address);}
 add(n){return new Pointer(this.address+n);}
 equals(other){return this.address===other.address;}
 isNull(){return this.address===0;}
}
function allocate(address,size){const block={address,bytes:new Uint8Array(size)};blocks.push(block);return new Pointer(address);}
function locate(pointer,n){const block=blocks.find(b=>b.address<=pointer.address&&pointer.address+n<=b.address+b.bytes.length);if(!block)throw Error('SYNTHETIC_RANGE');return {block,offset:pointer.address-block.address};}
function set32(pointer,value){const {block,offset}=locate(pointer,4);new DataView(block.bytes.buffer).setUint32(offset,value,true);}
function set16(pointer,value){const {block,offset}=locate(pointer,2);new DataView(block.bytes.buffer).setUint16(offset,value,true);}
function set8(pointer,value){const {block,offset}=locate(pointer,1);block.bytes[offset]=value;}
function setPointer(pointer,value){const {block,offset}=locate(pointer,8);new DataView(block.bytes.buffer).setBigUint64(offset,BigInt(value.address),true);}
function read(pointer,n){const {block,offset}=locate(pointer,n);return block.bytes.slice(offset,offset+n).buffer;}
const u16=(value,offset=0)=>new DataView(value).getUint16(offset,true),u32=(value,offset=0)=>new DataView(value).getUint32(offset,true);
const ptrAt=(value,offset=0)=>new Pointer(Number(new DataView(value).getBigUint64(offset,true)));
const base=new Pointer(0x140000000),delegate=allocate(0x10000,16),vtable=allocate(0x20000,0x1700);
const team=allocate(0x30000,4696),player=allocate(0x40000,512),other=allocate(0x50000,512),franchise=allocate(0x60000,0x13e70);
allocate(base.address+specs['rotation.current_delegate'].input_layout.root_rva,8);
setPointer(base.add(specs['rotation.current_delegate'].input_layout.root_rva),options.missing_delegate?new Pointer(0):delegate);
setPointer(delegate,vtable);
for(const [slot,rva] of Object.entries(specs['rotation.current_delegate'].input_layout.allowed_profiles[options.profile_index||0].slots))setPointer(vtable.add(Number(slot)),base.add(rva));
if(options.career_clamp)setPointer(vtable.add(0x16d8),base.add(0x11b2900));
setPointer(team,player);setPointer(team.add(8),other);
set16(player.add(0xf4),55);set16(other.add(0xf4),56);
set32(player.add(0xf8),0xa735aa91);set32(other.add(0xf8),0x753aa917);
set8(franchise.add(0x11ff9),1);
const initial=[u32(read(player.add(0xf8),4)),u32(read(other.add(0xf8),4))];
const context={request,bindingSpecs:specs,base,Uint8Array,Number,Object,read,ptrAt,u16,u32,
 team(id){if(id!==20)throw Error('TEAM_SUBSTITUTED');return team;},
 rosterPlayer(t,id){if(!t.equals(team))throw Error('TEAM_SUBSTITUTED');if(id===55)return player;if(id===56)return other;throw Error('PLAYER_SUBSTITUTED');},
 franchiseRecord(id){if(id!==20)throw Error('TEAM_SUBSTITUTED');return {pointer:franchise,index:7};},
 call(binding,...args){
  calls.push({binding,arguments:args.map(v=>v instanceof Pointer?({identity:v.equals(team)?'team':v.equals(player)?'player55':v.equals(other)?'player56':v.equals(delegate)?'delegate':'unexpected'}):v)});
  if(binding==='rotation.franchise_team_index'){
   if(args.length!==1||!args[0].equals(team))throw Error('INDEX_ABI');return options.wrong_index?255:7;
  }
  if(binding==='rotation.set_player_minutes'){
   if(args.length!==3||!args[0].equals(delegate)||![player,other].some(p=>p.equals(args[1]))||args[2]!==request.parameters.minutes)throw Error('SETTER_ABI_OR_VALUE_SUBSTITUTED');
   const word=u32(read(args[1].add(0xf8),4));
   set32(args[1].add(0xf8),((word&0xfe03ffff)|((options.wrong_value?1:args[2])<<18))>>>0);
   if(options.other_mutation)set32(other.add(0xf8),0);return;
  }
  if(binding==='rotation.mark_team_change'){
   if(args.length!==3||!args[0].equals(team)||args[1]!==1||args[2]!==0)throw Error('TEAM_CHANGE_ABI');
   if(options.refresh_failure)throw Error('SYNTHETIC_NATIVE_REFRESH_FAILURE');
   set8(franchise.add(0x11ff9),0);return;
  }
  throw Error('UNEXPECTED_NATIVE_CALL');
 },
 result(outcome,details){messages.push({outcome,details});}
};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:1000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({initial,after:[u32(read(player.add(0xf8),4)),u32(read(other.add(0xf8),4))],calls,messages,error}));
