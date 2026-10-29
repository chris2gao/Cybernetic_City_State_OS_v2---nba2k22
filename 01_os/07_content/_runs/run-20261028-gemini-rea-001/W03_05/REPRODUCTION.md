# W03-05 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 验证 0x11b2bb0 单球员分钟位段写入
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x11b2bb0 0x11b2bda

# 2. 验证 0xedf000 球员名单槽位提取
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0xedf000 0xedf00d
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_rotation_timeline.py"
```
