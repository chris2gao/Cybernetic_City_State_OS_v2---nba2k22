# W03-12 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 验证 0x978360 球员属性读取例程
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x978360 0x978385

# 2. 验证 0x9888b0 球员薪资读取例程
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x9888b0 0x9888c5

# 3. 验证 0x149ae80 战术书已分配战术数读取例程
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x149ae80 0x149aea0
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_native_getters.py"
```
