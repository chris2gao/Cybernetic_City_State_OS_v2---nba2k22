#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 /absolute/path/to/dedicated-cosmic-ray-venv" >&2
    exit 64
fi

venv=$(realpath -e -- "$1")
repo=$(git rev-parse --show-toplevel)
case "$repo" in
    /mnt/*)
        echo "run-014 validation requires a WSL Linux filesystem clone" >&2
        exit 65
        ;;
esac

cosmic_ray="$venv/bin/cosmic-ray"
python="$venv/bin/python"
[[ -x "$cosmic_ray" && -x "$python" ]] || exit 69
[[ "$("$cosmic_ray" --version)" == "cosmic-ray, version 8.4.6" ]] || exit 78

run="$repo/01_os/_runs/run-014-cosmic-ray安装对照验证"
temporary=$(mktemp -d /tmp/run014-validation.XXXXXX)
cleanup() {
    rm -rf -- "$temporary"
}
trap cleanup EXIT

"$python" -m pytest -q \
    "$run/07_测试执行/test_summarize.py" \
    "$run/07_测试执行/test_collect_environment.py"
"$python" "$run/07_测试执行/calibration_survivor_proof.py" \
    "$run/07_测试执行/calibration/calibration_pkg/logic.py" \
    "$temporary/calibration-proof.json"
"$python" "$run/07_测试执行/real_survivor_proof.py" \
    "$repo/01_os/06_execution/tools/check_jsonschema/inspect_schema_refs.py" \
    "$temporary/real-proof.json"
"$python" "$run/07_测试执行/validate_repository_state.py" "$repo"
