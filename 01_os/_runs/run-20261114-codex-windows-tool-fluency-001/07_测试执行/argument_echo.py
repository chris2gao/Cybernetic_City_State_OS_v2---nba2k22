"""Offline argv, stderr and exit-code fixture used by the PowerShell replay."""
import json
import sys

if sys.argv[1] == "--fail":
    print("fixture native failure", file=sys.stderr)
    raise SystemExit(7)
if sys.argv[1] == "--warning":
    print("fixture warning", file=sys.stderr)
    print("ok")
else:
    print(json.dumps(sys.argv[1:], ensure_ascii=False))
