---
load_profile_id: "backend_executor"
authority: "routing_only"
reflects_protocol_release_head: ".ai/communication_compliance/material_event_policy.yml#protocol_release_head"
canonical_ref_digests:
  "06_Silicon_Index/CONSTITUTION_DIGEST.md": "ad7f76dca6a42657e7fc4220fdff0acde542c6ad52b894d796da008e90cd888e"
  "AGENTS.md": "356afde2be0bd60fd5fe6078624cb5a78c4338693efda52882eb0c5a271bc827"
  ".ai/TOKEN_USAGE_PROFILE.md": "b738226e32c1efddf8c61ffa551b728c201dd82ed02d6dd86fa9bb4c887cbadb"
  ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md": "5c3f0c6acf12f1eed546088cd9c8a90050859681516de11414029e5a05b04f49"
---

# Backend executor load profile

Routing manifest only; it grants no role, write access, publication, or Human authority.

Load the constitutional digest, `AGENTS.md`, `.ai/TOKEN_USAGE_PROFILE.md`, the backend
work-mechanism protocol, and the exact current task packet. The token profile is a lazy
canonical pointer here; this manifest does not copy its discipline. Dereference every
non-null current signal ref.

Load the default large-task or long-run protocol only when its trigger applies. Load
Math Mentor teaching/validation contracts only for a Math Mentor task. Load full
constitutional sources for protected actions or constitutional conflict.
