from pathlib import Path
import subprocess
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError
from domain import scaffold_domain
from catalog import discover_g2


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)
    return result.stdout.decode().strip()


def test_new_domain_empty_catalog_identity_and_no_core_copy(tmp_path):
    (tmp_path / "CORE_MANIFEST.yml").write_text("domain_owned_paths: [08_Domain_Applications/]\n")
    receipt = scaffold_domain(tmp_path, "maths2.0", "example/maths", "a" * 40)
    assert receipt["status"] == "DOMAIN_CATALOG_INITIALIZED_EMPTY"
    git(tmp_path, "init", "-q")
    assert sorted(receipt["files"]) == sorted(["08_Domain_Applications/domain.yml", "08_Domain_Applications/knowledge_catalog.yml",
        "09_Domain_Global_Mechanisms/domain_mechanisms.yml", "09_Domain_Global_Mechanisms/README.md"])
    git(tmp_path, "add", "--", "CORE_MANIFEST.yml", "08_Domain_Applications/", "09_Domain_Global_Mechanisms/")
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


def test_scaffold_never_overwrites_any_existing_domain_file(tmp_path):
    (tmp_path / "CORE_MANIFEST.yml").write_text("domain_owned_paths: [08_Domain_Applications/]")
    for name in ("08_Domain_Applications/domain.yml", "08_Domain_Applications/knowledge_catalog.yml",
                 "09_Domain_Global_Mechanisms/README.md", "09_Domain_Global_Mechanisms/domain_mechanisms.yml"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("domain-owned content")
        with pytest.raises(PRMSError, match="REJECTED"):
            scaffold_domain(tmp_path, "maths2.0", "example/maths", "a" * 40)
        assert target.read_text() == "domain-owned content"
        written = [p for p in ("08_Domain_Applications/domain.yml", "09_Domain_Global_Mechanisms/domain_mechanisms.yml")
                   if p != name and (tmp_path / p).exists()]
        assert written == []
        target.unlink()


def test_missing_catalog_remains_uninitialized(tmp_path):
    (tmp_path / "08_Domain_Applications").mkdir()
    (tmp_path / "08_Domain_Applications/domain.yml").write_text("domain_id: example\nrepository: example/domain\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "--", "08_Domain_Applications/domain.yml")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "uninitialized G2")
    source = GitSource(tmp_path, git(tmp_path, "rev-parse", "HEAD"), "example/domain")
    assert discover_g2(source, "example")["status"] == "DOMAIN_CATALOG_UNINITIALIZED"


def test_formal_g2_uses_frozen_domain_body_and_matching_publication_evidence(tmp_path):
    (tmp_path / "CORE_MANIFEST.yml").write_text("domain_owned_paths: [08_Domain_Applications/]\n")
    scaffold_domain(tmp_path, "maths2.0", "example/maths", "a" * 40)
    body = tmp_path / "08_Domain_Applications/method.md"
    body.write_text("# Domain method\n\nSynthetic approved domain source.\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "--", "CORE_MANIFEST.yml", "08_Domain_Applications/", "09_Domain_Global_Mechanisms/")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "domain body")
    body_commit = git(tmp_path, "rev-parse", "HEAD")
    blob = git(tmp_path, "rev-parse", "HEAD:08_Domain_Applications/method.md")
    root = tmp_path / "08_Domain_Applications"
    evidence = {"schema_version": "prms.publication_evidence.v1", "mechanism_id": "method",
                "domain_id": "maths2.0", "repository": "example/maths", "subject_blob": blob}
    (root / "human.yml").write_text(yaml.safe_dump({**evidence, "kind": "HUMAN_APPROVAL", "decision": "APPROVED"}))
    (root / "review.yml").write_text(yaml.safe_dump({**evidence, "kind": "INDEPENDENT_REVIEW", "decision": "PASS",
                                                    "reviewer_session": "review", "executor_session": "execution"}))
    entry = {"mechanism_id": "method", "domain_id": "maths2.0", "repo": "example/maths",
             "source_commit": body_commit, "content_path": "08_Domain_Applications/method.md", "canonical_blob": blob,
             "owner": {"domain_id": "maths2.0", "repository": "example/maths"}, "publication_status": "PUBLISHED",
             "version": "1", "applicability": ["maths2.0"], "dependencies": [],
             "evidence_refs": ["08_Domain_Applications/human.yml", "08_Domain_Applications/review.yml"]}
    (tmp_path / "09_Domain_Global_Mechanisms/domain_mechanisms.yml").write_text(
        yaml.safe_dump({"domain_id": "maths2.0", "repository": "example/maths", "entries": [entry]}))
    git(tmp_path, "add", "--", "08_Domain_Applications/", "09_Domain_Global_Mechanisms/")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "published fixture records")
    source = GitSource(tmp_path, git(tmp_path, "rev-parse", "HEAD"), "example/maths")
    result = discover_g2(source, "maths2.0")
    assert result["entries"][0]["source"]["commit"] == body_commit
    assert result["entries"][0]["publication_verification"].startswith("MATCHING_PUBLISHED_RECORDS")
    assert result["entries"][0]["action_authorized"] is False
    from catalog import discover_g1
    from context import plan_context, human_choice, assemble_context
    from domain_context import plan_domain_context, choose_domain_context, assemble_domain_context
    core_root = Path(__file__).resolve().parents[6]
    core = GitSource(core_root, "446ca66ad48831f5fcdb1af18f37d07619e048c4", "fixture/core")
    cp = plan_context(core, discover_g1(core), session_id="s", role="planner", task_id="task")
    cc = human_choice(cp, session_id="s", selected_paths=[], decision_source="fixture")
    cr = assemble_context(core, cp, cc, budget_bytes=1_000_000)
    dp = plan_domain_context(source, result, cp, role="planner")
    dc = choose_domain_context(dp, session_id="s", selected_ids=[], decision_source="Human declines optional G2")
    dr = assemble_domain_context(source, cr, dp, dc, budget_bytes=1_000_000)
    assert dr["reads"] == [] and dr["skipped"][0]["reason"] == "NOT_SELECTED"
    assert not dr["action_authorized"]  # omission never grants the dependent operation
    # A follow-up source changes the reviewer into the executor: no silent approval.
    record = yaml.safe_load((root / "review.yml").read_text())
    record["reviewer_session"] = "execution"
    (root / "review.yml").write_text(yaml.safe_dump(record))
    git(tmp_path, "add", "--", "08_Domain_Applications/review.yml")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "invalid reviewer identity fixture")
    source = GitSource(tmp_path, git(tmp_path, "rev-parse", "HEAD"), "example/maths")
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        discover_g2(source, "maths2.0")


def commit_domain(tmp_path, domain_yml, catalog_path=None, catalog=None):
    (tmp_path / "08_Domain_Applications").mkdir(exist_ok=True)
    (tmp_path / "08_Domain_Applications/domain.yml").write_text(yaml.safe_dump(domain_yml))
    if catalog_path:
        (tmp_path / catalog_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / catalog_path).write_text(yaml.safe_dump(catalog))
    if not (tmp_path / ".git").exists():
        git(tmp_path, "init", "-q")
    git(tmp_path, "add", "-A")
    git(tmp_path, "-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
    return GitSource(tmp_path, git(tmp_path, "rev-parse", "HEAD"), "example/domain")


def test_catalog_lives_in_09_and_an_08_catalog_is_rejected(tmp_path):
    ident = {"domain_id": "example", "repository": "example/domain"}
    source = commit_domain(tmp_path, ident, "09_Domain_Global_Mechanisms/domain_mechanisms.yml", {**ident, "entries": []})
    assert discover_g2(source, "example")["status"] == "CATALOG_DISCOVERED_NOT_ACTIVATED"  # default path is 09
    source = commit_domain(tmp_path, {**ident, "global_mechanism_catalog": "08_Domain_Applications/domain_mechanisms.yml"},
                           "08_Domain_Applications/domain_mechanisms.yml", {**ident, "entries": []})
    with pytest.raises(PRMSError, match="REJECTED"):
        discover_g2(source, "example")


def test_entry_body_may_live_in_09_but_not_in_core(tmp_path):
    ident = {"domain_id": "example", "repository": "example/domain"}
    body = tmp_path / "09_Domain_Global_Mechanisms/loading_rule.md"
    body.parent.mkdir(parents=True)
    body.write_text("# Loading rule\n")
    source = commit_domain(tmp_path, ident)
    blob = git(tmp_path, "rev-parse", "HEAD:09_Domain_Global_Mechanisms/loading_rule.md")
    entry = {"mechanism_id": "rule", "domain_id": "example", "repo": "example/domain", "source_commit": source.commit,
             "content_path": "09_Domain_Global_Mechanisms/loading_rule.md", "canonical_blob": blob, "owner": "example",
             "publication_status": "DRAFT", "version": "1", "applicability": ["example"], "dependencies": [],
             "evidence_refs": []}
    source = commit_domain(tmp_path, ident, "09_Domain_Global_Mechanisms/domain_mechanisms.yml", {**ident, "entries": [entry]})
    assert discover_g2(source, "example")["entries"][0]["content_path"] == entry["content_path"]
    entry = {**entry, "content_path": "01_os/README.md", "canonical_blob": git(tmp_path, "rev-parse", "HEAD:08_Domain_Applications/domain.yml")}
    source = commit_domain(tmp_path, ident, "09_Domain_Global_Mechanisms/domain_mechanisms.yml", {**ident, "entries": [entry]})
    with pytest.raises(PRMSError, match="REJECTED"):
        discover_g2(source, "example")
