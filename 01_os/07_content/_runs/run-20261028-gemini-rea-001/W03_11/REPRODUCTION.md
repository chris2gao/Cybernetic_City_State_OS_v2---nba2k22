# W03-11 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 验证 0xf1e370..0xf1e3e0 4 个 PlayType 微型 Setter 的半字节位操作
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0xf1e370 0xf1e3e6

# 2. 验证 0x990a10 属性与倾向 155 项跳转表边界 (cmp ebp, 0x9b)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x990a20 0x990a48

# 3. 验证 0x992d40 徽章等级校验与写入
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x992d40 0x992d65
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_player_playtypes.py"
```
