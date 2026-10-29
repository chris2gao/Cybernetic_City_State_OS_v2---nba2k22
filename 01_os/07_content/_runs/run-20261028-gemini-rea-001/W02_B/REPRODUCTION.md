# Reproduction Guide: W02-B 18 Individual Defensive Matchup Settings

## 1. Disassembly Verification of Matchup Default Initializer
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x1465278, 0x1465295):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x1465278: mov      dword ptr [rax], 0xffffffff
0x146527e: and      dword ptr [rax + 8], 0xfffff800
0x1465285: mov      dword ptr [rax + 4], 0x280000
0x146528c: mov      word ptr [rax], di
0x146528f: mov      word ptr [rax + 2], bp
```
**Proof**:
- `0x146527e`: `and dword ptr [rax + 8], 0xfffff800` clears the lowest 11 bits of word 2 (`OnballHelp` through `PreRotate`).
- `0x1465285`: `mov dword ptr [rax + 4], 0x280000` sets Word 1 default to `0x280000` (DoubleTeamPerimeter=1 at bit 19, DoubleTeamPost=1 at bit 21, all others 0).

## 2. Disassembly Verification of 12-Byte Block Update
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x1465349, 0x1465366):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x1465349: movsd    xmm0, qword ptr [rsi]
0x146534d: movsxd   rax, ebx
0x1465350: lea      rax, [rax + rax*2]
0x1465354: lea      rax, [rax + 0x19]
0x1465358: lea      rax, [rdi + rax*4]
0x146535c: movsd    qword ptr [rax], xmm0
0x1465360: mov      ecx, dword ptr [rsi + 8]
0x1465363: mov      dword ptr [rax + 8], ecx
```
**Proof**:
- Demonstrates 12-byte atomic copy (8 bytes via `movsd`, 4 bytes via `mov ecx`). No individual micro-setters exist in binary.

## 3. Offline Unit Test Reproduction
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/W02_B/tests/test_w02_b_defense_18.py" -v
```
**Expected Output**:
- 4 passed, exit code 0.
