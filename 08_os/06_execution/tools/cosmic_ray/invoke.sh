#!/usr/bin/env bash
set -euo pipefail

readonly EXPECTED_COSMIC_RAY_VERSION="8.4.6"
readonly EXPECTED_PYTHON_VERSION="3.14.4"
readonly EXPECTED_PYTEST_VERSION="9.1.1"
readonly SUMMARY_REL="08_os/06_execution/tools/cosmic_ray/summarize.py"

fail() {
    local exit_code="$1"
    shift
    printf 'cosmic-ray wrapper: %s\n' "$*" >&2
    exit "$exit_code"
}

require_value() {
    local option="$1"
    local value="${2:-}"
    [[ -n "$value" ]] || fail 64 "missing value for ${option}"
}

read_include_system_site_packages() {
    local cfg_path="$1"
    awk '
        function trim(value) {
            sub(/^[[:space:]]+/, "", value)
            sub(/[[:space:]]+$/, "", value)
            return value
        }
        {
            line = $0
            sub(/\r$/, "", line)
            separator = index(line, "=")
            if (separator == 0) next
            key = tolower(trim(substr(line, 1, separator - 1)))
            value = tolower(trim(substr(line, separator + 1)))
            if (key == "include-system-site-packages") {
                count += 1
                selected = value
            }
        }
        END {
            if (count != 1 || (selected != "true" && selected != "false")) exit 2
            print selected
        }
    ' "$cfg_path" 2>/dev/null
}

repo_root=""
venv_path=""
project_dir=""
target_path=""
test_path=""
receipt_dir=""
cosmic_ray_executable=""
cr_report_executable=""
timeout_seconds="5"
max_mutations="500"
declare -a allowed_targets=()

while (($# > 0)); do
    case "$1" in
        --repo-root)
            require_value "$1" "${2:-}"
            repo_root="$2"
            shift 2
            ;;
        --venv)
            require_value "$1" "${2:-}"
            venv_path="$2"
            shift 2
            ;;
        --project-dir)
            require_value "$1" "${2:-}"
            project_dir="$2"
            shift 2
            ;;
        --target)
            require_value "$1" "${2:-}"
            target_path="$2"
            shift 2
            ;;
        --allow-target)
            require_value "$1" "${2:-}"
            allowed_targets+=("$2")
            shift 2
            ;;
        --test-path)
            require_value "$1" "${2:-}"
            test_path="$2"
            shift 2
            ;;
        --receipt-dir)
            require_value "$1" "${2:-}"
            receipt_dir="$2"
            shift 2
            ;;
        --cosmic-ray-executable)
            require_value "$1" "${2:-}"
            cosmic_ray_executable="$2"
            shift 2
            ;;
        --cr-report-executable)
            require_value "$1" "${2:-}"
            cr_report_executable="$2"
            shift 2
            ;;
        --timeout-seconds)
            require_value "$1" "${2:-}"
            timeout_seconds="$2"
            shift 2
            ;;
        --max-mutations)
            require_value "$1" "${2:-}"
            max_mutations="$2"
            shift 2
            ;;
        --help)
            printf '%s\n' \
                'Usage: invoke.sh --repo-root PATH --venv PATH --project-dir RELPATH' \
                '                 --target RELPATH --allow-target RELPATH' \
                '                 --test-path PROJECT_RELPATH --receipt-dir ABSOLUTE_PATH' \
                '                 [--cosmic-ray-executable PATH] [--cr-report-executable PATH]' \
                '                 [--timeout-seconds N] [--max-mutations N]'
            exit 0
            ;;
        *)
            fail 64 "unknown option: $1"
            ;;
    esac
done

[[ -n "$repo_root" ]] || fail 64 "--repo-root is required"
[[ -n "$venv_path" ]] || fail 64 "--venv is required"
[[ -n "$project_dir" ]] || fail 64 "--project-dir is required"
[[ -n "$target_path" ]] || fail 64 "--target is required"
[[ -n "$test_path" ]] || fail 64 "--test-path is required"
[[ -n "$receipt_dir" ]] || fail 64 "--receipt-dir is required"
((${#allowed_targets[@]} == 1)) \
    || fail 64 "exactly one --allow-target is required"
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] \
    || fail 64 "--timeout-seconds must be a positive integer"
((timeout_seconds <= 3600)) \
    || fail 64 "--timeout-seconds must not exceed 3600"
[[ "$max_mutations" =~ ^[1-9][0-9]*$ ]] \
    || fail 64 "--max-mutations must be a positive integer"
((max_mutations <= 10000)) \
    || fail 64 "--max-mutations must not exceed 10000"

unset PYTHONPATH
unset PYTHONHOME
unset PYTHONUSERBASE

repo_real="$(realpath -e -- "$repo_root")" || fail 66 "repository not found"
[[ -d "$repo_real" ]] || fail 66 "repository is not a directory"
case "$repo_real" in
    /mnt/*)
        fail 65 "repository must be on the WSL Linux filesystem"
        ;;
esac
git_top="$(git -C "$repo_real" rev-parse --show-toplevel 2>/dev/null)" \
    || fail 66 "repository is not a Git worktree"
[[ "$git_top" == "$repo_real" ]] || fail 65 "--repo-root must be the worktree root"
[[ -z "$(git -C "$repo_real" status --porcelain)" ]] \
    || fail 73 "Git worktree must be clean"

project_real="$(realpath -e -- "$repo_real/$project_dir")" \
    || fail 66 "mutation project not found"
[[ -d "$project_real" ]] || fail 66 "mutation project is not a directory"
case "$project_real/" in
    "$repo_real"/*) ;;
    *) fail 65 "mutation project resolves outside repository" ;;
esac
project_relative="${project_real#"$repo_real"/}"

target_real="$(realpath -e -- "$repo_real/$target_path")" \
    || fail 66 "mutation target not found"
[[ -f "$target_real" ]] || fail 66 "mutation target is not a file"
case "$target_real" in
    "$repo_real"/*) ;;
    *) fail 65 "mutation target resolves outside repository" ;;
esac
[[ "$target_real" == *.py ]] || fail 65 "mutation target must be one Python file"
target_relative="${target_real#"$repo_real"/}"

allowed_real="$(realpath -m -- "$repo_real/${allowed_targets[0]}")"
case "$allowed_real" in
    "$repo_real"/*) ;;
    *) fail 65 "allowlisted target resolves outside repository" ;;
esac
[[ "$target_real" == "$allowed_real" ]] \
    || fail 65 "mutation target is outside explicit allowlist"

test_real="$(realpath -e -- "$project_real/$test_path")" \
    || fail 66 "baseline test path not found"
[[ -f "$test_real" ]] || fail 66 "baseline test path is not a file"
case "$test_real" in
    "$project_real"/*) ;;
    *) fail 65 "baseline test path resolves outside mutation project" ;;
esac
test_relative="${test_real#"$project_real"/}"
case "$test_relative" in
    *[[:space:]]*) fail 65 "baseline test path must not contain whitespace" ;;
esac

case "$receipt_dir" in
    /*) ;;
    *) fail 65 "receipt directory must be absolute" ;;
esac
case "$receipt_dir" in
    /mnt/*) fail 65 "receipt directory must be on the WSL Linux filesystem" ;;
esac
[[ ! -e "$receipt_dir" ]] || fail 65 "receipt directory must not already exist"
receipt_parent="$(realpath -e -- "$(dirname "$receipt_dir")")" \
    || fail 66 "receipt parent directory not found"
case "$receipt_parent/" in
    "$repo_real"/*) fail 65 "receipt directory must be outside repository" ;;
esac

venv_real="$(realpath -e -- "$venv_path" 2>/dev/null)" || fail 69 "virtualenv not found"
python_executable="$venv_real/bin/python"
[[ -x "$python_executable" ]] || fail 69 "virtualenv Python is unavailable"
set +e
site_packages_value="$(read_include_system_site_packages "$venv_real/pyvenv.cfg")"
site_packages_exit=$?
python_version_output="$("$python_executable" -c \
    'import platform; print(platform.python_version())' 2>&1)"
python_version_exit=$?
pytest_version_output="$("$python_executable" -m pytest --version 2>&1)"
pytest_version_exit=$?
set -e
[[ "$site_packages_exit" -eq 0 && "$site_packages_value" == "false" ]] \
    || fail 78 "virtualenv isolation mismatch"
[[ "$python_version_exit" -eq 0 && "$python_version_output" == "$EXPECTED_PYTHON_VERSION" ]] \
    || fail 78 "Python runtime mismatch"
[[ "$pytest_version_exit" -eq 0 && "$pytest_version_output" == "pytest $EXPECTED_PYTEST_VERSION" ]] \
    || fail 78 "pytest runtime mismatch"
if [[ -z "$cosmic_ray_executable" ]]; then
    cosmic_ray_executable="$venv_real/bin/cosmic-ray"
fi
cosmic_ray_real="$(realpath -e -- "$cosmic_ray_executable" 2>/dev/null)" \
    || fail 69 "Cosmic Ray executable not found"
[[ -x "$cosmic_ray_real" ]] || fail 69 "Cosmic Ray executable is not executable"
if [[ -z "$cr_report_executable" ]]; then
    cr_report_executable="$venv_real/bin/cr-report"
fi
cr_report_real="$(realpath -e -- "$cr_report_executable" 2>/dev/null)" \
    || fail 69 "cr-report executable not found"
summary_real="$(realpath -e -- "$repo_real/$SUMMARY_REL")" \
    || fail 69 "summary helper not found"

set +e
version_output="$("$cosmic_ray_real" --version 2>&1)"
version_exit=$?
set -e
[[ "$version_exit" -eq 0 ]] \
    || fail 78 "Cosmic Ray runtime mismatch"
[[ "$version_output" == "cosmic-ray, version ${EXPECTED_COSMIC_RAY_VERSION}" ]] \
    || fail 78 "Cosmic Ray runtime mismatch"

work_root="$(mktemp -d "${TMPDIR:-/tmp}/citystate-cosmic-ray.XXXXXX")"
cleanup() {
    if [[ -n "${work_root:-}" && -d "$work_root" ]]; then
        rm -rf -- "$work_root"
    fi
}
trap cleanup EXIT

git -C "$repo_real" archive --format=tar HEAD "$project_relative" \
    | tar -xf - -C "$work_root"
work_project="$work_root/$project_relative"
case "$target_real" in
    "$project_real"/*)
        target_project_relative="${target_real#"$project_real"/}"
        work_target="$work_project/$target_project_relative"
        ;;
    *)
        target_project_relative="target/$(basename "$target_real")"
        mkdir -p -- "$work_project/target"
        work_target="$work_project/$target_project_relative"
        cp -- "$target_real" "$work_target"
        ;;
esac
source_before="$(sha256sum "$work_target" | cut -d ' ' -f 1)"

cd "$work_project"
set +e
"$python_executable" -m pytest -q -x "$test_relative" \
    >"$work_root/baseline.stdout.txt" \
    2>"$work_root/baseline.stderr.txt"
baseline_exit=$?
set -e
[[ "$baseline_exit" -eq 0 ]] \
    || fail 67 "baseline pytest failed with exit ${baseline_exit}"

cat >"$work_root/cosmic-ray.toml" <<EOF
[cosmic-ray]
module-path = "$target_project_relative"
timeout = $timeout_seconds
excluded-modules = []
test-command = "$python_executable -m pytest -q -x $test_relative"
distributor.name = "local"
EOF

mkdir -- "$receipt_dir"
set +e
"$cosmic_ray_real" init "$work_root/cosmic-ray.toml" "$work_root/session.sqlite" \
    >"$work_root/init.stdout.txt" \
    2>"$work_root/init.stderr.txt"
init_exit=$?
set -e
if [[ "$init_exit" -ne 0 ]]; then
    cp -- "$work_root/init.stdout.txt" "$receipt_dir/init.stdout.txt"
    cp -- "$work_root/init.stderr.txt" "$receipt_dir/init.stderr.txt"
    printf 'phase=init\nexit_code=%s\n' "$init_exit" >"$receipt_dir/failure.env"
    fail 68 "session initialization failed with exit ${init_exit}"
fi

"$cosmic_ray_real" dump "$work_root/session.sqlite" >"$work_root/pending.dump.jsonl"
pending_count="$(wc -l <"$work_root/pending.dump.jsonl")"
if ((pending_count > max_mutations)); then
    cp -- "$work_root/pending.dump.jsonl" "$receipt_dir/pending.dump.jsonl"
    printf 'phase=session_limit\nmutation_count=%s\nlimit=%s\n' \
        "$pending_count" "$max_mutations" >"$receipt_dir/failure.env"
    fail 74 "session has ${pending_count} mutations; limit is ${max_mutations}"
fi

set +e
"$cosmic_ray_real" exec "$work_root/cosmic-ray.toml" "$work_root/session.sqlite" \
    >"$work_root/exec.stdout.txt" \
    2>"$work_root/exec.stderr.txt"
exec_exit=$?
set -e
if [[ "$exec_exit" -ne 0 ]]; then
    cp -- "$work_root/exec.stdout.txt" "$receipt_dir/exec.stdout.txt"
    cp -- "$work_root/exec.stderr.txt" "$receipt_dir/exec.stderr.txt"
    printf 'phase=exec\nexit_code=%s\n' "$exec_exit" >"$receipt_dir/failure.env"
    fail 70 "mutation execution failed with exit ${exec_exit}"
fi

"$cosmic_ray_real" dump "$work_root/session.sqlite" >"$work_root/session.dump.jsonl" \
    || fail 71 "session dump failed"
"$cr_report_real" --show-diff --all-mutations "$work_root/session.sqlite" \
    >"$work_root/report.txt" || fail 71 "report generation failed"
"$python_executable" "$summary_real" \
    "$work_root/session.dump.jsonl" "$work_root/summary.json" \
    >"$work_root/summary.stdout.txt" || fail 71 "summary generation failed"

source_after="$(sha256sum "$work_target" | cut -d ' ' -f 1)"
[[ "$source_before" == "$source_after" ]] \
    || fail 71 "Cosmic Ray did not restore the archived source"
[[ -z "$(git -C "$repo_real" status --porcelain)" ]] \
    || fail 73 "repository state changed during mutation run"

cp -- "$work_root/session.dump.jsonl" "$receipt_dir/session.dump.jsonl"
cp -- "$work_root/summary.json" "$receipt_dir/summary.json"
cp -- "$work_root/report.txt" "$receipt_dir/report.txt"
cp -- "$work_root/baseline.stdout.txt" "$receipt_dir/baseline.stdout.txt"
cp -- "$work_root/baseline.stderr.txt" "$receipt_dir/baseline.stderr.txt"
cp -- "$work_root/init.stdout.txt" "$receipt_dir/init.stdout.txt"
cp -- "$work_root/init.stderr.txt" "$receipt_dir/init.stderr.txt"
cp -- "$work_root/exec.stdout.txt" "$receipt_dir/exec.stdout.txt"
cp -- "$work_root/exec.stderr.txt" "$receipt_dir/exec.stderr.txt"
cat >"$receipt_dir/receipt.env" <<EOF
cosmic_ray_version=$EXPECTED_COSMIC_RAY_VERSION
distributor=local
workers=1
timeout_seconds=$timeout_seconds
mutation_count=$pending_count
source_before_sha256=$source_before
source_after_sha256=$source_after
canonical_target=$target_relative
EOF

cat "$work_root/summary.json"
unsafe_count="$("$python_executable" -c \
    'import json,sys; print(sum(json.load(open(sys.argv[1], encoding="utf-8"))["unsafe_outcomes"].values()))' \
    "$work_root/summary.json")"
if ((unsafe_count > 0)); then
    fail 72 "session contains ${unsafe_count} incomplete, timeout, or error outcomes"
fi
printf 'cosmic-ray wrapper: receipt=%s cleanup=scheduled\n' "$receipt_dir" >&2
