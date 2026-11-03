# Increment 31: frequent process restarts and interrupted-refresh recovery

Candidate code: `6fcf3db2f29c346cd601af0343dc4a97ff931c54`.

Human clarified that ordinary development restarts reopen the same test save,
while gameplay captures are explicitly requested and may follow further game
time. Restart announcements must not be a prerequisite for continuing work.
The durable work order now records that contract and the supplied keyboard
navigation. The actual save remains `nba2k22_test_01 / MyLEAGUE0003`; switching
save files still requires the Human's filename declaration.

`reconnect-game SAVE_DIRECTORY MyLEAGUE0003 NEW_OUTPUT_DIRECTORY` discovers the
one current NBA2K22.exe automatically and reopens it with the existing read-only
access mask. It verifies the current PE/build, Native game-mode/date metadata,
current roots and controls; it records PID plus creation FILETIME, current game
progress and connection evidence. It does not create a capture unit or refresh
annual history. Process-session evidence stays outside the facts database and
never supplies cached dynamic addresses to readers.

`refresh-world auto ...` explicitly acquires selected sources using a freshly
resolved PID. Existing bounded source readers continue resolving their own roots,
descriptors and identity controls. The batch now checkpoints date/stage as well
as process/build/season, stopping on mid-batch changes and retaining prior commits.
New ordinary captures do not reuse the previous month's data by default. The
schedule adapter still walks its full current bounded Native schedule and uses
only the existing qualified frozen-Box reuse policy.

`--resume-report OLD_REPORT` checks the save/database binding, old plan and
controller liveness. A report still marked RUNNING requires the exact prior
controller PID and creation time to be observed terminal; errors or unavailable
evidence remain unknown. A live controller cannot trigger a second worker.
If the Human declares `--data-updated`, Native progress/season changed, or prior
progress is unavailable, the requested sources are captured again. Otherwise
successful DB receipts are retained with original observation times and source
process provenance; unfinished sources continue. A terminated controller that
committed just before losing its result JSON can be reconciled against the
actual registered child artifact paths, sizes and hashes. Ambiguity or changed
artifacts stops recovery. Retained observations are explicitly not current reads.
Annual families still enforce one refresh per bound save/Native season year.

254 tests and SQLite smoke passed at the exact candidate. Eight new cases cover
discovery, reconnect/no-ingest, restarted-process resume, changed date/explicit
update/legacy-progress recapture, live or unknown controllers, commit recovery
with and without result JSON, corrupted provenance, binding mismatch and
mid-batch progress changes. Controller death and later-month progression are
fixture cases; the actual game process was neither killed nor advanced.

The actual process changed from PID5092 / FILETIME134374550526935769 to PID11668 /
FILETIME134374763743810259. The supported module remains base0x140000000,
size115056640, PE timestamp1652287197. Current Native Today is2021-11-20,
period29; season-year2022 stays distinct from civil year2021. Both actual
reconnects left the database SHA256 unchanged at
`09fa9a373cb2bd0c994aacc8136e6c71255595f258bdb1b02f4733bd014009d1`.

One explicitly bounded engineering verification capture created
`native-game-mode:496e3e911bb214cfa21f65c1`; its resume added zero units and left
the post-capture hash unchanged. All38 previous unit receipts and their original
times remain exact; all96 table row counts differ only by one capture run, one
unit, one game-mode observation and five source artifacts. The schema staysv22,
96 tables/1729 columns. The current local database has1402757 rows and39 successful
units, SHA256`26cf0d4ceeadb902d02331a8ed8681181b77e92d4104a44fd2494a17cea55567`.
Annual buckets and the save binding are unchanged. Actual workerPID4704 was
confirmed absent after its terminal report, independently of the result file.
The small Native source archive accompanies increment30's existing full v22
snapshot; this increment does not claim a new full database snapshot or an
executed offline LIVE_READ restoration from these source files.

Computer Use was used solely for current window selection, restoring the
minimized game window, and `include_screenshot=false, include_text=true`.
The accessibility tree contains only the top-level NBA2K22 window. It exposes
no menu, field name or value. No screenshots were requested, no game key/mouse
input or value edit was made, and no UI-to-Native field correspondence is claimed.
The earlier screenshot failure remains unresolved. Keyboard control information
alone does not make an unidentified game page safe to modify.

No game/save writes, date advance, getter invocation, annual refresh, capacity
work, master integration or independent acceptance occurred. The full world-data
implementation goal remains active.
