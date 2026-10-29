# Durable tasks, disposable windows

Default work is sequential. Human explicitly requests saving A before switching
to B. Save first, confirm the durable commit, then switch. PRMS does not initiate
a switch, background capture or another model. Returning to A reads its own saved
context; B's current assignment does not hide A.

## Durable record

`SAVE_TASK_CONTEXT` is a task-scoped existing WriterGate operation. One Git tree
publishes the immutable context, per-task CURRENT, checkpoint and role CURRENT.
Each task has its own `roles/<role>/tasks/<task>/CURRENT.json`. Revisions preserve
previous plans and events. The window and temporary session capability are not
the memory store.

Input has `task_id`, `task_plan`, `load_spec`. The plan contains `objective` and
explicit lists `plan`, `progress`, `open_items`, `next_steps`, `human_decision_refs`.
Record actual Human wording as HUMAN_DECISION events with original sources;
plan references and model summaries cannot fabricate new approvals.

The load specification contains `core_repository`, exact `core_commit`,
`role_type`, ongoing Human `memory_choice_ref`, optional `stage`, `actions`,
`required_paths`, `optional_paths`, `selected_paths`, `history_depth` and
`selected_event_ids`. Resume rebinds this retained context-only selection to the
new session. An ongoing Human instruction survives a window switch; it grants
no additional execution or copy authority.

## Foreground commands

An isolated state store must already exist outside Core/domain code. Save uses
its current owner session. These commands do not create repositories, credentials
or services. Deployed hosts instead call the same operation through their ingress.

```text
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py save --state-root <existing-isolated-state> --role <role-id> --session <current-owner> --payload <task-plan.json> --operation-id <unique-save-id> --isolated-test-only --output <new-save-receipt.json>
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py list --state-root <existing-state> --role <role-id> --output <new-task-list.json>
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py resume --state-root <existing-state> --role <role-id> --task <task-id> --session <new-window-id> --core-root <Core-checkout> --output <new-workbench-directory>
```

Resume gets Core version and loading instructions from durable state, without the
old chat, old session capability or old temporary plan files. It reads all latest
durable events for the selected task, including facts newer than its checkpoint;
lag and missing history are explicit. It does not change the current role/task
assignment or state. Updating frozen source versions remains an explicit action.

The new workbench contains readable `CONTEXT.md` with saved plan/progress/next
work, typed facts and decisions, gaps and actual selected Core bodies. It also
contains recovery JSON, plan, choice, history choice, exact-byte bundle and a
separately retained receiver request. Human opens/pastes the context into the new
window. No automatic app injection or model comprehension is claimed.

## Receiver file contract

`handoff_cli.py export`, `receive`, `verify-ack` use explicit Core/state,
plan/choice/history files. Export takes package and handoff ID; receive takes the
separately retained request and current receiver session. `--help` lists arguments.
Verification rereads exact source bytes/current state and binds role, task,
session and choices. Changed/missing objects, stale state and insufficient budget
are rejected. Outputs cannot silently overwrite. PARTIAL context retains gaps;
BLOCKED context cannot be exported as usable context. Context and transport byte
budgets are measured separately.

An ack proves receiver-tool file validation, not model identity, comprehension,
owner takeover, delivery or execution authorization. These artifacts are context
files; formal OS task messages retain communication_system's Human-relay contract.

## Dormant trusted-host port

`ingress.TrustedIngress(store, authority, enabled=False)` is callable but dormant.
HostAuthority authenticates opaque transport contexts and returns immutable
HostSession role/task/operation scopes and exact four-part CopyGrants. Mutation
and copy reauthenticate before publication. Expired/revoked/substituted/out-of-
scope calls are rejected. Host control may revoke sessions; recover is scoped.
Missing copy grants deny copy in every mode.

The host must keep this object, authority and transport outside model control.
It is an integration port, not a new identity provider or network service.
Fake-transport tests establish IMPLEMENTED_UNVERIFIED_PLATFORM only.
`require_enforced()` still refuses unproved fencing. Real GitHub/host/window
experiments remain NOT_RUN; deployment is outside this task's completion scope.
