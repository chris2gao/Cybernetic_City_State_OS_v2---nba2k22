import json
import shutil
import subprocess
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "publish-review.ps1"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo).stdout.strip()


def new_remote(tmp_path: Path) -> tuple[Path, Path, str]:
    bare = tmp_path / "remote.git"
    source = tmp_path / "source"
    run("git", "init", "--bare", str(bare), cwd=tmp_path)
    source.mkdir()
    git(source, "init")
    git(source, "config", "user.email", "publish-test@example.invalid")
    git(source, "config", "user.name", "Publish Test")
    existing = source / ".ai" / "existing.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("existing\n", encoding="utf-8")
    git(source, "add", "--", ".ai/existing.md")
    git(source, "commit", "-m", "seed")
    git(source, "remote", "add", "origin", str(bare))
    git(source, "push", "-u", "origin", "HEAD:ai/review/latest")
    return source, bare, git(source, "rev-parse", "HEAD")


def invoke(
    source: Path,
    staging: Path,
    city_state: Path,
    *extra: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL
    return run(
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-SourceDir",
        str(staging),
        "-Message",
        "publish test",
        "-RepositoryRoot",
        str(source),
        "-CityStateRoot",
        str(city_state),
        *extra,
        cwd=source,
        check=check,
    )


def staging_tree(tmp_path: Path, name: str = "staging") -> Path:
    staging = tmp_path / name
    report = staging / "CODEX_REPORTS" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text("report\n", encoding="utf-8")
    return staging


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_publish_review_dry_run_keeps_remote_and_staging(tmp_path: Path) -> None:
    source, bare, original = new_remote(tmp_path)
    staging = staging_tree(tmp_path)
    result = invoke(
        source,
        staging,
        tmp_path / "citystate",
        "-Refs",
        ".ai/existing.md",
        "-DryRun",
    )
    value = json.loads(result.stdout)
    assert value["status"] == "dry_run_pass"
    assert value["changed_paths"] == [".ai/CODEX_REPORTS/report.md"]
    assert staging.exists()
    assert run("git", "--git-dir", str(bare), "rev-parse", "refs/heads/ai/review/latest", cwd=tmp_path).stdout.strip() == original


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_publish_review_missing_ref_fails_and_preserves_staging(tmp_path: Path) -> None:
    source, _bare, _original = new_remote(tmp_path)
    staging = staging_tree(tmp_path)
    result = invoke(
        source,
        staging,
        tmp_path / "citystate",
        "-Refs",
        ".ai/missing.md",
        "-DryRun",
        check=False,
    )
    assert result.returncode != 0
    assert "required refs missing" in result.stdout + result.stderr
    assert staging.exists()


@pytest.mark.skipif(not POWERSHELL, reason="PowerShell is required")
def test_publish_review_normal_push_consumes_staging(tmp_path: Path) -> None:
    source, bare, original = new_remote(tmp_path)
    staging = staging_tree(tmp_path)
    result = invoke(
        source,
        staging,
        tmp_path / "citystate",
        "-Refs",
        ".ai/existing.md",
    )
    value = json.loads(result.stdout)
    assert value["status"] == "published"
    assert not staging.exists()
    published = run("git", "--git-dir", str(bare), "rev-parse", "refs/heads/ai/review/latest", cwd=tmp_path).stdout.strip()
    assert published != original
    body = run("git", "--git-dir", str(bare), "show", f"{published}:.ai/CODEX_REPORTS/report.md", cwd=tmp_path).stdout
    assert body == "report\n"


def test_publish_review_script_keeps_push_and_staging_boundaries_explicit() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "@('add','--')" in text
    assert "@('push',$RemoteName,\"HEAD:$ReviewBranch\")" in text
    assert "push --force" not in text
    assert "git add ." not in text
    assert "publish-review may push only an ai/review/* branch" in text
    assert "staging was preserved" in text
