/**
 * NBA 2K22 MyCAREER Offline Team Practice Unlocker & Reward Fix
 * 
 * Target: NBA2K22.exe (SHA256: 1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5)
 */

var mainMod = Process.findModuleByName('NBA2K22.exe');
if (!mainMod) {
    send({error: 'Could not find NBA2K22.exe module'});
} else {
    var base = mainMod.base;
    send({status: 'Attached to NBA2K22.exe', base: base.toString()});

    // 1. Entrance Guard: TK_WORLD::ACTIVITY2_TEAMPRACTICEFACILITY::CreatePlayers (RVA: 0x163f4a0)
    var pCreatePlayers = base.add(0x163f4a0);
    Interceptor.attach(pCreatePlayers, {
        onEnter: function(args) {
            var pThis = args[0]; // rcx
            var practiceType = pThis.add(0x488).readU32();
            if (practiceType === 0) {
                pThis.add(0x488).writeU32(1);
                send({event: 'PracticeTypePatched', from: 0, to: 1});
            }
        }
    });

    // 2. Reward & Badge XP Guard: CAREERMODE_DELEGATE::LiveDrill_HandleCalculateResults (RVA: 0x11f8680)
    var pHandleDrillResults = base.add(0x11f8680);
    var pTrackingFlag = base.add(0x11dfe33 + 7 + 0x51722ea); // 0x146352124
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

    // 3. Exit Guard: CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded (RVA: 0x11f8bf0)
    var pPracticeEnded = base.add(0x11f8bf0);
    Interceptor.attach(pPracticeEnded, {
        onEnter: function(args) {
            send({event: 'HandleLivePracticeEnded_Enter'});
        },
        onLeave: function(retval) {
            send({event: 'HandleLivePracticeEnded_Leave', status: 'Safe'});
        }
    });

    send({status: 'Armed', guards: ['CreatePlayers_0x163f4a0', 'LiveDrill_0x11f8680', 'PracticeEnded_0x11f8bf0']});
}
