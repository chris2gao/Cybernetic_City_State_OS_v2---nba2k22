# Checkpoint005 — Player PlayType Native setters

The complete M0–M5 task remains active. Source PR18 is still the fixed baseline `094f1aa641f93dec2277707ad9dbf5bdb0341247`; engineering continues in Draft PR19. No game attachment, Native live call or state change occurred.

## Implemented

The existing `PLAYER_SET_PLAY_TYPES_1_TO_4` action is promoted from a noncallable editor lead to a deferred dedicated-setter implementation. Four existing logical requirements are now callable in the engineering catalog; mapping count remains57 rather than inflating with new aliases. Registry state is65 actions and47 binding/layout records.

Inputs are exact team/player IDs and a nonempty `slot_values` object, with keys1..4 and enum integers0..15. Each role requirement is restricted to its own slot. Player personas need an explicit grant and matching `player_scope`; no permission follows from the role label. Batch conflicts are scoped to player/slot and overlap trades on that player. The raw Native interface can process explicit multiple slots, in stable slot order, without choosing values or altering omitted slots.

The four Native functions are straight-line field setters with no calls/branches/ownership changes. Fixed code signatures, fresh identity checks and exact whole-word readback are implemented. UI/cache refresh, simulation use, later AI overrides, independent readback and Save/Reload are not proven.

Unbound or noncallable mutations now advertise `role_endpoint:null`, rather than misleadingly appearing to offer a read endpoint. Existing capabilities and external requests retain their appropriate interfaces.

## Evidence and other Player gaps

Decoded field writes uncovered setters missed by name/direct-call searches. Actual startup LEAs install them in dynamic property descriptors. Direct-call and absolute-pointer zero results are preserved without inferring absence. The offsets/enum meanings reuse existing PC22/R04 sources; raw descriptor IDs are not falsely named. `PLAYER_PLAYTYPE_NATIVE_CONTRACT.md` links the exact windows and startup references.

The parent copy body now has its complete31509-byte unwind extent and eight callback sites recorded; child copy/refresh bodies and small callback predicates are also recovered. The default recovery bound remains24KiB, with an explicit64KiB selected-function option used here. No exhausted whole-game Ghidra import was retried. Safe private input, pointer ownership/normalization and refresh/readback for attributes/tendencies/badges are not closed; parent copy stays noncallable.

`recover_field_writers.py` is packaged for continuation and reproduced611 writer instructions across452 candidate entries from2599577 decoded bytes. These counts include unrelated objects and are not counts of usable Player functions. `CHECKPOINT_005_SOURCE_DELTA.json` pins the inherited category source.

## Verification and continuation

Six focused compiler/planner/JS-handler tests and one new endpoint-consumer check passed offline. One local fixture injected four cancelling neighbor-bit flips; it was repaired to inject one lasting corruption. No failure exhausted three repairs. Fixed-commit Managed Run/Inspect is pending at the code checkpoint and will be recorded after execution; no41-test result is claimed in advance.

P04/P06/P07/P09/P10/P12 navigation and mechanism/interface documents are synchronized in this engineering branch. Data acquisition/SQLite/history systems remain unchanged. Continue parent field safety/refresh, signing/staff, remaining Coach/Book/Freelance/rotation/training and actual context/readback integration, preserving all183 requirements. Live scenarios require concentrated Human approval; this checkpoint is not the final handoff.
