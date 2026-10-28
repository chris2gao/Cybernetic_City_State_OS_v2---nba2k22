# Checkpoint010: signing terms, internal status and filtered offer observations

Full task NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01 remains active across M0–M5. PR18 latest remote HEAD was rechecked as094f1aa641f93dec2277707ad9dbf5bdb0341247, unchanged from the engineering baseline. Remote master remains7742568ac677b3c16079887463f05e81cb1191ed. Engineering branch and Draft PR19 remain separate. No game attachment, capture or state change occurred.

## Concrete progress

Continued M2 original signing recovery instead of replaying existing trades/Coach successes. Complete enum registration thunks, literal CRCs and descriptor types restore27 values across signing status/type/contract-type/distribution/option. All25 registered fields and the six-slot ForcedWage array form a versioned schema. Packaged enum/schema recovery was executed against the pinned local PE; both replay outputs equal retained data exactly. The sources are local PE/Capstone, not a REA Provider result.

The original lookup/allocator fixes pool ownership and extent: game-owned1000x44 records. New signing.team_offers / READ_TEAM_SIGNING_OFFERS takes exact Team UID/status/archive selection and reads registered fields only. It uses zero Native business calls, two bounded scans, full selected-record/set/root/team stability checks and no writes. Unknown enum values remain explicit; a matching bracket is not atomicity or ABA protection, and record indexes are transient. No signing-specific role snapshot provider, current save identity, full contract ledger or production acquisition integration is claimed.

The inert explicit contract codec and M0 parameter schema require caller-decided six wages, years, option/type/distribution and no-trade clause. Encoding bounds are distinct from legal/UI terms. Codec output retains EMPTY status and cannot be dispatched as a fresh Native offer. SIGN_FREE_AGENT has no runtime handler.

New original-body findings explain the remaining gap: GenerateContract chooses/clamps terms and options; acquire/reset can call Player salary setters and alter Player flags. Whole-function reuse would modify caller-decided terms or current state. OfferContract can copy private44-byte input into the pool, but context/origin/mode and deferred completion remain unqualified. ACCEPTED6 differs from SIGNED8, and neither status alone proves independent roster/contract effects. A newly recovered Process subhelper changes Player/team/history and is retained as a transition lead, not a safe wage decoder. Original bodies are preserved, including NO_UNWIND for the selected salary Setter; no guessed extent or return type was promoted.

## Verification and index

Nine focused tests pass offline: all enum/registered-field joins, independently packed field/signed/array fixtures, explicit encoding/bounds and untouched status/flags, exact queries, selected-team/archive/unknown values, entering/leaving/changed rows, context failure, no game calls/byte mutation and unavailable signer/role cards. Synthetic memory runs the shipped read handler; it does not execute the game binary.

The complete fixed-candidate Managed Run/Inspect is pending execution and receipt retention. Source/index verification covers the unchanged183 requirements plus14 technical datasets, retained static hashes, schema/runtime binding agreement, unavailable signing and the seven affected module links. Current counts:69 actions,56 bindings/layouts,59 effective requirement mappings,14 read datasets. Counts are not acceptance or M0–M5 completion.

Production capture, SQLite/history/publishing, master and PR18 are unchanged. Updated P03/P04/P05/P08/P09/P10/P12 link to SIGNING_NATIVE_CONTRACT.md, exact codec/runtime/data and remaining gaps. Full remaining work includes fresh explicit-term signing construction/submission/readback and other GM transactions/staff, complete Coach/Book/Freelance/rotation/training, remaining Player/global/body/development/child objects, role data/current-save/independent observers, concentrated Human-approved live scenarios, independent review and final M5 audit.
