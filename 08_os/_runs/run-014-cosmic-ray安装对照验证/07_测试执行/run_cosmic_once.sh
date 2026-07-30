#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
    echo "usage: $0 REPO_ROOT COMMIT_SHA PROJECT_REL OUTPUT_DIR" >&2
    exit 64
fi

repo_root=$1
commit_sha=$2
project_rel=$3
output_dir=$4
cosmic_venv=/home/gk/.venvs/core-cosmic-ray-8.4.6
pytest_python=/home/gk/.venvs/core-mutmut-3.6.0/bin/python

case "$repo_root" in
    /mnt/*)
        echo "repository on /mnt is forbidden for mutation execution" >&2
        exit 65
        ;;
    /*)
        ;;
    *)
        echo "repository root must be absolute" >&2
        exit 65
        ;;
esac

if [[ -n "$(git -C "$repo_root" status --porcelain)" ]]; then
    echo "repository must be clean" >&2
    exit 66
fi

git -C "$repo_root" cat-file -e "${commit_sha}^{commit}"
case "$project_rel" in
    /*|*".."*)
        echo "project path must be a contained relative path" >&2
        exit 65
        ;;
esac

if [[ ! -x "$cosmic_venv/bin/cosmic-ray" ]]; then
    echo "Cosmic Ray executable is missing" >&2
    exit 67
fi
if [[ "$("$cosmic_venv/bin/cosmic-ray" --version)" != "cosmic-ray, version 8.4.6" ]]; then
    echo "Cosmic Ray version mismatch" >&2
    exit 67
fi
if [[ ! -x "$pytest_python" ]]; then
    echo "pytest interpreter is missing" >&2
    exit 67
fi

temp_root=$(mktemp -d /tmp/citystate-cosmic-ray.XXXXXX)
cleanup() {
    rm -rf -- "$temp_root"
}
trap cleanup EXIT

mkdir -p -- "$output_dir"
git -C "$repo_root" archive "$commit_sha" | tar -x -C "$temp_root"
project_dir="$temp_root/$project_rel"
if [[ ! -d "$project_dir" ]]; then
    echo "archived project path is missing" >&2
    exit 68
fi

cd "$project_dir"
source_path=calibration_pkg/logic.py
source_before=$(sha256sum "$source_path" | cut -d " " -f 1)

baseline_started_ms=$(date +%s%3N)
timeout 120s "$pytest_python" -m pytest -q -x tests \
    >"$output_dir/baseline.stdout.txt" \
    2>"$output_dir/baseline.stderr.txt"
baseline_finished_ms=$(date +%s%3N)

init_started_ms=$(date +%s%3N)
timeout 120s "$cosmic_venv/bin/cosmic-ray" init \
    cosmic-ray.toml session.sqlite \
    >"$output_dir/init.stdout.txt" \
    2>"$output_dir/init.stderr.txt"
init_finished_ms=$(date +%s%3N)

exec_started_ms=$(date +%s%3N)
timeout 600s "$cosmic_venv/bin/cosmic-ray" exec \
    cosmic-ray.toml session.sqlite \
    >"$output_dir/exec.stdout.txt" \
    2>"$output_dir/exec.stderr.txt"
exec_finished_ms=$(date +%s%3N)

report_started_ms=$(date +%s%3N)
"$cosmic_venv/bin/cosmic-ray" dump session.sqlite \
    >"$output_dir/session.dump.jsonl"
"$cosmic_venv/bin/cr-report" --show-diff --all-mutations session.sqlite \
    >"$output_dir/report.txt"
report_finished_ms=$(date +%s%3N)

cp -- session.sqlite "$output_dir/session.sqlite"
source_after=$(sha256sum "$source_path" | cut -d " " -f 1)
session_sha256=$(sha256sum "$output_dir/session.sqlite" | cut -d " " -f 1)
session_bytes=$(stat -c %s "$output_dir/session.sqlite")

cat >"$output_dir/timing.env" <<EOF
baseline_ms=$((baseline_finished_ms - baseline_started_ms))
init_ms=$((init_finished_ms - init_started_ms))
exec_ms=$((exec_finished_ms - exec_started_ms))
report_ms=$((report_finished_ms - report_started_ms))
total_ms=$((report_finished_ms - baseline_started_ms))
source_before_sha256=$source_before
source_after_sha256=$source_after
session_sha256=$session_sha256
session_bytes=$session_bytes
commit_sha=$commit_sha
EOF

if [[ "$source_before" != "$source_after" ]]; then
    echo "Cosmic Ray did not restore the archived source" >&2
    exit 69
fi

printf 'output_dir=%s\n' "$output_dir"
printf 'session_sha256=%s\n' "$session_sha256"
printf 'session_bytes=%s\n' "$session_bytes"
