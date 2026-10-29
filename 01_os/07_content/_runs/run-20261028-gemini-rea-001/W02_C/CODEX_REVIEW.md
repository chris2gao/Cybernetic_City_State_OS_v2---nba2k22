# Codex Review Points: W02-C Team Playbook 68 Slots

## 1. 核心审查要点 (Top Audit Points)

1. **360 字节与 68 槽物理布局**:
   - `PLAYBOOKDATA` 结构总长度 360 字节（`0x168`），与 `coach_tactics_profile.json` 中的 `playbook_stride: 360` 吻合。
   - 槽位起始偏移为相对 `+0x58`（88 字节），68 个槽位每槽 4 字节（uint32 Play CRC32），`88 + 68 * 4 = 360` 字节。
   - `0x7aa584` 指令 `cmp eax, 0x44` 验证了原版 UI 与业务对 68 槽的上限检查。

2. **四个分区范围**:
   - `REGULAR`: 槽 0..29 (30 槽，偏移 `0x58`..`0xD0`)
   - `BENCH`: 槽 30..49 (20 槽，偏移 `0xD0`..`0x120`)
   - `ENDGAME`: 槽 50..59 (10 槽，偏移 `0x120`..`0x148`)
   - `FAVORITE`: 槽 60..67 (8 槽，偏移 `0x148`..`0x168`)

3. **共享战术池与球队战术书边界**:
   - 共享战术池保存全局战术脚本与动画；
   - 球队 Playbook 仅保存 68 项引用的 CRC32，修改槽位写入的是目标战术的 CRC32，绝不破坏共享池。

4. **独立提交机制缺口**:
   - 原版单独在内存中修改 68 槽后，持久化写盘依赖整个 Coach/Team 数据的存盘事务。尚未发现独立的单一微型 Playbook Flush Native Action，标记为 `STILL_PARTIAL`。
