# 任务包 83: 30支球队教练设置“模拟侧重”独立文件执行任务包

> **任务标识**: `TASK-20261123-SIMULATED-GAMEPLAN-FOCUS-EXECUTION`  
> **任务类型**: 执行派单与 REA Native 内存注入执行包  
> **文件格式**: `SPEC-FULL-DIMENSIONAL-NATIVE-MOD-V2` (Doc 43)  
> **文件位置**: `C:\nba2k22\exports\20261123_simulated_gameplan_focus_execution\`  
> **执行目标**: 30 支球队主教练 `GAMEPLAN` 模拟侧重页面 (Scoring Options 1~3 & 6大 POE 攻防重点)  
> **安全级别**: 严格受控内存写入 (只写已定位连续 12 字节 0x178~0x183，杜绝越界)  

---

## 1. 执行背景与说明

本任务包针对 NBA 2K22 教练设置中的 **“模拟侧重” (Simulated Focus)** 页面。  
该页面包含：
- **终结第一选择、第二选择、第三选择** (绑定球队前三大得分核心的真实 Player ID)
- **进攻重点 / 进攻侧重** (POEOffense: 冲击篮筐、为射手跑位、打低位、挡拆进攻等)
- **进攻节奏** (POEOffenseTempo: 耐心阵地、中立、尽早出手)
- **进攻篮板策略** (POEOffenseRebound: 极速退防、冲抢前板)
- **防守重点 / 防守侧重** (POEDefense: 保护禁区、贴防外线三分)
- **防守对抗策略** (POEDefensePhysicality: 保守避免犯规、强硬身体对抗)
- **防守篮板策略** (POEDefenseRebound: 全员保护后板、抓篮板快攻反击)

---

## 2. 执行文件路径与清单

执行模型可直接从以下目录按顺序逐队读取并注入：
**执行目录**: `C:\nba2k22\exports\20261123_simulated_gameplan_focus_execution\`

### 文件清单 (按 Team ID 顺序排列):
1. `00_PHI_sim_focus_mod.json` (76ers: Embiid / Harden / Maxey)
2. `01_MIL_sim_focus_mod.json` (Bucks: Giannis / Middleton / Holiday)
3. `02_WAS_sim_focus_mod.json` (Wizards: Beal / Porzingis / Kuzma)
4. `03_CHI_sim_focus_mod.json` (Bulls: DeRozan / LaVine / Coby White)
5. `04_CLE_sim_focus_mod.json` (Cavaliers: Mitchell / Garland / LeVert)
6. `05_BOS_sim_focus_mod.json` (Celtics: Tatum / Brown / Smart)
7. `06_LAC_sim_focus_mod.json` (Clippers: Leonard / George / Powell)
8. `08_MEM_sim_focus_mod.json` (Grizzlies: Morant / Bane / Melton)
9. `09_ATL_sim_focus_mod.json` (Hawks: Young / Murray / Bogdanovic)
10. `10_MIA_sim_focus_mod.json` (Heat: Butler / Adebayo / Herro)
11. `11_NOP_sim_focus_mod.json` (Pelicans: Zion / Ingram / McCollum)
12. `12_UTA_sim_focus_mod.json` (Jazz: Markkanen / Sexton / Clarkson)
13. `13_SAC_sim_focus_mod.json` (Kings: Fox / Sabonis / Mitchell)
14. `14_NYK_sim_focus_mod.json` (Knicks: Brunson / Randle / Barrett)
15. `15_LAL_sim_focus_mod.json` (Lakers: LeBron / Davis / Nunn)
16. `16_ORL_sim_focus_mod.json` (Magic: Wagner / Suggs / Carter)
17. `17_DAL_sim_focus_mod.json` (Mavericks: Doncic / Dinwiddie / Wood)
18. `18_BKN_sim_focus_mod.json` (Nets: Durant / Irving / Drummond)
19. `19_DEN_sim_focus_mod.json` (Nuggets: Jokic / Murray / Hyland)
20. `20_IND_sim_focus_mod.json` (Pacers: Haliburton / Siakam / Hield)
21. `21_DET_sim_focus_mod.json` (Pistons: Cunningham / Bey / Duarte)
22. `22_TOR_sim_focus_mod.json` (Raptors: VanVleet / Barnes / Dragic)
23. `23_HOU_sim_focus_mod.json` (Rockets: Green / Sengun / Porter)
24. `24_OKC_sim_focus_mod.json` (Thunder: Gilgeous-Alexander / Giddey / Dort)
25. `25_SAS_sim_focus_mod.json` (Spurs: Ball / Johnson / Vassell)
26. `26_PHX_sim_focus_mod.json` (Suns: Booker / Paul / Ayton)
27. `27_MIN_sim_focus_mod.json` (Timberwolves: Edwards / Russell / Towns)
28. `28_POR_sim_focus_mod.json` (Trail Blazers: Lillard / Grant / Bledsoe)
29. `29_GSW_sim_focus_mod.json` (Warriors: Curry / Thompson / Wiggins)
30. `31_CHA_sim_focus_mod.json` (Hornets: Ball / Rozier / Bridges)

---

## 3. 执行规范与安全准则

1. **执行方式**: 
   - 执行模型通过 REA Native 方法读取对应球队 `GAMEPLAN` 内存基址；
   - 遍历各队 json 中的 `writes` 数组（共 9 项）；
   - 计算目标地址 `target_addr = gameplan_base + write["offset"]`；
   - 按照 `write["type"]` (`uint16` 写 2 字节小端序，`uint8` 写 1 字节) 直写 `write["val_raw"]`。
2. **零风险保证**:
   - 仅写已完全定位、严格收敛的 12 字节区域（`offset 376` 至 `offset 387`）；
   - 严禁篡改相邻字段，内存越界保护生效。
