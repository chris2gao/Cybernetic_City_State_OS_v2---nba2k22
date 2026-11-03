# Daily training partial Native operations

Status: recovered composition, **offline-tested only**. No game attachment, new Native call observation, UI evidence or persistence proof. This extends existing TEAM training Apply, not the home/away intensity0..5 profile or individual training system.

| Role requirement | Native action | Exact submission parameters | Meaning/boundary |
|---|---|---|---|
| TRAIN.TEAM_FOCUS | TRAIN_TEAM_PATCH_FOCUS_RAW | team_id, date, focus_values_raw[3] | Replace three finite float32 values in the selected day's existing training input. Actual UI units and slot labels remain UNKNOWN; no division by100, normalization or optimized allocation. |
| TRAIN.TEAM_PROFILE | TRAIN_TEAM_PATCH_PROFILE_RAW | team_id, date, profile_values_raw[3], subfocus_points_raw[38] | Replace the three raw profile bytes and38 raw subfocus bytes. Byte encoding0..255 is not a certified set of meaningful UI choices; names remain UNKNOWN. |

Roles still require explicit host identity/action grants and phase applicability. A Player role is not automatically entitled to edit team training. The Native facade's encoded-value capability does not grant that identity permission.

## Existing Native mechanism reused

`training.daily_by_date` (`0x12f1390`, TEAM*, native date key) returns the existing56-byte daily record. `training.set_team_on_date` (`0x1325f10`, TEAM*, same date key, private64-byte input) applies the original service. Both are existing recovered bindings, not new function discoveries.

Copy the entire existing daily record into private input+8. For focus, replace only input+8..19 (three float32). For profile/subfocus, replace only input+20..60 (three+38 bytes). Leave input+61 and later copied bytes untouched, preserving raw intensity and neighboring bits. All bridge writes are to caller-owned allocation; the service performs the game operation. No direct writes into the live daily object.

If the exact requested day has no existing record, stop before Apply. Do not create a day, advance the game, choose another date, or construct default values. Original Apply may no-op on game days; a returned call does not prove the requested state is visible. Preserve `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED` until independent readback confirms the exact fields.

## Validation

`tests/training_patch_harness.js` executes the real handler in Node VM with an instrumented private-pointer model and counting Native stub. Tests compare every input byte, prove game-memory model bytes stay unchanged, preserve exact TEAM/date arguments, check missing-date behavior and reject malformed/nonfinite/out-of-width input. This proves input composition and bridge sequencing only, not game ABI effects or scene suitability.

The existing daily getter and Apply signatures remain build-bound to SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. Future live scenarios need current save/TEAM/date binding and the Human-approved concentrated operation scope.
