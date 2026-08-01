# Personal-path repository validator

This deterministic validator finds configured personal absolute paths in UTF-8 text.
It scans either every tracked file in the requested repository-relative scopes or
every file changed from an explicit Git base, including staged, unstaged and
untracked files. It does not run continuously, use the network, enter boot, or expose
an MCP surface.

## Usage

```powershell
python 08_os/06_execution/validators/personal_paths/validate.py `
  --repo-root . --mode tracked 08_os

python 08_os/06_execution/validators/personal_paths/validate.py `
  --repo-root . --mode changed --base <40-character-sha>
```

`--summary-only` suppresses detailed findings when retained evidence must contain
counts without reproducing sensitive path strings. Normal output reports the
repository-relative file, line, pattern ID and matching line snippet for every hit.

## Pattern table

`patterns.json` is the default configurable pattern table. A pattern may provide a
single `literal` or a list of `segments`, which are concatenated before scanning.
The default table uses segments so the validator does not create its own finding.
User-specific values belong in configuration, never in validator logic.

## Exit codes

| Exit | Meaning |
| :--- | :--- |
| `0` | All requested UTF-8 text is clean. |
| `1` | One or more configured paths were found. |
| `2` | Invocation, configuration, Git, scope or file-access error. |

Binary, symlink and non-UTF-8 files are counted as skipped because this validator's
declared scope is UTF-8 text. Tests cover clean tracked input, a generated negative
fixture, changed-mode detection, detailed reporting, summary-only reporting, and the
three exit-code classes.
