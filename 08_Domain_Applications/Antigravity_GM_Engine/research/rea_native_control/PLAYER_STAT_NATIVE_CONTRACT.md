# Indexed Native Player ability/durability and tendency edits

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`, fixed PC22 build SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. This is a deferred implementation with static and offline evidence, not new live-game acceptance. Existing capture/database/history code is unchanged.

## Inputs, values and role rights

| Interface | Exact parameters | Accepted values |
|---|---|---|
| `PLAYER_SET_ATTRIBUTE` | `team_id`, `player_id`, `field_id`, `value` | Explicit named qualified ability/durability field; UI integer25..99 |
| `PLAYER_PATCH_ATTRIBUTES` | `team_id`, `player_id`, `values` object | Nonempty exact field→UI integer25..99 map |
| `PLAYER_SET_TENDENCY` | `team_id`, `player_id`, `field_id`, `value` | Exact tendency field; integer0..100 |
| `PLAYER_PATCH_TENDENCIES` | `team_id`, `player_id`, `values` object | Nonempty exact tendency→integer0..100 map |

TEAM/PLAYER IDs are integers0..65534 and refer to the current supplied roster identity, not names or slots. Examples below are interface examples, not an approved live target:

```json
{"team_id":20,"player_id":55,"field_id":"intangibles","value":50}
{"team_id":20,"player_id":55,"values":{"SHOT_TENDENCY":80,"PLAY_DISCIPLINE_TENDENCY":65}}
```

`data/player_stat_fields.json` derives the internal index/byte effect from all156 entries of the actual setter switch and joins existing field definitions. There are55 named ability/durability fields, of which54 are enabled. Potential is identified but blocked: its delegate branch invokes the broader refresh `0x99b670`, whose derived effects are not yet qualified. Native indices51/56 remain unclassified and unavailable. All99 tendency positions have recovered0..100 writes;48 have existing names,51 remain explicitly `UNKNOWN_SEMANTICS`. Unnamed stable IDs such as `UNIDENTIFIED_TENDENCY_08` are technical editor identifiers, not invented behavior names.

Role grants remain independent of this technical catalog:

- Ordinary GM ability scope is only the existing `intangibles`25..99 exception, and still needs an explicit host action grant. It does not grant general ability, durability, Potential or Badge editing.
- Other qualified ability/durability edits require an explicitly granted `WORLD_ADMIN` profile and owning team scope. Coach/Player do not obtain ability self-improvement through an action-name claim.
- GM/Coach/Player tendency cards expose only the48 named fields, with an explicit action/phase/team grant. A Player additionally must match its own `player_scope` UID.
- Explicit world editors may address the51 unnamed tendency positions, with their meaning still UNKNOWN. Technical field access is not a claim that a persona understands the field.

The four logical requirements `PLAYER.EDIT.ATTR_SET`, `.ATTR_BATCH`, `.TENDENCY_SET`, `.TENDENCY_BATCH` now map to these actual interfaces. Their current role cards list the permitted field IDs and value ranges without Native addresses. The original planning role labels remain separately recorded as source metadata. Batches reject conflicts on the same player/field; trades overlap the whole player resource. No executor chooses values, redistributes ratings or optimizes tendencies.

## Recovered original business path

`0x990a10(PLAYER*, native_stat_index:int, value:int)` is the original indexed UI setter, not a broad parent-object copy. Its156-entry jump table at `0x991f08` dispatches the given stat. Ability cases clamp to25..99 and call their dedicated Native setters; tendency cases clamp to0..100 and write the mapped byte. The wrapper rejects out-of-range input before any call rather than relying on a silent clamp.

Every one of the54 qualified ability leaves has the same verified prefix: clear `PLAYER+0x31c` bit6, transform the UI value to `3*value-75`, and store its own byte. Existing native profile conversion agrees with this25..99 scale. The leaves also query membership in the Native player pool and may set original global UI/cache flags. These are disclosed Native side effects, not direct script writes. Tendencies store the supplied integer directly.

The original setter then calls the UI-value getter `0x978360` and the current delegate slot `0x1248` with the player, stat index and resulting value. In the recovered generic delegate this points to `0x11aeb40`: it invokes broad refresh only for index34/Potential and otherwise returns. The runtime requires that known callback plus the existing team-index method footprint before editing. Potential is excluded before entering the Native function, preserving the boundary of the qualified path.

The script resolves the exact current TEAM/PLAYER, snapshots156 stat bytes and the cache DWORD, invokes the indexed setter once per explicitly provided field, and rechecks identity. It requires the entire stat region to equal the original patched only at supplied bytes. Ability edits must show only the expected bit6 invalidation in the cache word; tendency edits preserve it. Result details disclose only requested field values, never the whole raw stat snapshot or unrequested Potential. There is no parent editor state, private whole-Player copy or script write to game-owned memory.

The maximum direct Native call count is now three times the number of requested fields: original Getter before, one original Setter, original Getter after. A multi-field operation is not atomic: an exception or unexpected postcondition leaves an unknown result, preserves the claim/resources and does not retry, finish the remaining fields or roll back automatically. The adapter discards the Native tail-callback return because the original UI callers do not use it; it does not fabricate a success return code.

## Evidence and validation limits

Primary evidence under `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/`:

- `player_attribute_tendency_field_writers_011.json`: structural field writers that revealed the indexed services.
- `player_indexed_stat_setters_012.json`: complete public indexed setter and representative encoding leaf.
- `player_indexed_stat_field_contract_015.json`: all156 dispatch entries and existing-profile/name join.
- `player_stat_delegate_thunk_016.json`: exact notification branch and Potential exception.
- `player_refresh_indexed_helpers_009.json`, `player_indexed_leaf_windows_010.json`: bounded getter/helper leads. Jump-table bytes after RET are data, not extra instructions or functions.

`tools/recover_player_stat_fields.py` reproduces the selected switch/profile join without opening the game process. Local PE/Capstone evidence is explicitly not REA Provider output. REA remains the deferred Native transport. No whole-game Ghidra import was retried.

Eight focused offline tests run the real compiler, role planner and JS handler over a synthetic Native ABI/memory model. They cover all54 enabled attribute indices, all99 tendency byte locations, untouched stat/cache fields, exact boundaries, protected Potential, wrong delegate, partial interruption, role/own-player policy and the independent source-prefix/field-map correspondence. These tests do not execute the game binary or prove real UI/simulation behavior.

Remaining gaps: actual current save/scene binding, live invocation, independent observer integration, UI/cache display effects, simulation/natural-growth behavior and persistence. None is inferred from an offline PASS. Potential and two unnamed attribute cases remain unavailable. Before real changes, the Human must approve concentrated scenarios naming the loaded save, exact fields/objects, values and Native cache effects; this development brief is not unlimited live-write authority.

## Badge discovery is separate

`0x992d40` is now known to take `(PLAYER*, badge_id:int, level:uint8, rule_flag:int)`. Real original UI callers use flag0; recursive coupling uses1. IDs0..98 have per-ID maximum1 or4, and the positive-level path for some personality IDs can change other badges through original mutual-exclusion/trait rules. The implementation must not choose flag1 as a shortcut or pretend this is an isolated bit setter.

The full8892-byte function, coupling helpers and original UI callsites are retained in `player_indexed_badge_setter_014.json`, `player_badge_coupling_helpers_017.json`, `player_badge_setter_callers_018.json`. A known badge predicate/helper window starts inside an instruction at `0x97c6b0`; that prefix in `player_badge_getter_tail_and_dispatch_019.json` is not an entry/ABI proof and must not be reused as such. Reconstruct future badge getter paths from actual dispatch targets. Safe coupled-change scope, exact labels and a qualified runtime contract remain open, so the four-argument badge candidate is explicitly noncallable. Attribute/tendency progress does not promote it.

Later static recovery closes all99 internal Badge names, packed fields, per-ID maxima and signed modifier field layouts. See [Badge recovery](BADGE_NATIVE_RECOVERY.md). Internal names are not verified UI/mode labels; effective modifier lifecycle, coupling/assertion preflight and a callable runtime remain open. This supersedes the earlier raw-name gap without promoting the Badge candidate.

The later [Badge contract](BADGE_NATIVE_CONTRACT.md) now provides a distinct original-rule runtime with explicit coupled states and current effective-modifier checks. The discovery candidate remains noncallable; this does not promote Potential, parent copying or ordinary persona rights.

Current Getter/readback follow-up: the [selected Player reader](PLAYER_EDITOR_READ_CONTRACT.md) recovers all153 selected original Getter paths and pins its float constants. Stat edit receipts now use that original Getter for before/after integers, reject after-value disagreement, and recheck bytes/flags/delegate identity across reads. This supersedes the earlier JS-derived before-value estimate while preserving exact supplied values and raw-byte checks. Same-handler agreement still does not prove independent UI/gameplay/persistence.
