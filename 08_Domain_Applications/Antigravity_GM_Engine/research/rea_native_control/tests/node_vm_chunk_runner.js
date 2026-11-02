/**
 * Out-of-process synthetic Frida Node.js VM runner for REA chunk scripts.
 * 
 * Faithfully executes compiled chunk scripts in an isolated Node.js vm context,
 * simulating Windows x64 Frida APIs (Process, Memory, NativeFunction, Interceptor,
 * thread resolution, PeekMessageA GUI hook, 156-byte Player stat invariants,
 * and Coach GamePlan projection).
 * 
 * Usage:
 *   node node_vm_chunk_runner.js <script_path> [--fault-injection <mode>]
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const scriptPath = process.argv[2];
if (!scriptPath || !fs.existsSync(scriptPath)) {
  console.error(JSON.stringify({ error: "SCRIPT_PATH_NOT_FOUND", path: scriptPath }));
  process.exit(1);
}

// Parse optional fault injection argument
let faultInjection = null;
const faultIdx = process.argv.indexOf('--fault-injection');
if (faultIdx !== -1 && process.argv[faultIdx + 1]) {
  faultInjection = process.argv[faultIdx + 1];
}

const scriptCode = fs.readFileSync(scriptPath, 'utf8');

// Simulated 64-bit Address Space
class MockPointer {
  constructor(addr) {
    this.addr = typeof addr === 'bigint' ? addr : BigInt(addr);
  }
  add(offset) {
    return new MockPointer(this.addr + BigInt(offset));
  }
  sub(offset) {
    return new MockPointer(this.addr - BigInt(offset));
  }
  equals(other) {
    return other instanceof MockPointer && this.addr === other.addr;
  }
  isNull() {
    return this.addr === 0n;
  }
  toInt32() {
    return Number(BigInt.asIntN(32, this.addr));
  }
  toUInt32() {
    return Number(BigInt.asUintN(32, this.addr));
  }
  toString(radix = 16) {
    return '0x' + this.addr.toString(radix);
  }
}

function ptr(val) {
  if (typeof val === 'string' && val.startsWith('0x')) {
    return new MockPointer(BigInt(val));
  }
  return new MockPointer(BigInt(val || 0));
}

// Memory Page Store (Address -> Uint8Array)
const memoryPages = new Map();

function getMemoryBuffer(addr, size) {
  const pageBase = addr & ~0xFFFFn;
  if (!memoryPages.has(pageBase)) {
    memoryPages.set(pageBase, new Uint8Array(65536));
  }
  const page = memoryPages.get(pageBase);
  const pageOffset = Number(addr - pageBase);
  return { page, pageOffset };
}

function rawReadBytes(mockPtr, size) {
  const buf = new Uint8Array(size);
  for (let i = 0; i < size; i++) {
    const { page, pageOffset } = getMemoryBuffer(mockPtr.addr + BigInt(i), 1);
    buf[i] = page[pageOffset];
  }
  return buf.buffer.slice(buf.byteOffset, buf.byteOffset + size);
}

function rawWriteBytes(mockPtr, uint8Array) {
  for (let i = 0; i < uint8Array.length; i++) {
    const { page, pageOffset } = getMemoryBuffer(mockPtr.addr + BigInt(i), 1);
    page[pageOffset] = uint8Array[i];
  }
}

MockPointer.prototype.readByteArray = function(size) {
  return rawReadBytes(this, size);
};
MockPointer.prototype.readU32 = function() {
  const bytes = new Uint8Array(rawReadBytes(this, 4));
  return new DataView(bytes.buffer).getUint32(0, true);
};
MockPointer.prototype.readUtf16String = function(len) {
  const bytes = new Uint8Array(rawReadBytes(this, len * 2));
  let str = '';
  for (let i = 0; i < len * 2; i += 2) {
    const code = bytes[i] | (bytes[i + 1] << 8);
    if (!code) break;
    str += String.fromCharCode(code);
  }
  return str;
};
MockPointer.prototype.writeByteArray = function(bufferOrArray) {
  const arr = bufferOrArray instanceof Uint8Array ? bufferOrArray : new Uint8Array(bufferOrArray);
  rawWriteBytes(this, arr);
};
MockPointer.prototype.writeU8 = function(val) {
  rawWriteBytes(this, new Uint8Array([val & 0xFF]));
};
MockPointer.prototype.writeU16 = function(val) {
  const arr = new Uint8Array(2);
  new DataView(arr.buffer).setUint16(0, val, true);
  rawWriteBytes(this, arr);
};
MockPointer.prototype.writeU32 = function(val) {
  const arr = new Uint8Array(4);
  new DataView(arr.buffer).setUint32(0, val, true);
  rawWriteBytes(this, arr);
};
MockPointer.prototype.writePointer = function(p) {
  const arr = new Uint8Array(8);
  new DataView(arr.buffer).setBigUint64(0, p.addr, true);
  rawWriteBytes(this, arr);
};

let nextAllocAddr = 0x200000000n;
const Memory = {
  alloc(size) {
    const p = new MockPointer(nextAllocAddr);
    nextAllocAddr += BigInt(Math.max(size, 4096));
    // Zero memory
    rawWriteBytes(p, new Uint8Array(size));
    return p;
  }
};

// Setup NBA2K22 mock layout
const baseAddr = 0x140000000n;
const basePtr = new MockPointer(baseAddr);

// Populate Pinned Native Code Signatures
const sigsPath = path.resolve(__dirname, 'node_vm_signatures.json');
if (fs.existsSync(sigsPath)) {
  const sigs = JSON.parse(fs.readFileSync(sigsPath, 'utf8'));
  for (const [key, bytes] of Object.entries(sigs)) {
    const rva = parseInt(key.split(':')[0], 10);
    if (faultInjection === 'PINNED_NATIVE_CODE_CHANGED') {
      const corrupt = new Uint8Array(bytes);
      corrupt[0] ^= 0xff;
      basePtr.add(rva).writeByteArray(corrupt);
    } else {
      basePtr.add(rva).writeByteArray(new Uint8Array(bytes));
    }
  }
}

// Setup Root RVA 0x5109b88 and 103972696 (Player stat delegate)
const statDelegatePtr = new MockPointer(0x150000000n);
const vtablePtr = new MockPointer(0x150001000n);
basePtr.add(0x5109b88).writePointer(statDelegatePtr);
basePtr.add(103972696).writePointer(statDelegatePtr);
statDelegatePtr.add(0).writePointer(vtablePtr);
statDelegatePtr.add(8).writePointer(vtablePtr);

// Required slots in vtable: slot 0 -> 0x978360, slot 8 -> 0x990a10, slot 736 -> 18713280, slot 4680 -> 18541376
if (faultInjection !== 'CORRUPT_DELEGATE') {
  vtablePtr.add(0).writePointer(basePtr.add(0x978360));
  vtablePtr.add(8).writePointer(basePtr.add(0x990a10));
  vtablePtr.add(736).writePointer(basePtr.add(18713280));
  vtablePtr.add(4680).writePointer(basePtr.add(18541376));
} else {
  vtablePtr.add(0).writePointer(ptr(0xdeadbeef));
  vtablePtr.add(8).writePointer(ptr(0xdeadbeef));
  vtablePtr.add(736).writePointer(ptr(0xdeadbeef));
  vtablePtr.add(4680).writePointer(ptr(0xdeadbeef));
}

// Setup Roster Root: getter(18701792) -> getter(0x11d5de0)
// Code at base + 0x11d5de0: 48 8b 05 [rel32]
const rosterGetterPtr = basePtr.add(18701792);
const rosterTargetPtr = new MockPointer(0x160000008n); // rosterRoot + 8
const relOffset = 0x1000;
rosterGetterPtr.writeByteArray(new Uint8Array([0x48, 0x8b, 0x05, relOffset & 0xFF, (relOffset >> 8) & 0xFF, (relOffset >> 16) & 0xFF, (relOffset >> 24) & 0xFF, 0x90]));
basePtr.add(18701792 + 7 + relOffset).writePointer(rosterTargetPtr);

const rosterRoot = rosterTargetPtr.sub(8);
const teamBasePtr = new MockPointer(0x170000000n);
// rosterRoot + 0x88 -> teamCount (30), teamBase (pointer)
const dirPtr = rosterRoot.add(0x88);
dirPtr.writePointer(new MockPointer(30n)); // 30 teams
dirPtr.add(8).writePointer(teamBasePtr);

// Populate Teams and Players
const playerValuesMap = new Map(); // pid -> { fieldId -> value }

for (let tId = 0; tId < 30; tId++) {
  const teamPtr = teamBasePtr.add(tId * 4696);
  teamPtr.add(0xca8).writeU16(tId);

  // Coach pointer at team + 0xce8
  const coachPtr = new MockPointer(0x180000000n + BigInt(tId * 4096));
  teamPtr.add(0xce8).writePointer(coachPtr);
  coachPtr.add(0x18).writePointer(teamPtr); // Coach owner matches team

  // Roster players (up to 15)
  for (let pIdx = 0; pIdx < 15; pIdx++) {
    const pid = 1000 + tId * 100 + pIdx;
    const playerPtr = new MockPointer(0x190000000n + BigInt(tId * 65536 + pIdx * 2048));
    teamPtr.add(pIdx * 8).writePointer(playerPtr);

    playerPtr.add(0xf4).writeU16(pid);
    playerPtr.add(0x60).writePointer(teamPtr);
    playerPtr.add(0xa8).writePointer(teamPtr);

    // Initial cache flags at 0x31c (e.g. 0xffffffff)
    playerPtr.add(0x31c).writeU32(0xffffffff);

    // Initialize 156 bytes stat buffer at 0x41f
    const statBuf = new Uint8Array(156);
    statBuf.fill(50);
    playerPtr.add(0x41f).writeByteArray(statBuf);

    playerValuesMap.set(pid, { playerPtr, stats: {} });
  }
}

// Special check for Damian Lillard on Portland (team 28, pid 2459)
const lillardPtr = new MockPointer(0x190000000n + BigInt(28 * 65536 + 0 * 2048));
teamBasePtr.add(28 * 4696).add(0 * 8).writePointer(lillardPtr);
lillardPtr.add(0xf4).writeU16(2459);
lillardPtr.add(0x60).writePointer(teamBasePtr.add(28 * 4696));
lillardPtr.add(0xa8).writePointer(teamBasePtr.add(28 * 4696));
lillardPtr.add(0x31c).writeU32(0xffffffff);
const lillardStatBuf = new Uint8Array(156);
lillardStatBuf.fill(50);
// SHOT_TENDENCY offset is 0x458 -> offset in 156 is 0x458 - 0x41f = 57
// Default expected_before = 95
lillardStatBuf[57] = (faultInjection === 'CAS_MISMATCH') ? 85 : 95;
lillardPtr.add(0x41f).writeByteArray(lillardStatBuf);
playerValuesMap.set(2459, { playerPtr: lillardPtr, stats: { 57: (faultInjection === 'CAS_MISMATCH') ? 85 : 95 } });

// Franchise Record Getter (6278620)
const franchiseTargetPtr = new MockPointer(0x1a0000000n);
const fGetterPtr = basePtr.add(6278620);
const fRelOffset = 0x2000;
fGetterPtr.writeByteArray(new Uint8Array([0x48, 0x8b, 0x05, fRelOffset & 0xFF, (fRelOffset >> 8) & 0xFF, (fRelOffset >> 16) & 0xFF, (fRelOffset >> 24) & 0xFF, 0x90]));
basePtr.add(6278620 + 7 + fRelOffset).writePointer(franchiseTargetPtr);

for (let i = 0; i < 36; i++) {
  const rec = franchiseTargetPtr.add(0x19cfd0 + i * 0x13e70);
  rec.writeU16(i); // teamId
  const gp = rec.add(0x7854);
  gp.writeU16(i); // teamId in gameplan
  // GamePlan buffer: 880 bytes
  const gpBuf = new Uint8Array(880);
  gpBuf.fill(0);
  gp.writeByteArray(gpBuf);
}

// Hook state
let attachedHooks = [];
let windowThreadId = 7777;
let currentThreadId = (faultInjection === 'WRONG_THREAD') ? 9999 : 7777;
let emittedMessages = [];

const ProcessMock = {
  arch: 'x64',
  id: 12345,
  mainModule: {
    base: basePtr,
    name: 'NBA2K22.exe'
  },
  getCurrentThreadId() {
    return currentThreadId;
  },
  enumerateModules() {
    return [{ base: basePtr, name: 'NBA2K22.exe' }];
  },
  getModuleByName(name) {
    if (name.toLowerCase() === 'user32.dll') {
      return {
        base: new MockPointer(0x7ff800000000n),
        name: 'user32.dll',
        getExportByName(exp) {
          return new MockPointer(0x7ff800001000n + BigInt(exp.length * 16));
        }
      };
    }
    return { base: basePtr, name };
  },
  findRangeByAddress(p) {
    return {
      base: new MockPointer(p.addr & ~0xFFFFn),
      size: 65536,
      protection: 'rwx'
    };
  }
};

const InterceptorMock = {
  attach(target, callbacks) {
    const hookObj = {
      target,
      callbacks,
      detach() {
        const idx = attachedHooks.indexOf(hookObj);
        if (idx !== -1) attachedHooks.splice(idx, 1);
      }
    };
    attachedHooks.push(hookObj);
    return hookObj;
  }
};

function NativeFunctionMock(address, returnType, argTypes, options) {
  return function(...args) {
    // 1. GUI / Window functions
    if (address.addr > 0x7ff800000000n) {
      if (argTypes.length === 2 && argTypes[0] === 'pointer' && argTypes[1] === 'pointer') {
        // GetWindowThreadProcessId(handle, cell) or EnumWindows
        if (returnType === 'uint') {
          // GetWindowThreadProcessId
          const cell = args[1];
          cell.writeU32(ProcessMock.id);
          return windowThreadId;
        } else if (returnType === 'int') {
          // EnumWindows(callback, lparam)
          const cb = args[0];
          cb(new MockPointer(0x1001n), ptr(0));
          return 1;
        }
      }
      if (argTypes.length === 1 && argTypes[0] === 'pointer') {
        // IsWindowVisible
        return 1;
      }
      if (argTypes.length === 3) {
        // GetWindowTextW(handle, title, max)
        const titlePtr = args[1];
        const titleStr = "NBA 2K22";
        const utf16Bytes = Buffer.from(titleStr, 'utf16le');
        titlePtr.writeByteArray(utf16Bytes);
        return titleStr.length;
      }
      if (argTypes.length === 4) {
        // PostMessageW: triggers the message pump!
        // Dispatch to attached PeekMessageA hook
        setImmediate(() => {
          for (const hook of [...attachedHooks]) {
            if (hook.callbacks && typeof hook.callbacks.onLeave === 'function') {
              hook.callbacks.onLeave();
            }
          }
        });
        return 1;
      }
    }

    // 2. Native bindings
    // player.get_stat_ui(player, native_index)
    if (argTypes.length === 2 && argTypes[0] === 'pointer' && typeof args[1] === 'number') {
      const playerPtr = args[0];
      const nativeIndex = args[1];
      const pid = new DataView(rawReadBytes(playerPtr.add(0xf4), 2)).getUint16(0, true);
      const statOffset = 0x41f + nativeIndex;
      const val = new DataView(rawReadBytes(playerPtr.add(statOffset), 1)).getUint8(0);
      return val;
    }

    // player.set_stat_ui(player, native_index, value)
    if (argTypes.length === 3 && argTypes[0] === 'pointer' && typeof args[1] === 'number') {
      const playerPtr = args[0];
      const nativeIndex = args[1];
      const val = args[2];
      const statOffset = 0x41f + nativeIndex;
      playerPtr.add(statOffset).writeU8(val);

      // Fault injection check
      if (faultInjection === 'UNREQUESTED_STAT_BYTE_CHANGED') {
        // Mutate adjacent byte (nativeIndex + 1)
        playerPtr.add(statOffset + 1).writeU8(255);
      }
      if (faultInjection === 'ATTRIBUTE_CACHE_FLAG_INVARIANT') {
        // Do not update flags or update wrong flags
        playerPtr.add(0x31c).writeU32(0x12345678);
      } else {
        // Tendency writes do not mutate flags; only attributes clear bit 6 (0x40)
        if (nativeIndex < 36) {
          const flags = playerPtr.add(0x31c).readU32();
          playerPtr.add(0x31c).writeU32((flags & ~0x40) >>> 0);
        }
      }
      return;
    }

    // coach.apply_gameplan(inputBuf, coach)
    if (argTypes.length === 2 && argTypes[0] === 'pointer' && argTypes[1] === 'pointer') {
      return;
    }

    return null;
  };
}

function NativeCallbackMock(fn, returnType, argTypes, abi) {
  return fn;
}

const sandbox = {
  Process: ProcessMock,
  Memory: Memory,
  NativeFunction: NativeFunctionMock,
  NativeCallback: NativeCallbackMock,
  Interceptor: InterceptorMock,
  ptr: ptr,
  send: function(msg) {
    emittedMessages.push(msg);
  },
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  Buffer: Buffer,
  DataView: DataView,
  Uint8Array: Uint8Array,
  console: console
};

const context = vm.createContext(sandbox);

try {
  vm.runInContext(scriptCode, context, { filename: scriptPath, timeout: 6000 });
} catch (e) {
  console.log(JSON.stringify({
    success: false,
    error: String(e),
    emitted_messages: emittedMessages
  }));
  process.exit(0);
}

// Wait for the async PeekMessageA trigger
setTimeout(() => {
  console.log(JSON.stringify({
    success: true,
    fault_injection: faultInjection,
    emitted_messages: emittedMessages
  }));
  process.exit(0);
}, 200);
