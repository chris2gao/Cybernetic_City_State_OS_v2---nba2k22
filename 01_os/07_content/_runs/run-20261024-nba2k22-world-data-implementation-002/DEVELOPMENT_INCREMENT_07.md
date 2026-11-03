# Increment 07 — native future picks, waived source and uninitialized draft pool

Full engineering goal remains **active and incomplete**. Implementation candidate: `d205a03f`. Schema v6 has **68 STRICT tables and 833 columns**, adding explicit draft-pool slot state, three separate public prospect-family tables and waived-salary observations. Class year is nullable rather than guessed. No whole-system, independent or Human final acceptance is claimed.

## Actual implemented pipeline

`capture-market PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT` reads current descriptors, checks exact executable bytes for the registered named draft getters, decodes all source records, requires complete simple future-pick year/round/original-team groups, and rereads all records/controls. Raw source reads are bounded and handle rights remain `0x1010`. Every prospect read and reread skips Potential byte1089. Current PLAYER records are not read by the final market collector.

Current PID8784 source has **504 draft records**, of which **300** satisfy the complete simple future-pick source contract: 2022–2026, two rounds/year, one original pick per 30 core teams. Current owner is stored separately from year/round/original-team identity. The remaining 204 source records are preserved as evidence, not fabricated historical draft results. Protection and swaps remain **UNKNOWN**; no tradeability policy/window is imposed.

The 136-byte waived pool has **222 actual records**, **32** with exact current core TEAM pointers and 190 with unmapped/empty owners. All are typed source observations with explicit mapping status, three unsigned raw salary buckets and candidate inline UTF16 names. The first Q word is not treated as a PLAYER pointer: actual controls include a link to another waived record. Canonical player ID/FK, absolute salary years and UI units remain unproven. No release event, free-agent availability or cap-space calculation is invented.

The draft-template pool has **90 allocated slots, all without names and all native ID zero**. Nonzero template/default bytes do not establish 90 people. The world records 90 `UNINITIALIZED_NO_NAME` slot observations, **zero draft prospects** and zero prospect attribute/tendency/play-type facts. Separate typed prospect families and nullable class year support initialized named observations without creating PLAYER instances or merging duplicate/zero native IDs. Named initialization is covered by a clearly synthetic transformation test; it is not claimed as current-game Native class acceptance.

## Queries and migration

`market DB [--team-id ID] [--limit N]` returns the latest source unit's pick owners, waived observations and draft-slot states with explicit partial-source status. It refuses silent row truncation. `prospect DB OBSERVATION_ID` returns separate public prospect families when such a named source exists. Public projections expose neither pointers/owner artifact paths nor Potential.

Copy-upgrade v5 -> v6 retained old files/declarations and selected `world-v6.sqlite` under unchanged `nba2k22_test_01 -> MyLEAGUE0003`. The audit compared **47,714 prior rows** by all old columns and confirmed the entire original v5 file still matches increment06's byte hash. No native game/save write occurred.

## Verification

Development regression passed **56 tests**. New checks replay actual named-getter bytes and complete pick groups, reject code mismatch before asset reading, reject duplicate native PickIndex, distinguish unnamed slots from people, keep named zero-ID templates separate with unknown year, decode inline waived text without following the first word, append changed pick ownership without manufacturing a trade, and reject query truncation. All five retained fixture DB examples remain fixture-grade; fresh Windows acquisition is separate evidence.

The actual-source audit rechecked every recorded artifact hash, the getter-byte controls and full future-pick set, direct waived/public-prospect read hashes, excluded Potential address intervals in both current PLAYER and prospect pools, **947 source-to-typed records**, SQLite integrity/FKs, old-row preservation and role-output privacy. It verified 300 current pick owners with unknown protection/swap state, 222 waived observations/32 mapped owners, 90 uninitialized slots and no draft result/market-status/person invention.

Artifacts under `06_执行/increment07/`: exact compressed v6 DB snapshot, source probe/capture archives, binding, market report, current/all-team query examples, typed exports, executed audit script, development report and logs. The first probe's experimental decoder and its code are retained separately; the final collector corrects the first-word assumption and explicit initialization semantics. Executed capture hashes and final candidate hashes are separately recorded.

Remaining full-goal work includes initialized class/year acceptance, protection/swaps and actual draft results, actual player/staff market availability, G League identities, the four unresolved game player IDs, lifecycle, calendar/badge/contract/finance UI semantics, full gameplan/training/mentor and text play sources, actual settings/rules/honors/records/news, capacity/recovery/role coverage and completed-candidate independent/Human acceptance. No Q10 exception is assumed. Codex continues as Owner; optional Gemini batches use Human relay only. Master remains untouched.
