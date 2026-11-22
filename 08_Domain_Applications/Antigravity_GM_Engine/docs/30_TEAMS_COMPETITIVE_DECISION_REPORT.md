# NBA 2K22 全联盟 30 队战力与轮换极致调优决策报告

> 任务标识：TASK-NBA2K22-SETTING3-STRATEGY-DECISION-01
> 数据基线：C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite
> 决策模型：NBA2K22 智能体决策模型 (AI Agent / Decision Architecture)

---

## 一、核心决策原则与上场时间调优机制

1. **240 分钟严格数学守恒**：全队 9 人主力轮换出场时间严格配平为 240 分钟（超巨 35~37m，主力 28~32m，优质第 6 人 26m，核心拼图 14~20m）。
2. **上场时间与补偿评分（Intangibles）解耦调优**：
   - 2K 原版 AI 在常规赛模拟中会覆盖手动设定的分钟数值。真正决定原版 AI 出场时间的核心参数是球员的【补偿评分（Intangibles）】。
   - 决策方案针对关键轮换球员（如防守大闸、微波炉射手）提供定向提升补偿评分方案（80~95），确保原版 AI 主动分配充足出场时间；对高评低效的 DNP 球员实施评分压制（40），杜绝 AI 乱排阵容。
3. **终结五虎（Clutch 5）定制**：锁定第四节决胜时刻最强阵容，确保关键时刻攻防兼备与投篮空间惩罚力。
4. **8 项 POE 攻防战术倾向定制**：根据阵容特质确立进攻核心模式、战术节奏、前场篮板策略、防守重心与压迫度。

---

## 二、全联盟 30 支球队战力方案概览表

| ID | 球队 | 进攻第一核心 | 战术二当家 | 最优首发五虎 | 终结五虎 (Clutch 5) | 主打战术倾向 (POE) |
|:---|:---|:---|:---|:---|:---|:---|
| 0 | **Philadelphia 76ers** | Joel Embiid | Seth Curry | Ben Simmons / Shake Milton / Danny Green / Tobias Harris / Joel Embiid | Seth Curry / Joel Embiid / Tobias Harris / Danny Green / Ben Simmons | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 1 | **Milwaukee Bucks** | Khris Middleton | Giannis Antetokoun | Jrue Holiday / Donte DiVincenzo / Khris Middleton / Giannis Antetokoun / Bobby Portis Jr. | Jrue Holiday / Giannis Antetokoun / Khris Middleton / Brook Lopez / Bobby Portis Jr. | GET_TO_BASKET + LIMIT_PERIMETER_SHOTS |
| 2 | **Washington Wizards** | Bradley Beal | Cassius Winston | Raul Neto / Bradley Beal / Kyle Kuzma / Rui Hachimura / Daniel Gafford | Bradley Beal / Davis Bertans / Raul Neto / Rui Hachimura / Kyle Kuzma | GET_TO_BASKET + NEUTRAL_DEFENSE_FOCUS |
| 3 | **Chicago Bulls** | Zach LaVine | Nikola Vucevic | T.J. McConnell / Zach LaVine / DeMar DeRozan / Patrick Williams / Nikola Vucevic | T.J. McConnell / Nikola Vucevic / Zach LaVine / DeMar DeRozan / Coby White | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 4 | **Cleveland Cavaliers** | Darius Garland | Caris LeVert | Darius Garland / Caris LeVert / Justin Holiday / Evan Mobley / Jarrett Allen | Caris LeVert / Jarrett Allen / Darius Garland / Kevin Love / Collin Sexton | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 5 | **Boston Celtics** | Jaylen Brown | Jayson Tatum | Marcus Smart / Jaylen Brown / Jayson Tatum / Al Horford / Robert Williams | Jaylen Brown / Al Horford / Jayson Tatum / Marcus Smart / Josh Richardson | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 6 | **Los Angeles Clippers** | Paul George | Kawhi Leonard | Eric Bledsoe / Paul George / Kawhi Leonard / Marcus Morris Sr. / Serge Ibaka | Paul George / Serge Ibaka / Kawhi Leonard / Marcus Morris Sr. / Reggie Jackson | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 8 | **Memphis Grizzlies** | Desmond Bane | Kyle Anderson | Ja Morant / Dillon Brooks / Kyle Anderson / Jaren Jackson Jr / Xavier Tillman | Dillon Brooks / Jaren Jackson Jr / Kyle Anderson / De'Anthony Melton / Ja Morant | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 9 | **Atlanta Hawks** | Trae Young | Bogdan Bogdanovic | Trae Young / Bogdan Bogdanovic / De'Andre Hunter / John Collins / Clint Capela | Bogdan Bogdanovic / John Collins / De'Andre Hunter / Danilo Gallinari / Skylar Mays | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 10 | **Miami Heat** | Kyle Lowry | Eric Gordon | Kyle Lowry / Eric Gordon / Jimmy Butler / Isaiah Todd / Bam Adebayo | Kyle Lowry / Bam Adebayo / Jimmy Butler / Eric Gordon / Victor Oladipo | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 11 | **New Orleans Pelicans** | Brandon Ingram | Zion Williamson | Tomas Satoransky / Buddy Hield / Brandon Ingram / Zion Williamson / Jonas Valanciuna | Devonte Graham / Jonas Valanciuna / Brandon Ingram / Tomas Satoransky / Buddy Hield | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 12 | **Utah Jazz** | Donovan Mitchell | Joe Ingles | Mike Conley / Donovan Mitchell / Joe Ingles / Eric Paschall / Rudy Gobert | Donovan Mitchell / Royce O'Neale / Mike Conley / Joe Ingles / Bojan Bogdanovic | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 13 | **Sacramento Kings** | De'Aaron Fox | Domantas Sabonis | De'Aaron Fox / Jahmi'us Ramsey / Jeremy Lamb / Domantas Sabonis / Richaun Holmes | De'Aaron Fox / Richaun Holmes / Jeremy Lamb / Harrison Barnes / Domantas Sabonis | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 14 | **New York Knicks** | Julius Randle | Evan Fournier | Derrick Rose / Evan Fournier / R.J. Barrett / Julius Randle / DeMarcus Cousins | Immanuel Quickley / Julius Randle / Alec Burks / Derrick Rose / R.J. Barrett | GET_SHOOTERS_OPEN + NEUTRAL_DEFENSE_FOCUS |
| 15 | **Los Angeles Lakers** | LeBron James | Kendrick Nunn | Russell Westbrook / Malik Monk / LeBron James / Anthony Davis / Nerlens Noel | Russell Westbrook / Anthony Davis / LeBron James / Kendrick Nunn / Carmelo Anthony | GET_TO_BASKET + NEUTRAL_DEFENSE_FOCUS |
| 16 | **Orlando Magic** | Cole Anthony | Terrence Ross | Cole Anthony / R.J. Hampton / Franz Wagner / Chuma Okeke / Wendell Carter Jr. | Jalen Suggs / Wendell Carter Jr. / Franz Wagner / Chuma Okeke / Cole Anthony | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 17 | **Dallas Mavericks** | Luka Doncic | Jalen Brunson | Luka Doncic / Tim Hardaway J / Reggie Bullock / Maxi Kleber / Kristaps Porzingis | Luka Doncic / Kristaps Porzingis / Reggie Bullock / Jalen Brunson / Maxi Kleber | GET_SHOOTERS_OPEN + NEUTRAL_DEFENSE_FOCUS |
| 18 | **Brooklyn Nets** | Kevin Durant | Kyrie Irving | Kyrie Irving / James Harden / Joe Harris / Kevin Durant / LaMarcus Aldridge | James Harden / Kevin Durant / Kyrie Irving / Joe Harris / LaMarcus Aldridge | GET_SHOOTERS_OPEN + NEUTRAL_DEFENSE_FOCUS |
| 19 | **Denver Nuggets** | Nikola Jokic | Jamal Murray | Jamal Murray / Austin Rivers / Michael Porter Jr. / Aaron Gordon / Nikola Jokic | Jamal Murray / Nikola Jokic / Michael Porter Jr. / Mason Plumlee / JaMychal Green | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 20 | **Indiana Pacers** | Tyrese Haliburton | Dejounte Murray | Tyrese Haliburton / Josh Hart / Robert Covington / Pascal Siakam / Myles Turner | Tyrese Haliburton / Pascal Siakam / Dejounte Murray / Myles Turner / Derrick White | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 21 | **Detroit Pistons** | Cade Cunningham | Jerami Grant | Cade Cunningham / Josh Jackson / Saddiq Bey / Jerami Grant / Isaiah Stewart | Cade Cunningham / Kelly Olynyk / Jerami Grant / Saddiq Bey / Isaiah Stewart | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 22 | **Toronto Raptors** | Malcolm Brogdon | Fred VanVleet | Malcolm Brogdon / Fred VanVleet / OG Anunoby / Scottie Barnes / Precious Achiuwa | Fred VanVleet / Chris Boucher / Malcolm Brogdon / OG Anunoby / Goran Dragic | GET_TO_BASKET + NEUTRAL_DEFENSE_FOCUS |
| 23 | **Houston Rockets** | Jalen Green | Duncan Robinson | John Wall / Jalen Green / David Nwaba / Tyler Bey / Christian Wood | John Wall / Daniel Theis / Jalen Green / Christian Wood / David Nwaba | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 24 | **Oklahoma City Thunder** | Shai Gilgeous-A | Theo Maledon | Shai Gilgeous-A / Luguentz Dort / Aleksej Pokusevski / Darius Bazley / Derrick Favors | Shai Gilgeous-A / Mike Muscala / Luguentz Dort / Derrick Favors / Ty Jerome | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 25 | **San Antonio Spurs** | Bryn Forbes | Keldon Johnson | Lonzo Ball / Lonnie Walker IV / Keldon Johnson / Thaddeus Young / Jakob Poeltl | Cory Joseph / Thaddeus Young / Keldon Johnson / Lonzo Ball / Devin Vassell | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 26 | **Phoenix Suns** | Chris Paul | Devin Booker | Chris Paul / Devin Booker / Mikal Bridges / Jae Crowder / Deandre Ayton | Chris Paul / Deandre Ayton / Devin Booker / Mikal Bridges / Jae Crowder | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 27 | **Minnesota Timberwolves** | Karl-Antho Towns | Malik Beasley | Patrick Beverley / Anthony Edwards / Torrey Craig / Taurean Prince / Karl-Antho Towns | Patrick Beverley / Karl-Antho Towns / Anthony Edwards / Naz Reid / Torrey Craig | FEED_THE_POST + NEUTRAL_DEFENSE_FOCUS |
| 28 | **Portland Trail Blazers** | Damian Lillard | C.J. McCollum | Damian Lillard / Moses Moody / Norman Powell / Larry Nance Jr. / Jusuf Nurkic | Damian Lillard / Jusuf Nurkic / Norman Powell / C.J. McCollum / Damion Lee | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |
| 29 | **Golden State Warriors** | Stephen Curry | Klay Thompson | Stephen Curry / Klay Thompson / Andrew Wiggins / Draymond Green / James Wiseman | Stephen Curry / Draymond Green / Klay Thompson / Otto Porter / Andrew Wiggins | GET_TO_BASKET + NEUTRAL_DEFENSE_FOCUS |
| 31 | **Charlotte Hornets** | Terry Rozier III | LaMelo Ball | LaMelo Ball / Terry Rozier III / Gordon Hayward / Miles Bridges / Kai Jones | Terry Rozier III / Miles Bridges / Gordon Hayward / LaMelo Ball / Will Barton | PICK_AND_ROLL_OFFENSE + NEUTRAL_DEFENSE_FOCUS |

---

## 三、分球队详细战力与轮换决策档案

### Philadelphia 76ers (PHI)
- **进攻轴心**：第一核心【Joel Embiid】，第二核心【Seth Curry】
- **最优首发阵容**：Ben Simmons / Shake Milton / Danny Green / Tobias Harris / Joel Embiid
- **第四节终结阵容**：Seth Curry / Joel Embiid / Tobias Harris / Danny Green / Ben Simmons
- **240 分钟轮换方案**：
  - 轮换名单：Ben Simmons (35分), Danny Green (30分), Tobias Harris (32分), Joel Embiid (37分), Andre Drummond (20分), Matisse Thybulle (26分), Shake Milton (28分), Jaden Springer (18分), Grant Riller (14分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Seth Curry**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Danny Green**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Tobias Harris**：当前 75 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Joel Embiid**：当前 85 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Andre Drummond**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Matisse Thybulle**：当前 40 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Shake Milton**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Tyrese Maxey**：当前 88 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Furkan Korkmaz**：当前 93 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Isaiah Joe**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jaden Springer**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Grant Riller**：当前 50 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Milwaukee Bucks (MIL)
- **进攻轴心**：第一核心【Khris Middleton】，第二核心【Giannis Antetokoun】
- **最优首发阵容**：Jrue Holiday / Donte DiVincenzo / Khris Middleton / Giannis Antetokoun / Bobby Portis Jr.
- **第四节终结阵容**：Jrue Holiday / Giannis Antetokoun / Khris Middleton / Brook Lopez / Bobby Portis Jr.
- **240 分钟轮换方案**：
  - 轮换名单：Jrue Holiday (35分), Donte DiVincenzo (28分), Khris Middleton (32分), Giannis Antetokoun (37分), Brook Lopez (26分), Bobby Portis Jr. (30分), Jordan Nwora (20分), Grayson Allen (14分), P.J. Dozier (18分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Jrue Holiday**：当前 75 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Giannis Antetokoun**：当前 86 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Brook Lopez**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Pat Connaughto**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Bobby Portis Jr.**：当前 35 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jordan Nwora**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Grayson Allen**：当前 95 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **P.J. Dozier**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_TO_BASKET
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: LIMIT_PERIMETER_SHOTS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: RUN_IN_TRANSITION
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Washington Wizards (WAS)
- **进攻轴心**：第一核心【Bradley Beal】，第二核心【Cassius Winston】
- **最优首发阵容**：Raul Neto / Bradley Beal / Kyle Kuzma / Rui Hachimura / Daniel Gafford
- **第四节终结阵容**：Bradley Beal / Davis Bertans / Raul Neto / Rui Hachimura / Kyle Kuzma
- **240 分钟轮换方案**：
  - 轮换名单：Bradley Beal (37分), Deni Avdija (26分), Rui Hachimura (32分), Kyle Kuzma (35分), Daniel Gafford (30分), Corey Kispert (14分), Davis Bertans (18分), Raul Neto (28分), Anthony Gill (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Spencer Dinwiddie**：当前 88 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Rui Hachimura**：当前 76 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Thomas Bryant**：当前 79 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kentavious Caldwell-P**：当前 84 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kyle Kuzma**：当前 75 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Daniel Gafford**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Corey Kispert**：当前 65 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Davis Bertans**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Aaron Holiday**：当前 87 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Raul Neto**：当前 80 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Anthony Gill**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_TO_BASKET
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Chicago Bulls (CHI)
- **进攻轴心**：第一核心【Zach LaVine】，第二核心【Nikola Vucevic】
- **最优首发阵容**：T.J. McConnell / Zach LaVine / DeMar DeRozan / Patrick Williams / Nikola Vucevic
- **第四节终结阵容**：T.J. McConnell / Nikola Vucevic / Zach LaVine / DeMar DeRozan / Coby White
- **240 分钟轮换方案**：
  - 轮换名单：Zach LaVine (37分), DeMar DeRozan (28分), Patrick Williams (35分), Nikola Vucevic (30分), Coby White (26分), Javonte Green (20分), Ayo Dosunmu (14分), T.J. Warren (18分), T.J. McConnell (32分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Zach LaVine**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Patrick Williams**：当前 78 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Ayo Dosunmu**：当前 70 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **T.J. McConnell**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Cleveland Cavaliers (CLE)
- **进攻轴心**：第一核心【Darius Garland】，第二核心【Caris LeVert】
- **最优首发阵容**：Darius Garland / Caris LeVert / Justin Holiday / Evan Mobley / Jarrett Allen
- **第四节终结阵容**：Caris LeVert / Jarrett Allen / Darius Garland / Kevin Love / Collin Sexton
- **240 分钟轮换方案**：
  - 轮换名单：Darius Garland (28分), Collin Sexton (18分), Jarrett Allen (30分), Evan Mobley (35分), Kevin Love (26分), Ricky Rubio (14分), Dylan Windler (20分), Caris LeVert (37分), Justin Holiday (32分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Isaac Okoro**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jarrett Allen**：当前 70 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Evan Mobley**：当前 40 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Kevin Love**：当前 40 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Ricky Rubio**：当前 85 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Tacko Fall**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Caris LeVert**：当前 85 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Justin Holiday**：当前 40 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Boston Celtics (BOS)
- **进攻轴心**：第一核心【Jaylen Brown】，第二核心【Jayson Tatum】
- **最优首发阵容**：Marcus Smart / Jaylen Brown / Jayson Tatum / Al Horford / Robert Williams
- **第四节终结阵容**：Jaylen Brown / Al Horford / Jayson Tatum / Marcus Smart / Josh Richardson
- **240 分钟轮换方案**：
  - 轮换名单：Dennis Schroder (18分), Marcus Smart (32分), Jaylen Brown (35分), Jayson Tatum (37分), Al Horford (30分), Robert Williams (28分), Josh Richardson (26分), Grant Williams (20分), Kris Dunn (14分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Marcus Smart**：当前 40 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jaylen Brown**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Al Horford**：当前 46 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Robert Williams**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Josh Richardson**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Grant Williams**：当前 79 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Payton Pritchard**：当前 79 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Aaron Nesmith**：当前 79 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kris Dunn**：当前 25 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Romeo Langford**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Los Angeles Clippers (LAC)
- **进攻轴心**：第一核心【Paul George】，第二核心【Kawhi Leonard】
- **最优首发阵容**：Eric Bledsoe / Paul George / Kawhi Leonard / Marcus Morris Sr. / Serge Ibaka
- **第四节终结阵容**：Paul George / Serge Ibaka / Kawhi Leonard / Marcus Morris Sr. / Reggie Jackson
- **240 分钟轮换方案**：
  - 轮换名单：Reggie Jackson (20分), Paul George (35分), Kawhi Leonard (37分), Marcus Morris Sr. (32分), Serge Ibaka (30分), Eric Bledsoe (28分), Jason Preston (18分), Brandon Boston Jr. (26分), Jay Scrubb (14分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Paul George**：当前 93 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Marcus Morris Sr.**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Serge Ibaka**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Eric Bledsoe**：当前 78 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Luke Kennard**：当前 88 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Terance Mann**：当前 79 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jason Preston**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Jevon Carter**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jay Scrubb**：当前 65 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Memphis Grizzlies (MEM)
- **进攻轴心**：第一核心【Desmond Bane】，第二核心【Kyle Anderson】
- **最优首发阵容**：Ja Morant / Dillon Brooks / Kyle Anderson / Jaren Jackson Jr / Xavier Tillman
- **第四节终结阵容**：Dillon Brooks / Jaren Jackson Jr / Kyle Anderson / De'Anthony Melton / Ja Morant
- **240 分钟轮换方案**：
  - 轮换名单：Ja Morant (28分), Dillon Brooks (32分), Kyle Anderson (37分), Jaren Jackson Jr (35分), Brandon Clarke (26分), Desmond Bane (18分), Xavier Tillman (30分), Ziaire Williams (14分), De'Anthony Melton (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Kyle Anderson**：当前 65 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Jaren Jackson Jr**：当前 85 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Brandon Clarke**：当前 44 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Desmond Bane**：当前 79 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Xavier Tillman**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Ziaire Williams**：当前 50 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Tyus Jones**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Juan Hernangome**：当前 89 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Sam Merrill**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Atlanta Hawks (ATL)
- **进攻轴心**：第一核心【Trae Young】，第二核心【Bogdan Bogdanovic】
- **最优首发阵容**：Trae Young / Bogdan Bogdanovic / De'Andre Hunter / John Collins / Clint Capela
- **第四节终结阵容**：Bogdan Bogdanovic / John Collins / De'Andre Hunter / Danilo Gallinari / Skylar Mays
- **240 分钟轮换方案**：
  - 轮换名单：Trae Young (28分), Bogdan Bogdanovic (32分), De'Andre Hunter (37分), John Collins (30分), Clint Capela (35分), Danilo Gallinari (18分), Kevin Huerter (14分), Jalen Johnson (20分), Skylar Mays (26分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Bogdan Bogdanovic**：当前 73 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **De'Andre Hunter**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **John Collins**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Clint Capela**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Danilo Gallinari**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Cameron Reddish**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kevin Huerter**：当前 96 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Delon Wright**：当前 93 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jalen Johnson**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Skylar Mays**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Miami Heat (MIA)
- **进攻轴心**：第一核心【Kyle Lowry】，第二核心【Eric Gordon】
- **最优首发阵容**：Kyle Lowry / Eric Gordon / Jimmy Butler / Isaiah Todd / Bam Adebayo
- **第四节终结阵容**：Kyle Lowry / Bam Adebayo / Jimmy Butler / Eric Gordon / Victor Oladipo
- **240 分钟轮换方案**：
  - 轮换名单：Kyle Lowry (32分), Jimmy Butler (35分), P.J. Tucker (18分), Bam Adebayo (37分), Tyler Herro (20分), Victor Oladipo (26分), Markieff Morris (14分), Eric Gordon (30分), Isaiah Todd (28分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Kyle Lowry**：当前 80 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jimmy Butler**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **P.J. Tucker**：当前 79 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Bam Adebayo**：当前 40 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Max Strus**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Markieff Morris**：当前 45 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Gabe Vincent**：当前 86 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Eric Gordon**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Isaiah Todd**：当前 70 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### New Orleans Pelicans (NOP)
- **进攻轴心**：第一核心【Brandon Ingram】，第二核心【Zion Williamson】
- **最优首发阵容**：Tomas Satoransky / Buddy Hield / Brandon Ingram / Zion Williamson / Jonas Valanciuna
- **第四节终结阵容**：Devonte Graham / Jonas Valanciuna / Brandon Ingram / Tomas Satoransky / Buddy Hield
- **240 分钟轮换方案**：
  - 轮换名单：Brandon Ingram (35分), Zion Williamson (37分), Jonas Valanciuna (32分), Tomas Satoransky (28分), Nickeil Alexander- (26分), Naji Marshall (14分), Trey Murphy (20分), Herbert Jones (18分), Buddy Hield (30分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Devonte Graham**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Brandon Ingram**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Zion Williamson**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Jonas Valanciuna**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Tomas Satoransky**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Garrett Temple**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Naji Marshall**：当前 73 -> 目标 73（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Trey Murphy**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Herbert Jones**：当前 40 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Utah Jazz (UTA)
- **进攻轴心**：第一核心【Donovan Mitchell】，第二核心【Joe Ingles】
- **最优首发阵容**：Mike Conley / Donovan Mitchell / Joe Ingles / Eric Paschall / Rudy Gobert
- **第四节终结阵容**：Donovan Mitchell / Royce O'Neale / Mike Conley / Joe Ingles / Bojan Bogdanovic
- **240 分钟轮换方案**：
  - 轮换名单：Mike Conley (30分), Donovan Mitchell (37分), Royce O'Neale (18分), Bojan Bogdanovic (20分), Rudy Gobert (32分), Jordan Clarkson (14分), Joe Ingles (35分), Rudy Gay (26分), Eric Paschall (28分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Mike Conley**：当前 70 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jordan Clarkson**：当前 95 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Joe Ingles**：当前 30 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Rudy Gay**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Eric Paschall**：当前 45 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Miye Oni**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Sacramento Kings (SAC)
- **进攻轴心**：第一核心【De'Aaron Fox】，第二核心【Domantas Sabonis】
- **最优首发阵容**：De'Aaron Fox / Jahmi'us Ramsey / Jeremy Lamb / Domantas Sabonis / Richaun Holmes
- **第四节终结阵容**：De'Aaron Fox / Richaun Holmes / Jeremy Lamb / Harrison Barnes / Domantas Sabonis
- **240 分钟轮换方案**：
  - 轮换名单：De'Aaron Fox (35分), Harrison Barnes (18分), Marvin Bagley III (14分), Richaun Holmes (30分), Davion Mitchell (26分), Terence Davis (20分), Jahmi'us Ramsey (28分), Domantas Sabonis (37分), Jeremy Lamb (32分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **De'Aaron Fox**：当前 50 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Harrison Barnes**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Marvin Bagley III**：当前 45 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Richaun Holmes**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Davion Mitchell**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Terence Davis**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Chimezie Metu**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Robert Woodard II**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jeremy Lamb**：当前 70 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### New York Knicks (NYK)
- **进攻轴心**：第一核心【Julius Randle】，第二核心【Evan Fournier】
- **最优首发阵容**：Derrick Rose / Evan Fournier / R.J. Barrett / Julius Randle / DeMarcus Cousins
- **第四节终结阵容**：Immanuel Quickley / Julius Randle / Alec Burks / Derrick Rose / R.J. Barrett
- **240 分钟轮换方案**：
  - 轮换名单：Evan Fournier (28分), R.J. Barrett (32分), Julius Randle (37分), Mitchell Robinson (20分), Derrick Rose (30分), Alec Burks (26分), Miles McBride (14分), Talen Horton-Tuc (18分), DeMarcus Cousins (35分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Kemba Walker**：当前 93 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Julius Randle**：当前 75 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Derrick Rose**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Alec Burks**：当前 62 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Immanuel Quickley**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kevin Knox II**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Miles McBride**：当前 60 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Talen Horton-Tuc**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **DeMarcus Cousins**：当前 35 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Sterling Brown**：当前 83 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_SHOOTERS_OPEN
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Los Angeles Lakers (LAL)
- **进攻轴心**：第一核心【LeBron James】，第二核心【Kendrick Nunn】
- **最优首发阵容**：Russell Westbrook / Malik Monk / LeBron James / Anthony Davis / Nerlens Noel
- **第四节终结阵容**：Russell Westbrook / Anthony Davis / LeBron James / Kendrick Nunn / Carmelo Anthony
- **240 分钟轮换方案**：
  - 轮换名单：Russell Westbrook (32分), Malik Monk (28分), LeBron James (35分), Anthony Davis (37分), Carmelo Anthony (26分), Trevor Ariza (18分), Kendrick Nunn (14分), Kent Bazemore (20分), Nerlens Noel (30分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Russell Westbrook**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Anthony Davis**：当前 83 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Carmelo Anthony**：当前 25 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Kendrick Nunn**：当前 65 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Kent Bazemore**：当前 58 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Nerlens Noel**：当前 35 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_TO_BASKET
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: RUN_IN_TRANSITION
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Orlando Magic (ORL)
- **进攻轴心**：第一核心【Cole Anthony】，第二核心【Terrence Ross】
- **最优首发阵容**：Cole Anthony / R.J. Hampton / Franz Wagner / Chuma Okeke / Wendell Carter Jr.
- **第四节终结阵容**：Jalen Suggs / Wendell Carter Jr. / Franz Wagner / Chuma Okeke / Cole Anthony
- **240 分钟轮换方案**：
  - 轮换名单：Jalen Suggs (14分), Jonathan Isaac (26分), Chuma Okeke (37分), Wendell Carter Jr. (30分), Terrence Ross (18分), Cole Anthony (32分), Franz Wagner (35分), R.J. Hampton (28分), Ignas Brazdeikis (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Jalen Suggs**：当前 50 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Jonathan Isaac**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Chuma Okeke**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Wendell Carter Jr.**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Gary Harris**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Franz Wagner**：当前 50 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **R.J. Hampton**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **E'Twaun Moore**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Ignas Brazdeikis**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Dallas Mavericks (DAL)
- **进攻轴心**：第一核心【Luka Doncic】，第二核心【Jalen Brunson】
- **最优首发阵容**：Luka Doncic / Tim Hardaway J / Reggie Bullock / Maxi Kleber / Kristaps Porzingis
- **第四节终结阵容**：Luka Doncic / Kristaps Porzingis / Reggie Bullock / Jalen Brunson / Maxi Kleber
- **240 分钟轮换方案**：
  - 轮换名单：Luka Doncic (37分), Tim Hardaway J (28分), Dorian Finney-Smi (20分), Kristaps Porzingis (35分), Maxi Kleber (30分), Reggie Bullock (32分), Willie Cauley-Ste (14分), Jalen Brunson (26分), Taj Gibson (18分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Kristaps Porzingis**：当前 50 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Maxi Kleber**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Reggie Bullock**：当前 70 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Willie Cauley-Ste**：当前 51 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Jalen Brunson**：当前 35 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Moses Brown**：当前 89 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Trey Burke**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Taj Gibson**：当前 56 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_SHOOTERS_OPEN
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Brooklyn Nets (BKN)
- **进攻轴心**：第一核心【Kevin Durant】，第二核心【Kyrie Irving】
- **最优首发阵容**：Kyrie Irving / James Harden / Joe Harris / Kevin Durant / LaMarcus Aldridge
- **第四节终结阵容**：James Harden / Kevin Durant / Kyrie Irving / Joe Harris / LaMarcus Aldridge
- **240 分钟轮换方案**：
  - 轮换名单：James Harden (35分), Kyrie Irving (32分), Joe Harris (30分), Kevin Durant (37分), Blake Griffin (14分), Paul Millsap (20分), LaMarcus Aldridge (28分), Nicolas Claxton (18分), Nicolas Batum (26分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Kyrie Irving**：当前 80 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Joe Harris**：当前 82 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Blake Griffin**：当前 79 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Paul Millsap**：当前 45 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **LaMarcus Aldridge**：当前 25 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Patrick Mills**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Bruce Brown**：当前 91 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Nicolas Claxton**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Nicolas Batum**：当前 78 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_SHOOTERS_OPEN
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Denver Nuggets (DEN)
- **进攻轴心**：第一核心【Nikola Jokic】，第二核心【Jamal Murray】
- **最优首发阵容**：Jamal Murray / Austin Rivers / Michael Porter Jr. / Aaron Gordon / Nikola Jokic
- **第四节终结阵容**：Jamal Murray / Nikola Jokic / Michael Porter Jr. / Mason Plumlee / JaMychal Green
- **240 分钟轮换方案**：
  - 轮换名单：Jamal Murray (32分), Michael Porter Jr. (35分), Aaron Gordon (30分), Nikola Jokic (37分), JaMychal Green (18分), Jeff Green (26分), Austin Rivers (28分), George Hill (14分), Mason Plumlee (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Michael Porter Jr.**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Aaron Gordon**：当前 66 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Monte Morris**：当前 79 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Facundo Campazzo**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **JaMychal Green**：当前 76 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Jeff Green**：当前 65 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **George Hill**：当前 76 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Mason Plumlee**：当前 55 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Indiana Pacers (IND)
- **进攻轴心**：第一核心【Tyrese Haliburton】，第二核心【Dejounte Murray】
- **最优首发阵容**：Tyrese Haliburton / Josh Hart / Robert Covington / Pascal Siakam / Myles Turner
- **第四节终结阵容**：Tyrese Haliburton / Pascal Siakam / Dejounte Murray / Myles Turner / Derrick White
- **240 分钟轮换方案**：
  - 轮换名单：Myles Turner (32分), Tyrese Haliburton (37分), Pascal Siakam (35分), Robert Covington (30分), Josh Hart (28分), Dejounte Murray (26分), Derrick White (20分), Keita Bates-Diop (18分), Jarred Vanderbilt (14分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Myles Turner**：当前 25 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Tyrese Haliburton**：当前 25 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Pascal Siakam**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Lauri Markkanen**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Robert Covington**：当前 84 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **C.J. Elleby**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Dejounte Murray**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Keita Bates-Diop**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Jarred Vanderbilt**：当前 75 -> 目标 75（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Detroit Pistons (DET)
- **进攻轴心**：第一核心【Cade Cunningham】，第二核心【Jerami Grant】
- **最优首发阵容**：Cade Cunningham / Josh Jackson / Saddiq Bey / Jerami Grant / Isaiah Stewart
- **第四节终结阵容**：Cade Cunningham / Kelly Olynyk / Jerami Grant / Saddiq Bey / Isaiah Stewart
- **240 分钟轮换方案**：
  - 轮换名单：Cade Cunningham (37分), Saddiq Bey (30分), Jerami Grant (35分), Kelly Olynyk (26分), Josh Jackson (32分), Isaiah Stewart (28分), Saben Lee (18分), Rodney McGruder (14分), Chris Duarte (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Cade Cunningham**：当前 85 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Jerami Grant**：当前 65 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Kelly Olynyk**：当前 65 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Josh Jackson**：当前 75 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Frank Jackson**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Isaiah Stewart**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Rodney McGruder**：当前 95 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Kelan Martin**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Edmond Sumner**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Toronto Raptors (TOR)
- **进攻轴心**：第一核心【Malcolm Brogdon】，第二核心【Fred VanVleet】
- **最优首发阵容**：Malcolm Brogdon / Fred VanVleet / OG Anunoby / Scottie Barnes / Precious Achiuwa
- **第四节终结阵容**：Fred VanVleet / Chris Boucher / Malcolm Brogdon / OG Anunoby / Goran Dragic
- **240 分钟轮换方案**：
  - 轮换名单：Goran Dragic (18分), Fred VanVleet (30分), OG Anunoby (35分), Scottie Barnes (32分), Chris Boucher (26分), Gary Trent Jr. (20分), Precious Achiuwa (28分), Yuta Watanabe (14分), Malcolm Brogdon (37分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Goran Dragic**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **OG Anunoby**：当前 55 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Scottie Barnes**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Chris Boucher**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Precious Achiuwa**：当前 45 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Sviatoslav Mykhailiuk**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Yuta Watanabe**：当前 98 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Malachi Flynn**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Freddie Gillespie**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Malcolm Brogdon**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Maurice Harkless**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_TO_BASKET
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Houston Rockets (HOU)
- **进攻轴心**：第一核心【Jalen Green】，第二核心【Duncan Robinson】
- **最优首发阵容**：John Wall / Jalen Green / David Nwaba / Tyler Bey / Christian Wood
- **第四节终结阵容**：John Wall / Daniel Theis / Jalen Green / Christian Wood / David Nwaba
- **240 分钟轮换方案**：
  - 轮换名单：John Wall (30分), Jalen Green (35分), Jae'Sean Tate (14分), Daniel Theis (20分), Kenyon Martin Jr. (18分), David Nwaba (28分), Josh Christophe (26分), Christian Wood (37分), Tyler Bey (32分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **John Wall**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jalen Green**：当前 85 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Jae'Sean Tate**：当前 90 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Daniel Theis**：当前 40 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Kevin Porter Jr.**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **D.J. Augustin**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **David Nwaba**：当前 75 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Josh Christophe**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Christian Wood**：当前 75 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Duncan Robinson**：当前 84 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Tyler Bey**：当前 35 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Oklahoma City Thunder (OKC)
- **进攻轴心**：第一核心【Shai Gilgeous-A】，第二核心【Theo Maledon】
- **最优首发阵容**：Shai Gilgeous-A / Luguentz Dort / Aleksej Pokusevski / Darius Bazley / Derrick Favors
- **第四节终结阵容**：Shai Gilgeous-A / Mike Muscala / Luguentz Dort / Derrick Favors / Ty Jerome
- **240 分钟轮换方案**：
  - 轮换名单：Shai Gilgeous-A (37分), Luguentz Dort (35分), Aleksej Pokusevski (30分), Darius Bazley (28分), Derrick Favors (32分), Josh Giddey (20分), Kenrich Williams (14分), Tre Mann (26分), Ty Jerome (18分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Shai Gilgeous-A**：当前 80 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Luguentz Dort**：当前 90 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Derrick Favors**：当前 30 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Josh Giddey**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Kenrich Williams**：当前 55 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Tre Mann**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Paul Watson**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### San Antonio Spurs (SAS)
- **进攻轴心**：第一核心【Bryn Forbes】，第二核心【Keldon Johnson】
- **最优首发阵容**：Lonzo Ball / Lonnie Walker IV / Keldon Johnson / Thaddeus Young / Jakob Poeltl
- **第四节终结阵容**：Cory Joseph / Thaddeus Young / Keldon Johnson / Lonzo Ball / Devin Vassell
- **240 分钟轮换方案**：
  - 轮换名单：Keldon Johnson (35分), Thaddeus Young (32分), Jakob Poeltl (28分), Lonnie Walker IV (30分), Devin Vassell (26分), Joshua Primo (14分), Lonzo Ball (37分), Hamidou Diallo (18分), Cory Joseph (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Keldon Johnson**：当前 70 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Thaddeus Young**：当前 25 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jakob Poeltl**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Bryn Forbes**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Devin Vassell**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Joshua Primo**：当前 85 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Cory Joseph**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Phoenix Suns (PHX)
- **进攻轴心**：第一核心【Chris Paul】，第二核心【Devin Booker】
- **最优首发阵容**：Chris Paul / Devin Booker / Mikal Bridges / Jae Crowder / Deandre Ayton
- **第四节终结阵容**：Chris Paul / Deandre Ayton / Devin Booker / Mikal Bridges / Jae Crowder
- **240 分钟轮换方案**：
  - 轮换名单：Chris Paul (35分), Devin Booker (30分), Mikal Bridges (37分), Jae Crowder (32分), Deandre Ayton (28分), Cameron Johnson (26分), Cameron Payne (20分), Abdel Nader (14分), Chandler Hutchison (18分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Chris Paul**：当前 60 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Mikal Bridges**：当前 60 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Jae Crowder**：当前 76 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Cameron Johnson**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Cameron Payne**：当前 66 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Landry Shamet**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Elfrid Payton**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Abdel Nader**：当前 78 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Chandler Hutchison**：当前 56 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Minnesota Timberwolves (MIN)
- **进攻轴心**：第一核心【Karl-Antho Towns】，第二核心【Malik Beasley】
- **最优首发阵容**：Patrick Beverley / Anthony Edwards / Torrey Craig / Taurean Prince / Karl-Antho Towns
- **第四节终结阵容**：Patrick Beverley / Karl-Antho Towns / Anthony Edwards / Naz Reid / Torrey Craig
- **240 分钟轮换方案**：
  - 轮换名单：D'Angelo Russell (14分), Malik Beasley (18分), Anthony Edwards (35分), Karl-Antho Towns (37分), Naz Reid (26分), Patrick Beverley (30分), Taurean Prince (28分), James Ennis (20分), Torrey Craig (32分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **D'Angelo Russell**：当前 90 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Jaden McDaniels**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Karl-Antho Towns**：当前 60 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Naz Reid**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Josh Okogie**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Patrick Beverley**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Taurean Prince**：当前 65 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jaylen Nowell**：当前 80 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Leandro Bolmaro**：当前 85 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **James Ennis**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Torrey Craig**：当前 80 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: FEED_THE_POST
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 75

### Portland Trail Blazers (POR)
- **进攻轴心**：第一核心【Damian Lillard】，第二核心【C.J. McCollum】
- **最优首发阵容**：Damian Lillard / Moses Moody / Norman Powell / Larry Nance Jr. / Jusuf Nurkic
- **第四节终结阵容**：Damian Lillard / Jusuf Nurkic / Norman Powell / C.J. McCollum / Damion Lee
- **240 分钟轮换方案**：
  - 轮换名单：Damian Lillard (35分), C.J. McCollum (26分), Norman Powell (28分), Jusuf Nurkic (30分), Larry Nance Jr. (37分), Nassir Little (18分), Dennis Smith Jr. (14分), Moses Moody (32分), Damion Lee (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Jusuf Nurkic**：当前 80 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Larry Nance Jr.**：当前 50 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Nassir Little**：当前 60 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Dennis Smith Jr.**：当前 45 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Oshae Brissett**：当前 95 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Cedi Osman**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Moses Moody**：当前 75 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Damion Lee**：当前 70 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: PATIENT_OFFENSE
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Golden State Warriors (GSW)
- **进攻轴心**：第一核心【Stephen Curry】，第二核心【Klay Thompson】
- **最优首发阵容**：Stephen Curry / Klay Thompson / Andrew Wiggins / Draymond Green / James Wiseman
- **第四节终结阵容**：Stephen Curry / Draymond Green / Klay Thompson / Otto Porter / Andrew Wiggins
- **240 分钟轮换方案**：
  - 轮换名单：Stephen Curry (35分), Klay Thompson (37分), Andrew Wiggins (32分), Draymond Green (30分), James Wiseman (28分), Andre Iguodala (14分), Otto Porter (26分), Jonathan Kuminga (18分), Juan Toscano (20分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **Klay Thompson**：当前 65 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Andrew Wiggins**：当前 78 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Draymond Green**：当前 60 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **James Wiseman**：当前 55 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Andre Iguodala**：当前 40 -> 目标 70（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **Otto Porter**：当前 75 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Jordan Poole**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Jonathan Kuminga**：当前 50 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Juan Toscano**：当前 76 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Anfernee Simons**：当前 96 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Chris Chiozza**：当前 78 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: GET_TO_BASKET
  - `POEOffense2_Tempo`: SHOOT_AT_WILL
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65

### Charlotte Hornets (CHA)
- **进攻轴心**：第一核心【Terry Rozier III】，第二核心【LaMelo Ball】
- **最优首发阵容**：LaMelo Ball / Terry Rozier III / Gordon Hayward / Miles Bridges / Kai Jones
- **第四节终结阵容**：Terry Rozier III / Miles Bridges / Gordon Hayward / LaMelo Ball / Will Barton
- **240 分钟轮换方案**：
  - 轮换名单：LaMelo Ball (37分), Terry Rozier III (32分), Gordon Hayward (35分), P.J. Washington (20分), Miles Bridges (30分), Kelly Oubre Jr. (14分), Kai Jones (28分), J.T. Thor (18分), Will Barton (26分)（合计：240 分钟）
- **重点球员补偿评分 (Intangibles) 调优策略**：
  - **LaMelo Ball**：当前 60 -> 目标 95（BOOST_SUPERSTAR：维持或提升至超巨档位(95+)，确保原版游戏AI锁定35+分钟核心出场）
  - **Miles Bridges**：当前 75 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Kelly Oubre Jr.**：当前 90 -> 目标 76（ADJUST_ROTATION_EDGE：边缘轮换，适度维持在70~75，匹配14~18分钟角色时间）
  - **James Bouknight**：当前 90 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Cody Martin**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Kai Jones**：当前 50 -> 目标 85（BOOST_STARTER：首发主力档位(85+)，确保AI稳定分配30分钟左右首发时间）
  - **Jalen McDaniels**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **Wesley Iwundu**：当前 98 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
  - **J.T. Thor**：当前 45 -> 目标 80（BOOST_KEY_RESERVE：关键轮换微波炉/防守大闸，提升补偿评分至80+以防AI将其压制到板凳）
  - **Vlatko Cancar**：当前 76 -> 目标 40（SUPPRESS_DNP：非计划轮换球员，下调补偿评分至40，防止AI擅自上调其出场时间）
- **教练战术配置 (POE)**：
  - `POEOffense`: PICK_AND_ROLL_OFFENSE
  - `POEOffense2_Tempo`: NEUTRAL_OFFENSE_TEMPO
  - `POEOffense3_Rebound`: LIMIT_TRANSITION
  - `POEDefense`: NEUTRAL_DEFENSE_FOCUS
  - `POEDefense2_Physicality`: NEUTRAL_DEFENSE_TEMPO
  - `POEDefense3_Rebound`: CRASH_DEFENSIVE_BOARDS
  - `BenchDepth`: 9
  - `RunPlayTendency`: 65
