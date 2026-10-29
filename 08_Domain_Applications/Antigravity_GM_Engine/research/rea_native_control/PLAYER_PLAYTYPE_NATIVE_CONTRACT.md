# Four dedicated Player PlayType Native setters

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`; fixed PC22 EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. This is new static recovery and deferred implementation, with no new game attachment, live mutation, independent effect evidence or Save/Reload proof.

## Supplied values and role interface

Native action `PLAYER_SET_PLAY_TYPES_1_TO_4` now accepts an explicit nonempty slot object:

```json
{"team_id":20,"player_id":55,"slot_values":{"1":4,"2":2,"3":0,"4":15}}
```

Those IDs/values are an interface example, not a selected live scenario. TEAM/PLAYER IDs must be integers0..65534. Slot keys must be exactly strings `1`..`4`; values must be integers0..15. The earlier unbound array placeholder is replaced by this recovered contract, without an implicit array conversion. A key omitted by the caller is untouched, not filled with zero or another preference.

The existing `config/state_io_native/player.json` and R04B catalog supply the category names:

| Value | Existing PC22 category | Value | Existing PC22 category |
|---|---|---|---|
| 0 | None | 8 | Post Up Low |
| 1 | Isolation | 9 | Post Up High |
| 2 | Isolation Point | 10 | Guard Post Up |
| 3 | Isolation Wing | 11 | Cutter |
| 4 | P&R Ball Handler | 12 | Handoff Receiver |
| 5 | P&R Point | 13 | Handoff Passer |
| 6 | P&R Wing | 14 | Mid Range |
| 7 | P&R Roll Man | 15 | 3 PT |

These are ordered play-category assignments. They are not individual play CRCs and do not guarantee a CPU selection rate, available team Book entry or a play's actual execution. Native code also masks an input to four bits; the wrapper rejects out-of-range values before calling it rather than silently wrapping them.

Logical requirements `PLAYER.EDIT.PLAY_TYPE_1`..`_4` keep their PR18 identities and map to the existing action. Each role card narrows the schema to its own single slot, and the aggregator enforces exactly that key. Different slot intents may share a batch; two values for the same player/slot require role resolution. The resource also overlaps a trade involving the same player. No slot order or value is chosen by the executor.

An authenticated host profile must explicitly grant the action and owning team, with current-context/phase attestation. A Player persona additionally needs its target in `player_scope`. Default permissions remain empty. Technical mutability does not let a Player raise attributes or use another player's identity; persona contract/trade/training requests remain external requests.

## Native functions and effects

| Slot | Native leaf RVA | Win64 arguments | Exact field |
|---|---|---|---|
| 1 | `0xf1e370` | `(PLAYER*:RCX, category:int:EDX)` | `PLAYER+0x168`, bits0..3 |
| 2 | `0xf1e390` | same | bits4..7 |
| 3 | `0xf1e3b0` | same | bits8..11 |
| 4 | `0xf1e3d0` | same | bits12..15 |

Each recovered leaf is a complete straight-line sequence through RET: clear its mask, mask the supplied EDX to15, shift where needed, and OR into the same DWORD. There are no calls, branches, heap operations, child-object accesses or global-context accesses in these bodies. The adapter discards the return; no source-language return declaration is inferred.

The functions were found through decoded writes to the known field and explicit no-unwind leaf discovery. A slot1 direct-call scan returned zero; a static absolute-pointer scan also returned zero. Subsequent code-reference recovery found actual startup LEAs installing each setter at offset `+0x88` of a dynamically allocated property descriptor. This explains why a direct-call search alone missed them. Raw descriptor identifiers and their unproven name mappings are retained; no matching property name or class name was invented from them. Existing PLAYER field layout, the exact setter effects and independent assign-Playbook consumer path support the slot correspondence.

The handler resolves the exact current roster PLAYER, calls only the supplied slot setters in ascending slot order, then checks identity and the entire `+0x168` DWORD against the old word patched only at requested nibbles. All upper flags, including the separate candidate initiator field, must be preserved. The script performs no writes to game-owned memory. Direct Native-call budget is the number of supplied slots,1..4. Interruption or mismatch is unknown; no retry, automatic completion of the other slots or rollback is attempted.

No parent editor copy, broad Player refresh, UI event or network packet is invoked. Assigned raw slots are the recovered effect; whether a particular scene requires additional UI/cache notification, how simulation consumes the choice, and later automatic overrides remain explicit validation gaps.

## Evidence and repeatable discovery

Repository run `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/` contains:

- `player_playtype_field_writers_001.json`: offset-selected decoded candidates, including unrelated objects; these are not611 qualified Player setters.
- `player_playtype_native_leaf_windows_002.json`: four dedicated bodies through their RETs. Bytes after RET belong to padding/other functions and are not counted in a leaf.
- `player_playtype_slot1_callers_003.json`, `player_playtype_native_data_references_004.json`: bounded negative direct/data-reference results.
- `player_playtype_registration_leads_005.json`, `player_property_setter_descriptors_006.json`: positive startup callback-address references and descriptor writes.

Reproduce discovery using `tools/recover_field_writers.py --offset 0x168 0x169 --out <new-json>` and selected `recover_entry_windows.py` calls. The tools read the pinned local PE and are not REA Provider output or runtime traces. No whole-game Ghidra import was retried.

Six focused offline tests run the real compiler, role planner and JS handler against synthetic Native calls/memory. They check all four slots, exact multi-slot ordering/values, enum/key/type rejection, untouched slots/flags, slot-scope escape, persona identity and interrupted/incorrect outcomes. A test fixture's initial four repeated neighbor-bit flips cancelled one another; it was corrected to preserve a single injected corruption. That local fixture correction is not a game finding.

## Other Player edits remain open

The selected parent copy body at `0x8fbe60` is now recovered across its full31509-byte unwind range, plus child copies `0x8f3b50` / `0x8f9270` / `0x915dd0` and refresh `0x99b670`. This required an explicit selected-function64KiB bound; the default remains24KiB. It was not a whole-game analysis.

Parent copy transfers pointers at `+0x78..+0xe0`, processes many unrelated fields and contains eight identity/context callback sites. `0x11f60d0` checks mode/context fields; `0x11f38e0` checks whether a destination lies in a16MiB native pool window. The final refresh has additional calls and derived-state effects. Full code extent alone does not close safe clone construction, pointer ownership, normalization, role field permissions or refresh/readback. The existing parent-copy candidate stays explicitly noncallable; attributes, tendencies, badges and other profile edits are not promoted by the PlayType implementation.

A later separate checkpoint recovered the narrower original indexed stat service, closing54 named ability/durability and99 tendency field writes without parent copying. See [PLAYER_STAT_NATIVE_CONTRACT.md](PLAYER_STAT_NATIVE_CONTRACT.md) for exact role limits, Potential exclusion and offline-only evidence. This supersedes the attribute/tendency implementation gap above; it does not promote the parent copy, badges or other profile edits.
