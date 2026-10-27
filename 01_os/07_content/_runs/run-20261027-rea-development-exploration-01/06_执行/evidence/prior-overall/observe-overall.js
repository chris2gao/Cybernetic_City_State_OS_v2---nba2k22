// REA observation only; no hooks, NativeFunction, writes, or game actions.
const expected = [{"rva":9698800,"code_hex":"40534883ec20f6811c03000040488bd9751533d2e867b80500f30f10836c0100004883c4205bc3f30f10816c0100004883c4205bc3","sha256":"c6041e3c462f30e51305225c0eac515bd774186a18e4c1625065b9b05b64fdab"},{"rva":9698864,"code_hex":"40534883ec20f6811c03000040488bd9750733d2e827b80500f30f10836c0100004883c4205be9f5d30300","sha256":"9ffc0404d75ecd6546a67d232c69485fbe892679f8d2dffd22c67c260da2279e"},{"rva":9949776,"code_hex":"f30f114424084883ec780f2f05073f89010f28c80f87c20000000f2f05cfaa8901720d0f2f05ee0b8a010f869b000000488d05e5430b02c7442440000000004889442458488d0585ac5e004889442460488d8424800000004889442448488d055cc54c014889442450c744244402000000e85ac25e004c8bc04c8d0dd026ba01488d4424404889442438488d15cf509101488d054826ba014889442430488d0ddc26ba01488d056d26ba01c74424287b0000004889442420e8c3474d0185c07401ccf30f108c2480000000f30f590d510b8a01f30f2dc14883c478c30f2f05e1dc8901720d0f2f0580809d010f869b000000488d0523430b02c7442440000000004889442458488d05c3ab5e004889442460488d8424800000004889442448488d059ac44c014889442450c744244402000000e898c15e004c8bc04c8d0d0e26ba01488d4424404889442438488d150d509101488d058625ba014889442430488d0d7a26ba01488d05ab25ba01c7442428810000004889442420e801474d0185c07401ccf30f108c2480000000f30f2dc14883c478c3","sha256":"1e1d2fd618ad2de414b9e5461a338123c77971cbeb6ea5a4bfd24e1627c44a4a"}];
const m = Process.mainModule;
let budget=8192, total=0;
const trace=[];
const hex=a=>Array.from(new Uint8Array(a),b=>b.toString(16).padStart(2,'0')).join('');
function read(p,n,label){if(n<=0||n>1024||n>budget)throw Error('read budget');const v=p.readByteArray(n);total+=n;budget-=n;trace.push({label,bytes:n});return v;}
function pointer(a){return ptr('0x'+Array.from(new Uint8Array(a)).reverse().map(b=>b.toString(16).padStart(2,'0')).join(''));}
function safe(p){if(p.compare(ptr('0x10000'))<0||p.compare(ptr('0x00007fffffffffff'))>0)throw Error('noncanonical pointer');return p;}
for(const proof of expected){const value=read(m.base.add(proof.rva),proof.code_hex.length/2,'code:'+proof.rva);if(hex(value)!==proof.code_hex)throw Error('code binding mismatch');}
const rootRaw=read(m.base.add(0x06347720),8,'roster pointer');const roster=safe(pointer(rootRaw));
const descriptor=read(roster.add(16),16,'PLAYER descriptor');const dv=new DataView(descriptor);const count=Number(dv.getBigUint64(0,true));
if(!Number.isSafeInteger(count)||count<6||count>8192)throw Error('PLAYER descriptor count');
const pool=safe(pointer(descriptor.slice(8,16)));
const ranges=[[0,80],[244,246],[364,368],[760,764],[796,797]];
const denied=[[785,786],[880,882],[930,931],[1089,1090]];
for(const [a,b] of ranges)if(denied.some(([x,y])=>a<y&&x<b))throw Error('private interval overlap');
const rows=[];
for(let index=0;index<6;index++){
 const p=pool.add(index*1264),parts={};
 for(const [a,b] of ranges)parts[a]=hex(read(p.add(a),b-a,`player:${index}:${a}`));
 for(const [a,b] of ranges)if(hex(read(p.add(a),b-a,`recheck:${index}:${a}`))!==parts[a])throw Error('player changed during observation');
 rows.push({source_player_index:index,parts});
}
if(hex(read(m.base.add(0x06347720),8,'root recheck'))!==hex(rootRaw)||hex(read(roster.add(16),16,'descriptor recheck'))!==hex(descriptor))throw Error('root/descriptor changed');
send({kind:'overall-cache-read-only-evaluation',pid:Process.id,module:m.name,architecture:Process.arch,player_descriptor_count:count,rows,explicit_read_bytes:total,trace,protected_bytes_read:0,full_player_records_read:0,hooks:0,getter_calls:0,memory_writes:0,code_binding:'ALL_HISTORICAL_WINDOWS_MATCH',save_binding:'UNKNOWN_NOT_INFERRED_FROM_PROCESS',ui_binding:'NOT_OBSERVED'});
