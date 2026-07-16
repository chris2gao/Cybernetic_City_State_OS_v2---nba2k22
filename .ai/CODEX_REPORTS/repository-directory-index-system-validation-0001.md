# Repository Directory Index System 0001 — Validation Report

## Validation scope

Validation covers the complete generated index/manifest set on the candidate
and is repeated against the published Git tree after normal merge.

## Mechanical targets

| Target | Required | Result |
|---|---:|---|
| tracked directories indexed | 100% | pass: 160 / 160 |
| direct tracked files listed once | 100% | pass: 1,806 / 1,806 |
| direct child directories listed once | 100% | pass: 159 / 159 |
| missing / duplicate / orphan entries | 0 / 0 / 0 | pass: 0 / 0 / 0 |
| broken / unsafe links | 0 / 0 | pass: 0 / 0 |
| Git internal / untracked directories | 0 / 0 | pass: 0 / 0 |
| empty or generic descriptions | 0 | pass: 0 |
| UTF-8 / Markdown structure failures | 0 / 0 | pass: 0 / 0 |
| manual content lost | 0 | pass: 0; preservation self-test 2 / 2 |
| high-confidence secret findings | 0 | pass: 0 |
| deterministic second-run diff | 0 | pass: 0 |
| hashseed/TZ/cwd byte difference | 0 | pass: 3 / 3 byte-identical snapshots |
| git diff check | pass | pass: exact staged tree |

## Validation commands

```text
python generate_repository_indexes.py self-test
python generate_repository_indexes.py generate
python generate_repository_indexes.py check
python generate_repository_indexes.py validate
python generate_repository_indexes.py snapshot
```

Published verification adds `--ref <final-master>` and independently rebuilds
the inventory from `git ls-tree -r -z --full-tree <ref>`.

## Evidence qualification

Mechanical validation proves coverage, structure, byte stability and explicit
classification invariants. It does not replace foreground semantic review of
every generated natural-language summary. Real second-OS execution is not
available in this Windows host; the strongest local evidence is two isolated
paths with different `PYTHONHASHSEED`, `TZ`, locale variables and cwd plus a
nondeterminism source audit.

The three isolated snapshot cases also included an untrusted `GIT_INDEX_FILE`
and `GIT_DIR` injection case. All three produced byte-identical stdout with
SHA-256 `a02a4476838652b8bc98b9891fd4f78ac859acb2c6dafe6f6191aca56e45b89b`.
