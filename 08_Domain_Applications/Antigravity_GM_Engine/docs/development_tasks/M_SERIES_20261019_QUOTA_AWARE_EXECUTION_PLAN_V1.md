# M系列开发调度 V2 — 两个Codex窗口接力，按额度独立提交

**2026-10-19 最新窗口划分权威文档**：[DEV18](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)。用户先前反馈Codex周额度约9%、5小时约49%仅为当时状态，不由百分比推断剩余开发工时。

## 真实当前状态

- [PR#5 DEV14-A/B/C/D](https://github.com/chris2gao/nba2k22-gm-engine/pull/5)：**独立底层Codex窗口①**已提交；仍Open未合并，当前报告119项合成/静态测试通过，正式新字段生产采集与玩家批准游戏写入未完成。
- [PR#4 M3A/M3B](https://github.com/chris2gao/nba2k22-gm-engine/pull/4)：**M系列专属Codex窗口②**已提交；仍Draft/Open未合并，既有M3 P1–P5保持。
- 详细主线见[DEV17 V1.1](DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)，新GM[个人防守与球队同名书政策](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)。

## 交接顺序和独立窗口所有权

| 顺序 | 窗口 | 本次明确负责的交付 |
|---|---|---|
| **① P0** | **DEV14底层Codex①（PR#5）** | [DEV14-H](DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)三库身份/真人审批，少量定向测试 |
| **② P0** | **仍是DEV14窗口①** | [DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md) 全部球员Potential入库后自动置1、原生选秀注入源保护；Intangibles单字段受控写 |
| **③ P0** | **仍是DEV14窗口①** | 核实GM已知原生字段/团队BookID技术性恢复绑定受控动作，提交**`docs/development_reviews/DEV14_TO_M3_HANDOFF.md`**及PR#5当前commit、字段契约 |
| **④ 人工闸门** | 玩家 | 审核独立底层PR#5及交接，是否批准合并main；**不自动合并** |
| **⑤ P1** | **M系列Codex②（PR#4）** | 接收已完成底层，不再建设采集/SQLite/codec；将已批准合入main的DEV14整合到M3分支，冲突合并+P1–P5回归，开发DEV13/DEV17 M3-T决策与本队书归位 |
| **⑥ 人工闸门** | 玩家 | 审核M3 PR和是否实际启动GM V4/正式数据采集/游戏修改 |
| **⑦ 后续扩展** | Antigravity | 51未知倾向、Play CRC篮球动作解释、位置训练模板、疲劳；**不阻塞Codex主线** |

**新档战术书默认**：各队都使用自己同名的手册容器；休赛期换帅后把新教练当前`PlaybookID`恢复该队同名书，按新教练与球员改该队槽位。不研究克隆/分配30队书，也不以共享冲突假想测试作为M3开发门禁。真正Native ID查不到时局部报BLOCKED即可。完整休赛期员工签约另立任务。

## 执行额度规则

- **在独立窗口①只发送①→③的指令**：额度有限每次完成一块commit后停止并给出已做/没做/测试；窗口①完成后将PR#5最新SHA和交接文档给用户。
- **用户再把交接交给独立窗口②**：窗口②处理④授权之后的代码整合及⑤M3逻辑。千万不要把所有开发任务一起发给两个窗口，使其修改同一个`src/gm_data_access/query.py`、SQLite schema或游戏采集管道。
- 如果PR#5尚未合并，窗口②可做不依赖新接口的M3策略草案或纯离线测试，但不得假装PR#5已经在其分支，也不能自行复制DEV14底层到PR#4造成两套执行器。
- 不重跑DEV14全部119项、M3全部工程初始化，也不强迫AG一项项实测同族字段。阶段测试覆盖当批改动即可。
- **提交GitHub代码 ≠ 玩家同意游戏数据写入；模型没有自批权限**。整个交接中依然使用save/instance/generation/source batch/审批digest/回读/条件恢复。

## 直接可发两个窗口的短指令

**给DEV14窗口①**：“请按`docs/development_tasks/DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md`第二区段完成PR#5底层收尾及`DEV14_TO_M3_HANDOFF.md`。只负责安全IO/脱敏/Intangibles/有限BookID技术动作接口，不开发M3六维GM模型、不合并PR或写游戏。”

**给M系列窗口②（等交接后）**：“请读取`DEV14_TO_M3_HANDOFF.md`和`DEV17_CODEX_FIRST...`、最新PR#5代码，按已授权的Git合入次序整合DEV14到自己的PR#4，再开发M3-T决策/换帅同名Book归位，不复制底层或等AG扩展。不自动合并PR或更改游戏。”
