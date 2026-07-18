---
load_profile_id: "foreground_planner"
authority: "routing_only"
reflects_protocol_release_head: ".ai/communication_compliance/material_event_policy.yml#protocol_release_head"
canonical_ref_digests:
  "06_Silicon_Index/CONSTITUTION_DIGEST.md": "ad7f76dca6a42657e7fc4220fdff0acde542c6ad52b894d796da008e90cd888e"
  ".ai/PROTOCOL.md": "1813d289ef5eb0148e33761046a91cff3e9339a63a1a43a45b20a0b092466857"
  ".ai/PROTOCOL_ADHERENCE.md": "d0e5321222aa955bc0a15ca47a62f70755035fdc17744311fa6c5b0427d581db"
  ".ai/CODEX_TASK_INPUT_CONTRACT.md": "3f2fc98049929777a56fb77a8db56b912d77a953ee00c00a0355a80eae52e565"
  ".ai/communication_compliance/communication_event.schema.json": "d4a9edd3f2f9a76d68dfeb7f38db8cc81f697cb8a6b04dfaece4fab873a07453"
---

# Foreground planner load profile

Routing manifest only; it grants no role, write access, transition, or Human authority.

Before any C1/C2 behavior, read the current Human instruction, current STATE/current
signal, and dereference every applicable non-null ref. This profile only routes; it
does not copy or replace protocol text.

Load the constitutional digest, the role and seven-field sections of `.ai/PROTOCOL.md`,
the current task-input contract and communication-event schema, and the review triggers
in `.ai/PROTOCOL_ADHERENCE.md`. Then dereference the current signal and task/packet refs.

Load `.ai/role_memory/core.md` plus `.ai/role_memory/planner.md` as routing-only memory.

Load full `3号方案.md` plus Awakening for a protected action or constitutional conflict.
Load the rest of the full protocol when adjudicating protocol meaning, publication,
transition eligibility, or a malformed/conflicting handoff.
