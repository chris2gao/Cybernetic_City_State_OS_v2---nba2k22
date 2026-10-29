# Independent code-completeness review and repair scope

Human relayed the first independent read-only review on 2026-10-29, against
code e432afd2152bf50834b619f09c64ed61ca245017 and handoff
e3101d4000ab74a1cbdc6e1dcee675a26701de83. Verdict:
PARTIAL_IMPLEMENTATION / CODE_COMPLETE_NOT_ESTABLISHED. The reviewer did not
rerun the Owner tests or perform real platform, host or model-window experiments.

- IR-01: implement a dormant, callable TrustedIngress/WriterGate adapter with
  host-authenticated sessions, assignment scopes, revocation and GitHub backend
  calls; fake transport tests are implementation evidence only.
- IR-02: require exact source role, target role, frozen source commit and Human
  approval binding for every full-copy grant; no permissive default.
- IR-03: implement deterministic export and receiver acknowledgement for a new
  window, binding session, source, choice, role and actual loaded bytes. Use
  explicit Human relay; do not promise automatic injection or understanding.
- IR-04: retain proof-scope distinctions and unexecuted external gates.

Owner accepts R1 and R2 as in-scope engineering corrections, not deployment.
No real state repository, credential, service, independent chat or model window
is created. All eleven external-scope scenarios remain NOT_RUN until actual
evidence exists. A new exact code candidate and managed regression are required
before independent rereview. This file records review input, not repair success.

## Subsequent direct Human scope clarification

Human then clarified: the important result is correct context memory management
and loading according to the task plan; a model window is a temporary workbench,
and switching it must not sever memory. Correct loading/management is sufficient
to end this task. Normally tasks execute sequentially. Before A -> B, Human
explicitly requests saving A and intervenes in context management.

This supersedes treating real deployment/permission or independent acceptance as
mandatory closure gates for this engineering task. Preserve those original
external scenarios as NOT_RUN, without claiming production or full original
product acceptance. The remaining engineering focus is explicit durable per-task
save, correct source/plan-based resume in fresh workbenches, gap/budget handling,
regression and reviewable task-branch delivery. No automatic task switching.
