# NBA2K22 VAE REA Sweep 5 集中整改 · 独立复审完成指针

**复审身份**：GPT-6 `independent_review`（同一审核窗口，Human 已明确批准复用；不是新隔离Fork）  
**固定候选真实 SHA**：`6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`  
**原候选父SHA**：`b3e39f867364b4610fc57f5cc798c7ab33232eeb`  
**上一正式审核**：`a15079c425bb2f228afa333dee70df5cde12039c`  
**用户上传报告中的错误完整SHA**：`6f8dfe23a8e97f0450e1eeff99f1fae39d5fc65c`  
**审核分支**：`task/nba2k22-vae-sweep5-remediation-independent-rereview-20261031`（独立于Gemini和master）  
**最终结论**：**REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS**；3 P0、4 P1、2 P2。长期204字段机制研究继续，不要求一轮实证全部游戏因果。

## 已接受的阶段进展

- 校正Tempo、Touches、POEDefense的字段ID；图与204种子库存一致且为16点13边DAG
- 修正Tempo定点寄存器计算，在50/60/70/80/100上源等价得到10/22/34/46/70
- 实验桥接器区分启发式与静态线索，并报告`has_cross_model_divergence`
- 默认`LiveEngineAnalyzer/NativeConsumerTracer(auto_attach=False)`
- 图效果边全部维持`PENDING_GAMEPLAY_VALIDATION`
- 源代码实际定义45个pytest测试函数，但45/45执行尚未独立复跑

## 未闭环核心

1. PE法证收据生成器使用硬编码bytes和硬编码target PE SHA，进行自产bytes哈希；缺真实PE提取→收据的完整可复验证据链。已有Gemini本地PE检视日志仅作为开发者来源线索，未否认其做过本地读取。
2. Role原生证据仅存`0x1226942 + 0x88 = 0x12269ca`前的136字节，而Branch C`0x12269cf`及5项rating缩放`0x1226a18`皆在证据范围外。
3. 旧field_records中的`2026-10-31T03:00:00Z`统一虚构时间未恢复；`WORLD_REG_002`初始UINT32 raw bits `1056964608`仍在当前raw_legacy_capture中被转换为浮点0.5。
4. 8个rel32数学目标正确，但第8个call`0x174512a`不在Snapshot保存的28字节区间内。
5. 实际三项遥测合同未含报告宣称的save/build/season、USER/CPU、双Normalize、N≥10、真实窗口或证伪条件。只要求补语义，不锁定数据库物理结构。
6. 库存`tendency.SHOT_TENDENCY`/ `tendency.TOUCHES_TENDENCY`与live派生记录`tendency.ShotTendency`/`tendency.TouchTendency`为不同命名空间，需明确版控映射。
7. Tracer的enrichment默认`target_dir=None`仍可能原地覆盖正式204个field_records，需要纯函数或append-only派生发布门。
8. Gemini上传报告完整SHA错误；45个测试定义数可证明，但真实pytest和原PE未独立执行。

## 正式交付文件
- `01_任务输入/fixed_candidate_rereview_packet.json`：固定候选/任务/审核边界
- `07_测试执行/independent_rereview_matrix.json`：9发现，且对上一13项逐一评估闭环情况
- `08_结论/consolidated_sweep5_independent_rereview.md`：单份详细复审和有限集中整改建议
- `run.yml`：审核生命周期、审查者身份、未测项与非授权
- `08_结论/completion_pointer.md`：本完成指针（最终SHA以远程审核分支HEAD为准）

**无**：代码开发、游戏/存档更改、master合并、PRMS Save或正式Communication。后续仍由Gemini原任务单字段循环推进，未经Human另行授权不做受保护游戏干预。
