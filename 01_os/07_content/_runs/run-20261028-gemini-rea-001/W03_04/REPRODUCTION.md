# W03-04 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 查看 CoachData_ApplyGameplan (0x146eaa0) 关键字段投影指令
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x146eac0 0x146ec40

# 2. 查看 0x131f110 脏标志 Bit 1 与 CoachData 刷新机制
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x131f160 0x131f195
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_coach_settings.py"
```
