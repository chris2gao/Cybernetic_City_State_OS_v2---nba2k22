'use strict';

// Derived from #38 rea_read_today.js. No native getter or game state write.
const game = Process.getModuleByName('NBA2K22.exe');
const base = game.base;
const at = rva => base.add(rva);
if (Process.arch !== 'x64' || Process.platform !== 'windows' || base.readU16() !== 0x5a4d)
    throw Error('Unexpected NBA2K22 ABI or DOS signature');
const peOffset = at(0x3c).readU32();
if (peOffset < 64 || peOffset > 4096) throw Error('PE offset outside verified range');
const pe = at(peOffset);
if (pe.readU32() !== 0x4550 || pe.add(4).readU16() !== 0x8664
    || pe.add(8).readU32() !== 1652287197 || pe.add(24).readU16() !== 0x20b)
    throw Error('NBA2K22 PE layout mismatch');

function bytesHex(address, length) {
    return Array.from(new Uint8Array(address.readByteArray(length)),
        value => value.toString(16).padStart(2, '0')).join('');
}

const modeAt = at(103986288);
const objectAt = at(103972696);
const getter = at(15593488);
if (bytesHex(getter, 11) !== '488b0559c444058b400cc3')
    throw Error('GameMode getter code mismatch');

function readToday() {
    const mode = modeAt.readPointer(), object = objectAt.readPointer();
    if (mode.isNull() || object.isNull()) throw Error('GameMode context unavailable');
    const vtable = object.readPointer();
    if (vtable.compare(base) < 0 || vtable.add(832).compare(at(game.size)) > 0
        || !vtable.add(824).readPointer().equals(getter)) throw Error('GameMode vtable mismatch');
    const raw = mode.add(20).readU32(), modeCode = mode.add(4).readU32(), period = mode.add(12).readU32();
    if (!modeAt.readPointer().equals(mode) || !objectAt.readPointer().equals(object)
        || !object.readPointer().equals(vtable) || mode.add(20).readU32() !== raw
        || mode.add(4).readU32() !== modeCode || mode.add(12).readU32() !== period)
        throw Error('GameMode changed during read');
    const year = 2000 + (raw >>> 25), month = (raw >>> 21) & 15, day = (raw >>> 16) & 31;
    const minutes = (raw >>> 5) & 2047;
    const iso = new Date(Date.UTC(year, month, day));
    if (!raw || month > 11 || !day || iso.getUTCDate() !== day || minutes >= 1440)
        throw Error('Invalid SCHEDULEDATE');
    return {raw, today: iso.toISOString().slice(0, 10), minutes, mode: modeCode, period};
}

if (typeof calendarPlan === 'undefined')
    send({kind:'native-control-result', event:'REA_NATIVE_TODAY', pid:Process.id,
        ...readToday(), binding_status:'NATIVE_DATE_ONLY'});
