# NBA 2K22 REA Native 球员签约与报价标准接口协议 (v2.0 零裸写原生调用版)
# (NBA 2K22 REA Native Signing & Contract Offer Interface Protocol Specification v2.0)

> **协议标识 (Protocol ID)**: `SPEC-NATIVE-SIGNING-V2.0`  
> **适用版本**: NBA 2K22 (Steam PC x64) | 引擎底层: `NBA2K22.exe`  
> **上位规范**: [Doc 43 V2 全维度接口协议第 5 节](43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) | [FA Offer Native Contract](../research/rea_native_control/FA_OFFER_NATIVE_CONTRACT.md) | [Signing Native Contract](../research/rea_native_control/SIGNING_NATIVE_CONTRACT.md)  
> **替代说明**: 本协议为 `SPEC-NATIVE-SIGNING-V1.0` 的 REA Native 升级版，彻底废除 V1 中直接修改名册指针与合同位域的裸内存写入方式，统一通过 `research/rea_native_control` 已认证的原生函数接口执行报价、撤回与只读回执核验，并明确标定当前未闭环能力的诚实边界。  
> **对接角色**:  
> - **发布方 (数据分析与决策 / 任务规划)**: `data_analysis_and_decision` / `decision_architecture`  
> - **执行方 (REA Native 执行与 CAS 核验)**: `role-developer` / `batch_executor`  

---

## 一、 协议核心设计原则与能力边界 (Principles & Honesty Boundary)

1. **严格 REA Native 原生调用原则 (REA Native Only — 严禁裸内存写合同位域)**  
   - 所有自由球员报价与撤回必须通过 REA 工具链（`research/rea_native_control/facade.py` / `runtime/sign_fa_offer.js` / `runtime/sign_withdraw_offer.js`）调用游戏底层原生函数（`sign.offer_fa_phase` RVA `0x12BD4C0` 等）；
   - **严禁直接向全局签约池（`pool + 0x1727A8`）或球员结构体合同区（`0x1A4..0x1B8`、`0x32E`、`0x341`）执行裸内存写入**。
2. **显式全条款决策与零自动定价原则 (Explicit Caller-Decided Terms)**  
   - 协议要求决策方显式指定 6 年期完整薪资序列、年限、选项类型与交易否决权；
   - REA 底层构造 44 字节私有 `Offer` 结构并传入 `OfferContract`，绝不调用会篡改/钳位条款的 `GenerateContract` (`0x12B7290`)。
3. **当前 REA Native 能力成熟度诚实边界 (Capability Boundary)**  
   - **已实现并可调度 (`CALL_LOGIC_RECOVERED`)**：
     - `CONTRACT_SUBMIT_FREE_AGENT_OFFER`（`GM.CONTRACT.CONTRACT_OFFER`）：在自由球员签约期（`Period == 22 / FA_SIGNING`）向自由球员提交精确条款报价；
     - `CONTRACT_WITHDRAW_PENDING_OFFER`：撤回处于 `OFFERED` 状态的待处理报价；
     - `READ_TEAM_SIGNING_OFFERS` & `READ_PLAYER_CONTRACT`：只读核验报价池状态与球员实际合同字段。
   - **部分绑定 / 尚待逆向闭环 (`PARTIAL_BINDING` — 禁止越权调用)**：
     - `SIGN_FREE_AGENT`（最终直接成交通知）、`RE_SIGN_PLAYER`（`EXTENSION` 提前续约）、`CONTRACT_OPTION_ACTION`（球队/球员选项批处理）、`RELEASE_WAIVE_PLAYER`（裁员）在 `ACTION_SURFACE.md` 中仍存在状态机或标志位未闭合缺口；
     - **阻断铁律**：若任务要求执行上述尚未闭合的动作，执行端必须依据 Doc 43 V2 规则三**立即阻断并向人类上报能力边界**，严禁退回裸内存强写。

---

## 二、 REA Native 动作路由与参数枚举字典

### 1. 已认证 REA Native 动作清单

| 业务动作 | REA Action ID | Runtime Handler | 原生 RVA | 前置游戏阶段与实测状态 |
| :--- | :--- | :--- | :---: | :--- |
| **直接强制签约成交** *(休赛期默认推荐)* | `SIGN_FREE_AGENT_DIRECT_PROCESS` | `sign.process` (`Status=6 ACCEPTED -> 8 SIGNED`) | `0x12BDE70` | `Period == 22 (FA_SIGNING)`；**2026-11-24 实机 104/104 全部签约落袋通过** |
| **提交自由球员报价** | `CONTRACT_SUBMIT_FREE_AGENT_OFFER` | `sign.offer_fa_phase` (`runtime/sign_fa_offer.js`) | `0x12BD4C0` | `Period == 22 (FA_SIGNING)` 且 `Rules + 0x208 == 1`（受工资帽拦截） |
| **撤回待处理报价** | `CONTRACT_WITHDRAW_PENDING_OFFER` | `sign.offer_withdraw` (`runtime/sign_withdraw_offer.js`) | - | 目标记录处于 `OFFERED` 状态 |
| **读取球队报价池** | `READ_TEAM_SIGNING_OFFERS` | `read.signing_offers` (`runtime/read_signing_offers.js`) | - | 只读双扫描一致性快照 |
| **读取球员当前合同** | `READ_PLAYER_CONTRACT` | `read.player_contract` (`runtime/read_player_contract.js`) | - | 只读 17 项物理合同字段 |

> **直接强制签约（`sign.process`）调用契约**：构造 44 字节私有 `Proposal`（`PlayerId`, `TeamId`, `Wage`, `ForcedWage[6]`, `Years`, `Type=2 FREE_AGENT`, `Status=6 ACCEPTED`, `NegLevel=3`, `OptionType`, `NoTradeClause`），直接调用 `sign.process(proposal, ptr(0), 0, 0x6fea8977, 0x72a)`，成功后 `Status` 跃迁为 `8 (SIGNED)` 并直接入驻目标球队名册。

### 2. `CONTRACT_SUBMIT_FREE_AGENT_OFFER` 强类型参数契约

| 参数字段 | 类型与值域 | 说明与硬性约束 |
| :--- | :--- | :--- |
| `team_id` | `int` (`0 ~ 29`) | 报价发起球队原生 UID |
| `player_id` | `int` (`0 ~ 65534`) | 目标自由球员原生 UID，必须唯一存在于原生可用自由球员池（`sign.fa_available_pool`）且无现存基础/续约年限 |
| `contract.signing_type` | `"FREE_AGENT"` | 当前接口仅支持自由球员报价（原生 `sign.default_type` 必须返回 `2`） |
| `contract.contract_type` | `"NORMAL"` \| `"HARDSHIP"` | `0`: NORMAL, `2`: HARDSHIP |
| `contract.distribution` | `"CUSTOM"` | 仅允许自定义逐年薪资序列，不走自动涨跌幅生成器 |
| `contract.years_native` | `int` (`1 ~ 6`) | 含选项在内的总合同年限，必须大于等于选项所需最小年数 |
| `contract.annual_wages_native` | `int[6]` | 固定长度 6 的整数数组（单位：原生整数美元）。激活年份必须为 `1 ~ 2147483647`；未用年份槽位**必须严格为 `0`** |
| `contract.option_type` | `"NO_OPTION"` \| `"TEAM_OPTION"` \| `"PLAYER_OPTION"` \| `"TEAM_OPTION_2"` | 对应 `0` (0年), `1` (1年), `2` (1年), `3` (2年) |
| `contract.no_trade_clause` | `bool` | 是否包含交易否决权 |

---

## 三、 标准化签约报价规格书 JSON Schema (Machine-Ready Spec)

上游规划/决策模型输出目录：`C:\nba2k22\exports\YYYYMMDD_<task_name>_execution\`  
文件命名：`<SIGNING_ID>_signing_spec.json`（或按球队拆分 `{tid:02d}_{abbr}_signing_spec.json`）

```json
{
  "protocol_version": "v2.0_rea_native_signing",
  "task_package_id": "20261124_OFFSEASON_FA_OFFERS_LAL",
  "target_career": "MyLEAGUE0005",
  "target_process": "NBA2K22.exe",
  "required_game_period": "FA_SIGNING",
  "source_research_docs": [
    "26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md",
    "FA_OFFER_NATIVE_CONTRACT.md"
  ],
  "signings": [
    {
      "signing_item_id": "SIGN_2021_LAL_MELO_01",
      "decision_rationale": "【休赛期自由市场签约】湖人队以老将底薪向自由球员卡梅隆·安东尼提交 1 年期正式报价，补强锋线外线投射",
      "target_team": {
        "team_id": 13,
        "team_abbr": "LAL",
        "team_name": "Los Angeles Lakers"
      },
      "player": {
        "native_player_id": 1022,
        "player_name": "Carmelo Anthony",
        "cyberface_id": 1022
      },
      "rea_action_intent": {
        "action_id": "CONTRACT_SUBMIT_FREE_AGENT_OFFER",
        "parameters": {
          "team_id": 13,
          "player_id": 1022,
          "contract": {
            "signing_type": "FREE_AGENT",
            "annual_wages_native": [2641691, 0, 0, 0, 0, 0],
            "years_native": 1,
            "option_type": "NO_OPTION",
            "contract_type": "NORMAL",
            "distribution": "CUSTOM",
            "no_trade_clause": false
          }
        }
      }
    }
  ]
}
```

---

## 四、 REA 调用映射与 CAS 闭环验收标准

### 1. 执行端解析与 REA 调度流

1. **前置游戏阶段与资格核验**：
   - 执行模型读取 `signings[].rea_action_intent`；
   - REA `sign_fa_offer.js` 自动检查当前处于 `FA_SIGNING` (`period == 22`)、规则根节点就绪（`+0x208 == 1`）、代理虚表（Delegate vtable）与调优区间合法、目标球员唯一存在于原生可用自由球员池且无重复待处理报价；
   - 任意条件不满足时立即抛出对应错误并阻断上报，不执行任何写入。
2. **单次原生报价提交**：
   - 通过 `NativeControlFacade.submit_contract_offer(...)`（或 `DecisionOutbox` 提交 `ActionIntent`）在私有 `Memory.alloc(44)` 构造报文并单次调用 `sign.offer_fa_phase`；
   - 单次任务严禁自动重试或自行修改报价金额。
3. **独立只读回读核验 (Independent Readback CAS)**：
   - 若返回 `1`（`NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`），立即校验报价池中新增 exactly 1 条 `Status == 1 (OFFERED)` 记录且条款 100% 匹配输入；
   - 调用 `READ_TEAM_SIGNING_OFFERS` 与 `READ_PLAYER_CONTRACT` 进行独立只读确认，确认球员底层物理合同在确认签约前未被意外篡改。

### 2. 标准化执行回执 (`SIGNING_EXECUTION_RECEIPT.json`)

```json
{
  "protocol_version": "v2.0_rea_native_signing",
  "task_package_id": "20261124_OFFSEASON_FA_OFFERS_LAL",
  "status": "APPLIED_READBACK_CONFIRMED",
  "items_total": 1,
  "items_verified": 1,
  "mismatches_count": 0,
  "results": [
    {
      "signing_item_id": "SIGN_2021_LAL_MELO_01",
      "action_id": "CONTRACT_SUBMIT_FREE_AGENT_OFFER",
      "native_outcome": "NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED",
      "submission_only": true,
      "signing_completed": false,
      "observed_pool_status": "OFFERED",
      "decided_terms_preserved": true,
      "physical_contract_subset_unchanged": true
    }
  ]
}
```
