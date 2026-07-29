# context-management-mechanism · evidence 文件清单

本目录是 workflow `context-management-mechanism` 阶段二 `02_信息收集与提炼` 的耐久产物目录。

## 一、阶段状态

```yaml
stage: 02_信息收集与提炼
status: completed_with_residuals
requirement_version: 2
requirement_ref: 08_os/03_mechanisms/context_management/依据材料/requirement/A_需求建模_v2.yml
requirement_confirmation_ref: 08_os/03_mechanisms/context_management/依据材料/requirement/人类确认_v2.yml
final_evidence_ref: 07_证据索引与可行性判断_v1.yml
feasibility: partially_supported
stop_stage_02: true
mechanism_3_ready: true
```

阶段二已经完成双路线发现、第三方候选匹配、合并方语义裁定、Chapman 统计、本机运行试验和最终证据收口。
当前闭包以 Human 确认的 `A_需求建模_v2.yml` 与 `人类确认_v2.yml` 为有效需求锚点；
`A_需求建模_v1.yml` 与 `人类确认_v1.yml` 作为已被取代的历史记录保留。

A v2 固定 Web 交接的结果要求：按任务和 Web 角色独立授权、不可读取主仓库或其他空间、可撤销、可审计，
并只暴露获准输入、接收结构化结果。独立仓库、受控交接网关或其他同等边界实现由 B 比较选择，
所以具体拓扑不阻塞 `03_结果建模`；B 选定实现后，相应 `05_步骤拆分`、`06_执行` 必须等待所需测试。
`repo-per-role` 的生命周期成本仍未验证，若 B 选择该候选，须另行取得保护授权。

## 二、文件角色与当前实际路径

| 角色 | 实际路径 | 性质 |
|---|---|---|
| 机器可读研究目标 | `00_挖掘目标与领域_v1.yml` | canonical |
| NotebookLM 上传镜像 | `00_挖掘目标与领域_v1.md` | derived mirror |
| 机器可读内部证据 | `01_内部证据_v1.yml` | canonical |
| NotebookLM 上传镜像 | `01_内部证据_v1.md` | derived mirror |
| 普通 Web 检索预跑 | `02_ChatGPT外部检索_v1.md` | 预跑，不进入双路线覆盖测量 |
| 双路线与综合派单 | `03_独立检索与综合派单_v1.md` | 执行说明 |
| ChatGPT 正式 Deep Research | `chatgpt - deep-research-report.md` | 原始外部研究路线 |
| Gemini 正式 Deep Research | `gemini - Multi-Model OS Context Research.md` | 原始外部研究路线 |
| NotebookLM 第三方匹配 | `06_NotebookLM_第三方匹配_v1.md` | 候选匹配与缺口识别 |
| 合并方语义裁定 | `07a_机制同义裁定_v1.yml` | canonical synthesis |
| 开放发现统计 | `07b_开放发现统计_v1.yml` | canonical calculation |
| 证据索引草案 | `07c_证据索引草案_v1.yml` | historical draft，已被最终文件取代 |
| Codex 本机试验任务 | `08_Codex_本机分区运行试验任务_v1.yml` | execution packet |
| 本机运行试验报告 | `09_本机默认分区试验_v1.md` | canonical runtime evidence |
| 最终证据索引、可行性、边界、停止与 B 交接 | `07_证据索引与可行性判断_v1.yml` | 阶段二最终 canonical 交接产物 |

## 三、canonical 与上传镜像

`00`、`01` 的 `.yml` 文件是机器消费的 canonical 版本。

NotebookLM 当前不能上传 YAML，因此建立内容完全相同的 `.md` 镜像。镜像规则：

1. `.md` 只解决工具格式兼容，不形成新的独立证据；
2. `.md` 不得人工单独修改；
3. canonical YAML 变化时，必须同步重建 Markdown 镜像；
4. 上传前应核对两者内容 hash 或 Git blob SHA 相同；
5. 下游程序与机制 3 默认引用 `.yml`，NotebookLM 上传使用 `.md`。

本次核对结果：

```yaml
00_YAML_MD_blob_sha_identical: true
01_YAML_MD_blob_sha_identical: true
```

## 四、本次 NotebookLM 精确上传清单

上传文件路径均相对于仓库根目录：

```text
08_os/03_mechanisms/context_management/依据材料/evidence/00_挖掘目标与领域_v1.md
08_os/03_mechanisms/context_management/依据材料/evidence/01_内部证据_v1.md
08_os/03_mechanisms/context_management/依据材料/evidence/chatgpt - deep-research-report.md
08_os/03_mechanisms/context_management/依据材料/evidence/gemini - Multi-Model OS Context Research.md
```

NotebookLM 输出保存到：

```text
08_os/03_mechanisms/context_management/依据材料/evidence/06_NotebookLM_第三方匹配_v1.md
```

`02_ChatGPT外部检索_v1.md` 是预跑材料，不进入 NotebookLM 双路线正式匹配。

## 五、以后所有外部研究派单的文件落点契约

派单发布前必须同时写明：

```yaml
output_directory: <仓库内完整目录>
output_filename: <精确文件名>
output_format: <md|yml|json|其他>
canonical_or_mirror: <canonical|derived_mirror|raw_evidence|synthesis>
upload_inputs:
  - <每个待上传文件的完整仓库路径>
upload_output_path: <第三方工具输出的完整仓库路径>
start_when: <所有前置文件齐备条件>
```

不得只写“输出文件建议”，也不得要求人类自行推断存放目录。

## 六、NotebookLM 结果与合并裁定边界

`06_NotebookLM_第三方匹配_v1.md` 完成了共同项、分歧、单一路线项和候选同义映射，但没有完全满足逐条给出精确原文位置的要求。

因此它的最终定位是：

```yaml
notebooklm_result_status: candidate_mapping
may_support_final_merge: true
may_be_used_as_final_source_proof_without_recheck: false
follow_up_status: completed_by_07a_semantic_adjudication
```

NotebookLM 负责扎根匹配，不替代合并方的最终证据裁定。

## 七、最终结论的关键边界

- `clone/worktree` 是工作区组织分区，不是访问边界；
- Windows DACL 只验证当前主体正常读取路径，不是不可绕过的生产沙箱；
- 角色发布必须使用显式 `publish_allowlist`，禁止默认 `git add --all`；
- 固定入口、结构化 handoff 和内容指纹 stale 已完成最小运行验证；
- 输入体积显著缩小不等于模型质量提高；
- Web 受限交接的独立授权、不可越界、可撤销和可审计是 A v2 硬结果约束；
- GitHub `repo-per-role` 只是候选实现，其实际运营成本尚未验证，不得在 B 中写成既定方案。
