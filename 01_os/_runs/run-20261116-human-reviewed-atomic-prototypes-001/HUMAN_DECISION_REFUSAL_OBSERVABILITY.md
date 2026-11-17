# Human supplemental decision — refusal receipts and model–OS execution fit

**Human local date:** 2026-11-17 (America/Los_Angeles)  
**Core task:** OS-CORE-HUMAN-REVIEWED-ATOMIC-PROTOTYPES-SYSTEM-UPGRADE-20261116-001  
**Human instruction:** “约束呗，这个确实需要，而且要做记录，如果拒绝的次数过高，那说明模型与我们的os系统冲突。”

## Approved intention

- Host-enforced restrictions on unapproved execution operations are necessary, not merely prompt suggestions.
- A denied Host gateway request should leave a persistent, structured fact; a consistently high refusal count/rate is important evidence of possible **model behavior vs. OS execution contract friction**.
- The analysis must remain actionable for Human: identify which task/prototype/operation was refused, why, how often, and whether the model repeated a violation.
- Do not create a separate approval system, per-internal-check logs or an automated model ban.

## Engineering interpretation without invented Human thresholds

- Categorize `MODEL_POLICY` (attempts contrary to approved mode and registered tools), `HUMAN_PENDING` (review/authority not yet supplied), `SYSTEM_GAP` (missing approved capability), and `HOST_STATE` (revoked or changed mode/scope). All are recorded refusals but only the first is a direct candidate model-policy conflict signal. Repeated other categories can still justify Human investigation into instructions/Host integration.
- Compute both raw refused count and refusal rate over comparable observed Host gateway requests, grouped by model, task and operation route; dedupe event IDs. A tiny sample is not enough to assess a model.
- The `execution_decision_audit.summarize` thresholds (10 attempts, 30% model-policy refusal rate, or 3 repeated same-policy denials) are **software examples only**. The Human did **not** choose numeric production limits. `REVIEW_MODEL_OS_FIT` is an advisory diagnosis, never self-executing authorization/action.
- Only Host-mediation events enter this denominator. Current unmediated Claude/Codex Shell/GUI activity is not visible; no live model evaluation is claimed.

## Implemented candidate in Core PR #37

- `execution_mode_gateway.py` attaches Host audit events to compiled prototype admission, real bound callable invocation, and development tool admission/refusal.
- `execution_decision_audit.py` defines redacted immutable receipts, model/task/route-filtered read-only summary, `append_jsonl_sink` (Host-owned path, fsynced append) and `load_jsonl` for cross-session review.
- No actual raw prompt, sensitive CLI args, full file content or game save payload is logged. Host can persist records using existing run/PRMS storage; a missing required Host sink must not allow an operation silently.
- Genuine `Ready=false` is not counted as a refusal; an action admitted before a later Host mode change is not retroactively marked denied; later attempted action after revoke is refused.
- **Windows isolated test evidence:** at fixed source commit `333dcb28475032c403c5ea43587e25adbda8a35a`, `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1` → **154 passed, 8 subtests passed**, exit code 0. This verifies offline reference behavior, not real Host deployment.

## Explicit remaining boundary

The opt-in callable gateway still cannot prevent or observe external model tools not routed to it. Formal usage requires a trusted model identity, current task scope, actual Host tool-routing allowlist, and Host-owned writable audit directory inaccessible to the executing Agent. No new native/game actions or protected master publishing were authorized by this decision.
