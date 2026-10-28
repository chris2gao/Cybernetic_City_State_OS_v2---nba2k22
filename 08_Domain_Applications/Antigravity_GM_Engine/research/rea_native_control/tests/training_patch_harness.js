// Offline memory model ONLY: execute the real handler, never attach a process.
const fs=require('fs'),vm=require('vm');
const request=JSON.parse(fs.readFileSync(0,'utf8'));
const before=Uint8Array.from({length:56},(_,i)=>(i*13+7)&255);
const original=Uint8Array.from(before),calls=[],messages=[];
let dailyMissing=request.parameters.__missing===true;
delete request.parameters.__missing;
class OwnedPointer{
 constructor(bytes,offset=0){this.bytes=bytes;this.offset=offset;}
 add(n){return new OwnedPointer(this.bytes,this.offset+n);}
 writeByteArray(value){const data=new Uint8Array(value);if(this.offset+data.length>this.bytes.length)throw Error('PRIVATE_OVERFLOW');this.bytes.set(data,this.offset);}
 writeFloat(value){if(this.offset+4>this.bytes.length)throw Error('PRIVATE_OVERFLOW');new DataView(this.bytes.buffer).setFloat32(this.offset,value,true);}
 writeU8(value){if(this.offset>=this.bytes.length)throw Error('PRIVATE_OVERFLOW');this.bytes[this.offset]=value;}
}
const TEAM={kind:'synthetic-team'},DAILY={isNull:()=>dailyMissing};
let input=null;
const context={request,Uint8Array,Memory:{alloc(n){if(n!==64)throw Error('UNEXPECTED_PRIVATE_SIZE');return new OwnedPointer(new Uint8Array(n));}},
 team(id){if(id!==20)throw Error('WRONG_TEAM');return TEAM;},
 read(pointer,n){if(pointer!==DAILY||n!==56)throw Error('UNEXPECTED_GAME_READ');return Uint8Array.from(before).buffer;},
 call(binding,...args){
  calls.push(binding);
  if(args[0]!==TEAM||args[1]!==request.parameters.date)throw Error('TARGET_OR_DATE_SUBSTITUTION');
  if(binding==='training.daily_by_date')return DAILY;
  if(binding!=='training.set_team_on_date'||!(args[2] instanceof OwnedPointer))throw Error('UNEXPECTED_NATIVE_CALL');
  input=Array.from(args[2].bytes);return undefined;
 },
 result(outcome,details){messages.push({outcome,details});}
};
const source=fs.readFileSync(process.argv[2],'utf8');
let error=null;
try{vm.runInNewContext(source+'\nexecuteAction();',context,{timeout:1000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({before:Array.from(original),after_game_memory:Array.from(before),input,calls,messages,error}));
