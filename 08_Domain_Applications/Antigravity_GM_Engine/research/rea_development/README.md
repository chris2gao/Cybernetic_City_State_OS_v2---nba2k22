# REA 开发探索脚本

状态：2026-10-27 阶段性发布，Human 已暂停探索。先读 [使用手册](../../docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md) 与 RUN `08_结论/PLANNING_HANDOFF.md`。这些是有界实验工具，不是正式游戏批量写入器。

| 脚本 | 用途和输入 | 副作用 |
| --- | --- | --- |
| discover_native_seams.py | 固定EXE、PE注册模板和所选字符串LEA引用；需现成capstone | 读EXE，写新证据 |
| build_metadata_probe.py | native-seams.json → metadata/growth/presentation JS；需同构建EXE | 离线生成脚本；不附加游戏 |
| invoke_game_probe.ps1 | 审阅后JS、输出目录、唯一tag | 必须管理员；REA/Frida附加游戏；仅配套只读脚本获本轮验证 |
| decode_metadata.py | 观察Evidence、literal CRC map →字段候选 | 离线解析；字段size不可当通用复制跨度 |
| analyze_seam_functions.py | 固定EXE、已知xref和pdata→Capstone候选 | 不执行游戏，不等价完整函数或CFG |
| inventory_presentation.py | 固定EXE与root/Mods顶层IFF文件名 | 只给候选家族，不能统计关闭功能 |
| inventory_rea_capabilities.mjs | 当前全局REA→工具名及精选输入契约 | 短暂启动MCP，不启动Ghidra |
| run_bulk_fixture.py | `--out <fresh-directory>` | 启动自建Python进程，REA真实写入4096条再恢复；从不选游戏PID |
| run_call_trace_fixture.py | `--out <fresh-directory>` | 自建进程native-ABI回调上安装有界hook，结束清理；不对游戏hook |
| inspect_extracted_scorebug.py | REA archive bundle→解包目录和资源事实 | 只读REA已解包副本；不复制资产进仓库 |
| parse_scorebug_bindings.py | 前者findings→VCUI前缀/SCNE候选结构 | 只解析，保留RAW状态值；不是可逆格式编码器 |
| make_scorebug_candidate.py | 固定本机scorebug→全新研究副本 | 写游戏目录外IFF，单成员单参数变化；不部署 |
| compare_scorebug_candidates.mjs | 原模组与研究副本 | REA ZIP inventory/compare/export，最后close；无游戏运行副作用 |
| verify_delivery.py | `--integrity`或`--evidence` | 只验证本提交和已保存证据，不重启游戏实验 |

验证环境：Windows、Python3.14（已装capstone）、系统Node24.22.1、全局rea-agents6.8.0及其MCP SDK。JS SDK入口和管理员入口使用本机已验证的安装位置；其他机器先通过非敏感路径检查调整位置，不读取凭据或整个环境。原始schema快照随RUN证据提供，工具版本变化需重新核对。

执行示例（从仓库根，实验需当前任务明确覆盖）：

```text
python -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_development/run_bulk_fixture.py --out <new-fixture-directory>
node 08_Domain_Applications/Antigravity_GM_Engine/research/rea_development/inventory_rea_capabilities.mjs <new-contracts.json>
```

注意：游戏只读脚本入口的关键词检查不构成沙箱。运行任意JS前仍需审阅实际脚本、目标、读区与预算。证据中包括Frida注入、元数据定义、fixture效果、人工UI观察和离线推断，等级不可合并成一个PASS。
