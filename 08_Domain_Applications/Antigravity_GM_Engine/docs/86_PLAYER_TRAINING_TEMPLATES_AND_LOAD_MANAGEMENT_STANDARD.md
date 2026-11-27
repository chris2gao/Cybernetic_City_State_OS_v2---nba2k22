# 86 球员训练模板选择与负荷管理防伤标准规范
# (Player Training Templates Selection & Load Management Standard)

> **文档标识**: `DOC-86-PLAYER-TRAINING-LOAD-MANAGEMENT-STANDARD-V1`  
> **所属系统**: Cybernetic City-State OS v2 - NBA2K22 GM Engine (`08_Domain_Applications/Antigravity_GM_Engine/`)  
> **制定时间**: 2026-11-24  
> **机制依据**: REA 原生内存数据契约 (`config/state_io_native/training.json`，偏移 `0x318` 位域打包)、人类总架构师机制裁决  
> **关联宪法**: [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) 第 5 节三大铁律  

---

## 1. 核心定位与设计哲学

球员个人训练（Individual Training）是终极联盟中决定球员**属性发展流向、徽章领悟倾向以及身体健康耐久度**的核心长周期引擎。

在传统手工管理中，逐项配置 38 项细分训练点数极其繁琐且极易导致失衡。根据 2K22 PC 本世代引擎底层机制与人类裁决，确立本规范的两大核心基石：
1. **纯模板化决策（Template-Only Principle）**：**坚决不微调 38 项具体训练子数值，仅锁定训练位置（`position`）与技术模板（`player_type`）**。2K 底层会自动激活该模板对应的成长权重，以最低的决策复杂度精准塑造球员战术定位。
2. **保守梯队负荷管理（Conservative Load Management）**：训练强度直接推高累积疲劳，而高疲劳是日历模拟发生严重伤病的核心诱因。鉴于 GM 决策在单赛季仅微调 1~3 次，强度必须采取“**年轻正常、老年轻微**”的阶梯式防伤保守方案。

---

## 2. REA 底层内存结构与打包位域 (Bitfield)

训练数据数组起始于基址 `root(0x0632B480) + 0xC60`，单个球员结构体跨度为 **796 字节**（Stride 796），通过球员真实 `native_player_id`（`+0x00` 处 4 字节）寻址。

所有个人训练配置集中打包在偏移 **`0x318`**（4 字节 uint32，小端序）的位域中：

| 字段名称 | 布局规范 | 取值范围 | 枚举定义与业务含义 |
| :--- | :---: | :---: | :--- |
| **`position`** | Bit 8..10 (宽 3 位) | `0 ~ 4` | **训练位置模板**：<br>`0`: PG (控卫) \| `1`: SG (分卫) \| `2`: SF (小前) \| `3`: PF (大前) \| `4`: C (中锋) |
| **`player_type`** | Bit 11..15 (宽 5 位) | `0 ~ 8` | **训练技术模板（核心）**：决定球员长期成长方向与预设分配 |
| **`intensity`** | Bit 16..18 (宽 3 位) | `0 ~ 5` | **训练强度**：<br>`0`: 休息 (Rest) \| `1`: 极低 (Very Low) \| `2`: 低/轻微 (Low) \| `3`: 中/正常 (Medium) \| `4`: 高 (High) \| `5`: 极高 (Very High) |
| **`injury_recovery`** | Bit 19 (宽 1 位) | `0 / 1` | 伤病康复模式标记：`1` 为伤病恢复期保护 |
| **`is_intensity_overriden`**| Bit 20 (宽 1 位) | `0 / 1` | **个人覆盖开关**：**必须置 1**，确保个人设置独立生效，不被团队全局自动化重置 |

---

## 3. 九大原生训练模板（`player_type`）配置矩阵

| 枚举值 | 英文代码 | 中文名称 | 核心技能增益流向 | 适用球员定位与经典范例 |
| :---: | :--- | :--- | :--- | :--- |
| **`0`** | `ALL_AROUND` | **全能型** | 均衡全面成长，攻防兼顾 | 全面持球大核、未确定特化方向的高顺位新秀（如东契奇、坎宁安） |
| **`1`** | `TWO_WAY` | **攻防兼备型** | 侧重外线单兵单防/锁防与定点接球三分 | 3D 侧翼、领防尖兵、防守型得分后卫（如维金斯、米卡尔·布里奇斯） |
| **`2`** | `OFFENSIVE` | **进攻型** | 得分技巧、行进间急停跳投、投篮武器库 | 纯得分手、微波炉第六人、战术主攻单打手（如拉文、CJ·麦科勒姆） |
| **`3`** | `DEFENSIVE` | **防守型** | 单防施压、抢断拦截、防守意识、横移速度 | 纯防守专家、贴身锁防后卫（如多特、贝弗利） |
| **`4`** | `ATHLETIC` | **运动型** | 速度、弹跳、力量、冲筐爆发力、身体对抗 | 身体素质出众但技术粗糙的年轻锋线/跳跳男（如库明加、杰伦·约翰逊） |
| **`5`** | `REBOUNDING` | **篮板型** | 卡位意识、拼抢进攻与防守篮板嗅觉 | 传统肉搏内线、冲抢型大前锋/中锋（如卢尼、瓦兰丘纳斯） |
| **`6`** | `PLAYMAKING` | **组织型** | 控运稳定性、护球、传球视野与阵地战发牌 | 组织指挥官、高位策应枢纽、控球后卫（如哈利伯顿、保罗） |
| **`7`** | `OUTSIDE` | **外线型** | 三分球投射、中距离投篮、接球拉开空间 | 空间型五号位、定点投手、高炮台内线（如唐斯、迈尔斯·特纳、波蒂斯） |
| **`8`** | `INSIDE` | **内线型** | 低位背身推进、禁区勾手、终结放篮与对抗 | 传统低位单打中锋、吃饼终结内线（如恩比德、祖巴茨、加福德） |

---

## 4. 梯队化保守防伤负荷管理方案 (Conservative Load Management)

### 4.1 个人训练强度划分准则
* **发育成长梯队（年龄 ≤ 24/25 岁 且身体健康）**：
  * **强度标定**：`intensity = 3 (Medium / 正常)`
  * **设计目的**：赋予年轻球员充沛的成长点数积累，同时避免进入 `High / Very High` 带来的体能过载与疲劳激增，实现安全成长。
* **巅峰与定型老将梯队（年龄 ≥ 26/28 岁 或 长期核心负荷者）**：
  * **强度标定**：`intensity = 2 (Low / 轻微)`
  * **设计目的**：老将技术模型已经定型，高强度训练无法带来实质成长反而迅速累积疲劳。轻微强度能显著削减日历模拟中发生韧带、骨折等退役大伤的概率。
* **高危伤病与康复梯队（历史大伤体质、玻璃人、刚复出球员）**：
  * **强度标定**：`intensity = 1 (Very Low / 极低)` 或 `0 (Rest)`，同时置 `injury_recovery = 1`。
  * **设计目的**：以养生与体能储备为主，确保在季后赛等关键节点具备最高出勤可用性。
* **个人覆盖开关**：
  * **铁律**：所有单独配置了强度的球员，**必须设置 `is_intensity_overriden = 1`**。

### 4.2 团队层级双重防伤保护锁
在各队团队训练结构体（Stride 88）中，强制激活以下保护：
* `rest_before_b2b` (偏移 `0x54` bit 4) = `1`：背靠背赛前全队休息；
* `rest_after_b2b` (偏移 `0x54` bit 5) = `1`：背靠比赛后全队休息。

---

## 5. 执行包落地协议格式规范 (遵循 Doc 43 V2)

执行包保存路径：`C:\nba2k22\exports\YYYYMMDD_player_training_execution\<team_idx>_<TEAM>_training_mod.json`

```json
{
  "task_metadata": {
    "task_id": "CYCLE_02_PLAYER_TRAINING_FOCUS",
    "team_id": 14,
    "team_name": "Indiana Pacers",
    "protocol_version": "v2_sparse_delta",
    "generated_at": "2026-11-24"
  },
  "player_training_updates": [
    {
      "player_id": 1630169,
      "player_name": "Tyrese Haliburton",
      "age": 22,
      "training_deltas": {
        "position": 0,
        "player_type": 6,
        "intensity": 3,
        "is_intensity_overriden": 1
      },
      "comment": "年轻核心(22岁)，PG+组织型模板，正常强度(Medium)保障成长"
    },
    {
      "player_id": 1626167,
      "player_name": "Myles Turner",
      "age": 26,
      "training_deltas": {
        "position": 4,
        "player_type": 7,
        "intensity": 2,
        "is_intensity_overriden": 1
      },
      "comment": "空间中锋(26岁)，C+外线型模板，轻微强度(Low)防疲劳控伤病"
    }
  ]
}
```

---

## 6. 上游输入与当前赛季战术报告动态绑定准则 (Upstream Season Alignment)

* **直承当季战术手册报告，免除重复分析**：
  每次执行球员训练模板与负荷管理任务时，免除从零重复阵容分析，**必须以任务启动时所属的当前活动赛季（Current Active Season）为准**，直接读取该赛季战术手册专项任务（Doc 96/97）产出的单队报告（`docs/tactical_designs_<SEASON>/<TEAM>_<SEASON>_TACTICAL_DESIGN_REPORT.md`）；
* **单季时效与年度动态轮转**：
  战术设计报告**仅在当前赛季有效**，每个新赛季揭幕日均会重新执行并生成全新目录与报告。严禁硬编码某一固定历史年份（如 `2022_2023`，新赛季必须读取新赛季新目录）；直接提取当季报告中对球员的年龄、战术角色（持球大核、3D、高位中轴、传统内线）定位，快速映射九大训练模板并配置梯队防伤强度（年轻正常=3，老年轻微=2）。
