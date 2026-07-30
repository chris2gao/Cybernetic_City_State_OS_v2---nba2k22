#!/usr/bin/env bash
set -euo pipefail

readonly EXPECTED_MUTMUT_VERSION="3.6.0"

fail() {
    local exit_code="$1"
    shift
    printf 'mutmut wrapper: %s\n' "$*" >&2
    exit "$exit_code"
}

require_value() {
    local option="$1"
    local value="${2:-}"
    [[ -n "$value" ]] || fail 64 "missing value for ${option}"
}

repo_root=""
venv_path=""
project_dir=""
target_path=""
test_path=""
mutmut_executable=""
max_children="2"
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
        --mutmut-executable)
            require_value "$1" "${2:-}"
            mutmut_executable="$2"
            shift 2
            ;;
        --max-children)
            require_value "$1" "${2:-}"
            max_children="$2"
            shift 2
            ;;
        --help)
            printf '%s\n' \
                'Usage: invoke.sh --repo-root PATH --venv PATH --project-dir RELPATH' \
                '                 --target RELPATH --allow-target RELPATH' \
                '                 --test-path PROJECT_RELPATH [--allow-target RELPATH ...]' \
                '                 [--mutmut-executable PATH] [--max-children N]'
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
((${#allowed_targets[@]} > 0)) || fail 64 "at least one --allow-target is required"
[[ "$max_children" =~ ^[1-9][0-9]*$ ]] || fail 64 "--max-children must be a positive integer"

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
    "$repo_real"/*)
        ;;
    *)
        fail 65 "mutation project resolves outside repository"
        ;;
esac
project_relative="${project_real#"$repo_real"/}"

target_real="$(realpath -e -- "$repo_real/$target_path")" \
    || fail 66 "mutation target not found"
[[ -f "$target_real" ]] || fail 66 "mutation target is not a file"
case "$target_real" in
    "$repo_real"/*)
        ;;
    *)
        fail 65 "mutation target resolves outside repository"
        ;;
esac
[[ "$target_real" == *.py ]] || fail 65 "mutation target must be one Python file"
target_relative="${target_real#"$repo_real"/}"

target_allowed=false
for allowed_target in "${allowed_targets[@]}"; do
    allowed_real="$(realpath -m -- "$repo_real/$allowed_target")"
    case "$allowed_real" in
        "$repo_real"/*)
            ;;
        *)
            fail 65 "allowlisted target resolves outside repository"
            ;;
    esac
    if [[ "$target_real" == "$allowed_real" ]]; then
        target_allowed=true
    fi
done
[[ "$target_allowed" == true ]] || fail 65 "mutation target is outside explicit allowlist"

test_real="$(realpath -e -- "$project_real/$test_path")" \
    || fail 66 "baseline test path not found"
[[ -f "$test_real" ]] || fail 66 "baseline test path is not a file"
case "$test_real" in
    "$project_real"/*)
        ;;
    *)
        fail 65 "baseline test path resolves outside mutation project"
        ;;
esac
test_relative="${test_real#"$project_real"/}"

venv_real="$(realpath -e -- "$venv_path")" || fail 69 "virtualenv not found"
python_executable="$venv_real/bin/python"
[[ -x "$python_executable" ]] || fail 69 "virtualenv Python is unavailable"

if [[ -z "$mutmut_executable" ]]; then
    mutmut_executable="$venv_real/bin/mutmut"
fi
mutmut_real="$(realpath -e -- "$mutmut_executable")" \
    || fail 69 "mutmut executable not found"
[[ -x "$mutmut_real" ]] || fail 69 "mutmut executable is not executable"

work_root="$(mktemp -d "${TMPDIR:-/tmp}/citystate-mutmut.XXXXXX")"
cleanup() {
    if [[ -n "${work_root:-}" && -d "$work_root" ]]; then
        rm -rf -- "$work_root"
    fi
}
trap cleanup EXIT

git -C "$repo_real" archive --format=tar HEAD "$project_relative" \
    | tar -xf - -C "$work_root"
work_project="$work_root/$project_relative"
mkdir -p "$work_project/target"
cp -- "$target_real" "$work_project/target/$(basename "$target_real")"

cd "$work_project"
set +e
version_output="$("$mutmut_real" --version 2>&1)"
version_exit=$?
set -e
[[ "$version_exit" -eq 0 ]] \
    || fail 78 "version probe failed with exit ${version_exit}"
[[ "$version_output" == "mutmut, version ${EXPECTED_MUTMUT_VERSION}" ]] \
    || fail 78 "version mismatch: expected ${EXPECTED_MUTMUT_VERSION}, got ${version_output}"

set +e
"$python_executable" -m pytest -q "$test_relative"
baseline_exit=$?
set -e
[[ "$baseline_exit" -eq 0 ]] \
    || fail 67 "baseline pytest failed with exit ${baseline_exit}"

printf 'mutmut wrapper: target=%s version=%s workspace=%s\n' \
    "$target_relative" "$EXPECTED_MUTMUT_VERSION" "$work_root"
set +e
"$mutmut_real" run --max-children "$max_children"
mutation_exit=$?
set -e

if [[ -d mutants ]]; then
    "$mutmut_real" results --all true
fi

[[ -z "$(git -C "$repo_real" status --porcelain)" ]] \
    || fail 73 "tracked or untracked repository state changed during mutation run"
printf 'mutmut wrapper: cache_cleanup=scheduled process_exit=%s\n' "$mutation_exit"
exit "$mutation_exit"
