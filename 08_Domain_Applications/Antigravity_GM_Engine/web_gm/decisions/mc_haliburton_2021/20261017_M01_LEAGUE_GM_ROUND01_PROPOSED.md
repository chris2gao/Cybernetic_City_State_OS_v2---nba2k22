# 首次正式全联盟 GM 决策 — 30 队 × 12 模块

- decision_id: `GM-20261017-M01-R01`
- version: `1`
- status: `PROPOSED / PENDING_PLAYER_APPROVAL`
- career_id: `mc_haliburton_2021`
- source_batch_id: `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`
- data_updated_at: `2026-10-17T11:50:28.464724+00:00`
- game_date: `UNKNOWN`，游戏当月封账 `month_closed=false`
- audit: `PASS_VERIFIED`（32 项）；30 队、466 名现役球员
- gameplay_policy: `PLAYER_RULES_20261017_V3`
- transaction_executed: false; player_approved: false; game_write_authorized: false

## 解释与限制

- 本文件是**篮球经营判断**，不是比赛结果预测、球员能力修改或 Codex 执行指令。
- `league.json` 中战绩、得分与资产为游戏实测；场均净胜分 = 场均得分 - 对手场均得分，不是每百回合 Net Rating。
- `gm_analysis` 初评相同批次仅作量化依据；经营档位由此处逐队主观判断，不受待确认的 `gm_policy.json` 阈值自动约束。
- 球员真实赛季统计为迄今累计，部分人只出场1至2场；伤病、官方OVR、具体轮换、CBA完整账本未验证。
- 职员关联已通过源审计，但此次连接无法解码完整 staff.json；不作教练具名雇佣、解聘。
- 2022–24 是未来三届可讨论选秀权；1984 是历史新秀届次，不自动同步。

## 联盟优先结论

争冠观察 PHI/BKN/LAL/SAC；争取上游 MIL/POR/MIA/NYK；竞争或成长 BOS/CHI/ATL/MEM/PHX/DAL/GSW/WAS/NOP；结构调整 LAC/DEN/MIN/SAS；重组评估 IND/TOR/UTA/CHA；长期建设 CLE/HOU/ORL/OKC/DET。

## 逐队12模块

每队顺序：①生命周期战略；②现役阵容；③制服组；④进攻；⑤防守；⑥交易；⑦合同财务；⑧选秀/自由市场；⑨成长；⑩商业；⑪文化；⑫世界线。未具备可写字段和合法性确认前不得将战术方向转成具体字节。

### ATL | 11–8 | +1.37分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：杨/卡佩拉/柯林斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：杨持球挡拆、双翼站位；不自造POE枚举数值。
5. **defense — PROPOSED**：杨外围防守与侧翼轮转；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：保留骨架，询问廉价防守侧翼；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $134.63M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 5 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：亨特/赫尔特；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.5；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：高速年轻核心，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### BKN | 14–5 | +13.32分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：哈登/杜兰特/欧文；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：三核错峰分担持球；不自造POE枚举数值。
5. **defense — PROPOSED**：阿尔德里奇/格里芬的护框衔接；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不动三核，低成本内线才问价；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $167.21M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 1 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：克拉克斯顿；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.78；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：争冠期稳定，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### BOS | 10–9 | +4.16分/场
1. **strategy — PROPOSED**：RISING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：塔图姆/布朗/斯马特；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：双翼进攻加斯马特分球；不自造POE枚举数值。
5. **defense — PROPOSED**：外线压迫和罗伯特·威廉姆斯护框；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不动双翼，先内部优化；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $139.46M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：罗威/普理查德；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.75；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：双翼团队篮球，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### CHA | 7–13 | -6.25分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：拉梅洛/罗齐尔/华盛顿；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：拉梅洛发起挡拆；不自造POE枚举数值。
5. **defense — PROPOSED**：内线护框偏弱，评估特纳；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：试探特纳；不牺牲拉梅洛或重要自有首轮；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $106.53M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 5 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：布克奈特/华盛顿；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.38；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：年轻快节奏，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### CHI | 11–8 | +2.95分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：拉文/德罗赞/朗佐/武切维奇；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：朗佐串联双得分点与中锋；不自造POE枚举数值。
5. **defense — PROPOSED**：锋线尺寸与协防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：询价格兰特；谨慎保留青年球员；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $133.60M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 1 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：帕特里克·威廉姆斯/多森姆；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.75；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：本季冲击季后赛，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### CLE | 6–13 | -6.63分/场
1. **strategy — PROPOSED**：RISING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：加兰/塞克斯顿/莫布利/阿伦；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：双后卫与莫布利共建体系；不自造POE枚举数值。
5. **defense — PROPOSED**：外线防守及失误控制；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不卖青年四核，评估高薪老将；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $139.65M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：莫布利/奥科罗；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.3；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：年轻双高与后场，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### DAL | 9–8 | +1.12分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：东契奇/波尔津吉斯/布伦森；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：减少卢卡孤立高负荷；不自造POE枚举数值。
5. **defense — PROPOSED**：加强防守侧翼和换防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：只寻低成本防守拼图；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $118.55M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 2 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：布伦森/芬尼-史密斯；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.53；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：卢卡空间进攻，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### DEN | 8–10 | -5.00分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：约基奇/穆雷/波特；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：约基奇高位策应与穆雷无球；不自造POE枚举数值。
5. **defense — PROPOSED**：退防和协防衔接；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不交易三核心，轮换优先；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $135.16M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 1 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：波特与功能型翼侧；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.58；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：高位策应，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### DET | 2–16 | -13.11分/场
1. **strategy — PROPOSED**：REBUILDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：坎宁安/贝/斯图尔特；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：增加坎宁安组织与接应；不自造POE枚举数值。
5. **defense — PROPOSED**：年轻人的轮转纪律；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：格兰特列入高价询盘，只收年轻资产和选秀权；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $78.70M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 2 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：坎宁安/贝/斯图尔特；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.48；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：以新秀发展为先，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### GSW | 9–9 | +2.72分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：库里/克莱/格林/怀斯曼；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：格林传导、库里克莱无球；不自造POE枚举数值。
5. **defense — PROPOSED**：检查怀斯曼与前场协防适配；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不急卖怀斯曼、不卖三核；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $175.35M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 2 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：普尔/库明加/怀斯曼；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.86；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：传切团队，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### HOU | 8–10 | -7.39分/场
1. **strategy — PROPOSED**：REBUILDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：杰伦·格林/申京/伍德；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：年轻后场与申京更多配合；不自造POE枚举数值。
5. **defense — PROPOSED**：前场防守与失误；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：询价老将但不贴首轮甩沃尔；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $126.66M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 5 枚、次轮 2 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：杰伦·格林/申京；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.81；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：储备型重建，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### IND | 7–13 | -5.75分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：萨博尼斯/布罗格登/勒韦尔/特纳；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：萨博尼斯高位组织；不自造POE枚举数值。
5. **defense — PROPOSED**：双内线空间与护框配合；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：探索特纳对价，不低价拆队；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $131.28M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：杜阿尔特待可靠比赛样本；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.61；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：团队配合，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### LAC | 8–10 | +1.72分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：伦纳德/乔治；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：双翼错峰组织；不自造POE枚举数值。
5. **defense — PROPOSED**：巩固防守双翼与内线协作；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不交易双翼，内部策略优先；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $168.50M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 1 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：曼恩；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.86；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：现有争冠窗口，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### LAL | 15–5 | +13.05分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：詹姆斯/戴维斯/威斯布鲁克；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：三巨头组织和内线终结；不自造POE枚举数值。
5. **defense — PROPOSED**：外线投射及退防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不拆三核，低价射手才考虑；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $150.66M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 1 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：塔克；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.8；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：本局不复制现实威少叙事，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### MEM | 10–8 | +3.67分/场
1. **strategy — PROPOSED**：RISING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：莫兰特/小杰克逊/布鲁克斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：莫兰特突破和内线外弹；不自造POE枚举数值。
5. **defense — PROPOSED**：布鲁克斯/梅尔顿外围对位；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：保留6枚三年窗口首轮，拒绝短约梭哈；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $100.95M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 6 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：贝恩/克拉克；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.42；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：年轻成长曲线，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### MIA | 13–6 | +2.63分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：巴特勒/阿德巴约/洛瑞；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：巴特勒强攻、阿德巴约高位；不自造POE枚举数值。
5. **defense — PROPOSED**：保持现有强硬防守；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：仅低成本补替补内线；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $130.75M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 2 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：希罗；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.83；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：防守文化，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### MIL | 11–8 | +8.84分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：字母哥/米德尔顿/霍勒迪；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：三核分工、减少持球瓶颈；不自造POE枚举数值。
5. **defense — PROPOSED**：顶级核心对位与补篮板；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不急做改变三核的交易；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $150.99M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 1 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：迪温琴佐；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.87；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：争冠防守，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### MIN | 8–10 | -5.11分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：唐斯/拉塞尔/爱德华兹；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：唐斯外拉、拉塞尔组织；不自造POE枚举数值。
5. **defense — PROPOSED**：锋线压迫和转换退防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：保留爱德华兹，寻侧翼防守；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $135.66M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：爱德华兹/麦克丹尼尔斯；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.46；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：三核攻守整合，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### NOP | 10–10 | -0.55分/场
1. **strategy — PROPOSED**：RISING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：锡安/英格拉姆/瓦兰丘纳斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：锡安冲框加侧翼空间；不自造POE枚举数值。
5. **defense — PROPOSED**：外线投射及回防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不卖锡安/英格拉姆；保留首轮；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $114.90M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 5 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：海斯/亚历山大-沃克；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.45；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：双核心长期路线，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### NYK | 11–7 | +5.39分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：兰德尔/巴雷特/罗斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：兰德尔策应、双后场得分；不自造POE枚举数值。
5. **defense — PROPOSED**：外围对位与换防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不用多首轮立即梭哈；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $112.64M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 5 枚、次轮 7 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：巴雷特/奎克利/托平；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.55；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：务实篮球，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### OKC | 4–14 | -9.72分/场
1. **strategy — PROPOSED**：REBUILDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：亚历山大/吉迪/多尔特；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：亚历山大与吉迪共同发起；不自造POE枚举数值。
5. **defense — PROPOSED**：多尔特外线对位，实验年轻内线；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：保留12首轮价值，不为短期成绩追星；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $50.40M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 12 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：吉迪/亚历山大；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.36；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：长期资产储备，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### ORL | 5–14 | -10.95分/场
1. **strategy — PROPOSED**：REBUILDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：卡特/富尔茨/萨格斯/瓦格纳；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：提高外围空间和传导；不自造POE枚举数值。
5. **defense — PROPOSED**：艾萨克带动前场防守；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：拒绝卖年轻核心，老将交易仅探询；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $113.65M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 4 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：萨格斯/瓦格纳；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.42；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：耐心培育，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### PHI | 16–3 | +9.63分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：恩比德/西蒙斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：西蒙斯组织配合恩比德终结；不自造POE枚举数值。
5. **defense — PROPOSED**：西蒙斯对位和内线保护；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：绝不强制复制现实西蒙斯交易；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $142.20M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 5 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：马克西；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.85；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：16–3的胜率优先，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### PHX | 10–8 | +2.17分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：布克/保罗/艾顿；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：保罗艾顿挡拆、布克侧翼单打；不自造POE枚举数值。
5. **defense — PROPOSED**：侧翼协防与内线卡位；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：保留艾顿，观察替补深度；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $129.89M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 3 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：布里奇斯；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.36；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：团队连续性，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### POR | 12–7 | +4.95分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：利拉德/麦科勒姆/鲍威尔；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：延续强外线命中与顺下；不自造POE枚举数值。
5. **defense — PROPOSED**：强化锋线和内线防守；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：不急售麦科勒姆，询问防守型球员；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $138.18M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 1 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：安芬尼·西蒙斯；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.74；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：双枪争冠窗口，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### SAC | 14–5 | +9.11分/场
1. **strategy — PROPOSED**：CONTENDING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：哈利伯顿/福克斯；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：维持双后卫共存及低失误；不自造POE枚举数值。
5. **defense — PROPOSED**：前场护框/锋线对位；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：严禁交易玩家哈利伯顿，不急售希尔德；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $136.66M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：戴维恩·米切尔/巴格利；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.63；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：形成国王自主争冠历史，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### SAS | 8–9 | -6.65分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：德章泰·穆雷/瓦塞尔/凯尔登；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：增加组织与转换终结；不自造POE枚举数值。
5. **defense — PROPOSED**：穆雷外围对位与内线协防；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：赛迪斯·杨只在合理报价时询价；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $110.10M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 4 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：瓦塞尔/凯尔登；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.83；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：稳定转型，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### TOR | 7–12 | -6.84分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：范弗利特/西亚卡姆/巴恩斯/阿奴诺比；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：高位发起与接球投篮；不自造POE枚举数值。
5. **defense — PROPOSED**：年轻锋线防守；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：德拉季奇合同市场摸底，保留巴恩斯；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $137.15M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 3 枚、次轮 0 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：巴恩斯/阿丘瓦；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.74；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：团队连续性，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### UTA | 5–13 | -6.11分/场
1. **strategy — PROPOSED**：RETOOLING；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：米切尔/戈贝尔/康利；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：优先确认米切尔比赛可用性；不自造POE枚举数值。
5. **defense — PROPOSED**：戈贝尔护框与外围联动；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：暂不拆双核，复核样本后决策；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $155.04M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 1 枚、次轮 1 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：米切尔上场仅2场，需核验；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.72；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：拒绝凭一个月复制现实拆队，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

### WAS | 10–8 | +1.11分/场
1. **strategy — PROPOSED**：COMPETITIVE；短期检验现有结构，中期复核30队竞争格局，长期由自然成长和真实选秀决定。
2. **roster — PARTIAL**：比尔/丁威迪；在观测球员表现基础上评估，不以现实NBA成绩替代当前存档。
3. **staff — PARTIAL**：暂保留教练和制服组；团队角色读取需完整映射后才能决定岗位变更。
4. **offense — PROPOSED**：分担比尔持球；不自造POE枚举数值。
5. **defense — PROPOSED**：外线压迫和转换防守；未观测的轮换与伤病不能当既定事实。
6. **trades — PROPOSED**：核对比尔合同再评估交易；仅经营方向/询价，不是已生效报价。
7. **contracts — PARTIAL**：观测球队总工资 $135.46M（静态观测）；真实CBA空间、薪资匹配仍未知，不能认定交易合法。
8. **draft_free_agency — PARTIAL**：2022–24 当前持有首轮 2 枚、次轮 0 枚；任何报价以具体 asset_id 校验归属，暂不指定未认证的自由球员。
9. **development — PROPOSED**：阿夫迪亚/八村塁；严格自然成长，不改数值。
10. **business — PARTIAL**：fan_interest 0.54；票价敏感度/收入时间窗未认证前不擅自调价。
11. **culture — REFERENCE**：竞争力与弹性，不强制历史事件。
12. **worldline — PROPOSED**：本局实际成绩优先；历史重力不在本轮自动执行，历史选秀进度待玩家确认。

## 交易市场：真实筹码、仅为未确认的市场询价

### MKT-01 CHI / DET — 探询格兰特
- CHI 希望获得 DET Jerami Grant（pool_slot 319、18场场均21.11分、年薪 $20,002,500）。DET 在2–16时可考虑年轻人及首轮报价。
- 初始探询结构：CHI Coby White（slot 37，$5,837,760）+ Derrick Jones Jr.（slot 38，$9,720,900）+ 2022 POR原始首轮（`draft_pick:2022:1:28`，本批当前持有队CHI）↔ DET Jerami Grant。
- 静态工资：CHI 送出 $15,558,660、接收 $20,002,500，差额 +$4,443,840。此数仅作薪资差，**不是CBA匹配核验**；活塞可要求更多，公牛可拒绝高价。
- status: `INTEREST_ONLY / CBA_UNKNOWN / EXECUTOR_NOT_VALIDATED / PENDING_PLAYER_APPROVAL`。

### MKT-02 CHA / IND — 探询特纳
- CHA 考察 IND Myles Turner（slot 290，13场场均8.38分，内线防守能力87、封盖97，年薪$18,000,000）。
- 意向性回价：CHA Mason Plumlee（slot 151，$9,248,333）+ P.J. Washington（slot 150，$4,215,120）+ CHA持有的2024 BOS原始次轮（`draft_pick:2024:2:5`）↔ IND Turner。
- CHA 送出球员工资 $13,463,453、接收 $18,000,000，差额 +$4,536,547。需验证规则、价值和年龄/可用性；若索要CHA自有2023首轮则撤回报价。
- status: `INTEREST_ONLY / CBA_UNKNOWN / EXECUTOR_NOT_VALIDATED / PENDING_PLAYER_APPROVAL`。

## 特别警戒

- UTA 的 Donovan Mitchell 仅出场2场，Miye Oni仅出场1场（27分钟0分），不得把场均时间当稳定轮换规律，也不得推断受伤。
- SAC 同时有 `Tyrese Haliburton`（pool_slot=1235、19场、场均54.16分，玩家保护核心）与 `Ty Hali`（pool_slot=184、无当前赛季上场记录）。不可合并两个对象，任何操作须用完整身份重新校验。
- 当前队伍的 chemistry 字段均为70，无法作为团队差异依据。CLE/NOP/ORL/UTA 的 cash 中出现约42.9亿美元异常值，任何现金/票价决策都须先核验字段编码。
- POE 部分枚举未认证（尤其ON_BALL_PRESSURE），禁止猜测数字；正式轮换执行器也未验收。
- 勇士9–9、净胜分为正；湖人15–5且威斯布鲁克有效；76人16–3且西蒙斯持续出场，不能强制现实历史操作。

## 玩家审批动作（仅分别批准时生效）

| action_id | 优先级 | 内容 | 批准性质 | 当前游戏写入 |
|---|---|---|---|---|
| GM-A01 | P0 | 认可30队经营方向作为下一阶段决策基准 | 战略确认 | 无 |
| GM-A02 | P0 | 保护国王哈利伯顿、暂保留PHI/LAL/BKN主核 | 资产策略 | 无 |
| GM-A03 | P0 | 请求核对UTA核心出场样本、SAC同名身份、异常cash字段 | 数据分析请求 | 无 |
| GM-A04 | P1 | 对GSW/UTA/DAL/CHI/IND做战术/轮换可行性检查 | 研究/开发请求 | 无 |
| GM-A05 | P1 | 允许MKT-01与MKT-02进入市场询价讨论 | 非约束询价 | 无 |
| GM-A06 | P2 | 补齐制服组、伤病、轮换、门票弹性及完整交易合法性验证 | 数据/开发请求 | 无 |
| GM-A07 | P2 | 暂停属性改动和历史重力执行，继续游戏自然成长 | 世界线方向 | 无 |

批准任何上述内容，都不自动升级为具体交易/调价/写内存的批准。以后若形成明确执行方案，必须新版本列出现值/目标、两边球员/资产和写后业务验收，再交给Codex。

## 执行交接门槛

文档34/36说明现有策略和票价 setter 部分存在但游戏枚举/业务效果未全面验收；交易、选秀权、合同、人员变更和历史新秀注入尚缺生产级完整业务执行器。本轮**无已授权游戏动作**。玩家另行明确批准后，执行窗口仍须重新定位对象与内存、核验真实原值、处理失败和幂等，独立报告内存回读、存盘、GitHub同步结果。