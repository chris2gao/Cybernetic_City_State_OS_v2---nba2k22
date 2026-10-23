# AG-NATIVE-01B Codex 验收指南与成果交付说明

> **任务标识**：AG-NATIVE-01B  
> **执行模型**：Antigravity Gemini Flash 3.8  
> **分支**：`dev/native-io-exploration`  
> **交付状态**：`DELIVERED_PENDING_CODEX_ACCEPTANCE`  

---

## 1. 交付目标达成自查

| 核心目标 | 要求 | 交付状态 | 关键成果与证据位置 |
| :--- | :--- | :---: | :--- |
| **A. ROSTERDATA 完整描述符调查** | 识别真实描述符、对象类型、步长、数量及 Getter 对应关系，澄清 67 概念与 EndPointer 误区 | **完全达成** | [`ROSTERDATA_DIRECTORY_AUDIT.md`](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01B/ROSTERDATA_DIRECTORY_AUDIT.md)<br>75 槽位全景映射（67 活跃、8 预留）、16 字节结构体、静态单例地址 `+0x6347720` |
| **B. 新增对象深度逆向** | 选取此前未集成的原生对象，逆向其实际数据内容、记录布局与真实样本 | **完全达成** | [`WAIVED_SALARY_SPEC.md`](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01B/WAIVED_SALARY_SPEC.md)<br>136 字节字段表、UTF-16 名字解码、6 年死钱分摊、32 条活跃样本、`TEAM + 0xC88` 链表 |
| **C. 原生记录到数据表验证** | 建立独立 SQLite 样本表，通过自动化测试证明可可靠生成关系型数据 | **完全达成** | [`native_sample_schema.sql`](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01B/native_sample_schema.sql)<br>[`export_to_sqlite.py`](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01B/export_to_sqlite.py)<br>[`native_sample.db`](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01B/native_sample.db) (32 条死钱、30 队、75 描述符) |

---

## 2. 交付资产清单

本次所有产物严格隔离在 `research/native_access/AG_NATIVE_01B/`：

```
research/native_access/AG_NATIVE_01B/
├── ROSTERDATA_DIRECTORY_AUDIT.md       # 75 槽位描述符完整审计报告与 C++ Getter 汇编反编译
├── WAIVED_SALARY_SPEC.md               # 136 字节死钱数据结构规范、真实样本与双向链表
├── OLD_VS_NEW_STRUCTURE_COMPARISON.md  # 旧已证结构 (source_extensions) 与新逆向结构对照表
├── native_sample_schema.sql            # 独立 SQLite 关系型样本库建表脚本
├── export_to_sqlite.py                 # 原生二进制切片到 SQLite 样本库的转换与导出引擎
├── native_sample.db                    # 自动生成的轻量级 SQLite 样本数据库
├── fixtures/                           # 高保真二进制固件与机器可读元数据
│   ├── sample_descriptors.json         # 75 描述符完整机器可读映射 (含 Getter RVA、步长、数量)
│   ├── roster_descriptors_raw.bin      # 1,200 字节原生描述符内存快照
│   ├── sample_waived_salary.bin        # 30,192 字节全量 222 条死钱记录内存切片
│   └── sample_teams_30.bin             # 30 支核心 NBA 球队内存切片 (含 +0xC88 死钱链表头)
├── tests/
│   └── test_native_01b.py              # 8 项全覆盖自动化单元测试套件
└── ACCEPTANCE.md                       # 本文档
```

---

## 3. Codex 独立离线验收测试

Codex 审查员可直接在项目根目录下执行以下测试命令（无需游戏运行，无网络/生产数据库依赖）：

### 3.1 运行 AG-NATIVE-01B 自动化测试
```powershell
pytest research/native_access/AG_NATIVE_01B/tests/test_native_01b.py -v
```
**预期输出**：8 项测试全部通过 (`8 passed in ~0.3s`)。

### 3.2 运行回归测试 (验证 AG-NATIVE-01 兼容性)
```powershell
pytest research/native_access/AG_NATIVE_01/tests/test_native_reader_offline.py -v
```
**预期输出**：18 项测试全部通过 (`18 passed in ~0.05s`)。

### 3.3 快速查询 SQLite 样本数据库
```powershell
python -c "
import sqlite3
conn = sqlite3.connect('research/native_access/AG_NATIVE_01B/native_sample.db')
cur = conn.cursor()
cur.execute('SELECT t.name, count(w.id), sum(w.season_1_amount) FROM teams t JOIN waived_salaries w ON t.team_index = w.team_index GROUP BY t.team_index ORDER BY sum(w.season_1_amount) DESC LIMIT 3')
for r in cur.fetchall():
    print(f'{r[0]:10s} | 记录数: {r[1]:2d} | 第1赛季死钱: ${r[2]:10,d}')
"
```
**预期输出**：
- Pistons | 记录数: 6 | 第1赛季死钱: $45,492,507
- Thunder | 记录数: 4 | 第1赛季死钱: $28,274,688
- Hornets | 记录数: 1 | 第1赛季死钱: $8,856,969

---

## 4. 公开安全性与脱敏声明

- [x] **零潜在能力泄露**：本轮涉及的 `WAIVED_SALARY`、`roster_array_descriptors` 及 `teams` 结构中不包含任何球员能力值或潜力字段。
- [x] **零代码侵入**：未修改项目既有生产代码（`src/`）或主线数据库（`database/`）。
- [x] **无大规模内存转储**：固件仅包含有界二进制切片（总大小小于 200 KB）。
- [x] **只读原则遵守**：实机测试仅调用只读 API，未对游戏内存进行任何写操作。
