# Task packet input

`task_packet_input.py` is the shared input reader for task preflight and changed
path ledger. It validates input, not authorization or historical execution.

- `wrapped_v1`: exactly one top-level `task_packet` mapping, the section-7 shape.
- `legacy_flat`: an existing unwrapped packet. Consumers report this format;
  it is not silently interpreted as the canonical wrapper.
- A wrapper mixed with any top-level sibling is rejected. Packet fields must
  have one location. Explicit duplicate YAML keys are rejected **before** merge
  expansion; legal merge overrides and non-cyclic aliases remain supported.
  Cyclic aliases, malformed YAML and invalid UTF-8 are input errors.

Both formats require nonempty strings `task_id` and `branch`, a full 40-hex
`exact_base_sha`, nonempty string lists `allowed_changed_paths` and
`required_tests`, and a string list `prohibitions` (an explicit empty list is
valid). False, null, zero and other falsey values do not substitute for these
types. Publisher, when present, must be a mapping; declared head fields must
each be full 40-hex SHAs. Optional `big_task` must be a boolean.

Legacy flat `explicit_prohibitions` is explicitly normalized to `prohibitions`
and reported in `normalized_fields`. If both exist, both must be string lists
and exactly equal; conflicting values fail closed. Wrapped input must include
the canonical `prohibitions` field.

`publisher.expected_remote_master_head` binds the master baseline;
`publisher.expected_remote_head` binds the target publication branch's expected
head. They are **not aliases** and may legitimately differ. No fallback between
them exists. An absent master expectation remains unverified in preflight and
fails its default physical gate. The existing diagnostic override does not
create publication permission.

Run tests with `python -m pytest 01_os/06_execution/task_discipline/packet_input -q`.
