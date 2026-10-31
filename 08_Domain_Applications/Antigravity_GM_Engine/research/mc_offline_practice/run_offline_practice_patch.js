/**
 * NBA 2K22 MyCAREER Offline Team Practice Patch Runner (V3 - Audited)
 * 
 * Attaches to NBA2K22.exe using Frida after rigorous binary hash validation,
 * loads the offline practice facility unlocker with OS mutex protection and strict scoped guards.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const EXPECTED_EXE_SHA256 = '1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5';
const EXPECTED_PROCESS_NAME = 'nba2k22.exe';

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
    console.error('[FATAL] Could not load Frida module. Ensure rea-agents or frida is installed.');
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

function verifyExeSha256(procPath) {
    if (!procPath || !fs.existsSync(procPath)) {
        log('FATAL', `Process binary file not found on disk: "${procPath}". Cannot proceed without verified binary identity.`);
        return false;
    }
    const data = fs.readFileSync(procPath);
    const hash = crypto.createHash('sha256').update(data).digest('hex');
    if (hash.toLowerCase() !== EXPECTED_EXE_SHA256.toLowerCase()) {
        log('FATAL', `Process binary SHA256 mismatch!\n  Target Path: ${procPath}\n  Expected:    ${EXPECTED_EXE_SHA256}\n  Actual:      ${hash}\nAborting attachment to unverified binary.`);
        return false;
    }
    log('IDENTITY', `Target executable verified successfully: ${procPath} (SHA256: ${hash})`);
    return true;
}

async function main() {
    log('INIT', '====================================================');
    log('INIT', 'NBA 2K22 MyCAREER Offline Team Practice Unlocker V3');
    log('INIT', 'Target: NBA2K22.exe (Strict Identity & Scoped Guard)');
    log('INIT', '====================================================');

    if (!fs.existsSync(scriptPath)) {
        log('FATAL', `Patch script file not found at ${scriptPath}`);
        process.exit(1);
    }

    const scriptCode = fs.readFileSync(scriptPath, 'utf8');

    // 1. Locate target process
    const device = await frida.getLocalDevice();
    const processes = await device.enumerateProcesses();
    const targetProc = processes.find(p => p.name.toLowerCase() === EXPECTED_PROCESS_NAME);

    if (!targetProc) {
        log('FATAL', 'NBA2K22.exe is not currently running. Please launch the game first.');
        process.exit(1);
    }

    log('IDENTITY', `Located target process: NBA2K22.exe (PID: ${targetProc.pid})`);

    // 2. Query exact disk path and verify SHA256 BEFORE attaching
    let procPath = '';
    try {
        procPath = execSync(`powershell -NoProfile -Command "(Get-Process -Id ${targetProc.pid} -ErrorAction Stop).Path"`, { encoding: 'utf8' }).trim();
    } catch (e) {
        log('FATAL', `Failed to query executable path for PID ${targetProc.pid}: ${e.message}`);
        process.exit(1);
    }

    if (!verifyExeSha256(procPath)) {
        log('FATAL', 'Binary verification failed. Aborting.');
        process.exit(1);
    }

    // 3. Attach to process
    const session = await device.attach(targetProc.pid);
    log('ATTACH', `Successfully attached to PID ${targetProc.pid}`);

    session.detached.connect((reason) => {
        log('DETACH', `Target process detached (Reason: ${reason})`);
        process.exit(0);
    });

    // 4. Inject Script
    const script = await session.createScript(scriptCode);

    script.message.connect((message, data) => {
        if (message.type === 'send') {
            const p = message.payload;
            const cat = p.category || 'INFO';

            if (cat === 'HOOK_MOUNTED') {
                log('HOOK_MOUNTED', `Base: ${p.base} | Signatures verified | Global 0x146351848: ${p.global_0x146351848_init}`);
            } else if (cat === 'JOB_FUNCTION_HIT') {
                log('JOB_FUNCTION_HIT', `Job: ${p.job_pointer} (vtable: ${p.vtable}, caller: RVA 0x${p.caller_rva}) | Status 0x30: ${p.status_0x30_before}, 0x34: ${p.status_0x34_before}`);
            } else if (cat === 'JOB_SKIPPED_UNCONFIRMED') {
                log('JOB_SKIPPED_UNCONFIRMED', `Reason: ${p.reason} | ${p.message}`);
            } else if (cat === 'JOB_IDENTIFIED') {
                log('JOB_IDENTIFIED', `Confirmed target job: ${p.job_pointer} (matches GET_SERVER_DATA_JOB vtable).`);
            } else if (cat === 'JOB_STATE_MODIFIED') {
                log('JOB_STATE_MODIFIED', `Job: ${p.job_pointer} | Modified [job+0x30] -> ${p.status_0x30_after}, global -> ${p.global_0x146351848_after}`);
            } else if (cat === 'JOB_ORIGINAL_FUNCTION_RETURNED') {
                log('JOB_ORIGINAL_FUNCTION_RETURNED', `CreateAndSendRequest returned (retval=${p.retval}). Native early-exit branch taken.`);
            } else if (cat === 'PRACTICE_SCENE_LOADING') {
                log('PRACTICE_SCENE_LOADING', `Scene state: ${p.numeric_state} (${p.state_name}) on Activity ${p.activity}`);
            } else if (cat === 'CREATE_PLAYERS_HIT') {
                log('CREATE_PLAYERS_HIT', `CreatePlayers entered on Activity ${p.activity_pointer} | Current PracticeType: ${p.practiceType_before}`);
            } else if (cat === 'PRACTICE_TYPE_NORMALIZED') {
                log('PRACTICE_TYPE_NORMALIZED', `Normalized PracticeType: ${p.from} (UNKNOWN) -> ${p.to} (TEAM_PRACTICE). Assertion avoided.`);
            } else if (cat === 'PLAYERS_INSTANTIATED') {
                log('PLAYERS_INSTANTIATED', `CreatePlayers returned cleanly (retval=${p.retval}).`);
            } else if (cat === 'DRILL_REWARD_PROCESSED') {
                log('DRILL_REWARD_PROCESSED', `Drill: ${p.drill_type} | Stars: ${p.stars_original} -> ${p.stars_patched} (Fixed 3-Star Award)`);
            } else if (cat === 'PRACTICE_EXIT_TRIGGERED') {
                log('PRACTICE_EXIT_TRIGGERED', `HandleLivePracticeEnded entered. Cleaning up practice state.`);
            } else if (cat === 'PRACTICE_EXIT_RETURNED') {
                log('PRACTICE_EXIT_RETURNED', `HandleLivePracticeEnded returned cleanly (retval=${p.retval}).`);
            } else if (cat === 'ARMED') {
                log('ARMED', `Guards active: ${p.guards.join(', ')}`);
                log('OBSERVATION_REQUIRED', '==============================================================');
                log('OBSERVATION_REQUIRED', 'Ready for Human observation. Please click "进入球队训练" on MC calendar.');
                log('OBSERVATION_REQUIRED', 'Checklist for Human in-game confirmation:');
                log('OBSERVATION_REQUIRED', '  [ ] 1. Does the loading screen progress beyond 96%?');
                log('OBSERVATION_REQUIRED', '  [ ] 2. Does the camera view transition into the practice court?');
                log('OBSERVATION_REQUIRED', '  [ ] 3. Are teammates, coaches, and MyPLAYER visible on court?');
                log('OBSERVATION_REQUIRED', '  [ ] 4. Does the controller/keyboard move the MyPLAYER character?');
                log('OBSERVATION_REQUIRED', '  [ ] 5. Does exiting through the gym door return safely to the calendar?');
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

    // 5. Clean exit handling
    const cleanup = async () => {
        log('SHUTDOWN', 'Detaching from NBA2K22.exe and releasing OS Mutex...');
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
