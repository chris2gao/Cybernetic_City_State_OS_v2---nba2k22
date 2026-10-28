'use strict';
const u=Process.getModuleByName('user32.dll'),base=Process.mainModule.base,end=base.add(Process.mainModule.size),pidCell=Memory.alloc(4),name=Memory.alloc(256);
const threadOf=new NativeFunction(u.getExportByName('GetWindowThreadProcessId'),'uint',['pointer','pointer'],'win64'),visible=new NativeFunction(u.getExportByName('IsWindowVisible'),'int',['pointer'],'win64'),title=new NativeFunction(u.getExportByName('GetWindowTextW'),'int',['pointer','pointer','int'],'win64');
const windows=[];let selected=null;
const callback=new NativeCallback((h,l)=>{pidCell.writeU32(0);const tid=threadOf(h,pidCell);if(pidCell.readU32()===Process.id&&visible(h)){const length=title(h,name,128),text=length>0?name.readUtf16String(length):'';windows.push({thread_id:tid,title:text});if(!selected||/NBA/i.test(text))selected={handle:h,thread:tid};}return windows.length<8?1:0;},'int',['pointer','pointer'],'win64');
new NativeFunction(u.getExportByName('EnumWindows'),'int',['pointer','pointer'],'win64')(callback,ptr(0));
const events=[],hooks=[];
if(selected)for(const symbol of ['PeekMessageW','PeekMessageA','GetMessageW','GetMessageA']){try{hooks.push(Interceptor.attach(u.getExportByName(symbol),{onLeave(){if(Process.getCurrentThreadId()!==selected.thread||events.length>=8)return;events.push({symbol,thread_id:Process.getCurrentThreadId(),caller_rva:this.returnAddress.compare(base)>=0&&this.returnAddress.compare(end)<0?this.returnAddress.sub(base).toUInt32():null});}}));}catch(e){}}
if(selected)new NativeFunction(u.getExportByName('PostMessageW'),'int',['pointer','uint','pointer','pointer'],'win64')(selected.handle,0,ptr(0),ptr(0));
setTimeout(()=>{for(const h of hooks)h.detach();send({kind:'native-game-gui-thread-observation',windows,selected_thread:selected?.thread??null,message_pump_events:events,hooks_detached:hooks.length,wake_message:'WM_NULL_ONLY',game_business_calls:0,business_writes:0,absolute_addresses_emitted:false});},1200);
