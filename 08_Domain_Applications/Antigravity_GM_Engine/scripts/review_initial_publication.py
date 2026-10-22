"""Review staged filenames/bytes without displaying candidate credential values."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def git(*arguments):
    result = subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, check=True)
    return result.stdout


def main():
    files = git("diff", "--cached", "--name-only", "-z").decode().strip("\0").split("\0")
    allowed_roots = {"src", "scripts", "config", "docs", "web_gm", "published", "tests"}
    allowed_files = {"README.md", "AGENTS.md", ".gitignore", ".gitattributes", "requirements.txt", "database/schema.sql", "database/templates/save_template.json", "gm_state/README.md"}
    suspicious, sizes = [], {}
    credential_patterns = [rb"github_pat_[A-Za-z0-9_]{25,}", rb"gh[pousr]_[A-Za-z0-9]{25,}", rb"sk-(?:proj-)?[A-Za-z0-9_-]{30,}", rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"]
    for name in files:
        path = Path(name)
        if name not in allowed_files and path.parts[0] not in allowed_roots:
            raise RuntimeError(f"Unexpected staged path: {name}")
        if path.suffix in {".sqlite", ".zip", ".key", ".pem", ".log"} or path.name.startswith(".env") or "__pycache__" in path.parts:
            raise RuntimeError(f"Local/private artifact incorrectly staged: {name}")
        content = git("show", f":{name}")
        sizes[name] = len(content)
        if any(re.search(pattern, content) for pattern in credential_patterns):
            suspicious.append(name)
    if suspicious:
        raise RuntimeError(f"Credential-shaped content detected; values withheld. Paths: {suspicious}")
    print(json.dumps({"staged_files": len(files), "staged_bytes": sum(sizes.values()), "credential_pattern_matches": 0,
                      "json_verification": "DISABLED_TIMESTAMP_ONLY", "largest_file_bytes": max(sizes.values())}, indent=2))


if __name__ == "__main__":
    main()
