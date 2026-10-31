/**
 * NBA 2K22 MyCAREER Offline Team Practice Unlocker & Loading Fix
 * 
 * Target: NBA2K22.exe (SHA256: 1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5)
 * Base: 0x140000000
 */

var mainMod = Process.findModuleByName('NBA2K22.exe');
if (!mainMod) {
    send({error: 'Could not find NBA2K22.exe module'});
} else {
    var base = mainMod.base;
    send({status: 'Attached to NBA2K22.exe', base: base.toString()});

    var pStatusGlobal = base.add(0x6351848);
    var pTrackingFlag = base.add(0x6352124);
    var pContextGlobal = base.add(0x6327470);

    // 0. Network Job Bypass Guard: CAREERMODE_PROGRESSION::GET_SERVER_DATA_JOB::CreateAndSendRequest (RVA: 0x1239230)
    var pCreateAndSend = base.add(0x1239230);
    Interceptor.attach(pCreateAndSend, {
        onEnter: function(args) {
            var pJob = args[0];
            var s30 = pJob.add(0x30).readS32();
            var s34 = pJob.add(0x34).readS32();

            send({
                event: 'CreateAndSendRequest_Intercepted',
                pJob: pJob.toString(),
                status_0x30_before: s30,
                status_0x34_before: s34,
                global_0x146351848_before: pStatusGlobal.readS32()
            });

            // Mark job and global network status as COMPLETED (2) immediately to bypass 96% wait
            pJob.add(0x30).writeS32(2);
            pStatusGlobal.writeS32(2);

            send({
                event: 'NetworkJob_Bypassed',
                status_0x30_after: 2,
                global_0x146351848_after: 2
            });
        }
    });

    // 0b. Global Status Watcher: prevent async socket errors from reverting 0x146351848 to 3
    setInterval(function() {
        if (pStatusGlobal.readS32() === 3) {
            pStatusGlobal.writeS32(2);
            send({event: 'Status_3_Reverted_To_2'});
        }
    }, 100);

    // 1. Entrance Guard: TK_WORLD::ACTIVITY2_TEAMPRACTICEFACILITY::CreatePlayers (RVA: 0x163f4a0)
    var pCreatePlayers = base.add(0x163f4a0);
    Interceptor.attach(pCreatePlayers, {
        onEnter: function(args) {
            var pThis = args[0]; // rcx
            var practiceType = pThis.add(0x488).readU32();
            send({
                event: 'CreatePlayers_Enter',
                pThis: pThis.toString(),
                practiceType_before: practiceType
            });
            if (practiceType === 0) {
                pThis.add(0x488).writeU32(1);
                send({event: 'PracticeTypePatched', from: 0, to: 1});
            }
        },
        onLeave: function(retval) {
            send({event: 'CreatePlayers_Leave', retval: retval.toString()});
        }
    });

    // 2. Scene State Machine Monitor: ACTIVITY2_TEAMPRACTICEFACILITY::StateDispatch (RVA: 0x1731d30)
    var pStateDispatch = base.add(0x1731d30);
    Interceptor.attach(pStateDispatch, {
        onEnter: function(args) {
            var state = args[0].add(0x310).readS32();
            send({
                event: 'Activity_StateDispatch',
                activity: args[0].toString(),
                state: state
            });
        }
    });

    // 3. Reward & Badge XP Guard: CAREERMODE_DELEGATE::LiveDrill_HandleCalculateResults (RVA: 0x11f8680)
    var pHandleDrillResults = base.add(0x11f8680);
    Interceptor.attach(pHandleDrillResults, {
        onEnter: function(args) {
            var drillType = args[1].toInt32();
            var stars = args[2].toInt32();

            // Force 3-Star max rating for maximum badge progression
            args[2] = ptr(3);

            // Ensure tracking flag is active (1) during reward payout
            if (pTrackingFlag.readS32() === 0) {
                pTrackingFlag.writeS32(1);
            }
            send({event: 'DrillRewardPatched', drillType: drillType, originalStars: stars, forcedStars: 3});
        }
    });

    // 4. Exit Guard: CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded (RVA: 0x11f8bf0)
    var pPracticeEnded = base.add(0x11f8bf0);
    Interceptor.attach(pPracticeEnded, {
        onEnter: function(args) {
            send({event: 'HandleLivePracticeEnded_Enter'});
        },
        onLeave: function(retval) {
            send({event: 'HandleLivePracticeEnded_Leave', status: 'Safe'});
        }
    });

    send({
        status: 'Armed',
        guards: [
            'NetworkBypass_0x1239230',
            'StatusWatcher_0x6351848',
            'CreatePlayers_0x163f4a0',
            'StateDispatch_0x1731d30',
            'LiveDrill_0x11f8680',
            'PracticeEnded_0x11f8bf0'
        ]
    });
}
