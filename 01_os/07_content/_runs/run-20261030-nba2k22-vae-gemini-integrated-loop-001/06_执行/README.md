# 单一主任务迭代记录

每轮使用同一Task ID和本Run，写入当前检查点与简要的迭代记录；禁止用迭代编号代替独立OS任务。`iteration_ledger.jsonl`在真正执行第一轮时创建，按追加事实记录：sequence、base/head、selected_gap、evidence、actual_tests、changed_files、remaining_failures、next_priority、stop_reason。此README不声称已经执行任何循环。
