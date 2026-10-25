# Increment 22 — actual incremental Native Box reading

Previous goal turn was progress: increment21 delivered and actually exercised the thirteen-source manual refresh. This increment continues the same full engineering goal with runtime candidate **`cf2479399afdbf762c6833b8f2c91ad4a12e9c99`**. Schema is now **v17 / 85 STRICT tables / 1,315 columns**. Complete independent/Human acceptance is still outstanding.

## Why and what changed

The S1 baseline already had Native position, hand, jersey number, YearsPro and raw birth components in the player-state source; those were inspected and not reimplemented. The material missing behavior was ordinary schedule capture rereading every historical final Box. The related upstream runtime/prototype policy candidate at `origin/task/nba2k22-world-runtime-and-prototype-contract-20261025@be9178b9` was read as context, not merged or treated as an automatic amendment to the active task packet.

New typed `game_source_checks` separates an actually observed 60-byte game-header hash, actual Box-byte hash when read, acquisition/reuse mode, status, origin unit and explicit reuse basis. Ordinary capture considers only a prior successful LIVE_READ full capture in the same native season. Eligibility additionally requires a final state, eight regulation period rows, both team Boxes and complete per-side canonical/native captured participant identity and points mapping. A newer incomplete full capture disqualifies reuse rather than silently falling back to an earlier complete one.

When the current header matches that eligible frozen source, the collector reads no old Box bytes and inserts no duplicate state/period/player/team/native Box rows for that game. It appends a header-check row pointing to the prior full unit. Missing metadata, changed headers, new finals and incomplete mappings require a full Native read and recheck. Non-finals receive header checks and their actually observed current status, with no invented zero scores.

Matching a header does **not** prove equality of unread Box bytes. The contract is reuse of already frozen facts with a separately recorded current header check. `capture-season ... --recheck-frozen` explicitly rereads finals when reconciliation is needed, including possible changes that do not alter a header. Existing frozen-value guards continue rejecting contradictory observations; raw failure evidence is retained for adjudication instead of rewriting old facts.

`game` still returns state/period/Box arrays from exactly one selected unit. `latest_header_check` is separate metadata. A later reuse check never refreshes the Box's original source time. Historical acquisition cutoffs filter both independently. The full native schedule/index and context controls are still read/rechecked each request.

Current player context no longer needs a historical game/Box anchor. The collector resolves fresh core-team rosters and explicit new-game subjects, checks reciprocal current team/name controls and duplicate/out-of-pool roster pointers, then acquires the existing public fields/available Slot24 totals. A new-season window without final games is supported. Totals from another native year are withheld rather than relabeled; unresolved identities and missing totals remain explicit. This does not establish cross-session player lifecycle or UI semantics.

## Actual new-process execution

Human confirmed that only the game process restarted; the test save and other conditions were unchanged. The launch independently discovered **PID8648**. PID6212 is retired. The worker uses fresh process creation/build/year controls and fresh module/root descriptors, with the same checked context before/after both captures. The declared save remains `nba2k22_test_01 / MyLEAGUE0003`.

The existing copy-upgrade path migrated v16 to a new `world-v17.sqlite`, retained `world-v16.sqlite` and the previous declaration, then changed only the external database pointer. **All1,318,485 prior rows across84 tables are preserved by every old column**, except the necessary current `saves.schema_version` header change16→17. The original v16 file remains bit-for-bit SHA256 `5862abf394bf831b6f37cfd0f52c274f7d05bbfd41701f22761228505e93761c`. Save identity fields are unchanged.

The first v17 capture establishes source-check metadata. It reads all238 existing finals and checks994 non-finals. The second ordinary capture reuses202 qualified frozen finals, reads36 finals with incomplete canonical mappings and checks994 non-finals. Actual API traces, including both acquisition and consistency-recheck passes, show:

| Actual operation | Initial source capture | Next ordinary capture |
|---|---:|---:|
| Distinct final Box windows read | 238 | 36 |
| Qualified frozen Box windows not read | 0 | 202 |
| Box ReadProcessMemory calls | 952 | 144 |
| Box bytes actually requested/returned | 592,320 | 89,280 |
| Historical Box anchor reads | 0 | 0 |

No Box read address/label for any of the202 reused pool indices appears in the second trace. Those games also have zero new state/period/player/team/native Box rows. This proves actual Native read avoidance, not merely duplicate-row suppression after a full read.

All **1,232** current Game Box queries choose the correct source unit: the initial full unit for reused finals and the second unit for newly read finals/non-finals. Every array retains that selected unit; every latest header check points to the second unit. A sample historical cutoff retains the initial check and exactly the same original Box values/time. Current native year stays2022; current native Slot24 totals are not relabeled across years. The actual audit checks **2,096** source artifact hashes/sizes and **18,382** reads against private PLAYER intervals; all reads are bounded and read-only.

The final active database has **1,351,190** total physical rows. Its SHA256 is **`ba0d03601940d6739aae90b885a6a13363e551298d6197bf30d990eb5219bade`**. The exact SQLite snapshot and both source acquisitions are retained as ordered gzip-stream parts with manifests. Concatenate manifest parts in listed order to recreate each gzip stream; decompress the database stream and compare its complete SHA256. This is bounded artifact delivery, not database storage optimization.

## Verification and limits

**171 tests and SQLite smoke pass** at the exact executed code. Ten new cases cover no Native Box calls on reuse, changed-header full reads, LIVE_READ/complete-source requirements, newer partial disqualification, no age/unit mixing, wrong-origin/hash rollback, current roster collection without a Box anchor, old-year total withholding, duplicate roster rejection and explicit CLI reconciliation routing. DDL, all field cards and dictionary include the new typed table, constraints and provenance semantics. Future copy migration orders full source-check origins before references; no existing source is rewritten.

Source/code hashes, actual read traces, prior-fact preservation, source age, full archive streams/decompressed database, OS preflight and MWU are verified before publication. No issue exhausted the three-attempt failure budget. No game/save write, date advance, scheduler activation, Core modification, Antigravity dispatch or master integration occurred. Capacity and retention evaluation remain deferred until full real-season evidence. Native/UI/calendar/phase/identity lifecycle gaps remain open; no Q10 exception or final acceptance is inferred. The full engineering goal remains active.
