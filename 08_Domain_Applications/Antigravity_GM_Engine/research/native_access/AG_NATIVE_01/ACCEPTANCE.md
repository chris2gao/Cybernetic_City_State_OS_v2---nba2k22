# NBA2K22 原生数据访问模块 Codex 验收指南 (AG-NATIVE-01)

> **文档标识**：AG-NATIVE-01-ACCEPTANCE  
> **面向对象**：Codex 系统集成模型 / 后续开发者  
> **分支与基准**：`dev/native-io-exploration` (`07df6df00368b1c67e19a208bdfa105ca694eaec`)  
> **交付状态**：`DELIVERED_PENDING_CODEX_ACCEPTANCE`  

---

## 1. 交付物资产清单

本次任务所有代码、配置、固件、测试及文档严格封装在 `research/native_access/AG_NATIVE_01/` 目录下，未侵入项目既有生产代码或数据库：

| 文件路径 | 类型 | 职责说明 |
| :--- | :--- | :--- |
| `native_access.py` | 源码 | 统一原生对象读取引擎（含 `NativeReader`, `NativeRecord`, `LiveMemoryBackend`, `MockMemoryBackend`） |
| `native_access_catalog.json` | 规范/配置 | 7 类原生对象元数据（步长、容量、基地址偏移、字段布局、跨对象关系及反汇编证据） |
| `fixtures/sample_*.bin` | 固件切片 | 从实机提取的高保真二进制内存片段（涵盖 7 类对象及 `ROSTERDATA` 根描述符块） |
| `fixtures/fixtures_manifest.json` | 固件清单 | 二进制切片元数据及脱敏声明（球员潜力 byte `0x441` 已统一遮蔽为 `1`） |
| `tests/test_native_reader_offline.py` | 自动化测试 | 18 项全覆盖离线单元测试（验证 7 类对象读取、图式关联多跳、边界与异常处理） |
| `DISCOVERY.md` | 技术报告 | 逆向工程深度调查报告（汇编反编译、无 SQL 证据、数学守恒验证） |
| `ACCEPTANCE.md` | 验收文档 | 本文档，包含 Codex 验收指引、运行命令、API 示例与已知约束 |

---

## 2. 独立离线验收执行方式

本模块完全支持**无游戏依赖、无网络依赖、无数据库依赖**的确定性离线回放测试。Codex 可直接在命令行执行以下命令：

### 2.1 运行自动化测试套件

```powershell
pytest research/native_access/AG_NATIVE_01/tests/test_native_reader_offline.py -v
```

### 2.2 预期测试输出

测试套件包含 18 个细粒度测试用例，预期在 0.1 秒内全部通过 (`18 passed`)：
- `test_reader_initialization`: 验证目录加载与 `MockMemoryBackend` 初始化；
- `test_read_player_object`: 验证 `PLAYER` 结构体解析与字段提取；
- `test_read_team_object`: 验证 `TEAM` 结构体与胜负场解析；
- `test_read_staff_object`: 验证 `STAFF` 教练职员数据与薪资解析；
- `test_read_player_stats_object`: 验证 `PLAYER_STATS` 统计项解析；
- `test_read_team_stats_object`: 验证 `TEAM_STATS` 团队统计项解析；
- `test_read_draft_assets_object`: 验证 `DRAFT_ASSETS` 选秀资产解析；
- `test_read_waived_salary_object`: 验证新对象 `WAIVED_SALARY` 解析；
- `test_scoring_conservation_team`: 验证团队投篮得分绝对数学守恒 ($2\times\text{FGM} + 3\text{PM} + \text{FTM} == \text{PTS}$)；
- `test_scoring_conservation_player`: 验证个人投篮得分绝对数学守恒；
- `test_relation_player_to_team`: 验证 `PLAYER -> TEAM` 关联跳转；
- `test_relation_player_to_stats`: 验证 `PLAYER -> PLAYER_STATS` 关联跳转；
- `test_relation_team_to_stats`: 验证 `TEAM -> TEAM_STATS` 关联跳转；
- `test_relation_team_to_staff`: 验证 `TEAM -> STAFF` 一对多关联跳转；
- `test_relation_team_to_draft_assets`: 验证 `TEAM -> DRAFT_ASSETS` 一对多关联跳转；
- `test_relation_team_to_waived_salaries`: 验证 `TEAM -> WAIVED_SALARY` 一对多死钱关联跳转；
- `test_multihop_navigation`: 验证 `PLAYER -> TEAM -> TEAM_STATS` 跨两跳链式导航；
- `test_out_of_bounds_handling`: 验证超出容量边界时的抛错与安全防护。

---

## 3. `NativeReader` API 快速使用指南

### 3.1 离线模式初始化 (用于 CI / 本地开发 / 回放)

```python
from research.native_access.AG_NATIVE_01.native_access import NativeReader, MockMemoryBackend
from pathlib import Path

FIXTURES_DIR = Path("research/native_access/AG_NATIVE_01/fixtures")
backend = MockMemoryBackend(FIXTURES_DIR)
reader = NativeReader(backend=backend)
```

### 3.2 实机在线模式初始化 (需要管理员权限附加进程)

```python
from research.native_access.AG_NATIVE_01.native_access import NativeReader, LiveMemoryBackend

backend = LiveMemoryBackend(process_name="NBA2K22.exe")
backend.attach()
# 自动通过特征码与指针链校准 ROSTERDATA 根基址
reader = NativeReader(backend=backend)
```

### 3.3 核心 API 示例

#### 1. 列表遍历与条件筛选 (`list_objects` / `find_objects`)
```python
# 获取前 10 名现役球队
teams = reader.list_objects("TEAM", offset=0, limit=10)

# 条件查询所有属于步行者队 (team_id=11) 的职员
pacers_staff = reader.find_objects("STAFF", {"team_id": 11})
```

#### 2. 精确寻址 (`get_object`)
```python
# 读取索引为 179 的球员 (如 Haliburton)
player = reader.get_object("PLAYER", 179)
print(player["name"], player["team_id"], player["stats_index"])
```

#### 3. 关联关系与多跳图式导航 (`get_related`)
```python
# 1. 球员获取所属球队
team = player.get_related("team")

# 2. 球员获取当季统计
stats = player.get_related("stats")
print(f"得分: {stats['pts']}, 助攻: {stats['ast']}")

# 3. 链式两跳: 球员 -> 球队 -> 球队战绩
team_stats = player.get_related("team").get_related("stats")
print(f"母队胜场: {team_stats['wins']}, 负场: {team_stats['losses']}")

# 4. 球队获取死钱清单 (Waived Salaries)
dead_caps = team.get_related("waived_salaries")
for cap in dead_caps:
    print(f"死钱赛季金额: {cap['amount_season_1']}")
```

---

## 4. Codex 验收标准检查单

Codex 在对本任务进行代码审查与集成时，可逐项核对以下指标：

- [x] **零破坏性**：仅在 `research/native_access/AG_NATIVE_01/` 内增加新文件，未对主干既有文件进行任何修改。
- [x] **零写操作**：`LiveMemoryBackend` 仅调用 Win32 `ReadProcessMemory` API，不包含任何 `WriteProcessMemory`、动态注入或 Hook 逻辑。
- [x] **脱敏合规**：所有 `fixtures/sample_players.bin` 切片中的潜在能力字段（`potential`）均已统一掩码为 `1`。
- [x] **通用架构**：通过统一的 `native_access_catalog.json` 驱动，任意扩展第 8 个原生对象只需补充 JSON 目录项，无需重写 Reader 逻辑。
- [x] **自动化测试**：18/18 离线测试稳定通过，耗时小于 0.2 秒。

---

## 5. 已知约束与后续集成建议

1. **多赛季历史支持**：
   - 当前实机测试的 `PLAYER_STATS` 和 `TEAM_STATS` 针对的是当前常规赛累计数据。未来若需获取往季生涯历史，需进一步结合此前比赛历史原型模块。
2. **球员名字解析**：
   - 当前原型直接提取了原生结构中的 ASCII 字符或内部 ID。未来需接入已有项目的姓名表（`first_name_id`, `last_name_id`）做最终本地化显示映射。
3. **向 DEV28 生产模块集成路线**：
   - 建议在下一步系统集成任务中，将 `NativeReader` 的对象模型包装为服务接口，直接对接到未来的独立教练和球员 Agent 原料采集网关。
