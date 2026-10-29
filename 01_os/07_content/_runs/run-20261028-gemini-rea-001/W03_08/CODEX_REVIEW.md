# W03-08 Codex Review Guide

## 1. 重点审核内容
1. **名单人数硬约束**:
   - 裁员或签约前必须调用 `validate_roster_legality`。
   - 满 15 人时若直接调用签约 Native 函数会导致原版崩溃或静默失败，必须先触发裁员流程。
2. **职员签约的角色约束**:
   - 职员必须传入合法的角色枚举（8..20），传入小于 8 或大于 20 的 ID 会被 `0x1327590` 直接拒绝返回 0。
3. **集成建议**:
   - `staff_roster_codec.py` 适用于与 `team.waive` (0x12d3d30), `team.release_internal` (0x12d0340) 以及 `staff.sign` (0x13275e0 / 0x1327590) 配合。
