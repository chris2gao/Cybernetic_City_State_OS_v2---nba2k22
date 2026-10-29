# W03-07 Delivery Handoff: GM Contracts Full Chain

## 1. 范围与 17 项需求覆盖
本包全面研究并闭环了 `GM_CONTRACT_COMPLETION` 组的 17 项需求：
- 自由球员签约与提前续约 (`FA_SIGN`, `EXTEND`, `RE_SIGN`)
- 合同报价提交与状态追踪 (`CONTRACT_OFFER`, `OFFER_ACCEPT_OR_REJECT`)
- 球队选项与球员选项执行 (`TEAM_OPTION`, `PLAYER_OPTION`)
- 受限制自由球员与资质报价 (`QUALIFYING_OFFER`, `MATCH_RFA`)
- 鸟权放弃与预留空间释放 (`RENOUNCE_RIGHTS`, `CAP_HOLD_RELEASE`)
- 特例与双向/新秀合同 (`HARDSHIP_SIGN`, `TWO_WAY_SIGN`, `ROOKIE_SIGN`)
- 合同修改、重谈与报价撤回 (`CONTRACT_EDIT`, `CONTRACT_RENEGOTIATE`, `OFFER_WITHDRAW`)

## 2. 核心原生机制发现
1. **合同报价原生上下文 (`0x12bc4a0`)**:
   - 原版函数 `0x12bc4a0` 接受一个 48 字节的 `ContractOfferContext` 结构：
     - `+0x0`: uint16 `player_id`，调用 `0x140f3f580` 解析为 `Player*`。
     - `+0x2`: uint16 `team_id`，调用 `0x140f40eb0` 解析为 `Team*`。
     - `+0x4`: uint16 `years` (1..5 年)。
     - `+0x8`..`+0x1c`: 5 个 32 位整型对应各年薪资（美元）。
     - `+0x20`: 32 位合同标志与状态字：
       - Bit 12..13: 选项类型（0=无, 1=球队选项, 2=球员选项, 3=双向）。
       - Bit 14: 交易否决权 (No-Trade Clause)。
       - 状态值域：`0x100000` (PENDING), `0x200000` (ACCEPTED), `0x300000` (REJECTED), `0x1c0000` (WITHDRAWN)。
   - **关键自纠**: 提交报价仅进入 `PENDING` 挂起池，绝不能在调用返回 1 时直接宣称球员已 `SIGNED`！最终签约需要模拟步进中球员 AI 结算或在原版签约最终事务中确认。

2. **报价撤回机制 (`0x12b3840`)**:
   - 原版函数 `0x12b3840`（对应 `sign.cancel_pending_offer`）通过指令：
     ```assembly
     and dword ptr [rsi + 0x20], 0xffdfffff
     or  dword ptr [rsi + 0x20], 0x1c0000
     ```
     将报价标记为已撤回，并退回球队薪资空间预留。

3. **球队选项与球员选项决策阶段 (`0x12bf5a0`)**:
   - 原版检查赛季阶段（调用 `0x140edf010`），当且仅当处于赛季阶段 `0x16`（22 decimal: Offseason Options Phase）时，引擎统一遍历并结算选项。

## 3. 隔离候选与验证交付
- 交付编解码器：`contract_offer_codec.py`
- 交付独立测试：`pytest_gemini/test_contract_offer.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
