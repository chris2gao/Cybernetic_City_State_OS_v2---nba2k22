# B 主要实现说明 v1

> 状态：共同审阅草案，不是已确认结果模型。  
> 依据：A v2、阶段二证据、Antigravity 双模型家族实验、旧系统只读缺口对照，以及 Human 共同审阅批次 001。

## 1. 这套通讯系统到底是什么

它不是自动消息总线，也不是一个需要所有模型常驻监听的服务。

它是一个**按 task 隔离的文件通讯空间**：

1. 模型把需要长期或完整表达的内容写入文件；
2. 模型发布一条短而完整的结构化消息，指向需要读取的文件；
3. Human 决定是否转发、转给哪个实际模型、何时继续；
4. 接收模型只读取消息明确列出的直接引用，不自动扫描全部历史；
5. 确定性工具负责创建目录、分配序号、校验格式和执行清理；
6. 权限仍由任务角色和 Human 授权决定，通讯消息本身不授予权限。

目标不是模拟即时通讯软件，而是让不同产品、不同机器、Web 与本地模型都能通过相同的对象语义交换完整信息，同时避免聊天框堆积和重复加载。

---

## 2. 主要组成

### 2.1 全局发现索引

用途仅是找到某个 task 的通讯空间，不保存消息正文。

建议位置：

```text
GitHub: 01_os/_communication/index.yml
Local:  <configured_root>/index.yml
```

每个 task 只需要一条发现记录，例如：

```yaml
repository_id: core
task_id: os-v2-global-communication-system-001
task_root: 01_os/_communication/tasks/os-v2-global-communication-system-001
carrier: GitHub
coordinator_endpoint_id: chatgpt-web-planner-01
status: active
last_Human_update_at: 2026-08-05T22:38:00-07:00
```

这是导航，不是通讯状态机，也不负责列出全部消息。

### 2.2 task 通讯空间

GitHub 建议根：

```text
01_os/_communication/tasks/<task_id>/
```

本地建议根：

```text
<configured_machine_global_root>/<repository_id>/<task_id>/
```

逻辑目录保持一致：

```text
<task_root>/
├─ manifest.yml
├─ endpoints/
│  └─ <endpoint_id>.yml
├─ Human/
│  ├─ current.yml
│  └─ decisions/
├─ durable/
│  ├─ final_results/
│  └─ material_failures/
└─ runtime/
   ├─ indexes/
   │  └─ <sender_endpoint_id>.yml
   ├─ messages/
   │  └─ <sender_endpoint_id>/
   ├─ documents/
   │  └─ <sender_endpoint_id>/
   └─ scratch/
```

批次 001 已取消 task 级共享 `index.yml`。每个 sender 维护自己的索引，避免多个端点争用同一个文件。

### 2.3 manifest

`manifest.yml` 是 task 的入口说明，不保存动态消息历史。

主要包含：

- repository_id 与 task_id；
- task 目标；
- 载体和根路径；
- 当前任务分支或本地作用域；
- coordinator；
- endpoint card 列表；
- Human current 位置；
- 隐私规则；
- 生命周期状态；
- 通讯契约版本。

manifest 不授予权限，也不记录谁已经读取消息。

### 2.4 endpoint card

每个模型窗口、CLI 会话或 Human 实例使用一个独立 endpoint_id。

endpoint card 描述：

- 它是谁；
- 是 Web、本地桌面、CLI 还是 Human；
- 产品或模型名称；
- 当前 task role；
- 能否读写本地文件；
- 能否读写 GitHub；
- 实例标签。

它只声明当前能力，不授予权限。模型品牌、环境和任务角色必须分开，避免把“Claude”“Codex”之类产品名误当成权限。

---

## 3. sender 独立索引与 10000 条序号空间

### 3.1 为什么取消共享索引

多个端点可能同时在本地或 GitHub 发布消息。共享 `index.yml` 会产生：

- 每条消息都需要改同一个文件；
- GitHub 冲突概率上升；
- coordinator 成为不必要的消息发布瓶颈；
- 本地与线上多副本更难保持一致。

因此改为每个 sender 独立维护：

```text
runtime/indexes/<sender_endpoint_id>.yml
runtime/messages/<sender_endpoint_id>/
runtime/documents/<sender_endpoint_id>/
```

sender 只能写自己的三个区域。

### 3.2 序号规则

每个 task 中，每个 sender 独立拥有：

```text
00001 ... 10000
```

消息路径示例：

```text
runtime/messages/antigravity-desktop-executor-01/00001_request.yml
runtime/messages/antigravity-desktop-executor-01/00002_result.yml
```

消息 ID 示例：

```text
os-v2-global-communication-system-001::antigravity-desktop-executor-01::00002
```

每个 sender 的 index 只记录自己的消息：

```yaml
sender_endpoint_id: antigravity-desktop-executor-01
next_sequence: 3
entries:
  - sequence: 1
    message_id: os-v2-global-communication-system-001::antigravity-desktop-executor-01::00001
    title: 执行通讯理解实验
    exact_path: runtime/messages/antigravity-desktop-executor-01/00001_request.yml
    expected_recipient_endpoint_id: antigravity-desktop-opus-executor-01
    message_type: request
  - sequence: 2
    message_id: os-v2-global-communication-system-001::antigravity-desktop-executor-01::00002
    title: 返回通讯理解实验结果
    exact_path: runtime/messages/antigravity-desktop-executor-01/00002_result.yml
    expected_recipient_endpoint_id: chatgpt-web-planner-01
    message_type: result
```

达到 10000 时 v1 fail-closed，不自动扩容、不重用旧序号。理论上单个 sender 在单个 task 不会达到上限；若真的发生，说明 task 边界或通讯粒度需要 Human 重新判断。

### 3.3 如何看整个 task 的消息

默认不维持持续聚合索引。

需要全局视图时：

- Human 选择若干 sender index；
- AI 或工具临时聚合并排序；
- 聚合结果可以只显示在当前会话，也可以在 Human 要求时写入一个派生报告；
- 派生报告不是权威消息源，sender index 和消息文件才是原始记录。

这样把共享写入成本降到最低。

---

## 4. 一条消息的实际结构

批次 001 已删除 `summary`，避免与短 `content` 重复。

建议消息：

```yaml
message_id: os-v2-global-communication-system-001::chatgpt-web-planner-01::00007
task_id: os-v2-global-communication-system-001
title: 请求执行冻结测试
message_type: request
sender_endpoint_id: chatgpt-web-planner-01
expected_recipient_endpoint_id: antigravity-desktop-executor-01
content: >-
  按测试包执行冻结测试，只修改任务允许路径。完成后发布结果消息；
  如发现授权或输入缺失，停止并返回 blocked 消息。
requested_action: 执行测试包并发布结果
required_refs:
  - durable/final_results/test_package_v1.yml
  - Human/decisions/authorization_test_execution_v1.yml
authorization_ref: Human/decisions/authorization_test_execution_v1.yml
```

### 必填信息

- message_id；
- task_id；
- title；
- message_type；
- sender_endpoint_id；
- expected_recipient_endpoint_id；
- content；
- requested_action；
- required_refs。

`requested_action` 可以明确写 `none`，用于纯结果或信息消息。

### 可选信息

仅在有实际价值时添加：

- in_reply_to；
- supersedes；
- references；
- authorization_ref；
- facts、decisions、assumptions、unknowns、constraints、risks。

空的可选段不应出现。

### 不进入消息的内容

- 长报告；
- 大段 diff；
- 完整日志；
- 投递、已读、理解或接受状态；
- actual recipient 记录；
- 普通消息自定义 digest；
- 模型私有推理过程。

---

## 5. 长内容如何处理

长内容放在：

```text
runtime/documents/<author_endpoint_id>/
```

需要长期保存时再提升到：

```text
Human/decisions/
durable/final_results/
durable/material_failures/
```

常规通讯文档建议 Markdown + YAML front matter：

```markdown
---
document_id: test-report-001
task_id: os-v2-global-communication-system-001
author_endpoint_id: antigravity-desktop-executor-01
purpose: 冻结测试执行报告
privacy_class: repository_shareable
---

# 测试结果
...
```

已有源代码、任务包、测试文件或其他资源可以被消息直接引用，不需要为了通讯重新包装一份副本。

文档发布后不原地修改；修正时创建新版本，由新消息引用并用 `supersedes` 表明关系。

---

## 6. 消息发布流程

### 6.1 普通本地发布

1. sender 读取自己的 index；
2. 取得 `next_sequence`；
3. 如果需要长文档，先写入自己的 documents 目录；
4. validator 校验文档和 required_refs；
5. publisher 创建新的消息文件，拒绝覆盖已有路径；
6. publisher 将新条目追加到 sender 自己的 index；
7. 成功即表示 `sent`；不表示接收方已经读取。

本地 v1 的“不可变”是工具与契约级：publisher 不覆盖、序号不回退、validator 能发现修改。它不是文件系统 ACL 或密码学防篡改。

### 6.2 普通 GitHub 发布

sender-owned 新消息、新文档和 sender index 均属于追加式写入。

推荐一次提交包含：

- 新文档；
- 新消息；
- sender 自己的 index 更新。

发布前读取当前 task branch HEAD；若期间 HEAD 变化：

- 如果变化只来自其他 sender 的独占目录，执行模型可在重新确认无路径冲突后进行一次新的正常提交；
- 如果涉及自己预期写入的路径或共享文件，fail-closed 并报告精确冲突；
- 不建立自动无限重试。

是否允许“一次无冲突重试”应在后续共同审阅中最终确定。

### 6.3 共享文件写入

共享可变文件目前只有少数：

- manifest.yml；
- Human/current.yml；
- 全局发现 index。

这些写入必须绑定预期 HEAD，HEAD 改变时停止，不允许静默覆盖。

---

## 7. Human 如何中转

Human 在聊天里只需要发送紧凑指针：

```yaml
task_id: os-v2-global-communication-system-001
message_id: os-v2-global-communication-system-001::chatgpt-web-planner-01::00007
carrier: GitHub
exact_path_or_GitHub_ref: >-
  chris2gao/Cybernetic_City_State_OS_v2---core@dev/os-v2-global-communication-system-001:
  01_os/_communication/tasks/os-v2-global-communication-system-001/runtime/messages/chatgpt-web-planner-01/00007_request.yml
sender_endpoint_id: chatgpt-web-planner-01
expected_recipient_endpoint_id: antigravity-desktop-executor-01
one_line_purpose: 执行冻结测试
```

Human 可以：

- 转给预期模型；
- 转给另一个模型；
- 暂缓；
- 不转；
- 终止通讯链。

expected recipient 只是发送方建议，不是系统自动路由结果。

Human 转发也不自动授予越权权限。接收模型仍受当前任务角色约束；需要越权时，消息必须指向一个明确 Human 授权文件。

---

## 8. 接收方如何读取

接收方收到指针后，只加载：

1. task manifest；
2. 自己的 endpoint card；
3. 指定消息；
4. 消息 `required_refs` 中列出的直接文件；
5. 若有 `authorization_ref`，它必须同时出现在 required_refs 中。

默认禁止：

- 扫描整个 task 目录；
- 自动读取所有 sender index；
- 递归展开被引用文档中的全部引用；
- 自动加载完整历史；
- 猜测缺失文件的替代路径。

如果信息不足，接收方发布新的 `blocked` 或 `request` 消息，精确列出：

- 缺失路径；
- 不可理解的字段；
- 需要补充的决定或授权；
- 当前无法执行的动作。

由 Human 决定是否将这个请求转回发送方或交给其他模型。

---

## 9. 本地与 GitHub 如何跨载体

不做自动同步，也不做所有内容双写。

### 本地转 Web

1. sender 或 coordinator 判断需要 Web 模型；
2. Human 确认转交；
3. 只挑选 `repository_shareable` 内容；
4. 将需要的文档重新发布到当前 task GitHub 分支；
5. 生成一条新的 GitHub 消息，required_refs 全部改为 GitHub 可读路径；
6. Human 把新的 GitHub 指针交给 Web 模型。

`local_only` 不得迁移，`forbidden` 不得进入任何载体。

### GitHub 转本地

本地模型如果能直接读 GitHub，可以直接使用 GitHub 消息；不强制复制到本地通讯根。

只有在需要离线工作、机器局部材料或本地后续链路时，才由 Human 选择重新发布为本地消息。

跨载体消息是新的 transport message，可以通过 `references` 指向原逻辑消息，但不假装两个载体文件是自动一致副本。

---

## 10. 权限如何工作

通讯系统不实现完整权限系统。

接收模型判断动作权限时依次看：

1. 当前 task；
2. 当前 task role；
3. 当前 Human 授权；
4. 仓库、工具和运行环境的现有保护。

消息正文不能自我授权。sender 身份、产品名、coordinator 名称也不能授权。

越权动作的消息必须：

- 包含 `authorization_ref`；
- authorization_ref 同时属于 required_refs；
- 接收方实际读取该授权；
- 授权内容明确到动作、对象和范围；
- 仍受更高层系统、安全和仓库保护约束。

validator 只能判断“引用结构是否齐全”，不能替 Human 授权，也不能证明授权内容真实有效。

---

## 11. Human/current.yml 如何使用

它不是每条消息更新的状态机，只是低成本 Human 入口。

建议内容：

```yaml
task_id: os-v2-global-communication-system-001
title: 全局通讯机制设计与实现
important_refs:
  - Human/decisions/result-model-discussion-batch-001.yml
  - durable/final_results/current-candidate.yml
current_decision_needed: review_B_main_implementation
```

只在以下情况更新：

- Human 需要决策；
- 重大阻塞或风险；
- 阶段完成；
- 最终结果就绪；
- Human 明确要求。

谁负责更新仍是一个可讨论点。当前候选是 Human 指定的 coordinator；也可以进一步简化为“产生该重大事件的 endpoint 更新，但必须使用共享 HEAD 冲突保护”。

---

## 12. 修正、失败和响应

### 修正

旧消息不改。创建新消息：

```yaml
message_type: correction
supersedes: <old_message_id>
```

### 响应

响应是一条新消息，使用：

```yaml
message_type: response
in_reply_to: <request_message_id>
```

### 失败

只有以下失败进入 durable/material_failures：

- 阻塞当前动作；
- 可能改变最终结论；
- 代表重大安全、隐私或数据风险。

普通工具调用失败、一次修复成功的路径错误等不需要长期记录。

`sent` 只表示文件或 GitHub 发布操作成功，不表示接收、已读、理解或接受。

---

## 13. runtime 清理

任务完成时：

1. 决策模型询问 Human 是否清理，或 Human 主动触发；
2. cleanup 工具只读取路径关系和引用关系，不读取正文来判断价值；
3. 列出需要提升的 runtime 文档和仍被 durable 对象引用的内容；
4. 任何 durable 引用仍指向 runtime 时，拒绝清理；
5. Human 确认提升清单；
6. 将需保留内容复制或重建为 durable 新版本，并更新 durable 引用；
7. 再删除固定 runtime 子树：indexes、messages、documents、scratch；
8. 保留 manifest、endpoint cards、Human decisions、final results、material failures。

清理只声明当前 task 通讯空间的 runtime 已删除，不宣称 Git 历史、镜像、备份或模型提供商副本被彻底擦除。

---

## 14. 预计实现的确定性工具

建议一个 Python CLI，而不是多个分散脚本：

```text
python communication.py init-task ...
python communication.py register-endpoint ...
python communication.py publish-document ...
python communication.py publish-message ...
python communication.py validate ...
python communication.py aggregate-indexes ...
python communication.py promote ...
python communication.py cleanup-preview ...
python communication.py cleanup-execute ...
```

### 工具必须负责

- 创建固定目录；
- 校验 task_id、endpoint_id、message_id；
- 分配 sender 自己的下一序号；
- 拒绝序号回退、重复或超过 10000；
- 拒绝覆盖已发布消息；
- 校验 required_refs 是否存在；
- 校验 authorization_ref 是否也在 required_refs；
- 检查隐私类和载体；
- 校验 YAML 安全子集；
- 校验 sender 写入所有权；
- GitHub 共享写入的 expected-head 冲突保护；
- 检查 durable → runtime 断链风险；
- 输出确定性错误码。

### 工具不负责

- 决定实际收件人；
- 判断任务业务结论；
- 授予权限；
- 自动同步本地与 GitHub；
- 自动轮询或通知；
- 判断哪些文件在语义上应该进入 required_refs；
- 自动读取整个仓库构造上下文。

---

## 15. YAML 安全子集

为了让不同模型和程序稳定读取，v1 YAML 限制为：

- UTF-8；
- 每文件一个 YAML 文档；
- 禁止重复 key；
- 禁止自定义 tag；
- 禁止 anchor、alias 和 merge key；
- 禁止对象构造或可执行特性；
- 必填字段未知或缺失时拒绝；
- 文件引用不能是目录、symlink 或 submodule；
- 通讯对象默认不得越出 task root，除非 task 明确允许外部 required_ref。

这不是因为 YAML 普遍优于 JSON，而是当前 v1 对 Human、GitHub 和两个已测模型家族都足够可读。未来可以保留 JSON 编码适配，但不在 v1 同时维护两套规范。

---

## 16. 当前判断：哪些是必要的

### 必要

1. 一个 task 一个通讯空间；
2. sender、expected recipient 和 endpoint card；
3. sender-owned 消息、文档和索引；
4. 长内容外置；
5. Human 手动选择实际接收方；
6. required_refs 直接读取且缺失时 fail-closed；
7. 权限与消息分离；
8. 本地与 GitHub 同一逻辑结构；
9. runtime/durable 分区；
10. validator 和冻结正负测试；
11. 跨载体由 Human 控制重新发布；
12. durable 不得依赖清理后消失的 runtime。

### 建议保留但可以继续讨论

1. coordinator 角色；
2. Human/current.yml；
3. 全局发现 index；
4. Markdown + YAML front matter 作为长文档默认格式；
5. sender index 是 YAML 单文件还是 JSONL/分片文件；
6. GitHub HEAD 变化时是否允许一次无冲突重试；
7. 模型是否必须通过 CLI 发布，还是允许手工按模板写文件后再 validate。

### 不建议加入 v1

1. 自动 watcher、轮询、通知；
2. 自动本地/GitHub同步；
3. 送达/已读/理解状态机；
4. actual recipient 耐久记录；
5. 普通消息自定义 digest；
6. 每条消息 timestamp、优先级、协议版本；
7. OS 级 ACL 不可变；
8. 全量历史或递归引用读取；
9. 每条消息更新 Human 报告；
10. 多种 wire encoding 同时成为 canonical。

---

## 17. 当前最值得 Human 继续判断的内部问题

1. 取消共享 index 后，是否还需要固定 coordinator，还是 coordinator 只在维护 manifest 和 Human/current 时存在；
2. sender index 是否放在 runtime，并随消息一起清理；
3. Human/current 由 coordinator 独占更新，还是由产生重大事件的 endpoint 更新；
4. GitHub HEAD 变化但写入路径完全不冲突时，是否允许 publisher 自动做一次重新基于新 HEAD 的提交；
5. 是否强制所有消息通过 CLI 发布，还是允许模型直接写文件再运行 validator；
6. `requested_action` 是否必须保留，还是可以进一步合并到 content；
7. 长文档默认 front matter 是否必要，或只要求少数 metadata 文件。

这些问题会影响实际操作成本、冲突概率和工具复杂度，适合作为下一批共同审阅主题。
