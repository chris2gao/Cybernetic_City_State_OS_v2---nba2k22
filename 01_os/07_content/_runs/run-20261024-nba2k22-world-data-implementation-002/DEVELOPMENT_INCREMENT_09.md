# Increment 09 — actual settings words and registered league rules

Full engineering goal remains **active and incomplete**. Code candidate: `7cb6e41e`. Schema v8 has **74 STRICT tables and 944 columns**. This increment extends existing settings/rule tables, adds a bounded read-only source adapter, queries, raw-word/semantic quality and consistency checks. Whole-system managed verification, independent review and Human final acceptance remain pending.

## Restart and save binding

Human reported NBA2K22 restart. Host process inventory and the new worker both confirm **PID 8784**. PID 2564 is historical; no previous handle or heap address was reused to acquire these samples. Every capture resolves module/root/descriptor pointers afresh and rereads controls. Engineering save ID remains `nba2k22_test_01`, bound by Human to `E:\games\NBA 2K22\data\steam\steam_settings\1644960\remote\MyLEAGUE0003`. Restart alone does not create another save identity. Human will announce a filename switch.

The elevated worker opened the process with **0x1010 VM_READ | QUERY_LIMITED_INFORMATION** only. No write/injection capability, game date advance or native save write was used. The settings source requests no PLAYER structures. Antigravity was not dispatched; optional batch research remains Human-relayed.

## Source, semantics and implementation

The actual settings source yielded **546 four-byte words**: one preset code, 126 USER/CPU pairs in each of current/custom banks (504 float words), and 41 other registered global words. The adapter uses the registered world/settings/court slot layouts, reads the 2020-byte TUNEDATA_SAVED window in bounded chunks and individual four-byte global words, then checks fresh TEAM/TEAM_STATS season context and rereads all controls.

Duplicate catalog entries become aliases for one physical cell. The source dictionary gains 168 versioned logical field identities; current/custom and USER/CPU are separate observation scopes. Each observed word retains its unsigned raw bit pattern, exact uint32 or finite float32 interpretation (no scaling), explicit nonfinite diagnostic if needed, candidate-range status, sanitized aliases and semantic qualification. Profile default/target/recommendation values never become state or get applied. No parameter optimizer or writer is implemented.

**35 registered league-word observations** reference the matching setting observation in the same consistency unit. SQLite rejects older-unit references or differing int/float/text values. The observations do not assert CBA effects or external gameplay policy. The public global contract factor registered as `player_potential_factor` is a league configuration knob, not a hidden PLAYER attribute or a player-derived estimate.

One actual uint32 word registered as `max_contract_rating` is **40**, outside the old candidate minimum. The source bytes/value remain 40 with an explicit range discrepancy. A candidate range, catalog alias and observed word are separate claims. Static PE inspection found the expected executable build but did not resolve current global NativeType descriptors. Most Slider index names, current UI ranges/scales/effects and the remaining league settings remain gaps; all observations are qualified registered layouts, not current descriptor/UI certification.

## Durable queries and history verification

`capture-settings PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT_DIRECTORY` acquires, decodes, validates and atomically ingests actual source data using the live adapter receipt. Serializable fixture assertions cannot promote themselves to LIVE_READ. `settings DB [--scope-code CURRENT:USER]` and `rules DB [--season-id SEASON]` return bounded snapshots with source time, grade and semantic/range state. A too-small result cap fails explicitly. Role results omit pointers, source paths and raw PLAYER material.

Copy migration **v7 -> v8** retained the old DB/declaration and preserved **95,247 old rows**, compared across every old column. Original v7 whole-file hash still equals the increment08 archived hash. The actual-source audit compared **754 typed records** (168 metadata + 546 settings + 35 rules + 5 gaps), traced all source chunks/words to successful Windows read hashes, and checked typed decodes, integrity/FKs, actual query counts and exports. Current native fact unit is `settings:65f1ecac8394e6c8e514bc12` with source grade LIVE_READ.

Development suite passed **68 tests in 24.739 seconds**. New cases cover every source word, alias deduplication/default exclusion, USER/CPU and current/custom boundaries, nonfinite word preservation, out-of-candidate values, corrupt decode rejection, exact-unit/value rule links and transaction rollback. Seven retained example DBs are research fixture replay; they are not fresh acquisition evidence. Source fixture byte hashes are preserved through Git attributes.

Artifacts under `06_执行/increment09/`: compressed exact v8 fact DB; actual probe/capture archives; PE inspection and script; source/binding manifests; settings/rules query and JSONL exports; executed audit; full development logs, reports and compressed fixture databases. `settings_world_report.json` is the actual-source audit; `verification/development_report.json` documents fixture-based regression checks.

Publication preflight initially found two older task-packet omissions: the expected remote master and the confirmation-closure metadata. The packet now records the freshly read master and the existing Human-admin approval for read-only test-process access. This is a record of supplied authority, not a new grant; master integration, game/save writes, independent review and Human acceptance remain outside this engineering publication. The original blocked preflight is retained with its corrected result.

Remaining full-goal scope includes actual honors/records/news, global setting descriptors/full UI names/ranges/scale and remaining league rules, global rotation/training focus/safe history/mentor effect, unresolved game-player IDs, lifecycle/calendar/badge/contract/finance semantics, market availability/prospect class/year/G League, pick protections/swaps/results, capacity/recovery/role coverage and completed-candidate independent/Human acceptance. No Q10 exception is assumed. Master remains untouched.
