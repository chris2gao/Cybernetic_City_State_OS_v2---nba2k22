# W03-10 Codex Review Guide

## 1. 重点审核内容
1. **交易配平与限制规则**:
   - `trade_package_codec.py` 实现了完整的 NBA CBA 薪资配平校验算法。
   - 在调用 `0x132b040` (`trade.commit_wrapper`) 前必须先过配平检查，否则 Native 引擎内部会中断并返回失败代码。
2. **三方交易资产平衡**:
   - 三方交易中每个参与方都必须独立满足“转入薪资合法”与“名单人数不超过 15 人”。
3. **集成建议**:
   - 将 `trade_package_codec.py` 与 `trade.validate` (0x12ec130) 及 `trade.commit_wrapper` (0x132b040) 结合，支持完整的 GM 交易执行。
