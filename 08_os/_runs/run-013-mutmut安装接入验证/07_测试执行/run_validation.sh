#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
venv_path="${1:-/home/gk/.venvs/core-mutmut-3.6.0}"

exec "$venv_path/bin/python" \
    "$repo_root/08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/run_validation.py" \
    --repo-root "$repo_root" \
    --venv "$venv_path"
