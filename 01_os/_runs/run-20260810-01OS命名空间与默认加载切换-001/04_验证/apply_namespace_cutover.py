"""Apply the Human-authorized literal namespace replacement and final root rename."""
from __future__ import annotations

import subprocess
from pathlib import Path


OLD = "08" + "_os"
NEW = "01" + "_os"


def git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout


def main() -> int:
    repo = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip()).resolve()
    old_root = repo / OLD
    new_root = repo / NEW
    if not old_root.is_dir() or new_root.exists():
        raise RuntimeError("namespace roots are not in the required pre-cutover state")

    tracked = [
        item.decode("utf-8", "surrogateescape")
        for item in git(repo, "ls-files", "-z").split(b"\0")
        if item
    ]
    old_bytes = OLD.encode("ascii")
    new_bytes = NEW.encode("ascii")
    changed_files = 0
    replacements = 0
    for relative in tracked:
        path = repo / relative
        data = path.read_bytes()
        count = data.count(old_bytes)
        if count:
            path.write_bytes(data.replace(old_bytes, new_bytes))
            changed_files += 1
            replacements += count

    # Rename any tracked leaf name containing the namespace token. The root
    # directory rename remains the final mutation as required by the Human.
    renamed_inner_paths = 0
    for relative in sorted(tracked, key=lambda value: (value.count("/"), len(value)), reverse=True):
        if not relative.startswith(OLD + "/"):
            continue
        inside = relative[len(OLD) + 1 :]
        if OLD not in inside:
            continue
        source = old_root / inside
        if not source.exists():
            continue
        target = old_root / inside.replace(OLD, NEW)
        if target.exists():
            raise RuntimeError(f"inner rename target already exists: {target.relative_to(repo)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
        renamed_inner_paths += 1

    old_root.rename(new_root)

    residual_content: list[str] = []
    missing_targets: list[str] = []
    for relative in tracked:
        mapped = relative.replace(OLD, NEW)
        path = repo / mapped
        if not path.is_file():
            missing_targets.append(mapped)
        elif old_bytes in path.read_bytes():
            residual_content.append(mapped)
    if residual_content or missing_targets or old_root.exists() or not new_root.is_dir():
        raise RuntimeError(
            "cutover closure failed: "
            f"residual_content={len(residual_content)} missing_targets={len(missing_targets)}"
        )

    print(
        "namespace_cutover_ok "
        f"tracked={len(tracked)} changed_files={changed_files} replacements={replacements} "
        f"renamed_inner_paths={renamed_inner_paths} final_root={NEW}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
