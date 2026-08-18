---
document_id: os-v2-communication-git-blob-utf8-decoding-fix-001::execution-dispatch-00001
task_id: os-v2-communication-git-blob-utf8-decoding-fix-001
author_endpoint_id: gpt56-communication-utf8-foreground-001
author_task_role: communication_utf8_foreground_dispatch
purpose: Narrow implementation of locale-independent UTF-8 Git blob validation.
privacy_class: repository_shareable
---
# Objective

Fix the communication pointer validator so reading a repository text blob does not depend on the Windows ANSI code page, current locale, console code page, or `PYTHONUTF8` environment setting.

The observed defect is in `CommunicationValidator._git_blob`: `subprocess.run(..., text=True)` is used without an explicit encoding. A valid repository UTF-8 blob containing Chinese text can therefore be decoded as CP936/GBK on Windows and fail after GitHub convergence has already published the communication artifacts.

# Required implementation

Within the authorized task packet, implement the smallest deterministic fix:

1. Capture `git show <commit>:<relative>` stdout/stderr as bytes rather than locale-decoded text.
2. Decode successful stdout explicitly as UTF-8 with strict error handling.
3. Preserve the existing missing-blob error behavior for nonzero Git return codes.
4. Map invalid UTF-8 to a specific `CommunicationValidationError` that identifies the GitHub blob encoding failure; do not let it degrade into `yaml_input_must_be_text`.
5. Do not change pointer fields, communication protocol, authority semantics, resolver/gate behavior, publication sequencing, or Human relay semantics.
6. Do not make Windows locale changes or `PYTHONUTF8=1` part of the permanent implementation.

# Required verification

- Add a regression that exercises non-ASCII UTF-8 content through the Git blob readback/pointer validation path.
- Add a negative control for invalid UTF-8 bytes and require the specific fail-closed error.
- Ensure the GitHub republication test includes a non-ASCII UTF-8 artifact or manifest value so the actual convergence/bind path covers the previous blind spot.
- Run the relevant existing formal-activation and GitHub-republication suites, `git diff --check`, and exact changed-path allowlist verification.
- On Windows, capture Python version, `sys.flags.utf8_mode`, locale encoding, preferred encoding, and ACP if available. This is environment evidence only, not an implementation precondition.

# Repository boundary

Load the exact task packet and implementation brief from `01_os/_runs/run-20260817-communication-git-blob-utf8-decoding-fix-001/`. Work only on `dev/os-v2-communication-git-blob-utf8-decoding-fix-001`. Do not touch the stage-alignment task branch. Do not modify master.

If fixing the defect requires any protocol/schema/authority change or any path outside the packet allowlist, stop and return a formal blocked state rather than expanding scope.

# Completion

Commit and publish only the source task branch after local gates pass. Return exact candidate SHA, changed paths, commands/exit codes and environment evidence through the formal communication mechanism. Do not claim independent acceptance or master readiness.
