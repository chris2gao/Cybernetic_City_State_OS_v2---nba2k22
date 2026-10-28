// Synthetic pool only. Runs the shipped handler; exposes no Native write API.
const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const request=input.request,bindingSpecs=input.bindings,options=input.options||{},messages=[];
const schema=bindingSpecs['sign.pool_read_context'].input_layout.schema;
const imageBase=0x140000000,rootAddress=0x200000,poolAddress=rootAddress+schema.pool.offset;
class Pointer{constructor(value){this.value=value;}add(n){return new Pointer(this.value+n);}equals(p){return this.value===p.value;}isNull(){return this.value===0;}}
const base=new Pointer(imageBase),owner=new Pointer(0x3000);
const bytes=Buffer.alloc(schema.pool.count*schema.pool.stride),rootAt=imageBase+schema.pool.root_rva;
for(const row of input.records||[])Buffer.from(row.hex,'hex').copy(bytes,row.index*schema.pool.stride);
const initial=bytes.toString('hex');let rootReads=0,poolReads=0,teamReads=0,gameCalls=0;
function read(p,n){
 if(p.value===rootAt&&n===8){
  rootReads++;const value=options.null_root?0:options.root_changes&&rootReads>1?rootAddress+8:rootAddress;
  const out=new ArrayBuffer(8);new DataView(out).setBigUint64(0,BigInt(value),true);return out;
 }
 const offset=p.value-poolAddress;
 if(offset<0||n!==44||offset+n>bytes.length||offset%44)throw Error('UNEXPECTED_POOL_READ');
 if(poolReads++===schema.pool.count)for(const row of options.change_after_first_scan||[])Buffer.from(row.hex,'hex').copy(bytes,row.index*schema.pool.stride);
 return Uint8Array.from(bytes.subarray(offset,offset+n)).buffer;
}
const context={request,bindingSpecs,base,DataView,Uint8Array,Object,Array,Number,Set,Error,read,
 ptrAt(raw){return new Pointer(Number(new DataView(raw).getBigUint64(0,true)));},
 equal(a,b){return Buffer.from(a).equals(Buffer.from(b));},
 team(id){if(id!==20||options.team_missing)throw Error('TEAM_NOT_FOUND');teamReads++;return options.team_changes&&teamReads>1?new Pointer(0x4000):owner;},
 call(){gameCalls++;throw Error('SIGNING_READER_CALLED_BUSINESS_FUNCTION');},
 result(outcome,details){messages.push({outcome,details});}};
let error=null;
try{vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8')+'\nexecuteAction();',context,{timeout:3000});}catch(e){error=e.message;}
process.stdout.write(JSON.stringify({error,messages,gameCalls,poolReads,unchanged:initial===bytes.toString('hex')}));
