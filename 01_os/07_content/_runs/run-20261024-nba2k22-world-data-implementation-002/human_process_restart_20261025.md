# Human process restart clarification

Human reported that NBA2K22 had restarted, then explicitly clarified: only the game process changed; everything else is unchanged and the test save has not been touched.

The existing operator declaration remains `nba2k22_test_01 / MyLEAGUE0003` in the previously declared remote save directory. No save switch, game/save write or date-advance authorization is inferred.

The current process was freshly discovered as PID8648 before the increment22 worker was launched. Earlier PID6212 is retired. The worker receives the newly discovered PID, opens it read-only, resolves fresh module/root descriptors and records process-creation/build/year controls. No prior dynamic address is reused. Copy-upgrade concerns the external facts database and retains the v16 file/declaration; it does not change the native game save.

Authoritative actual outcomes and process checkpoints are in `06_执行/increment22/worker-report.json` and `actual-incremental-report.json`; this clarification alone is not proof that a capture completed.
