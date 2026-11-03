// No game code runs. Fake original service owns the only allowed mutation.
const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const request=input.request,bindingSpecs=input.bindings,o=input.options||{},calls=[],messages=[];
const layout=bindingSpecs['sign.withdraw_context'].input_layout,blocks=[],imageBase=0x140000000;
let poolReads=0,playerReads=0,teamReads=0,withdrawals=0,forbiddenWrites=0;
class Pointer{
 constructor(value){this.value=Number(value);}add(n){return new Pointer(this.value+Number(n));}
 equals(other){return other instanceof Pointer&&other.value===this.value;}isNull(){return !this.value;}
 writeByteArray(){forbiddenWrites++;throw Error('GAME_WRITE_FORBIDDEN');}
}
const ptr=n=>new Pointer(typeof n==='string'?Number(n):n),base=ptr(imageBase);
function block(at,n){const row={at,bytes:Buffer.alloc(n)};blocks.push(row);return row;}
function set64(row,at,value){row.bytes.writeBigUInt64LE(BigInt(value),at);}
function locate(p,n){const row=blocks.find(b=>p>=b.at&&p+n<=b.at+b.bytes.length);if(!row)throw Error('UNEXPECTED_ADDRESS');return row;}
const periodAt=0x10000,franchiseAt=0x100000,playerAt=0x20000,teamAt=0x30000;
const globalPeriod=block(imageBase+layout.roots.period.global_rva,8),globalPool=block(imageBase+layout.roots.pool.global_rva,8);
set64(globalPeriod,0,o.null_period?0:periodAt);set64(globalPool,0,o.null_pool?0:franchiseAt);
const period=block(periodAt,32);period.bytes.writeUInt32LE(o.period===undefined?22:o.period,12);
const player=block(playerAt,1264);player.bytes.writeUInt16LE(o.uid_mismatch?56:55,0xf4);
const poolAt=franchiseAt+layout.schema.pool.offset,pool=block(poolAt,44000);
for(const row of input.records||[])Buffer.from(row.hex,'hex').copy(pool.bytes,row.index*44);
const initial=Buffer.from(pool.bytes);
function read(p,n){
 const row=locate(p.value,n),at=p.value-row.at;
 if(row===pool&&n===44&&poolReads++===1000&&o.pool_changes_before)pool.bytes[36]^=1;
 if(row===player&&++playerReads===2&&o.player_changes_before)player.bytes[0x354]^=1;
 return Uint8Array.from(row.bytes.subarray(at,at+n)).buffer;
}
function call(id,...args){
 calls.push(id);if(calls.length>3)throw Error('DIRECT_CALL_BUDGET');
 if(id==='player.by_id'){
  if(args.length!==1||args[0]!==55)throw Error('UID_ARGS');
  if(o.period_changes_before&&withdrawals===0)period.bytes.writeUInt32LE(29,12);
  return ptr(o.player_null?0:playerAt);
 }
 if(id!=='sign.cancel_pending_offer')throw Error('UNEXPECTED_NATIVE_CALL');
 withdrawals++;if(withdrawals!==1||args.length!==2||args[1]!==0||args[0].value<poolAt||args[0].value>=poolAt+44000||(args[0].value-poolAt)%44)throw Error('ORIGINAL_ABI_ARGS');
 const at=args[0].value-poolAt;
 if(!o.no_effect){
  const selected=o.wrong_row?at+44:at,word=pool.bytes.readUInt32LE(selected+32);
  pool.bytes.writeUInt32LE((word&~0x3c0000)>>>0,selected+32);
  if(o.wrong_status)pool.bytes.writeUInt32LE(((word&~0x3c0000)|(8<<18))>>>0,selected+32);
 }
 if(o.terms_change_after)pool.bytes[at+4]^=1;
 if(o.other_record_change_after)pool.bytes[36]^=1;
 if(o.player_changes_after)player.bytes[0x354]^=1;
 if(o.root_changes_after)set64(globalPool,0,franchiseAt+8);
 if(o.period_changes_after)period.bytes.writeUInt32LE(29,12);
 return o.native_return===undefined?1:o.native_return;
}
const context={request,bindingSpecs,base,ptr,DataView,Uint8Array,Object,Array,Number,JSON,Error,read,call,
 u16:(b,at=0)=>new DataView(b).getUint16(at,true),u32:(b,at=0)=>new DataView(b).getUint32(at,true),
 ptrAt:(b,at=0)=>ptr(Number(new DataView(b).getBigUint64(at,true))),equal:(a,b)=>Buffer.from(a).equals(Buffer.from(b)),
 team(id){teamReads++;if(id!==20||o.team_missing)throw Error('TEAM_NOT_FOUND');return ptr(o.team_changes&&teamReads>1?teamAt+8:teamAt);},
 result(outcome,details){messages.push({outcome,details});}};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:3000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({error,messages,calls,withdrawals,poolReads,forbiddenWrites,poolUnchanged:initial.equals(pool.bytes),
 selectedAfter:pool.bytes.subarray(7*44,8*44).toString('hex')}));
