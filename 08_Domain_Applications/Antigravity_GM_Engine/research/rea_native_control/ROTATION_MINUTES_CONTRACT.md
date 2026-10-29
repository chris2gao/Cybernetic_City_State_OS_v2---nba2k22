# Explicit player rotation minutes — static recovery and deferred implementation

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`, fixed PC22 build SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. Source PR18 remains unchanged at `094f1aa641f93dec2277707ad9dbf5bdb0341247`. This increment is `CALL_LOGIC_RECOVERED` with offline implementation checks, not new live-game acceptance.

Role requirement `COACH.ROTATION.PLAYER_MINUTES` maps to `COACH_ROTATION_SET_PLAYER_MINUTES`:

```json
{"team_id":20,"player_id":55,"minutes":37}
```

These IDs and minutes are an example of the interface, not a selected live scenario. Inputs must be explicit integers: TEAM/PLAYER identities `0..65534`, minutes `0..48`. Zero assigns no rotation minutes. The UI's left/right paths at `0x870860` / `0x89af30` read `PLAYER+0xf8` bits18..24 and send the requested next value through current delegate slot `0x16d8`; the right path bounds assigned minutes at48. The seven-bit native representation is not permission to submit49..127.

## Recovered business chain

1. Resolve the current delegate from global RVA `0x6327f58`. Read its slots `0x2e0`, `0x508`, `0x538`, `0x16d0`, `0x16d8` and require one of the recovered generic implementation profiles. This is a method-footprint check, not proof of a current save, scene or class name. The host must attest those separately.
2. Resolve the exact supplied TEAM and its roster PLAYER using existing identity helpers. Resolve its existing FRANCHISE_TEAM_DATA. Call `0xedefe0(TEAM*)` and require its index to match the resolved franchise record. In the accepted delegates, slot `0x2e0` points to leaf `0x11d8ac0`, which reads `TEAM+0xcaa`. Never substitute another team or player.
3. Call `0x11b2bb0(delegate*, PLAYER*, minutes:int)` using Win64. This native leaf preserves all other `PLAYER+0xf8` bits and replaces bits18..24. The first argument is unused in the recovered body but remains the same current delegate, matching the original UI ABI. Native callers ignore the return; the adapter discards it with a void ABI rather than inferring a source-language return declaration.
4. Follow the original post-change path: slot `0x538`'s thunk `0x1223760` translates `(delegate*,TEAM*,1,0)` into `0x12d21f0(TEAM*,1,0)`. The implementation calls that business function directly with the same TEAM and fixed kind/flag. For kind1 it queries team eligibility through `0xedf480`, obtains franchise data through `0xfda730`, and writes native byte `FRANCHISE_TEAM_DATA+0x11ff9=0`. The recovered eligibility implementations only inspect flags/team identity. The kind0/17/18 branches are not used by this action.
5. Read all15 supported roster slots again. Require stable slot/object/UID identity, exact requested minutes, unchanged other bits and other players' entire `+0xf8` words, and native change flag0. A mismatch or interrupted post-change call is unknown and never automatically retried or rolled back.

Maximum direct Native calls:3 (index getter, minute setter, team-change function). Existing GUI-thread transport, pinned code signatures and journal claims are reused. The script itself never writes to game-owned memory. It does not call menu confirmation handlers, rebuild/optimize the rotation, balance a team total, select a different player or modify the supplied value. Raw same-handler observations remain separate from independent effect evidence.

## Excluded career branch and context evidence

`0x11b2900` is associated with literal `BASE_CAREERMODE_DELEGATE::FELON_Rotationmenu_HandlePlayerMinutesChange`. It compares the selected career player, may clamp the requested value using career limits, and can enter UI messaging. It is explicitly excluded. Accepted slot `0x16d8` must point to `0x11b2bb0`; slot `0x16d0` must point to the recovered constant-true predicate `0x26f1f0`; slot `0x538` must point to the recovered team-change thunk. Three static table anchors support the accepted generic profiles; two anchors share the same selected method footprint. No RTTI class name or live current mode is inferred from them.

Primary static evidence is in repository run `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/`:

- `rotation_adjust_and_system_setter_001.json`: both UI caller chains and0..48 bound.
- `rotation_leaf_field_candidates_002.json`, `rotation_virtual_field_join_002.json`: native leaf discovery and field-to-slot join.
- `rotation_qualified_entry_windows_003.json`, `rotation_delegate_leaf_windows_004.json`: exact leaf/thunk instruction windows. Bytes after RET/tail-JMP are not treated as a function continuation.
- `rotation_team_refresh_business_001.json`, `rotation_team_refresh_dependencies_001.json`, `rotation_delegate_notification_dependencies_001.json`: post-change chain and query implementations.

These are local pinned-PE/Capstone results, explicitly not REA Provider output or runtime traces. REA remains the eventual execution transport. The failed RTTI lookup is recorded in `rotation_virtual_slot_candidates_001.json`; this build has no observed MSVC RTTI name prefix in `.rdata`, so the subsequent join uses decoded fields and method pointers instead.

## Permissions, tests and remaining gaps

Only a host-authenticated Coach profile with this exact action grant, owning the supplied team and a current phase attestation, can submit it. A Player request does not acquire Coach permission. Batches can contain exact minutes for different players; conflicting values for one player require role resolution. Trade operations overlap the same player resource and cannot silently race it. There is no inferred240-minute rule or rebalancing policy.

`tests/test_rotation_minutes.py` runs the real compiler, planner and JS handler over a synthetic memory/Native ABI model. It checks0/37/48, exact argument identity/order, other-bit/player preservation, foreign-team rejection, unsupported/career context rejection, context-index mismatch and unknown outcomes after setter/refresh failures. The synthetic Native model does not prove that the real game executes these calls safely.

Still unverified: current live delegate/save/phase binding; GUI display refresh; actual simulation use; auto-coach overrides; independent readback; Save/Reload. The inherited TEAM resolver covers15 slots, not additional roster representations. A future concentrated Human-approved test plan must name the actual loaded save, exact team/player, before-value, requested value and observation/persistence scope before any game mutation.
