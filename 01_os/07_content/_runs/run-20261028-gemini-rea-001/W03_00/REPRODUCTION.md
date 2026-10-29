# W03-00 Reproduction Guide

## 1. 离线复现环境要求
- Python 3.10+
- `pe_local.py` (位于 `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/`)
- 游戏可执行文件：`NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)

## 2. 离线反汇编复现指令
```powershell
# 1. 验证 18 项防守位段默认值与掩码
python -c "import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action'); from pe_local import Image; img = Image(); print([(hex(r['rva']), r['mnemonic'], r['operands']) for r in img.instruction_rows(0x1465275, 0x1465290)])"

# 2. 验证 Playbook 68 槽上限判断与计数读取
python -c "import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action'); from pe_local import Image; img = Image(); print([(hex(r['rva']), r['mnemonic'], r['operands']) for r in img.instruction_rows(0x7aa575, 0x7aa590)])"
python -c "import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action'); from pe_local import Image; img = Image(); print([(hex(r['rva']), r['mnemonic'], r['operands']) for r in img.instruction_rows(0x149ae80, 0x149aea5)])"

# 3. 验证 Gameplan 原版提交流水线与异步事件分发
python -c "import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action'); from pe_local import Image; img = Image(); print([(hex(r['rva']), r['mnemonic'], r['operands']) for r in img.instruction_rows(0x7a7aa3, 0x7a7ab8)])"
python -c "import sys; sys.path.insert(0, r'08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action'); from pe_local import Image; img = Image(); print([(hex(r['rva']), r['mnemonic'], r['operands']) for r in img.instruction_rows(0x14af7f0, 0x14af805)])"
```
