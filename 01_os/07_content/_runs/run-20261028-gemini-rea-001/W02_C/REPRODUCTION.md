# Reproduction Guide: W02-C Team Playbook 68 Slots

## 1. PE Disassembly Verification
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x7aa57b, 0x7aa58a):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x7aa57b: test     eax, eax
0x7aa57d: je       0x1407aa594
0x7aa57f: call     0x14149ae80
0x7aa584: cmp      eax, 0x44
0x7aa587: jne      0x1407aa594
0x7aa589: mov      ecx, dword ptr [rip + 0x1cc6dd9]
```
**Proof**: `cmp eax, 0x44` (68 decimal) strictly validates the 68 playbook slots.

## 2. Offline Unit Test Reproduction
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/W02_C/tests/test_w02_c_playbook_68.py" -v
```
**Expected Output**:
- 4 passed, exit code 0.
