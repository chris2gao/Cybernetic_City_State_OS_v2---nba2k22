# Selected Player reads and capture-free role snapshot projection

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`; fixed PC22 build SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. Implemented deferred read program and offline receipt adapter, with no new game attachment/capture or live acceptance. Existing production acquisition, SQLite/history and publishing code are unchanged.

## Native query

The existing `player.profile` reader still returns its original identity/contract subset. A separate `player.editor_state` dataset maps to `READ_PLAYER_EDITOR_STATE`. It fills the current-value input gap for [attribute/tendency](PLAYER_STAT_NATIVE_CONTRACT.md), [PlayType](PLAYER_PLAYTYPE_NATIVE_CONTRACT.md) and [explicit coupled Badge](BADGE_NATIVE_CONTRACT.md) operations; it does not silently change the old reader's return shape or claim complete PLAYER coverage.

The query supplies exact `team_id`, `player_id` integer UIDs0..65534 and a `projection` object with **all four arrays**, explicitly empty when unneeded:

```json
{
  "team_id":20,"player_id":55,
  "projection":{
    "attributes":["driving_layup"],
    "tendencies":["SHOT_TENDENCY"],
    "badges":["Expressive","Unpredictable","LaidBack"],
    "play_types":["1","4"]
  }
}
```

This is an interface example, not an approved live target. At least one field is required. Wildcards, duplicates, unknown IDs, `potential` and Badge `NONE` are rejected before a transport call and by the runtime's projection validation. There are54 named ability/durability fields,99 tendency positions,98 non-sentinel Badge fields and4 ordered slots:255 selectable fields, not a complete PLAYER object or255 Native functions. The51 unnamed tendencies remain explicitly unknown in meaning. An explicit read grant does not promote their ordinary-role edit rights.

The current target resolver checks the requested team's15 current roster slots, exact UID and current/contract ownership. Free agents, reserves and global player lookup are not inferred. Those remain part of the full task's outstanding object-resolution scope.

## Recovered Getter and snapshot behavior

`0x978360(PLAYER*,stat_index:int)` returns the original integer view. The packaged `tools/recover_player_read_getter.py` follows all153 selected paths from its159-entry table, checks each load against the independently recovered Setter field, rejects calls/memory destinations and records the actual one-third/25 float constants. Artifact`static/player_stat_read_getter_contract_026.json` retains instructions, constants and code/table hashes. Runtime signatures pin both code/table and float data. This uses original Native conversion and current rounding mode, not a guessed JS/Python attribute formula.

Badge raw levels come from the recovered packed fields; effective levels call the original `0x97b870(player,id,0)` and compare with the current signed-modifier snapshot. `runtime/player_modifiers.js` is shared by this reader and the Badge Setter, so selector/stage/cycle/read-budget checks do not diverge. Each selected Badge exposes both raw and effective values; an effective temporary increase is not mislabeled as a raw edit or an unlocked UI tier. The four PlayType nibbles use the existing ordered category layout.

The maximum direct Native calls equal selected attributes + tendencies + Badges (251 for the full projection); PlayType-only reads use0. There are no Setter bindings or calls. Full196 stat/Badge bytes, slots, cache word and relevant modifier snapshots are bracketed before/after. A changed bracket, target or effective-Getter mismatch emits no successful read snapshot. A bracket match is **not an atomic snapshot guarantee** or proof that no transient ABA/concurrent event occurred. Values remain same-handler observations; no independent UI/effect/persistence claim follows.

Attributes must match the recovered Native Getter25..99 range. A tendency outside its known0..100 edit range is retained as the actual observed integer, marked outside that edit contract rather than silently clamped. Unrequested fields, Potential, arbitrary byte dumps and pointer lists are not emitted.

## Host receipt to role data

`PlayerEditorSnapshotProvider` consumes one completed `NativeActionResult` and performs no process lookup, transport dispatch or recapture. It checks the exact action/outcome, target/projection, read-only bracket flag, field shapes and explicit observation provenance. It freezes the receipt and host context against later accidental caller mutation. Host labels include world/save/generation/season/phase/snapshot and are checked against the recipient profile.

Those labels are **HOST_ATTESTED_NOT_NATIVE_SAVE_DETECTION**. `NATIVE_TRANSPORT_RECEIPT` requires its observation reference to match the transport's evidence ID; `OFFLINE_FIXTURE` remains visibly marked as such. This is binding/shape validation within the trusted host boundary, not authenticity verification of an operator-supplied receipt or proof that a host save label matches the real game. Real context guards and evidence provenance still require integration/validation.

The provider is supplied to the existing `RoleCapabilityService.read_role_visible_data`; that method continues to consume snapshots and does not start Native capture. Read grants are exact flat field tokens such as `attributes.driving_layup`, `tendencies.SHOT_TENDENCY`, `badges.Expressive` and `play_types.1`. `identity` and `observation` must also be granted, so the fields retain target/provenance. Missing captured fields, wrong team/context or ungranted dataset fail rather than producing defaults. Other captured fields are not returned. Field records contain meaningful values, names/range status and provenance without Native offsets/RVAs.

Reading is separate from editing. A Player/GM/Coach may receive an explicitly granted Badge observation without acquiring a Badge action grant. Team subject scope and field visibility come from the trusted host; this adapter does not invent persona privacy or self-improvement rules. Badge editing remains WORLD_ADMIN-only, and Player editing continues to enforce its own UID/slot/field restrictions.

Typical host sequence is an explicit `NativeReadFacade.read(NativeReadQuery(...))` with an authorized transport, then provider construction from that receipt and the host's context, then capture-free role projection. Without a transport the read facade returns PREPARED; it does not attach to the game. For a future Badge edit, the caller reads every name in the capability card's possible coupled group and uses its raw levels as `expected_before`; it still decides and explicitly supplies `expected_after` itself. No auto-decision or Setter is triggered by the reader/provider.

## Evidence and remaining work

Ten focused offline tests exercise the actual read compiler/handler and role provider, all255 selectors/251 direct Getter calls, raw/effective differences, original Getter overrides, out-of-edit-range tendencies, forbidden projections, concurrent/fault snapshots, immutable receipt projection, provenance/context/team failures, read/edit rights separation and inert default transport. They use a synthetic memory/ABI model. Full fixed-candidate Managed results belong in the progress pointer only after execution.

Current implementation does not replace the production data layer, prove real save/world identity, provide all child objects/unclassified stats, independently confirm writes or establish live/UI/persistence acceptance. Full M0–M5 remains active, including real context/data/observer integration, remaining GM/Coach operations and Player object/profile coverage. Source/image reads here are local PE/Capstone, not REA Provider results; actual Native execution remains the explicitly enabled REA transport path.
