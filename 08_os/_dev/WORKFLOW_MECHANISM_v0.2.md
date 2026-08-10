# 工作流机制 v0.2

状态：活动。取代 v0.1。

## 阶段连接

每阶段输出版本化耐久产物；下游只消费声明的输入。A、证据、B、测试和 handoff 是显式
依赖节点，内容哈希变化使旧入口 stale。checkpoint 只恢复，不代替 stale 判定。

## 上下文机制

全局 canonical 位于 `03_mechanisms/context_management/`，由 boot 清单和 execution
loader 加载。角色有效上下文、耐久事实与审计记录分平面。共享 OS 的开发/验证运行位于
core-owned `_runs/`，不注册；机制、boot、loader、活动开发规范注册。领域业务与领域
workflow 流量位于 domain-owned
`08_os/07_content/_runs/`，同样不注册。

`workspace_partition` 仅组织工作目录和默认加载面；clone/worktree 绝不是
`enforced_access_boundary`。私有 runtime 位于仓库外，或仅位于被忽略的
`_runs/<run-id>/_runtime/`。

D2 已决：沿用现有后端执行角色并收窄派单，活动裁决只引用
`决定_谁执行_v0.2.md`。

跨角色发布使用精确 allowlist，禁止宽泛暂存/打包。正式 handoff 进入 run 的公开区；
角色 private/scratch 完成后删除，删除前先提取耐久事实和失败记录。

## 角色与循环

规划、执行、审核等角色通过结构化 handoff 协作。执行与验证循环以冻结测试为边界；
审核同时核对实现对 B 与证据，避免只过拟合测试字面。
