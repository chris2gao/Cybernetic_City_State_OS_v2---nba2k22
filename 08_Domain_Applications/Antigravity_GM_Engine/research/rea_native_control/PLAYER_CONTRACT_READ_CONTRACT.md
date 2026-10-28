# Original Player contract readback — checkpoint011

PC22 build SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. Static local PE/Capstone and offline synthetic execution only. No new game attachment/capture, business mutation, UI test, save detection or persistence proof. Full M0–M5 is incomplete.

## Corrected contract semantics

The legacy technical profile used4 bits for years_left_on_contract. Original Getter0x9886c0 extracts **5 bits at PLAYER+0x32c, shift18**, adds extension length from+0x340 bits15..17, and optionally adds the option-year count. Input flag0 excludes option years; flag1 includes them. Option encodings0/1/2/3 add0/1/1/2 years respectively. Its original assertion path is reached when the unsigned sum exceeds6.

The17-field control-layer contract descriptor now overrides this field to5 bits with a fixed primary-source pointer. The original production memory_field_profile.json is unchanged; data acquisition/database/history pipelines are unchanged. The existing player.profile technical handler benefits from the corrected RAW width. Its raw field is **base non-option years**, not the total returned by either original Getter. Native sums beyond6 are preserved as raw evidence and are not clamped or called through the assertion-bearing Getter.

The original six-way salary Getter0x9888b0 maps indices0..5 to PLAYER+0x1a4..0x1b8 and masks the upper bit. All six dispatch-table targets and complete leaf paths were recovered. Original Setter0x998820 preserves the upper bit and unsigned-clamps supplied values at0x7fffffff. Therefore a uint32 wage can be encoded in a signing proposal without being applied unchanged to Player salary storage. The role signing parameter card now discloses these consumer semantics; no salary-edit action is added.

## Query and exact behavior

```python
NativeReadFacade(control).read(NativeReadQuery('player.contract_state', {'player_id': 55}))
```

READ_PLAYER_CONTRACT_STATE resolves the exact UID through the existing original Player lookup, reads the17 scoped raw contract fields, calls the six original salary Getters, and conditionally calls the two remaining-year Getter forms. Each returned Getter value must agree with the independently decoded raw fields/formula. It resolves UID again and brackets selected contract bytes, current/contract Team links and IDs, and the two relevant130-word flags. Changed identity/selected state or Getter disagreement emits no snapshot. Unrelated stat changes do not invalidate a stable contract observation.

The maximum is10 direct Native calls: two UID resolutions, six salary Getters and two year Getters. For each unsafe year sum, the result contains value:null and status:BLOCKED_NATIVE_ASSERTION_SUM_GT6; that Getter is skipped. Without/with-options guards are independent. There is no Native setter, offer, option-mark change or contract processor.

Output contains exact Player UID, current and contract Team IDs (null when absent), contract_raw, wages_native, explicit option encoding/name/year count, original remaining-year observations and two raw flag values. The130 bit9 selection mark is reused by other game systems and is not a durable signed/exercised-status certificate. No arbitrary Player bytes, pointer or Potential is output.

The existing global UID lookup is reused; complete live global/free-agent/reserve coverage is not certified by offline tests. Matching brackets do not prove atomicity or exclude ABA. Host save/world/generation/season/phase, capture provenance, role field grants and a sanitized provider remain necessary. No dedicated contract snapshot-provider or automatic production capture integration is claimed. These observations can support a future independent signing observer; running this handler inside a signing operation alone would not establish independent completion.

## Further original signing/option findings

- In the applicable non-ten-day/non-two-way, non-extension signing branch, positive ForcedWage[0] selects the six explicit salary Setter calls. Required active years with a zero slot reach assertion logic. Zero first ForcedWage selects the distribution calculator instead. Ten-day/two-way branches calculate wages rather than honor the same explicit array. These are conditional consumer facts, not a qualified signer.
- ProcessMarkedOptions0x12bfec0 consumes130 bit9 and the current option/remaining-year state; it can change contract years/options, emit events and update team state. Its only accepted direct caller recovered by the bounded caller tool is the whole-league loop0x1290da0, which also refreshes teams and ends with0xee0180(0). The meaning of that final service is unresolved; no phase advance is proven. The loop is not an individual contract action.
- Mark producer0xe9fcc0 opens a UI dialog using current selection/context; response2 sets bit9, response3 clears it, other responses leave it. Global0x1290e60 resets marks, makes game decisions and ends with0xee0180(20), whose state meaning remains unresolved. Neither is an exact caller-supplied Player/decision Setter. The field-writer scan also finds unrelated uses of the same bit; offset matching does not qualify object semantics.

SIGN_FREE_AGENT and CONTRACT_OPTION_ACTION remain unavailable. Next is exact-term fresh signing construction, safe original modes/context and option decision binding, plus current identity and independent roster/contract completion integration. No raw business-memory workaround or automatic pricing is authorized by these discoveries.

## Evidence and reproduction

Run-relative static sources012..021 preserve complete consumers/UID resolvers, distribution/submission callers, leaf windows, bounded mark-writer candidates, marked-option callers, the phase loop and mark producers. The writer scan examined663 candidate instructions across489 candidate entries within4,758,923 decoded bytes. Candidates are not qualified setters; scopes, limits and missing unwind entries remain in the evidence.

```powershell
python -X utf8 -B tools/recover_contract_readback.py --out <new-evidence.json>
python -X utf8 -B -m unittest discover -s tests -p test_player_contract_read.py -v
```

Primary packaged source: Run static/player_contract_native_readback_021.json. The recovery joins each dispatch slot to the actual leaf operand, retains complete year Getter/assertion code and pins code/table bytes. Nine focused tests run shipped handlers against synthetic memory, including the existing profile regression, upper salary flags,5th base-year bit, option counts, guarded invalid sums, Getter mismatch, selected-state changes and null-team observations. No game code is executed by these tests.
