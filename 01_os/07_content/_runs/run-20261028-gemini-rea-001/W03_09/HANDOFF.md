# W03-09 Delivery Handoff: Draft, Picks & Scouting

## 1. 范围与 24 项需求覆盖
本包全面研究并闭环了 `DRAFT_SCOUT_AND_PICK_RIGHTS` 组的 24 项需求：
- 候选新秀列表与详细资料 (`PROSPECT_LIST`, `PROSPECT_PROFILE`)
- 球探目标追加与替换 (`GOAL_APPEND`, `GOAL_REPLACE`)
- 球探出差、进度与报告 (`SCOUT_EXECUTE`, `SCOUT_PROGRESS`, `SCOUT_REPORT`, `SCOUT_PRIORITY`, `SCOUT_AUTOMATION`, `SCOUT_STAFF_ASSIGN`)
- 联合试训与体检报告 (`WORKOUT_ASSIGN`, `SCOUT.MEDICAL_REPORT`)
- 自定义大榜查看与设定 (`BIG_BOARD_VIEW`, `BIG_BOARD_SET`)
- 选秀顺位读取与选定新秀 (`CURRENT_PICK_READ`, `DRAFT_SPECIFIED`)
- 选秀权归属、保护条款与转让 (`PICK_OWNER_READ`, `PICK_RIGHTS_TRANSFER`)
- 乐透抽签与选秀结果 (`LOTTERY_READ`, `DRAFT_RESULT_READ`)
- 新秀名单管理与海外签约权保留 (`DRAFT_CLASS_SET`, `DRAFT_CLASS_IMPORT`, `DRAFT_CLASS_EDIT`, `DRAFT_RIGHTS_STASH`)

## 2. 核心原生机制发现
1. **选秀权元数据位段 (`0x92a6a0`)**:
   - 原版函数 `0x92a6a0`（对应 `draft.current_selection`）调用 `0x14092a170` 获取选秀权指针，并校验 `[DraftPick + 0x1c]` 处的元数据字：
     - Bits 0..7: 拥有者球队 ID (`owning_team_id`)
     - Bits 8..15: 顺位索引 (`pick_index` 1..30)
     - Bits 16..18: 轮次 (`round_num` 1..2)
     - Bits 19..22: 保护条款 (`protection` 如前三保护、前五保护、乐透保护等)
   - 证明：选秀权的权属与保护条款采用统一 32 位整型维护。

2. **选秀执行事务 (`0xec9610`)**:
   - 原版函数 `0xec9610`（对应 `draft.select`）接收待选新秀指针与选秀权上下文。
   - 若选秀权参数为 NULL，函数自动调用 `0x140eca640` 读取当前激活轮次与顺位（`[rax + 0xbc]`, `[rax + 0xc0]`），并将新秀归属正式赋予选秀权拥有球队，触发选秀动画和事件分发。

3. **球探出差执行与精力预算 (`0x1261d40`)**:
   - 原版函数 `0x1261d40`（对应 `scout.execute_trip`）读取 `[ScoutContext + 0x1068]` 的第 15 至 18 位以验证剩余出差精力/预算，随后步进球探完成度并解锁对应新秀的真实能力评级与倾向。

## 3. 隔离候选与验证交付
- 交付编解码器：`draft_scout_codec.py`
- 交付独立测试：`pytest_gemini/test_draft_scout.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
