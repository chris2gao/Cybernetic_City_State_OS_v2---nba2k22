# Task-selected project context

This extends existing context management and reuses PRMS GitSource. It creates no
role state, service or authority. A project chooses its own index and JSON module
registry; module IDs and the business root are owner-defined, never NBA defaults.

```text
python -B 01_os/06_execution/task_discipline/project_context/project_context.py discover --repo-root <checkout> --repository <owner/repo> --commit <40-sha> --index <index.md> --registry <modules.json> --selected-module <id> --output <new-file.json>
python -B 01_os/06_execution/task_discipline/project_context/project_context.py sync --repo-root <checkout> --repository <owner/repo> --base <base-sha> --commit <candidate-sha> --index <index.md> --registry <modules.json> --affected-module <id>
```

Registry shape is `module_base` and `modules`, each with unique `id`, name,
evidence-scoped status, `docs` and implementation `artifacts`. Prefixes denote
directories. Discovery inventories references but loads only selected document
bodies. Explicit `../` navigation is disclosed without treating it as local domain
content. Missing selected sources fail; absent catalog is reported, not invented.

`sync` compares exact base/candidate Git trees. Code changes derive affected module
IDs from artifacts. The candidate must update both index and registry, including
the actual affected module records; an unrelated row change is insufficient.
Exit 1 means INDEX_SYNC_PENDING; 3 means invalid/missing source or contract.
These checks do not authenticate claims in prose or grant publication permission.

`source_status` re-resolves repository/commit/path and published-master ancestry;
a caller's Draft/master label cannot substitute for that observation.
`validate_handoff` checks exact source head, result, gaps, next steps, plan/actual
delta, reproduction and evidence scope, plus explicit write/next owners when a
workspace is shared. Independent review requires a distinct session and declared
absence of private executor context, but these declarations do not prove reality.

`retry_disposition` counts failed corrective actions for the same signature (not
read-only diagnosis). A changed remedy/new evidence is required; three exhausted
repairs require joint research and the existing failure log, with scope, evidence,
impact and the Human-model question. Unknown external outcomes are never blindly
replayed. This helper reports a disposition and never retries or logs on its own.
