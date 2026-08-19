---
document_id: os-v2-citystate-local-host-control-baseline-001::poc-a-retry-execution-00002
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Correct the POC-A Human Task Authority challenge procedure after the first executor produced a commitment mismatch without running the canonical verifier.
privacy_class: repository_shareable
---
# Task B / POC-A retry correction

This is a retry of the same bounded POC-A under the unchanged Task B Current Model and unchanged Human Task Authority. The prior blocked result at commit `1245d9592d5fe1843b831bc4cee4b395b2e0207e` remains valid history and proves only that the prior recipient-side challenge procedure returned mismatch; it does not prove that the Human code or durable authority record is invalid.

## Mandatory correction: canonical verifier only

Do not ask the Human to paste the Human Task Authority Code into ChatGPT. Do not manually implement, approximate, mentally calculate or independently re-code the canonical JSON/SHA-256 construction.

Before any Remote Desktop Commander POC probe, ask the current Human to perform the following manual authority-verification step on the Windows host in an ordinary PowerShell window. This manual secret-entry step is intentionally Human-only.

Use the existing local Task B worktree:

```powershell
cd E:\_pubwork\localhost-b-001
python .\01_os\06_execution\boot\stage_collaborative_deliberation\human_challenge_verify.py . .\01_os\_communication\Cybernetic_City_State_OS_v2---core\active\os-v2-citystate-local-host-control-baseline-001\Human\task_authority_v2.yml
```

If `python` is not available as that command, the Human may use `py -3` with the same script and arguments. No Human code appears in the command line.

When the verifier prompts for `Human Task Authority / legacy authority code (not echoed)`, the Human types the Task B code directly into that local hidden-input prompt. The Human must not paste the code into ChatGPT, GitHub, a file, a command line, a log, or any durable artifact.

The Human then pastes back only the verifier's JSON output. Accept the challenge only if all of the following hold:
- `result` is `verified`;
- `scheme` is `citystate-human-task-authority-v2`;
- `task_id` is `os-v2-citystate-local-host-control-baseline-001`;
- `decision_id` is `D-LOCALHOST-BASELINE-001-EXECUTION`;
- `decision_type` is `substantive_execution_authorization`;
- `exact_model_version` is `chatgpt-local-host-control-mcp-current-model-v2`;
- `plaintext_persisted` is `false`;
- `commitment_checked` exactly equals the stored event commitment in `Human/task_authority_v2.yml`.

The canonical verifier itself verifies both the task commitment and decision-event commitment before returning `verified`. If the verifier is unavailable, returns mismatch, or the pasted JSON fields do not match the durable authority record, STOP and publish `blocked_authority_challenge` without using Remote Desktop Commander for POC execution.

## POC probes after challenge VERIFIED

After challenge VERIFIED, execute the POC-A probes from `documents/gpt56-localhost-b-foreground-001/00001_poc_a_execution.md`, with only its old challenge paragraph replaced by this correction. The local POC scope remains unchanged: device/tool discovery, non-recursive Desktop listing, exact harmless test-file create/readback/cleanup, benign PowerShell output/version, bounded node-process metadata, and optional read-only Git probe.

All prior safety boundaries remain active: no secrets or credentials, no administrator escalation, no system-security changes, no VPS/DNS/VPN/nginx/xray/cloudflared/firewall work, no paid/API-credit activation, no destructive Git, no unrelated deletion, and no redelegation.

Publish one formal result to the foreground and STOP. Do not begin another Task B subtask.
