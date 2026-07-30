#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--version" ]]; then
    printf 'mutmut, version 9.9.9\n'
    exit 0
fi

printf 'fake mutmut must not reach mutation execution\n' >&2
exit 99
