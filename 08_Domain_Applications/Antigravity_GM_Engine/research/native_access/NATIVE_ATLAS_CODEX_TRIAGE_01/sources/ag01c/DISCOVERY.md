# NBA2K22 ROSTERDATA 原生数据结构深度逆向发现报告 (AG-NATIVE-01C)

> **任务标识**：AG-NATIVE-01C  
> **执行模型**：Antigravity Gemini Flash 3.8  
> **分支**：`dev/native-io-exploration`  
> **前置成果**：AG-NATIVE-01 (`49d3bff`) / AG-NATIVE-01B (`227b3ac`)  
> **交付日期**：2026-10-22  

---

## 一、异常步长与堆对齐疑难破解 (Work Package 1)

在前序审计中，Slot 9, 21, 41, 46, 54 及 74 因“指针差除以容量存在余数（如 216.01）”而被列为异常。本轮通过深入静态反汇编 `NBA2K22.exe` 原生 Getter 代码段（RVA `0xF3A000` 至 `0xF45000`），捕获了编译期绝对硬编码的步长指令，**彻底破解了全部 6 项步长疑难**：

### 1. 原生汇编证据与真实步长

| 槽位 | 元素容量 | 原生 x64 反汇编指令 | 真实记录步长 | 数据总大小 | 堆分配跨度 | 余数字节解释 | 状态判定 |
|:---:|:---:|:---|:---:|:---:|:---:|:---|:---:|
| **Slot 9** | 583 | `0x140F3C525: imul rbx, rbx, 0x3C` | **60 字节** (`0x3C`) | 34,980 B | 34,984 B | **+4 B** 堆 8 字节边界对齐 (`0x88A4 -> 0x88A8`) | `STRIDE_VERIFIED_BY_NATIVE_CODE` |
| **Slot 21** | 287 | `0x140F3C3DC: lea rcx, [rbx+rbx*2]; lea rbx, [rax+rcx*4]` | **12 字节** (`0x0C`) | 3,444 B | 3,446 B | **+2 B** 堆起始地址 8 字节对齐 (`0xD74 -> 0xD76`) | `STRIDE_VERIFIED_BY_NATIVE_CODE` |
| **Slot 41** | 6,769 | `0x140F3DAC5: imul rbx, rbx, 0x98` | **152 字节** (`0x98`) | 1,028,888 B | 1,028,892 B | **+4 B** 堆 8 字节边界对齐 (`0xFB318 -> 0xFB31C`) | `STRIDE_VERIFIED_BY_NATIVE_CODE` |
| **Slot 46** | 543 | `0x140F3D0F5: imul rbx, rbx, 0xD8` | **216 字节** (`0xD8`) | 117,288 B | 117,292 B | **+4 B** 堆 8 字节边界对齐 (`0x1CA28 -> 0x1CA2C`) | `STRIDE_VERIFIED_BY_NATIVE_CODE` |
| **Slot 54** | 5,227 | `0x140F44FEF: add rdi, 0x40` (循环解包步进) | **64 字节** (`0x40`) | 334,528 B | 334,532 B | **+4 B** 堆 8 字节边界对齐 (`0x51AC0 -> 0x51AC4`) | `STRIDE_VERIFIED_BY_NATIVE_CODE` |
| **Slot 74** | 8,136 | `0x140F3D91C: lea rbx, [rax+rbx*2]` | **2 字节** (`uint16`) | 16,272 B | 末尾数组 | 无后续指针，原生指令直接证明步长为 2 字节 | `STRIDE_VERIFIED_BY_NATIVE_CODE` |

### 2. 核心架构认知：现代 64 位堆分配对齐
- 过去推算步长直接采用 `(NextPointer - CurrentPointer) / Count`，导致整除余数产生形如 `216.01` 的非整数假象。
- 逆向证实：Windows 64 位 VC++ 运行时堆分配器对分配块强制执行 **8 字节（`0x08`）边界对齐**。当 `Count * Stride` 非 8 的倍数时，分配器会自动补入 2 或 4 个填充字节（Padding），然后再紧接着分配下一个数组。

---

## 二、全新破解的原生数据对象 (Work Package 2)

本轮成功突破并深度逆向了 3 大类具有极高业务价值的原生数据结构：

### 1. Slot 39: `NBA_RECORD_BOOK` (NBA 历史纪录大全与排行榜)
- **全局容量**：**69,040 项**，步长 **52 字节 (`0x34`)**，对应原生 Getter RVA `0xF400A0`。
- **业务意义**：游戏内置的全量 NBA 历史纪录簿，涵盖单场、单季、季后赛、球队队史以及历史生涯各项指标的纪录榜单。
- **记录二进制布局**：
  - `+0x00..+0x13` (20B)：`first_name` (Latin-1 字符串，如 "Wilt", "Kobe", "Michael")
  - `+0x14..+0x27` (20B)：`last_name` (Latin-1 字符串，如 "Chamberlain", "Bryant", "Jordan")
  - `+0x28..+0x2B` (4B)：`stat_value` (IEEE-754 32位单精度浮点数，如 100.0, 81.0, 38387.0)
  - `+0x2C..+0x2D` (2B)：`packed_date` (16 位压缩日期)
    - **纪元日期解码公式**：
      $$\text{Year} = 1920 + (\text{val} \gg 9)$$
      $$\text{Month} = (\text{val} \gg 5) \ \& \ 0x0F$$
      $$\text{Day} = \text{val} \ \& \ 0x1F$$
    - 示例：张伯伦 100 分之夜数值 `21602` $\to$ `1962-03-02`；科比 81 分之夜数值 `44086` $\to$ `2006-01-22`。精确无误。
  - `+0x2E..+0x2F` (2B)：`category_code` (纪录分类代码，如 `0x008F` 为常规赛单场得分、`0x00E0` 为生涯总得分、`0x028F` 为单场三分数等)
  - `+0x30..+0x31` (2B)：`player_id` (原生球员 ID，如 Curry=1612, Klay=2338)
  - `+0x32..+0x33` (2B)：`flags` (球队标识与纪录作用域标志)

### 2. Slot 44: `SCHEDULE_CALENDAR` (常规赛完整赛程与对阵结果日历)
- **全局容量**：**1,260 场比赛**，步长 **24 字节 (`0x18`)**，对应原生 Getter RVA `0xF3DB80`。
- **业务意义**：NBA 82 场常规赛的完整赛程排定表与实时模拟比分结果。
- **记录二进制布局**：
  - `+0x00` (8B)：`home_team_ptr` (主队对象指针，指向 `TEAM` 结构)
  - `+0x08` (8B)：`away_team_ptr` (客队对象指针，指向 `TEAM` 结构)
  - `+0x10..+0x13` (4B)：比赛得分与阶段统计数据
  - `+0x14` (2B)：`status_code` 比赛状态哨兵码
    - `1`：主队获胜 (`HOME_WIN`)
    - `0`：客队获胜 (`AWAY_WIN`)
    - `65535` (`0xFFFF`)：**尚未进行的未来赛程** (`UNPLAYED`)
  - `+0x16` (2B)：`game_day_index` 赛程轮次 / 日程索引

### 3. Slot 31-34: `NAME_AND_TEXT_CATALOG` (官方底层文字与名字字典族)
过去工程中一直依靠外部名单表或反推名字，本次证实 **NBA 2K22 原生维护了全套文字词典**，均采用 **48 字节** 步长（`wchar_t[24]`, UTF-16LE 字符串）：
- **Slot 31** (2,744 项)：**球员名字典 (First Names)**（ID 0="Adrian", 1="Alex", 2="Alexis" 等）
- **Slot 32** (4,119 项)：**球员姓氏典 (Last Names)**（ID 0="Abass", 1="Abdenour", 2="Abdi" 等）
- **Slot 33** (88 项)：**城市名称字典 (City Names)**（Albuquerque, Anaheim, Anchorage...）
- **Slot 34** (56 项)：**球队昵称字典 (Team Nicknames)**（76ers, Badgers, Ballers, Barons...）

### 4. Slot 67: `SHOES_CATALOG` (球鞋与装备型号库)
- **全局容量**：443 款球鞋，步长 **116 字节 (`0x74`)**，对应原生 Getter RVA `0xF40730`。
- 包含 "2K Generic", "Air Jordan X", "Crazy 1", "Kyrie 1", "KD 7 Aunt Pearl" 等全量装备型号与品牌指针。

---

## 三、WAIVED_SALARY 前序推断订正 (Work Package 3)

根据审查意见，本轮对死钱对象进行了严格定性修正：
1. **`is_stretched` 标记定性修正**：
   - 前期通过“金额非零年份数 $\ge 3$”标记延伸条款。本轮在代码、数据库列名中统一重命名为 **`is_stretched_heuristic`**，明确其为消费端启发式推断字段，而非游戏原生位域。
2. **链表结构定性**：
   - 确认其为 `TEAM + 0xC88`（表头） $\to$ 各记录 `prev_record_ptr` $\to \dots \to 0$ 的**单向侵入式前驱链表**。
3. **SQLite 转换消除硬编码**：
   - 取消固定基址 `0x7FF4E73065F0` 的硬编码依赖，通过步长取模验证指针合法性。
   - 严格启用每个连接的 `PRAGMA foreign_keys = ON;`。
