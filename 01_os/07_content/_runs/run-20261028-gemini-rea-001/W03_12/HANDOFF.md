# W03-12 Delivery Handoff: Native Getter and Readback Catalog

## 1. 范围与目标
作为 Wave-03 的关键读回支撑包，本包建立了专为 GM 与 Coach 第一版决策输入与后置验证服务的全域 Native Getter 目录，涵盖 6 大核心领域：
- 球员基础与统计 (`Player Getters`)
- 教练与战术大纲 (`Coach & Gameplan Getters`)
- 战术书与战术项 (`Playbook Getters`)
- 名单与职员 (`Roster & Staff Getters`)
- 合同与自由球员 (`Contract & Free Agency Getters`)
- 选秀与球探 (`Draft & Scouting Getters`)

## 2. 核心原生只读接口发现
1. **球员核心只读流水线**:
   - `player.by_id` (`0xf3fa80`): 根据球员 ID 查询 64 位实体指针。
   - `player.get_stat` (`0x978360`): 读取 155 项属性与倾向。
   - `player.get_badge_level` (`0x97b870`): 查询指定徽章的实际生效等级 (0..4)。
   - `player.get_salary` (`0x9888b0`): 读取当年薪资。
   - `player.get_contract_years` (`0x9886c0`): 读取剩余合同年限。
   - `player.get_roster_slot` (`0xedf000`): 读取名单深度图槽位 (0..14)。
   - `player.get_minutes` (`0x11b2bb0` 读取): 读取分配的轮换分钟数 (0..48)。
   - `player.get_playtypes` (`0xf1e370` 对应字段): 读取 4 个有序战术类型 (16 位打包半字节)。

2. **教练与战术只读流水线**:
   - `coach.get_coachdata` (`0x1409cd2a0`): 获取当前球队的活动教练执行上下文指针。
   - `coach.get_default_gameplan` (`TeamFranchise + 0x7854`): 读取 880 字节默认战术大纲。
   - `coach.get_dirty_flags` (`TeamFranchise + 0x7bc4`): 读取战术与设置刷新脏标记。
   - `coach.get_poe_settings` (`COACHDATA + 0x13c`): 读取 6 项 5 位 POE 压缩设置。
   - `coach.get_tactical_system` (`COACHDATA + 0x148` bits 17..24): 读取战术体系枚举。

3. **战术书、名单、合同与选秀只读接口**:
   - `playbook.get_count` (`0x149ae80`): 读取当前战术书分配数量（上限 68）。
   - `team.get_roster_count` (`TeamFranchise + 0xee8`): 读取激活球员人数。
   - `sign.get_fa_count` (`0x9b5bf0`): 读取可用自由球员总数。
   - `franchise.get_season_phase` (`0x140edf010`): 读取赛季进行阶段（如选项阶段 0x16）。
   - `draft.get_current_pick` (`0x92a6a0`): 读取当前选秀大会顺位与选秀权元数据。
   - `scout.get_trip_budget` (`ScoutContext + 0x1068` bits 15..18): 读取球探出差精力预算。

## 3. 隔离候选与验证交付
- 交付目录模块：`native_getter_catalog.py`
- 交付独立测试：`pytest_gemini/test_native_getters.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
