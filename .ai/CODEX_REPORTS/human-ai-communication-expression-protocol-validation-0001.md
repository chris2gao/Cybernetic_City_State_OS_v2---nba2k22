# Human-AI Communication Protocol Validation

```yaml
task_id: human-ai-communication-expression-protocol-0001
source_head: eb46be9dadf9672091883e4e69bcaaa70b0cb163
parent_candidate: 8f0eec213484d16a97956d356a9ef1e163fc45fe
validation_scope: consolidated_provider_neutral_correction_validation
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
| compatible role occupants mapped | 4 / 4 |
| fresh provider onboarding scenarios | 4 / 4 |
| mixed-recipient positive/fallback scenarios | 2 / 2 |
| unqualified canonical participant exclusions remaining | 0 |
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

The historical schema names are frozen compatibility labels. ChatGPT and Claude foreground occupants use the first sequence; Codex and Claude Code backend occupants use the second. Provider substitution does not rename a key, add a field, change order, or grant authority.

## Semantic Regression Checks

- Mandatory dispatch language is present across the canonical protocol, common conventions, autonomous communication mechanism, adherence rules, initialization prompt, and Codex work mechanism.
- Targeted scans found no remaining statement that a recommendation is optional, may merely be included, or is not required when the Human is asked to start or continue backend work.
- Statements that the recommendation is not a Human Brief or machine-pointer field are retained as channel-boundary rules, not optional-dispatch exceptions.
- Material review/completion without backend dispatch requires bounded expression but not an execution recommendation.
- Parser-only acknowledgement and explicit Human pointer-only/no-extra-text output remain narrow expression exemptions.
- Strict machine-only Codex output remains pointer-only and preserves expression through `brief_ref`.
- Every chain-of-thought reference is a negative guard; no private reasoning transcript is requested or disclosed.
- Human Speaker control over objective, engine routing, protected adjudication, source/master publication, runtime, Coordinator, secrets, and destructive operations is preserved.
- Role mapping is present in the canonical protocol and inherited by adherence, common conventions, autonomous communication, initialization, the backend work mechanism, and durable decisions.
- Targeted scans found no unqualified canonical scope/role/bootstrap statement that excludes Claude or Claude Code where compatibility matters.
- A separable mixed interface keeps the exact pointer bytes isolated and places Human status/recommendation/expression outside the closed block.
- A non-separable interface emits pointer-only, requires a non-null resolvable `brief_ref`, preserves all Human content in the Brief, and fails closed if that carrier is missing or incomplete.
- Interface fallback relocates content and is not treated as a Human waiver.

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
| fresh ChatGPT instance | foreground role + frozen ChatGPT-to-Codex schema | pass |
| fresh Claude instance | foreground role + same frozen ChatGPT-to-Codex schema | pass |
| fresh Codex instance | backend role + frozen Codex-to-ChatGPT schema + work mechanism | pass |
| fresh Claude Code instance | backend role + same frozen Codex-to-ChatGPT schema + work mechanism | pass |
| separable mixed Human+machine interface | unchanged pointer block + Human content outside | pass |
| non-separable mixed interface with resolvable Brief | pointer-only + all Human content through `brief_ref` | pass |
| non-separable mixed interface with null/missing/incomplete Brief | blocked | correctly rejected |
| expression or extra key inserted into pointer | fail pointer purity | correctly rejected |

## Residual Risk

Historical provider names remain visible in frozen wire labels, state values, path/key namespaces, and implementation-component names. The compatibility rule distinguishes those stable audit contracts from provider-derived authority; future providers still require a reviewed compatibility update rather than being inferred automatically.
