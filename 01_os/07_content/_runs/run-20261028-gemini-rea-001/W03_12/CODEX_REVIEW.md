# W03-12 Codex Review Guide

## 1. 重点审核内容
1. **Getter 与执行前后状态闭环**:
   - 本 Getter 目录覆盖了 W03 全域执行前（Preflight Validation）所需的环境输入，以及执行后（Post-Execution Verification）的状态读回。
   - 建议在所有 Native Mutate 操作之后，调用本目录对应的 Getter 函数进行读回校验，确保写入已在游戏内存中实际生效。
2. **结构体相对偏移稳定性**:
   - 结构体内部字段偏移（如 `COACHDATA + 0x13c`, `[rcx + 0x168]` 等）直接与 `NBA2K22.exe` 固定构建哈希强绑定，在游戏更新或切换不同构建版本时需重新核对。
3. **集成建议**:
   - Codex 可将 `native_getter_catalog.py` 作为 `reader/` 或 `facade.py` 中数据查询与前置校验的标准映射源。
