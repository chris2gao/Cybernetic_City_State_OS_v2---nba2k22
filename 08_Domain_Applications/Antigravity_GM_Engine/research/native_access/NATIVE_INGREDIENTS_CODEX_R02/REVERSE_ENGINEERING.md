# NATIVE-INGREDIENTS-CODEX-R02

本轮已解决 GM 链式对象的指针身份污染，并把 PlayerStat 的原生位域、Player 姓名边界和 Draft signed-round 变成可复算的研究解码器。它们仍未构成当前存档绑定或生产查询能力。

任务来源是 [Issue #3](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/3)。本轮从 master `407e2134bd2f595477099b2c6e3484c818059fd9` 建立隔离分支。Gemini 输入固定为 `5cef84fb21892266686bd5fd75a06901ea911d12`，上轮 Codex 输入固定为 `7d778aa3bd2f64145f997af0e44d9062c94fc55c`；来源、原始路径与字节哈希见 `source_manifest.json`。原件未覆写。Core 更新 `446ca66ad48831f5fcdb1af18f37d07619e048c4` 的任务封套/方法自由原则用于本轮执行，未合并或改写领域仓库的 core-owned 文件。

`static_capture.json` 来自磁盘 NBA2K22.exe，实测 SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`，83,688,840B，首选基址 `0x140000000`。下面地址均为 RVA。`static_evidence.py` 保存 22 个有界指令块、原始字节、哈希、资源与完整统计分派表，可对该磁盘镜像重放。`.pdata` 会分割函数，指令块不冒充完整调用图。没有打开当前游戏进程，未操作游戏 UI、存档或生产消费者。

## GM 链表与实体归属：P0 已解决

| 命题 | 原生证据 | 历史样本校验 |
|---|---|---|
| DeadCap `+8` 是拥有者 Team | `0x9CBA60`：`[rdx+8]=rcx; rax=[rcx+0xC88]; [rdx]=rax; [rcx+0xC88]=rdx` | 三条记录归属 Slot8 index `[4,4,9]`，不是 Slot1 Player |
| DeadCap `+0` 是从 Team 头向后遍历的 next | 插入函数把旧头放在 `+0`；`0x9D1570` 沿 `[rax]` 寻找/摘链，更新前节点或 Team 头 | record1 的 next 精确落在 record0，形成 `[1,0]` 的闭合样本链 |
| TradeException 采用同类结构 | `0x9CBC90`：`[rdx+8]=rcx; rax=[rcx+0xC90]; [rdx]=rax; [rcx+0xC90]=rdx`；`0x9D15E0` 沿 `+0` 摘链 | record1 next 精确指向 record2；`+8` Team indices `[2,3,3]` |
| TPE 消费者身份 | `0x12CC6E0` 的资源名 `Franchise_Team_DeleteTradeExceptionById`，沿 Team `+0xC90`、记录 `+0` 查找，比较记录 `+0x60` 并调用摘链函数 | 结构与 slot71 Getter 的对象族相符 |
| Manager 空闲链与 Team 对象链不同 | DeadCap allocate `0x9214F0`：manager 首 u16 为 free-head，record `+0x36` 为 next-free index；分配后写 `0xFFFF`。TPE allocate `0x9D6460` 对应 `+0x62`。release 把旧 free-head 写入该字段，再将当前 index 写回 manager | 历史审计没有保留这些尾部，不能宣称六条记录都已实测 active；更不能把 `0xFFFF` 称为所有记录恒定 sentinel |

DeadCap Getter 为 `0xF3C780`、TPE Getter 为 `0xF41540`。Gemini 包中的 TPE `0xF3C840` 不是这个 Getter，下一轮应纠正。DeadCap 分配调用者 `0x12CC990` 从已分配记录调用 `0x9CBA60`，把获取的 Team 交给上述插入路径。TPE 创建者的同一段代码也调用 `0x9CBC90`。证明覆盖这个 build 的结构与历史样本指针归属，未证明现在的 Team 表头、完整容器成员或真实存档交易规则。

历史 Pool 验证为 `(pointer-base) % stride == 0` 且 index 在 count 内；Team stride4696、DeadCap136、TPE112。它不能单独命名业务角色；原生写入、遍历和命名消费者补足角色证据。遇到跨池、未对齐、循环、跨 Team 或未保留节点，fixture decoder 失败，不把新地址解引用。`+0` 不是 prev/next 两个字段中的一半，`+8` 不是第二条反向链。`is_stretched` 只从三年金额推测，未找到原生 stretch flag，已降为 UNKNOWN；未重建 PlayerID。

## PlayerStat：原生分派与邻接位域

`0xEECDD0` 对 stat enum 先减1，限制 `0..250`，通过 251B 表 `0xEED194` 映射到 47 项 RVA 表 `0xEED0D8`，再跳往各 case。完整表与全部 case 原始字节已保存。`simple_cases` 从 load / shift / mask 指令解析出可直接实现的字段；比较型、组合型 case 保留原始证据，解码器拒绝未实现的复合 case。

| stat enum | RVA | 原生表达式 |
|---|---|---|
| 83，现有资料称 games played | `0xEECE01` | `u32(+8) & 0x7F` |
| 84 | `0xEECE5C` | `u32(+0xC) & 0x7F` |
| 86 | `0xEECE68` | `(u32(+0xC) >> 7) & 0x1FFF` |
| 3 | `0xEECE7B` | `u32(+0xC) >> 20` |
| 4 | `0xEECE2D` | `(u32(+8) >> 15) & 0x1FFF` |

`+8` 的 bit7、bits8..14 由另两个 case 单独提取，并非 games played 的一部分。12 条原始48B记录的 SHA 全部与 Gemini 审计吻合；stat83 复算为 `[16,58,57,79,81,16,57,64,74,70,44,2]`，而旧 u16 输出包含272、33850、34361等混合值。测试翻转所有邻位仍保持低7位，不能仅靠“结果不超过82”证明解包。原生字段可表达127；特殊赛制是否合理由 UI/赛季证据判断，不在 decoder 静默裁剪。stat83 的位段确定，当前 UI 的 GP 标签、赛季、球队/赛事拆分和存档加入仍待独立对照。

`0xF22220` 把 Player `+0xFC + selector*2` 读为 signed16 index，负值或 `>= Slot24.count` 返回 null；index0有效。`0xF22380` 循环24个常规入口；`0xF22270` 在特定 mode/selector 条件下改用 selector24，`0xF22420` 出现25入口循环。因此普通表是 `+0xFC..+0x12B`，特殊入口为 `+0x12C`。24/25是消费结构容量，不等于“24/25个赛季”。旧22入口读取不足，`0xFFFF` 空洞不代表后续无有效项；不得把过滤后的索引数直接叫职业赛季数。当前只能保留 Gemini 已给出的索引关系，不能重新补读遗漏的6B。

`+4` 的 season code 原样保留，未把 high byte 递减自动升级成公历年份或赛事类型。

## Player 姓名：40B + 40B，不是32B + 32B

TPE 创建消费者 `0x12E9D13..0x12E9D4C` 从 Player Getter `0xF3F580` 取得 Player；随后分别以源 `Player+0x28`、`Player+0`，长度参数 `0x14` 调用 `0xFBC080`，目的分别是 TPE `+0x38`、`+0x10`。该 helper 按 `word` 读源、以 `*2` 计算长度，说明两段均为20个 UTF16码元，即40B。原有 AG_NATIVE_01 与 AG_NATIVE_01D decoder 也使用 surname `[0:40]`、given `[40:80]`；字段角色沿用这一既有解释，完整当前姓名仍需 UI 绑定。

Gemini 以 UTF8 在首个零字节截断，得到 S/C；它读取64B而非完整80B，并且仅保留16B preview及64B的不可逆SHA。preview确实是 UTF16 的 Simmons/Curry。解码器要求完整80B，测试包含中文、代理对、满20码元、非法代理与缺失字段；不得凭真实NBA常识补上 Ben/Stephen。合成姓名只是边界测试，不是恢复出的游戏数据。

## DraftData：修复 signed5 与命名证据

`0x92A210` 的资源 `DraftData_GetByOriginalTeam`，在 `0x92A2EC` 比较记录 `+8`；`0x92A3A0` 资源 `DraftData_GetByPickTeamAndIndex` 在 `0x92A4D7` 比较记录 `+0`。这支持 pick Team / original Team 的结构角色。`shl 24; sar 27` 是32位定宽操作，等价：`bits=(meta>>3)&31; result=bits-32 if bits&16 else bits`。旧 Python 的无限精度表达式没有截断高位，结果错误。

6条样本的三个qword、token、metadata可恢复完整32B；重建 SHA 与独立审计中的32B SHA逐条一致，标记为 `RECONSTRUCTED_FIELDS_HASH_MATCH_FULL_AUDIT`，不是假装当时保存了 raw hex。六条 round 均为0；负例覆盖全部低字节及负16、负1、高位污染。两 Team 不同只输出 `references_differ`，不输出合法 traded-asset。bit17/token保持 raw，保护、交换、公历时间、备选 token 路径和 UI 法律条件继续 UNKNOWN。

## RecordData 与安全证据的边界

`0xF32E5F` 读取 `+0x2C >>21 &7` 并与过滤参数比较，支持“原生 type filter”这一窄命题。历史10条中100PTS/81PTS/36FGM都等于4，直接否定其是完整统计项目分类。`+0x30` token15584 的重复不足以证明全局PlayerID；`+0x32` raw Team word也没有当前存档身份绑定。未解决的完整分类、tail namespace、UI join作为下一轮静态探针，不能先塞进 Player DTO。

52条显式历史审计共5172B，分阶段数值重算吻合；这不证明 helper 无额外读取，也不证明执行器不能自授读取。历史实现由脚本任意 `register_allowed_range`，expected image SHA是常量，不能证明 PID1828 对应的真实进程文件已哈希。Save仍UNBOUND；其 Managed Run/Inspect 通过仅表示当时计划中的断言通过。

`offline_policy.py` 使用外部固定 manifest + 独立固定摘要、不可变许可和精确范围匹配；预算分相，敏感 deny 优先，绑定包含 PID/creation token/build/module/context，backend失败/短读预先计费并停止。20个测试中9个专门挑战该 mock：自登记、改范围、错 PID/复用PID/build/module/context、移借预算、敏感交叉、隐式 helper、短读及外部摘要不符。它只允许精确类型的 MockBackend，没有 Windows adapter。全权限执行者可改动整个程序或信任输入，因此这不是防恶意执行器的安全隔离，也没有替历史运行补作实机认证。

## 验证与后续

`test_research.py` 有11个 fixture/身份回归和9个 policy负例/正例；`verify_delivery.py` 将它们分两项，第三项从磁盘精确重放静态证据，第四项验证来源、范围与 MWU。Managed Run、Inspect 的原始日志及受检提交保存在任务 run。精确命令与限制见 `REPRODUCE.md`。

`corrected_claims.json` 分开 RAW / STATIC_CONFIRMED / LIVE_SAMPLED / UI_BOUND / SAVE_BOUND / PRODUCTION_READY。这里 LIVE_SAMPLED 只指历史 Gemini 样本，不是本轮新实机活动。`next_round_plan.json` 与 `GEMINI_NEXT_ROUND.md` 交付3个最高收益项目；新 live 项目均为提案，尚未发送、启动或获得新增读取权限。本次成果需要另一会话独立验收，任务分支 push 不等于 master 集成。
