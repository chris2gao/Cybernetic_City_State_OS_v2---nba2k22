# 实机功能验证记录

来源任务NBA2K22-REA-MYLEAGUE-NATIVE-CONTROL-VALIDATION-01，初始基线0008af1。PR14的静态源码不是实机证明；本页只增加本次真实观察。

## 新增已证明的操作

`COACH_SET_KNOWN_CURRENT_SETTINGS`在IND（team_id20）／Rick Carlisle上将`RunPlayTendency`从raw90设为raw55。实际调用Gameplan→Coach原生服务RVA0x146eaa0一次；私有输入保留其它投影字段。函数内完整352字节投影符合预期、原Gameplan未变；独立新REA读取确认55及另外9个已绑定字段不变。状态REAL_NATIVE_EFFECT_VERIFIED，仅覆盖这个字段和实例，UI单位及SaveReload未知。效果保留给Human查看。

## 已有真实Reader子集

IND名单15人及TEAM互链、当前Coach10字段、20个当前公开候选身份、IND球探3Goal／每Goal11项身份与remaining_trips_raw7已真实返回。球队财务仍只raw两个汇总，Player完整属性/倾向/徽章未覆盖，球探原始进度不等于已解锁报告。独立PLAYER与指定prospect进度Reader列入第二批。

## 正在验证的球探追加

Human委托Owner选择测试输入后，选定已公开观察的Sam Perkins UID33143、IND20。IND3槽已满，因此第二批预期原版Append返回拒绝；不删除/覆盖旧目标、不换队，也不消耗考察次数。第二批执行前仍需它自己的精确批单许可。拒绝路径不等于成功分派，后者需空槽场景。

当前真实原始证据与批单在Run：`01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001/`。首批可复核源码及证据提交`8bda78883cbb8f9b10eeabf9a8f08a116fe296db`；能力按字段/实例附加在`data/native_live_validation.json`，保留静态Registry原成熟度，避免把十个字段全部提升。
