"""Read-only exact-ref mismatch report; no contract edits or guessed cause."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml

root = Path.cwd()
refs = sorted(root.glob('01_os/01_workflow/*/实现/阶段协同推演profile引用_v1.yml'))
problems = []
seen = set()
for ref_path in refs:
    data = yaml.safe_load(ref_path.read_text(encoding='utf-8'))
    for name, value in data.items():
        if not isinstance(value, dict) or not {'path', 'blob_sha'}.issubset(value):
            continue
        target = value['path']
        if target in seen:
            continue
        seen.add(target)
        raw = (root / target).read_bytes()
        physical = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        proc = subprocess.run(['git', 'rev-parse', 'HEAD:' + target], capture_output=True, check=True)
        git_blob = proc.stdout.decode().strip()
        if physical != value['blob_sha']:
            problems.append({'target': target, 'declared': value['blob_sha'],
                             'physical': physical, 'head_blob': git_blob,
                             'physical_equals_git': physical == git_blob})
print(json.dumps({'mismatches': problems}, ensure_ascii=False, indent=2))
