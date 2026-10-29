# W03-09 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 验证 0x92a6a0 选秀权位段解包 (轮次、顺位、球队)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x92a6c0 0x92a6ea

# 2. 验证 0xec9610 选秀执行与自动当前顺位获取 (0x140eca640)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0xec9630 0xec9650

# 3. 验证 0x1261d40 球探出差预算提取 (bits 15..18 of +0x1068)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x1261d4a 0x1261d60
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_draft_scout.py"
```
