# T15 / GE-01 — Human-paused execution-quality failure record (2026-11-16)

**Decision authority:** Human (new conversation decision).  
**State:** `PAUSED_BY_HUMAN / INCOMPLETE / NOT_ACCEPTED`; not `DONE`, `PASS`, `CLOSED_AS_COMPLETED`, or a terminal verdict on all possible coding tasks.  
**Scope:** **Codex-run T15/GE-01 monitored NBA2K22 research comparison**, not the whole NBA2K22 project. No fresh Codex execution, game operation, tests, Calendar change, Core development, merge or Native authorization is requested.
**Next executor:** Human intends to evaluate Claude; **not yet commissioned, approved, or compared in this record**. A later continuation requires a new explicit Human instruction. No automatic hand-off or unattended resume.

## Pinned provenance

- NBA main research Issue [#40](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40) remains **OPEN**; this pause does not mark its research goals complete.
- GE-01 / T15 pilot Issue [#46](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/46), to be closed for **not planned / paused**, not completed.
- T15 original scope contract: [TASK_CONTRACT.md](TASK_CONTRACT.md), original task branch commit `1bd39f3cb7bb5d55412bfcefde741f5c0bb612df`. This is preserved as a historical document; it **does not** override the current Human stop.
- NBA master observed `c345268d1a72a61a2d2aa9218b0c9a944548d218`; Core master `5806c381c599e817106cbdb7c6352f6156b8cdcc` at T15 planning time. Core PRs #23/#34/#35 are merged, but integration is **not** proof of behavioral adoption.
- Calendar false blocker evidence: [Issue #46 correction](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/46#issuecomment-6924134867), PR #42 `simulate_to_native_date.js` `verifyWindow(after)` lines 72–82 and older offline `sim_control.py`. The all-Pending gate is a **wrapper assumption**, not an established NBA Native engine requirement.

## Human observations and executor self-report

**These are Human-observed / Codex-reported claims, not an independently recovered complete T15 event log.** Do not invent exact counts, timestamps, native GameIDs or verified new study outcomes.

1. **Time-to-value failure:** At a Human observation at least **20 minutes** after T15 launch, Codex had not yet entered actual Calendar simulation. Later the Human observed a long path of foreground-window control, preflight checks and one-off script creation before a Calendar simulation was eventually completed. Exact first-dispatch and end-to-end durations **NOT independently verified here**.
2. **Dynamic implementation of operational plan:** Codex explicitly reported: the task contract fixed the *business flow* in advance, but it **did not determine all calls, checks or scripts before starting**; it inspected interfaces and incrementally supplemented scripts during the run. This establishes incomplete prebound execution planning, not that every individual later action was unnecessary.
3. **Spurious Calendar gate:** On 2021-11-15 the observed schedule contained **four already Final and seven Pending**. The test wrapper rejected mixed-state days as if all games must be Pending before simulation. That prevented the planned study path even though a mixed schedule is not itself a proven domain hazard. A legitimate implementation must preserve already-Final outcomes and only count newly completed games, retaining exact same-source and no-replay protections.
4. **Mistaken planning prohibition:** GPT-authored T15 contract G1 and hard prohibition incorrectly told Codex to stop and not fix the Calendar gate. This promoted a provisional implementation limit to Human-level task authority. **GPT planning bears direct responsibility** for that constraint. Earlier 'do not repair Calendar' applied to the preceding read-only GE-01 fact audit and should not have been carried forward as an indefinite research stop.
5. **Failed Human escalation:** On a local tool constraint that blocked an unfinished Goal, the assistant/executor path did not promptly return an explicit `INCOMPLETE` reason and a narrow choice to the Human. `STOP_ACTION != STOP_GOAL`; safety stop must not be silently treated as a decision to abandon research.
6. **Reuse and granularity failure:** A formerly exercised Native Calendar action appears to have required numerous model-controlled foreground, tool-discovery, runtime-script and repeated-check steps. A full primary trace is needed to distinguish (a) required built-in verification, (b) genuinely new mixed-day defect work, (c) redundant reimplementation and (d) unnecessary checks. The observed multiplicity is a serious usability / engineering-cost concern, but **exact 'overhead %' or redundant-call count is not established**.
7. **Governance insufficiency:** PR23 `Atom/Chain/Executor` and PR35 `next_business_action` cannot enforce an immutable action path unless the actual caller uses them. PR23's action order and PR35's graph-aware selector can differ; neither alone validates that newly invented preconditions are legitimate. No evidence in this record that production Codex behavior was actually under an external deterministic controller.

## Accountability and acceptance result

| Axis | T15 finding | Evidence grade |
| --- | --- | --- |
| Goal understood | NBA scientific goal is modify approved attributes → simulate actual games → recollect WorldData → compare effects | Human objective / written T15 contract |
| Predictable execution and reuse | **FAIL for claimed autonomous commercial-grade task execution in this pilot**: action-path completion was not fixed/controlled in advance and substantial improvised work was observed | Codex admission + Human observation |
| Calendar safety policy | **UNJUSTIFIED BLOCKER**: all-Pending is not a demonstrated Native engine requirement | Source inspection; mixed-day Native behavior still needs controlled verification |
| Planner quality | **FAIL**: GPT T15 contract propagated an invalid stop condition and prohibited local remedy | Frozen contract and source inspection |
| Outcome validity | **UNVERIFIED / NOT ACCEPTED**: Human says a calendar simulation eventually happened; no new authoritative T15 end-to-end GameID/Getter/WorldData/effect receipt has been reviewed here | No full raw T15 trace or domain readback available in current planning chat |
| Time/efficiency comparison | **INCOMPLETE**: >=20-min delayed first Calendar attempt at Human checkpoint, exact new-arm T1/T2/T3 unavailable | Human observation, no final monitored summary supplied |
| Project-wide judgment | Do **not** extrapolate this failure to a formal proof that all models or all Codex coding tasks are incapable. Human judges Codex unfit for this autonomous commercial-project role for now. | Human decision, role-specific |

**Critical separation:** Engineering code/tests/PR count is not equivalent to business Done. A later completed simulation does not retroactively certify the T15 autonomous execution workflow. The historical PR #41 report of 520 simulated games is from a different context, not T15 acceptance.

## Human pause instruction, immediate effect

- **Do not continue T15/GE-01 with Codex.** No added debug, runtime probing, script generation, Calendar/REA/Native Setter action, in-game changes, read-only recapture, save restore, merge, or new validation loop on this pilot.
- This is an **administrative GitHub pause**. It does **not** remotely terminate a currently running Codex process or monitor; if any exist, Human must stop/disconnect them in their execution environment. Do not claim remote processes were killed.
- Freeze existing local raw Codex event logs, runtime receipts, save/WorldData/Outbox snapshots and historical Git objects in place. **Do not upload private raw logs, save files, SQLite or Frida payloads.** Preserve unresolved Native UNKNOWN resource locks for explicit later reconciliation; closing a GitHub Issue is not an Outbox release.
- Do **not** merge draft NBA #41/#42/#43 merely to 'close out' this failure. Do not change Core master or NBA master.
- Keep Issue #40 open as historical research parent; future Claude assessment should independently demonstrate a useful, bounded, reproducible action path and real game research, under separately scoped Human operational authority.
- A resumption decision must come from Human. `PAUSED_BY_HUMAN` is a project-state record, not a promise of further automatic background work.

## Minimal future evaluation criterion (not an active assignment)

Human may choose to assess Claude for this role. The meaningful comparison is: Can it reuse a pre-existing callable Calendar action without reauthoring scripts or inventing stops, ask Human promptly for a truly novel decision, complete one authorized Setter→Calendar→WorldData→analysis loop, and provide reliable receipts with acceptable preparation cost? Treat it as a new, explicitly authorized evaluation, **not** as an automatically activated T15 replacement.

**Record author:** GPT planning/review assistant, documenting the Human's pause decision and distinguishing sourced facts, executive self-report and unverified details. Original scope remains preserved in Git.
