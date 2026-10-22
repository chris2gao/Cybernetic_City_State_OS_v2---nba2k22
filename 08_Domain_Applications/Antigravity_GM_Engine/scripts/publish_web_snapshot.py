"""Publish a player-triggered data bundle; freshness is shown by timestamps.

Normal pushes only. No force pushes, credentials, external decision execution,
or unrelated staged/source changes are accepted by this data-only publisher.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from snapshot_integrity import write_json_atomic
from save_context import validate_save_id


def command(args, check=True):
    result = subprocess.run(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]} {args[1]} failed: {result.stderr[-1200:]}")
    return result


def commit_data(message):
    changed = command(["git", "diff", "--cached", "--quiet"], check=False)
    if changed.returncode == 1:
        command(["git", "commit", "-m", message])
    elif changed.returncode:
        raise RuntimeError("Could not inspect staged data changes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", type=validate_save_id, required=True)
    args = parser.parse_args()
    from gm_state_io.lifecycle import operation
    with operation(args.save_id,'publish'):
        return publish(args)


def publish(args):
    pointer_path = f"published/saves/{args.save_id}/latest.json"
    pointer = json.loads((ROOT / pointer_path).read_text(encoding="utf-8"))
    directory = (ROOT / "published" / pointer["batch_path"]).resolve()
    if not directory.is_relative_to((ROOT / "published/saves" / args.save_id).resolve()):
        raise RuntimeError("Data path is outside the selected career")
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get('player_potential_mask',{}).get('potential_mask_version') != 'potential_v1':
        raise RuntimeError('UNMASKED_HISTORICAL_GM_BATCH_REPUBLISH_DISABLED_REQUIRES_SEPARATE_AUTHORIZED_CONVERSION')
    config = json.loads((ROOT / "config/github_sync.json").read_text(encoding="utf-8"))
    repository, branch = config["repository"], config["branch"]
    remote = json.loads(command(["gh", "repo", "view", repository, "--json", "nameWithOwner,isPrivate,url"]).stdout)
    required_visibility = config.get('visibility_required', 'private')
    if required_visibility not in ('private', 'public'):
        raise RuntimeError('Invalid configured repository visibility')
    actual_visibility = 'private' if remote['isPrivate'] else 'public'
    if remote["nameWithOwner"].casefold() != repository.casefold() or actual_visibility != required_visibility:
        raise RuntimeError("Destination does not match the configured repository and visibility")
    origin = command(["git", "remote", "get-url", "origin"]).stdout.strip().removesuffix(".git")
    if origin not in (f"git@github.com:{repository}", f"https://github.com/{repository}"):
        raise RuntimeError("Git origin does not match the configured repository")
    if command(["git", "branch", "--show-current"]).stdout.strip() != branch:
        raise RuntimeError("Data publication must run from the configured branch")
    allowed = (f"published/saves/{args.save_id}/", "published/index.json")
    def allowed_path(path):
        return path == allowed[1] or path.startswith(allowed[0])
    staged = command(["git", "diff", "--cached", "--name-only"]).stdout.splitlines()
    if any(not allowed_path(path) for path in staged):
        raise RuntimeError("Unrelated files are staged; data publisher will not commit them")
    dirty_source = command(["git", "diff", "--name-only", "--", "src", "scripts", "config"]).stdout.splitlines()
    if dirty_source:
        raise RuntimeError("Capture/export source or configuration differs from the committed version")
    command(["git", "fetch", "origin", branch])
    command(["git", "merge-base", "--is-ancestor", f"origin/{branch}", "HEAD"])
    unpublished = command(["git", "diff", "--name-only", f"origin/{branch}..HEAD"]).stdout.splitlines()
    if any(not allowed_path(path) for path in unpublished):
        raise RuntimeError("Unpublished source changes require separate review before a data-only push")
    pending = command(["git", "diff", "--name-only", "--", "published"]).stdout.splitlines()
    pending += command(["git", "ls-files", "--others", "--exclude-standard", "--", "published"]).stdout.splitlines()
    if any(not allowed_path(path) for path in pending):
        raise RuntimeError("Another career or reading-protocol update is pending; refusing a mixed publication")
    command(["git", "add", "--", allowed[0].rstrip("/"), allowed[1]])
    commit_data(f"data: publish {manifest['batch_id']}")
    command(["git", "push", "origin", f"HEAD:{branch}"])
    commit = command(["git", "rev-parse", "HEAD"]).stdout.strip()
    archive = ROOT / "_exports/archives" / manifest["archive"]["filename"]
    tag = manifest["archive"]["release_tag"]
    release = command(["gh", "release", "view", tag, "--repo", repository, "--json", "url,assets"], check=False)
    if release.returncode:
        with tempfile.TemporaryDirectory(prefix="gm_release_notes_") as temporary:
            notes = Path(temporary) / "notes.md"
            notes.write_text(f"Player-triggered capture for {manifest['save_id']} at game date {manifest['context'].get('game_date')}.\n\n"
                             f"Snapshot: `{manifest['snapshot_id']}`\nData updated at (UTC): `{manifest['data_updated_at']}`\n\n"
                             "SQLite backups are for reproducibility. Web GMs read the small JSON files under published/. Unobserved fields remain null.\n", encoding="utf-8")
            command(["gh", "release", "create", tag, str(archive), "--repo", repository, "--target", commit,
                     "--title", f"Data {manifest['context'].get('game_date')} / {manifest['batch_id']}", "--notes-file", str(notes)])
    elif not any(asset["name"] == archive.name for asset in json.loads(release.stdout)["assets"]):
        # Resume a release created before an interrupted attachment upload.
        command(["gh", "release", "upload", tag, str(archive), "--repo", repository])
    # Record success only after the database upload command has succeeded.
    # No JSON hashes, field comparisons or download-and-compare step is run.
    uploaded_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    pointer.update({"data_updated_at": manifest["data_updated_at"], "uploaded_at": uploaded_at,
                    "upload_status": "UPLOADED", "sync_mode": "TIMESTAMP_ONLY",
                    "archive_url": f"https://github.com/{repository}/releases/download/{tag}/{archive.name}"})
    write_json_atomic(str(ROOT / pointer_path), pointer)
    index_path = ROOT / "published/index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["careers"][args.save_id].update({"data_updated_at": manifest["data_updated_at"],
                                         "uploaded_at": uploaded_at})
    write_json_atomic(str(index_path), index)
    command(["git", "add", "--", pointer_path, "published/index.json"])
    commit_data(f"data: record upload time for {manifest['batch_id']}")
    command(["git", "push", "origin", f"HEAD:{branch}"])
    commit = command(["git", "rev-parse", "HEAD"]).stdout.strip()
    receipt = {"repository": repository, "visibility": actual_visibility, "commit": commit, "batch_id": manifest["batch_id"],
               "game_date": manifest["context"].get("game_date"), "data_updated_at": manifest["data_updated_at"],
               "uploaded_at": uploaded_at, "upload_status": "UPLOADED", "sync_mode": "TIMESTAMP_ONLY",
               "latest_url": f"https://github.com/{repository}/blob/{branch}/{pointer_path}",
               "entry_url": f"https://github.com/{repository}/blob/{commit}/{pointer_path}",
               "release_url": f"https://github.com/{repository}/releases/tag/{tag}",
               "chatgpt_web_connection_verified": False}
    write_json_atomic(str(ROOT / "_exports/receipts" / f"{manifest['batch_id']}.json"), receipt)
    print(json.dumps(receipt, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
