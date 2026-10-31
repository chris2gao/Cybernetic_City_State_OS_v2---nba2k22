/**
 * NBA 2K22 MyCAREER Offline Team Practice Patch Runner (V2 - Hardened)
 * 
 * Attaches to NBA2K22.exe using Frida and loads the offline practice facility unlocker,
 * 3-star badge progression enabler, network 96% early-exit bypass, and arena state monitors.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Expected executable identity
const EXPECTED_EXE_SHA256 = '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5';
const EXPECTED_PROCESS_NAME = 'nba2k22.exe';

// Locate Frida from REA bundle or global node_modules
let frida;
const fridaPaths = [
    'C:/Users/gk/AppData/Roaming/npm/node_modules/rea-agents/node_modules/frida',
    'frida'
];

for (const p of fridaPaths) {
    try {
        frida = require(p);
        break;
    } catch (e) {}
}

if (!frida) {
    console.error('[ERROR] Could not load Frida module. Ensure rea-agents or frida is installed.');
    process.exit(1);
}

const scriptPath = path.join(__dirname, 'patch_offline_team_practice.js');
const logPath = path.join(__dirname, 'practice_patch_live.log');

function log(category, msg) {
    const timestamp = new Date().toISOString();
    const formatted = `[${timestamp}] [${category}] ${msg}`;
    console.log(formatted);
    try {
        fs.appendFileSync(logPath, formatted + '\n', 'utf8');
    } catch (e) {}
}

async function verifyExeSha256(procPath) {
    if (!fs.existsSync(procPath)) {
        log('WARN', `Cannot directly read executable at ${procPath} for hash check; skipping disk hash verification.`);
        return true;
    }
    const data = fs.readFileSync(procPath);
    const hash = crypto.createHash('sha256').update(data).digest('hex');
    if (hash.toLowerCase() !== EXPECTED_EXE_SHA256.toLowerCase()) {
        log('FATAL', `Executable SHA256 mismatch!\n  Expected: ${EXPECTED_EXE_SHA256}\n  Actual:   ${hash}`);
        return false;
    }
    log('IDENTITY', `Executable binary SHA256 verified: ${hash}`);
    return true;
}

async function main() {
    log('INIT', '====================================================');
    log('INIT', 'NBA 2K22 MyCAREER Offline Team Practice Unlocker V2');
    log('INIT', 'Target Process: NBA2K22.exe');
    log('INIT', '====================================================');

    if (!fs.existsSync(scriptPath)) {
        log('FATAL', `Patch script file not found: ${scriptPath}`);
        process.exit(1);
    }

    const scriptCode = fs.readFileSync(scriptPath, 'utf8');

    // 1. Enumerate and identify target process
    const device = await frida.getLocalDevice();
    const processes = await device.enumerateProcesses();
    const targetProc = processes.find(p => p.name.toLowerCase() === EXPECTED_PROCESS_NAME);

    if (!targetProc) {
        log('ERROR', 'NBA2K22.exe is not currently running. Please launch the game first.');
        process.exit(1);
    }

    log('IDENTITY', `Located target process: NBA2K22.exe (PID: ${targetProc.pid})`);

    // 2. Attach to process
    const session = await device.attach(targetProc.pid);
    log('ATTACH', `Successfully attached to PID ${targetProc.pid}`);

    session.detached.connect((reason) => {
        log('DETACH', `Target process detached (Reason: ${reason})`);
        process.exit(0);
    });

    // 3. Inject Script
    const script = await session.createScript(scriptCode);

    script.message.connect((message, data) => {
        if (message.type === 'send') {
            const p = message.payload;
            const cat = p.category || 'INFO';

            if (cat === 'HOOK_MOUNTED') {
                log('HOOK_MOUNTED', `Base: ${p.base} | Binary signatures verified | Global status: ${p.global_0x146351848_init}`);
            } else if (cat === 'JOB_INTERCEPTED') {
                log('JOB_INTERCEPTED', `Job: ${p.job_pointer} (vtable: ${p.vtable}) | Pre-status: [job+0x30]=${p.status_0x30_before}, [job+0x34]=${p.status_0x34_before}`);
            } else if (cat === 'JOB_STATE_MODIFIED') {
                log('JOB_STATE_MODIFIED', `Job: ${p.job_pointer} | Modified [job+0x30] -> ${p.status_0x30_after}, global -> ${p.global_0x146351848_after}`);
            } else if (cat === 'JOB_EARLY_EXIT') {
                log('JOB_EARLY_EXIT', `CreateAndSendRequest returned via native early-exit branch (retval=${p.retval}). Network dispatch skipped.`);
            } else if (cat === 'CREATE_PLAYERS_ENTER') {
                log('CREATE_PLAYERS_ENTER', `Activity: ${p.activity_pointer} | PracticeType read: ${p.practiceType_before}`);
            } else if (cat === 'PRACTICE_TYPE_PATCHED') {
                log('PRACTICE_TYPE_PATCHED', `Normalized PracticeType: ${p.from} (UNKNOWN) -> ${p.to} (TEAM_PRACTICE). Assertion prevented.`);
            } else if (cat === 'CREATE_PLAYERS_LEAVE') {
                log('CREATE_PLAYERS_LEAVE', `CreatePlayers returned cleanly (retval=${p.retval}).`);
            } else if (cat === 'SCENE_STATE_CHANGED') {
                log('SCENE_STATE_CHANGED', `State transition: ${p.numeric_state} (${p.state_name}) on Activity ${p.activity}`);
            } else if (cat === 'DRILL_REWARD_ENTER') {
                log('DRILL_REWARD_ENTER', `Drill: ${p.drill_type} | Stars: ${p.stars_original} -> ${p.stars_patched} (Fixed 3-Star Award)`);
            } else if (cat === 'PRACTICE_ENDED_ENTER') {
                log('PRACTICE_ENDED_ENTER', `HandleLivePracticeEnded entered. Clearing practice session state.`);
            } else if (cat === 'PRACTICE_ENDED_LEAVE') {
                log('PRACTICE_ENDED_LEAVE', `HandleLivePracticeEnded completed cleanly (retval=${p.retval}).`);
            } else if (cat === 'ARMED') {
                log('ARMED', `All guards active: ${p.guards.join(', ')}`);
                log('OBSERVATION_REQUIRED', '==============================================================');
                log('OBSERVATION_REQUIRED', 'Ready for Human test! Please click "进入球队训练" on MC calendar.');
                log('OBSERVATION_REQUIRED', 'Observe the following points in-game:');
                log('OBSERVATION_REQUIRED', '  [ ] 1. Does the loading screen progress beyond 96%?');
                log('OBSERVATION_REQUIRED', '  [ ] 2. Does the camera transition into the practice court?');
                log('OBSERVATION_REQUIRED', '  [ ] 3. Are teammates, coaches, and MyPLAYER visible on court?');
                log('OBSERVATION_REQUIRED', '  [ ] 4. Does the controller acquire player movement?');
                log('OBSERVATION_REQUIRED', '  [ ] 5. Does exiting via the gym door return safely to the calendar?');
                log('OBSERVATION_REQUIRED', '==============================================================');
            } else if (cat === 'INJECTION_ABORTED') {
                log('FATAL', p.message);
                process.exit(1);
            } else if (cat === 'SIGNATURE_MISMATCH') {
                log('FATAL', `Signature check failed at ${p.function} (RVA ${p.rva}): expected [${p.expected}], got [${p.actual}]`);
                process.exit(1);
            } else {
                log('PAYLOAD', JSON.stringify(p));
            }
        } else if (message.type === 'error') {
            log('SCRIPT_ERROR', message.stack || message.description);
        }
    });

    await script.load();

    // 4. Handle clean exit
    const cleanup = async () => {
        log('SHUTDOWN', 'Detaching from NBA2K22.exe...');
        try {
            await script.unload();
            await session.detach();
        } catch (e) {}
        log('SHUTDOWN', 'Detached cleanly. Exiting.');
        process.exit(0);
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
}

main().catch((err) => {
    log('FATAL', `${err.message}\n${err.stack}`);
    process.exit(1);
});
