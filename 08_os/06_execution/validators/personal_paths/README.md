# Personal-path repository validator

This deterministic validator finds configured personal absolute paths in UTF-8 text.
It scans either every tracked file in the requested repository-relative scopes or
every file changed from an explicit Git base, including staged, unstaged and
untracked files. It is an on-demand validator; it does not run continuously, use the
network, enter boot, or expose an MCP surface.

## Usage

```powershell
python 08_os/06_execution/validators/personal_paths/validate.py `
  --repo-root . --mode tracked 08_os

python 08_os/06_execution/validators/personal_paths/validate.py `
  --repo-root . --mode changed --base <40-character-sha>

python 08_os/06_execution/validators/personal_paths/validate.py `
  --repo-root . --mode changed --base <remote-sha> --head <local-sha>
```

`--summary-only` suppresses detailed findings when retained evidence must contain
counts without reproducing sensitive path strings. Normal output reports the
repository-relative file, line, pattern ID and matching line snippet for every hit.
When `--head` is supplied, changed mode reads the exact blobs at that commit and does
not mix in staged, unstaged or untracked working-tree content. The pre-push guard uses
this form for the exact `remote_sha..local_sha` range.

## Pattern table

`patterns.json` is the default configurable pattern table. A pattern may provide a
single `literal` or a list of `segments`, which are concatenated before scanning.
Each entry may also declare a `variants` list. The built-in variant family is
literal-only and deterministic: `canonical`, `escaped_backslash`, and
`forward_slash`. Windows-rooted entries may additionally set `case_insensitive: true`
so one segmented Windows home value can cover canonical, JSON-escaped,
forward-slash, and lowercase variants without duplicating the personal path in the
pattern table itself. The default table uses segments so the validator does not
create its own finding. User-specific values belong in configuration, never in
validator logic.

The default table also covers the WSL-style mounted forms of the configured Windows
home and workspace roots (`/mnt/<drive>/...`). The Linux home and mounted families
are case-insensitive; equivalent literal variants are deterministically de-duplicated.

## Exit codes

| Exit | Meaning |
| :--- | :--- |
| `0` | All requested UTF-8 text is clean. |
| `1` | One or more configured paths were found. |
| `2` | Invocation, configuration, Git, scope or file-access error. |

Binary, symlink and non-UTF-8 files are counted as skipped because this validator's
declared scope is UTF-8 text. Tests cover clean tracked input, a generated negative
fixture, changed-mode detection, escaped-backslash coverage, forward-slash coverage,
case-insensitive coverage, detailed reporting, summary-only reporting, and the three
exit-code classes.

## Known limitations

Exit `0` means only that the selected UTF-8 text, under the selected Git scope, did
not contain any configured variants at scan time. It does not prove the whole
repository is clean, it does not cover binary or non-UTF-8 files, and it cannot detect
path families that are absent from `patterns.json`.
