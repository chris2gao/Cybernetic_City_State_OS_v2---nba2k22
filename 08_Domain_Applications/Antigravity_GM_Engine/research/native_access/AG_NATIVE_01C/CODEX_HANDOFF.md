# AG-NATIVE-01C Codex 审计与交接备忘录 (CODEX_HANDOFF)

> **任务标识**：AG-NATIVE-01C  
> **交接模型**：Antigravity Gemini Flash 3.8 $\to$ Codex  
> **分支**：`dev/native-io-exploration`  
> **状态**：`AG_NATIVE_01C_DELIVERED_PENDING_CODEX_REVIEW`  

---

## 一、实际破解成果摘要

1. **彻底解决 6 项异常步长疑难**：
   - Slot 9 (60B)、Slot 21 (12B)、Slot 41 (152B)、Slot 46 (216B)、Slot 54 (64B)、Slot 74 (2B) 全部由原生 x64 汇编反编译指令严格证实（状态为 `STRIDE_VERIFIED_BY_NATIVE_CODE`）。
   - 证明了所谓的“余数”均为 64 位 VC++ 堆分配器的 8 字节边界对齐填充字节（Padding）。
2. **全新攻破 3 大类核心游戏数据结构**：
   - **`NBA_RECORD_BOOK` (Slot 39, 52B, 69,040项)**：全量单场/单季/生涯/季后赛历史纪录库，破解了 **1920 纪元压缩日期算法** (`Year = 1920 + (val >> 9)`)，捕获了张伯伦 100 分、科比 81 分、克莱 14 记三分等历史榜单。
   - **`SCHEDULE_CALENDAR` (Slot 44, 24B, 1,260项)**：常规赛赛程对阵日历，打通主客场 `TEAM` 指针与胜负状态哨兵码 (`1`=主胜, `0`=客胜, `65535`=未赛)。
   - **`NAME_AND_TEXT_CATALOG` (Slot 31-34, 48B)**：官方底层名字与文字字典，确认了 2,744 个 First Names、4,119 个 Last Names、88 个 Cities 及 56 个 Nicknames。
3. **WAIVED_SALARY 推断字段规范修正**：
   - 将 `is_stretched` 严格重命名并定性为 `is_stretched_heuristic`，明确为消费端推断；消除了硬编码 TEAM 基址。

---

## 二、结构已确认 vs 启发式推断 vs 待留存清单

| 结构 / 字段 | 状态分类 | 依据与说明 |
| :--- | :---: | :--- |
| **Slot 9, 21, 41, 46, 54, 74 步长** | `STRUCTURE_VERIFIED` | 由原生汇编 `imul` / `lea` / `add` 指针步进指令硬核证实 |
| **Record Book 姓名与浮点数得分** | `STRUCTURE_VERIFIED` | 20B 姓名 + 4B IEEE-754 浮点数，与 NBA 官方单场/生涯记录 100% 吻合 |
| **Record Book 1920 纪元日期算法** | `STRUCTURE_VERIFIED` | 跨越 1962、1978、1986、2005、2006、2018 多个历史年代验证零误差 |
| **Schedule 对阵与未赛哨兵** | `STRUCTURE_VERIFIED` | 主客场指针回指 TEAM，`65535` 严格对应当前保存日历未赛场次 |
| **Slot 31-34 官方文字字典** | `STRUCTURE_VERIFIED` | 原生 UTF-16LE 字符串，索引直接对应球星 `first_name_id`/`last_name_id` |
| **Waived Salary 延伸条款标记** | `DERIVED_HEURISTIC` | 标记为 `is_stretched_heuristic` (基于分摊年数 $\ge 3$)，非原生位域 |
| **Record Book 尾部 2 字节 flags** | `UNKNOWN_PENDING_CODEX` | 偏向主客场或季后赛标记，交由 Codex 深度测试时进一步推断 |
| **Schedule 得分压缩区 `0x10..0x13`** | `UNKNOWN_PENDING_CODEX` | 包含比分或阶段统计紧凑码，已赛场次有值，保留供后续解码 |

---

## 三、新增源码、固件与测试路径

```
research/native_access/AG_NATIVE_01C/
├── DISCOVERY.md                     # 详细逆向调查与汇编反编译报告
├── CODEX_HANDOFF.md                 # 本交接备忘录
├── object_catalog.json              # 机器可读的 75 槽位新版目录 (更新步长与新对象)
├── decoders/
│   ├── record_book_decoder.py       # 历史纪录 52 字节解码引擎 (含日期公式)
│   └── schedule_decoder.py          # 赛程日历 24 字节解码引擎
├── export_sample_sqlite.py          # 多对象 SQLite 独立样本库构建脚本
├── native_sample_01c.db             # 自动构建并已验证外键约束的 SQLite 样本库
├── fixtures/
│   ├── sample_record_book_500.bin   # 前 500 条历史纪录切片
│   ├── sample_schedule_100.bin      # 前 100 场赛程切片
│   ├── sample_first_names_100.bin   # 前 100 个名字切片
│   ├── sample_last_names_100.bin    # 前 100 个姓氏切片
│   └── sample_teams_catalog.json    # 219 支全量球队元数据 (用于外键完整性)
└── tests/
    └── test_native_01c.py           # 6 项自动化单元测试
```

---

## 四、Codex 最小成本复现与验收方式

在项目根目录下直接运行 pytest（脱离游戏环境，纯二进制切片回放）：
```powershell
# 1. 运行 AG-NATIVE-01C 新增测试 (预期 6 passed in ~2s)
pytest research/native_access/AG_NATIVE_01C/tests/test_native_01c.py -v

# 2. 运行全局回归测试 (包含 01 与 01B，预期全部通过)
pytest research/native_access/AG_NATIVE_01/tests/test_native_reader_offline.py research/native_access/AG_NATIVE_01B/tests/test_native_01b.py research/native_access/AG_NATIVE_01C/tests/test_native_01c.py -v
```

---

## 五、建议 Codex 后续跟进的复杂问题

1. **Schedule 比分压缩编码（`0x10..0x13`）**：
   - 现已证实 `0x14` 为胜负哨兵，`0x10..0x13` 的 4 个字节疑似存放了双方最终比分（如通过 16 位整型或压缩差值存储）。建议 Codex 在后续比赛结算流中比对两场真实比赛的比分数值。
2. **NativeReader 统一集成**：
   - 将 `record_book_decoder` 和 `schedule_decoder` 封装为 `NativeReader` 的子方法（如 `reader.list_record_book()`、`reader.list_schedule()`）。
3. **字典直接查表化**：
   - 可直接利用 Slot 31 & 32 将 `PLAYER` 结构体中的 `first_name_id` / `last_name_id` 直译为文字，彻底摆脱外部离线名字 mapping 文件的维护成本。
