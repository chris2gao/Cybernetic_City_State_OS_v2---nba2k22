'use strict';
const calendarPlan = {"creation_filetime":"134391145927700356","dispatch":true,"expires_ms":1794654410645,"game_season_year":2022,"games":[{"away":20,"day":726597632,"home":14,"id":203},{"away":19,"day":726597632,"home":17,"id":204},{"away":23,"day":726597632,"home":8,"id":205},{"away":26,"day":726597632,"home":27,"id":206},{"away":10,"day":726597632,"home":24,"id":207},{"away":22,"day":726597632,"home":28,"id":208},{"away":3,"day":726597632,"home":15,"id":209},{"away":29,"day":726663168,"home":18,"id":210},{"away":0,"day":726663168,"home":12,"id":211},{"away":25,"day":726663168,"home":6,"id":212}],"module_base":"0x140000000","module_size":115056640,"pe_timestamp":1652287197,"pid":6964,"plan_digest":"03b9512f53e2fe60b740231e62eda9579c88c632d3db648d3a8462683cb29327","selected":726597632,"stop":726663168,"thread":8244,"today":726635074};
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
// This suffix is bundled with native_today.js and a validated calendarPlan.
if (Process.id !== calendarPlan.pid || !base.equals(ptr(calendarPlan.module_base))
    || game.size !== calendarPlan.module_size) throw Error('Target epoch changed');
const kernel = Process.getModuleByName('kernel32.dll');
const currentProcess = new NativeFunction(kernel.getExportByName('GetCurrentProcess'), 'pointer', []);
const getProcessTimes = new NativeFunction(kernel.getExportByName('GetProcessTimes'),
    'int', ['pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
const times = Memory.alloc(32);
if (!getProcessTimes(currentProcess(), times, times.add(8), times.add(16), times.add(24))
    || times.readU64().toString() !== calendarPlan.creation_filetime)
    throw Error('Process creation time changed');

const dispatcher = at(0x1268320), frameEntry = at(0xbad3c0), caller = at(0x17bcb95);
const call = at(0x17bcb90), table = at(0x2479e30);
if (bytesHex(dispatcher, 8) !== '48895c2410555657' || call.readU8() !== 0xe8
    || !caller.add(call.add(1).readS32()).equals(frameEntry)
    || !table.add(0x18).readPointer().equals(at(0x82b8f0)))
    throw Error('Native dispatcher or frame boundary mismatch');

const seasonAt = at(0x632b4b8), rosterAt = at(0x6347720), schedulerAt = at(0x6933668);
const season = seasonAt.readPointer(), roster = rosterAt.readPointer(), scheduler = schedulerAt.readPointer();
const mode = modeAt.readPointer(), modeObject = objectAt.readPointer();
if ([season, roster, scheduler, mode, modeObject].some(value => value.isNull()))
    throw Error('Native scene unavailable');
const countAt = roster.add(160), indexAt = countAt.add(8);
const index = indexAt.readPointer(), count = countAt.readU64().toNumber();
if (count < 1 || count > 1742 || index.isNull()) throw Error('Schedule capacity gate failed');

const user32 = Process.getModuleByName('user32.dll');
const getForeground = new NativeFunction(user32.getExportByName('GetForegroundWindow'), 'pointer', []);
const windowThread = new NativeFunction(user32.getExportByName('GetWindowThreadProcessId'),
    'uint32', ['pointer', 'pointer']);
const isVisible = new NativeFunction(user32.getExportByName('IsWindowVisible'), 'int', ['pointer']);
const isIconic = new NativeFunction(user32.getExportByName('IsIconic'), 'int', ['pointer']);
const windowPid = Memory.alloc(4);
function foregroundThread() {
    const window = getForeground();
    if (window.isNull() || !isVisible(window) || isIconic(window)) return 0;
    const thread = windowThread(window, windowPid);
    return windowPid.readU32() === Process.id ? thread : 0;
}
function idle() {
    return scheduler.add(0x390).readU32() === 0xffffffff
        && scheduler.add(0x398).readPointer().isNull()
        && [0x634e9e8, 0x3722d98, 0x3724808, 0x3724818, 0x3724820].every(rva => at(rva).readU32() === 0);
}

const expected = new Map(calendarPlan.games.map(game => [game.id, game]));
const selected = calendarPlan.selected, next = calendarPlan.stop, start = (calendarPlan.today & 0xffff0000) >>> 0;
const out = status => send({kind:'native-control-result', status, pid:Process.id,
    plan_digest:calendarPlan.plan_digest});
function verifyWindow(after) {
    const today = readToday();
    if (today.mode !== 1 || today.period !== 29
        || today.raw !== (after ? next : calendarPlan.today)
        || !modeAt.readPointer().equals(mode) || !objectAt.readPointer().equals(modeObject)
        || !seasonAt.readPointer().equals(season) || !rosterAt.readPointer().equals(roster)
        || !schedulerAt.readPointer().equals(scheduler) || !indexAt.readPointer().equals(index)
        || countAt.readU64().toNumber() !== count)
        throw Error('Native world, calendar or stage changed');
    const observed = new Map();
    for (let i = 0; i < count; i++) {
        const address = season.add(0x28 + i * 60);
        const day = (address.readU32() & 0xffff0000) >>> 0;
        if (day < start || day > next) continue;
        const id = address.add(8).readU32(), plan = expected.get(id);
        if (!plan || observed.has(id) || plan.day !== day || plan.home !== address.add(12).readU16()
            || plan.away !== address.add(14).readU16()) throw Error('Schedule fixture differs');
        const flags = address.add(56).readU32(), played = address.add(4).readU32();
        const header = bytesHex(address, 60);
        let box = '', stats = null, length = 0;
        if (after && day <= selected) {
            const index = address.add(20).readU16(), h = address.add(22).readU8(), a = address.add(23).readU8();
            if (((flags >>> 11) & 3) !== 2 || !(flags & 0x40000)
                || ((played & 0xffff0000) >>> 0) !== day
                || !h || !a || h > 26 || a > 26 || index + h + a > 45292)
                throw Error('Final or Box bounds differ');
            length = (h + a) * 24;
            stats = season.add(112308 + index * 24);
            box = bytesHex(stats, length);
        } else if ((flags & 0x41800) || played || address.add(20).readU32()) {
            throw Error('Expected pending game has changed');
        }
        observed.set(id, {id, day, address, header, stats, length, box});
    }
    if (observed.size !== expected.size || readToday().raw !== today.raw)
        throw Error('Expected Game IDs or native date changed');
    for (const row of observed.values()) {
        if (bytesHex(row.address, 60) !== row.header || (row.stats && bytesHex(row.stats, row.length) !== row.box))
            throw Error('Schedule or Box changed during read');
    }
    return {today, rows:Array.from(observed.values())};
}

verifyWindow(false);
const payload = Memory.alloc(24);
payload.writePointer(table);
payload.add(8).writeU32(selected);
payload.add(16).writeU32(1);
const gateExpiry = Math.min(Date.now() + 6000, calendarPlan.expires_ms);
let firstThread = 0, decided = false, active = false;

if (calendarPlan.dispatch) {
    const raise = Process.getModuleByName('KERNELBASE.dll').findExportByName('RaiseException');
    if (!raise) throw Error('Exception telemetry unavailable');
    Interceptor.attach(raise, {onEnter(args) {
        if (active && this.threadId === calendarPlan.thread)
            send({event:'NATIVE_EXCEPTION_OBSERVED', source:'RaiseException', code:args[0].toUInt32()});
    }});
    Process.setExceptionHandler(details => {
        if (active)
            send({event:'NATIVE_EXCEPTION_OBSERVED', source:'Frida', type:details.type});
        return false;
    });
}
Interceptor.attach(frameEntry, {onEnter() {
    if (decided || Date.now() >= gateExpiry || !this.returnAddress.equals(caller) || !idle()) return;
    const guiThread = foregroundThread();
    if (!guiThread || guiThread === this.threadId || (calendarPlan.thread && this.threadId !== calendarPlan.thread))
        return;
    try {
        if (firstThread !== this.threadId) {
            firstThread = this.threadId;
            return;
        }
        decided = true;
        verifyWindow(false);
        if (!calendarPlan.dispatch) {
            send({event:'FRAME_GATE_OBSERVED', thread:this.threadId, gui_thread:guiThread});
            out('FRAME_GATE_OBSERVED');
            return;
        }
        if (Date.now() >= gateExpiry || foregroundThread() !== guiThread || !idle())
            throw Error('Frame or authorization gate changed before dispatch');
        const invoke = new NativeFunction(dispatcher, 'uint32', ['uint32','pointer'], 'win64');
        send({event:'WILL_DISPATCH_ONCE', command:17, thread:this.threadId, selected});
        active = true;
        const status = invoke(17, payload);
        active = false;
        send({event:'DISPATCH_RETURN', status, today:readToday().raw, frame_idle:idle()});
        if (status !== 0x504521a8 || !idle() || foregroundThread() !== guiThread)
            throw Error('Native return or foreground state requires reconciliation');
        const capture = verifyWindow(true);
        const boxes = capture.rows.filter(row => row.day <= selected)
            .map(({id, header, box}) => ({id, header_hex:header, box_hex:box}));
        for (let i = 0; i < boxes.length; i += 8)
            send({event:'REA_POST_SIM_BOX_UNIT', part:i / 8, total:Math.ceil(boxes.length / 8),
                pid:Process.id, today_raw:capture.today.raw, games:boxes.slice(i, i + 8)});
        send({event:'NEXT_DAY_PENDING', ids:capture.rows.filter(row => row.day === next).map(row => row.id)});
        out('RETURNED_WITH_NATIVE_READBACK');
    } catch (error) {
        active = false;
        send({event:'STOP', detail:String(error)});
        out('PAUSE_AND_RECONCILE');
    }
}});
setTimeout(() => {
    if (!decided) {
        decided = true;
        out('FRAME_GATE_NOT_OBSERVED');
    }
}, 6500);
