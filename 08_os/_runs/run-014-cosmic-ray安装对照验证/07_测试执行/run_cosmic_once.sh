#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 8 ]]; then
    echo "usage: $0 REPO_ROOT COMMIT_SHA PROJECT_REL OUTPUT_DIR [SOURCE_REL] [TEST_PATH] [CONFIG_REL] [CANONICAL_SOURCE_REL]" >&2
    exit 64
fi

repo_root=$1
commit_sha=$2
project_rel=$3
output_dir=$4
source_path=${5:-calibration_pkg/logic.py}
test_path=${6:-tests}
config_rel=${7:-}
canonical_source_rel=${8:-}
cosmic_venv=${COSMIC_RAY_VENV:?COSMIC_RAY_VENV is required}
pytest_python="$cosmic_venv/bin/python"

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
if [[ -n "$config_rel" ]]; then
    cp -- "$temp_root/$config_rel" "$project_dir/cosmic-ray.toml"
    sed -i "s|\${COSMIC_RAY_VENV}|$cosmic_venv|g" "$project_dir/cosmic-ray.toml"
fi
if [[ -n "$canonical_source_rel" ]]; then
    mkdir -p -- "$(dirname "$project_dir/$source_path")"
    cp -- "$temp_root/$canonical_source_rel" "$project_dir/$source_path"
fi

cd "$project_dir"
source_before=$(sha256sum "$source_path" | cut -d " " -f 1)

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/baseline.time" \
timeout 120s "$pytest_python" -m pytest -q -x "$test_path" \
    >"$output_dir/baseline.stdout.txt" \
    2>"$output_dir/baseline.stderr.txt"

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/init.time" \
timeout 120s "$cosmic_venv/bin/cosmic-ray" init \
    cosmic-ray.toml session.sqlite \
    >"$output_dir/init.stdout.txt" \
    2>"$output_dir/init.stderr.txt"

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/exec.time" \
timeout 600s "$cosmic_venv/bin/cosmic-ray" exec \
    cosmic-ray.toml session.sqlite \
    >"$output_dir/exec.stdout.txt" \
    2>"$output_dir/exec.stderr.txt"

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/dump.time" \
"$cosmic_venv/bin/cosmic-ray" dump session.sqlite \
    >"$output_dir/session.dump.jsonl"
/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/report.time" \
"$cosmic_venv/bin/cr-report" --show-diff --all-mutations session.sqlite \
    >"$output_dir/report.txt"

cp -- session.sqlite "$output_dir/session.sqlite"
source_after=$(sha256sum "$source_path" | cut -d " " -f 1)
session_sha256=$(sha256sum "$output_dir/session.sqlite" | cut -d " " -f 1)
session_bytes=$(stat -c %s "$output_dir/session.sqlite")

cat >"$output_dir/receipt.env" <<EOF
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
