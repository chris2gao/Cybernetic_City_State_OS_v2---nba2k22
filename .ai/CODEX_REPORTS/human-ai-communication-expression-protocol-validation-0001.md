# Human-AI Communication Protocol Validation

```yaml
task_id: human-ai-communication-expression-protocol-0001
source_head: eb46be9dadf9672091883e4e69bcaaa70b0cb163
validation_scope: consolidated_candidate_validation
result: pass
```

## Consolidated Result

All required protocol, pointer, authority, scope, Markdown, Git-diff, and added-secret checks pass. Validation was performed against the exact source baseline and the complete 10-path candidate diff.

## Quantitative Results

| Check | Result |
|---|---:|
| required durable protocol files read | 7 / 7 |
| required durable protocol files modified | 7 / 7 |
| canonical pointer definitions equal to baseline | 8 / 8 |
| dispatch recommendation fields present in canonical definition/example | 7 / 7 |
| legacy true optional-dispatch contradictions remaining | 0 |
| Human-response preflight fields present | 8 / 8 |
| onboarding communication questions directly answerable | 7 / 7 |
| source mailbox files changed | 0 / 4 |
| Plan 3 authority document changed | 0 / 1 |
| changed paths within exact task set | 10 / 10 |
| high-confidence added-secret findings | 0 |

## Pointer-Schema Regression

The following frozen key sequences remain unchanged in name and order:

```text
ChatGPT -> Codex:
signal_id, decision, task_ref, packet_ref, brief_ref, source_head, human_gate

Codex -> ChatGPT:
packet_id, status, report_ref, brief_ref, source_head, review_branch_head, human_gate
```

The comparison covered the two definitions in `.ai/PROTOCOL.md` and the six canonical YAML examples in `.ai/HANDOFF_COMMON_CONVENTIONS.md`, `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`, and `.ai/HANDOFF_INIT_PROMPT.md`. Optional `detail_ref` remains outside the required core.

## Semantic Regression Checks

- Mandatory dispatch language is present across the canonical protocol, common conventions, autonomous communication mechanism, adherence rules, initialization prompt, and Codex work mechanism.
- Targeted scans found no remaining statement that a recommendation is optional, may merely be included, or is not required when the Human is asked to start or continue backend work.
- Statements that the recommendation is not a Human Brief or machine-pointer field are retained as channel-boundary rules, not optional-dispatch exceptions.
- Material review/completion without backend dispatch requires bounded expression but not an execution recommendation.
- Parser-only acknowledgement and explicit Human pointer-only/no-extra-text output remain narrow expression exemptions.
- Strict machine-only Codex output remains pointer-only and preserves expression through `brief_ref`.
- Every chain-of-thought reference is a negative guard; no private reasoning transcript is requested or disclosed.
- Human Speaker control over objective, engine routing, protected adjudication, source/master publication, runtime, Coordinator, secrets, and destructive operations is preserved.

## Structural And Git Checks

- Markdown fence balance: pass for all 10 changed Markdown files.
- Internal canonical refs and channel paths: pass.
- Exact changed-path set and source-mailbox neutrality: pass.
- `git diff --check`: pass.
- Plan 3 unchanged from source baseline: pass.
- High-confidence scan of added diff lines only for private-key blocks, credential assignments, and token-shaped values: no finding.

## Scenario Checks

| Scenario | Expected | Result |
|---|---|---|
| backend dispatch with pointer, 7-field recommendation, and 2–5 sentence expression | pass | pass |
| backend dispatch with pointer only | fail completeness | correctly rejected by contract |
| material review without backend dispatch but with expression | pass | pass |
| strict machine pointer with `brief_ref` preserving expression | pass | pass |
| parser-only acknowledgement without material result | pass exemption | pass |
| expression claims permission to push or activate runtime | fail authority | correctly forbidden |
| Human explicitly requests pointer-only output | pass waiver | pass |
| recommendation omits any required field | fail completeness | correctly rejected by preflight |

## Residual Risk

`material` is defined by an explicit event taxonomy, but unusual mixed-recipient interfaces may still require judgment about whether the direct UI response is a strict machine channel or a Human operational channel. The protocol resolves that ambiguity by classifying the intended recipient and preserving expression in the durable Human Brief whenever the machine channel must remain pointer-only.
