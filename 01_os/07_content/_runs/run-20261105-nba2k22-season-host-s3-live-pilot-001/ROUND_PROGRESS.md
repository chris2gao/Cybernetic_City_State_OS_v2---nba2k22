# S3 Human calendar advance progress

One of four Human advances has been verified. The Host is waiting for the second calendar trigger after `cycle-002`. Human supplied “已完成日历模拟” after `cycle-001`. The game process and isolated binding matched the established epoch.

| Advance | Schedule date | Mode Today | Finalized games in memory and SQLite | Capture | Next decision |
| --- | --- | --- | --- | --- | --- |
| After cycle-001 | 2021-11-19 → 2021-11-26, 7 days | 2021-11-27 | 238 → 291, 53 new | a9c89db9dcd9, 100.320549 s, 16 freshly acquired sources, 4 annual sources with verified prior receipts | cycle-002 NO_CHANGE, zero targets |

All 53 new games passed exact schedule-unit SQLite verification. The initial check rejected overtime game 262 because the stored period rows contain regulation quarters only. The corrected verifier binds the retained raw header to the exact game and acquisition unit, verifies the four SQL periods against that header, and adds its aggregate overtime bytes. The observed result was 125–125 in regulation plus 7–17 in overtime, for a final 132–142. Readback with the missing and tampered headers failed as expected. The original failure record is retained. The recovery reused the committed batch, performed no recapture, and only sealed the already-open next decision after fresh same-epoch/progress checks. The targeted calendar/SQL regression returned 4 passed, 11 deselected and exit 0.

The native save hash was stable across the Host readback. The verified capture and Outbox changes are in the isolated runtime. No executable role grant was present. The next plan has zero GM, Coach or Player intents and no Native targets. Its digest is `c7f864ef38945b4e0105d9fde3333918871f1e8f8ff2bdf4db09ad16423c2cd4`.

The next Human calendar advance is approximately seven game days, to December 4 if the UI shows November 27. After Human confirms completion, verify after `cycle-002` using the existing readback entry. The first advance has terminal evidence and is not replayed.

- [Original readback failure](receipts/advance-after-cycle-001.json)
- [Corrected exact-unit verification and next seal](receipts/advance-after-cycle-001-reverified.json)
- [Incremental source receipts and timings](receipts/advance-after-cycle-001-sources.json)
- [Targeted regression log](receipts/s3-overtime-verify-01.log)
