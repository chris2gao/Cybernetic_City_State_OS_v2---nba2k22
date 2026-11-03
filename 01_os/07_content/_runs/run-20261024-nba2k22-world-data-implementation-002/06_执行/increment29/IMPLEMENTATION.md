# Increment 29: Native global lineups and stored rotation

Candidate code: `1cc410befcebf9fb8848ad0dcabfc91e31666fb7`.

The older planning source reads stored opponent plans. Those records do not
establish a team's global lineup, and `team_rotation_slots` had no real rows.
The new source acquires the named TEAMDATA global arrays directly and keeps
them separate from opponent plans.

Current Native metadata establishes thirteen `LineupPlayer` pointer slots,
eight five-player arrays (`Starter`, `LineupBench`, `LineupTall`, `LineupQuick`,
`LineupDefense`, `Lineup3Pter`, `LineupFreeThrow`, `LineupCustom`) and the full
48-by5 `AdvancedRotationPlayerId` matrix, with byte strides10/2. Every matrix
coordinate and pointer slot is retained, including zero/sentinel values and
disabled/stale lineups. Advanced ID namespace and clock/position labels remain
unproved; no canonical player is assigned from those raw IDs.

PLAYER `PlayingTime` is an unsigned seven-bit field at+248 bit18. Its UI units
and actual deployment are not proved. `ForceNonStarter` is a two-bit Native
enum at+764 bit26 with exact labels FALSE/TRUE_WITH_RESET/TRUE_FOREVER. Unknown
codes keep their raw value and NULL label. The complete public PLAYER pool is
captured with102-byte projections that physically exclude every private interval.

Schema v21 has92 STRICT tables and1517 columns. Four typed tables keep team
lineup controls/custom name, named pointer-array slots, raw advanced matrix
coordinates and full-pool PLAYER rotation fields. Existing `team_rotation_slots`
now stores each Native global pointer slot and its qualified same-unit referent.
`planned_minutes` and `role_code` remain NULL. Raw pointer addresses remain in
restricted source artifacts. Queries expose the Native source index/name and
explicit null/outside/misaligned/owner-roster status instead of a forced match.

The reader verifies both complete Native field signatures, selected primitive
CRCs, enum tables, array extents/strides, name dimensions and protected PLAYER
field ranges. It repeats subject/roster/array/directory/root controls and pairs
same-unit game-mode date/stage. SQL rejects cross-unit/mismatched subjects,
missing same-unit team controls and fabricated global Native minutes/roles.

`lineups` is the seventeenth explicitly invoked serial refresh family.
`lineups DB TEAM_ID --include-advanced` and `native-player-rotation DB` expose
the actual typed source with acquisition time/grade and `--as-of`. Continued
player pages require an explicit source unit. The team card includes this
global-lineup source alongside its other independently timed observations.

235 tests and SQLite smoke pass at the exact candidate. The adjacent actual
report records all prior-row/column comparisons, raw pointer/scalar/matrix
checks, protected-free read intervals and source/snapshot hashes. Copy upgrade
retains v20 and changes only the binding's fact-file name; save identity stays
`nba2k22_test_01` / `MyLEAGUE0003`.

Actual PID5092 source contains3390 public PLAYER subjects and461 current core
roster subjects. All1590 global/named lineup references resolve to reciprocal
current same-team roster members. The235-test candidate captures390 global
slots,1200 named slots and7200 matrix coordinates;10170 player-field comparisons
and50850 protected-free PLAYER interval checks pass. All1382123 prior rows in88
tables are preserved, apart from the copy's schema-version header change. The
result has1397842 rows and37 successful units. All30 observed HasAdvancedRotation
flags are0; this is a stored-array observation, not live advanced-rotation use.
Stephen Curry's PlayingTime is34 in this sample, retained as a raw Native value.

No Computer Use, game writes, getter invocations, date advancement, annual
history/award refresh, capacity work or master merge is performed. UI units,
actual deployment, lifecycle, full-season capacity and final independent/Human
acceptance remain unproved. This increment does not close the overall goal.
