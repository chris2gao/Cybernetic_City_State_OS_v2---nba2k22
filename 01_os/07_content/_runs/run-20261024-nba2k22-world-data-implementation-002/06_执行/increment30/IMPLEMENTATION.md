# Increment 30: complete public Native staff pool

Candidate code: `0e9e1366c82fde7a483bc6652eb8124630a77eb1`.

The older organization source acquires current assigned staff. It does not
describe the full COACHDATA pool or qualify unassigned/unnamed source records.
The new source retains every bounded Slot19 descriptor record, all240 current
core TEAM.Coach_Internal slots, and119 metadata-selected scalar candidates
minus one explicitly named padding field:118 public scalars in the final model.

Schema v22 has96 STRICT tables and1729 columns. Four tables keep staff source
identity/status/three current TEAM-directory pointer interpretations,55 profile
scalars,63 tactics scalars and all eight role slots per core team. Original
assigned-staff tables remain immutable and retain their original source times.
The staff/team queries include the new independently timed Native source.

Native PersonType is4 bits, unlike the old position alias's low3 bits. Exact
Native role labels are COACH/ASSISTANT/SCOUT/TRAINER/GM/OWNER/CFO/ASSISTANT_GM;
unregistered raw codes retain NULL labels. Status is separately NORMAL/RELEASED/
RETIRED/INACTIVE. A current-team pointer, reciprocal role and status label are
independent facts; none is silently converted into hiring eligibility.

Canonical staff aliases require a single reciprocal current role, a globally
unique current pool ID and the exact existing public name. Duplicate IDs,
multiple roles, unnamed slots and other sources stay visible without invented
persistent people or arbitrary merges. Previous/MyTeam team pointers are only
qualified current-directory referents; no transfer event is fabricated.

Wage is a24-bit Native unsigned value. Native int-declared fields retain both
their raw bit pattern and signed-width interpretation. Nineteen current enum
tables provide exact literal labels where recoverable, including grade/system/
strategy codes. UI money/grade scale, sentinel semantics and effects remain
unproved. Tactics and preference data are observed engine fields; this work
does not implement independent coach/owner/GM personality or decision rules.

The existing generic Potential-key ingestion restriction remains in place.
Staff max/growth bytes260..264 and the shared TightLipped byte are physically
excluded; no alias bypass is introduced. All40 ordinary SeasonStats references
are also excluded so that annual staff history remains a separate source gap.
No PLAYER values are read. Names, primitive/enum bindings, omitted-byte layout,
role dimensions, all projections/roles/directories/root and same-unit game mode
are verified/rechecked. Raw pointer addresses stay in restricted artifacts.

`native-staff DB --all-sources --include-details` exposes the full source pool;
the compact default selects reciprocal current core roles. Details provide both
typed families, while person-type/status/team/name/index filters and explicit
unit pagination support exploration. `staff-slots DB TEAM_ID` retains all eight
slots and exact reference/reciprocity status. Both support `--as-of`.

246 tests and SQLite smoke pass at the exact candidate. The adjacent actual
report records all prior-row comparisons, scalar/label/pointer checks, omitted-
byte and annual-reference exclusions, query evidence and snapshot hashes.
Copy-upgrade retains v21 and changes only the binding's fact-file name; the
save identity remains nba2k22_test_01 / MyLEAGUE0003.

No Computer Use, game write, getter invocation, date advancement, annual history
refresh, capacity work, independent acceptance or master merge occurs. The full
world-data implementation goal remains active.
