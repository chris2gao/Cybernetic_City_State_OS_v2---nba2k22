"""Read exact historical research input or locate verified local archive data."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


INDEX = Path(__file__).with_name("source_index.json")


def digest_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_bytes(row):
    result = subprocess.run(
        ["git", "-C", str(INDEX.parent), "show", f"{row['commit']}:{row['path']}"],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(f"Public source unavailable at {row['commit']}:{row['path']}. Fetch the migration branch history.")
    content = result.stdout
    git_blob = hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()
    if (len(content), git_blob, hashlib.sha256(content).hexdigest()) != (
        row["size_bytes"], row["blob"], row["sha256"]
    ):
        raise ValueError(f"Public source integrity mismatch for {row['path']}")
    return content


def archive_path(root, row):
    relative = PurePosixPath(row["archive_key"], row["path"])
    if relative.is_absolute() or ".." in relative.parts or "\\" in str(relative) or ":" in str(relative):
        raise ValueError(f"Unsafe archive index path {relative}")
    root = root.resolve()
    path = root.joinpath(*relative.parts).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Archive path escapes the root: {relative}")
    if not path.is_file():
        raise ValueError(f"Offline archive data missing: {relative}")
    if path.stat().st_size != row["size_bytes"] or digest_file(path) != row["sha256"]:
        raise ValueError(f"Offline archive integrity mismatch: {relative}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    source = commands.add_parser("source", help="emit verified public source bytes")
    source.add_argument("name")
    data = commands.add_parser("data", help="print the path to a verified offline file")
    data.add_argument("git_blob_sha1")
    data.add_argument("--archive-root", required=True, type=Path)
    args = parser.parse_args()
    index = json.loads(INDEX.read_bytes())
    try:
        if args.command == "source":
            sys.stdout.buffer.write(source_bytes(index["source"][args.name]))
        else:
            print(archive_path(args.archive_root, index["archive_by_git_blob_sha1"][args.git_blob_sha1]))
    except KeyError as error:
        parser.exit(2, f"Unknown historical source key: {error}\n")
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
