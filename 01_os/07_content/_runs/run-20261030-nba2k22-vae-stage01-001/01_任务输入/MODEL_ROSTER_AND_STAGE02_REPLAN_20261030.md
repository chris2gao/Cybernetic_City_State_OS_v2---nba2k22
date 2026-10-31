# VAE 当前执行模型编排修正（2026-10-30）

## Human 原始资源边界
Human明确：**“vae，目前只有gpt和gemini flash 3.8（拥有本地执行能力）参与，codex目前没有额度了，参与不了。”**

此条只适用于**当前与未来 VAE 新任务**，不追补旧任务中的模型身份，也不推断Codex何时恢复额度。

## 当前任务路由
| 岗位/执行面 | 可用成员 | 主责/使用条件 |
|---|---|---|
| `decision_architecture` VAE规划 | 本GPT规划窗口 | 规划、拆单、派单、结果接收、审核路由，不替开发者执行 |
| `execution` 文档/方案/结构化合同/分析 | 从公共基线新Fork的GPT开发窗口 | 正式开发提交 Run 与 completion pointer |
| `independent_review` | 新的、隔离的GPT审核窗口 | 独立核验代码与证据，不继承开发者私有判断；同模型家族时如实记录 |
| `auxiliary_mechanical`或`execution` 本地取证/工具执行 | Gemini Flash 3.8（Human所称标签） | 根据每个具体任务的权限/技术成熟度与本地环境执行；身份凭据如实标注 |
| Codex | 当前不可用 | 不派新VAE任务，不让其成为Stage02或工程开发的当前前置Owner |

Gemini可本地执行不等于已经有权限启停游戏、提权、注入、修改存档、变更运行配置或调用未证实Native接口；必须在新任务合同中按动作限定授权。

## 已派Codex任务的处置
- 原任务 `NBA2K22-VAE-STAGE02-G01-G03-READONLY-EVIDENCE-20261030-001`，派单 `ac48662f1c96e60eab04a077ed93cf0ec2694c4b`。
- 因资源不可用、尚未接收执行证据，暂缓为 `deferred`；状态提交 `90f42546b2e6d17bd52f28f3e9b26342888a4bcc`，保留原task packet与owner为历史指派。
- **不得由Gemini继续使用这一Codex Task ID或Run**。新任务要另建独立Run，明确源引/模型记录/验收与安全边界。

## Stage02规划次序（候选，非执行派单）
1. GPT先根据已批准A及独立审核发现，压缩并核对G01–G03真实取证需求、证据分层、F02比较上下文必填与所需先决条件；仅产出有限合同。
2. Gemini在新独立任务中调查本地已存在的Reader、游戏配置信息及安全只读路径；根据授权可做现场读回，输出带build/save/mode/side/controller/normalize/时间的证据或逐项UNKNOWN。
3. GPT独立审核窗口核实Gemini的关键来源、实际运行读回可复现性及权限边界；Human只就受保护动作或负载关键新语义决定作确认。
4. 对有界实验机器合同完成F02/F03/F07修订与证据复核后，再考虑游戏变动、竞技比较和Stage03结果B，不能直接把首批研究当正式阶段完成。

## 当前治理状态
Human确认精确VAE A-v1仍有效。Core完整七阶段Runner未取得PASS，旧收尾记录为BLOCKED，不应借更换执行模型重新制造假的独立Stage01完成门。Stage02可先做满足现有起始条件的有界准备与安全只读研究，正式Run验收依Core原规则。

## 上下文规则
只保留Human资源决定、模型路由、任务状态、证据指针、未解问题与下一派单。PRMS`SAVE_TASK_CONTEXT`及Communication v2正式送达目前仍未执行，不冒充已完成。
