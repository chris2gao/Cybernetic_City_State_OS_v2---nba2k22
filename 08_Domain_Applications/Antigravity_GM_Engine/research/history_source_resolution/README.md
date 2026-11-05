# Historical source resolution

This directory preserves the eight exact WorldData inputs used by the archived information-assist pack, plus the matching Schema files. These files are historical research inputs. The live WorldData implementation remains in `world_data_prototype`.

From this directory, use `python -B -X utf8 resolve.py source competition_views.py` to read a public input. The command checks its Git blob ID, size and SHA256 before emitting bytes. A shallow clone needs the pinned capsule commit. Source entries identify the public Git commit, path and blob, with the historical commit recorded as provenance.

Use `python -B -X utf8 resolve.py data <git-blob-sha1> --archive-root <offline-archive-directory>` for data. It resolves the archive key and relative path from the index, verifies the local file, and prints the verified path. Missing and mismatched files exit with code 2. The archive root is supplied locally. This command makes no GitHub data request.

The index covers 234 Host files and 234 unique Host blobs, plus four distinct v25 snapshot segments outside the Host exclusion inventory. The groups have zero overlap. The 238 unique blob IDs are the precise cleanup scope. Repeated appearances in Git history are represented by a single blob ID.

The legacy scripts and candidate test receipts remain frozen in the original PRs. Use this entrypoint for new historical reads. The cleanup preserves the original PR #18 REA research inputs and the original PR #26 and #27 commits.
