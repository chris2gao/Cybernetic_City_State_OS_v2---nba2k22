# Cooperative communication lanes

This directory defines a C0/C1 cooperative convenience layer. It prevents accidental
shared-file overwrites and reduces repeated context. It is not a trusted runtime,
identity system, scheduler, CAS protocol, authorization source, or replacement for
the communication gate.

## Instance layout

```text
.ai/lanes/<lane_instance_id>/
├── meta.yml
├── seq
└── events/
    ├── NNN.lane-envelope.yml
    └── NNN.yml
```

`lane_instance_id` is a self-declared local UUID-like identifier. `meta.yml`, `seq`,
and temporary files are local runtime bookkeeping and are ignored. Durable event and
envelope artifacts may be tracked on `ai/review/latest` so canonical STATE can cite
them immutably.

An event uses the existing communication-event schema and keeps its seven-field
pointer byte shape unchanged. Its `required_refs` includes the independent envelope
artifact. Because an immutable Git ref cannot refer to the commit that contains
itself, publish the envelope first, then publish `NNN.yml` referring to that envelope
commit. There is no dual write to legacy `.ai/OUTBOX.md`.

Each instance appends only to its own directory. Files are first written to a temporary
name and atomically renamed. `seq` increases monotonically. `reduce-lanes.ps1` rejects
an envelope whose lane ID differs from its directory, duplicate backend claims for one
task, duplicate event IDs, and a task listed as both legacy and lane delivery.

## Canonical reduction

Only the foreground role invokes `reduce-lanes.ps1` to write `.ai/STATE.yml`. The
reducer takes the maximum numbered event per lane, sorts by lane ID and sequence,
ignores events whose reflected review head predates the configured lane epoch, and
records immutable event and envelope refs plus SHA-256 digests in `lane_inputs`.
The communication gate only parses and resolves those optional refs; it does not
upgrade policy, authorization, or transition semantics.

After the protocol release named by
`.ai/communication_compliance/material_event_policy.yml#protocol_release_head`, backend
receipts use lanes. Legacy shared OUTBOX is read-only compatibility input. The same
event must not be written to both channels, and the same task in mixed mode fails
closed. Source/master neutral mailbox rules remain unchanged.
