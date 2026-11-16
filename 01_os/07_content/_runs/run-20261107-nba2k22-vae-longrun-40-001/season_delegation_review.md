# 赛季级委托审批材料

机器合同 [season_research_delegation.json](season_research_delegation.json) 是待批准候选。公开文件中的空绑定字段须在私有副本填入，以确切最终摘要供 Human 裁决。当前前置是 [Issue #39](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/39) 的测试专用接口、短窗安全和 Save/reload；本次不启动 runner。

| 现行机制 | 候选变化 | 取舍和验收 |
| --- | --- | --- |
| S4 的单角色同队 1–3 人、原 role manifest hash、逐批精确文件 SHA 和 plan digest、Getter CAS、原生资源锁 | 由 Human 分开批准 Setter 委托封套。未来由现有 Host 验证受信 Human 决策，针对封套内已冻结 UID/队伍、角色、字段和剂量生成逐批可审计证明。 | **当前逐批门继续生效。** 候选扩展需在 Host 证明审批链、拒绝伪造/过期/撤销、精确范围、并发 CAS 和 UNKNOWN 锁，独立审核后按保护规则集成。 |
| S3 和 #39 的日期检查、前台短窗 Native 研究、赛果采集 | 单独日历许可。每窗最多 7 日、1 次原生调用，至多 14 窗和 98 游戏日。候选最晚 stop-exclusive 2022-04-11，实际更早取新鲜赛程常规赛界与已批准事件界。 | 逐窗冻结 Game IDs、场景、前台、异常、核验和无重放；跨贸易截止、全明星及非普通比赛窗先停。 |
| 当前跨赛季没有自动承接 | 单一有界前台 runner 到停止门输出季检查点。Human 推进下一常规赛或恢复冻结备份。 | 显式 Save/reload 通过后才开启自动多窗口。新 save/epoch/赛季需再绑定并核对封套覆盖。PRMS 在可用既有授权状态仓时走 WriterGate，否则走精确 GitHub 检查点。 |

建议封套按首轮设计收紧为每队每窗最多一位有效 UID，一次单项批次。每窗最多 12 批，赛季总计最多 168 次写入，含任何恢复值操作。处理剂量仅限相对预登记基线 ±5，值域 0–100。48 小时为建议墙钟预算，最终精确 UTC 到期随批准固定。旧 95→96 证据用于认证调用路径，这些建议剂量和预算需要本次裁决。筛选可自适应选择已冻结合格对象，主要端点、剂量和世界线变更进入下一份批准。

Human 最终需对**同一份确切填充合同摘要**给出两项独立范围决定：

- 是否批准在这个槽、赛季和日期/次数上界内执行 `calendar_sim_authorization`。
- 是否批准在这个槽、队伍/UID 集、字段、剂量和次数上界内启用 Host 的 `native_setter_batch_authorization`。如暂不批准，继续沿用已存在的精确逐批门。

批准仅记录 Human 原话与来源。风险停止后由 Host/日历日志进行只读核对，结果不明保持占用，任何撤销立即阻止新批次。常规赛界人类接管。参见 [Core §7.2](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/877077c16bad41cfa97c1ebc9862a70ce610ff0b/01_os/%E5%BC%80%E5%8F%91%E5%85%A5%E5%8F%A3%E4%B8%8E%E5%8D%95%E7%AA%97%E5%8F%A3%E4%BB%BB%E5%8A%A1%E8%A7%84%E8%8C%83_v1.md#72-human-%E7%A1%AE%E8%AE%A4%E4%B8%8E%E5%A4%A7%E4%BB%BB%E5%8A%A1%E9%A2%84%E7%A1%AE%E8%AE%A4)。
