# 单字段科研Loop账本

每轮只处理一个field_id，基于共享队列固定SHA；首轮不跳过任何字段，阻塞时单条归档UNKNOWN并推进。实际执行后创建`iteration_ledger.jsonl`与`field_records/<field_id>.json`，附每轮来源/工具命令/预期/实际/反例/下一改进及精确commit。当前仅派单，未运行任何一轮。
