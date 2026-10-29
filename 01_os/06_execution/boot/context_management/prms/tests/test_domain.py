from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError
from domain import scaffold_domain
from catalog import discover_g2


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)
    return result.stdout.decode().strip()


def test_new_domain_empty_catalog_identity_and_no_core_copy(tmp_path):
    (tmp_path / "CORE_MANIFEST.yml").write_text("domain_owned_paths: [09_Domain_Global_Mechanisms/]\n")
    receipt = scaffold_domain(tmp_path, "maths2.0", "example/maths", "a" * 40)
    assert receipt["status"] == "DOMAIN_CATALOG_INITIALIZED_EMPTY"
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "--", "CORE_MANIFEST.yml", "08_Domain_Applications/domain.yml", "09_Domain_Global_Mechanisms/")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "isolated domain fixture")
    sha = git(tmp_path, "rev-parse", "HEAD")
    source = GitSource(tmp_path, sha, "example/maths")
    catalog = discover_g2(source, "maths2.0")
    assert catalog["entries"] == [] and catalog["candidates"] == []
    assert catalog["status"] == "CATALOG_DISCOVERED_NOT_ACTIVATED"
    with pytest.raises(PRMSError, match="REJECTED"):
        discover_g2(source, "nba2k22")
    with pytest.raises(PRMSError, match="REJECTED"):
        scaffold_domain(tmp_path, "maths2.0", "example/maths", sha)


def test_missing_catalog_remains_uninitialized(tmp_path):
    (tmp_path / "08_Domain_Applications").mkdir()
    (tmp_path / "08_Domain_Applications/domain.yml").write_text("domain_id: example\nrepository: example/domain\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "--", "08_Domain_Applications/domain.yml")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "uninitialized G2")
    source = GitSource(tmp_path, git(tmp_path, "rev-parse", "HEAD"), "example/domain")
    assert discover_g2(source, "example")["status"] == "DOMAIN_CATALOG_UNINITIALIZED"
