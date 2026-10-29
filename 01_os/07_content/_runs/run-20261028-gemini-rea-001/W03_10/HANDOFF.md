# W03-10 Delivery Handoff: GM Trade Remaining Mechanisms

## 1. 范围与 10 项需求覆盖
本包全面研究并闭环了 `GM_TRADE_REMAINING` 组的 10 项需求：
- 直接执行已同意交易包 (`GM.TRADE.EXECUTE_AGREED`)
- 多人资产交易 (`GM.TRADE.MULTI_PLAYER`)
- 纯选秀权交易 (`GM.TRADE.PICK_ONLY`)
- 球员与签权混合交易 (`GM.TRADE.MIXED`)
- 三方交易资产路由 (`GM.TRADE.THREE_TEAM`)
- 交易货架加入与移出 (`GM.TRADE.TRADE_BLOCK_ADD`, `GM.TRADE.TRADE_BLOCK_REMOVE`)
- 选秀权转让与保护条款指定 (`GM.TRADE.PICK_ASSIGNMENT`)
- Trade Finder 读取与历史成交记录 (`GM.TRADE.FINDER_READ`, `GM.TRADE.TRADE_HISTORY_READ`)

## 2. 核心原生机制发现
1. **交易前置限制与资格校验 (`0x12ec130`)**:
   - 原版函数 `0x12ec130` 对交易涉及的每位球员进行资格检查。
   - 核心校验指令：`test dword ptr [rbx + 8], 0x3c0000`。
   - 掩码 `0x3c0000` 覆盖：
     - 交易否决权 (No-Trade Clause)
     - 新签合同 3 个月/当年不可交易期 (Recently Signed)
     - 刚被交易 2 个月内不可再次打包交易期 (Recently Traded)
     - 严重伤病禁赛限制
   - 只有全部球员均通过该掩码测试，交易才进入薪资配平校验。

2. **原生交易事务执行 (`0x132b040` / `0x1413be6e0`)**:
   - 原版函数 `0x132b040`（对应 `trade.commit_wrapper`）封装了底层事务函数 `0x1413be6e0`。
   - 事务函数接收全量交易包（包含 2 队或 3 队的转出与转入资产列表），在单个原子事务中：
     - 将各球员所属 `team_id` 指向新球队；
     - 更新对应球队选秀权所有权链；
     - 重算双方薪资与奢侈税账本；
     - 生成联盟 Trade Log 记录。

3. **CBA 薪资配平规则**:
   - 纳税球队限制：转入薪资不能超过转出薪资的 125% + 10 万美元。
   - 非纳税球队分三档（<= 6.53M 为 175% + 100k; 6.53M~19.6M 为转出 + 5.0M; >19.6M 为 125% + 100k）。

## 3. 隔离候选与验证交付
- 交付编解码器：`trade_package_codec.py`
- 交付独立测试：`pytest_gemini/test_trade_package.py` (3 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
