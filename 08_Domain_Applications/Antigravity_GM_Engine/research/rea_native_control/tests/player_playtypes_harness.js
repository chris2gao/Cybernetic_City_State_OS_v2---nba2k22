// Offline Native ABI model; the actual deferred handler is evaluated unchanged.
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8')),request=input.request,options=input.options||{};
const memory=new ArrayBuffer(512),view=new DataView(memory),calls=[],messages=[];
view.setUint32(0x168,0xa5c31240,true);
const before=view.getUint32(0x168,true);
class Pointer{
 constructor(offset=0){this.offset=offset;}
 add(value){return new Pointer(this.offset+value);}
 equals(other){return other instanceof Pointer&&this.offset===other.offset;}
}
const PLAYER=new Pointer(),TEAM={identity:'team20'};
const context={request,Object,Array,Number,
 team(id){if(id!==20)throw Error('TEAM_SUBSTITUTED');return TEAM;},
 rosterPlayer(team,id){if(team!==TEAM||id!==55)throw Error('PLAYER_SUBSTITUTED');return PLAYER;},
 read(pointer,n){if(!(pointer instanceof Pointer)||pointer.offset!==0x168||n!==4)throw Error('UNEXPECTED_MEMORY_READ');return memory.slice(0x168,0x16c);},
 u32(value){return new DataView(value).getUint32(0,true);},
 call(binding,...args){
  const match=/^player\.set_playtype_([1-4])$/.exec(binding);
  if(!match||args.length!==2||!args[0].equals(PLAYER))throw Error('WRONG_NATIVE_ABI_OR_TARGET');
  const slot=Number(match[1]),value=args[1];
  if(value!==request.parameters.slot_values[String(slot)])throw Error('VALUE_SUBSTITUTED');
  calls.push({binding,player_uid:55,value});
  const shift=(slot-1)*4,word=view.getUint32(0x168,true);
  view.setUint32(0x168,((word&~(15<<shift))|((value&15)<<shift))>>>0,true);
  if(options.corrupt_neighbor&&calls.length===1)view.setUint32(0x168,view.getUint32(0x168,true)^0x40000,true);
  if(options.fail_after===calls.length)throw Error('SYNTHETIC_INTERRUPTED_NATIVE_CALL');
 },
 result(outcome,details){messages.push({outcome,details});}
};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:1000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({before,after:view.getUint32(0x168,true),calls,messages,error}));
