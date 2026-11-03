# Increment 04 — operator-bound save and actual live world pipeline

Full engineering goal remains **active and incomplete**. Candidate implementation commit: `353e6940`. Schema stays **v3, 62 STRICT tables, 659 columns**.

## Implemented behavior

`init-save SAVE_DIRECTORY SAVE_ID NATIVE_SAVE_FILE` creates one operator declaration and one append-only facts DB; creation refuses overwrite. Human's current declaration binds `nba2k22_test_01` to `MyLEAGUE0003`. Human will announce filename switches; normal reopen retains the same ID. No native GUID or memory fingerprint is demanded as the save identity.

`capture-live PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT --game-index 0` performs direct Windows read-only acquisition, decode, consistency checks, atomic typed ingestion and source retention. It checks the loaded filename against the declared binding. A receipt tied to the actual reader and exact payload permits `LIVE_READ`; assertion-only JSON ingestion still rejects that grade. Acquisition provenance is separate from target UI/semantic certification.

The adapter reads actual Slot1/8/24 descriptors, all bounded native player IDs, TEAM identity/name controls, candidate public PLAYER segments and linked current season records. Duplicate IDs require one valid current-team/current-season candidate. A unique Native ID plus valid TEAM pointer can identify a player with no current season total; no cumulative zero is inferred. Selected bytes, TEAM controls, directory descriptors and game/Box bytes are reread before acceptance. Source changes reject the observation.

Potential byte 1089 is excluded from **every Windows read**, rather than captured and later exposed. The retained owner-only public PLAYER artifacts carry a documented zero placeholder for that byte. Queries and exports expose only typed allowed fields.

## Actual current-process results

Two direct administrator workers read the dedicated test PID 2564 with access mask `0x1010` (read/query only). Both workers completed and closed their handles.

- First observation: 25 canonical players/Boxes, 25 cumulative records. Rodney Hood was initially unresolved because Slot24 index was sentinel 65535.
- Second observation after the evidence-driven missing-total case: **26 players, 26 canonical game Boxes, 25 current cumulative records**, two named teams and eight period-score rows; all 26 original native Box rows remain staged. Rodney Hood is uniquely present at native ID4100/pool index25, has a valid native TEAM pointer and no current total. His missing total stays absent.
- Each of 26 players has 54 registered public attributes, 48 named tendencies, 17 contract fields and four ordered PlayTypes, with vitals and observed team membership. These are registered Native codecs on freshly read bytes; target UI meanings/ranges are not collectively certified.
- Latest canonical Boxes sum to **122 and 106**, matching the source period totals. The file keeps both observations: 51 canonical Box history rows. Canonical game date stays NULL pending calendar evidence; no current phase/team split/finalization is invented.

## Verification and retained artifacts

`development_check.py` passed **40 tests** (20.917 seconds), retained three fixture databases and ran the existing SQL/query/export/privacy checks. New cases cover template discrimination, unique player without cumulative row, ambiguous candidates, changed acquisition source, filename switching and rejection of asserted LIVE_READ. Fixture tests do not certify a live call; the two fresh captures are separate evidence.

The bound-world audit independently checked recorded raw hashes against actual read-trace hashes, public PLAYER segment boundaries and all excluded-byte address intervals, database integrity/FKs, latest source grade and row counts, both score sums and Rodney Hood's missing total. It wrote a named latest-Box query, full observed game history, public history export and player-card example; outputs contain no owner raw path, pointer or restricted Potential field.

`06_执行/increment04/` contains a compressed exact facts DB snapshot, bound-world report, source archive/manifests, declaration and public query results. `verification/` contains the actual fixture development report/logs and the audit script used. The first capture's exact source hashes are retained; the second uses the final candidate code hashes. Old increment03 evidence remains unchanged.

## Remaining scope

Continue with full active schedule and wider player/team/staff sources, badge and contract UI semantics, coaching/training/finance/market/draft/G League/settings/honors/news, current-season and native-player lifecycle identities, capacity/recovery checks and role outputs. No Q10 exception is assumed. The completed all-domain candidate still needs concentrated verification, separate independent review and Human acceptance. Master is untouched. Codex remains Owner; optional Gemini batches use Human relay only.
