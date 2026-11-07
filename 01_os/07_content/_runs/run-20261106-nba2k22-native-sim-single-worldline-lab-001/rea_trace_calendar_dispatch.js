// REA observation only. Does not enqueue or execute a game command.
'use strict';

const exe = Process.getModuleByName('NBA2K22.exe');
const base = exe.base;
const pe = base.add(base.add(0x3c).readU32());
if (Process.arch !== 'x64' || Process.platform !== 'windows'
    || pe.readU32() !== 0x4550 || pe.add(8).readU32() !== 1652287197) {
    throw Error('Unexpected PE build');
}
const dispatcher = base.add(0x1268320);
const wrapper = base.add(0x11be250);
const exact = (address, bytes) => Array.from(new Uint8Array(address.readByteArray(bytes.length)))
    .every((value, index) => value === bytes[index]);
if (!exact(dispatcher, [0x48, 0x89, 0x5c, 0x24, 0x10, 0x55, 0x56, 0x57])
    || !exact(wrapper, [0x40, 0x53, 0x48, 0x83, 0xec, 0x40])) throw Error('Unexpected entry bytes');

const candidates = new Set([17, 18, 19, 20, 31, 32, 34, 35]);
const limit = 64;
let sent = 0;
let sequence = 0;
const active = new Map();
const rva = ptr => ptr.compare(base) >= 0 && ptr.compare(base.add(exe.size)) < 0
    ? ptr.sub(base).toString() : null;
function emit(event, details) {
    if (sent === limit) send({event: 'REA_DISPATCH_TRACE_CAP_REACHED', limit});
    if (sent++ < limit) send({event, ...details});
}
function payloadType(payload) {
    if (payload.isNull()) return {kind: 'null'};
    try {
        const vtable = rva(payload.readPointer());
        return {kind: vtable ? 'module_vtable' : 'external_vtable', vtable_rva: vtable};
    } catch (_) {
        return {kind: 'unreadable'};
    }
}

Interceptor.attach(dispatcher, {
    onEnter(args) {
        const command = args[0].toUInt32();
        if (!candidates.has(command)) return;
        this.frame = {id: ++sequence, command, thread: this.threadId};
        this.previous = active.get(this.threadId);
        active.set(this.threadId, this.frame);
        emit('REA_SIM_COMMAND_ENTRY', {
            ...this.frame,
            caller_rva: rva(this.returnAddress),
            payload: payloadType(args[1]),
            frames: Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 10).map(rva),
        });
    },
    onLeave(result) {
        if (!this.frame) return;
        if (this.previous) active.set(this.threadId, this.previous);
        else active.delete(this.threadId);
        emit('REA_SIM_COMMAND_RETURN', {...this.frame, eax: result.toUInt32()});
    },
});
Interceptor.attach(wrapper, {
    onEnter(args) {
        const frame = active.get(this.threadId);
        if (!frame || rva(this.returnAddress) !== '0x12690e1') return;
        this.frame = frame;
        emit('REA_SIM_WRAPPER_ENTRY', {
            ...frame, target_word: args[0].toUInt32(), context_nonnull: !args[1].isNull(),
            r8d: args[2].toUInt32(), r9d: args[3].toUInt32(),
            stack5: args[4].toUInt32(), stack6: args[5].toUInt32(), stack7: args[6].toUInt32(),
        });
    },
    onLeave(result) {
        if (this.frame) emit('REA_SIM_WRAPPER_RETURN', {...this.frame, eax: result.toUInt32()});
    },
});
send({event: 'REA_DISPATCH_TRACE_ARMED', pid: Process.id, limit});
