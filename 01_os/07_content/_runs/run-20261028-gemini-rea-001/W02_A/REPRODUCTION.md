# Reproduction Guide: W02-A GREA-01 Evidence Repair

## 1. Prerequisites
- Target binary: `E:\Games\NBA 2K22\NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
- Disassembly engine: `pe_local.py` (built-in PE parser + Capstone 5.0.9)
- Command line: PowerShell on Windows

## 2. Exact Disassembly Commands and Actual Outputs

### 2.1 Recheck RVA 0x146ec50 (Owner Team ID vs Coach Pointer)
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x146ec50, 0x146ec7c):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x146ec50: push     rbx
0x146ec52: sub      rsp, 0x20
0x146ec56: mov      rbx, rcx
0x146ec59: movzx    ecx, word ptr [rcx + 2]
0x146ec5d: call     0x140f40eb0
0x146ec62: xor      edx, edx
0x146ec64: mov      rcx, rax
0x146ec67: call     0x1409cd2a0
0x146ec6c: mov      rdx, rax
0x146ec6f: mov      rcx, rbx
0x146ec72: add      rsp, 0x20
0x146ec76: pop      rbx
0x146ec77: jmp      0x14146eaa0
```
**Finding**: Instruction at `0x146ec59` is `movzx ecx, word ptr [rcx + 2]` (reads uint16 `owner_team_index`), resolves it via `0x140f40eb0` and `0x1409cd2a0` to `pCoach`, and tail-calls `0x14146eaa0`. The previous GREA-01 text claiming a 64-bit pointer dereference at `+2` was textually imprecise and is hereby corrected.

### 2.2 Recheck RVA 0x131f110 (Commit Scope)
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x131f110, 0x131f160):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x131f110: mov      qword ptr [rsp + 8], rbx
0x131f115: push     rdi
0x131f116: sub      rsp, 0x20
0x131f11a: test     byte ptr [rcx + 0x7bc4], 1
0x131f121: mov      rbx, rcx
0x131f124: je       0x14131f13d
0x131f126: add      rcx, 0x7854
0x131f12d: call     0x1414f7ec0
0x131f132: test     eax, eax
0x131f134: je       0x14131f13d
0x131f136: and      dword ptr [rbx + 0x7bc4], 0xfffffffe
0x131f13d: mov      eax, dword ptr [rbx + 0x7bc4]
0x131f143: test     al, 1
0x131f145: je       0x14131f166
0x131f147: xor      edx, edx
0x131f149: lea      rcx, [rbx + 0x7854]
0x131f150: lea      r8d, [rdx + 1]
0x131f154: call     0x14146ec80
0x131f159: and      dword ptr [rbx + 0x7bc4], 0xfffffffe
```
**Finding**: Operates exclusively on `+0x7854` (Slot 35: Default Gameplan). Does not flush opponent gameplans.

### 2.3 Recheck RVA 0x12f6540 (35 Slots Loop Bounds)
```powershell
python -c "
import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action')
from pe_local import Image
img = Image()
for ins in img.instructions(0x12f65f0, 0x12f6630):
    print(f'{hex(ins.address - img.base)}: {ins.mnemonic:8s} {ins.op_str}')
"
```
**Actual Output**:
```
0x12f65f0: movsxd   rax, ebx
0x12f65f3: imul     rcx, rax, 0x370
0x12f65fa: add      rcx, 4
0x12f65fe: add      rcx, rsi
0x12f6601: call     0x140fe12f0
0x12f6606: test     rax, rax
0x12f6609: je       0x1412f661b
0x12f660b: movzx    ecx, word ptr [rdi + 0xca8]
0x12f6612: cmp      word ptr [rax + 0xca8], cx
0x12f6619: je       0x1412f6634
0x12f661b: inc      ebx
0x12f661d: cmp      ebx, 0x23
0x12f6620: jl       0x1412f65f0
```
**Finding**: `cmp ebx, 0x23` proves 35 slots; `imul rcx, rax, 0x370` proves 880-byte stride; `add rcx, 4` proves manager offset `+4`.
