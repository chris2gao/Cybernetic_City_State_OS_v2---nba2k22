# Increment 06 — real team/staff/coaching/financial sources

Full engineering goal remains **active and incomplete**. Implementation candidate: `830ef312`. Schema v5 has **63 STRICT tables and 693 columns**. Added `team_state_observations` and distinct coach defaults, financial and team-total columns, preserving all original table names and observations. No whole-system/independent/Human acceptance is claimed.

## Implemented source pipeline

`capture-organization PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT` uses actual TEAM, STAFF and TEAM_STATS descriptors in the current process. Each core team's eight role pointers must be descriptor-aligned and reciprocate both the STAFF team's pointer and its role bits. Assigned native staff UniqueId is resolved from current native metadata, checked for uniqueness in the assigned set and used as a save-local identity. Name changes under the same identity reject rather than merge different people.

The existing native coach metadata verifier runs through a bounded read-only adapter; it does not instantiate legacy GameMemory or an executor. The actual current metadata contains 142 COACHDATA definitions and 18 defensive definitions; the verifier checks registered field layouts, enums and type signatures. The adapter maps 24 head-coach defaults into distinct typed columns, without claiming semantics for all 142 fields. It uses four-bit PreferredSystem/ActiveSystem from the verified coach profile instead of truncating to the older STAFF three-bit registration.

Team current statistics at +0xE80 resolve to 62-byte TEAM_STATS records. Registered fields are decoded into typed season totals; every team's native scoring identity, wins/losses, points and opponent points must match a freshly acquired complete schedule. Schedules, selected TEAM/STAFF/stat/book records and descriptors are reread to reject source changes.

The 360-byte loaded PLAYBOOKDATA layout and enum are checked. Head-coach PlaybookID selects one unique loaded enum; its separate native unique ID is retained. Each team's 68 ordered CRC slots is saved, including raw zero CRCs. Names stay NULL until a text source is acquired.

## Actual fresh PID8784 results

- **30 core teams**, with eight reciprocal roles each: **240 staff identities, assignments, contract observations and seven-field public skill snapshots**.
- **30 current team season totals**, all reconciled against wins/losses/points/PA from the actual current schedule; no final-season closure inferred.
- **30 head-coach preference and 24-default tactic observations**.
- **84 loaded playbooks**, resolving all selected team books into **2,040 ordered native CRC slots**.
- **30 financial snapshots** (eight registered uint32 values each) and **30 chemistry/fan state snapshots** (two raw floats). No signed-cash correction, native salary unit assertion, cap-space or external CBA inference.
- The organization unit reads **no PLAYER structures**. Public projections exclude Potential, raw source structures, runtime addresses and owner artifact paths. Assigned staff is not inferred to be the entire staff market; no unavailable/free-agent state is fabricated.

The first source-only probe and the later complete capture are retained separately. The complete capture's actual executed source hashes are retained. Later field-dictionary annotations changed catalog evidence descriptions only; the final candidate hashes and tests identify those bytes separately.

## Queries, migration and verification

`team DB TEAM_ID` returns field-specific observation freshness for finances, state and coach defaults, latest observed assigned staff/book slots and team-total history. `staff DB STAFF_ID` returns contract/seven-skill/preference families and assignment history. Native amounts/codes retain their raw representation and source grade.

Copy-upgrade v4 -> v5 retained the v4 DB and declaration and selected `world-v5.sqlite`. Offline audit compared **43,862 old rows** by all previously present columns and verified the entire original v4 file still matches increment05's exact byte hash. The added columns do not rewrite old facts or old registry evidence.

The source audit compared **3,215 new typed/entity/gap records** against the captured manifest/codec values, checked direct read-trace hashes for TEAM, STAFF and totals, rechecked every team's schedule reconciliation and reciprocal role, tested all 30 team queries (eight staff / 68 slots), FK/integrity and role projection privacy. Actual raw structures, schedule controls, manifests, reports and code hashes are archived.

The development suite passed **50 tests**. New source-fixture checks cover reciprocal role failures, four-bit system decoding, unsigned cash preservation, missing cap-space semantics, a plausible-but-wrong cumulative total, identity conflict rollback, and duplicate staff ID rejection. Four retained fixture DB examples include the new actual-source research replay; these are separate from the fresh LIVE_READ world file.

Artifacts: `06_执行/increment06/`: compressed exact v5 DB, actual source archives, binding, organization report, team/staff query examples and typed exports, executed audit script, development report and logs. Game/save writes: **none**. Master: **untouched**.

Remaining full-goal work includes the four unresolved player IDs, current player/staff lifecycle, calendar/badge/contract/finance UI semantics, full gameplan/rotation/defense and training/mentor sources, text play labels, market availability and draft/G League, actual settings/rules/honors/records/news, capacity/recovery/role coverage and completed-candidate independent/Human acceptance. No Q10 exception is assumed. Codex continues as Owner; optional Gemini batch research uses Human relay only.
