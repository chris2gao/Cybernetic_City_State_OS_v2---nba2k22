# Native calendar simulation dossier

Evidence grade: `PE_STATIC_CANDIDATE`. Registry capability: `SIM_CALL_UNVERIFIED`, default `DISABLED`. The on-disk Win64 PE SHA256 is `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, identical to the existing NBA REA Profile's build. REA admitted the PE. Its Ghidra whole-image string query returned provider_timeout at 330000 ms. The narrower PE-section and Capstone unwind-range passes supplied the results below. No runtime attachment or game action was performed.

## Recovered static path

| Static anchor | Observed behavior |
|---|---|
| `0xbd956e`–`0xbd957f` | The generated MyGM callable registration passes the pointer `0x8258e0` alongside the literal `void MyGmMenu_Overlay_Simulation_Update()` at `0x2952f50`. It is a simulation overlay update callback. The exact button/confirmation-to-overlay transition is still unknown. |
| `0x8258e0` → `0x825918` | Checks a global condition and an object predicate. One path tail-jumps to `0x7ed990` after comparing a predicate result with 2. Other paths return or tail-jump to `0x23c0a0`. This dispatch predicate's enum is unknown. |
| `0x7ed990` | Reads a mode/state through a virtual call, clears another value through a virtual call, branches, fetches/validates dates and prepares the call context. The path near `0x7eda90` calls `0x1fbcd0`, adds one to its EAX, then calls `0x26f370` before using its result as ECX. Call sites `0x7edb2c` and `0x7edbf5` both invoke the same wrapper with different date-source paths. This is why the civil target cannot simply be packed and passed through. |
| `0x11be250` | Forwards register and stack arguments to `0x11be290`, preserves the EAX result across a global-object vtable `+0x520` call, then returns it. This wrapper is the stronger later-call candidate than bypassing wrapper cleanup. |
| `0x11be290` | References `GameMode_SimulateToDate_Internal` at `0x11be2f4` and `GameMode_DoPreSimulationChecks` at `0x11be57f`, in `gamemode_game.vcc`. Reads current global date, walks precheck callbacks, calls `0xed8cb0` on one date/context branch, and compares the current and target values again at `0x11be63f`–`0x11be64d` with a loop-back path. Success/early exits can return EAX=1, so EAX alone has insufficient meaning. |

The wrapper and backend RVA-range SHA256s are `0dc7c3ce6eb4f394701405d48510f5d4605627cc9f8c0f21cc3c969c52da16d7` and `3da6f3df5779fa6c4b8d62a37db36b11d5775a207d3a419a747a5242cde5cc35`. The `0x7ed990` range hash is `84910c0b9c5cd8f712fc9346b4df85f994403c2f7ed2e41241e842d9b5f499e5`.

### ABI and unknowns

Observed Windows x64 candidate shape: EAX 32-bit status, ECX 32-bit native date candidate, RDX context pointer (from `0xbaa7e0` at these call sites; later consumed through `[r14+0x2e8]`), R8D and R9D 32-bit flags/selectors, plus 32-bit inputs at caller `[rsp+0x20/0x28/0x30]`. At the two overlay call sites observed values include `R8D=1,R9D=1,stack5=1,stack6=0x64af641e` and a branch-specific seventh word (`0x62` or `0x56`). Their types/purpose and valid combinations are unverified. The context is engine-supplied and global state is dereferenced. Ownership, lifetime, scene transitions and reentry restrictions are unknown. This is an observed register contract, with no ready-to-call prototype.

Existing Calendar Reader decodes four-byte SCHEDULEDATE as ID, minutes, day, month and base-year offset from 2000. The candidate overlay conversion has more steps, including a possible next-day boundary. Endpoint inclusivity and the UI selection → raw argument correspondence must be captured for the exact MyLEAGUE calendar option. The registered overlay callback identifies the game dispatch path, but thread ID, thread affinity, worker ownership and safe external dispatch remain unknown. The historical GUI-thread REA setter does not prove sim affinity or authorize use here.

Native completion events are still unverified. `0x11be531`/`0x11be66f` route the same token `0x4a633316` through `0x11be710` with different line-like values. Treat these as hypotheses for observation, not completion callbacks. Completion admission requires correct idle scene/date, all preregistered games final and natively simulated, and complete same-capture-unit WorldData/Box verification. Track any save/dialog/postponement or unexpected advancement independently.

### Negative discrimination and existing interfaces

- `0x1224b60` references `CAREERMODE_SEASON_SIM_SERVICE::SimToDate`; `0x5f98c2` references the MyCAREER debug path. The online-server `MyLeagueOnlineServer_SimulateThroughEventOnDate` literal at `0x2c44de8` is another distinct route.
- `0x809530` references `MYGM_SIMCAST_MENU::SimCast_AdvanceToNext` and also reaches the wrapper. A generic wrapper xref is insufficient to assign MyLEAGUE Calendar UI semantics. Date getters, raw date writes, game-status edits and manufactured Box outputs are outside the candidate.
- Reuse the existing `calendar_native_profile.json` and `calendar_codec.py` for readback, `calendar_sim_orchestrator.py::inspect_calendar_progress` and SQL integrity checks for capture, and `season_cycle_host.py::advance_calendar_check` for postcondition checks. `ACTION_SURFACE.md` and the existing Native bindings establish the previously available action surface. No sim RVA has been added to a live binding table.

Reproduce with `python -B pe_calendar_strings.py <PE>` and `python -B pe_calendar_xrefs.py <PE> 0x2b537d8 0x11be290 0x11be250 0x7ed990 0x8258e0`. Add `--dump --around` with `0xbd956e 0x7edb2c 0x7edbf5 0x11be536 0x11be674` to replay bounded instructions. The xref scan covers direct RIP-relative and rel32 references within PE unwind ranges, with no completeness claim for indirect or leaf edges.
