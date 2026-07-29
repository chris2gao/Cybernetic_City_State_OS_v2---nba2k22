# 外部工具中转与 Codex 委派契约 v1

## 目的

把无法直接连接的 Web 工具纳入 workflow，同时不依赖聊天记忆传递任务。

GitHub 是唯一耐久派单面。任何需要人类中转给 NotebookLM、Gemini、其他 Web 模型，或需要 Codex 执行的工作，都必须先形成仓库内的完整任务包。

## 一、NotebookLM 人工中转

### 职责分工

- 规划/分析角色：准备全部输入文件、上传顺序、完整提问正文、启动条件、输出格式和精确回存路径。
- 人类：按任务包把指定文件上传 NotebookLM，粘贴指定提问正文，将完整原始输出回存到指定路径。
- 合并方：回读输出，检查路径、完整性、原文定位和扎根性；不把人类中转视为语义审核。

### GitHub 派单包必须包含

```yaml
operation: notebooklm_human_relay
status: ready_to_send
upload_inputs:
  - <仓库根目录起算的完整路径>
upload_order:
  - <按序列出的文件>
prompt_ref: <完整提问正文所在文件路径>
prompt_section: <精确标题或行范围>
start_when:
  - <全部前置条件>
expected_output:
  format: md
  required_sections:
    - <必须返回的部分>
upload_output_path: <NotebookLM 原始输出的精确回存路径>
completion_check:
  - <完整性与扎根性检查>
```

### 规则

1. 不在聊天窗口单独发布关键提问正文；聊天只发布任务包指针与摘要。
2. 人类不需要自行判断上传哪些文件、放到哪里、用什么文件名。
3. NotebookLM 不支持 canonical 格式时，规划方先在 GitHub 建立 `derived_mirror`，并核对内容一致性。
4. NotebookLM 输出必须原样回存；整理、裁剪和结论提炼由合并方另建产物完成。
5. 需要补问时，新建编号化补问任务文件，不覆盖上一轮请求和输出。

## 二、Codex 委派

### 适合交给 Codex 的工作

- 本地文件批量转换、重命名和索引生成；
- schema、validator、确定性计算和测试实现；
- 从已裁定的证据清单生成结构化中间产物；
- 运行本机隔离、权限、路径和恢复试验；
- 执行明确 allowed paths、完成条件和测试命令的实现任务。

### 不应直接交给 Codex 的工作

- 决定需求 A 的语义；
- 裁定两个证据是否表达同一机制；
- 选择最终方案 B；
- 在缺少明确输入和验收标准时自行扩大范围；
- 代替独立审核者审核自己的实现。

### Codex 任务包必须包含

```yaml
operation: codex_execution
status: ready_to_dispatch
task_id: <稳定标识>
source_branch: <分支>
source_head: <不可变提交>
inputs:
  - <精确文件或提交引用>
allowed_paths:
  - <允许修改路径>
forbidden_paths:
  - <禁止修改路径>
required_outputs:
  - <精确输出路径>
acceptance_tests:
  - <可执行测试或确定性判据>
publication_policy:
  source_push_authorized: false
  work_branch: <工作分支>
  review_required: true
```

### 委派原则

- 理解、证据裁定和结果选择由规划/分析与人类负责；确定性执行优先交给 Codex。
- Codex 只能消费任务包明确授权的输入，不通过聊天补齐隐含上下文。
- Codex 输出必须由独立角色按精确提交审核。

## 三、当前人工中转者

```yaml
human_relay:
  operator: GK
  notebooklm:
    action: 上传 GitHub 指定文件、粘贴指定正文、回存完整输出
  semantic_decision: false
```

人类中转是传输通道，不承担证据结论的默认背书。
