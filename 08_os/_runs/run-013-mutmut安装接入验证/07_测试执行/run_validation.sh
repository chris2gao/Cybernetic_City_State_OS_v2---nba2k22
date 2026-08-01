#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
venv_path="${1:-${MUTMUT_VENV:-}}"

if [[ -z "$venv_path" ]]; then
    printf '%s\n' 'usage: run_validation.sh <mutmut-venv> or set MUTMUT_VENV' >&2
    exit 2
fi

exec "$venv_path/bin/python" \
    "$repo_root/08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/run_validation.py" \
    --repo-root "$repo_root" \
    --venv "$venv_path"
