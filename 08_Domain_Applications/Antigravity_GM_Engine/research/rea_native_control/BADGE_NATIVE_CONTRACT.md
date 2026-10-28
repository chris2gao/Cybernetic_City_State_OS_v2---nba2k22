# Badge Native edit with explicit coupled states

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`; pinned PC22 EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. This is an implemented deferred Native program with static/offline evidence. No new game attachment, real mutation, UI/simulation/persistence proof or independent acceptance is claimed.

## Role and parameter contract

Logical requirement `PLAYER.EDIT.BADGE_SET` maps to `PLAYER_SET_BADGE`. It requires an explicit host-authenticated WORLD_ADMIN action grant, team scope, current-context/phase applicability and Human-approved live scenario before actual execution. Ordinary GM, Coach and Player profiles cannot obtain Badge self-improvement through this interface, even if their submitted JSON claims permission. The raw facade remains a trusted technical backend, not a second authorization authority.

Parameters are exact and mandatory:

| Parameter | Meaning |
|---|---|
| `team_id`, `player_id` | Current owning roster TEAM/PLAYER integer UID0..65534, resolved through existing roster/contract ownership checks |
| `field_id` | One of98 non-sentinel internal Native enum names, obtained from `get_allowed_values`; `NONE` is unavailable |
| `value` | Exact integer raw level0..the selected field's maximum1 or4; booleans/out-of-range values are rejected without clamping |
| `expected_before` | Explicit raw levels for the complete possible coupled group, from the approved current snapshot |
| `expected_after` | Explicit complete group after-state chosen/acknowledged by the caller; the executor rejects disagreement with original rules |

An isolated skill has a one-field group. Four exclusive pairs and Expressive/Unpredictable/LaidBack require the entire pair/triple, even for a zero/unchanged input. Unspecified fields are not filled in. Example interface payload, not a live approved target:

```json
{
  "team_id":20,"player_id":55,"field_id":"HighFriendliness","value":1,
  "expected_before":{"LowFriendliness":1,"HighFriendliness":0},
  "expected_after":{"LowFriendliness":0,"HighFriendliness":1}
}
```

`data/player_badge_fields.json` exposes backend IDs/bit fields and signed modifier layout derived from static evidence025. Role cards expose names, per-field levels, meaning limits and exact coupled groups without addresses or offsets. There are80 maximum4 fields and18 non-sentinel maximum1 flags. These are original internal names; PC22 MyLEAGUE UI labels, availability of career/progression-looking flags and their broader gameplay meaning remain unverified. Explicit technical world editing does not silently treat them as ordinary UI actions or persona rights.

## Original rules and preflight

The implementation retains the original four-argument setter `0x992d40(PLAYER*,badge_id,level,rule_flag)` with **flag0**. It does not call internal recursive flag1 as an edit shortcut. Exact rules, internal names and primary static sources are in [Badge recovery](BADGE_NATIVE_RECOVERY.md).

Before any Native call, the handler resolves the original league delegate footprint (team Getter and no-op Badge notification), the exact roster player, raw group values and the full possible after-state. It inspects the current modifier list rooted at PLAYER+0xd8, rejects cycles/unreadable nodes and applies the actual selector/stage gate and signed2/4-bit encodings. The1024-node bound is an inspection budget, not an inferred game population maximum. A larger list defers rather than truncating the sum or proceeding.

Original effective Getter `0x97b870(player,id,0)` then independently checks the snapshot-derived effective levels of LowFriendliness, Expressive and Unpredictable. Modifier memory, list root, stage selector, player/team identity and delegate footprint must remain unchanged across this preflight. The implementation qualifies the current operation's inputs without claiming a general semantic model of modifier provenance or lifecycle.

The executor predicts only the original game's consequences of the supplied request. It rejects the existing rule that blocks LowFriendliness when effective Expressive is positive and the trait-helper assertion conditions involving effective LowFriendliness. It rejects any caller after-state that differs from those original consequences. A raw unchanged-primary value follows the original early return and cannot secretly normalize other Badges. No preferred personality, alternative Badge/value or rule bypass is selected by the executor.

The batch aggregator reserves the entire possible group plus relevant rule-read fields. For example, a positive Expressive edit also reserves LowFriendliness, and a positive LowFriendliness edit reserves Expressive. Conflicting writes or guard changes are returned to the roles, not resolved by choosing a winner. Trades overlap the whole Player resource. Distinct independent skill fields can be submitted as separate explicit intents; the batch is not atomic.

## Call, readback and interruption

After three read-only effective Getter calls, the handler invokes the original setter exactly once. Four is the maximum number of direct Native calls, not a claim that original internal recursion makes no additional game calls. The shared GUI-thread one-shot transport and existing current-context host guard remain required.

It snapshots196 contiguous stat/Badge bytes and the cache DWORD, requires every unrequested field and padding bit to remain unchanged, checks all explicit raw group results and the original bit6 invalidation (or unchanged-primary early return), and rechecks modifier/context snapshots. Internal preservation reads include other stat bytes, but results disclose only the caller's explicit Badge group and observation metadata; Potential is not emitted.

A mismatch, concurrent change, blocked precondition or interruption does not trigger another Setter, finish a changed plan or roll back automatically. Native returns and same-handler checks remain `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`. Existing journal claims/resources and a separately supplied independent observer govern UNKNOWN recovery and later confirmation. There is no assertion that same-handler equality proves lasting gameplay effect.

## Verification and remaining scope

Nine focused offline tests exercise the actual compiler, role planner and JS handler over a synthetic Native ABI/memory model. They cover all98 non-sentinel IDs, exact per-field maxima, flag0 ABI, source-field correspondence, every exclusive pair, trait combinations including temporary modifiers, signed/selector cases, cycles/inspection budget, stale or unexpected group states, unchanged-primary behavior, identity changes, unrequested bytes/padding, cache mismatch, interruption and cross-rule batch conflicts. They do not execute the game binary. Fixed-candidate verification results belong in the Run progress pointer only after execution.

Runtime signature checks pin the setter, trait helper, raw/effective Getters, modifier dispatch, maximum switch and delegate methods. The earlier discovery-only `player.badge_set_candidate` stays explicitly noncallable as historical evidence; this implementation uses distinct qualified bindings and never promotes that incomplete candidate by deleting its warnings.

Remaining: host integration with the real current save/scene and approval scope, independent readback, per-mode UI/gameplay semantics, natural modifier evolution, and UI/simulation/SaveReload validation. Existing roster resolver covers15 current roster slots; free-agent/reserve/global player resolution is not inferred. Potential, body/development/profile operations, remaining M2/M3 work and full M0–M5 completion remain open. Concentrated exact-save/object/value scenarios require Human approval before live changes.
