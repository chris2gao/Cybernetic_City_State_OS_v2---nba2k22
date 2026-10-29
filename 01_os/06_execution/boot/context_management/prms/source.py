"""Immutable, scoped Git source reads. Working-tree bytes never prove a commit."""
from __future__ import annotations

import hashlib
import base64
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


class PRMSError(Exception):
    def __init__(self, status, detail=""):
        self.status, self.detail = status, detail
        super().__init__(f"{status}: {detail}")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    p = PurePosixPath(path)
    if (not path or p.is_absolute() or ".." in p.parts or "\\" in path
            or ":" in path or path != p.as_posix()):
        raise PRMSError("REJECTED", "invalid source path")
    if any(x.lower() in {".env", ".ssh", "credentials", "id_rsa", "id_ed25519"}
           or x.lower().startswith(".env.") or x.lower().endswith((".pem", ".key"))
           for x in p.parts):
        raise PRMSError("REJECTED", "sensitive source path")
    return path


class GitSource:
    def __init__(self, root, commit, repository):
        self.root = Path(root).resolve()
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise PRMSError("REJECTED", "exact 40-character commit required")
        self.commit, self.repository = commit, repository
        actual = self.git("rev-parse", f"{commit}^{{commit}}").decode().strip()
        if actual != commit:
            raise PRMSError("SOURCE_MISSING", "commit mismatch")
        self.tree = {}
        for line in self.git("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not line:
                continue
            meta, path = line.split(b"\t", 1)
            mode, kind, sha = meta.decode().split()
            if kind == "blob":
                self.tree[path.decode("utf-8")] = {"blob": sha, "mode": mode}
        self.reads = []
        self._cache = {}

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True)
        if result.returncode:
            raise PRMSError("SOURCE_MISSING", result.stderr.decode("utf-8", "replace")[:200])
        return result.stdout

    def read(self, path, expected_blob=None):
        safe_path(path)
        entry = self.tree.get(path)
        if entry is None or entry["mode"] == "120000":
            raise PRMSError("SOURCE_MISSING", path)
        if expected_blob is not None and expected_blob != entry["blob"]:
            raise PRMSError("SUMMARY_STALE", path)
        if entry["blob"] not in self._cache:
            self._cache[entry["blob"]] = self.git("cat-file", "blob", entry["blob"])
        data = self._cache[entry["blob"]]
        git_hash = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if git_hash != entry["blob"]:
            raise PRMSError("SOURCE_MISSING", "blob verification failed")
        proof = {"repository": self.repository, "commit": self.commit, "path": path,
                 "blob": git_hash, "sha256": digest(data), "bytes": len(data)}
        self.reads.append(proof)
        return data, proof

    def json(self, path):
        return json.loads(self.read(path)[0])

    def at(self, commit):
        return GitSource(self.root, commit, self.repository)


class GitHubSource(GitSource):
    """Read-only remote source adapter using existing authenticated GitHub CLI."""
    def __init__(self, repository, commit):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise PRMSError("REJECTED", "canonical repository identity required")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise PRMSError("REJECTED", "exact commit required")
        self.repository, self.commit = repository, commit
        self.reads, self._cache = [], {}
        obj = self.api(f"git/trees/{commit}?recursive=1")
        if obj.get("truncated"):
            raise PRMSError("CATALOG_PARTIAL", "GitHub tree response truncated")
        self.tree = {i["path"]: {"blob": i["sha"], "mode": i["mode"]}
                     for i in obj["tree"] if i["type"] == "blob"}

    def api(self, path):
        proc = subprocess.run(["gh", "api", f"repos/{self.repository}/{path}"], capture_output=True)
        if proc.returncode:
            raise PRMSError("SOURCE_MISSING", "GitHub source request failed")
        return json.loads(proc.stdout)

    def at(self, commit):
        return GitHubSource(self.repository, commit)

    def read(self, path, expected_blob=None):
        safe_path(path)
        info = self.tree.get(path)
        if info is None or info["mode"] == "120000":
            raise PRMSError("SOURCE_MISSING", path)
        if expected_blob is not None and info["blob"] != expected_blob:
            raise PRMSError("SUMMARY_STALE", path)
        blob = info["blob"]
        if blob not in self._cache:
            self._cache[blob] = base64.b64decode(self.api("git/blobs/" + blob)["content"])
        data = self._cache[blob]
        if hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != blob:
            raise PRMSError("SOURCE_MISSING", "GitHub blob digest mismatch")
        proof = {"repository": self.repository, "commit": self.commit, "path": path,
                 "blob": blob, "sha256": digest(data), "bytes": len(data)}
        self.reads.append(proof)
        return data, proof
