# Mechanism Activation execution entry

All functions here are explicit, one-shot operations. `activation.py` classifies a
structured planned action, resolves mandatory mechanisms, evaluates their pre-action
gate, and recomputes two-sided material claims. Material acceptance requires an
explicit `MaterialObservationContext` populated by trusted expected-source resolvers
and physical-observation adapters outside the receipt; receipt fields alone always
fail closed. The context has no ordinary-caller binding API. It accepts only opaque,
one-use handles entered in the execution issuance ledger after a controlled resolver
has physically read the expected source and a controlled adapter has physically
consumed the observation. Caller-provided values, resolver/adapter labels, consumed
reference sets, constructed lookalike handles, or unbound secret markers are never
provenance. `validate_mechanism_activation.py`
checks canonical wiring and inventory truthfulness.

The resolver and gate never authorize, publish, mutate, deliver, acknowledge, poll,
schedule, or advance a task. Mechanism-specific execution remains in that mechanism's
own execution directory. Communication's publisher imports this gate so a newly
published formal action cannot bypass it.
