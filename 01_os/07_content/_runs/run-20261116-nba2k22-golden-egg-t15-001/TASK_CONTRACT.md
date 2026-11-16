# NBA2K22 · T15 金蛋执行链真实业务效率对照任务（最小闭环）

**Task ID:** `NBA2K22-GOLDEN-EGG-T15-ONE-WINDOW-LIVE-COMPARISON-20261116-001`  
**Role:** `execution / Codex`; **reviews:** Human final decision + GPT evidence review, no extra independent model.  
**Status:** `READY_FOR_FRESH_READ_ONLY_PRECHECK`; **not** Native Setter / Calendar / save restore permission. This document is an execution contract and evidence index; it is **not** an actual game run receipt, launch action, Stage07 formal completion, or permission token.

## 0. Source identity / reuse first (do not re-research all branches)

- Core master: `5806c381c599e817106cbdb7c6352f6156b8cdcc`; PR #23 already merged `193d1e5cb7dca346f62f2d4e6010ce6067f4a50d`; PR #34 merged `4a48bce5680d3a92663c9876b1e1c92e4db54b3c`; PR #35 merged `91a55b102787b5f7ca714f8e0dcab1f5870d6a6a`.
- NBA master: `c345268d1a72a61a2d2aa9218b0c9a944548d218`; T15 task branch from this fixed version. Never use stale PR #41/#42/#43 as master.
- NBA Draft reference PR #41 `cdb2a3b2b9f9de79fe068b1644c6ba147d05d8e5`: finite one-window harness and historical V2 result; `.../run-20261107-nba2k22-vae-longrun-40-001/CHECKPOINT.md`.
- NBA Draft reference PR #42 `ada6f30051eb9a2f17193af6985497eeb789ea1c`: test-only calendar getter/simulation tool and Outbox protections; `.../run-20261107-nba2k22-test-only-calendar-39-001/CHECKPOINT.md`.
- NBA Draft reference PR #43 `99938b46e47c7ded9a8ba317fef6a7849342a171`: 223-factor engineering coverage, only `SHOT_TENDENCY` historically certified; no automatic acceptance of 70 missing controls; `.../run-20261108-nba2k22-full-factor-engineering-001/DEVELOPMENT_DELIVERY.md`.
- Old GE-01 monitored **comparison source**: NBA Issue #46 and *private* `C:/Users/gk/Documents/ChatGPT/nba2k22/ge46-monitored-20261116/` (`events.jsonl`, `monitor-session.json`, `WORKFLOW_BEHAVIOR_AUDIT.md`). Read-only source only, do not upload raw sessions.
- Parent scientific program: NBA Issues #39/#40; do not create a new competing research program.

### Historical observation warning — highest-priority anti-replay check

The **latest content within PR #41's CHECKPOINT.md** reports prior V2 research on `MyLEAGUE0005`: 12 cycles, 143 read-back setters, 520 completed native games, 458 accepted WorldData game records, eventual `Today=2022-04-10` and `IN_MEMORY_ONLY`, with final 15 games still pending. Its initial section also retains a much earlier `2022-01-07` context. These are **reported historical checkpoints, not proof of the currently loaded game state**. Do not reuse the dated 2021-11/2022-01 candidate plans or replay any completed GameIDs/Outbox requests. `MyLEAGUE0003` is cold backup, not an automatically usable experiment slot.

## 1. Core PR #23 / #35 compatibility decision for this task

**Static code-level finding:** co-exist without import/symbol conflict, but **do not use both as independent dispatchers of the same side-effect step.** PR23's `Executor.inspect` walks children in declared order and may stop at the first blocked node. PR35's `next_business_action` can choose a later ready independent business node or a causal predecessor, based on provided `depends_on`. Their ordering is intentionally not identical. PR23 keeps `_attempted` only in the current Python object; PR35 takes external `attempted`/`unknown_resources` facts. Neither issues permission or replaces persistent Outbox/CAS.

**T15 safe composition:** use G/R/A/D semantics for a finite task plan; use **exactly one** live next-action selection policy (PR35 explicit JSON selector), then call the **existing NBA domain Host/REA/Outbox exactly once per authorized action**. PR23 `Executor.advance/run_available` is NOT an additional live dispatcher for these same actions. PR23 reference examples can be used for read-only/offline compatibility tests. Domain reads and journal are the only source of real Done and UNKNOWN reconciliation. No new scheduler, adapter platform or implicit authority layer.

**Small offline test before any real action:** (C1) PR23 parent Done remains false with child qualification success but no games/post-capture; (C2) PR35 can choose a later independent ready business when an earlier sibling is BLOCKED; (C3) PR23 attempting the same tree would stop at that earlier sibling, so the two choices must not both be dispatched; (C4) a proposed attempted/UNKNOWN external action does not cause another Native call; (C5) a genuine fixture prerequisite blocks the business until verified. Report exact code refs, test input/exit and differences. This is a single targeted test, not a new development loop; testing a hypothetical adapter does not certify actual game safety.

## 2. Real Goal and observable Done

**Goal:** demonstrate one genuinely useful, authorized NBA2K22 research loop under the now-integrated Core goal-first Workflow, with nonintrusive Codex fact monitoring, and compare its *observable business progress and path/time evidence* with GE-01's old-Workflow monitored session.

**Real business loop:** `fresh identity/schedule → pre-capture → Human-approved native SHOT_TENDENCY intervention with Getter/CAS → authorized bounded Native Calendar sim → post-capture of same GameIDs/source units → explicit effect observation`.

**Domain Done:** at least one actual game window with true current Save/worldline/process identity, committed or explicitly reconciled Native modification, independently read-back original/target values, one or more uniquely new completed GameIDs with matching source-unit team/player Box, real post-capture and a modest descriptive H/L/C comparison or a clearly labeled inconclusive effect. **Tests, qualifier receipts, documents or game date alone do not imply Done.**

**Stop without false Done:** if current save, permission, matchability, Calendar contract, source integrity, game availability or UNKNOWN resources block this, report the **first specific real blocker**; do not repair generic infrastructure or make a substitute research claim.

## 3. G/R/A/D task steps (minimum actions, no repeated formal freeze gate)

### G0 · Once-only Core and monitor setup
- Read exact Core master `factmon.py`, `next-business-action` and PR23 reference once, plus the relevant NBA test-only entrypoints from pins.
- Run the tiny C1–C5 **offline compatibility** probe if local environment is available; do not block read-only game identity on unrelated formal review ceremony. If code/interface ambiguity cannot be resolved safely, choose a single selector and record the limit.
- Codex starts the **existing** opt-in Core `factmon.py watch` on its actual current Codex rollout JSONL **when** session path/foreground process are known; record start/stop, coverage, gaps, private logs. If unavailable, continue honestly without pretending monitoring succeeded; cannot pass full T15 time-quality comparison without coverage.

### G1 · Immediate, bounded read-only reality check
- Verify whether game is running and which actual test slot/save, worldline, build, process epoch, GameMode Today, in-memory vs disk lineage, Outbox unresolved entries, authorization already granted/expired, real Pending GameIDs and source units are current.
- **First decisive Calendar check**: on intended *current* day, determine whether all expected GameIDs are Pending/Final and whether `verifyWindow(false)` is actually compatible. GE-01 found a partial-day Calendar fixture mismatch and **did not authorize repair**. If it persists, stop affected simulation; do not bypass the guard or alter the game.
- If source cannot establish a clean disposable identity, season window or Outbox reconciliation, report just that blocker and minimum Human action. No arbitrary restoration of 0005/0003, no stale pre-capture, no blanket rerun of 223 factors.
- A one-time read-only, minimal pre-capture may run if needed to define precise live comparison; source artifact stays private, only redacted digest/row counts public.

### G2 · Exact Human authorization boundary, only if fresh G1 passes
- Prepare **one** precise operational envelope with actual disposable Save/worldline, process/build epoch, fixed UID/team/field `SHOT_TENDENCY`, fresh before/target and CAS, matched control team(s), allowed game IDs and exclusive target date, max native writes (default at most two H/L, control unchanged), max Calendar calls (default one day/window), outbox/receipt/stop conditions, expiry and Human consent reference.
- **The current instruction authorizes this task's assessment/planning and available read-only work, not unspecified native setter, calendar dispatch, save writes or restoration.** Do not fabricate a permission token. Reuse still-valid precise Human authority if it genuinely covers the exact envelope; otherwise ask for a **single scoped Human approval** and stop affected action. No piecemeal per-step requests.
- Use only previously certified `SHOT_TENDENCY`; do not activate new unqualified factors from PR #43. Plans in PR #41 are historical examples, not automatic future dose authorizations.

### G3 · Exactly one authorized live scientific window
- Once G2 is truly authorized, pre-capture fresh public sources, then Native CAS/Getter for H/L, then test-only Calendar short bounded date; never write scoreboard/calendar memory, never progress an entire season.
- Each attempted native action claims existing Outbox/Journal before dispatch; on timeout/error/unknown stop and reconcile from authoritative readback; never run the same request a second time blindly.
- Compare actual Final GameIDs and matching team/player Box from same WorldData capture unit; record excluded/incomplete results with reason. Produce minimal differences in player FGA, minutes, FGA/36 and team FGA share; explain teammate/opponent spillover and one-window low power. No fictitious causal inference.
- If game/UI prompts, process identity, focus safety, backup/reload or old partially finalized day prevents execution, stop *that* action, report. Current run never automatically saves, restores, simulates past season boundary or moves to playoffs.

### G4 · T15 old/new comparison and close-out
- Stop own fact monitor and verify exit; create private events and report, preserve actual source SHA256; put only redacted summary and paths/digests in GitHub on the task branch.
- Historical old arm: GE-01 observed 54m05s task span, 46m02s monitored ON, ~61s six-family pre-capture and **zero completed real research loops** with Calendar obstruction. Distinguish monitored ON/OFF from wall; never label all gaps model thought or waste.
- New arm: report matched scope, time to first real business action, time to first *decisive* preflight, time to first accepted game and real Done, number of source-correct completed games, CAS+Getter receipts, optional/duplicate tool actions and confirmed excess, monitoring coverage and unknown spans.
- Old and new arms may have **different calendar fixtures, save progress, authorization and game state**. Report this as a **descriptive, confounded before/after comparison**, *not* causal proof of optimization. A stronger paired clean-save A/B can be proposed separately if Human wants causal precision.
- T15 verdict may be `OBSERVED_PROGRESS_WITH_CONFOUNDERS`, `REAL_BLOCKER_PRECISELY_IDENTIFIED`, or `NOT_RUN`. SC-10 is satisfied only as a *transparent comparable observation*, not automatic causal superiority. A-v1 full closure additionally needs appropriate Human acceptance.

## 4. Hard prohibitions and narrow delivery

No new full-factor platform, no auto-merge of NBA #41/#42/#43, no broad recertification, no old Calendar repair under this task, no gameplay without explicit precise bound authority, no hidden replay, no season-long unattended simulation, no public raw Codex logs/save/SQLite/Frida payload/private consent, no PR23 live `Executor` double dispatch, no fake benchmark or comparison score.

**Expected handoff to Human/GPT:** one report, containing source SHAs; exact live identity and stop gate; tiny C1–C5 outcome; precise Human envelope if needed; either one real completed research loop or a justified real blocker; monitor evidence coverage; comparable timing facts and confounders; and an exact task-branch commit. Stop at actual boundary, do not launch another preparation loop.

**Current external reality:** Desktop Commander for this conversation is offline. No live game process, save lineage, dates, current authorization, or Outbox state has been independently observed in this planning run. They remain UNKNOWN. This contract itself creates no live authorization.
