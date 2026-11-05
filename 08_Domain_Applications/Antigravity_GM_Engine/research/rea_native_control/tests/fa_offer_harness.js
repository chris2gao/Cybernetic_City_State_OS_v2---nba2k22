// Offline fake address space. Only the simulated original service can write game blocks.
const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const request=input.request,bindingSpecs=input.bindings,o=input.options||{},messages=[],calls=[];
const layout=bindingSpecs['sign.fa_offer_context'].input_layout,schema=layout.schema,blocks=[];
let offers=0,poolReads=0,playerReads=0,privateInput=null,forbiddenWrites=0;
const imageBase=0x140000000;
class Pointer{
 constructor(value){this.value=Number(value);}add(n){return new Pointer(this.value+Number(n));}
 equals(p){return p instanceof Pointer&&this.value===p.value;}isNull(){return this.value===0;}
 writeByteArray(raw){const row=locate(this.value,raw.byteLength);if(!row.private){forbiddenWrites++;throw Error('GAME_WRITE_FORBIDDEN');}Buffer.from(raw).copy(row.bytes,this.value-row.at);}
}
const ptr=n=>new Pointer(typeof n==='string'?Number(n):n),base=ptr(imageBase);
function block(at,n,private=false){const row={at,bytes:Buffer.alloc(n),private};blocks.push(row);return row;}
function locate(at,n){const row=blocks.find(b=>at>=b.at&&at+n<=b.at+b.bytes.length);if(!row)throw Error('UNEXPECTED_READ_'+at.toString(16)+'_'+n);return row;}
function set64(row,offset,value){row.bytes.writeBigUInt64LE(BigInt(value),offset);}
const addresses={period:0x10000,pool:0x100000,rules:0x20000,tuning:0x4000000,delegate:0x30000};
const roots={};
for(const [name,at] of Object.entries(addresses)){
 const global=block(imageBase+layout.roots[name].global_rva,8);set64(global,0,o.null_root===name?0:at);roots[name]=global;
}
const period=block(addresses.period,32),rules=block(addresses.rules,0x210);
period.bytes.writeUInt32LE(o.period===undefined?22:o.period,12);rules.bytes.writeUInt32LE(o.rules===undefined?1:o.rules,0x208);
const tuning=block(addresses.tuning+0x5a5e2c,12);tuning.bytes.writeFloatLE(0,0);tuning.bytes.writeFloatLE(o.invalid_tuning?0:1,8);
const delegate=block(addresses.delegate,8),profile=layout.delegate_profiles[0],tableAt=imageBase+profile.static_vtable_rva;
set64(delegate,0,o.bad_delegate?0xdead:tableAt);
const table=block(tableAt,0x1000);
for(const [slot,target] of Object.entries(profile.required_slots))set64(table,Number(slot),imageBase+target+(o.bad_slot?1:0));
const playerAt=0x50000,teamAt=0x60000,availableAt=0x70000,available=block(availableAt,0x1f48),player=block(playerAt,1264);
player.bytes.writeUInt16LE(o.uid_mismatch?56:55,0xf4);
player.bytes.writeUInt32LE((o.base_years||0)<<18,0x32c);player.bytes.writeUInt32LE((o.extension_years||0)<<15,0x340);
set64(available,0,o.missing_member?0x90000:playerAt);
if(o.duplicate_member)set64(available,8,playerAt);
available.bytes.writeUInt16LE(o.duplicate_member?2:1,0x1f40);
const pool=block(addresses.pool+schema.pool.offset,44000);
for(let i=0;i<1000;i++){
 pool.bytes.writeUInt32LE(0xace00000,i*44+40);
 if(o.full_pool)pool.bytes.writeUInt32LE(1<<18,i*44+32);
}
for(const row of input.records||[])Buffer.from(row.hex,'hex').copy(pool.bytes,row.index*44);
const poolBefore=Buffer.from(pool.bytes);
function read(p,n){
 const row=locate(p.value,n),offset=p.value-row.at;
 if(row===pool&&n===44&&poolReads++===1000&&o.pool_changes_before)pool.bytes[36]^=1;
 if(row===player){playerReads++;if(playerReads===2&&o.player_changes_before)player.bytes[0x354]^=1;}
 return Uint8Array.from(row.bytes.subarray(offset,offset+n)).buffer;
}
function nativeCall(id,...args){
 calls.push(id);if(calls.length>7)throw Error('BUDGET_EXCEEDED');
 if(id==='sign.fa_available_count')return o.available_count===undefined?(o.duplicate_member?2:1):o.available_count;
 if(id==='sign.fa_available_pool'){
  if(args.length!==1||args[0]!==0)throw Error('AVAILABLE_POOL_ARGS');
  return ptr(o.pool_resolver_null?0:availableAt);
 }
 if(id==='player.by_id'){if(args.length!==1||args[0]!==55)throw Error('PLAYER_ARGS');return ptr(o.player_null?0:playerAt);}
 if(id==='sign.default_type'){
  if(!args[0].equals(ptr(playerAt))||!args[1].equals(ptr(teamAt)))throw Error('TYPE_ARGS');
  if(o.period_changes_before)period.bytes.writeUInt32LE(29,12);
  return o.default_type===undefined?2:o.default_type;
 }
 if(id!=='sign.offer_fa_phase')throw Error('UNEXPECTED_NATIVE_CALL');
 offers++;if(offers!==1||args.length!==4||!args[1].isNull()||args[2]!==0||args[3]!==0)throw Error('FIXED_ORIGINAL_CALLER_ARGS');
 const proposal=locate(args[0].value,44);if(!proposal.private)throw Error('PROPOSAL_NOT_PRIVATE');
 privateInput=proposal.bytes.toString('hex');
 if(!o.reject_no_record){
  let slot=-1;for(let i=0;i<1000;i++)if(((pool.bytes.readUInt32LE(i*44+32)>>>18)&15)===0){slot=i;break;}
  if(slot<0)throw Error('SIMULATOR_POOL_FULL');
  proposal.bytes.copy(pool.bytes,slot*44);
  const status=o.response_status===undefined?(o.reject_record?4:1):o.response_status;
  const word=pool.bytes.readUInt32LE(slot*44+32);
  pool.bytes.writeUInt32LE(((word&~(15<<18))|(status<<18)|(1<<15))>>>0,slot*44+32);
  if(o.pool_terms_change)pool.bytes.writeUInt32LE(999,slot*44+4);
  if(o.duplicate_created)pool.bytes.copy(pool.bytes,(slot+1)*44,slot*44,(slot+1)*44);
 }
 if(o.private_terms_change)proposal.bytes.writeUInt32LE(999,4);
 if(o.contract_changes_after)player.bytes.writeUInt32LE(1<<18,0x32c);
 if(o.team_link_changes_after)set64(player,0x60,teamAt);
 if(o.directory_changes_after)set64(available,0,0x90000);
 if(o.period_changes_after)period.bytes.writeUInt32LE(29,12);
 if(o.root_changes_after)set64(roots.pool,0,addresses.pool+8);
 if(o.delegate_changes_after)set64(delegate,0,tableAt+8);
 return o.native_return===undefined?(o.reject_no_record||o.reject_record?0:1):o.native_return;
}
const context={request,bindingSpecs,base,ptr,DataView,Uint8Array,Object,Array,Number,JSON,Error,read,
 u16:(b,at=0)=>new DataView(b).getUint16(at,true),u32:(b,at=0)=>new DataView(b).getUint32(at,true),
 ptrAt:(b,at=0)=>ptr(Number(new DataView(b).getBigUint64(at,true))),
 equal:(a,b)=>Buffer.from(a).equals(Buffer.from(b)),
 Memory:{alloc(n){const row=block(0x9000000,n,true);return ptr(row.at);}},
 team(id){if(id!==20||o.team_missing)throw Error('TEAM_NOT_FOUND');return ptr(teamAt);},call:nativeCall,
 result(outcome,details){messages.push({outcome,details});}};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:3000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({error,messages,calls,offers,poolReads,privateInput,forbiddenWrites,poolUnchanged:poolBefore.equals(pool.bytes),firstRecord:pool.bytes.subarray(0,44).toString('hex')}));
