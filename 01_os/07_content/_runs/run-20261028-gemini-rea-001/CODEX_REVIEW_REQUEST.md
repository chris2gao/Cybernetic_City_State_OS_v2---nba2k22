# Codex Review Request: GREA-01 Opponent Gameplan

## 1. 审核请求背景与目标
- **请求方**: Gemini (REA Native机制探索与隔离候选开发)
- **接收方 / 审核人**: Codex (Formal Engineering Owner)
- **任务编号**: `GREA-01`
- **分支**: `gemini_rea` (基于 commit `39086984adfa554d36315382d41bc2e5d2e54c39`)
- **生命周期**: `candidate_ready_for_independent_review`

请 Codex 对本轮发现的对手 Gameplan 原生内存结构、`PressureOnball` 位段编解码以及原生提交事务调用链进行独立工程审核。

---

## 2. 交付与变更清单 (Allowlist Scoped)

### 2.1 运行记录与证据文档
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/run.yml`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/README.md`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/GREA_01_OPPONENT_GAMEPLAN.md`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/GREA_HANDOFF_TEMPLATE.md`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/GREA_HANDOFF.md`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/NATIVE_CALL_CHAIN.json`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/REPRODUCTION.md`
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/CODEX_REVIEW_REQUEST.md`

### 2.2 隔离候选代码与离线测试
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/__init__.py`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/gameplan_opponent.py`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/native_call_chain.py`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/tests/__init__.py`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/tests/test_grea_01_gameplan_opponent.py`

*(本轮严格未修改任何生产核心代码、无 master 变更、未触及 Codex 正在施工的工作目录)*

---

## 3. Codex 重点独立审查清单 (Audit Checklist)

1. **结构体尺寸与偏移对齐**:
   - `FRANCHISE_GAMEPLAN_MANAGER` 大小为 `0x13E70` (81,520 字节)，槽位 35 个，偏移 `+0x4 + index * 880`。
   - `GAMEPLAN` 大小为 880 字节（`0x370`）。
   - Matchup 数组在 `GAMEPLAN + 0x64`，23 个条目，每条目 12 字节。
   - 审查点：请核对实机 MyLEAGUE 运行时，Pacers (team_id=11) 或其他球队的管理器指针计算公式是否精确吻合。
2. **`PressureOnball` 位段提取**:
   - 位于 `Matchup + 0x4` (word1) 的 `bits 0..2`（掩码 `0x7`）。
   - 取值 0=AUTO, 1=GAP, 2=MODERATE, 3=TIGHT, 4=SMOTHER。
   - 审查点：请核对与 `DEV_20261017_07_OVERALL_DEFENSE_EVIDENCE.json` 及实机 UI 的一致性。
3. **原生提交事务完整性**:
   - 原版 UI 保存流程：确保 Gameplan -> 写入 Matchup -> `0x146ec50 ApplyToCoach` -> `0x7a7aab: mov word ptr [rbx], 1` 置 `IsInUse = 1` -> `0x131f110 CommitPendingFlags`。
   - 审查点：当正式将本候选方案集成进 `COACH_SET_GAMEPLAN` 的 Native Action 绑定时，是否还需要挂接存档脏标志以保证退出 MyLEAGUE 时自动存盘。

---

## 4. 离线复现与测试验证
Codex 可随时执行以下命令复现：
```powershell
python -m pytest "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/GREA_01/tests/test_grea_01_gameplan_opponent.py" -v
```
预期：12 项测试全部通过，退出码 0。
