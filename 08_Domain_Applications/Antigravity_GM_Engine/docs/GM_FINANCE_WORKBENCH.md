# GM财务与三年情景工作台

版本 `gm_finance_projection_v1`。读取现有同批静态查询快照，计算派生财务情景，保存到 `database/workbench/<career>/gm_workbench.sqlite`。本工具不进行报价竞价，不批准或执行交易/签约，不修改游戏或事实库。

## 实际命令

在项目根目录运行：

```powershell
python -B scripts/gm_finance.py project --career mc_haliburton_2021 --base-season 2021-2022 --run finance_review_01
python -B scripts/gm_finance.py list --career mc_haliburton_2021
python -B scripts/gm_finance.py show --career mc_haliburton_2021 --run finance_review_01 --team SAS
python -B scripts/gm_finance.py show --career mc_haliburton_2021 --run finance_review_01 --team SAS --contracts --season 2022-2023 --limit 20
python -B scripts/gm_finance.py compare --career mc_haliburton_2021 --run finance_review_01 --scenario examples/gm_finance_scenario.json
python -B scripts/gm_finance.py show --career mc_haliburton_2021 --run finance_review_01 --scenario internal_review --team SAS
python -B scripts/gm_finance.py export --career mc_haliburton_2021 --run finance_review_01
```

`--batch`固定历史/当前批次；省略时由M0按本地published/latest解析。`--base-season`在快照context缺少season时必填；本轮M02便属于这种情况，不能只从日期推断休赛期是否已过账。`--horizon`默认3（当前季+随后两季），最多6。`--workbench`可指定独立开发库，但文件名必须是gm_workbench.sqlite；解析后的路径不能位于saves/query_snapshots/published/seasons（忽略大小写）。读取模式不会创建不存在的库。

project创建新run，相同ID拒绝覆盖。compare为每个互斥备选保存新scenario_id；不同情景可使用同一资产，同一情景内不能重复转让。show只读；合同明细和情景行支持limit/offset并返回next_offset。export默认写入 `_exports/finance/<run>`，目录存在就拒绝覆盖；自定义输出同样拒绝saves/query_snapshots/published/seasons目录，生成精简summary.json及Markdown，不上传工作台。

## 金额解释

- 原始六薪资槽仍是已采编码金额；默认按“slot1为base_season，后续顺延”计算，结果明确为SCENARIO。
- `projected_salary_total`为所有输入槽完整时的情景总额；缺金额时为null，`projected_known_subtotal`仍返回已知部分与覆盖程度。
- `known_salary_subtotal/total`只接纳具有可靠季节映射且无未决条件的条目。当前M02尚没有这种认证，不把三年情景重命名为保证承诺。
- 选项年度明确后可输出exercise/decline分支；未知选项/延期保留条件，不把years_left=1认证为自由球员，不自动叠加延期金额。
- cash/budget/payroll保留独立原始口径。工资帽/税线差只在显式给定适用年度参考值时计算proxy；`signing_capacity`保持UNKNOWN。

可选 `--assumptions FILE`：

```json
{
  "phase": "REGULAR_SEASON",
  "reference_lines": {"2021-2022": {"salary_cap": 112414000, "tax_line": 136606000}},
  "player_overrides": {
    "EXACT_BATCH_LOCAL_IDENTITY": {
      "slot_seasons": {"1": "2021-2022", "2": "2022-2023"},
      "option_season": "2023-2024",
      "option_decision": "EXERCISE"
    }
  }
}
```

参考线例子仅为现实NBA2021–22历史值，非本局认证。override仍为调用者情景假设，不升级为源观测。`--policy FILE`可携带ExternalFinancePolicyV1（字段见M1设计）：DRAFT、适用年度/局/阶段不符、缺少可靠金额/语义时只返回UNKNOWN。输入里的PLAYER_CONFIRMED声明只用于该情景的规则口径，不构成游戏动作批准；程序从不据此调用执行器。

## 情景输入

kind为KEEP、INTERNAL_COACHING或TRADE_OR_SIGNING。moves只在第三种允许；当前支持：

| type | 输入 |
| --- | --- |
| TRADE_PLAYER | identity、from_team_id、to_team_id |
| TRADE_PICK | asset_id、from_team_id、to_team_id；当前持有且同批trade_eligible=1 |
| SIGN_NEW | 新的候选identity/name、to_team_id、effective_season、salaries整数列表；不认证FA资格 |
| REPLACE_CURRENT | 本队identity、to_team_id、effective_season必须当前基准季、salaries |
| EXTEND_FUTURE | 本队identity、to_team_id、未来effective_season、salaries；该季起明确替换情景，保留前段原合同 |

逐年合同金额必须为正整数，最多6年，受现有31位金额格式约束。交易移动同一工资向量；合同替换先移除该段旧条目再加入，不双算。未来情景结束后的0是“未另续约”的假设，不认证真实无义务。输出双方逐年差额、人数变化、资产去向、机会成本、三种方案比较、财务与执行缺口。签约/替换/延期始终标BLOCKED_EXECUTOR，实际执行按文档38另行处理。

## 直接相关验收

`python -B -m unittest discover -s tests -p test_gm_finance_m1.py -v`覆盖金额缺失/条件、交易向量/重复资产、替换与延期、政策口径、存储事务及只读路径。`python -B scripts/check_gm_finance_m1.py`仅对已有M02静态副本生成开发run、钻取GSW/SAS/CLE并检查保存/小结果/导出，证据位于忽略的_exports。不会进行新采集或游戏操作。
