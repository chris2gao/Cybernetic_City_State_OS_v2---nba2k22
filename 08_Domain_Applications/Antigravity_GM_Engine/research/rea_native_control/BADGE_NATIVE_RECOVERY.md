# Indexed Badge recovery: raw fields, internal names, effective modifiers and coupling

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`; pinned PC22 EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. This is bounded static discovery, not a callable Badge runtime or new game evidence. REA remains the deferred Native transport; these artifacts use local PE/Capstone and are not REA Provider output.

## Native identities and values recovered

`tools/recover_badge_fields.py` reconstructs all99 raw Getter dispatch targets at `0x97c700`, checks each field's clear mask against the corresponding original Setter case, checks the per-ID maximum switch and confirms that distinct fields do not overlap. Selected output025 retains the actual getter paths, setter case references, bit positions, original code and hashes. The original internal name pointer array at `0x24c6970` contains99 UTF-16 strings; the same array is referenced by the original setter's diagnostic path. No external Badge catalog was guessed onto native IDs.

There are80 maximum4 fields and19 maximum1 fields. **The latter include ID0 `NONE`, an internal sentinel, so this is not a claim of99 ordinary editable Badges.** The other18 internal one-bit names are AlphaDog, Enforcer, LowFriendliness, HighFriendliness, SmallEgo, BigEgo, HighWorkEthic, VeryHighWorkEthic, NegativelyMotivated, PositivelyMotivated, Expressive, Unpredictable, LaidBack, OnCourtCoach, CareerGymEliminator, BigMarketPlayer, FairWeatherPlayer and TaxAvoiderPlayer. These are internal enum names, not independently verified PC22 MyLEAGUE UI labels, mode availability or role rights. In particular, career/progression-looking flags must not silently become ordinary MyLEAGUE edit options. The earlier research's21 personality candidates are a different catalog, not21 proven native flags.

The raw Getter `0x97c0c0(PLAYER*,badge_id,normalize_boolean)` reads packed bytes `+0x4bb..+0x4e2`. Flag0 returns raw levels; a nonzero normalization flag returns3 for positive one-bit fields. The maximum Getter `0x19500f0(id)` returns1 or4 for valid IDs0..98 and0 outside the range. Neither proves that ID0 should be called or that raw packed values above maximum are legitimate.

## Effective level is a separate source

`0x97b870` begins with similar raw extraction, then walks the list rooted at `PLAYER+0xd8`. It compares modifier-node metadata with `PLAYER+0x354` low3 bits, requires the low13-bit selector `0x1fff`, and calls `0x969b30(node,badge_id)` for a signed adjustment. Aggregate adjustments change the returned level and are clamped by the recovered path. This effective Getter is used by the original coupling rules.

The selected modifier Getter has no unwind entry, but its actual99-target dispatch at `0x969f1c` closes bounded straight-line leaves. Output025 records each signed2/4-bit field's DWORD offset and shift operations through RET, rather than pretending a prefix window is a complete unwind-defined function. Modifier provenance, lifecycle, list stability and mode/save semantics remain unqualified. A raw-byte-only preflight is insufficient to predict effective-level coupling guards.

## Normal original setter rules

`0x992d40(PLAYER*,badge_id:int,level:uint8,rule_flag:int)` uses rule flag0 in original external UI callers. Recursive rule application uses1. Using1 as a general entry would bypass original logic and is not an approved shortcut. When raw level already equals the supplied value, the setter returns early. Otherwise, flag0 plus a positive value dispatches special rules for selected IDs5..25:

| IDs and internal names | Recovered behavior |
|---|---|
| 5 LowFriendliness / 8 HighFriendliness | Select one at Native maximum and clear the other; requesting5 is blocked when effective Expressive21 is positive |
| 9 SmallEgo / 12 BigEgo | Select one at maximum and clear the other |
| 13 HighWorkEthic / 16 VeryHighWorkEthic | Select one at maximum and clear the other |
| 17 NegativelyMotivated / 20 PositivelyMotivated | Select one at maximum and clear the other |
| 21 Expressive / 24 Unpredictable / 25 LaidBack | Calls trait helper `0x970360`; clears all three, then sets21,24,both,or25 according to the chosen trait state and effective prior levels |

The four3-entry arrays contain zero placeholders, which the Native loops skip. Those zeros do not imply assigning Badge0. The trait helper's states2/3 can enter a diagnostic/assert path if effective LowFriendliness5 is positive; it does not silently clear that field. The exact chosen state uses effective getters, so a detached raw snapshot cannot stand in for this logic.

Non-special cases use their own per-ID maximum and preserve neighboring packed bits. The common tail clears `PLAYER+0x31c` bit6 and invokes current delegate slot `0x1178`. Three previously recovered league vtables point that slot to a no-op; the current runtime/delegate still needs exact qualification. Recovered code is not proof that arbitrary scene/thread/context is safe.

## Evidence and remaining execution gap

Source directory: `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/`.

- 014/017/018: full setter, trait/effective Getter bodies and original rule-flag0 external callers.
- 020/023: explicit absence of unwind entries for selected leaf candidates, not function absence or recovery failure.
- 021/024: bounded entry windows revealing real dispatch tables; bytes after RET/table data are not extra code.
- 022: initial99-field/mask/max reconstruction before the name and modifier joins; retained as history.
- 025: complete selected99 raw field/name/max/modifier joins and positive-rule tables, validated directly against the pinned PE by the packaged tool. It supersedes022's unknown-name field without rewriting that evidence.

The earlier019 window at `0x97c6b0` begins inside an instruction. It is not an entry or ABI proof. New reconstruction follows actual dispatch targets and does not reuse that prefix.

The Badge binding remains explicitly `not_callable` and the action has no runtime handler or submission endpoint. Remaining work: qualify modifier source/list invariants and effective preflight, establish current-mode field rights and sentinel exclusions, represent all intended/collateral changes without changing role decisions, close context/thread/current-identity/readback behavior, and obtain concentrated Human approval before any live scenarios. No game attachment, Native call, UI, simulation or Save/Reload validation occurred. Full M0–M5 remains incomplete.
