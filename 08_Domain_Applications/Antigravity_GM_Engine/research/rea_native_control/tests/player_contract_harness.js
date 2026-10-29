const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const request=input.request,bindingSpecs=input.bindings,options=input.options||{},messages=[],calls=[];
const memory=Uint8Array.from(Buffer.from(input.player_hex,'hex')),original=Array.from(memory);
class Pointer{constructor(address){this.address=address;}equals(p){return this.address===p.address;}isNull(){return this.address===0;}add(n){return new Pointer(this.address+n);}}
const player=new Pointer(0x10000),current=new Pointer(options.no_current?0:0x20000),owner=new Pointer(options.no_owner?0:0x30000);
new DataView(memory.buffer).setBigUint64(0x60,BigInt(current.address),true);
new DataView(memory.buffer).setBigUint64(0xa8,BigInt(owner.address),true);
const before=Array.from(memory);let resolutions=0;
const u16=(b,o=0)=>new DataView(b).getUint16(o,true),u32=(b,o=0)=>new DataView(b).getUint32(o,true);
function set32(at,value){new DataView(memory.buffer).setUint32(at,value,true);}
const context={request,bindingSpecs,Number,Object,Set,Uint8Array,Math,u16,u32,playerContractFields:input.contract_fields||[],text(){return '';},
 ptrAt(b,o=0){return new Pointer(Number(new DataView(b).getBigUint64(o,true)));},
 read(p,n){
  if(p.equals(player)&&n===1264)return memory.slice().buffer;
  if(n===2&&[current.address+0xca8,owner.address+0xca8].includes(p.address)){
   const out=new ArrayBuffer(2);new DataView(out).setUint16(0,options.team_id_changes&&resolutions>1?21:20,true);return out;
  }
  throw Error('UNEXPECTED_SYNTHETIC_READ');
 },
 call(binding,...args){
  calls.push({binding,args:args.map(value=>value instanceof Pointer?'PLAYER':value)});
  if(binding==='player.by_id'){
   if(args.length!==1||args[0]!==55)throw Error('UID_SUBSTITUTED');resolutions++;
   if(options.missing)return new Pointer(0);
   if(options.changed_identity&&resolutions>1)return new Pointer(0x10008);
   return player;
  }
  if(!args[0].equals(player))throw Error('WRONG_PLAYER');
  if(binding==='player.get_salary'){
   if(args.length!==2||args[1]<0||args[1]>5)throw Error('SALARY_ABI');
   const value=u32(memory.buffer,0x1a4+args[1]*4)&0x7fffffff;
   if(args[1]===5){
    if(options.salary_changes)set32(0x1a4,901);
    if(options.mark_changes)set32(0x130,u32(memory.buffer,0x130)^0x200);
    if(options.unrelated_changes)memory[0x41f]^=1;
   }
   return value+(options.wrong_salary?1:0);
  }
  if(binding==='player.get_remaining_contract_years'){
   if(args.length!==2||![0,1].includes(args[1]))throw Error('YEARS_ABI');
   const base=(u32(memory.buffer,0x32c)>>>18)&31,extension=(u32(memory.buffer,0x340)>>>15)&7;
   const option=(u32(memory.buffer,0x314)>>>28)&3,count=[0,1,1,2][option];
   const total=base+extension+(args[1]?count:0);
   if(total>6)throw Error('ORIGINAL_ASSERTION_WOULD_EXECUTE');
   return total+(options.wrong_years?1:0);
  }
  throw Error('UNEXPECTED_BUSINESS_CALL');
 },
 result(outcome,details){messages.push({outcome,details});}};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:3000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({error,messages,calls,unchanged:JSON.stringify(before)===JSON.stringify(Array.from(memory))}));
