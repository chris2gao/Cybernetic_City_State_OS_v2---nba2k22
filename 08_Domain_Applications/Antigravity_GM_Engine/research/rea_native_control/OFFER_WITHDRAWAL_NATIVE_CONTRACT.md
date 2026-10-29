# Withdraw one expected pending offer — checkpoint013

Static/offline engineering for pinned PC22 EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`; source is local PE/Capstone **NOT_REA_PROVIDER**. New live calls, UI, save persistence and independent acceptance are NOT_RUN. Complete M0–M5 remains active.

## Discovered requirement and scope

The fixed PR18 inventory contains183 requirements including creation, acceptance/rejection and renegotiation, but no separate withdrawal of a pending offer. `data/supplemental_requirements.json` adds **GM.CONTRACT.OFFER_WITHDRAW**, mapped to **CONTRACT_WITHDRAW_PENDING_OFFER**. The source183 objects remain unchanged. `RoleCapabilityService` loads the supplement without permitting duplicate/replacement IDs; the supplement participates in catalog versioning. Coverage now separately reports183 source,1 supplement,184 total requirements. The original50 mapping provenance remains unchanged; current effective mappings are61.

This action removes exactly one caller-selected pending free-agent offer from the active pool through the original cancellation service. It does not accept/reject an offer, choose a competing offer, sign a Player, refund a quota or restore prior negotiation/response state. `GM.CONTRACT.OFFER_ACCEPT_OR_REJECT`, `SIGN_FREE_AGENT` and contract-option actions remain unavailable. Exact current UI labels/eligibility are unverified.

The trusted host supplies GM identity, explicit permission, owned Team scope, phase grant and current world/save/generation/season/snapshot with `FA_SIGNING_OFFERS`. Native parent period22 FA_SIGNING is independently checked. Native save and offer subscene identity remain host attestations. New live state changes require concentrated Human-approved scenarios.

## Exact input and role entry

```python
intent = ActionIntent.decided('withdraw-unique', 'gm20', 'GM.CONTRACT.OFFER_WITHDRAW', {
    'team_id': 20, 'player_id': 55,
    'expected_offer': selected_team_offer['fields']})
```

`selected_team_offer` is an explicitly selected current `signing.team_offers` observation. Supply **all25 registered fields**, including all six ForcedWage slots, signed PissedOffLevel, negotiation/interest flags and term fields. Numeric representation is checked; booleans cannot replace integers. IDs must exactly match the outer Team/Player, Status must be1 OFFERED, Type2 FREE_AGENT and IsArchived0. No partial expectation, default values, inferred status or arbitrary record index is accepted. The input carries decoded registered values, not pointers or raw memory.

The host submits the immutable intent via `submit_decided_actions` with trusted profiles, grants, context guard and an independent observer. `get_allowed_values` identifies the observation source and enum meanings. `NativeControlFacade.withdraw_contract_offer` is an inert preparation/technical dispatch entry without implicit role authorization or process access.

## Original service and evidence

Canonical source: Run `static/sign_pending_offer_withdrawal_contract_034.json`; replay tool `tools/recover_pending_offer_withdrawal.py`. It retains the complete216-byte selected service, roots, fixed caller window and byte signatures.

- Original `0x12b4040` takes `(44-byte game-owned record*, int flag)` and returns int. EMPTY returns0. Nonempty records clear word32's status mask0x3c0000 and return1.
- For prior OFFERED status it resolves the Player UID. The subsequent Type mask0x1c00000 sends non-DRAFT_PICK types directly to the success tail. Therefore the qualified FREE_AGENT2 branch preserves other record bytes and bypasses the later draft-only available-player cleanup path. That other path can change Player/availability and is not qualified here.
- Original caller `0x12bb8fd` supplies `edx=0` and an actual pool-record pointer. The backend reproduces exactly flag0, without assigning a universal business meaning to the flag.
- Distinct period/pool globals0x632b470/0x632b478 are recovered from RIP-relative MOVs. The1000x44 pool at+0x1727a8 and registered field semantics are inherited from the existing signing contract. Original Player UID lookup is reused.

The implementation never clears the field itself. It calls the original service once with the current selected game-owned pointer; no allocator, generator, Process, phase advance, whole-pool cancellation or rollback is invoked.

## Preflight, effects and result

The handler resolves exact Team and Player UID, captures Player bytes, then scans all1000 offers. Exactly one active unarchived non-qualifying Player/Team identity must exist, and every registered field must match `expected_offer`. Archived/qualifying rows do not become substitute targets. It scans the whole pool again and brackets Player, Team, period and roots immediately before the call.

Maximum direct Native calls: **3** — Player lookup, one original cancellation, Player lookup again. Original helper-internal calls are not counted as separate backend calls.

After return1, it requires exact selected bytes with only status bits cleared, equality of every other pool row, unchanged Player bytes/UID resolution and Team resolution, and stable roots/period. No unexpected result is treated as success. Zero/other returns, stale/multiple identities, preflight changes or extra postcall effects stop or produce an unknown result without a second call.

A matching observation emits `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`, `withdrawal_only:true`, `signing_completed:false`, previous OFFERED/current EMPTY and scoped preservation flags. record_index is a transient observation, not durable identity. Matching brackets do not prove atomicity or exclude ABA. The raw record retains its other fields after becoming EMPTY; this is active-pool removal rather than data erasure.

Only a separately supplied context/intent-bound host observer can confirm the requested withdrawal. Without that confirmation, the journal retains the broad Player and Team-offer resource claims across new request IDs. A withdrawal and a new offer for the same Player conflict; the aggregator cannot silently cancel-and-replace or decide new terms. Reconciliation does not replay Native operations.

## Response/commit discoveries that remain disqualified

Sources028..033 preserve the bounded caller/body investigation rather than hiding unsuccessful leads:

| Source / service | Recovered behavior | Why not an exact role signing action |
|---|---|---|
| Process direct callers028 |24 decoded direct references in the stated scan; no truncated result | Indirect calls and all control-flow coverage remain unproven; a reference does not qualify ABI/context |
| 0x12bf5a0 in029 | Scans offers, validates/scores and selects the greatest positive score, copies/processes the selected record and clears competitors; asserts against period22 | Chooses an offer and has broader effects; cannot execute a caller-specified signing |
| 0x12bf900 in029 | Sorts/scans the pool and processes Type0 draft records, including accepted records in a second pass | Whole-pool rookie contract lifecycle, not one specified decision |
| 0x12b54a0/5f80/6650/6f70 in029 | Multiple processing/selection branches and franchise substate inputs | Substate semantics and complete exact-decision contexts remain unqualified |
| 0x12b4120 in030 | Clears other active unarchived offers for the same Player, with events/period/team branches | Competitor/side-effect processor, not a single-offer decision |
| Script query031 |46 matching strings;0 callbacks under the specific existing registration template | Negative result is limited to that template; it does not prove absence of an API |
| Caller/body sources032/033 | Cancel helper also appears inside automatic pool/team/period routines | Do not expose those parent routines; only the small guarded Type2 service subset is implemented |

Final signing, deferred confirmation, individual option decisions, other statuses/types, replacement semantics, full current-scene/save integration, UI and persistence remain work. Other M0–M5 requirements continue.

## Offline reproduction

```powershell
python -X utf8 -B tools/recover_pending_offer_withdrawal.py --out <new-evidence.json>
python -X utf8 -B -m unittest discover -s tests -p test_offer_withdrawal.py -v
```

Ten focused tests execute the shipped handler in a fake address space with no writable backend API. The simulated original service supplies the only mutation. Tests compare independent raw bytes; cover all-field expectation/ranges, duplicate/stale identity, scene/roots/Player/Team/pool changes, wrong returns/records/status and extra effects, immutable original183 plus one supplement, GM permissions, conflicts and no replay. No game code executes.
