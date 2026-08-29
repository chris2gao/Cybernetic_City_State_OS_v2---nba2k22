# window_role_binding (Stage 04 fixture overlay)

Reference conforming shape for the T2 composition mechanism. It is a **test
fixture**, not the implementation: Stage 05/06 chooses its own mechanism name,
filenames and field names. This overlay deliberately differs from B's proposal
on all three, so that a green run proves the frozen checks are not fitted to
B's naming.

The mechanism owns three contracts and nothing else:

- `roles_v1.yml` — provider-independent role contract, authority effect none;
- `windows_v1.yml` — formal window identity, entry modes, lifecycle, and the
  bindings to `context_management` and `model_routing` by pointer;
- `handoff_v1.yml` — structured cross-window handoff, Human-relayed.

`context_management` remains the source of truth for context and stale
semantics. `model_routing` remains the source of truth for provider, surface,
model and parameter selection, and its route authority stays `routing_only`.
`communication_system` remains the Human-relayed message transport; this
mechanism never becomes live message or session state.

Failure surfaces at the validator or the boot receipt. Nothing here starts a
background process, spawns a window, delivers a handoff or advances a task.
