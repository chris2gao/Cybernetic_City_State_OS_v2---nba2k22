# S3 live calendar pilot closeout

`completion_pointer: receipts/pilot-closeout-audit.json`

**VERIFIED_FOUR_HUMAN_CALENDAR_ROUNDS**. The calendar, collection, SQLite and Outbox NO_CHANGE path completed all four Human-triggered rounds. The conditional Native Setter path was not exercised because the isolated worldline had no verified role delegation and all four sealed batches had zero intents. The evidence supports live state and score integrity, with game-effect causality unassessed.

| Evidence | Result |
| --- | --- |
| Baseline | MyLEAGUE0003 and PID 8536, isolated worldline worldline-nba2k22_test_01-branch-34a775, FULL 3c48559bcd02, 20 verified sources in 118.14 seconds |
| Human advances | 7, 8, 8 and 8 in-game days. Schedule cursor 2021-11-19 → 2021-12-20. Final mode Today 2021-12-21. |
| Final games | 238 baseline → 463 final. All 225 new distinct games match their exact capture-unit SQLite score readback, including 10 overtime games. |
| Source cadence | Each incremental refresh records 16 acquired sources and 4 annual sources with verified existing receipts. |
| Outbox | cycle-001 through cycle-004 all COMPLETED and each digest matches its seal. Zero intents. Host cursor NEXT_CAPTURED/cycle-005 is the final advance-check pointer. There is no fifth Outbox cycle. |
| Isolation | Original WorldData database and original save binding hashes match L0. The isolated on-disk backup matches the baseline save hash. For each Host readback, the native save file hash matched before and after the operation. The user-driven simulations occurred between readback windows. |
| Durable artifacts | Isolated SQLite, Host state and ledger, Outbox, disk backup, 20-family capture receipts and exports remain in the private runtime. Published Git evidence contains compact receipts and their source hashes. |

### Adjustments observed during the pilot

- The first live decision originally treated a matching FULL baseline as a repeated state. The Host now allows first-cycle reuse only when the live date matches and no newly finalized game is present.
- An empty live decision originally entered the Native authorization route. The Host now closes an empty Outbox and seals a context-bound NO_CHANGE digest before waiting for the operator.
- The first incremental verification rejected game 262 because the SQL quarter rows contain regulation points. The verifier now requires the exact game/unit native header hash when overtime is present, checks SQL regulation against the header and adds aggregate overtime from those bytes. The retained batch passed re-verification without another capture. Missing and tampered overtime headers failed the negative check.
- The first Host-focused pytest invocation hit Windows shared temporary-link cleanup after the assertions passed. A dedicated basetemp returned exit 0.

### Reproduction and evidence

Actual collection used `initialize_pilot_admin.ps1 -DeclaredLoadedFilename MyLEAGUE0003` and `first_decision_admin.ps1`. Each Human advance used `advance_verified_round_admin.ps1 -AfterCycle <cycle> -CompletedTrigger '已完成日历模拟'`. Advance 001 originally exited 1 for the overtime readback. Its separate retained verification and seal used `verify_retained_first_advance_admin.ps1` and exited 0. Advances 002–004 exited 0. Raw stdout and stderr accompany the advance receipts.

The final audit ran `python -B -X utf8 audit_pilot_closeout.py --runtime <isolated-runtime> --historical <historical-binding-directory>` and exited 0. It compared all four actual raw report digests, the 225 exact-unit results, the final SQLite count, all four Outbox seals, the original world database/binding and the disk backup.

- [Final audit and per-round metrics](receipts/pilot-closeout-audit.json)
- [Per-round live receipts](ROUND_PROGRESS.md)
- [First FULL and first decision](FIRST_ROUND_CHECKPOINT.md)
- [Host targeted regression, 4 passed](receipts/host-focused-verify-02.log)
- [Calendar and SQL targeted regression, 4 passed](receipts/s3-overtime-verify-01.log)

The pilot ends at the fourth readback. Any later Native write trial requires a genuine role grant and a separately reviewed exact target plan.
