/**
 * NBA 2K22 MyCAREER Offline Team Practice Patch Runner
 * 
 * Attaches to NBA2K22.exe using Frida and loads the offline practice facility unlocker,
 * 3-star badge progression enabler, network 96% bypass, and crash prevention interceptors.
 */

const fs = require('fs');
const path = require('path');

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

function log(msg) {
    const timestamp = new Date().toISOString();
    const formatted = `[${timestamp}] ${msg}`;
    console.log(formatted);
    try {
        fs.appendFileSync(logPath, formatted + '\n', 'utf8');
    } catch (e) {}
}

async function main() {
    log('====================================================');
    log('NBA 2K22 MyCAREER Offline Team Practice Unlocker');
    log('Target Process: NBA2K22.exe');
    log('====================================================');

    if (!fs.existsSync(scriptPath)) {
        log(`[FATAL] Script file not found: ${scriptPath}`);
        process.exit(1);
    }

    const scriptCode = fs.readFileSync(scriptPath, 'utf8');

    // 1. Find process
    const device = await frida.getLocalDevice();
    const processes = await device.enumerateProcesses();
    const targetProc = processes.find(p => p.name.toLowerCase() === 'nba2k22.exe');

    if (!targetProc) {
        log('[ERROR] NBA2K22.exe is not currently running. Please launch the game first.');
        process.exit(1);
    }

    log(`[INFO] Found target process: NBA2K22.exe (PID: ${targetProc.pid})`);

    // 2. Attach
    const session = await device.attach(targetProc.pid);
    log(`[INFO] Attached to process PID ${targetProc.pid}`);

    session.detached.connect((reason) => {
        log(`[SESSION] Target process detached (Reason: ${reason})`);
        process.exit(0);
    });

    // 3. Inject Script
    const script = await session.createScript(scriptCode);
    script.message.connect((message, data) => {
        if (message.type === 'send') {
            const payload = message.payload;
            if (payload.event === 'NetworkJob_Bypassed') {
                log(`>>> [INTERCEPT: NETWORK] 96% Freeze Bypass Triggered! Job status -> ${payload.status_0x30_after}, Global status -> ${payload.global_0x146351848_after}. Network send skipped!`);
            } else if (payload.event === 'CreateAndSendRequest_Intercepted') {
                log(`>>> [INTERCEPT: NETWORK] CreateAndSendRequest intercepted on job ${payload.pJob} (s30=${payload.status_0x30_before}, global=${payload.global_0x146351848_before})`);
            } else if (payload.event === 'Status_3_Reverted_To_2') {
                log(`>>> [INTERCEPT: NETWORK] Guard reset pending network status (3 -> 2).`);
            } else if (payload.event === 'Activity_StateDispatch') {
                log(`>>> [INTERCEPT: SCENE] Team Practice Facility State -> ${payload.state}`);
            } else if (payload.event === 'PracticeTypePatched') {
                log(`>>> [INTERCEPT: ENTRY] Team Practice type patched from UNKNOWN (${payload.from}) -> ACTIVE (${payload.to}). Assertion crash prevented!`);
            } else if (payload.event === 'CreatePlayers_Enter') {
                log(`>>> [INTERCEPT: ENTRY] CreatePlayers entered (PracticeType=${payload.practiceType_before}). Instantiating court players...`);
            } else if (payload.event === 'CreatePlayers_Leave') {
                log(`>>> [INTERCEPT: ENTRY] CreatePlayers completed cleanly.`);
            } else if (payload.event === 'DrillRewardPatched') {
                log(`>>> [INTERCEPT: REWARD] Drill type ${payload.drillType} completed! Stars upgraded: ${payload.originalStars} -> ${payload.forcedStars} (Max 3-Star Badge XP + MyPOINTS awarded).`);
            } else if (payload.event === 'HandleLivePracticeEnded_Enter') {
                log(`>>> [INTERCEPT: EXIT] HandleLivePracticeEnded entered. Cleaning up practice session state...`);
            } else if (payload.event === 'HandleLivePracticeEnded_Leave') {
                log(`>>> [INTERCEPT: EXIT] HandleLivePracticeEnded complete (Status: ${payload.status}). Save state clean and safe!`);
            } else if (payload.status === 'Armed') {
                log(`[SUCCESS] Patch is ARMED! Active Guards: ${payload.guards.join(', ')}`);
                log('[READY] You can now click "进入球队训练" on the MC calendar.');
            } else {
                log(`[PAYLOAD] ${JSON.stringify(payload)}`);
            }
        } else if (message.type === 'error') {
            log(`[SCRIPT ERROR] ${message.stack || message.description}`);
        }
    });

    await script.load();

    // 4. Handle clean exit
    const cleanup = async () => {
        log('[INFO] Stopping patch and detaching from NBA2K22.exe...');
        try {
            await script.unload();
            await session.detach();
        } catch (e) {}
        log('[INFO] Detached cleanly. Exiting.');
        process.exit(0);
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);

    // Keep running
    log('[RUNNING] Patch daemon is running. Press Ctrl+C to stop.');
}

main().catch((err) => {
    log(`[FATAL ERROR] ${err.message}\n${err.stack}`);
    process.exit(1);
});
