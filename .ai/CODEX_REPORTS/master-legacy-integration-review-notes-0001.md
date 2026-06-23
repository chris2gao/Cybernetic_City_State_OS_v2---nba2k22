# Master Legacy Integration Review Notes 0001

## Review Required

This dry-run branch is ready for human/ChatGPT review as an integration candidate. It is not approved for direct merge.

## Accepted Scope Executed

- Full `08_Domain_Applications/Math_Mentor` legacy replacement.
- Approved non-08 added/modified legacy import set, with no-op imports documented separately.
- Non-08 master deletions ignored.
- No source branch push.
- No master push.
- No Coordinator/runtime activation.

## Main Review Questions

1. Should risk-like root generation scripts and temp batch files remain in the final merge payload, given they are explicitly part of the approved import list?
2. Should active `.ai` mailbox files be merged as stateful artifacts or trimmed before final source publication?
3. Should legacy `08` staging directories remain in the final source branch, or be archived after merge review?

## Gate

`human_gate: required`
