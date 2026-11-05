"""Audit integration scope and pinned sources without opening the game."""
from pathlib import Path
import hashlib
import json
import posixpath
import subprocess


BASE = "dfa08af8bb6e4abf1cd8ad304f47b096ecc38167"
OLD = "400c998be89ab2c8b902e50667af500f0fda178e"
HOST = "1fc2965ae10ef2a34abb37d800d86cd548f24aeb"
DOMAIN = "08_Domain_Applications/Antigravity_GM_Engine"
PROFILE = f"{DOMAIN}/research/rea_core_profile"
ARCHIVE = f"{DOMAIN}/research/history_source_resolution"
HISTORICAL_RUN = "01_os/07_content/_runs/run-20261029-nba-rea-core-adapter-001"


def git(*args):
    return subprocess.check_output(["git", *args])


def obj(ref, path):
    return git("rev-parse", f"{ref}:{path}").decode().strip()


def blob(ref, path):
    return git("show", f"{ref}:{path}")


def ancestor(before, after, expected):
    result = subprocess.run(["git", "merge-base", "--is-ancestor", before, after], check=False)
    assert result.returncode == expected, (before, after, result.returncode)


head = git("rev-parse", "HEAD").decode().strip()
ancestor(BASE, head, 0)
ancestor(OLD, head, 0)
ancestor(HOST, head, 1)
for path in (f"{PROFILE}/bridge.py", f"{PROFILE}/profile.json", f"{PROFILE}/test_bridge.py", HISTORICAL_RUN):
    assert obj(OLD, path) == obj(head, path), path

assert obj(BASE, ARCHIVE) == obj(head, ARCHIVE)
archive_index = json.loads(blob(head, f"{ARCHIVE}/source_index.json"))
archive_blobs = set(archive_index["archive_by_git_blob_sha1"])
introduced = {line.split(b" ", 1)[0].decode() for line in git("rev-list", "--objects", head, f"^{BASE}").splitlines()}
assert len(archive_blobs) == 238 and not (archive_blobs & introduced)

index = blob(head, f"{DOMAIN}/PROJECT_INDEX.md").decode()
registry = json.loads(blob(head, f"{DOMAIN}/docs/development/PROJECT_MODULE_REGISTRY_V2.json"))
modules = registry["modules"]
assert [row["id"] for row in modules] == [f"P{number:02}" for number in range(13)]
assert registry["module_count"] == len(modules)
entries = 0
for row in modules:
    assert f"| {row['id']} | {row['name']} | `{row['status']}` |" in index, row["id"]
    for entry in row["docs"] + row["artifacts"]:
        obj(head, posixpath.normpath(f"{DOMAIN}/{entry}"))
        entries += 1
    for source in row.get("external_source_refs", []):
        obj(source["commit"], posixpath.normpath(f"{DOMAIN}/{source['path']}"))

profile = json.loads(blob(head, f"{PROFILE}/profile.json"))
research = profile["native_research"]
fixed = {}
for name in ("action_catalog", "binding_catalog", "read_catalog", "effect_evidence"):
    path = f"{research['directory']}/{research[name]}"
    fixed[name] = {"git_blob": obj(research["commit"], path),
                   "sha256": hashlib.sha256(blob(research["commit"], path)).hexdigest()}
executor = profile["native_executor_candidate"]
for key in ("facade", "bulk", "outbox"):
    path = f"{research['directory']}/{executor[key]}"
    assert obj(executor["commit"], path) == obj(BASE, path) == obj(head, path), path

print(json.dumps({"status": "PASS", "nba_head": head, "base": BASE, "historical_pr27": OLD,
                  "module_count": len(modules), "current_entry_count": entries, "pr18_fixed_sources": fixed,
                  "pr26_current_executor_blob_equivalence": True, "pr28_tree_unchanged": True,
                  "archive_blob_candidates_excluded": len(archive_blobs), "original_host_is_ancestor": False},
                 indent=2))
