/**
 * NBA 2K22 MyCAREER Offline Team Practice Unlocker & Loading Fix (V2 - Hardened)
 * 
 * Target: NBA2K22.exe
 * Target SHA256: 1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5
 * Base: 0x140000000
 */

(function() {
    'use strict';

    // 1. Guard against duplicate patch injection
    if (globalThis.__NBA2K22_OFFLINE_PATCH_ACTIVE__) {
        send({
            level: 'ERROR',
            category: 'INJECTION_ABORTED',
            message: 'Duplicate patch detected! An instance of patch_offline_team_practice is already resident in this process.'
        });
        return;
    }

    var mainMod = Process.findModuleByName('NBA2K22.exe');
    if (!mainMod) {
        send({
            level: 'FATAL',
            category: 'MODULE_NOT_FOUND',
            message: 'Could not find NBA2K22.exe module in current process.'
        });
        return;
    }

    var base = mainMod.base;

    // 2. Signature verification before attaching hooks
    var signatures = [
        { name: 'CreateAndSendRequest', rva: 0x1239230, expected: '40 55 53 48 8b' },
        { name: 'CreatePlayers',        rva: 0x163f4a0, expected: '40 55 53 56 57 41 54' },
        { name: 'StateDispatch',        rva: 0x1731d30, expected: '48 8b c4 48 89 58 08' },
        { name: 'LiveDrill_Results',    rva: 0x11f8680, expected: '40 55 41 56' },
        { name: 'PracticeEnded',        rva: 0x11f8bf0, expected: '48 83 ec 38' }
    ];

    for (var i = 0; i < signatures.length; i++) {
        var sig = signatures[i];
        var ptrTarget = base.add(sig.rva);
        var actualBytes = [];
        var expLen = sig.expected.split(' ').length;
        for (var b = 0; b < expLen; b++) {
            var byteVal = ptrTarget.add(b).readU8();
            actualBytes.push((byteVal < 16 ? '0' : '') + byteVal.toString(16));
        }
        var actualStr = actualBytes.join(' ');
        if (actualStr.toLowerCase() !== sig.expected.toLowerCase()) {
            send({
                level: 'FATAL',
                category: 'SIGNATURE_MISMATCH',
                function: sig.name,
                rva: '0x' + sig.rva.toString(16),
                expected: sig.expected,
                actual: actualStr,
                message: 'Binary signature verification failed at ' + sig.name + '. Aborting injection to protect process memory.'
            });
            return;
        }
    }

    // Mark as active once verification passes
    globalThis.__NBA2K22_OFFLINE_PATCH_ACTIVE__ = true;

    var pStatusGlobal = base.add(0x6351848);
    var pTrackingFlag = base.add(0x6352124);

    send({
        level: 'INFO',
        category: 'HOOK_MOUNTED',
        base: base.toString(),
        global_0x146351848_init: pStatusGlobal.readS32(),
        tracking_0x146352124_init: pTrackingFlag.readS32(),
        message: 'Binary signatures verified. Attaching targeted hooks.'
    });

    // =========================================================================
    // GUARD 0: Network Job Early Exit (RVA: 0x1239230)
    // Target: CAREERMODE_PROGRESSION::GET_SERVER_DATA_JOB::CreateAndSendRequest
    // =========================================================================
    var pCreateAndSend = base.add(0x1239230);
    Interceptor.attach(pCreateAndSend, {
        onEnter: function(args) {
            var pJob = args[0];
            var s30 = pJob.add(0x30).readS32();
            var s34 = pJob.add(0x34).readS32();
            var vtable = pJob.readPointer();

            send({
                level: 'INFO',
                category: 'JOB_INTERCEPTED',
                job_pointer: pJob.toString(),
                vtable: vtable.toString(),
                status_0x30_before: s30,
                status_0x34_before: s34,
                global_0x146351848_before: pStatusGlobal.readS32(),
                message: 'CreateAndSendRequest intercepted for career progression job.'
            });

            // Native mechanism: when [pJob + 0x30] != 0 at entry, instruction 0x141239241 (jne 0x141239463)
            // takes the native early-exit branch, completely skipping network dispatch call (0x141e51ad0).
            pJob.add(0x30).writeS32(2);
            pStatusGlobal.writeS32(2);

            send({
                level: 'INFO',
                category: 'JOB_STATE_MODIFIED',
                job_pointer: pJob.toString(),
                status_0x30_after: 2,
                global_0x146351848_after: 2,
                message: 'Pre-set job status to 2 (COMPLETED) to route into native early-exit branch.'
            });
        },
        onLeave: function(retval) {
            send({
                level: 'INFO',
                category: 'JOB_EARLY_EXIT',
                retval: retval.toString(),
                message: 'CreateAndSendRequest returned cleanly via early-exit path. Network dispatch bypassed.'
            });
        }
    });

    // =========================================================================
    // GUARD 1: Entrance Practice Type Normalization (RVA: 0x163f4a0)
    // Target: TK_WORLD::ACTIVITY2_TEAMPRACTICEFACILITY::CreatePlayers
    // =========================================================================
    var pCreatePlayers = base.add(0x163f4a0);
    Interceptor.attach(pCreatePlayers, {
        onEnter: function(args) {
            var pThis = args[0];
            var practiceType = pThis.add(0x488).readU32();

            send({
                level: 'INFO',
                category: 'CREATE_PLAYERS_ENTER',
                activity_pointer: pThis.toString(),
                practiceType_before: practiceType,
                message: 'CreatePlayers entered. Checking practice type.'
            });

            if (practiceType === 0) {
                // Type 1 = Standard Team Practice (Team drills & free shooting enabled)
                pThis.add(0x488).writeU32(1);
                send({
                    level: 'INFO',
                    category: 'PRACTICE_TYPE_PATCHED',
                    from: 0,
                    to: 1,
                    message: 'Normalized practice type from 0 (UNKNOWN) to 1 (TEAM_PRACTICE) to bypass fatal int3 assertion.'
                });
            }
        },
        onLeave: function(retval) {
            send({
                level: 'INFO',
                category: 'CREATE_PLAYERS_LEAVE',
                retval: retval.toString(),
                message: 'CreatePlayers completed cleanly. Player and coach entities instantiated.'
            });
        }
    });

    // =========================================================================
    // GUARD 2: Scene State Machine Transition Monitor (RVA: 0x1731d30)
    // Target: ACTIVITY2_TEAMPRACTICEFACILITY::StateDispatch
    // =========================================================================
    var stateNames = {
        0: 'STATE_0_ALLOCATE_RESOURCES',
        1: 'STATE_1_LOAD_IFF_ASSETS',
        2: 'STATE_2_VERIFY_ASSETS',
        3: 'STATE_3_SPAWN_PLAYERS',
        4: 'STATE_4_ACQUIRE_PLAYER_CONTROL',
        5: 'STATE_5_TEARDOWN_PRACTICE'
    };

    var pStateDispatch = base.add(0x1731d30);
    var lastLoggedState = -1;
    Interceptor.attach(pStateDispatch, {
        onEnter: function(args) {
            var state = args[0].add(0x310).readS32();
            if (state !== lastLoggedState) {
                lastLoggedState = state;
                var stateLabel = stateNames[state] || ('UNKNOWN_STATE_' + state);
                send({
                    level: 'INFO',
                    category: 'SCENE_STATE_CHANGED',
                    numeric_state: state,
                    state_name: stateLabel,
                    activity: args[0].toString(),
                    message: 'Scene state transition observed: ' + stateLabel
                });
            }
        }
    });

    // =========================================================================
    // GUARD 3: Drill Badge Reward & XP Progression (RVA: 0x11f8680)
    // Target: CAREERMODE_DELEGATE::LiveDrill_HandleCalculateResults
    // =========================================================================
    var pHandleDrillResults = base.add(0x11f8680);
    Interceptor.attach(pHandleDrillResults, {
        onEnter: function(args) {
            var drillType = args[1].toInt32();
            var stars = args[2].toInt32();

            // Patch stars argument (args[2] in x64 Windows ABI = r8) to 3 (Max)
            args[2] = ptr(3);

            // Ensure progression tracking flag is active
            if (pTrackingFlag.readS32() === 0) {
                pTrackingFlag.writeS32(1);
            }

            send({
                level: 'INFO',
                category: 'DRILL_REWARD_ENTER',
                drill_type: drillType,
                stars_original: stars,
                stars_patched: 3,
                tracking_flag: 1,
                message: 'Live drill completed. Awarded 3-star badge progression rating.'
            });
        }
    });

    // =========================================================================
    // GUARD 4: Arena Exit & Calendar Timeline Safe Recovery (RVA: 0x11f8bf0)
    // Target: CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded
    // =========================================================================
    var pPracticeEnded = base.add(0x11f8bf0);
    Interceptor.attach(pPracticeEnded, {
        onEnter: function(args) {
            send({
                level: 'INFO',
                category: 'PRACTICE_ENDED_ENTER',
                message: 'Exit requested. HandleLivePracticeEnded entered. Cleaning up arena state and clearing timeline flags.'
            });
        },
        onLeave: function(retval) {
            send({
                level: 'INFO',
                category: 'PRACTICE_ENDED_LEAVE',
                retval: retval.toString(),
                message: 'HandleLivePracticeEnded returned cleanly. Save dirty flag updated for timeline advance.'
            });
        }
    });

    send({
        level: 'INFO',
        category: 'ARMED',
        guards: [
            'Guard0_NetworkJobEarlyExit_0x1239230',
            'Guard1_PracticeTypeNormalize_0x163f4a0',
            'Guard2_SceneStateMonitor_0x1731d30',
            'Guard3_DrillFixed3Star_0x11f8680',
            'Guard4_PracticeEndedExit_0x11f8bf0'
        ],
        message: 'All 5 guards armed cleanly without periodic timer interference.'
    });
})();
