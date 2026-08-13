# Mechanism Activation and Adherence

This mechanism binds a planned action to the mechanisms that the OS requires for
that action. It separates four facts that must never be collapsed:

1. the formal-action constitution classifies intent and normalizes the recipient;
2. the trigger resolver decides which mechanisms are mandatory;
3. the pre-action gate verifies already-existing preconditions but grants no authority;
4. post-action evidence proves what physically happened through two-sided claims.

Natural-language text can always remain ordinary Human discussion. It becomes an OS
formal cross-endpoint action only through the constitution path and its evidence. A
copied prompt, role label, provider name, or plausible-looking pointer cannot create a
valid formal action.

The canonical contracts in this directory are loaded by
`../../02_boot/mechanism_activation/启动清单_v1.yml`. Executable classification,
resolution, gating, material-claim comparison, and receipt validation live under
`../../06_execution/boot/mechanism_activation/`.

## Boundaries

- The resolver and gate have `authority_effect: none`.
- Mechanism MUST decisions live here; optional wrappers or skills only implement HOW.
- No loader starts delivery, polling, acknowledgement, scheduling, task progression,
  watcher, daemon, or coordinator behavior.
- Communication is the first complete gated vertical slice. Other mechanisms remain
  at their honestly inventoried level until separately upgraded and independently
  accepted.
- Generic workflow validation-modality routing is outside this mechanism.

## Effectiveness language

`L0_DEFINED`, `L1_BOOT_VISIBLE`, `L2_TRIGGER_BOUND`, `L3_EXECUTION_GATED`, and
`L4_E2E_ADVERSARIALLY_VERIFIED` are cumulative. Only independently verified L4 may
be called `operationally_active`; a candidate awaiting independent acceptance must say
so explicitly.
