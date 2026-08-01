#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
    echo "usage: $0 REPO_ROOT OUTPUT_ROOT COSMIC_RAY_VENV MUTMUT_VENV" >&2
    exit 64
fi

repo=$(realpath -e -- "$1")
output_root=$2
export COSMIC_RAY_VENV=$(realpath -e -- "$3")
export MUTMUT_VENV=$(realpath -e -- "$4")
experiments="$output_root/experiments"
[[ ! -e "$experiments" ]] || {
    echo "experiments output already exists" >&2
    exit 65
}
[[ -z "$(git -C "$repo" status --porcelain)" ]] || {
    echo "repository must be clean" >&2
    exit 66
}

run_rel="08_os/_runs/run-014-cosmic-ray安装对照验证/07_测试执行"
cosmic_runner="$repo/$run_rel/run_cosmic_once.sh"
mutmut_runner="$repo/$run_rel/run_mutmut_once.sh"
analyzer="$repo/$run_rel/analyze_cosmic_dump.py"
calibration="$run_rel/calibration"
timeout_project="$run_rel/timeout_probe"
real_project="08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/real_target_tests"
real_target="08_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py"

run_cosmic_pair() {
    local phase=$1
    local commit=$2
    local project=$3
    local source=$4
    local tests=$5
    local config=$6
    local canonical=${7:-}
    local repetition output
    for repetition in rep1 rep2; do
        output="$experiments/$phase/cosmic/$repetition"
        "$cosmic_runner" "$repo" "$commit" "$project" "$output" \
            "$source" "$tests" "$config" "$canonical"
        "$COSMIC_RAY_VENV/bin/python" "$analyzer" \
            "$output/session.dump.jsonl" "$output/normalized.json"
    done
}

run_mutmut_pair() {
    local phase=$1
    local commit=$2
    local project=$3
    local source=$4
    local tests=$5
    local canonical=${6:-}
    local repetition output capture
    for repetition in rep1 rep2; do
        output="$experiments/$phase/mutmut/$repetition"
        capture=1
        [[ "$repetition" == "rep1" ]] || capture=0
        CAPTURE_ALL_MUTANTS=$capture "$mutmut_runner" \
            "$repo" "$commit" "$project" "$output" \
            "$source" "$tests" "$canonical"
    done
}

weak_commit="c89e1e6c53d12af870d2e128a007987fada39c1f"
strong_commit="2481fbaff06cc12a8f37afe537e20f3369f07cb1"
timeout_commit="b4c45812106e26a4be0c2a74af0f3807fb8e634b"
real_commit=$(git -C "$repo" rev-parse HEAD)

run_cosmic_pair weak "$weak_commit" "$calibration" \
    calibration_pkg/logic.py tests "$calibration/cosmic-ray.toml"
run_mutmut_pair weak "$weak_commit" "$calibration" calibration_pkg/logic.py tests

run_cosmic_pair strong "$strong_commit" "$calibration" \
    calibration_pkg/logic.py tests "$calibration/cosmic-ray.toml"
run_mutmut_pair strong "$strong_commit" "$calibration" calibration_pkg/logic.py tests

run_cosmic_pair timeout "$timeout_commit" "$timeout_project" \
    timeout_pkg/logic.py tests "$timeout_project/cosmic-ray.toml"
run_mutmut_pair timeout "$timeout_commit" "$timeout_project" timeout_pkg/logic.py tests

run_cosmic_pair real "$real_commit" "$real_project" \
    target/inspect_schema_refs.py tests/inspector_cases.py \
    "$run_rel/real_target_cosmic-ray.toml" "$real_target"
run_mutmut_pair real "$real_commit" "$real_project" \
    target/inspect_schema_refs.py tests/inspector_cases.py "$real_target"

printf 'experiments_root=%s\n' "$experiments"
