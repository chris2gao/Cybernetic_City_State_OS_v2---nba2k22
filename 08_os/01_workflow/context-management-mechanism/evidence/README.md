# context-management-mechanism · evidence 文件清单

本目录是 workflow `context-management-mechanism` 阶段二 `02_信息收集与提炼` 的耐久产物目录。

## 一、文件角色与当前实际路径

| 角色 | 实际路径 | 性质 |
|---|---|---|
| 机器可读研究目标 | `00_挖掘目标与领域_v1.yml` | canonical |
| NotebookLM 上传镜像 | `00_挖掘目标与领域_v1.md` | derived mirror |
| 机器可读内部证据 | `01_内部证据_v1.yml` | canonical |
| NotebookLM 上传镜像 | `01_内部证据_v1.md` | derived mirror |
| 普通 Web 检索预跑 | `02_ChatGPT外部检索_v1.md` | 预跑，不进入双路线覆盖测量 |
| 双路线与综合派单 | `03_独立检索与综合派单_v1.md` | 执行说明 |
| ChatGPT 正式 Deep Research | `chatgpt - deep-research-report.md` | 原始外部证据 |
| Gemini 正式 Deep Research | `gemini - Multi-Model OS Context Research.md` | 原始外部证据 |
| NotebookLM 第三方匹配 | `06_NotebookLM_第三方匹配_v1.md` | 候选匹配与缺口识别 |
| 最终证据索引与可行性判断 | `07_证据索引与可行性判断_v1.yml` | 待生成；阶段二最终交接产物 |

## 二、canonical 与上传镜像

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

## 三、本次 NotebookLM 精确上传清单

必须上传以下四个文件，路径均相对于仓库根目录：

```text
08_os/01_workflow/context-management-mechanism/evidence/00_挖掘目标与领域_v1.md
08_os/01_workflow/context-management-mechanism/evidence/01_内部证据_v1.md
08_os/01_workflow/context-management-mechanism/evidence/chatgpt - deep-research-report.md
08_os/01_workflow/context-management-mechanism/evidence/gemini - Multi-Model OS Context Research.md
```

NotebookLM 输出必须保存到：

```text
08_os/01_workflow/context-management-mechanism/evidence/06_NotebookLM_第三方匹配_v1.md
```

`02_ChatGPT外部检索_v1.md` 是预跑材料，不进入 NotebookLM 双路线正式匹配。

## 四、以后所有外部研究派单的文件落点契约

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

## 五、当前 NotebookLM 结果的边界

`06_NotebookLM_第三方匹配_v1.md` 已完成：

- 定向结论的共同项、分歧和单一路线项；
- 三类开放发现清单的重合与候选同义项；
- 外部证据与第一代内部证据的对照。

但它没有完全满足派单中的一项要求：**逐条给出两份报告的精确原文位置**。

因此当前定位是：

```yaml
notebooklm_result_status: candidate_mapping
may_support_final_merge: true
may_be_used_as_final_source_proof_without_recheck: false
required_follow_up: 合并方回到两份原始报告核对关键匹配与来源独立性
```

NotebookLM 负责扎根匹配，不替代合并方的最终证据裁定。