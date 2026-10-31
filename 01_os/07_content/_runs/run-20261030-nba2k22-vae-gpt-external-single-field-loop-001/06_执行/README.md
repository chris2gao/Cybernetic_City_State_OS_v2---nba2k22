# 逐字段外部资料研究执行记录

首轮从队列第一个字段开始，每轮独立字段档案，研究结果与反例追加在本Run。每次成功写入checkpoint及iteration_ledger.jsonl、field_records/<field_id>.json。未执行前不得创建伪造的首轮结果。
