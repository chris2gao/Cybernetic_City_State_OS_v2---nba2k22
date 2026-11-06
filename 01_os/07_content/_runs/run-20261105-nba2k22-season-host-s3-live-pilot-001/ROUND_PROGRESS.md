# S3 Human calendar advance progress

Two of four Human advances have been verified. The Host is waiting for the third calendar trigger after `cycle-003`. Human supplied “已完成日历模拟” after each completed cycle. Both readbacks matched the established game process epoch and isolated save binding.

| Advance | Schedule date | Mode Today | Finalized games in memory and SQLite | Capture | Next decision |
| --- | --- | --- | --- | --- | --- |
| After cycle-001 | 2021-11-19 → 2021-11-26, 7 days | 2021-11-27 | 238 → 291, 53 new | a9c89db9dcd9, 100.320549 s, 16 freshly acquired sources, 4 annual sources with verified prior receipts | cycle-002 NO_CHANGE, zero targets |
| After cycle-002 | 2021-11-26 → 2021-12-04, 8 days | 2021-12-05 | 291 → 348, 57 new | 69f58620c330, 99.987548 s, 16 freshly acquired sources, 4 annual sources with verified prior receipts | cycle-003 NO_CHANGE, zero targets |

All 53 new games passed exact schedule-unit SQLite verification. The initial check rejected overtime game 262 because the stored period rows contain regulation quarters only. The corrected verifier binds the retained raw header to the exact game and acquisition unit, verifies the four SQL periods against that header, and adds its aggregate overtime bytes. The observed result was 125–125 in regulation plus 7–17 in overtime, for a final 132–142. Readback with the missing and tampered headers failed as expected. The original failure record is retained. The recovery reused the committed batch, performed no recapture, and only sealed the already-open next decision after fresh same-epoch/progress checks. The targeted calendar/SQL regression returned 4 passed, 11 deselected and exit 0.

The second advance passed all 57 exact-unit checks on its first readback, including three overtime games. The native save hash was stable across each Host readback. The verified capture and Outbox changes are in the isolated runtime. No executable role grant was present. The sealed `cycle-003` has zero GM, Coach or Player intents and no Native targets. Its digest is `9c6f0c2ea57178bce603826ca3b4b478a556b686a53c32933943f5ddf096a587`.

The next Human calendar advance is approximately seven game days, to December 12 if the UI shows December 5. After Human confirms completion, use the existing readback entry for `cycle-003`. Both verified advances have terminal evidence.

- [Original readback failure](receipts/advance-after-cycle-001.json)
- [Corrected exact-unit verification and next seal](receipts/advance-after-cycle-001-reverified.json)
- [Incremental source receipts and timings](receipts/advance-after-cycle-001-sources.json)
- [Targeted regression log](receipts/s3-overtime-verify-01.log)
- [Second advance and cycle-003 seal](receipts/advance-after-cycle-002.json)
- [Second incremental source receipts](receipts/advance-after-cycle-002-sources.json)
