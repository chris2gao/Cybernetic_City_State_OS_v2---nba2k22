# check-jsonschema 在城邦 OS 中的职责与收益

## Human 结论

`check-jsonschema` 0.37.4 已达到 `verified_on_demand`：本机安装链可解引用，
本轮校准 schema、合法 YAML/JSON、核心负例、五次重复性、schema 引用闭包和
exact-version fail-closed 路径全部通过。它可以作为一个任务显式调用的本地 CLI，
但不能进入默认 boot，不能暴露成 MCP，也不能被写成“已经覆盖整个 OS”。

## 它具体负责什么

当某个 OS 对象已经拥有真正的 JSON Schema 时，它检查本地 YAML/JSON 是否符合
已编码结构：

- 必填字段是否存在；
- string、boolean、array、object 等类型是否正确；
- enum、const、pattern 是否满足；
- 不允许的额外字段是否出现；
- 嵌套对象和数组的形状是否正确；
- schema 自身能否通过 metaschema。

适用对象可以是未来机器化的 run manifest、typed handoff、registry 扩展或阶段
输入契约。现有 `需求建模schema_v1.md`、`B_schema_v1.md` 和
`测试schema_v1.md` 是 Markdown 规范，不能直接交给 CLI；必须先由单独任务编码并
审查机器契约。

## 它防止的真实错误

run-012 实际阻断了缺必填字段、错误 boolean、非法状态值、多余字段、嵌套数组
类型错误、损坏 schema、非法 schema keyword、缺失 schema/instance 和损坏 YAML。
同一合法 YAML 连续五次的退出码与诊断完全一致。

这比让模型判断“看起来差不多”更可靠，因为失败规则、字段位置和退出码由同一份
版本化契约决定。模型不会因措辞流畅而放过一个缺失字段。

## 它不负责什么

通过只等于 well-formed，不等于 correct。工具不证明：

- claim 或 evidence 为真；
- evidence 足够、独立或新鲜；
- 跨文件 ID、路径或 Git ref 存在；
- A、B、测试之间语义一致；
- 业务方案合理、风险可接受；
- Human 已授权下游动作。

自建 validator 继续负责跨文件、文件系统、Git、集合和项目特有约束；模型/Human
继续负责语义、来源、取舍与授权。

## 为什么是按需 CLI

它每次只需启动一个短命 CLI。MCP 会增加 server 生命周期、工具 schema 暴露和
上下文面，而这里没有服务状态、交互会话或远程资源需要维持。默认 boot 也不应
携带工具说明或 schema。

canonical wrapper 通过 PATH 或 caller 显式 executable 解析工具，先验证本地输入，
再以独立 preflight 将 schema 收紧为严格 JSON、fragment-only 引用且无 HTTP(S)
identifier，随后运行时探测并精确匹配 `check-jsonschema 0.37.4`。两个门都通过后
才启动 validation，并保留底层退出码。工具、Python、preflight、版本、schema 或
instance 不可用时明确失败，不回退模型判断，不修改全局状态。

## 实测收益和成本

### 错误检出

- 43/43 matrix cases 通过，其中原始矩阵 27/27、边界修复 14/14、测量 2/2；
- 五次重复运行完全一致；
- 中文和空格路径通过；
- PATH 移除工具目录时 wrapper 以 exit 69 fail closed；
- URL-shaped schema 参数被当作非本地文件拒绝；
- 外部 `$ref` / `$dynamicRef` / `$recursiveRef`、HTTP(S) identifier、非 JSON
  schema 在 validation 前以 exit 65 拒绝；
- 版本漂移、损坏的 version 输出和 probe 失败以 exit 78 拒绝；
- 所有边界拒绝案例的 validation sentinel 均未出现。

原始 CLI 在 instance 缺失时输出 3033 UTF-8 字节 traceback；wrapper 在启动工具
前以 exit 66 和 205 字节诊断停止。这既减少噪声，也把“输入不存在”和“schema
校验失败”分成稳定故障类别。

### 时间和机器资源

- exact-version probe：462.805 ms；
- schema reference preflight：191.880 ms；
- 直接 CLI validation：556.268 ms；
- `pwsh` wrapper 总耗时：1588.680 ms；
- 五次后续 CLI：平均 483.410 ms，范围 443.970–508.052 ms；
- Windows PowerShell 5.1 wrapper 成功路径：1304.700 ms；
- pipx venv：686 个文件、12,360,162 字节；
- 测试结束后匹配的常驻工具/venv Python 进程：0。

首个测量进程之前已经执行安装探测，因此只能称“无常驻进程的新 process start”，
不能声称 OS 文件缓存完全冷。launched process/进程树峰值内存没有得到可靠值，
记为 `not_observable`。

### token/context

平台没有提供本轮真实 token telemetry：

```yaml
installed_idle:
  observed_exact_tokens: not_observable
  architectural_result: no_tool_schema_or_document_injected
  expected_incremental_tokens: 0
  expected_incremental_tokens_basis: architecture_not_billing_telemetry
registered_on_demand:
  observed_exact_tokens: not_observable
  default_boot_reference: false
  mcp_exposed: false
invoked:
  observed_exact_tokens: not_observable
diagnostic_consumed_by_model:
  observed_exact_tokens: not_observable
```

校准 schema 加缺字段实例共 2015 个 ASCII-dominant 字符/字节；建议给模型的短诊断
为 66 字符/字节，减少 1949 字符，约 96.7%。透明的英文规划代理为 504 对 17
token，标签是 `proxy_not_billing_tokens`，不是计费或平台实测值，也不能外推中文。

## 网络与残余风险

没有进行网络抓包，因此网络结论只能写
`not_observable_no_packet_capture`，不能写“已证明零连接”。上游包和直接 CLI
仍自带 remote-schema 能力；canonical v1 wrapper 不依赖“顶层路径是本地文件”
这一弱条件，而是在启动 validation 前递归检查 schema，机械拒绝所有非 fragment
引用及 HTTP(S) `$id`/legacy `id`。标准 `$schema` URI 与 schema 内 fragment
继续允许。需要本地多文件模块化 schema 时，必须由后续任务设计新的受控解析面，
不能绕过当前门禁。

残余风险：

- 错误或过宽 schema 会产生确定性的错误信心；
- 某些 `format` 行为依赖 validator 配置和依赖；
- 工具升级可能改变诊断、draft 或依赖；
- 直接绕过 wrapper 会重新暴露长 traceback、remote URI 和不稳定输入错误；
- 当前保守 preflight 不支持本地多文件 schema；
- registry 状态只绑定 0.37.4、Python 3.14.6 与本轮 fixture，不自动涵盖未来 schema。

## Human 生命周期

Human 可在单独授权的维护任务中使用 `py -m pipx upgrade check-jsonschema` 或
`py -m pipx uninstall check-jsonschema`。任何版本、Python runtime、wrapper 或
机器契约变化后，必须重跑 metaschema、合法 YAML/JSON、全部核心负例、外部引用
闭包、exact-version 边界、validation sentinel、五次重复、中文空格路径和工具
不可用测试，再更新 registry。

## 何时阻止下游

以下任一情况必须停止当前对象向下游流转：

- wrapper 找不到 executable、schema 或 instance；
- schema preflight 不可用或拒绝输入；
- version probe 失败、输出不可解析或不是精确的 0.37.4；
- schema 未通过 metaschema；
- instance 解析失败；
- validation 返回非零；
- 任务需要跨文件或语义判断，却试图把结构 PASS 当作充分证据；
- 工具版本与 registry 不一致且未复验。
