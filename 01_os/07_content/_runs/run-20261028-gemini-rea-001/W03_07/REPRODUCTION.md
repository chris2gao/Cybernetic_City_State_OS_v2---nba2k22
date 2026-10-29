# W03-07 Reproduction Guide

## 1. 运行环境
- Python 3.10+
- `pe_local.py`
- `pytest`

## 2. 离线反汇编取证验证
```powershell
# 1. 验证 0x12bc4a0 合同报价解包与实体解析
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x12bc4c9 0x12bc520

# 2. 验证 0x12b3840 报价撤回位操作 (0x1c0000)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x12b3850 0x12b3865

# 3. 验证 0x12bf5a0 选项结算阶段判断 (0x16 = Phase 22)
python "C:\Users\gk\.gemini\antigravity\brain\99371714-f36b-434d-a1ca-1dbd5c3d71cb\scratch\disasm_helper.py" 0x12bf5cc 0x12bf5ec
```

## 3. 运行隔离单元测试
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/pytest_gemini/test_contract_offer.py"
```
