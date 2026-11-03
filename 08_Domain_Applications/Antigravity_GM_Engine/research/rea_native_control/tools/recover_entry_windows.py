"""Bounded entry windows for selected leaf/thunk candidates, not whole CFGs."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'rea_native_action'))
from pe_local import Image


def recover(image, rvas, size):
    if not 1 <= len(rvas) <= 16 or not 8 <= size <= 256:
        raise ValueError('Select 1..16 entries and an 8..256 byte window')
    windows = []
    for rva in rvas:
        raw = image.read(rva, size)
        windows.append({'entry_candidate_rva': rva, 'window_bytes': size,
                        'window_sha256': hashlib.sha256(raw).hexdigest(),
                        'unwind_chain': image.unwind_chain(rva),
                        'instructions': image.instruction_rows(rva, rva + size)})
    return {'source_kind': 'PINNED_PE_ENTRY_WINDOWS_NOT_REA_PROVIDER',
            'game_build_sha256': image.sha256, 'game_access': False,
            'windows': windows,
            'limitations': ['Window boundaries are not function extents or an ABI proof',
                           'Bytes after a RET or tail JMP may belong to a different function',
                           'No game code was executed']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rva', nargs='+', type=lambda value: int(value, 0), required=True)
    parser.add_argument('--bytes', type=int, default=96)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise SystemExit('Existing evidence is immutable; select a new output')
    value = recover(Image(), args.rva, args.bytes)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'windows': len(value['windows']), 'bytes_each': args.bytes,
                      'game_access': False}))
