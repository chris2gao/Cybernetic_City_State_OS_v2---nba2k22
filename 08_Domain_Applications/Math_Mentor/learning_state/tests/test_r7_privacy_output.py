"""Round-7: the privacy scan must not publish the values it exists to catch.

The scanner reported raw paths.  A denylist term can appear in a tracked
FILENAME, so a filename hit printed the term itself - into a log written for
committing.  The round-6 test that claimed "denylist values are never printed"
used a content-only term, so the filename case went unnoticed.

Every scan here runs against a synthetic throwaway Git repository, never the
real one, so a term can be planted in a tracked filename safely.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest

PACKAGE = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    )


@pytest.fixture
def planted_repo(tmp_path: Path):
    """A synthetic repo with the term in BOTH a filename and file content.

    Returns (repo_path, term).  The term is generated per run so it can never
    collide with anything in the real repository.
    """
    term = f"plantedalias{uuid4().hex[:10]}"
    repo = tmp_path / "synthetic_repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    _git(repo, "config", "user.name", "fixture")

    # The term in a tracked FILENAME - the case that used to leak.
    (repo / f"notes_{term}.md").write_text("nothing sensitive inside\n", encoding="utf-8")
    # And the term inside tracked CONTENT, under an innocent filename.
    (repo / "other.md").write_text(f"mentions {term} once\n", encoding="utf-8")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "planted fixture")
    return repo, term


def _scan_repo(repo: Path, term: str, *args: str) -> subprocess.CompletedProcess:
    """Scan the synthetic repo.

    `--repo-root` is required: the scanner resolves its default repository from
    its own file location, so a bare `cwd=` would silently scan the real one.
    """
    env = dict(os.environ)
    env["LEARNER_DENYLIST"] = term
    return subprocess.run(
        [
            sys.executable,
            str(PACKAGE / "privacy_scan.py"),
            "HEAD",
            "--repo-root",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def _scan_real(denylist: str, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["LEARNER_DENYLIST"] = denylist
    return subprocess.run(
        [sys.executable, str(PACKAGE / "privacy_scan.py"), "HEAD", *args],
        capture_output=True,
        text=True,
        env=env,
    )


# --- the leak that motivated this round ------------------------------------


def test_filename_hit_is_counted(planted_repo):
    repo, term = planted_repo
    result = _scan_repo(repo, term)
    assert "filename_hits: 0" not in result.stdout, result.stdout + result.stderr
    assert result.returncode == 1


def test_term_never_appears_in_stdout_or_stderr(planted_repo):
    """The whole point: a filename hit must not publish the term."""
    repo, term = planted_repo
    result = _scan_repo(repo, term)
    assert term not in result.stdout, "a denylist term reached stdout"
    assert term not in result.stderr, "a denylist term reached stderr"


def test_content_and_filename_hits_are_both_redacted(planted_repo):
    repo, term = planted_repo
    result = _scan_repo(repo, term)
    assert "[REDACTED]" in result.stdout
    assert "path_disclosure: redacted+fingerprint" in result.stdout
    assert term not in result.stdout


def test_redaction_is_case_insensitive(planted_repo):
    """Filename matching is case-insensitive, so redaction must be too."""
    repo, term = planted_repo
    result = _scan_repo(repo, term.upper())
    assert term not in result.stdout
    assert term.upper() not in result.stdout


def test_reveal_flag_is_opt_in_and_not_the_default(planted_repo):
    repo, term = planted_repo
    default = _scan_repo(repo, term)
    assert term not in default.stdout

    revealed = _scan_repo(repo, term, "--reveal-paths")
    assert term in revealed.stdout, "the local diagnostic must still be useful"
    assert "NOT committable" in revealed.stderr


# --- properties that must survive the change -------------------------------


def test_invalid_ref_is_still_exit_two_and_never_clean():
    env = dict(os.environ)
    env["LEARNER_DENYLIST"] = f"absent-{uuid4().hex}"
    bad = subprocess.run(
        [sys.executable, str(PACKAGE / "privacy_scan.py"), "definitely-not-a-ref-xyz"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert bad.returncode == 2
    assert "SCAN FAILED" in bad.stdout
    assert "NOT a clean result" in bad.stdout


def test_clean_scan_is_still_exit_zero():
    """A term invented per run cannot be in the tree, so the tree is clean."""
    result = _scan_real(f"absent-{uuid4().hex}")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "content_matching_lines: 0" in result.stdout
    assert "filename_hits: 0" in result.stdout
    assert "scan_errors: 0" in result.stdout


def test_duplicate_denylist_entries_are_still_deduplicated():
    term = f"absent-{uuid4().hex}"
    result = _scan_real(f"{term},{term}, {term} ")
    assert "denylist_terms: 1" in result.stdout
