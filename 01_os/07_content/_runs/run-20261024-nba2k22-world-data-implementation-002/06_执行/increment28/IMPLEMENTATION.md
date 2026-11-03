# Increment 28: Native typed TEAM finance

Candidate code: `618255cc42d8a5c128120ed2ba904e827da343ea`.

The existing unsigned legacy snapshot used `payroll_raw` for Native `ExpPayroll`
and `cash_raw` for Native `BankBalance`. Current TEAMDATA metadata identifies
those fields as signed `int`, while Native `Salary` is `u32`. The new source
records their Native representations in a distinct immutable table. It does
not rewrite earlier unsigned source words or infer currency scale/cap space.

Schema v20 has 88 STRICT tables and 1,471 columns. The new table adds 67 columns:
identity/unit/observation-season references, 26 typed integer scalars, 15 float
word/finite-REAL pairs, four packed flag/enum values and three enum labels.
Each nonfinite float preserves its original word and has a NULL REAL; unknown
enum codes preserve their raw code and have a NULL label. The field dictionary
describes those NULL cases separately from a missing observation.

The source verifies the TEAMDATA constructor/size/full field signature, each
selected primitive CRC, enum type bindings and exact enum tables. Native name
array extents are 25/18/7 UTF16 units. It reads the current core TEAM identities
and minimal named financial projections, repeats every data/directory control,
and pairs the same-unit Native game-mode date/stage. It invokes no getters and
reads no PLAYER values. `finance` is an ordinary refresh family; historical
records and awards keep their existing independent annual cadence.

`finance DB --team-id ID --unit-id UNIT --as-of TIMESTAMP` returns one complete
source unit, including its acquisition grade and same-unit game mode. The team
query includes this typed result and an explicit qualification for old aliases.
Copy migration creates `world-v20.sqlite` and retains `world-v19.sqlite` unchanged;
only the binding's database filename changes.

225 tests and SQLite smoke pass at the candidate. Actual read/audit results,
all prior-row comparisons, signed-field samples, query output and source/snapshot
hashes are reported in the adjacent machine-readable evidence.

Computer Use capture exhausted three materially different attempts, including
the Human's windowed-mode change. No image was obtained. The unresolved backend
timeout is recorded in `ui-capture-failure.json` and the global failure log as
`NBA2K22-WGC-CAPTURE-20261025`. An external DisplayPort monitor and integrated
Intel adapter were observed; neither was proved to cause the timeout. The Human
subsequently requested that this task avoid Computer Use as much as possible;
Native engineering continues without further capture retries.

UI monetary units, accounting duration, live financial transitions, full-season
capacity and final independent/Human acceptance remain unproved. This increment
does not close the overall world-data implementation goal.


The first actual finance attempt stopped before ingestion because it compared
the full24-byte runtime name-dimension control block against static PE bytes.
A bounded diagnostic established unchanged extents25/18/7 and a runtime-initialized
word at+8 (value2 rather than static0). The repaired reader checks the one-dimensional
extent/rank whose meaning is evidenced, retains the full runtime control block,
and repeats it for stability. It does not assign semantics to other control words.
The original failed attempt is preserved in the source archive; the corrected
candidate was rechecked with225 tests and SQLite smoke before acquisition resumed.
