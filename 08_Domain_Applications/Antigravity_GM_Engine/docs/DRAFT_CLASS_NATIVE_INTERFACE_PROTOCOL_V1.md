# NBA 2K22 历史选秀名单 REA Native 批量注入标准接口协议 (v2.2 全维真实化与槽位定位规范)
# (Draft Class REA Native Batch Modification Interface Protocol Specification v2.2)

> **协议标识 (Protocol ID)**: `SPEC-DRAFT-CLASS-NATIVE-MOD-V2.2`  
> **适用版本**: NBA 2K22 (Steam PC x64) | 引擎底层: `NBA2K22.exe`  
> **适用业务**: 任意历史年份选秀名单（1984、1985、1992、1996、2003 等）的全量 60 槽位工业化重构、缺失传奇补齐、以及**全名单效力 $\ge 7$ 年球星的新秀全维真实化（能力/潜力/倾向/徽章/战术动作）**与 Native 批量热注入。  
> **对接角色**:  
> - **规划与决策方**: `role-planner` / `data_analysis_and_decision` (数据分析、真实化建模与差分规格制定)  
> - **执行与核验方**: `role-developer` / `batch_executor` (REA Native / 内存直写与 CAS 回读校验)  

---

## 一、 协议核心设计原则与六大宪法守则 (Constitutional Principles)

为确保全量 60 名新秀在实机运行内存与底层存档数据库中 100% 稳定生效，杜绝任何闪退、身材畸形，彻底解决**“选秀年份偏移错误”、“活动槽位寻址错位”与“皮包骨匿名泥人”**问题，所有年份选秀数据包必须无条件遵循以下六大守则：

### 1. 选秀池活动槽位寻址与排重原则 (Active Draft Pool Slots vs. Historical Vault)
在 2K22 底层架构中，选秀池与历史球星名宿库采用**分段寻址机制**（步长 `0x4F0` = 1,264 字节）：
- **活动选秀池固定物理槽位 (`Slot 590 ~ 649`)**：
  - 在 MyLEAGUE 模式中，当前赛季正在进行的选秀名单（如 1984 届）固定映射在全局球员池数组的 **`Slot 590 ~ 649`（共 60 个槽位）**；
  - 游戏 UI 中的“球探 (Scouting) - 选秀名单”只读取此活动槽位区间；
  - **历史传奇常驻底库 (`Slot 3190 ~ 3250`)** 是 2K22 原生只读的全局名宿模板库（如 Slot 3191 是乔丹模板，Slot 3195 是斯托克顿模板），但**不是活动选秀池**！执行模型严禁误将选秀名单写入 3190+ 槽位，必须定位并写入 `Slot 590 ~ 649`。

### 2. 选秀年份物理偏移量绝对校验守则 (Draft Year Offset `0x179` Hard Rule)
- 2K22 球员结构体中，选秀年份的唯一物理偏移量为 **`0x179`**（单字节 `uint8`，存储相对于 1900 年的偏移，即 $1984 - 1900 = 84 = \text{0x54}$）；
- **严禁写入 `0x0FA`**：`0x0FA` 为无关属性字节，写入不仅会破坏原有属性，而且会导致 `0x179` 处的年份依然停留在 2023（`123`），造成游戏引擎在加载 1984 选秀名单时直接在底层将球员过滤剔除；
- 执行端在 CAS 回读验证时，必须硬性断言：`1900 + mem.read_bytes(slot_addr + 0x179, 1)[0] == target_draft_year`！

### 3. 官方自带球星“身份骨骼绝对保护 + 数值倾向真实化重塑”双轨准则
- **解除只读限制**：2K 官方已经在该年份选秀名单中内置的真实球星（例如 1984 届的乔丹、奥拉朱旺、斯托克顿；1996 届的科比、艾弗森等），**正式解除原纯只读锁定**！
- **身份与骨骼绝对保护（红线）**：必须保留官方原生球星的真实姓名、面补 ID、`0x90` 独立外观堆指针（`APPEARANCEDATA`）；**严禁按选秀顺位强行重排球员槽位**（选秀顺位由游戏休赛期选秀大会各队 AI 依据实时需求自主抽取）。
- **全维数值真实化**：针对官方自带球星普遍存在的“套用巅峰属性、三分虚高、犯规率过高、无战术发起权”等时代失真，必须依据其真实新秀赛季客观档案，对其攻防属性、战术倾向（99 维）、技能等级徽章及战术手册（`tactical_playbook`）进行精准真实化重塑。

### 4. 杜绝“皮包骨错位”：泥人槽位全量身份与全维真实化合并交付铁律
- 原始存档中 `Slot 596 ~ 649` 初始状态为随机生成的匿名泥人（Face ID = 1）；
- **严禁只打差分数值补丁而不写身份字段**！若只写入属性倾向差分，球员在游戏中依然叫泥人名字、长着泥人面孔；
- 交付给执行端的选秀规格书，必须是将**“泥人全量身份置换（姓名、面补 ID、0x179 年份、位置、159 字节动作包、等级徽章纯净化）”**与**“老将真实感数值倾向差分”**完全融合的**统一主规格书**（如 `1984_draft_enhancement_spec.json`）。

### 5. 《新时代架空三分投射校准准则》与《跨时代攻防真实能力归一化标准》
- **新时代架空三分投射**：以真实中距离跳投（Mid-Range）与罚球命中率（FT%）作为纯投射手感锚点，推导合理新秀三分能力；
  - 乔丹（84.5% FT）标定 72 三分、倾向 25；斯托克顿（38.4% 历史三分+84%+ FT）标定 75 三分、倾向 30；帕金斯（80.6% FT）标定 70 三分、倾向 35；
  - 新秀阶段严格控制在 70~75 区间保成长；纯内线与非射手（大梦、索普、威利斯、凯奇、麦考密克、格雷）三分倾向彻底清零。
- **跨时代攻防归一化**：
  - 消除 80 年代规则与节奏噪音，转换为 Per-36 分钟折算并还原真实防守压迫感与身体天赋（如罗伯特森抢断 95、死亡缠绕金）；
  - **常规犯规安全锁（Foul <= 45）**：全员 100% 压制至 40~45，彻底消除 6 犯毕业失真；
  - **战术核心重力与发起权**：按战术地位赋予 `touches`（乔丹 95、斯托克顿 85、大梦 88、巴克利 82），后场核心配置 `is_play_initiator: 1` 与专属 4 槽位 `play_types`。

### 6. 双端原子落盘与 SQLite 全量字段同步 (Dual-End Atomic Commit)
- 数据包必须同时提交至**实时运行内存 (`NBA2K22.exe` RAM)** 与 **存档数据库 (`player_pool.sqlite`)**；
- 必须同步更新 SQLite 表中的 `first_name`, `last_name`, `full_name`, `cyberface_id`, `draft_year`, `position`, `potential`, `raw_struct`，防止 MyLEAGUE 日程推进或菜单切换触发读盘覆写回滚。

### 7. 球员结构体不可篡改“三不动基石”防闪退宪法 (Three Immutable Anchors: `0x88`, `0x90`, `0xF4`)
- 任何选秀球员或现役球员结构体重构，必须在装配前备份并在生成目标结构体时 100% 原样保留以下三个关键偏移：
  1. **`0x88`**（HeadMorph 头部雕刻与微变形指针）；
  2. **`0x90`**（AppearanceData 独立外观堆指针，单人步长为 0x40 字节）；
  3. **`0xF4`**（UniqueId 球员运行时唯一标识）。
- **日历模拟零崩溃防线**：游戏引擎读档时将 `0xF4` 注册入 `[rdi + 0x220]` 全局哈希表。若新秀或球星 `0xF4` 被清零，日历模拟推进至该球员时必触发空指针闪退（CTD）。执行端装配器必须硬性保护 `0xF4`，CAS 回读必须断言 `rb_f4 != 0`！

---

## 二、 槽位定位对照速查表 (1984 届标杆案例)

| 槽位区间 | 槽位性质 | 预设初始状态 | 注入与真实化处理准则 | 校验要求 |
| :---: | :---: | :---: | :--- | :--- |
| **`Slot 590 ~ 595`** | **官方自带球星区** | 2K 官方原生名宿 (奥拉朱旺、乔丹、帕金斯、索普、威利斯、斯托克顿) | **双轨处理**：保留原生姓名、原生面补 ID、`0x90` 外观指针；覆写 `0x179` 选秀年份(84)、全维攻防属性、新时代架空三分、犯规安全锁、战术发起权与徽章。 | `rb_face == orig_face`<br>`rb_yr == 1984`<br>`rb_foul <= 45` |
| **`Slot 596 ~ 649`** | **历史传奇补齐区** | 游戏引擎随机泥人 (Face ID = 1, 选秀年份 2023) | **全量重构+真实化**：覆写 UTF-16LE 姓名、官方真实面补 ID、`0x179` 选秀年份(84)、真实位置、`0x90` 指针保留、159 字节技术动作包、等级徽章按位纯净化并写入目标徽章、全维攻防倾向。 | `rb_name == spec_name`<br>`rb_face == spec_face`<br>`rb_yr == 1984`<br>`rb_foul <= 45` |
| **`Slot 3190 ~ 3250`**| **历史名宿模板库** | 2K22 全局名宿只读模板 (非活动选秀池) | **只读审计区**：严禁作为选秀名单修改目标写入。 | 只读，不覆写 |

---

## 三、 标准化合并规格书 JSON Schema (Machine-Ready Master Spec)

执行模型在执行选秀任务时，必须优先加载全量合并主规格书（`C:\nba2k22\exports\<YEAR>_draft_enhancement_spec.json`）：

```json
{
  "protocol_version": "v2.2_full_dimensional_realism_reconstructed",
  "draft_year": 1984,
  "target_career": "MyLEAGUE0005",
  "total_slots": 60,
  "slot_range": [590, 649],
  "prospects": [
    {
      "slot_id": 591,
      "first_name": "Michael",
      "last_name": "Jordan",
      "full_name": "Michael Jordan",
      "position": 1,
      "position_name": "SG",
      "face_id": 1759,
      "draft_year": 1984,
      "is_official_preserved": false,
      "potential": 99,
      "attributes": {
        "mid_range": 92,
        "three_point": 72,
        "driving_layup": 94,
        "driving_dunk": 95,
        "free_throw": 85,
        "speed": 94,
        "pass_iq": 80,
        "pass_vision": 78,
        "steal": 88
      },
      "tendencies": {
        "shot": 92,
        "shot_mid_range": 95,
        "shot_three": 25,
        "touches": 95,
        "foul": 42
      },
      "tactical_playbook": {
        "is_play_initiator": 1,
        "play_types": [1, 3, 4, 11]
      }
    },
    {
      "slot_id": 623,
      "first_name": "Charles",
      "last_name": "Barkley",
      "full_name": "Charles Barkley",
      "position": 3,
      "position_name": "PF",
      "face_id": 2001,
      "draft_year": 1984,
      "is_official_preserved": false,
      "potential": 97,
      "animation_block_hex": "...",
      "personality_hex": "...",
      "attributes": {
        "three_point": 48,
        "off_rebound": 94,
        "def_rebound": 95,
        "strength": 96
      },
      "tendencies": {
        "touches": 82,
        "foul": 45
      },
      "badges": {
        "ReboundChaser": 2,
        "Box": 2
      }
    }
  ]
}
```

---

## 四、 执行模型必须遵守的防错核验法则 (Zero-Error Defense Rules)

1. **绝对偏移量基准**：选秀年份偏移量代码中必须且只能引用 `OFF_DRAFT_YEAR = 0x179`；
2. **槽位面补与身份哨兵**：若检测到 `Slot 596 ~ 649` 处于泥人状态（Face ID = 1），必须执行全量身份写入，严禁单向跳过姓名面补只写属性；
3. **CAS 双端核验通过标准**：
   - 60 / 60 槽位核验通过；
   - 60 / 60 槽位内存与数据库 `0x179` 均等于目标选秀年份（如 1984）；
   - 60 / 60 槽位 `foul <= 50`；
   - 60 / 60 槽位 `0xF4` 唯一 ID 均不为 0（`rb_f4 != 0`），且 `0x88`/`0x90` 指针完好；
   - 0 读写异常。
