from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource
from catalog import discover_g1


def test_unregistered_mechanism_and_nonreadme_source_are_explicit(tmp_path):
    mechanism = tmp_path / "01_os/03_mechanisms/new_mechanism"
    registry = tmp_path / "01_os/05_registry"
    mechanism.mkdir(parents=True)
    registry.mkdir(parents=True)
    (mechanism / "README.md").write_text("# New mechanism\n\nUnregistered fixture.\n")
    (mechanism / "contract.yml").write_text("schema_version: fixture.v1\n")
    (registry / "fixture.yml").write_text("entries:\n  - path: 01_os/03_mechanisms/registered_but_missing/README.md\n")
    for args in [["init", "-q"], ["add", "--", "01_os/"],
                 ["-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "inconsistent registry fixture"]]:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path).decode().strip()
    catalog = discover_g1(GitSource(tmp_path, sha, "fixture/core"))
    assert catalog["unregistered_candidate_paths"] == ["01_os/03_mechanisms/new_mechanism/README.md"]
    assert "01_os/03_mechanisms/new_mechanism/contract.yml" in catalog["unregistered_source_paths"]
    assert catalog["entries"][0]["status"] == "CANDIDATE_UNREGISTERED"
    assert not catalog["entries"][0]["action_authorized"]
    assert catalog["missing_references"][0]["path"].endswith("registered_but_missing/README.md")
    assert catalog["registry_consistency"] == "PARTIAL"
