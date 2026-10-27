const target=19883328,expected='48895c24084889742410574883ec60488bf1488bfa0fb709e853a9c4ff33db48',module=Process.mainModule,entry=module.base.add(target);let events=0,readBytes=0;const maxEvents=12;
function read(p,n){if(readBytes+n>8192)throw Error('trace read budget');readBytes+=n;return p.readByteArray(n);}
const hex=a=>Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,'0')).join('');
if(hex(read(entry,32))!==expected)throw Error('trace entry bytes changed');
const hook=Interceptor.attach(entry,{onEnter(args){this.keep=events<maxEvents;if(!this.keep)return;events++;this.thread=Process.getCurrentThreadId();this.caller=(this.returnAddress.compare(module.base)>=0&&this.returnAddress.compare(module.base.add(module.size))<0)?this.returnAddress.sub(module.base).toUInt32():null;
 try{this.owner=new DataView(read(args[0],2)).getUint16(0,true);this.opponent=new DataView(read(args[1].add(0xca8),2)).getUint16(0,true);}catch(e){this.error='ARGUMENT_READ_NOT_CONFIRMED';}
},onLeave(value){if(this.keep)send({kind:'coach-gameplan-lookup-event',owner_id:this.owner??null,opponent_id:this.opponent??null,raw_index:value.toUInt32()&255,thread_id:this.thread,caller_rva:this.caller,argument_error:this.error??null,ai_dispatch_proven:false});}});
setTimeout(()=>{hook.detach();send({kind:'coach-gameplan-trace-summary',function_rva:target,event_count:events,max_events:maxEvents,read_bytes:readBytes,hook_detached:true,observation_window_ms:900,business_memory_writes:0,explicit_native_calls:0,ai_dispatch_proven:false,absolute_addresses_emitted:false});},900);
