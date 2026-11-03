# 首批功能验证准备记录

任务接手基线0008af1d7ca1c67a6d5f747b35c57062d1bde7d6。远端master当次核实为7742568ac677b3c16079887463f05e81cb1191ed。本轮初始状态为纯准备，没有访问游戏进程、附加、内存读取、Hook或原生调用。

离线核实：PC22 EXE SHA256仍为1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5；Node v24.22.1及REA CLI存在。当前命令进程不是管理员；此记录不推断当前游戏PID、存档、页面或权限状态。

已向Human一次合并询问：当前模式/页面与可恢复测试存档、指定球队与新教练字段目标值、球探队伍及候选UID（不知道UID可先读候选）。收到之前不自行选择业务输入。初步只读请求仅准备当前公开候选前20项身份，没有分派、消耗、选秀、交易或日期推进。

## 独立读回补齐

- READ_COACH_CURRENT补全已静态绑定的十个known_current_settings，保留互相关联作为只读身份假设，不增加STAFF池/对齐硬阻断。
- SCOUT_READ_TRIP_BUDGET加入最多3个Goal、每Goal最多17项的公开候选身份读回。依据旧SetSpecific完整函数：Goal+0x88的NumProspects位12起8位；每项4字节的低8位是当前候选池索引（写入函数用prospect与pool的差除以640），再从当前池映射UID。原始排名/点数仍不称完整报告。
- validation_batch.py仅prepare时生成精确脚本/哈希；execute-case要求Human确认引用、相同批单哈希、可恢复存档和显式管理员运行。每case一次性预留；缺少结果不允许重放。每次经原Facade/脚本生成器，锁定游戏PID与启动时间。
- Native runtime附加前增加预期PID反核。没有自动提权、后台服务、重复提交或补偿写入。

## 后续完整验证范围（未缩减）

A：一个指定Team/Coach/Player子集，以及当前公开候选/球探槽。B：Human指定的一个新教练字段（或明确给定训练参数的操作）。C：Human指定队伍与候选UID的精确球探分派，独立读回数量和身份；消费次数操作须另获明确许可。D：只有真实选秀场景/确定交易资产及许可才进入对应一次试验，不制造场景。

没有Human批单许可时真实游戏状态为NOT_AUTHORIZED_NOT_EXECUTED，所有新增成熟度保持旧值。task preflight的唯一未覆盖项是EXPERIMENT_BATCH_01_LIVE_GAME_ACCESS；该结果如实保留，不用历史许可填平。准备代码仍属于任务书明确允许的工作。
