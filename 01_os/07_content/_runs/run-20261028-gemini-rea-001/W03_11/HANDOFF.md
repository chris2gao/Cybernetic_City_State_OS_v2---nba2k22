# W03-11 Delivery Handoff: Player Tendencies & 4 PlayTypes

## 1. 范围与 16 项需求覆盖
本包全面研究并闭环了 `PLAYER_EDIT_REMAINING` 组中与教练管辖相关的 16 项需求：
- 单项与批量属性更新 (`PLAYER.EDIT.ATTR_SET`, `PLAYER.EDIT.ATTR_BATCH`)
- 单项与批量倾向更新 (`PLAYER.EDIT.TENDENCY_SET`, `PLAYER.EDIT.TENDENCY_BATCH`)
- 徽章等级设定与移除 (`PLAYER.EDIT.BADGE_SET`, `PLAYER.EDIT.BADGE_REMOVE`)
- 四项有序战术类型指定 (`PLAYER.EDIT.PLAY_TYPE_1`, `PLAYER.EDIT.PLAY_TYPE_2`, `PLAYER.EDIT.PLAY_TYPE_3`, `PLAYER.EDIT.PLAY_TYPE_4`)
- 战术发起者标志 (`PLAYER.EDIT.PLAY_INITIATOR`)
- 球员基本资料、体能上限、伤病状态、潜力与 DNA (`PLAYER.EDIT.PLAYER_VITALS`, `PLAYER.EDIT.DURABILITY_SET`, `PLAYER.EDIT.INJURY_STATUS`, `PLAYER.EDIT.POTENTIAL_SET`, `PLAYER.EDIT.DNA_IMPORT`)

## 2. 核心原生机制发现
1. **4 项战术类型打包半字节（Nibble）架构 (`0xf1e370`..`0xf1e3e0`)**:
   - 游戏在球员结构体偏移 `+0x168` 处维护一个 16 位整型，由 4 个 4 位半字节构成：
     - Bits 0..3: PlayType 1 (`0xf1e370`)
     - Bits 4..7: PlayType 2 (`0xf1e390`)
     - Bits 8..11: PlayType 3 (`0xf1e3b0`)
     - Bits 12..15: PlayType 4 (`0xf1e3d0`)
   - 对应原生反汇编证实：原版提供了 4 个微型 Setter，分别使用掩码 `0xfffffff0`、`0xffffff0f`、`0xfffff0ff`、`0xffff0fff` 与位移（0, 4, 8, 12 位）进行读写。
   - 战术类型值域涵盖：0=None, 1=ISO, 2=P&R Handler, 3=P&R Roll, 4=Post Up Low, 5=Post Up High, 6=Guard Post Up, 7=Cutter, 8=Handoff, 9=Mid Range, 10=3PT, 11=ISO 3PT, 12=Catch & Shoot。

2. **155 项属性与倾向跳转表 (`0x990a10`)**:
   - 原版函数 `0x990a10`（对应 `player.set_stat_ui`）通过 `cmp ebp, 0x9b`（155 decimal）校验属性/倾向索引。
   - 通过基址相对寻址的跳转表直接索引并分发至对应字段的写入例程。

3. **徽章系统等级设定 (`0x992d40`)**:
   - 原版函数 `0x992d40`（对应 `player.set_badge`）接受球员指针、徽章 ID 与等级字节（0..4）。
   - 等级 0 直接解除并移除该徽章，等级 1..4 分别对应铜、银、金、名人堂等级。

## 3. 隔离候选与验证交付
- 交付编解码器：`player_playtypes_codec.py`
- 交付独立测试：`pytest_gemini/test_player_playtypes.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
