# M3｜AI GM↔AI GM交易：评估、资格与commit分别判断

范围：PC22离线MyLEAGUE内部AI自动交易；玩家确认/编辑菜单不作执行主链。共享纯业务核心如有AI调用点仍可研究，不能因带UI名字就断言其所有被调函数均Human专属。

## 分阶段证据

| 阶段 | 本轮源绑定结果 | 结论 |
| --- | --- | --- |
| proposal/evaluation | `.rdata`中EVALUATE_AI_TRADES字面量，未由该字面量找到可执行AI调用点 | 名称线索，AI路径未验证 |
| validator | 对ValidateTrade、TRADE_MANAGER等有界词项查询未取得对应AI资格函数 | BOUNDED_UNKNOWN，不是不存在 |
| exception资产访问 | GetException、GetExceptionAmount候选fragment分别RVA19863840..19864056、19864064..19864291，50/55指令 | L2局部访问器证据，不能代validator或commit |
| commit | 未找到源绑定、可安全外调的完整AI-AI commit路径 | BOUNDED_UNKNOWN；未调用 |
| 玩家UI | MYLEAGUEMENU_THREETEAMTRADE的Text/GameEvent/QueryDbHandler字面量 | UI候选分支不作为AI-AI执行证据，未宣称共享内核不可能 |

GetException片段可见对对象+4的0x30000 mask、0xFFFF ID条件及链式对象查询；不在此命名常数的业务意义。该片段没有提供交易原子性、合法性、公平性或双方同意算法。调用子函数的副作用也未闭合，不能作为“纯函数可调用”依据。

## 必须覆盖的影响集合

名单/球队归属、合同归属与条款、薪资与奢侈税/例外、选秀权及保护、球队交易记录、消息/事件、索引/缓存和后续存档一致性，都需逐项查证。当前这些原生commit变化均未观察。

现有`approved_trade_executor.py`自述`ownership_transfer_v2`不写salary/attributes/minutes/strategy/finance；本轮仅静态读取，不调用。它是已有批准外部执行路线的历史工程，不能作为原版事务或新Memory后端资格。保持原交易/签约/选秀架构原样。

## AI边界与后端

外部AI GM代表某队，不证明引擎把它标为AI_CONTROLLED。双方controller来源和AI分发均未知；原型中Human counterparty明确被拒绝，任何未合格Native/Memory请求都NO_SAFE_PATH。只改变Player TeamID的结果也不会作为完整交易。

Native=NOT_QUALIFIED；Memory=NOT_QUALIFIED；disposition=BOUNDED_UNKNOWN。没有真实交易函数hook/调用，没有交易写入，没有场景或日期推进，没有L3/L4。

后继：先给一个无玩家确认环的AI-AI交易观察场景及资产集合，追踪自然proposal/evaluate/validate/commit间的边界和失败响应；交易effectful PoC后置于已闭合的coach实验。未知原子性或部分提交时停止，不承诺盲快照回滚。
