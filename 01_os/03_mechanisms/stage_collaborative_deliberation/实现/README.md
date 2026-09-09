# 阶段协同推演闭环 · 实现契约

本目录保存机制的机器契约、验证器与回归 fixture。当前 exact-ref 消费面随经批准的正文变更同步更新；历史 pointer 不被改写。当前运行状态仍由 `../激活状态_v1.yml` 以 append-only 方式声明为 `active_dormant`，本次任务不修改或再次激活它。

## 组成

- `结果对象契约_v1.yml`：8 个家族、45 个对象类型、47 个结果名；
- `状态转换与不变量契约_v1.yml`：10 个状态维度、16 条不变量；
- `路由与失败契约_v1.yml`：5 个 router、26 个失败码；
- `加载与receipt契约_v1.yml`：dormant/full/incremental receipt 与原子发布边界；
- `verify_no_canonical_live_state.py`：拒绝 canonical live instance state；
- `verify_stage_collaborative_deliberation.py`：当前任务作用域 instance 入口及显式历史 helper；
- `verify_stage_collaborative_deliberation_v2.py`：当前 active-dormant static validator，现场重算 exact-ref 图并复用基础入口；
- `test_task_scope_readiness.py` 与 `fixtures/instance/task_scope_cases_v1.yml`：真实临时 Git 仓库中的普通动作、受保护动作、源码错误、类型、作用域和历史兼容反例；原有合法 YAML merge fixture 保持不变。

当前机制可加载但默认 dormant。进入 full 或 incremental 仍需命中 profile trigger 并满足当前任务 gate；全局激活不替代其他授权。

## 当前任务入口

```text
python verify_stage_collaborative_deliberation_v2.py instance INSTANCE.json --repo-root REPOSITORY_ROOT --candidate FULL_COMMIT_SHA --json-output
```

`instance` 必须使用外部实例中的 `task_scope`，其封闭字段和动作结构见 `../阶段profile契约_v1.yml` 的 `task_scope_execution_contract`。任务包须为规范 `task_packet` 包装；任务包、profile、publisher policy、动作确认和决定依据从候选的普通 Git blob 读取，不用 mutable worktree 同名文件。候选/基线必须是真实完整 commit，全部候选 diff 受任务 allowlist 约束，动作 paths 和阶段再作精确绑定。源码缺失、类型错误、读取失败均非通过。

普通动作是任务包中预先声明的 `ordinary_task_work`，目标必须为该任务的非 master 分支；不是外部输入写一个 `ordinary: true` 就可放行。完整 common model、当前阶段必需字段、未知项处置与 typed receipt 在 dormant/full/incremental 中都保留。既定任务作用域已经覆盖的动作不增加逐阶段确认或固定提问轮数。

承重决定使用明确 `decision_id`：已委托决定绑定精确任务包、选中动作及其 `covered_decision_ids`；新决定绑定候选中的明确记录及完整任务/动作作用域。裸 `ref`、actor 标签或推断不是依据。受保护动作仍须匹配 publisher policy 和明确确认；`expected_target_head` 是声明值，不是假装读过实时远端。core 历史改写仍被禁止。

## 完成证据与边界

提出 progression 时，`current_exact_output_version` 和 `completion.bound_output_version` 均须等于候选，`actual_result` 须为非空字符串。`completion.verification_result` 是 `{commit, path, blob_sha}`，指向独立 Git 证据提交中的普通 YAML blob；正文必须精确为 `schema_version: stage_verification_result.v1`、当前 `candidate/task_id/stage_id` 和 `status: verified`。该证据提交可晚于候选，外部 instance 再引用它，因此不要求候选在自己的树中写入自身 SHA。若未提出 progression，提供了 verification_result 也必须有效。

可选 completion_pointer 必须 append-only 并绑定当前候选；supersedes 与 supersedes_record_ref 若出现须成对为非空字符串。这里不自动发布 pointer，也不从这些字符串推断已投递、已验收。

这个校验器证明声明的结构、范围和 Git 记录绑定，不认证 Human 身份、不复跑记录声称的测试，也不约束任意后续 shell。实际命令和完整日志使用 managed verification，最终独立验收另行进行；本入口不豁免审核、master gate 或 runtime gate。

## 显式历史输入

历史 `validate_instance`、authority/challenge helper API 保持可读，CLI 必须显式选择 `legacy_instance`；它仍要求旧记录已经具备其引用的历史依据。新 `instance` 缺字段不会退回旧路径，也不为普通任务生成 nonce/旧式授权。`static`、`material_event`、`review_execution` 仍是各自独立模式，不把其结果冒充当前 instance 通过。
