# DEV14-H — 确定性I/O底座上线前小规模加固（P0）

**2026-10-19 · 执行：Codex · 依赖：[PR #5](https://github.com/chris2gao/nba2k22-gm-engine/pull/5) / head `31f2682` · 仅增量修改，不重复A/B/C/D。**

## 判定与约束

DEV14 V1.1工程完成（119项此前报告的定向+复用测试通过），但正式游戏写入/玩家授权的实证尚未完成，当前GitHub状态PR#5 Open、未合并。**本单只做两个真实审查缺口，另外一项最低成本集成检查。** 一律不碰正式游戏、不采集、不自动合并任何PR、不启用GM V4。将修改放在现有PR #5分支或独立补丁分支，最终由用户决定合并。

### H1 — 三份SQLite库的存档/generation一致性

**审计事实**：在PR#5的`src/gm_state_io/workspace.py`，`Workspaces.check_databases(w)`目前只读取`league_state.sqlite.save_metadata`和`gm_control.sqlite.control_metadata`，未验证`player_pool.sqlite.save_metadata`。而`src/auto_pipeline_ingest.py`以`*.capture`暂存池并`os.replace`替换整个`player_pool.sqlite`。不能因初始化时写了generation就认定下一次采集后仍存在。

**Codex必须实现：**
1. 对每个ACTIVE/career/generation检查`league_state.sqlite`、`player_pool.sqlite`、`gm_control.sqlite`三个实存文件的save_id/save_instance_id/generation_id与源元数据匹配。检查值使用`binding(w)`的实际键集合；不以目录名相符代替证据。
2. 采集生成pool临时库后、整体替换前，用同一来源绑定写入/认证`save_metadata`；整库替换失败须阻断，避免旧pool/新league混代次。遵守既有`full_verified_v1`、M0同批哈希/静态只读双库。
3. 发现缺失/错误metadata时`POOL_SAVE_BINDING_MISMATCH`或兼容项目风格的明确失败码；没有静默自修复、没有从别档复制球员池。历史尚未纳管的旧存档维持已有明确`adopt`路径，不通过自动写标签掩盖来源错误。
4. 合成测试：A/B两个save均同名M02、同`player_id`，交换pool文件后所有stage/activate/新正式采集入口拒绝。随后同批正确pool正常运行。另测`os.replace`后metadata仍符合代次。
5. 校验生产M0历史旧批只读不改；不要进行真实游戏内存采集以验证本项。

### H2 — 真人授权与模型提供参数严格分开

**审计事实**：PR#5 `scripts/gm_state_io.py`的`--approve-game-writes`、`--player-approval-reference`、`--loaded-save-confirmation`是**由CLI调用者传入**；`src/gm_state_io/executor.py`中的`require_approval()`只校验字段不为空/摘要绑定/退出编辑页，不能独立证明玩家本人批准。自动模型如果能提供文件和这些参数，可能绕过治理规定。

**最小可行处理**（必须公开真实信任边界）：
1. 新增单独的**人工审批消费契约**：`PENDING_HUMAN_APPROVAL`、`HUMAN_APPROVED`、`MODEL_PROVIDED_CLAIM_ONLY`等不同状态。后者永远不得调用RW。
2. **不要把字符串`player_approval_reference`、文件名`approval.json`、`approved:true`视为真人授权**。建议提供仅真人操作的前台`review/approve`命令/工作流：显示存档、球队/球员、字段、前后值、动作数量、digest、原生属性保护与影响范围，由人确认后将完整批准绑定交给执行角色；GM/执行模型只读取结果且不可自行创建批准凭据。
3. 要实现真正不可伪造的授权，凭据签发权限必须与执行模型的OS/应用权限隔离（独立用户、受控GUI/签发服务或其他真实安全边界）；若执行模型具有与玩家完全相同的系统和文件权限，单纯JSON/HMAC密钥放同权限目录**不能宣称已提供密码学强制隔离**。在尚未完成权限隔离前，给状态`MANUAL_OPERATOR_TRUST_ONLY`并禁用无监督RW；玩家监督+明确确认仍可使用现有受限流程。
4. 继续保留完整`save_id+instance+generation+batch+decision/version+action_ids+digest`审批tuple，执行时动态前值CAS、游戏实际载档用户确认、退出编辑页声明及条件恢复。不能弱化现有保护。
5. 最少增加两条测试：模型仅提交可自构造JSON/CLI flags时不获得生产权限；有独立人工批准并保持同一源计划时可运行合成MemoryBackend。真签发缺独立权限时只交付`MANUAL_OPERATOR_TRUST_ONLY`和明确残余风险，不为追求形式完工虚称安全已完成。

### H3 — M3兼容的最小提前检查（不执行DEV13）

- 确认PR#5修改的`src/gm_data_access/query.py`、`scripts/gm_data_query.py`和当前PR#4里的M3`src/gm_data_access/analysis_inputs.py`、`src/gm_core/analysis_packet.py`接口无路径丢失。两个PR在`AGENTS.md`、开发基线等文件有重叠，不能“先合并谁都无所谓”。
- **推荐顺序**：先完成本单并由用户批准将PR#5合并main；然后让PR#4重置/合并来自新main的变更并跑现有M3 P1–P5定向回归，再由用户决定合并PR#4；DEV13新增工作放后续独立PR。
- 若Codex周额度不足：H1优先，其次H2明确拒绝模型伪审批/人工信任边界；H3只出兼容报告。不要拿额度跑全部119项或重做M3。

## 有界验收与交付

交付**一个小补丁或PR**：差异、A/B pool交换阻断、一次合成批准拒绝/通过、已有教练/M0最小回归、H2真实信任边界声明；不得改变游戏、发布新Observed、合并两PR或生成GM30队决策。

**成功条件**：DEV14的物理隔离与审批不会因轻量模型调度成为单点错误来源。