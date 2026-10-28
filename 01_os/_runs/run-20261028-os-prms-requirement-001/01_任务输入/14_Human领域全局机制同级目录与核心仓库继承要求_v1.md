# Human新增要求：领域全局机制同级目录与主OS仓库继承分发

- 日期：2026-10-28。
- 所属任务：os-prms-global-persistent-role-memory-20261028-001；阶段01b。
- Human来源：本次对话的明确自然语言输入（无独立签名/外部消息ID，不伪造）。
- 性质：新需求与仓库关系核查指令，不是Q52选项裁决、不确认完整A、不授权跨仓库开发、master修改或实际分发。

## Human原始表述

> 特色领域机制需要独立的全局目录，最好适合08文件同级的目录，可以建立一个。另外就是我们这次开发的内容，是要更新到主os仓库，并从它扩展到其他的os系统的仓库的，你可以查看一下，我们这个仓库，就是在原os系统开发完成的仓库生成的仓库，有github关联的。

## 本轮确认的需求意图

1. 每个OS领域仓库具有独立于08应用源/业务产物的**领域级全局机制目录**，适合在仓库根下与08同级；该目录属于本领域，不把2K材料复制到数学/英语等领域。
2. 通用PRMS机制、启动加载协议、Registry等最终以**主OS核心仓库**为正式权威；经过既定规划/实施/审批流程后向各个领域仓库受控继承，而不是2K仓库独立维护永久分叉版本。
3. 保留现有Q35=C/Q36=B：阶段03设计B经Human确认后直接升级**OS核心规划规范**；运行时工程另需后续工作流，不得把本次谈话当跨仓库写入许可。
4. 目录建议为 \`09_Domain_Global_Mechanisms/\`；确切名称与物理结构先写需求候选，**本阶段不实际创建根级目录**，因当前Run allowed_changed_paths仅限其自身且禁止工程变更。
5. 既有Q52“全局加载深度”仍待Human选择，本轮没有暗中选A/B/C。

## GitHub证据快照（供复核，不将SHA假定为永久最新）

- Core正式仓库：\`chris2gao/Cybernetic_City_State_OS_v2---core\`，master \`446ca66ad48831f5fcdb1af18f37d07619e048c4\`。
- NBA2K22领域仓库：\`chris2gao/Cybernetic_City_State_OS_v2---nba2k22\`，master \`7742568ac677b3c16079887463f05e81cb1191ed\`。
- 数学领域仓库：\`chris2gao/Cybernetic_City_State_OS_v2---maths2.0\`，master \`c877e4e3b08bd1f2edacb725bb5f1f04a57a3277\`。
- 三仓均存在祖先提交 \`3ae48d2183a6e77d63a43783c7e1999edc01711e\`；GitHub compare以此为base对各自master显示ahead、behind=0，merge-base为该提交。
- NBA2K22/Core的\`CORE_MANIFEST.yml\`明确 \`core_repository: git@github.com:chris2gao/Cybernetic_City_State_OS_v2---core.git\`、core_owned_paths含01_os机制目录、domain_owned_paths含08_Domain_Applications和01_os/07_content。目前尚无09目录所有权声明。
- NBA2K22 \`08_Domain_Applications/domain.yml\` 记录 \`upstream_remote: core\`、\`publication_remote: origin\`、\`update_policy: Human_requested_on_demand_three_way_merge\`、\`automatic_updates_enabled: false\`。
- Core仓库 \`new-domain.ps1\` 以clone Core建立领域仓库，重命名原origin为core，添加领域origin并独立push；GitHub API \`fork: false\`，与Git祖先共享不是GitHub平台Fork语义。
- Core所有权规范说明domain不得自行改写core-owned canonical；真正升级应从core仓库进行验证与正式发布，再按每领域明确请求合并，不能将领域PRMS规划分支整树反向merge进Core。
- 源文件准确路径：\`CORE_MANIFEST.yml\`、\`new-domain.ps1\`、\`08_Domain_Applications/domain.yml\`、\`01_os/README.md\`、\`01_os/05_registry/repository_publisher_authority_v1.yml\`。

## 待定而未越权的边界

- 目录名 \`09_Domain_Global_Mechanisms/\` 为可审查建议，尚未进入正式A完整版本。
- Core \`CORE_MANIFEST.yml\`、\`new-domain.ps1\`、通用Boot/Registry/Loader需要在后续**Core授权范围**中修改，本次不修改。
- 已完成任务经验若要成为G1/G2正式机制，必须先提炼候选、证据评审、适用性/权限检查、Human按受保护规则确认并正式发布，不可“任务完成直接越权写master”。
- “全局加载”全文或摘要比例Q52、Human选择记忆加载的每窗口/复用粒度后续继续协同讨论。
