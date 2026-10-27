import argparse,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();data=Path('E:/Games/NBA 2K22/NBA2K22.exe').read_bytes()
assert hashlib.sha256(data).hexdigest()=='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
target=19883328;expected=data[target-2560:target-2560+32].hex()
js=r'''const target=__RVA__,expected='__HEX__',module=Process.mainModule,entry=module.base.add(target);let events=0,readBytes=0;const maxEvents=12;
function read(p,n){if(readBytes+n>8192)throw Error('trace read budget');readBytes+=n;return p.readByteArray(n);}
const hex=a=>Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,'0')).join('');
if(hex(read(entry,32))!==expected)throw Error('trace entry bytes changed');
const hook=Interceptor.attach(entry,{onEnter(args){this.keep=events<maxEvents;if(!this.keep)return;events++;this.thread=Process.getCurrentThreadId();this.caller=(this.returnAddress.compare(module.base)>=0&&this.returnAddress.compare(module.base.add(module.size))<0)?this.returnAddress.sub(module.base).toUInt32():null;
 try{this.owner=new DataView(read(args[0],2)).getUint16(0,true);this.opponent=new DataView(read(args[1].add(0xca8),2)).getUint16(0,true);}catch(e){this.error='ARGUMENT_READ_NOT_CONFIRMED';}
},onLeave(value){if(this.keep)send({kind:'coach-gameplan-lookup-event',owner_id:this.owner??null,opponent_id:this.opponent??null,raw_index:value.toUInt32()&255,thread_id:this.thread,caller_rva:this.caller,argument_error:this.error??null,ai_dispatch_proven:false});}});
setTimeout(()=>{hook.detach();send({kind:'coach-gameplan-trace-summary',function_rva:target,event_count:events,max_events:maxEvents,read_bytes:readBytes,hook_detached:true,observation_window_ms:900,business_memory_writes:0,explicit_native_calls:0,ai_dispatch_proven:false,absolute_addresses_emitted:false});},900);
'''.replace('__RVA__',str(target)).replace('__HEX__',expected)
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'coach_trace_probe.js').write_text(js,encoding='utf-8');print(json.dumps({'rva':target,'entry_bytes':32,'max_events':12,'window_ms':900,'business_writes':0,'calls':0}))
