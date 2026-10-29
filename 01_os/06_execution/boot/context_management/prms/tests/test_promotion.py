"""Owner-publication consumption tested against local Git, not real Human identity."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError, canonical, digest
from memory import propose_experience, reconcile_experience_publication


def test_only_published_owner_ref_can_supply_k2_records(tmp_path):
    root, remote = tmp_path / "code", tmp_path / "published.git"
    root.mkdir()
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout.decode().strip()
    subprocess.run(["git", "init", "--bare", str(remote)], capture_output=True, check=True)
    git("init", "-q")
    git("remote", "add", "origin", str(remote))
    candidate = propose_experience(["fixture source"], ["fixture falsifier"], "all domains", "core-owned")
    (root / "method.md").write_text("# Synthetic owner-published method\n")
    blob = git("hash-object", "method.md")
    (root / "approval.json").write_text(json.dumps({"kind": "HUMAN_APPROVAL", "decision": "APPROVED", "subject_blob": blob}))
    (root / "review.json").write_text(json.dumps({"kind": "INDEPENDENT_REVIEW", "decision": "PASS", "subject_blob": blob,
                                                "reviewer_session": "fixture-review", "executor_session": "fixture-execution"}))
    manifest = {"schema_version": "prms.experience_publication.v1", "candidate_digest": digest(canonical(candidate)),
                "target_owner": "core-owned", "canonical_path": "method.md", "canonical_blob": blob,
                "human_approval_ref": "approval.json", "independent_review_ref": "review.json"}
    (root / "publication.json").write_text(json.dumps(manifest))
    git("add", "--", "method.md", "approval.json", "review.json", "publication.json")
    git("-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture publication")
    sha = git("rev-parse", "HEAD")
    source = GitSource(root, sha, "fixture/core")
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        reconcile_experience_publication(candidate, source, "publication.json")
    git("push", "origin", "HEAD:refs/heads/master")
    result = reconcile_experience_publication(candidate, source, "publication.json")
    assert result["layer"] == "K2" and not result["action_authorized"]
    assert result["mechanism_effective"] == "NOT_INFERRED_FROM_PUBLICATION"
    assert candidate["layer"] == "K1"  # original candidate is not silently rewritten
