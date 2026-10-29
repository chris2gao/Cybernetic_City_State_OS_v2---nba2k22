# W03-08 Delivery Handoff: GM Staff & Roster Management

## 1. 范围与 20 项需求覆盖
本包全面研究并闭环了 `STAFF_AND_ROSTER` 组的 20 项需求：
- 名单激活/非激活移动与名单合法性 (`GM.ROSTER.LIST_MOVE`, `GM.ROSTER.INACTIVE_SET`, `GM.ROSTER.ROSTER_LEGALITY_READ`)
- 首发、替补、角色与位置分配 (`GM.ROSTER.STARTER_SET`, `GM.ROSTER.BENCH_ASSIGN`, `GM.ROSTER.POSITION_ASSIGN`, `GM.ROSTER.ROLE_ASSIGN`, `GM.ROSTER.ROSTER_SLOT_SWAP`)
- 下放与召回 G-League (`GM.ROSTER.G_LEAGUE_ASSIGN`, `GM.ROSTER.G_LEAGUE_RECALL`)
- 裁员与合同绑定 (`GM.ROSTER.WAIVE`, `GM.ROSTER.TEAM_ASSIGN_CONTRACT`)
- 职员池与雇佣/解雇/续约/调岗 (`GM.STAFF.STAFF_POOL_READ`, `GM.STAFF.HIRE`, `GM.STAFF.FIRE`, `GM.STAFF.EXTEND`, `GM.STAFF.REASSIGN`)
- 更换主教练、职员预算与属性 (`GM.STAFF.REPLACE_HEAD_COACH`, `GM.STAFF.STAFF_BUDGET_SET`, `GM.STAFF.STAFF_ATTRIBUTE_SET`)

## 2. 核心原生机制发现
1. **名单裁员与释放机制 (`0x12d0340` / `0x12d3d30`)**:
   - 原版函数 `0x12d0340`（对应 `team.release_internal` / `team.waive`）接收球队 Franchise 上下文与待裁球员槽位索引。
   - 读取并更新 `[TeamFranchise + 0xee8]` 处维护的激活名单计数。
   - 裁员后，球员归属 TeamID 被置为 `0xffff`（自由球员池），原槽位后面的球员前移填补空缺。
   - 名单合法性约束：常规赛期间常规名单球员必须在 13 至 15 人之间，外加最多 2 名双向合同球员（全队上限 17 人）。

2. **职员系统角色有效性与分发 (`0x1327590`)**:
   - 原版函数 `0x1327590`（对应 `staff.sign` 前置校验）严格限定职员岗位范围：
     ```assembly
     add ecx, -8
     cmp ecx, 0xc
     ja  0x1413275b4  ; 越界直接返回 0 (False)
     ```
   - 证明：职员岗位在底层以枚举 8 至 20（共 13 种职员角色）维护：
     - 8: 主教练 (Head Coach)
     - 9: 助理教练 (Assistant Coach)
     - 10: 首席球探 (Lead Scout)
     - 11: 区域球探 (Scout)
     - 12: 首席运动表现训练师 (Head Trainer)
     - 13: 助理训练师 (Trainer)
     - 14: 首席财务官 (CFO)
     - 15: GM 特别助理 (Assistant GM) 等。

## 3. 隔离候选与验证交付
- 交付编解码器：`staff_roster_codec.py`
- 交付独立测试：`pytest_gemini/test_staff_roster.py` (3 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
