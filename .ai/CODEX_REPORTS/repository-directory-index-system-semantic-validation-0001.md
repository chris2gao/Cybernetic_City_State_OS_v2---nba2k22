# Repository Directory Index System Semantic Validation 0001

## Result

`pass`

## Required gates

- Python compile and generator self-test
- exact semantic ledger counts and zero unknowns
- 160/updated-final directory indexes, 1,806/updated-final direct files, and 159 child edges, each exactly once
- zero missing/duplicate/orphan entries and zero broken/unsafe links
- canonical UTF-8/LF generated blocks and ordered required sections
- zero secret-value findings and zero generic/tautological phrase findings
- 14 metadata-only protected entries and zero protected-body reads
- source-neutral mailbox boundary
- deterministic second generation and identical snapshots
- full JSON/YAML structural classification, anchor uniqueness, and rendered-fragment checks
- final Git-tree validation by exact candidate ref

## Exact results

- `python -m py_compile generate_repository_indexes.py`: pass
- `python generate_repository_indexes.py self-test`: pass, including 6 file-boundary, 2 directory-boundary, 8 schema-structure, 7 structured-anchor, and 2 confirmed repository-regression cases
- `python generate_repository_indexes.py check`: pass, 161 generated outputs
- `python generate_repository_indexes.py validate`: pass
- `python generate_repository_indexes.py semantic-audit`: pass
- `python generate_repository_indexes.py compare-baseline`: pass; 1,806/1,806 baseline files joined exactly once and correction totals reproduced
- tracked directories / index files: 160 / 160
- final direct-file entries: 1,809 (1,806 audited baseline entries plus three required semantic reports)
- direct-child-directory entries: 159
- missing or duplicate file/child entries: 0
- orphan indexes, broken links, unsafe links: 0
- UTF-8, Markdown structure, empty/generic description failures: 0
- secret-value findings: 0
- metadata-only file entries: 14
- `unknown_requires_review`: 0
- private or restricted body reads: 0
- readable JSON/YAML artifacts structurally scanned: 1,169
- metadata-only JSON/YAML exclusions: 1
- physical schema-shaped artifacts / schema-classified: 22 / 22
- schema filename variants / schema-classified: 22 / 22
- all structured schema-authority artifacts: 24 (22 physical schemas plus 2 explicit structured schema contracts)
- schema-shaped misclassifications: 0
- exact duplicate structured anchors: 0
- repeated rendered anchor fragments: 0
- records with safely path-qualified anchors: 72
- confirmed regressions: 2 / 2 pass

## Deterministic hashes

- tracked pathset: `9cc33ffc7011c7647fefc1dfd9b6f60ed2b007f43b8614b54e40c851b3e0129f`
- directory set: `e174f7f0a54ff3d0b24b9faed089af79a9dad18c3352ad88281a74420528a293`
- coverage edges: `96e4f8a3e4895b7a09d59d395a11a5c7cc79e8d30c4b9e7dd82f9d0237f52ff4`
- generated indexes: `89ec7fe4e62331a13e4b7591a652a63ae65c2b3c9c741f50b7750e9ab21df598`
- manifest bytes: `8db0fbfad85421cf5f2815aa9096b379f0c91ac17fc48090eaf6cc2c7ccc97c9`
- output bundle: `bef50d624b77eadf8b7f5096d5f7244fce608116a270223253a1f4256a41e9ff`

The second generation, staged-tree revalidation, committed-ref validation, remote-master equality, and source-neutral mailbox readback are publication gates recorded in the final handoff.
