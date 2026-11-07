// REA Frida script for the fixed NBA2K22 Win64 build. No NativeFunction calls.
'use strict';

const moduleInfo = Process.getModuleByName('NBA2K22.exe');
const base = moduleInfo.base;
if (Process.arch !== 'x64' || Process.platform !== 'windows') throw Error('Unexpected host ABI');
if (base.readU16() !== 0x5a4d) throw Error('Missing DOS signature');
const peOffset = base.add(0x3c).readU32();
if (peOffset < 64 || peOffset > 4096) throw Error('Unexpected PE header location');
const pe = base.add(peOffset);
if (pe.readU32() !== 0x4550 || pe.add(4).readU16() !== 0x8664
    || pe.add(8).readU32() !== 1652287197 || pe.add(24).readU16() !== 0x20b) {
    throw Error('NBA2K22 PE layout mismatch');
}

// game_mode_native_profile.json: GAMEMODE pointer, vtable binding, getter code proof.
const modeAt = base.add(103986288);
const objectAt = base.add(103972696);
const expectedGetter = base.add(15593488);
const expectedBytes = '488b0559c444058b400cc3';
const getterBytes = Array.from(new Uint8Array(expectedGetter.readByteArray(expectedBytes.length / 2)),
    byte => byte.toString(16).padStart(2, '0')).join('');
if (getterBytes !== expectedBytes) throw Error('GameMode getter code mismatch');

const mode = modeAt.readPointer();
const object = objectAt.readPointer();
if (mode.isNull() || object.isNull()) throw Error('GameMode context unavailable');
const vtable = object.readPointer();
if (vtable.compare(base) < 0 || vtable.add(832).compare(base.add(moduleInfo.size)) > 0
    || !vtable.add(824).readPointer().equals(expectedGetter)) throw Error('GameMode vtable mismatch');

const todayAddress = mode.add(20);
const raw = todayAddress.readU32();
if (!modeAt.readPointer().equals(mode) || !objectAt.readPointer().equals(object)
    || !object.readPointer().equals(vtable) || todayAddress.readU32() !== raw) {
    throw Error('GameMode identity or date changed while reading');
}
const day = (raw >>> 16) & 31;
const month = (raw >>> 21) & 15;
const year = 2000 + (raw >>> 25);
const minutes = (raw >>> 5) & 2047;
const dayValue = new Date(Date.UTC(year, month, day));
if (!raw || month > 11 || !day || dayValue.getUTCDate() !== day || minutes >= 1440) {
    throw Error('Invalid native SCHEDULEDATE');
}
const pad = n => String(n).padStart(2, '0');
send({
    event: 'REA_NATIVE_TODAY', pid: Process.id, raw: '0x' + raw.toString(16),
    today: dayValue.toISOString().slice(0, 10),
    time: pad(Math.floor(minutes / 60)) + ':' + pad(minutes % 60),
    domain: 'GAME_CIVIL_TIME', getter_called: false, game_writes: false,
});
