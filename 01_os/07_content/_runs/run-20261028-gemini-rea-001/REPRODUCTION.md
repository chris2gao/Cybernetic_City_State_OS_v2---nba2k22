# Reproduction Guide: GREA-01 Opponent Gameplan

## 1. 目标与环境要求
- **目标**: 复现对 NBA 2K22 原生二进制关于对手 Gameplan 的反汇编证据，并执行离线测试验证。
- **操作系统**: Windows (PowerShell)
- **Python**: 3.10+
- **目标可执行文件**: `E:\Games\NBA 2K22\NBA2K22.exe` (SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)
- **Git 分支**: `gemini_rea`

---

## 2. 静态反汇编证据复现 (Static Disassembly Reproduction)

使用已有的反汇编工具 `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/pe_local.py`：

### 2.1 验证 `GetTeamGameplanManager` (RVA `0xfda730`)
```powershell
python -c "
import pefile, capstone
pe = pefile.PE(r'E:\Games\NBA 2K22\NBA2K22.exe', fast_load=True)
sec = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
offset = 0xfda730 - sec.VirtualAddress + sec.PointerToRawData
data = open(r'E:\Games\NBA 2K22\NBA2K22.exe', 'rb')
data.seek(offset)
code = data.read(0x40)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for ins in md.disasm(code, 0x140fda730):
    print(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
    if ins.mnemonic == 'ret': break
"
```
预期输出：
- 调用 `0xedefe0`（获取球队索引）；
- 读取 `[0x3c23170]`（Franchise 指针）；
- 计算 `rdx * 0x13e70` 并加上 `0x19cfd0`。

### 2.2 验证 UI 提交处 `IsInUse` 置 1 与 `CommitPendingFlags` 调用 (RVA `0x7a7aab`)
```powershell
python -c "
import pefile, capstone
pe = pefile.PE(r'E:\Games\NBA 2K22\NBA2K22.exe', fast_load=True)
sec = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
offset = 0x7a7aa0 - sec.VirtualAddress + sec.PointerToRawData
data = open(r'E:\Games\NBA 2K22\NBA2K22.exe', 'rb')
data.seek(offset)
code = data.read(0x30)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for ins in md.disasm(code, 0x1407a7aa0):
    print(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
"
```
预期输出：
- `mov word ptr [rbx], 1`（在 `0x7a7aab` 设置 `IsInUse = 1`）；
- 紧接着调用 `0x131f110`（`CommitPendingFlags`）。

---

## 3. 离线单元测试复现 (Offline Unit Test Reproduction)

无需启动游戏，直接在终端执行：

```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/tests/test_grea_01_gameplan_opponent.py" -v
```

预期结果：
- 12 个测试全部 `PASSED`；
- 退出码为 `0`；
- 验证涵盖结构大小、`PressureOnball` 位段编解码、多对手隔离不变性以及事务调用链顺序。
