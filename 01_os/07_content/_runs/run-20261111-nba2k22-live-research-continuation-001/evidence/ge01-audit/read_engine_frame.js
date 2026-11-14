'use strict';
const game = Process.getModuleByName('NBA2K22.exe');
const base = game.base;
if (Process.id !== 6964 || !base.equals(ptr('0x140000000')) || game.size !== 115056640) throw Error('GE01 process changed');
const frame = base.add(0xbad3c0), caller = base.add(0x17bcb95), call = base.add(0x17bcb90);
if (call.readU8() !== 0xe8 || !caller.add(call.add(1).readS32()).equals(frame)) throw Error('Frame source differs');
let recorded = false;
const hook = Interceptor.attach(frame, { onEnter() {
 if (recorded || !this.returnAddress.equals(caller)) return;
 const scheduler = base.add(0x6933668).readPointer();
 const idle = !scheduler.isNull() && scheduler.add(0x390).readU32() === 0xffffffff && scheduler.add(0x398).readPointer().isNull();
 if (!idle) return;
 recorded = true;
 send({event:'GE01_READ_ONLY_IDLE_FRAME',pid:Process.id,thread:this.threadId,caller:'0x17bcb95',frame:'0xbad3c0',idle:true,game_calls:0,game_writes:0});
}});
setTimeout(() => hook.detach(), 1400);
