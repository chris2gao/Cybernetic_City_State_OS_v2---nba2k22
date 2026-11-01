# Stage02 · 针对独立审核六项发现的定向整改证据

- 原执行交付：`cf95f2451bbe5722b6d946434078c515564252a9`，独立审核：`553ee3af68dba5cd42e52969e739ab0748989faa`，本次整改静态输入 HEAD `0b078012087707f4cbf527d7536af456b3ae7f04`。
- 审核裁定 `REWORK_REQUIRED_TARGETED_EVIDENCE_GATES`。本执行窗口**提出整改复审候选**，未宣布审核者关闭发现。

| Findings | 本次整改 | 证据成熟度 |
|---|---|---|
| S02-P0-01 | M3/M4 7项Team Box 0/2124列降级，2项Opponent改为JOIN或Native发现；连同原来16项Reader标签全面逐列重分类 | 固定WorldData v24 field-maturity，非重新运行SQLite |
| S02-P0-02 | `PLAYER_PTS` 旧26400值明确来自已有公式 `2*fg_made + three_made + ft_made`（fixture），独立PC22 Native PTS仍 UNKNOWN | 不新增公式或直接替代来源 |
| S02-P1-03 | 15个Graph `MET_*`聚合节点显式JOIN 38个指标中的具体ID，给出实体/粒度及Reader状态，三条端到端链测试 | 纯语义、无新已证因果边 |
| S02-P1-04 | 逐字段GPT质量索引：24个规范元数据键缺项、3条ledger计数差异、15份顶层冲突键缺失，均有固定审计+源档案位置；51条NO_DIRECT标记保留 | 审计异常不自动等于Native字段失败 |
| S02-P2-05 | 保存旧M01–M09收据历史快照，M04/M06标记修订，M09标记prepublication边界及已验证cf95远端发布事实 | 本次新最终HEAD需另行GitHub回读，无法在同提交自引用 |
| S02-P2-06 | 12个无边节点逐一标记UNLINKED_PROSPECTIVE_NODE及原因。Rebound POE是仅候选语义不等于Native因果 | 不加虚构边 |

## 原生数据优先裁决

`schema_present`、`materialized_non_null`、`source_declaration`、`native_UI_or_getter_proof`、`current_MC_available`互相独立。球队Box有2124行≠其已空字段有值；fixture生成的player_box非NULL≠当前Native读取；旧派生PTS≠游戏原生得分。实际`player_attribute_snapshots`部分属性具旧表Native声明与非NULL，但例如`overall_raw` 0/9822，必须按字段考证。

## 未扩展权限

204字段身份、68节点、50边、38原生指标与来源缺口、16行为映射、3组可证伪未执行Pilot、Human持续学习原则全部保留。没有修改采集器、物理SQL、游戏、MC存档、REA Setter、Gemini分支、Core或NBA master。

静态检查明细：`07_测试执行/targeted_remediation_verification.json`。目标状态：`EXECUTION_REWORK_DELIVERED_PENDING_INDEPENDENT_REREVIEW`。不代替下一审核窗口的PASS/FAIL裁定。
