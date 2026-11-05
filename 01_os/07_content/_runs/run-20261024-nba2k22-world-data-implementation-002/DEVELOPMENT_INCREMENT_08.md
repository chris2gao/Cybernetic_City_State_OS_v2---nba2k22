# Increment 08 — stored opponent plans, current training and mentor source

Full goal remains **active and incomplete**. Implementation candidate: `c9116fff`. Schema v7 has **74 STRICT tables and 936 columns**. Added separate plan/rotation/defense observations, training-slot state and mentor header/source observations; expanded existing training/association tables. Whole-system, independent and Human final acceptance remain pending.

## Actual source path

`capture-planning PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT` revalidates current native roster/franchise getters and type/enum metadata, resolves all core franchise managers, reads their registered 35 plan slots and requires the full 29-core-opponent set per team. GAMEPLAN's unpacked byte fields are decoded independently of packed COACHDATA defaults. Every current roster member must be descriptor-aligned, have a nonempty public name, a unique assigned native UID and reciprocal TEAM/PLAYER pointers. Selected records, roots and descriptors are reread to reject changes.

Current PID8784 source proves **461 current roster members** and **870 stored core opponent plans**, with **869 native commit flags0 and one flag1** (team20/opponent0). These flags do not establish played-game effect. The other 180 profile-window plan slots are retained as source controls, not promoted into the core opponent set.

Every accepted plan has 23 source rotation slots and 23 defensive slots: **20,010 rows of each**. Rotation links require exact current own-roster UID; matchup targets require current opponent-roster UID; defenders require current own-roster UID. Sentinel/stale/unmapped references retain raw IDs with NULL canonical FKs. SQLite rejects child rows borrowing an older unit's parent and canonical subjects lacking same-unit roster ownership. Native enums and byte layouts are source evidence, not current UI/effect acceptance.

## Training and mentorship

Thirty team training records yield six registered flags each. PLAYER_TRAINING reads **only four-byte ID and four-byte flags at +0x318**, not the 796-byte record/history arrays. The 786-slot profile bound is explicitly not an active count: **456 unique current-roster IDs**, 35 outside the current core roster and 295 empty sentinels. Only the 456 matched IDs produce canonical player training observations. Duplicate IDs cannot select the first record; they stay source slots. Training focus/schedules and global rotation settings are not fabricated from these fields.

Thirty mentor headers have plausible team/count fields, with **61 relation headers**. All pairs match two distinct current own-roster UIDs, with unique mentee assignment in this capture, so 61 observed associations are recorded. Native duration/compatibility word/badge count remain raw. `association_status=OBSERVED_PAIR_ACTIVITY_NOT_VERIFIED`: no actor consent, badge activity/tier, development effect or outcome is inferred. Badge slot bodies are not read.

No full PLAYER structure, hidden Potential byte, training overall/attribute/history array or mentor badge-slot body is requested by this adapter. Named roster identities use only public name, UID and team-pointer reads. No game/save write, date advance or native activation occurs.

## Queries, migration and verification

`planning DB [--team-id ID] [--limit N]` returns bounded stored-plan/training/association snapshots with commit/source state and training identity counts. `gameplan DB TEAM_ID OPPONENT_ID` returns one latest plan plus ordered rotation/defense rows and any proven current-player names. It explicitly separates observed commit flag from game effect. Privacy projections withhold raw buffers, owner source paths, pointers and Potential.

Copy-upgrade v6 -> v7 retained old files/declarations. Offline audit compared **49,598 old rows** by all previous columns and confirmed the original v6 file still matches increment07's exact byte hash. It then checked **43,272 source-to-typed records**, direct record read hashes, current roster links, plan decodes, training projections, SQLite integrity/FKs and role query/export privacy. Physical read intervals prove zero requests overlapping known PLAYER Potential, training history arrays or mentor badge-slot bodies.

Development suite passed **62 tests in 23.771 seconds**. New fixture cases cover stored-plan/association queries, byte-based plan decoding versus coach offsets, retained flag0 behavior, wrong-team canonical FK rejection and atomic rollback, cross-unit parent rejection, duplicate training-ID staging and ambiguous mentor withholding. Six retained fixture DB examples remain research replay; actual LIVE_READ acquisition is separate evidence.

Artifacts under `06_执行/increment08/`: exact compressed v7 DB, source probe/capture archives and code hashes, binding, source report, bounded planning and one-plan query examples, training/mentor exports, executed audit and development logs. The initial probe and final capture are distinct. Later classifier extraction adds consistency checking without promoting older observations or changing their raw bytes.

Remaining full-goal scope: global rotation, training focus/safe history, mentor badge activity/effect, actual settings/rules/honors/records/news, text play labels, four unresolved game-player identities, lifecycle/calendar/badge/contract/finance semantics, actual market availability, initialized class/year, protection/swaps/results and G League, capacity/recovery/role coverage and completed-candidate independent/Human acceptance. No Q10 exception is assumed. Codex remains Owner; optional Gemini batches use Human relay only. Master remains untouched.
