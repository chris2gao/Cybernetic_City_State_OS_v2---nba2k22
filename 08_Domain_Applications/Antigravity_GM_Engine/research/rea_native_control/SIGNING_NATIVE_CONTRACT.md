# Signing terms and team-offer observation — checkpoint010

Static/offline engineering against PC22 build SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`. No new process attachment, capture, business call, write, UI or persistence evidence. `SIGN_FREE_AGENT` remains unavailable. Full M0–M5 remains active.

## Registered fields and enum meanings

`data/signing_schema.json` joins all25 registered FRANCHISE_SIGNING fields to five Native enum descriptors and27 values. Complete33-byte four-LEA registration tail thunks have static entry-pointer corroboration. Type CRC, row count, unique literal-bank name CRC and value agree. BSS descriptors have no file-backed contents: recovery reads their registration inputs. Evidence is local pinned PE/Capstone, not REA Provider output.

| Field | Recovered internal values |
|---|---|
| Status | 0 EMPTY,1 OFFERED,2 RFA_QUALIFIED,3 WAITING,4 REJECTED_WAIT,5 REJECTED,6 ACCEPTED,7 TEAM_DECLINED,8 SIGNED,9 BANNED |
| Type | 0 DRAFT_PICK,1 EXTENSION,2 FREE_AGENT,3 QUALIFYING_OFFER |
| ContractType | 0 NORMAL,1 TEN_DAY,2 HARDSHIP,3 TWO_WAY |
| Distribution | 0 CUSTOM,1 ASCEND_BIRD,2 ASCEND,3 FLAT,4 DESCEND |
| OptionType | 0 NO_OPTION,1 TEAM_OPTION,2 PLAYER_OPTION,3 TEAM_OPTION_2 |

Internal names do not certify current UI labels/availability. TEAM_OPTION_2 retains its name without an invented option-year interpretation. Unknown stored enum encodings retain raw values and null names.

The44-byte record has Player/Team UIDs at0/2, Wage at4, six ForcedWage uint32 slots at8..31, packed negotiation/clauses/status/type/distribution/options at32, four interest bytes at36..39, and city/years/archive/user flags at40. The registered static array info begins with6, agreeing with the24-byte extent. PissedOffLevel uses signed8-bit interpretation corroborated by the original signed load. RecentOffer is bit13 of the32 word; IsExistingOffer is bit15. Unregistered upper bits at40 are not emitted as a raw field.

## Explicit private encoding and M0 cards

`signing_fields.encode_explicit_contract(player_id, team_id, contract)` accepts exactly:

```json
{"signing_type":"FREE_AGENT","annual_wages_native":[101,202,303,404,0,0],"years_native":4,"option_type":"PLAYER_OPTION","contract_type":"NORMAL","distribution":"CUSTOM","no_trade_clause":false}
```

Numbers are synthetic encoding examples, not recommended/game-legal terms. All six wage slots are caller supplied; slot0 enters Wage and all six enter ForcedWage. There is no pricing, salary matching, term selection, GenerateContract call or unit conversion. UIDs exclude65535, wages fit uint32, years fit0..7. Encoding bounds do not certify eligibility, legal duration, currency, option effects or acceptance.

The codec returns inert private bytes with EMPTY status and execution/negotiation flags clear. **It is not a fresh Native offer constructor and must not be dispatched as one.** Original GenerateContract starts ordinary records at OFFERED (RFA_QUALIFIED for Type3), sets negotiation state and may derive/clamp wages, years, distribution and options. These semantics remain unqualified for an exact caller-decided offer.

Role `get_allowed_values` now exposes the explicit input schema, enum meanings and unavailable lifecycle/dispatch status for mapped signing requirements. SIGN_FREE_AGENT permits FREE_AGENT in its schema; the standalone codec supports other known types for offline analysis. Enum knowledge grants no role permission. The facade still returns UNKNOWN_BINDING for signing and cannot render a signer.

## Read-only team-offer query

`NativeReadFacade.read(NativeReadQuery('signing.team_offers', parameters))` prepares READ_TEAM_SIGNING_OFFERS:

```json
{"team_id":20,"statuses":["OFFERED","ACCEPTED","SIGNED"],"include_archived":0}
```

An explicit nonempty unique status list is required. EMPTY is excluded; UNRECOGNIZED explicitly selects raw10..15. Archive inclusion is integer0/1. No implicit-all query. Preparation is inert without a supplied authorized transport.

Original lookup/allocator bodies prove the franchise root global0x632b478, inline pool+0x1727a8,1000 records and44-byte stride. The reader pins their complete code extents but invokes neither helper. It verifies the requested Team against the existing directory, scans the bounded pool twice and requires full selected-record bytes and selected-set membership to agree. Entering/leaving rows, selected changes, root changes and team changes prevent a snapshot. Changes wholly outside the selected set do not invalidate selected rows.

Output contains the query, selected registered fields and enum pairs. record_index is transient, not durable identity. Player UID65535 is unresolved/null in the identity wrapper, with its registered raw value retained. No Player resolver or current global PLAYER relationship is certified. **Zero Native business calls**, no setter, pointer output or arbitrary44-byte dump.

Matching brackets do not prove atomicity or exclude ABA. Host-authorized world/save/generation/season/phase, observation provenance and a sanitized role provider remain required. No signing-specific snapshot provider or Native save detection is claimed. Production capture/database/history pipelines are unchanged.

## Lifecycle evidence and remaining execution gap

- Lookup0x12ba5a0 skips EMPTY, archived and QUALIFYING_OFFER, then matches Player/optional Team. The reader deliberately permits explicitly requested archival/qualifying observations.
- Allocator0x12b6520 resets game-owned EMPTY records and may reclaim REJECTED records subject to a team predicate. It preserves unregistered upper bits at40. It is not private allocation.
- Acquire/reset0x12b38b0 can reset live offers. Its argument4==0/stack argument5!=0 path calls Player salary Setter0x998820; later code changes Player flags. It remains noncallable. The full UI caller also changes Player/team state and is not inert preparation.
- GenerateContract0x12b7290 initializes the supplied object, derives/clamps prices/terms, copies special contracts and applies option/distribution heuristics. Whole-function reuse would violate exact caller-decided terms. It is not exposed as a preparation shortcut.
- OfferContract0x12bd4c0 validates, finds/allocates a pool record, copies44 input bytes when pointers differ and conditionally calls Process. Observed variants use different contexts/origin/mode flags. Return1 is not completed signing; mode1 can return without Process. The0x16 mode label remains UNKNOWN.
- Process0x12bde70 has broad Player/team/contract effects and assertion paths. Five observed argument origins do not establish a return/completion contract. Newly recovered0x12d4530 itself changes Player/team/history state; it is a transition lead, not a wage decoder or safe helper.

Next: qualify exact explicit-term fresh construction and mode/origin/context; close option/distribution consumers and deferred completion; resolve current free-agent/global Player identity; implement original submission with independent roster/contract readback. Do not patch pool status, invoke side-effectful acquire/reset or generated pricing, or replace business calls with raw field writes. Live tests require concentrated Human-approved scenarios.

## Reproduction

From this control directory, with the pinned local EXE available, select new output paths:

```powershell
python -X utf8 -B tools/recover_enum_registration.py --entry 0xe5b70 0xe5ba0 0xe5bd0 0xe66a0 0x9a110 --out <new-enum-evidence.json>
python -X utf8 -B tools/recover_signing_schema.py --out <new-schema-evidence.json>
python -X utf8 -B -m unittest discover -s tests -p test_signing_contract.py -v
```

Field source: evidence/static/types-signing-02.json. Run static sources: sign_pool_lookup_and_allocate_003.json, sign_native_enums_007.json, sign_validation_and_offer_state_helpers_008.json, sign_input_construction_callers_009.json, sign_terms_and_salary_helpers_010.json and sign_team_player_transition_helper_011.json. Earlier bounded leads retain their limits. Nine focused tests run actual compiler/handler against synthetic memory, compare independently packed bytes and join enums to registered types. They do not execute the game binary or prove a real signing.
