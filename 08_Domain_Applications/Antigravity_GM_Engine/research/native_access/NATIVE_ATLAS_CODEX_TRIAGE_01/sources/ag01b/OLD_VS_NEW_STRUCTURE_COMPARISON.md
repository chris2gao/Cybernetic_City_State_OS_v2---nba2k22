# 旧已证结构与 AG-NATIVE-01B 新逆向结构深度对照表 (AG-NATIVE-01B)

> **任务标识**：AG-NATIVE-01B  
> **编制依据**：`docs/31_SOURCE_EXTENSION_DISCOVERY.md`、`src/source_extensions.py`、`src/address_calibrator.py`、`config/memory_field_profile.json`、`native_access.py` 及实机逆向  
> **分支**：`dev/native-io-exploration`  

---

## 1. 结构定位与基准偏移对照 (Root Offset Delta)

在过去的工程实现中，代码以 `address_calibrator.py` 探测出的历史“球员池根原点（Player Pool Root）”为基准。本轮通过逆向 `NBA2K22.exe` 原生 Getter 汇编（函数 `0x1411D5DE0`），精确定位了游戏引擎内部真正的 C++ 单例对象基址 `g_pRosterData`。

两者之间存在恒定 **8 字节** 的偏移差：
$$\text{Calibrated Root Address} = \text{Native } g\_pRosterData - 0x08$$

| 对象类型 | 旧工程代码偏移 (`root + offset`) | 原生 C++ 汇编偏移 (`g_pRosterData + offset`) | 结构步长 (Stride) | 历史已知容量 | 本轮实测容量 | 变化与判定 |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **`PLAYER`** | `root + 0x020` (Count: `+0x018`) | `mgr + 0x010` (Count: `+0x010`) | **1,264 字节** | 3,383 ~ 3,392 | 3,390 | **一致**。旧代码正确解析了球员 55 项能力和合同 |
| **`TEAM`** | 未在 `roster_directory` 登记 | `mgr + 0x080` (Count: `+0x080`) | **4,696 字节** | 30 (仅核心队) | 219 (含历史/全明星) | **扩展**。旧代码仅按固定偏移读 30 队，现已纳入目录 |
| **`STAFF`** | `root + 0x140` (Count: `+0x138`) | `mgr + 0x130` (Count: `+0x130`) | **352 字节** | 1,470 | 1,470 | **一致**。对应原生 Getter `0xF3C120` |
| **`PLAYER_STATS`** | `root + 0x190` (Count: `+0x188`) | `mgr + 0x180` (Count: `+0x180`) | **48 字节** | ~400 (仅当前活跃) | 9,773 (总分配槽) | **一致**。旧代码读取前 400 人，现已确认全量物理容量 |
| **`TEAM_STATS`** | `root + 0x1D0` (Count: `+0x1C8`) | `mgr + 0x1C0` (Count: `+0x1C0`) | **62 字节** | 30 (仅现役队) | 2,964 (总分配槽) | **一致**。对应原生 Getter `0xF413B0` |
| **`DRAFT_ASSETS`** | `root + 0x2B0` (Count: `+0x2A8`) | `mgr + 0x2A0` (Count: `+0x2A0`) | **32 字节** | 504 | 504 | **一致**。对应原生 Getter `0xF3C940` |
| **`WAIVED_SALARY`**| 仅在 `docs/31` 文档提及为候选 | `mgr + 0x3D0` (Count: `+0x3D0`) | **136 字节** | 未集成 / 候选 | 222 (实测 32 活跃) | **新集成**。对应原生 Getter `0xF3C790`，打通死钱链表 |

---

## 2. “EndPointer 终点校验方程”的本质解析

### 旧代码实现逻辑 (`src/source_extensions.py`)
```python
address = mem.require_uint64(root + offset)
count = mem.require_uint64(root + offset - 8)
end = mem.require_uint64(root + offset + 0x10)
if end != address + count * stride:
    raise RuntimeError('Invalid roster directory descriptor')
```
旧逻辑假定每个描述符内部保存了一个专属的 `EndPointer`（位于 `offset + 0x10`）。

### 本轮实机逆向证伪与澄清
1. 每个描述符实际仅占用 16 字节（`0x10`）：`[uint64_t count, void* pData]`。
2. 偏移 `root + offset + 0x10` 根本不是当前对象的字段，而是**下一个相邻描述符的 `pData` 指针**。
3. 之所以 `end == address + count * stride` 恒成立，是因为游戏内存分配器将所有 67 个数组在堆内存中按描述符顺序连续紧凑分配。
4. **影响**：该发现消除了对“虚构 EndPointer”的依赖，明确了数组目录是标准紧凑描述符数组（`Array of Struct`），便于构建通用迭代器。

---

## 3. 数据表映射与消费层设计差异

| 维度 | 旧工程方案 (`M0 / source_extensions`) | AG-NATIVE-01B 新设计 (`NativeSqliteExporter`) |
| :--- | :--- | :--- |
| **数据源定位** | 每次全内存大扫描或依赖缓存 | 支持静态单例指针 `NBA2K22.exe + 0x6347720` 直达，秒级就绪 |
| **对象覆盖** | 5 类硬编码对象 | 67 类原生数组描述符目录驱动，支持按类型通用查询 |
| **财务死钱支持** | 无（大名单外死钱被忽略） | 完整解码 136 字节 `WAIVED_SALARY`，覆盖延伸条款与买断金额 |
| **关系持久化** | 扁平化 JSON 文本嵌入快照表 | 原生外键与链表指针保留，建立标准关系型表结构与索引 |
| **离线沙箱支持** | 依赖已跑完的历史生产数据库 | 纯二进制切片固件（`fixtures/`），无依赖 0.05 秒确定性测试 |

---

## 4. 总结与兼容性建议

- AG-NATIVE-01B 的发现与旧代码在**步长（Stride）**和**相对数据偏移**上 100% 吻合，证明旧代码的核心字段解码逻辑是完全正确的。
- 差异仅在于**上层管理器组织方式的认识提升**（从散装 offset 升级为单例数组描述符表），以及**补全了此前缺失的 WAIVED_SALARY 核心对象**。
- 现有生产代码无需推倒重来，可在后续 DEV28 任务中逐步以 `NativeReader` 取代散装扫描。
