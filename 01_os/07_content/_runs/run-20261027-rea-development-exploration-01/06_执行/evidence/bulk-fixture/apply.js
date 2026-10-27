const target={"pid": 9040, "address": "0x22ab991d710", "count": 4096, "stride": 16},restore=false;if(Process.id!==target.pid)throw Error('owned PID changed');
const base=ptr(target.address),count=target.count,stride=16,bytes=count*stride;
if(count!==4096||bytes!==65536)throw Error('fixture shape');
const before=base.readByteArray(bytes),v=new DataView(before);let casChecks=0;
function expected(i,changed){const value=i*3+(changed?7:0),g=changed?2:1;return [i+1,value,g,((i+1)^value^g)>>>0];}
function matches(i,words){return words.every((x,k)=>v.getUint32(i*16+k*4,true)===x);}
let mismatchAbortProof=null;
if(!restore){const wrong=expected(0,false);wrong[1]++;mismatchAbortProof=!matches(0,wrong);if(!mismatchAbortProof)throw Error('negative CAS failed');}
// Entire plan is checked before the first write. This is not cross-process atomic CAS.
for(let i=0;i<count;i++){if(!matches(i,expected(i,restore)))throw Error('before mismatch at '+i);casChecks++;}
const desired=new ArrayBuffer(bytes),d=new DataView(desired);
for(let i=0;i<count;i++)expected(i,!restore).forEach((x,k)=>d.setUint32(i*16+k*4,x,true));
base.writeByteArray(desired);
const after=new DataView(base.readByteArray(bytes));let verified=0;
for(let i=0;i<count;i++){if(!expected(i,!restore).every((x,k)=>after.getUint32(i*16+k*4,true)===x))throw Error('readback mismatch');verified++;}
send({kind:restore?'owned-fixture-restored':'owned-fixture-bulk-applied',records:count,stride,cas_checks:casChecks,negative_cas_abort_no_write:mismatchAbortProof,verified,bytes_written:bytes,explicit_bytes_read:bytes*2,game_target:false});
