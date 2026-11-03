# Human ruling — source-only NBA2K22 mainline integration (2026-11-03)

Task: `OS-NBA2K22-HISTORICAL-BRANCH-INTEGRATION-20261103-001`.

The latest Human ruling **supersedes** the prior instruction to merge the entire Host commit history. Bring completed WorldData v24, Calendar, native advanced statistics, REA Bulk, Decision Outbox and SeasonCycleHost source and necessary documents into a clean branch starting at the latest NBA master. Keep large SQLite world snapshots, redundant backups, compressed data partitions and raw captures **locally** in offline archives. Preserve original paths, source Git blob identity, sizes and computed SHA256 in the final LOCAL archive receipt. Do not remove executable SQL Schema, migration source, original key reports or deterministic small test fixtures.

Old Host branches and Git objects remain intact pending a separate explicit decision on remote history rewriting, PR references and PRMS SHA rebind. No remote force push, old ref deletion, history pruning or hidden rewrite is authorized. Core merging is unaffected.

Actual local archive SHA256 computation is **pending access to the original full local Git object store**; the source manifest records SHA-1 Git blob IDs and exact sizes now, without inventing a SHA256 checksum. The bundled `archive_local_artifacts.py` computes them when executed locally. Old tests are not rerun under the Human's minimum-necessary integration policy.
