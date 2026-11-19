"""Real local Git three-way inheritance test; no real domain ref is changed."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[6]
BASE = "446ca66ad48831f5fcdb1af18f37d07619e048c4"


def test_core_candidate_merge_preserves_domain_owned_08_and_no_role_state(tmp_path):
    candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    domain = tmp_path / "domain"
    subprocess.run(["git", "clone", "--shared", "--no-checkout", str(ROOT), str(domain)], check=True, capture_output=True)
    def git(*args):
        result = subprocess.run(["git", "-c", "core.longpaths=true", *args], cwd=domain, capture_output=True)
        assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
        return result.stdout
    git("checkout", "-b", "fixture-domain", BASE)
    # Both domain-owned roots (08 content, 09 loading configuration) survive a core merge.
    paths = [domain / "08_Domain_Applications/domain.yml", domain / "09_Domain_Global_Mechanisms/domain_mechanisms.yml"]
    contents = b"domain_id: fixture\nentries: []\nfixture_domain_content: retained\n"
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    git("add", "--", "08_Domain_Applications/", "09_Domain_Global_Mechanisms/")
    git("-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "domain-owned fixture")
    git("-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "merge", "--no-edit", candidate)
    assert all(path.read_bytes() == contents for path in paths)
    tree = [p.decode() for p in git("ls-tree", "-r", "--name-only", "HEAD").splitlines()]
    assert not any(p.startswith(("roles/", "publications/", "state/roles/")) for p in tree)
    assert git("show", "HEAD:CORE_MANIFEST.yml") == git("show", candidate + ":CORE_MANIFEST.yml")
