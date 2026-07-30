#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 7 ]]; then
    echo "usage: $0 REPO_ROOT COMMIT_SHA PROJECT_REL OUTPUT_DIR [SOURCE_REL] [TEST_PATH] [CANONICAL_SOURCE_REL]" >&2
    exit 64
fi

repo_root=$1
commit_sha=$2
project_rel=$3
output_dir=$4
source_path=${5:-calibration_pkg/logic.py}
test_path=${6:-tests}
canonical_source_rel=${7:-}
mutmut_venv=/home/gk/.venvs/core-mutmut-3.6.0

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

if [[ ! -x "$mutmut_venv/bin/mutmut" ]]; then
    echo "mutmut executable is missing" >&2
    exit 67
fi

temp_root=$(mktemp -d /tmp/citystate-mutmut-comparison.XXXXXX)
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
if [[ -n "$canonical_source_rel" ]]; then
    mkdir -p -- "$(dirname "$project_dir/$source_path")"
    cp -- "$temp_root/$canonical_source_rel" "$project_dir/$source_path"
fi

cd "$project_dir"
source_before=$(sha256sum "$source_path" | cut -d " " -f 1)

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/baseline.time" \
timeout 120s "$mutmut_venv/bin/python" -m pytest -q -x "$test_path" \
    >"$output_dir/baseline.stdout.txt" \
    2>"$output_dir/baseline.stderr.txt"

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/exec.time" \
timeout 600s "$mutmut_venv/bin/mutmut" run --max-children 1 \
    >"$output_dir/exec.stdout.txt" \
    2>"$output_dir/exec.stderr.txt"

/usr/bin/time -f "wall_seconds=%e" -o "$output_dir/report.time" \
"$mutmut_venv/bin/mutmut" results --all true \
    >"$output_dir/results.txt"

if [[ "${CAPTURE_ALL_MUTANTS:-1}" == "1" ]]; then
    while IFS= read -r mutant_name; do
        printf '=== %s ===\n' "$mutant_name"
        "$mutmut_venv/bin/mutmut" show "$mutant_name"
    done < <(
        sed -n 's/^[[:space:]]*\([^:]*\):.*/\1/p' "$output_dir/results.txt"
    ) >"$output_dir/all-mutants.txt"
else
    printf 'not_captured_in_repeat_run\n' >"$output_dir/all-mutants.txt"
fi

if [[ -f mutants/.mutmut-cache ]]; then
    cp -- mutants/.mutmut-cache "$output_dir/mutmut-cache.sqlite"
fi
mutant_source="mutants/$source_path"
if [[ -f "$mutant_source" ]]; then
    cp -- "$mutant_source" "$output_dir/mutants-source.py"
fi
if [[ -f "${mutant_source}.meta" ]]; then
    cp -- "${mutant_source}.meta" "$output_dir/mutants-source.py.meta"
fi
find mutants -maxdepth 2 -type f -printf '%P\t%s\n' \
    | sort >"$output_dir/mutants-files.tsv"

source_after=$(sha256sum "$source_path" | cut -d " " -f 1)
mutants_bytes=$(du -sb mutants | cut -f 1)
mutants_files=$(find mutants -type f | wc -l)
cat >"$output_dir/receipt.env" <<EOF
source_before_sha256=$source_before
source_after_sha256=$source_after
mutants_bytes=$mutants_bytes
mutants_files=$mutants_files
commit_sha=$commit_sha
EOF

if [[ "$source_before" != "$source_after" ]]; then
    echo "mutmut changed the archived source" >&2
    exit 69
fi

printf 'output_dir=%s\n' "$output_dir"
printf 'mutants_bytes=%s\n' "$mutants_bytes"
printf 'mutants_files=%s\n' "$mutants_files"
