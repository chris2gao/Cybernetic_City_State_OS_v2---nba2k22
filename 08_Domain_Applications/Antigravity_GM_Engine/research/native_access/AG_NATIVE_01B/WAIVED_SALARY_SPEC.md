# WAIVED_SALARY (被裁球员分摊死钱) 原生数据结构深度逆向规范 (AG-NATIVE-01B)

> **对象类型**：`WAIVED_SALARY`  
> **分类归属**：`FINANCE_DEAD_CAP` (终极联盟财务与薪资帽管理)  
> **记录步长**：**136 字节 (`0x88`)**  
> **全局容量**：222 槽位  
> **实机活跃数**：32 条记录 (覆盖全联盟 16 支具有历史死钱的球队)  
> **验证状态**：`STRUCTURE_VERIFIED` / `CROSS_SESSION_VERIFIED`  

---

## 1. 业务背景与游戏原生作用

在 NBA 劳资协议（CBA）及 NBA 2K22 MyLEAGUE 模式中，当球队使用延伸条款（Stretch Provision）裁掉具有保障合同的球员，或者买断球员（Buyout）时，剩余保障薪资将在未来 1 至 6 个赛季内计入球队工资帽，称为“死钱（Dead Cap / Waived Salary）”。

在过去工程中，项目仅采集了 30 队常规大名单内球员的本季薪资，导致死钱未被纳入考量（例如活塞队仅格里芬一人即占有近 3000 万美元死钱空间）。本模块完整逆向并实现了对游戏原生死钱账本的只读访问。

---

## 2. 原生二进制结构字段定义 (136 字节)

通过对 222 个槽位及对应 32 条活跃记录的二进制对照分析，完整还原的结构体布局如下：

| 字节偏移 | 字段名 | 原生类型 | 解码规则 / 含义说明 | 样本取值示例 |
| :---: | :---: | :---: | :--- | :--- |
| `+0x00` | `prev_record_ptr` | `uint64_t` | **同队死钱侵入式双向链表的前驱指针**。若为 0 表示链表尾部（最后一项） | `0x7FF4E7C3E180` 或 `0x0` |
| `+0x08` | `team_ptr` | `uint64_t` | **所属球队对象指针**。指向 `TEAM` 数组中对应队伍基址 | `0x7FF4E730AF50` (凯尔特人) |
| `+0x10` | `season_1_amount`| `uint32_t` | **第 1 赛季 (当前赛季) 死钱金额** (美元) | `92857` ($92,857) |
| `+0x14` | `season_2_amount`| `uint32_t` | **第 2 赛季 (下一赛季) 死钱金额** (美元) | `92857` ($92,857) |
| `+0x18` | `season_3_amount`| `uint32_t` | **第 3 赛季死钱金额** (美元) | `92857` ($92,857) |
| `+0x1C` | `season_4_amount`| `uint32_t` | **第 4 赛季死钱金额** (美元) | `0` |
| `+0x20` | `season_5_amount`| `uint32_t` | **第 5 赛季死钱金额** (美元) | `0` |
| `+0x24` | `season_6_amount`| `uint32_t` | **第 6 赛季死钱金额** (美元) | `0` |
| `+0x28..33`| `waiver_flags` | `uint8_t[12]`| 裁决状态标志位、分摊属性、延伸条款标识位 | `[0, 0, ...]` |
| `+0x34` | `player_id` | `uint16_t` | **球员原生档案 ID** (若为自由球员或历史特例可能为 0) | `1530` (Batum), `1600` (Griffin) |
| `+0x36` | `sentinel` | `uint16_t` | 结构边界哨兵码，固定为 `0xFFFF` | `0xFFFF` |
| `+0x38..5F`| `last_name` | `wchar_t[20]`| **球员姓氏** (UTF-16LE 字符串，最大 20 字符 / 40 字节) | `Jackson`, `Batum`, `Griffin` |
| `+0x60..7F`| `first_name` | `wchar_t[16]`| **球员名字** (UTF-16LE 字符串，最大 16 字符 / 32 字节) | `Demetrius`, `Nicolas`, `Blake` |
| `+0x80..87`| `reserved` | `uint64_t` | 尾部内存对齐保留区 (全零) | `0x0` |

---

## 3. 关联关系与双向导航机制

游戏为死钱数据提供了两种原生寻址途径：

### 3.1 途径一：全局线性数组直接索引
- 通过 `ROSTERDATA` 描述符 Slot 61（原生偏移 `+0x3D0`），直接获取 `pWaivedSalary` 基址。
- 原生 Getter：`ROSTERDATA::GetWaivedSalaryByIndex` (RVA `0xF3C790`)。
- 寻址方程：`Record = pWaivedSalary + Index * 136` ($O(1)$ 复杂度)。

### 3.2 途径二：球队侵入式链表 (Intrusive Linked List)
- 在 `TEAM` 结构体中（步长 4696 字节），偏移 **`+0xC88`** 存储了该球队专属死钱链表的**表头指针（Head Pointer）**。
- 链表遍历规则：
  ```
  TEAM + 0xC88 ────> WaivedRecord_A (Head)
                          │
                          ├────> prev_record_ptr (+0x00) ────> WaivedRecord_B
                          │                                         │
                          │                                         └────> 0x0 (Tail)
                          │
                          └────> team_ptr (+0x08) ─────────────> 回指 TEAM
  ```
- **实测一致性验证**：对 30 支球队遍历 `TEAM + 0xC88` 收集到的记录集，与全局线性扫描提取到的 32 条活跃记录集**100% 互素重合，顺序与指针完全闭环**。

---

## 4. 实机代表性真实数据样本 (已脱敏)

从当前运行游戏进程（2021-22 赛季）提取并验证的代表性死钱样本如下：

```json
[
  {
    "slot_index": 11,
    "team_index": 13,
    "team_name": "Los Angeles Lakers",
    "full_name": "Luol Deng",
    "player_id": 0,
    "season_1_amount": 5000000,
    "season_2_amount": 0,
    "season_3_amount": 0,
    "total_dead_cap": 5000000,
    "remaining_seasons": 1,
    "is_stretched": 0,
    "note": "湖人队历史上最著名的延伸买断合同 (本季为最后一年 $5,000,000)"
  },
  {
    "slot_index": 7,
    "team_index": 20,
    "team_name": "Detroit Pistons",
    "full_name": "Blake Griffin",
    "player_id": 1600,
    "season_1_amount": 29764126,
    "season_2_amount": 0,
    "season_3_amount": 0,
    "total_dead_cap": 29764126,
    "remaining_seasons": 1,
    "is_stretched": 0,
    "note": "活塞队买断格里芬产生的巨额一次性死钱 ($29,764,126)"
  },
  {
    "slot_index": 2,
    "team_index": 9,
    "team_name": "Charlotte Hornets",
    "full_name": "Nicolas Batum",
    "player_id": 1530,
    "season_1_amount": 8856969,
    "season_2_amount": 8856969,
    "season_3_amount": 0,
    "total_dead_cap": 17713938,
    "remaining_seasons": 2,
    "is_stretched": 0,
    "note": "黄蜂队裁掉巴图姆分摊死钱 (剩余 2 季，每季 $8,856,969)"
  },
  {
    "slot_index": 0,
    "team_index": 4,
    "team_name": "Boston Celtics",
    "full_name": "Demetrius Jackson",
    "player_id": 0,
    "season_1_amount": 92857,
    "season_2_amount": 92857,
    "season_3_amount": 92857,
    "total_dead_cap": 278571,
    "remaining_seasons": 3,
    "is_stretched": 1,
    "note": "凯尔特人队长期延伸死钱 (持续 3 季，每季 $92,857)"
  },
  {
    "slot_index": 13,
    "team_index": 1,
    "team_name": "Milwaukee Bucks",
    "full_name": "Larry Sanders",
    "player_id": 0,
    "season_1_amount": 1865546,
    "season_2_amount": 0,
    "season_3_amount": 0,
    "total_dead_cap": 1865546,
    "remaining_seasons": 1,
    "is_stretched": 0,
    "note": "雄鹿队历史桑德斯买断分摊死钱 (本季最后一年 $1,865,546)"
  }
]
```
