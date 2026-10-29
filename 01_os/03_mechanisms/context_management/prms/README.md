# Persistent role memory (PRMS)

Versioned extension of the existing context-management mechanism. Approved inputs:
NBA2K22 planning archive `3c53fd2e4ea98c7bd99b3c5961134690c4832803`,
A `OS-PRMS-A-v1-RC02`, B `B-v1-RC01`, and catalog addendum
`B-v1-RC01-ADDENDUM-CATALOG-01`. Approval provenance is recorded in that run's
Human records 16 and 17. Historical candidate headers do not revoke those decisions.

This code candidate is not deployed or independently accepted. It does not start
a service, create a state repository, merge Core or any domain, or activate a tool.

Implementation lives in `01_os/06_execution/boot/context_management/prms/`.
See [`TASK_CONTINUITY.md`](TASK_CONTINUITY.md) for explicit task save, switch,
resume and Human-relay receiver operations. Each task retains its own durable
context pointer; a new workbench reads its saved plan and loading instructions.
Code and catalogs travel with Core; mutable role CURRENT, event history and
credentials never do. State repositories require separate Human approval and a
trust boundary preventing clients from directly updating authoritative refs.

Discovery, summaries, body loading, effectiveness and action authorization remain
separate fields. B0 is mandatory, optional choices are session-bound, missing
required sources fail closed, and no recovery receipt grants execution rights.

Workflow, communications, task lifecycle and mechanism activation retain their
existing canonical owners. PRMS consumes their contracts rather than redefining
their authority. Source requirements and 48 acceptance scenarios remain pinned
in the implementation run's source manifest and coverage report.
