# W03-07 Codex Review Guide

## 1. 重点审核内容
1. **报价状态机与签约结算**:
   - `0x12bc4a0` 负责创建/提交报价单（`status = PENDING`）。
   - 必须通过模拟步进让球员 AI 作出决策，或通过直接修改球员结构体 `[Player + 0x354]` 的所属球队与合同属性来完成强制签约（Force Sign）。
2. **薪资帽预留空间 (Cap Hold)**:
   - 提交报价时，游戏引擎会在球队薪资中增加相应的 Cap Hold，撤回报价（`0x12b3840`）会释放该 Cap Hold。
3. **集成建议**:
   - 将 `contract_offer_codec.py` 对接到 `sign.offer_contract` (0x12bcdb0 / 0x12bc4a0) 和 `sign.cancel_pending_offer` (0x12b3840)。
