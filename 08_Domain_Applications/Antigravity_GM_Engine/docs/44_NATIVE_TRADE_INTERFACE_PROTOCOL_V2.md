# NBA 2K22 REA Native 交易标准接口协议 (v2.0 零裸写原生调用版)
# (NBA 2K22 REA Native Trade Interface Protocol Specification v2.0)

> **协议标识 (Protocol ID)**: `SPEC-NATIVE-TRADE-V2.0`  
> **适用版本**: NBA 2K22 (Steam PC x64) | 引擎底层: `NBA2K22.exe`  
> **上位规范**: [Doc 43 V2 全维度接口协议第 5 节](43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) | [REA Action Surface](../research/rea_native_control/ACTION_SURFACE.md)  
> **替代说明**: 本协议为 `SPEC-NATIVE-TRADE-V1.0` 的 REA Native 升级版，全面废除裸内存指针强写通道，统一通过 `research/rea_native_control` 已认证的原生函数接口执行交易过户。  
> **对接角色**:  
> - **发布方 (数据分析与决策 / 任务规划)**: `data_analysis_and_decision` / `decision_architecture`  
> - **执行方 (REA Native 执行与 CAS 核验)**: `role-developer` / `batch_executor`  

---

## 一、 协议核心设计原则与四大宪法守则 (Constitutional Principles)

1. **严格 REA Native 原生调用原则 (REA Native Only — 严禁裸内存暴力写入)**  
   - 交易执行必须通过 REA 工具链（`research/rea_native_control/facade.py` / `runtime/trade.js`）调用游戏内核已认证的原生函数（`trade.context`、`trade.add_player`、`trade.add_pick`、`trade.process` 或 `trade.validate` / `trade.commit_wrapper`）；
   - **严禁直接裸内存写名册指针（`team + 0x00..0xC8`）或强改人数计数（`0xCB1`、`0x1047`）**，杜绝因绕过引擎内部事务状态导致的存档损坏或赛季结算崩溃。
2. **零占位纯差分与自解释原则 (Zero Placeholder & Self-Documenting)**  
   - 规格书严禁出现 `65535`、`0`（非真实 ID）、`null` 等占位符；无选秀权交易时 `picks_a` / `picks_b` 必须明确为空数组 `[]`；
   - 每笔交易及每个资产均须附带人类与审核协调员可读的 `decision_rationale` 与 `source_research_docs`，REA 执行端旁路忽略描述字段，仅提取强类型 Native 参数。
3. **四维锁定精确寻址原则 (Deterministic Addressing)**  
   - 球员资产必须提供 `native_player_id`（`PLAYER_STRUCT + 0xF4` 处的 `uint16` UID，供 REA `player.by_id` / `rosterPlayer` 精确寻址），并附带 `player_name`、`cyberface_id`、`roster_index` 用作前置防串号核验；
   - 选秀权资产必须提供 `pick_unique_id`（供 REA `pick.by_id` / `pick.unique_id` 精确寻址及当前持有球队指针校验）。
4. **生命周期前置门禁与金丝雀护盾 (Lifecycle Gate & Canary Guard)**  
   - 执行前 REA 底层强制校验游戏处于合法交易生命周期（`mode + 0x150 == 1`, `fr + 0x08 != 0`, `fr + 0xAC == 0`）；
   - 私有 `Proposal`（1,700 字节）前后布置 `0xA7` 金丝雀内存护盾，任何越界写立即阻断。

---

## 二、 REA Native 动作路由与底层绑定字典

### 1. 两大原生执行模式 (`execution_mode`)

| 执行模式 | 对应 REA Action ID | 底层 Runtime Handler | 适用场景与机理 |
| :--- | :--- | :--- | :--- |
| **`AGREED_DIRECT_PROCESS`** *(默认推荐)* | `TRADE_EXECUTE_AGREED_PACKAGE` | `trade.agreed` (`runtime/trade.js`) | 外部 GM 决策与真人玩家已批准交易。直接装配私有 Proposal 并调用 `trade.context()` + `trade.process(proposal, context, out)`，**跳过外围 `FullCheck` 薪资/CPU 拒绝逻辑**，由游戏内核原子完成球员与选秀权过户。 |
| **`FULL_VALIDATE_COMMIT`** | `TRADE_PLAYERS` / `TRADE_VALIDATE_COMMIT` | `trade.players` (`runtime/trade.js`) | 需由 2K 原生引擎执行完整 CBA 规则校验时使用。依次调用 `trade.validate(proposal)` 与 `trade.commit_wrapper(proposal, out)`。 |

### 2. 底层 Native 绑定与 RVA 索引 (PC22 固定构建)

| Binding ID | RVA | 返回类型 | Win64 显式参数 | 职责说明 |
| :--- | :---: | :---: | :--- | :--- |
| `trade.context` | `0xBAA7E0` | `pointer` | `(void)` | 获取当前游戏原生交易上下文指针 |
| `trade.add_player` | `0x12DEC20` | `int` | `proposal:pointer, from_team:pointer, to_team:pointer, player:pointer` | 向私有交易提案添加互换球员 |
| `trade.add_pick` | `0x12DE850` | `int` | `proposal:pointer, from_team:pointer, to_team:pointer, pick:pointer` | 向私有交易提案添加互换选秀权 |
| `trade.process` | `0x12E93B0` | `int` | `proposal:pointer, context:pointer, output:pointer` | 内核级直接执行已达成的交易提案 |
| `trade.validate` | `0x12EC930` | `int` | `proposal:pointer` | 原生交易规则预校验 |
| `trade.commit_wrapper` | `0x132B840` | `int` | `proposal:pointer, output:pointer` | 触发原生 `FullCheck` 并提交交易 |
| `pick.by_id` | `0xF3CA00` | `pointer` | `pick_id:uint` | 根据全局唯一 ID 解析选秀权对象指针 |
| `pick.unique_id` | `0x947330` | `uint` | `pick:pointer` | 回读验证选秀权唯一 ID |

---

## 三、 标准化交易规格书 JSON Schema (Machine-Ready Spec)

上游规划/决策模型输出目录：`C:\nba2k22\exports\YYYYMMDD_<task_name>_execution\`  
单笔或同批次交易文件命名：`<TRADE_ID>_trade_spec.json`

```json
{
  "protocol_version": "v2.0_rea_native_trade",
  "task_package_id": "20261124_OFFSEASON_TRADE_BKN_PHI",
  "target_career": "MyLEAGUE0005",
  "target_process": "NBA2K22.exe",
  "execution_mode": "AGREED_DIRECT_PROCESS",
  "source_research_docs": [
    "26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md",
    "2022_real_transactions_ledger.json"
  ],
  "transactions": [
    {
      "transaction_id": "TX_20220210_BKN_PHI_01",
      "decision_rationale": "【休赛期真实历史线对齐】复现 76 人与篮网核心互换交易，哈登与西蒙斯互换并附带首轮签资产",
      "team_a": {
        "team_id": 0,
        "team_abbr": "PHI",
        "team_name": "Philadelphia 76ers"
      },
      "team_b": {
        "team_id": 18,
        "team_abbr": "BKN",
        "team_name": "Brooklyn Nets"
      },
      "team_a_sends": {
        "players": [
          {
            "native_player_id": 4512,
            "player_name": "Ben Simmons",
            "cyberface_id": 7200,
            "roster_index": 0
          }
        ],
        "picks": [
          {
            "pick_unique_id": 10042,
            "draft_year": 2022,
            "round": 1,
            "original_team_id": 0,
            "desc": "2022 PHI 首轮签"
          }
        ]
      },
      "team_b_sends": {
        "players": [
          {
            "native_player_id": 1863,
            "player_name": "James Harden",
            "cyberface_id": 1863,
            "roster_index": 1
          }
        ],
        "picks": []
      },
      "rea_action_intent": {
        "action_id": "TRADE_EXECUTE_AGREED_PACKAGE",
        "parameters": {
          "team_a": 0,
          "team_b": 18,
          "players_a": [4512],
          "players_b": [1863],
          "picks_a": [10042],
          "picks_b": [],
          "execution_mode": "AGREED_DIRECT_PROCESS"
        }
      }
    }
  ]
}
```

---

## 四、 REA 调用映射与 CAS 闭环验收标准

### 1. 执行端解析与 REA 调度流

1. **提取与前置校验**：
   - 执行模型读取 `transactions[].rea_action_intent`，校验 `team_a` / `team_b` (`0..29`)、球员 `native_player_id` 在 `from_team` 现役名册中存在且 `cyberface_id` 一致、选秀权 `pick_unique_id` 当前归属指针等于 `from_team`；
   - 若存在任意未定位 ID 或归属不匹配，**立即阻断并向人类上报**，严禁猜测替代。
2. **直接调用 REA Native 接口**：
   - 通过 `NativeControlFacade.gm_trade(...)`（或 `DecisionOutbox` 提交 `ActionIntent`）下发至 `runtime/trade.js`；
   - 单次执行严格仅调用一次 `trade.process`（或 `trade.commit_wrapper`），禁止自动重试。
3. **独立只读回读核验 (Independent Readback CAS)**：
   - 交易调用返回非错误码（`process_return != 0` / `NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`）后，调用只读接口 `READ_TEAM_ROSTER_BASIC`（`runtime/read_team.js`）核验两队新名册；
   - 确认双方球员 `CURRENT_TEAM` 与名册列表 100% 变更完成，选秀权 `pick.by_id` 归属指针指向新东家。

### 2. 标准化执行回执 (`TRADE_EXECUTION_RECEIPT.json`)

```json
{
  "protocol_version": "v2.0_rea_native_trade",
  "task_package_id": "20261124_OFFSEASON_TRADE_BKN_PHI",
  "status": "APPLIED_READBACK_CONFIRMED",
  "transactions_total": 1,
  "transactions_verified": 1,
  "mismatches_count": 0,
  "results": [
    {
      "transaction_id": "TX_20220210_BKN_PHI_01",
      "action_id": "TRADE_EXECUTE_AGREED_PACKAGE",
      "native_outcome": "NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED",
      "private_canaries_intact": true,
      "readback_roster_verified": true,
      "readback_picks_verified": true
    }
  ]
}
```
