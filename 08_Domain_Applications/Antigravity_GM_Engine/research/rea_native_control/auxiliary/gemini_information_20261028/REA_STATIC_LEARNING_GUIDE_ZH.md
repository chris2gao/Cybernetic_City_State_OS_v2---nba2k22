# 先学会这套REA辅助取证方法

## 目标和职责

NBA2K22原生引擎是游戏事实权威。GM/Coach/Player决定对象和值；工程层提供准确的信息/能力和执行机制。本包只做静态信息来源协助，既不做业务决策，也不接管数据库、执行器或最终验收。

合理的Flash首包是：抄准类型/数组/枚举表，核对很短的完整函数和参数来源，给出独立字节反例，标清不确定。暂不承担复杂PER/球员评价算法、深层间接调用、多线程别名、跨存档身份、实机权限、完整Reader或主架构。不要用模型名称推断自己能完成这些任务。

## 证据链

按顺序保留：固定EXE SHA → 实际工具/版本或provider → 完整原始输出 → 选择范围/原始字节 → 对象/字段/参数绑定 → 反例/限制 → 候选结论。不要从字符串名字直接跳到功能已经可用。

主工程曾成功使用REA的有界静态与Frida能力，但**历史实机成功不授权本包调用或附加**。整游戏Ghidra重试路线已停止。当前可用工具、provider和会话必须从实际客户端查询，不能复制Codex的命名空间或假设skill安装等于MCP已连接。

## REA最小使用流程

1. 读取本包AGENTS、SCOPE和INPUT_MANIFEST，校验目标SHA。记录实际客户端/模型显示；无法核实时写UNKNOWN，禁用子代理。
2. 检查实际REA工具清单和当前工具schema。只有已存在、同目标且可用的静态会话才可复用；不要为本包打开整EXE触发新的深provider导入。
3. 选一个明确地址/类型。可使用实际可用的`procedure_info`、`read_bytes`、`analyze_function`、`trace_native_values`、`inspect_analysis_view`等静态能力。**这些是操作类别示例，具体工具名与参数以客户端真实schema为准。** 工具不存在就记录缺口，不编造调用。
4. 每个代码窗口通常不超过256字节，单次选定函数不超过1024字节、最多2个；只跟一层明确直接引用。静态数组/字面bank每次最多4096字节、最多128行。需要新范围时先写明当前证据推导出的地址和理由，仍只限本包对象。
5. 保留完整REA返回及Evidence引用；有retained bundle就导出到本独立目录，没有则保留完整inline输出和限制。摘要不能替代原始Evidence。实际provider不可用时，允许用输入中的`pe_local.py`和局部恢复脚本，输出必须标`PINNED_PE_CAPSTONE_NOT_REA_PROVIDER`。
6. 保存真实的`tool_calls.jsonl`及输出文件、argv/选择器、退出码或provider状态；捕获失败也保留。不要捏造证据ID、耗时、读数或“测试通过”。

不要在连接问题上重装整个环境。连接、provider、CLI PATH和宿主超时是不同问题。按输入中的REA skill/recovery快照查对应条目；需要改全局设置/安装/启动/权限时停止该路线并报告，继续其他静态包。

## 已有离线工具

打包路径保留`inputs/research/rea_native_control/tools/`与`inputs/research/rea_native_action/pe_local.py`相对结构；因此可从前者目录运行现成脚本，输出使用`work/<new-file>.json`的绝对路径。

```powershell
python -X utf8 -B recover_entry_windows.py --rva <evidence-derived-rva> --bytes 128 --out <absolute-new-work-json>
python -X utf8 -B recover_functions.py --rva <confirmed-function-entry> --maximum-function-bytes 1024 --out <absolute-new-work-json>
python -X utf8 -B recover_enum_registration.py --entry <confirmed-tail-thunk-entry> --out <absolute-new-work-json>
```

尖括号是待你从证据确认的值，不能照抄成命令。本包没有提供已确认enum入口；已有的LEA站点不能直接当函数入口。`NO_UNWIND`不等于不存在，padding猜测不等于完整CFG；短tail thunk须完整指令形状、表头/CRC/数量及入口引用交叉核对。工具不会替你判定所有业务语义。

## 写结论前的反问

- 这是注册字段、存储值、可调用Getter、当前实机值还是UI含义？只写证据达到的一层。
- 该数字是RVA、绝对VA、字节偏移、位宽、元素数还是索引？有没有混用？
- 数组轴来自维度/消费者还是我按名称猜的？MADE/ATTEMPTED的值是否真的由enum行证明？
- 有没有边界值、错误CRC、错误stride、越界index、缺失字段或不一致样本这样的负例？未运行负例必须写NOT_RUN。
- 统计来源属于哪一对象和时间窗口？不知道就UNKNOWN；不能从邻近布局、同名或同数值推断身份/赛季。

当前投篮图的14×2布局是已知起点，枚举数值、实体索引与时间语义是待证事项。STAT_REPORT_PER等文字不是公式，Simulator的Pace常量不是比赛实际节奏，Role UsageScore不能直接视为USG%。Overall仍在已有Human deferred清单内。
