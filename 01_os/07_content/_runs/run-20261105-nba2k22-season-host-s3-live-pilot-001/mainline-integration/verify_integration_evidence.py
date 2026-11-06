"""Verify the mainline snapshot against the immutable pilot (no live access)."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PureWindowsPath

BASE = "66f8f73f1a91597f4562b834c2acad332ad9de5b"
SOURCE = "58512372e223845936478ec2a6999093bb5c02e7"
RUN = "01_os/07_content/_runs/run-20261105-nba2k22-season-host-s3-live-pilot-001"
ROOT = Path(__file__).resolve().parents[5]
ENGINE = "08_Domain_Applications/Antigravity_GM_Engine/"
CODE = {
    ENGINE + "research/rea_native_control/season_cycle_host.py",
    ENGINE + "research/rea_native_control/tests/test_season_cycle_host.py",
    ENGINE + "world_data_prototype/calendar_sim_orchestrator.py",
}
CODE_CORRECTIONS = {
    "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/season_cycle_host.py": "87ef31465a8257094068db5c5fd3d244b044903f",
    "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tests/test_season_cycle_host.py": "b36246717c513ffa183957d1ff9fc603d5769dfe",
    "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/calendar_sim_orchestrator.py": "dd3b05f46a6c501e9c63cb54cc54058b335d1041",
}
PATH = re.compile(rb'(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.-]+\\)[^"\r\n<>|?*]+')
SECRET_SIGNATURE = re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----')


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def names(base, head):
    return set(git("diff", "--name-only", "-z", base, head).decode().rstrip("\0").split("\0"))


def portable(data):
    def replace(match):
        path = match.group().decode().replace("\\\\", "\\")
        return ("<LOCAL_PATH>/" + PureWindowsPath(path).name).encode()
    return PATH.sub(replace, data)


def portable_pilot_initializer(data):
    assert data.count(b"    native = NATIVE_ROOT / args.declared_loaded_filename") == 1
    data, count = re.subn(rb'^NATIVE_ROOT = Path\("[^"\r\n]+"\)\r?\n', b"", data, flags=re.M)
    assert count == 1
    data = data.replace(b"import json", b"import json\nimport os", 1)
    return data.replace(
        b"    native = NATIVE_ROOT / args.declared_loaded_filename",
        b'    native_root = Path(os.environ["NBA2K22_S3_NATIVE_SAVE_ROOT"])\n'
        b'    if not native_root.is_absolute():\n'
        b'        raise ValueError("NBA2K22_S3_NATIVE_SAVE_ROOT must be an absolute path")\n'
        b'    native = native_root / args.declared_loaded_filename',
        1,
    )


def main():
    if sys.argv[1:2] == ["--pytest"]:
        # An exclusive base avoids pytest's shared Windows junction cleanup.
        with tempfile.TemporaryDirectory(prefix="nba2k22-s3-verify-") as scratch:
            return subprocess.call([sys.executable, "-B", "-X", "utf8", "-m", "pytest",
                                    "--basetemp", str(Path(scratch) / "pytest"), *sys.argv[2:]])
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prepare-redactions", action="store_true")
    args = p.parse_args()
    source_paths = names(BASE, SOURCE)
    assert len(source_paths) == 51 and {x for x in source_paths if not x.startswith(RUN + "/")} == CODE
    redacted = {}
    head = git("rev-parse", "HEAD").decode().strip()
    for path in sorted(source_paths):
        source = git("show", f"{SOURCE}:{path}")
        if path in CODE:
            if not args.prepare_redactions:
                if path in CODE_CORRECTIONS:
                    assert git("rev-parse", f"{head}:{path}").decode().strip() == CODE_CORRECTIONS[path], path
                else:
                    assert git("show", f"{head}:{path}") == source, path
            continue
        assert not SECRET_SIGNATURE.search(source) and b"\0" not in source and len(source) < 64_000, path
        target = portable(source) if "/receipts/" in path else (
            portable_pilot_initializer(source) if path == RUN + "/initialize_pilot.py" else source
        )
        assert not PATH.search(target), path
        if target != source:
            redacted[path.removeprefix(RUN + "/")] = {
                "source_sha256": hashlib.sha256(source).hexdigest(),
                "portable_sha256": hashlib.sha256(target).hexdigest(),
            }
            if args.prepare_redactions:
                (ROOT / path).write_bytes(target)
        if not args.prepare_redactions:
            assert git("show", f"{head}:{path}") == target, path
    manifest = Path(__file__).with_name("redactions.json")
    if args.prepare_redactions:
        manifest.write_bytes((json.dumps(redacted, indent=2) + "\n").encode())
    else:
        assert json.loads(manifest.read_bytes()) == redacted
        candidate_paths = names(BASE, head)
        assert candidate_paths >= source_paths
        assert all(x.startswith(RUN + "/mainline-integration/") for x in candidate_paths - source_paths)
        git("diff", "--check", BASE, head)
        audit = json.loads(git("show", f"{head}:{RUN}/receipts/pilot-closeout-audit.json"))
        assert [r["new_finals"] for r in audit["rounds"]] == [53, 57, 55, 60]
        assert sum(r["overtime_games"] for r in audit["rounds"]) == 10
        assert (audit["new_finals"], audit["final_games"], audit["outbox_intents"]) == (225, 463, 0)
        assert audit["native_write_path"] == "NOT_EXERCISED_ZERO_INTENTS"
    print(f"{len(source_paths)} fixed source files; {len(redacted)} sanitized pilot files; "
          "3 pinned S3 integration code and regression blobs")


if __name__ == "__main__":
    raise SystemExit(main())
