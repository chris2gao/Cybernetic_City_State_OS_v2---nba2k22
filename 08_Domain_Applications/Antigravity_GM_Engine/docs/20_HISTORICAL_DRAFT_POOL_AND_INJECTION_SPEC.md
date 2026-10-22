# NBA 2K22 历史球员池全景数据库与新秀槽位注入规范 (Historical Draft Pool & Rookie Injection Spec)

> **实现边界：** 全局球员池抓取与按 `raw_struct[0x70] & 0xE0 == 0xE0` 查找历史新秀已可用；选秀目标槽位写入目前未完成实机校准/实现。本文中的注入伪代码不是可执行能力。未来任何槽位写入都要先提交变更方案并取得玩家批准，再做只读目标校验、写入和回读验证。总审批和证据规则见 [22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md)。

本文记录 NBA 2K22 **全量球员池总账本**、历史新秀候选查询规则，以及未来 60 个新秀槽位覆盖的安全边界；槽位写入目前尚未实现。

当前局从 2021–2022 开始，历史选秀按 1984–2020 逐届轮回；2020 后返回 1984，只在玩家确认该届已完成后推进。规则与属性编辑边界见 [文档 26](26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)。导入已有的新秀模型不授权修改现役球员属性；旧手填 60 人名单生成器不得作为生产数据源。

历史候选人必须由球员原始结构中的类型码确认，再经数据库筛选、排重后进入选秀名单。数据库查询是候选人名单的权威来源；类型码缺失时不按姓名或选秀年份猜测克隆版本。

---

## 一、底层球员池物理寻址与数据结构规范

在 NBA 2K22 游戏进程内存中，所有现役球员、名宿传奇、经典复古队、自建球员及自由球员，均连续驻留于一个巨大的**全局一维结构体数组 (Global Player Struct Array)** 中。

### 1. 核心寻址参数
* **数组物理起始基址 (Base Address)**：每次抓取前由 `AddressCalibrator` 重新校准；`0x7ff4e6dfb2e8` 仅为某次运行观测值，不能用作重启后的固定地址。
* **单球员结构体字节步长 (Stride)**：精确为 **`0x4F0`（1,264 字节）**
* **总槽位数量**：**3,320 个球员结构体**
* **内存占用总容量**：$3,320 \times 1,264 \text{ bytes} \approx 4.19 \text{ MB}$

### 2. 字段反汇编公式与解包标准

通过对已知真实选秀顺位的超级巨星（乔丹、詹姆斯、科比、库里、杜兰特、约基奇）进行交叉反汇编定位，确立以下官方位域解析公式：

| 字段名称 (Field) | 偏移 (Offset) | 类型与位域 | 官方物理映射与解包公式 | 实测巨星验算范例 |
| :--- | :---: | :---: | :--- | :--- |
| **姓氏 (Last Name)** | `0x00` | UTF-16LE, 40B | `raw[0:40].decode('utf-16le').split('\0')[0]` | Jordan, James, Bryant |
| **名字 (First Name)** | `0x28` | UTF-16LE, 40B | `raw[40:80].decode('utf-16le').split('\0')[0]` | Michael, LeBron, Kobe |
| **面补 ID (Face ID)** | `0x6C` | uint16 (2B) | `struct.unpack_from('<H', raw, 0x6C)[0]` | 乔丹: `1759`, 詹皇: `1013`, 科比: `195` |
| **球员类型/历史新秀标记** | `0x70` | uint8 位域 | **历史新秀：`(raw[0x70] & 0xE0) == 0xE0`**；高三位类型码 `111`，低五位保留原值 | 艾弗森 `0xE7`、科比 `0xF7`；普通同名克隆不满足掩码 |
| **选秀年份 (Draft Year)** | `0x179` | uint8 (1B) | **$\text{Year} = 1900 + \text{raw}[0x179]$** | 乔丹: $1900+84=1984$；詹皇: $1900+103=2003$ |
| **选秀轮次 (Draft Round)**| `0x316` | 高 4 bits | **$\text{Round} = (\text{raw}[0x316] \gg 4) \ \& \ 0x0F$** | 乔丹: 首轮(1)；约基奇: 次轮(2) |
| **选秀顺位 (Draft Pick)** | `0x312` | uint16 位域 | **$\text{Pick} = (\text{u16}[0x312] \gg 6) \ \& \ 0x3F$** | 詹皇: 1；杜兰特: 2；乔丹: 3；库里: 7 |
| **主打位置 (Position)** | `0xF9` | 低 3 bits | **$\text{Pos} = \text{raw}[0xF9] \ \& \ 0x07$** | `0=PG, 1=SG, 2=SF, 3=PF, 4=C` |
| **球员潜力 (Potential)** | `0xEB` | uint8 (1B) | `raw[0xEB]`（有效区间 50 ~ 99） | 乔丹: `98`, 詹姆斯: `99`, 科比: `98` |
| **完整结构体 (BLOB)** | `0x00~0x4F0` | Binary 1264B | **原汁原味整块切片保存至 SQLite `raw_struct`** | 保留 100% 投篮动作、徽章、热区与护具 |

---

## 二、全量球员池数据库架构 (`nba2k22_players.sqlite`)

全量球员数据保存在独立 SQLite 文件。月度统一流程写入当前存档目录下的 `player_pool.sqlite`；单独运行 `src/dump_player_pool.py` 时默认写入旧版兼容文件 `database/nba2k22_players.sqlite`。

### 1. 表结构定义 (`player_pool`)
```sql
CREATE TABLE IF NOT EXISTS player_pool (
    slot_id INTEGER PRIMARY KEY,      -- 内存原始槽位 (0 ~ 3319)
    first_name TEXT,                  -- 名字
    last_name TEXT,                   -- 姓氏
    full_name TEXT,                   -- 全名 (索引主键，用于去重)
    draft_year INTEGER,               -- 真实选秀年份 (1950 ~ 2021)
    draft_round INTEGER,              -- 选秀轮次 (历史上可超过两轮；0 表示未识别)
    draft_pick INTEGER,               -- 当轮顺位
    overall_pick INTEGER,             -- 仅能确认时写入；未知保持 NULL
    cyberface_id INTEGER,             -- 官方真实面补 ID
    position INTEGER,                 -- 位置代码 (0~4)
    position_name TEXT,               -- 位置名称 (PG/SG/SF/PF/C)
    raw_potential INTEGER,            -- 原始潜力字节
    potential INTEGER,                -- 球员天花板潜力值
    memory_addr TEXT,                 -- 兼容字段；新采集留空，避免保存重启后失效的绝对地址
    raw_struct BLOB                   -- 核心：完整 1,264 字节二进制数据块
);

-- 高效检索索引
CREATE INDEX idx_draft_year_pick ON player_pool(draft_year, draft_round, draft_pick);
CREATE INDEX idx_full_name ON player_pool(full_name);
```

### 2. 历史新秀类型码和克隆排重规则

类型码由两组已知样本对照确认：艾弗森全身照 ID `16558` 的槽位 `3021` 原始字节 `raw_struct[0x70] = 0xE7`；科比全身照 ID `16565` 的槽位 `3028` 为 `0xF7`。两人的其他同名克隆均不满足高三位掩码。两条已知记录共同指向类型码 7：

```python
raw_type = raw_struct[0x70]
is_historical_rookie = (raw_type & 0xE0) == 0xE0
```

采集脚本只保存完整 `raw_struct`；筛选时直接读取 `raw_struct[0x70]` 判定类型，不再持久化可从原始结构重算的 `is_rookie` 或 `rookie_tag_raw` 字段。选秀查询只接受类型码 7 的记录，并按规范化姓名、年份、轮次、当轮顺位排重；未命中类型码的同名现役/巅峰克隆不能顶替新秀模型。

已保存的球员池快照中，1996 届有 14 条类型码 7 的记录（包括上述艾弗森和科比）；1984 届当前有 7 条。每届可用人数以脚本查询结果为准，不硬编码成 13 人或 60 人。若预期球员缺少类型码，将其记为覆盖缺口，不从其他克隆推断属性。

### 3. 覆盖年份与跨度
* **年份跨度**：1950 年 至 2021 年
* **独立选秀届次**：共 **69 个独立历史选秀年份**
* **总球员样本**：3,320 个原始槽位，保留同名不同版本克隆；按选秀届次查询时再依新秀类型和选秀身份排重

---

## 三、休赛期 60 个新秀槽位的历史名单接管规程

游戏最多生成 60 个临时新秀槽位。60 是容量上限，不是必须替换人数；历史球员池通常只包含一部分真实历史新秀，其余槽位继续使用游戏生成的小人。

1. **筛选来源**：按目标选秀年份读取 `player_pool`，只有 `raw_struct[0x70] & 0xE0 == 0xE0` 的记录可作为历史新秀；每次查询直接从原始结构计算，不依赖冗余标签列。
2. **排重和排序**：按规范化姓名、选秀年份、选秀轮次、当轮顺位排重；按轮次和当轮顺位排序。仅对 `draft_pick` 有效的记录安排选秀顺位；原始轮次数据保留，不能把早期多轮选秀强行改成两轮。
3. **槽位写入**：只对筛选出的 N 名新秀构造目标槽位数据（N 不超过 60），其余 `60-N` 个游戏小人槽位保持原样。类型标签缺失时不以其他同名克隆替补，记录为数据覆盖缺口。

**顺序和布局边界**：`pick_proj` 是已验证候选名单内的顺序号，不等于 NBA 原始综合顺位，也不等于目标槽位编号。来源字段保留 `draft_round` 与 `draft_pick`；如果某年的每轮人数未知，不推算跨轮综合顺位，数据库 `overall_pick` 保持 `NULL`。球员池来源 `raw_struct` 的步长为 `0x4F0`。选秀界面目标结构是独立布局，必须另行校准目标基址、步长和字段映射；不能把来源 `0x4F0` 字节块直接当成目标槽位结构整体写入。

---

## 四、Python 接口与执行脚本指南

### 1. 全量转储与刷新脚本 (`src/dump_player_pool.py`)
当游戏更新名单或打了大型复古名单补丁后，可运行此脚本刷新旧版兼容球员池数据库。统一月度流程会自动将球员池采集到当前存档自己的临时库，通过校验后原子替换正式文件：
```powershell
python "e:\games\NBA 2K22\Antigravity_GM_Engine\src\dump_player_pool.py"
```

### 2. 按年份查询选秀名单接口 (`query_draft_class`)
在 Python 代码或交互会话中随时调用：
```python
from dump_player_pool import query_draft_class

# 检索 1996 届已确认的历史新秀；人数由数据库实际覆盖决定
rookies_1996 = query_draft_class(1996, limit=10)
for r in rookies_1996:
    print(r["pick_proj"], r["full_name"], r["position_name"], r["cyberface_id"])
```

### 3. 目标槽位写入阶段（待独立校准和实现）
当前代码实现候选查询，不包含已验证的 `inject_draft_class_to_memory` 内存写入接口。目标数组布局、写入时机和字段映射需要另行实机校准。实现后应先用只读/试运行校验目标槽位，不得把来源记录整块复制到目标地址。伪代码流程：
```python
def inject_year_draft(target_year=1984):
    rookies = query_draft_class(target_year, limit=60)
    # 只遍历已验证的新秀；未匹配的槽位继续使用游戏小人
    for idx, r in enumerate(rookies):
        # idx 只是候选顺序；需经过单独校准的映射函数决定目标槽位
        # 依据目标布局字段映射写入，不得整块复制来源 raw_struct
        ...
```

---

## 五、未来交互设想（目标槽位写入实现并获批前不可执行）

目标槽位接口完成实机校准、实现和玩家批准后，未来可提供以下交互：
* 玩家在聊天框只需输入一句话：
  > **“已进入休赛期选秀界面，帮我载入 1984 年（或任意年份）选秀名单。”**
* 流程从当前存档的 `player_pool.sqlite`（旧版兼容路径为 `database/nba2k22_players.sqlite`）读取已确认的新秀记录；只安排命中的真实球员，剩余槽位保留小人。目标内存结构仍需独立校准和字段映射。
