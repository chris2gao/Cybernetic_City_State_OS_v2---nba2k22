# Exact free-agent offer submission — checkpoint012

This is static/offline implementation against PC22 executable SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. New live calls, game effects, UI, save persistence and independent acceptance are **NOT_RUN**. The complete M0–M5 objective remains active. Source is pinned local PE/Capstone, explicitly **NOT_REA_PROVIDER**.

## Business boundary and role inputs

`GM.CONTRACT.CONTRACT_OFFER` now maps to `CONTRACT_SUBMIT_FREE_AGENT_OFFER`. It implements the existing distinct demand to submit a specified offer; `GM.CONTRACT.FA_SIGN` / `SIGN_FREE_AGENT` and `CONTRACT_OPTION_ACTION` remain unavailable. There is no claim of completed signing or accepted terms.

The host supplies a GM identity, owned Team UID, explicit permission and phase grant, exact current-save context, and phase `FA_SIGNING_OFFERS`. The Native parent period must independently equal22 `FA_SIGNING`. The offer-versus-confirmation substate and save/world identity remain host attestations; they have not been recovered as Native facts. A caller-supplied Boolean is insufficient for batch authorization. Live use requires Human-approved scenarios and current-state integration.

```python
intent = ActionIntent.decided('offer-unique', 'gm20', 'GM.CONTRACT.CONTRACT_OFFER', {
    'team_id': 20, 'player_id': 55,
    'contract': {'signing_type': 'FREE_AGENT', 'annual_wages_native': [101,202,303,404,0,0],
                 'years_native': 4, 'option_type': 'PLAYER_OPTION', 'contract_type': 'NORMAL',
                 'distribution': 'CUSTOM', 'no_trade_clause': False}})
```

These are synthetic encoding values, not a suggested price or certified legal offer. The caller chooses every term. Use the host `submit_decided_actions` entry with trusted profiles, grants, context guard and an independent readback provider. The technical facade also has `submit_contract_offer`; preparation without a supplied transport is inert and the facade alone does not confer role authorization.

| Parameter | Supported values and actual meaning |
|---|---|
| Team / Player | Exact Native UID integers0..65534; no substitute target |
| signing_type | `FREE_AGENT` only; original default-type predicate must return2 |
| contract_type | `NORMAL`0 or `HARDSHIP`2; original validation still decides eligibility |
| distribution | `CUSTOM`0 only; no wage calculator |
| annual_wages_native | Exactly6 explicit slots; active years are positive integers at most2147483647; unused slots exactly0 |
| years_native | Total1..6 years including the selected option years; no clamping |
| option_type | `NO_OPTION`0/0 years, `TEAM_OPTION`1/1 year, `PLAYER_OPTION`2/1 year, `TEAM_OPTION_2`3/2 years |
| no_trade_clause | Explicit Boolean; original experience/eligibility validation retained |

No extension, ten-day/two-way, other distributions, other periods, existing-offer replacement, final confirmation, offer withdrawal, forced acceptance, or automatic term generation is qualified by this action. UInt32 proposal storage is wider than the original Player salary consumer's31-bit value; out-of-range offers are rejected before dispatch. These are encoding/consumer guards, not a replacement CBA or negotiation policy.

## Primary Native evidence

The canonical packed source is Run `static/sign_fa_offer_runtime_contract_027.json`; sources022..026 retain bounded code, root and pool derivations. `tools/recover_fa_offer_contract.py` replays the selected evidence against the pinned EXE.

`0xedf010` is a current-period Getter. Complete Setter `0xee0180` stores previous/current values at period-root+0x10/+0xc. Its indexed debug CRC table at0x2a46620 uniquely matches31 names in a selected1024-byte literal bank, including20 `CONTRACT_OPTIONS`,22 `FA_SIGNING`,29 `REGULARSEASON`. This supersedes checkpoint010/011's explicit UNKNOWN for the old “0x16 mode” and `0xee0180` meaning. It proves a period marker, not calendar advancement or persistence.

| Native root global RVA | Source / use |
|---|---|
| 0x632b470 | Current-period Getter; require root+0xc ==22 |
| 0x632b478 | Signing pool root;1000 records at+0x1727a8,44 bytes each |
| 0x632b498 | Rules root; require +0x208 ==1; do not read this gate from the pool root |
| 0x632b468 | Tuning root; pin the observed response desirability bounds |
| 0x6327f58 | Delegate root; require an inherited exact static vtable and used slot targets |

These roots come from exact RIP-relative MOV operands. Their numeric rule value and static delegate profiles are not proof of a MyGM/MyLEAGUE class label, current live readiness or save identity. Code/table/literal signatures are checked by the shared compiler runtime; full-process attachment is not part of recovery.

The original FA caller `0x12bda50` enumerates `0x9b5bf0` / `0x9b5bb0`. The count getter and `0xf3cf10(0)` resolve a bounded original available pool:1000 pointer slots and u16 count at+0x1f40, total0x1f48 bytes. The handler requires a positive original count, exact pool count agreement, and exactly one occurrence of the explicitly requested Player pointer. It also requires zero5-bit base-contract years and zero3-bit extension years. Original `0x12b7d60(Player*,Team*)` must return2 FREE_AGENT. These checks qualify the original pool membership; no complete live FA universe or independent eligibility certification is asserted.

## Private construction and original service

The original generator `0x12b7290` clears registered POD fields while preserving word40 upper19 bits, initializes ordinary offers at Status1 OFFERED, and finishes with NegLevel3 and cleared counteroffer/interest flags. Its whole body also generates and changes business terms and is never called by this backend.

`encode_fresh_fa_offer` models the qualified initialization on private44-byte bytes, using an observed first EMPTY template solely for preserved unregistered bits. The JS handler independently constructs the same bytes in private `Memory.alloc(44)`. It sets exact UID/wage/years/options/clause inputs, Status1, NegLevel3, Type2 and CUSTOM0, with force/verbal/existing/user flags0. The older `encode_explicit_contract` remains an inert EMPTY-status analysis codec. No live record is reset, allocated or written by the new backend.

The only new business service invocation is `0x12bd4c0(private_record, null, 0, 0)` once, reproducing fixed arguments at original caller `0x12bdccf`. This subset has its own binding `sign.offer_fa_phase`; the generic `sign.offer_contract` retains its unknowns. Fixed flags are justified by that caller, without a general interpretation of all flag combinations.

Original OfferContract performs validation, lookup/allocation, record copy and negotiation/response work. Under Native period22 it follows pending/rejected branches. It can affect quotas, responses and negotiation state. There is no direct Process invocation, stage advance, game-memory field patch, forced accepted/signed status or automatic retry in the new backend. Original service effects are intentional; the private constructor is not a claim that submission is side-effect free.

Before dispatch, the entire offer pool is read twice, existing lookup-eligible Player/Team offers are rejected, an EMPTY slot is required, and Player bytes, available directory, roots, Team resolution, delegate slots and selected tuning are bracketed. The backend declines to reclaim rejected records or replace prior offers. After the call it checks Player identity/team links, all17 selected physical contract fields, available-directory stability, exact supplied terms in both private and newly created records, and context again. Matching brackets do not prove atomicity or exclude ABA.

Maximum direct Native calls: **7** — count, available pool0, Player UID, default type, one OfferContract, Player UID again, available pool0 again. No game target or business value is chosen by the backend.

## Return and unresolved effects

- Return1 plus exactly one matching newly occupied Status1 OFFERED record produces `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`, `submission_only:true`, `signing_completed:false`.
- Return0 permits no new record or one matching Status4 REJECTED_WAIT record and produces `REJECTED_BY_GAME`. Original rejection-side response/quota effects may still exist.
- Other returns, unexpected ACCEPTED/SIGNED status, changed terms, duplicate created records or changed context/selected physical contract state produce an unknown outcome. The handler performs no rollback or second call.

These are same-handler observations. A separately supplied host observer must bind evidence to the exact context/intent before the batch can record `APPLIED_READBACK_CONFIRMED`. That label confirms this requested offer submission only. It does not mean accepted offer, signed Player, persistent save or full signing capability. Without independent confirmation, the journal retains the broad Player resource reservation across new request IDs and stops dependent mutations. Competing GMs' offers for one Player require role resolution; the aggregator does not pick a winner or change prices.

Remaining M2 work includes deferred offer response/confirmation and final signing, extensions and individual option decisions, other contract types/distributions, staff transactions, complete current-scene/save binding, and independent roster/contract/persistence observations. Other M0–M5 obligations remain in the full183-item coverage export.

## Offline reproduction

```powershell
python -X utf8 -B tools/recover_fa_offer_contract.py --out <new-evidence.json>
python -X utf8 -B -m unittest discover -s tests -p test_fa_offer.py -v
```

The fake address-space harness runs the shipped JS handler, checks exact fixed ABI arguments and seven-call budget, permits backend writes only to private allocation, and models service responses as synthetic mutations. An independently packed byte fixture checks the constructor. Negative cases cover unsupported/implicit terms, phase/rules/delegate/tuning, available-player identity, existing years/offers, pool exhaustion/concurrent changes, Native rejection, changed terms/status/contracts/roots and no replay. The harness never launches or calls the game binary.
