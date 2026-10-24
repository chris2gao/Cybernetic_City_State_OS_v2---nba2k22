# Increment 10 — complete native record book and qualified historical observations

Full engineering goal remains **active and incomplete**. Code candidate: `25de00f644640b2efa77a2d348d5ce410289743d`. Schema v9 contains **74 STRICT tables and 960 columns**. The previous goal turn delivered actual settings/rule source and was progress; this increment adds actual RES-H record-book acquisition, exact typed storage, pinned pagination and full export. It does not substitute a record book for season awards or news.

## Source and implementation

AG_NATIVE_01C provided the Slot39 record-book lead and 52-byte field layout. Static inspection of the known local NBA2K22 PE found the Getter at RVA `0xF400A0`. The actual PID8784 worker independently read that Getter and confirmed its native count/pointer offsets `+0x270/+0x278` and multiply-by-52 stride. It reopened the process, resolved fresh ROSTERDATA and Slots39/8/28, bounded the native count at 80,000, and acquired the complete actual array in record-aligned blocks with individual Windows reads <=1200 bytes. Every source block, Getter, root, descriptor and season control was reread before acceptance.

Actual native count is **69,040**, all with nonempty ASCII names and finite float32 metrics in this capture, across **143 native category codes**. The raw source includes the Wilt Chamberlain 100.0 and Kobe Bryant 81.0 entries, with their original native codes/words. These observations come from the running game, not an external NBA source or a recreated fixture. A curated 365-row research fixture spans all 143 observed category codes and selected source positions, with exact byte hashes.

`records_reader.py` retains each 52-byte source slot's inline names, metric raw uint32 and exact float32/hex interpretation, native date/category/player words, trailing flags and decode/interpretation state. It does not use the old decoder's three-decimal rounding. Nonfinite metrics preserve the word and an explicit diagnostic with NULL numeric value. Empty or invalid name prefixes are classified without invented subjects.

The existing `season_record_entries` table is extended rather than duplicating record facts. Actual record scope is not necessarily the current season: `season_id` is now nullable, and the separate `observed_in_season_id` stores the proved acquisition context. This is an evidence-driven physical schema adjustment within the approved task. No current PLAYER identity, team, ranking, occurrence date or record season is inferred from names, raw IDs, flags or the source observation year. All 69,040 canonical holder/record-season/occurred-at fields remain NULL.

## Interpretation limits that the full read exposed

A subset of source rows has a legacy candidate category label; **67,354** retain their native code without a fabricated label. Current UI category/scope semantics remain unverified. All observed trailing flags are zero, which is not proof of team/scope meaning.

The 1920-epoch date formula produces **13,252 Gregorian-valid candidates**, **26,870 words invalid under that candidate interpretation**, and **28,918 zero date words**. A failure of that candidate formula is not declared source corruption. Every original word is retained, candidates remain explicitly qualified, and `occurred_at` stays NULL. The current observed season2022 is not attached to historical Wilt/Kobe records as their record season.

The record book establishes neither final award winners nor native news. `season_award_instances`, recipients and news remain unobserved by this adapter. No Q10 exception or final RES-H acceptance is assumed. Static PE public string clues include award-related names, but they are not actual award data or a certified readable source.

## Queries, preservation and validation

`capture-records PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT_DIRECTORY` implements actual read -> decode -> validate -> receipt-bound LIVE_READ ingest. `records DB` supports native category/name filtering and explicit index pages; the result returns its unit ID and `has_more/next_after_index`. Pin `--unit-id` on later pages so a newer acquisition cannot change the source in the middle of pagination. Full JSONL export remains streamed with an explicit sufficient limit.

Bound save remains `nba2k22_test_01 / MyLEAGUE0003`. Copy migration v8 -> v9 preserved **96,060 old rows**, compared by every preexisting column, and the old v8 file still matches increment09's exact archived hash. Actual-source audit decoded every raw row and compared **69,045 source-to-typed rows**: 69,040 records and five explicit gaps. It checked Windows read hashes, the complete source indices, SQLite integrity/FKs, seven pinned query pages covering all 69,040 rows, full 69,040-row public export and withheld canonical identities/season/date. New unit: `records:b410948bd93f7d5135cfaf80`.

Development suite passed **73 tests in 28.458 seconds**. Record cases cover exact fixture byte replay, unrounded and nonfinite metrics, invalid date/name classification, missing/duplicate coverage and tampered value rejection, no fabricated awards/holders/seasons, filter results and stable pinned pagination across a newer acquisition. Eight retained fixture DB examples are research replay; actual acquisition is independently evidenced in the source archives.

The process handle requested **0x1010 VM_READ | QUERY_LIMITED_INFORMATION** only; no PLAYER struct was acquired. There was no game/save write, injection, date advance, Antigravity dispatch or master change. Source artifact paths, process pointers and raw materials are not included in role projections.

Artifacts under `06_执行/increment10/`: exact compressed v9 DB, separate probe/live source archives, static inspection and script, binding/source manifests, bounded query examples and full compressed JSONL export, executed source/history audit, development logs/reports and compressed fixture DBs. `records_world_report.json` records actual-source checks; fixture verification is separately labeled.

Remaining full-goal scope includes actual season awards/news, record category/subject/scope/date certification, settings NativeType/UI completeness, global rotation/training focus/safe history/mentor effect, four unresolved game-player IDs, lifecycle/calendar/badge/contract/finance semantics, market availability/prospect class/year/G League, draft protections/swaps/results, capacity/recovery/role coverage, whole-candidate managed verification and separate independent/Human acceptance. Codex remains Owner and the task stays active.
