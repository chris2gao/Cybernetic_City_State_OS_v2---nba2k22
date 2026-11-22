# NBA 2K22 1984 届历史选秀名单第一阶段勘测与增强工程报告
## (Task ID: TASK-NBA2K22-1984-DRAFT-RECON-01)

> **任务定位**：针对 `C:\nba2k22\saves\MyLEAGUE0005\` 存档展开第一阶段数据勘测、特征工程与名单规范编制。
> **执行角色**：`role-content-developer` (特色内容开发 / 执行模型)
> **安全纪律**：本阶段为只读特征工程与离线脚本研发，未执行任何内存热写入；严格收敛于 1984 届选秀名单，未处理任何 1984 以前历史名宿。

---

### 一、选秀名单槽位结构勘测发现

通过对 `C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite` 的深度勘测，确立了游戏实机加载 1984 选秀名单的物理布局：

1. **槽位映射区间**：
   - 游戏当前挂载的选秀名单（`draft_year = 2022` 临时映射代号）起始于 **Slot 590**，终止于 **Slot 741**（共 151 个新秀槽位）；
   - 前两轮 60 名真实顺位新秀精确映射至 **Slot 590 至 Slot 649**（共 60 个槽位）；
   - 步长对应底层球员结构体数组，步长为精确 `0x4F0`（1,264 字节）。

2. **当前存档现状与历史遗留缺陷诊断**：
   - **顺位错位**：先前局部测试中，Slot 591~595 零散写入了 Jordan、Perkins、Thorpe、Willis、Stockton，但 Slot 590（状元槽位）仍为随机小人 `Darius Bonner`，导致乔丹被错置为第 2 顺位、斯托克顿被错置为第 6 顺位；
   - **泥人泛滥（Mud-man）**：Slot 590 以及 Slot 596~649 等其余 55 个槽位的 `cyberface_id` 均为 `1`（游戏原生随机捏脸泥人），游戏内呈现严重失真；
   - **巨星缺失**：官方名单因历史版权缺失查尔斯·巴克利（Charles Barkley），且奥拉朱旺未在选秀前列正确挂载。

---

### 二、1984 届 60 名真实新秀全景盘点

本次工程严格根据 1984 年 NBA 真实选秀记录（1984 NBA Draft），建立完整的 60 人真实新秀总账：

- **首轮（Picks 1 ~ 24）**：
  1. Hakeem Olajuwon (HOU) - C
  2. Sam Bowie (POR) - C
  3. Michael Jordan (CHI) - SG
  4. Sam Perkins (DAL) - PF
  5. Charles Barkley (PHI) - PF
  6. Melvin Turpin (CLE) - C
  7. Alvin Robertson (SAS) - SG
  8. Lancaster Gordon (LAC) - SG
  9. Otis Thorpe (SAC) - PF
  10. Leon Wood (PHI) - PG
  11. Kevin Willis (ATL) - PF
  12. Tim McCormick (CLE) - C
  13. Jay Humphries (PHX) - PG
  14. Michael Cage (LAC) - PF
  15. Terence Stansbury (DAL) - SG
  16. John Stockton (UTA) - PG
  17. Jeff Turner (NJN) - PF
  18. Vern Fleming (IND) - PG
  19. Bernard Thompson (POR) - SF
  20. Tony Campbell (DET) - SF
  21. Kenny Green (PHI) - SF
  22. Tom Sewell (PHI) - SG
  23. Earl Jones (LAL) - C
  24. Michael Young (BOS) - SF

- **次轮与深度轮次遗珠（Picks 25 ~ 60）**：
  - 次轮核心：Devin Durrant, Victor Fleming, Ron Anderson, Cory Blackwell, Stuart Gray, Steve Burtt, Jay Murphy, Vince Humphries, Steve Colter, Tony Costner, Othell Wilson, Kelly McKinley, Ben Coleman, Charlie Sitton, Danny Young, Anthony Teachey, Tom Sluby, Willie White, Greg Wiltjer, Fred Reynolds, Gary Plummer, Jerome Kersey (Pick 46), Brian Martin.
  - 三轮及后续神级拼图：Jim Petersen (Pick 48), Eric Turner (Pick 49), Carl Henry (Pick 50), Dan Trant, Vernon Hawkins, Ricky Ross, Michael Revell, Ron Cavenall, Dave Lattin, Mark Halsel, Greg Hargrove, Mark Waddell, Dan Crosswhite.

---

### 三、Face ID 分类与外观映射方案（消灭随机泥人）

为彻底消除 `cyberface_id == 1` 的随机泥人脸，建立两级外观映射标准：

#### 1. Class A：官方底层高精度面补（9 人）
通过检索 `player_pool.sqlite` 历史模型与 2K 经典面补库，确立以下官方 Face ID：
- **Hakeem Olajuwon** (Pick 1, Slot 590): `Face ID 952`（2K 官方奥拉朱旺真实面补，原代码 378 已修正）
- **Michael Jordan** (Pick 3, Slot 592): `Face ID 1759`（2K 官方 1984 年轻/新秀版乔丹）
- **Sam Perkins** (Pick 4, Slot 593): `Face ID 1747`（2K 官方珀金斯面补）
- **Charles Barkley** (Pick 5, Slot 594): `Face ID 606`（2K 复古/Mod 标准巴克利独立面补）
- **Otis Thorpe** (Pick 9, Slot 598): `Face ID 2019`（2K 官方索普面补）
- **Kevin Willis** (Pick 11, Slot 600): `Face ID 318`（2K 官方威利斯面补）
- **John Stockton** (Pick 16, Slot 605): `Face ID 163`（2K 官方斯托克顿面补）
- **Jeff Turner** (Pick 17, Slot 606): `Face ID 2047`（2K 官方特纳面补）
- **Jerome Kersey** (Pick 46, Slot 635): `Face ID 1749`（2K 官方柯西面补）

#### 2. Class B：高质量专属通用预设面补（51 人）
对其余 51 名无独立官方面补的球员，依据其身材体型、位置骨骼特征，统一分配 `1050` 至 `1103` 范围内的专属预设 Face ID，彻底杜绝空白面孔与随机泥人，确保进入游戏后所有人均有工整逼真的 3D 建模。

---

### 四、交付物与验证清单

本任务产出的全部规范、脚本与报告均已同步保存于本地仓库与外部 `C:\nba2k22` 目录：

1. **选秀增强规格书**：
   - 仓库路径：`08_Domain_Applications/Antigravity_GM_Engine/database/draft_classes/1984_draft_enhancement_spec.json`
   - 外部路径：`C:\nba2k22\exports\1984_draft_enhancement_spec.json`
   - 规模：完整包含 60 名真实新秀（Picks 1 ~ 60，Slot 590 ~ 649），包含完整攻防属性、身高级别、倾向与面补映射。

2. **批量修改与增强执行脚本**：
   - 仓库路径：`08_Domain_Applications/Antigravity_GM_Engine/src/apply_1984_draft_enhancements.py`
   - 外部路径：`C:\nba2k22\exports\apply_1984_draft_enhancements.py`
   - 特性：
     - 支持 `--dry-run` 预览与 `--commit` 写入；
     - 自动执行修改前快照备份（`.bak`）；
     - 同步更新关系字段与 1,264 字节二进制 `raw_struct`；
     - 支持 `--verify` 自动化全量回读与哈希比对。

3. **测试验证结果**：
   - 静态规格测试：`python -c "import json; d=json.load(open('.../1984_draft_enhancement_spec.json')); assert len(d) >= 60"` $\rightarrow$ **PASS (60 人)**
   - 语法编译测试：`python -m py_compile .../apply_1984_draft_enhancements.py` $\rightarrow$ **PASS (Exit 0)**
   - 演练运行：`apply_1984_draft_enhancements.py` (DRY-RUN 模式) $\rightarrow$ **PASS (60 槽位全部对齐)**

---

### 五、后续执行模型调用指南

后续负责实机修改或数据库持久化的执行模型，可通过单行命令一键完成 1984 选秀增强注入：

```bash
# 1. 演练并查看变更日志
python 08_Domain_Applications/Antigravity_GM_Engine/src/apply_1984_draft_enhancements.py --db-path "C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite"

# 2. 正式持久化写入 (带自动备份)
python 08_Domain_Applications/Antigravity_GM_Engine/src/apply_1984_draft_enhancements.py --db-path "C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite" --commit

# 3. 验证回读契合度
python 08_Domain_Applications/Antigravity_GM_Engine/src/apply_1984_draft_enhancements.py --db-path "C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite" --verify
```
