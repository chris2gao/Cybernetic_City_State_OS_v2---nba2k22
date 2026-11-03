# 操作覆盖清单（静态基线与逐例实测分开）

下表保留PR14静态能力基线。Issue15实测结果按输入记在[data/native_live_validation.json](data/native_live_validation.json)和[VALIDATION_RESULTS.md](VALIDATION_RESULTS.md)，Registry.get/list均加载该证据层。角色模型的取值与执行入口见[机制说明](ROLE_MODEL_MECHANISM_GUIDE.md)。`CALL_LOGIC_RECOVERED`本身不表示实测通过，Reader仍为子集覆盖。

新增默认交易入口：`TRADE_EXECUTE_AGREED_PACKAGE`，输入`team_a,team_b,players_a,players_b,picks_a,picks_b`，handler=`trade.agreed`。外部GM决策完成后，私有提案直接调用原生Process；不调用外围FullCheck。原生`trade.context`为`pointer()` RVA0xbaa7e0；`trade.process`为`int(pointer,pointer,pointer)` RVA0x12e93b0，分别接收提案、原生上下文、私有int32输出。旧交易动作仍指原完整检查路径，不能与新增直接路径混为一个实测结果。

| 动作ID | 域 | 成熟度 | 输入键 | 实现/缺口 |
|---|---|---|---|---|
| TRADE_PLAYERS | D01 | PRIOR_LIVE_SUCCESS | team_a, team_b, players_a, players_b, picks_a, picks_b | trade.players |
| TRADE_PICKS | D01 | CALL_LOGIC_RECOVERED | team_a, team_b, players_a, players_b, picks_a, picks_b | trade.assets |
| TRADE_MIXED_ASSETS | D01 | CALL_LOGIC_RECOVERED | team_a, team_b, players_a, players_b, picks_a, picks_b | trade.assets |
| TRADE_VALIDATE_COMMIT | D01 | PRIOR_LIVE_SUCCESS | team_a, team_b, players_a, players_b, picks_a, picks_b | trade.players |
| SIGN_FREE_AGENT | D02 | PARTIAL_BINDING | team_id, player_id, contract | Private proposal init/enums/flags and status handling need static closure; no automatic wage generation |
| RE_SIGN_PLAYER | D02 | PARTIAL_BINDING | team_id, player_id, contract | Extension signing type and eligible phase/counterparty status unresolved |
| RELEASE_WAIVE_PLAYER | D02 | PARTIAL_BINDING | team_id, player_id, waiver_parameters | Eight-argument waiver service found; flags and public wrapper not closed; no guessed bypass |
| CONTRACT_OPTION_ACTION | D02 | PARTIAL_BINDING | team_id, player_id, option_decision | Need native option-marking setter before ProcessMarkedOptions; do not edit option memory directly |
| PLAYER_SET_ATTRIBUTE | D03 | PARTIAL_BINDING | player_id, field_id, value | Native editor flush0x141f880 reaches parent/subobject copies and refresh, but independent attribute/tendency/badge/PlayType field apply and child ownership are not restored |
| PLAYER_SET_TENDENCY | D03 | PARTIAL_BINDING | player_id, field_id, value | Native editor flush0x141f880 reaches parent/subobject copies and refresh, but independent attribute/tendency/badge/PlayType field apply and child ownership are not restored |
| PLAYER_SET_BADGE | D03 | PARTIAL_BINDING | player_id, field_id, value | Native editor flush0x141f880 reaches parent/subobject copies and refresh, but independent attribute/tendency/badge/PlayType field apply and child ownership are not restored |
| PLAYER_SET_PLAY_TYPES_1_TO_4 | D03 | PARTIAL_BINDING | player_id, slot_values | Native editor flush0x141f880 reaches parent/subobject copies and refresh, but independent attribute/tendency/badge/PlayType field apply and child ownership are not restored |
| STAFF_SET_ATTRIBUTE | D03 | REFERENCE_ONLY | staff_id, field_id, value | Staff/Coach raw layouts exist but no qualified arbitrary staff-attribute native mutator is recovered |
| PLAYER_SET_EDITABLE_INFO | D03 | PARTIAL_BINDING | player_id, field_id, value | Native editor flush0x141f880 reaches parent/subobject copies and refresh, but independent attribute/tendency/badge/PlayType field apply and child ownership are not restored |
| COACH_APPLY_OFFENSE_POE | D04 | CALL_LOGIC_RECOVERED | team_id, value, expected_before | coach.poe |
| COACH_APPLY_DEFENSE_POE | D04 | PRIOR_LIVE_SUCCESS | team_id, value, expected_before | coach.poe |
| COACH_SET_GAMEPLAN | D04 | PARTIAL_BINDING | team_id, opponent_team_id, gameplan | Creating an opponent plan and applying a projection does not restore full persistent Gameplan commit |
| COACH_ADD_REPLACE_PLAY | D04 | PARTIAL_BINDING | team_id, parameters | Legacy playbook/setting layouts are read/write references only; native add/replace/apply/refresh service or non-null reference lookup is not restored |
| COACH_REPLACE_PLAYBOOK | D04 | PARTIAL_BINDING | team_id, parameters | Legacy playbook/setting layouts are read/write references only; native add/replace/apply/refresh service or non-null reference lookup is not restored |
| COACH_SET_SYSTEM_FREELANCE_ACE | D04 | PARTIAL_BINDING | team_id, parameters | Legacy playbook/setting layouts are read/write references only; native add/replace/apply/refresh service or non-null reference lookup is not restored |
| COACH_SET_ROTATION_POLICY | D04 | CALL_LOGIC_RECOVERED | team_id, settings | coach.settings |
| TEAM_SET_ROSTER_ASSIGNMENT | D05 | NOT_FOUND_WITH_SEARCH_SCOPE | team_id, parameters | Bounded named-Setter searches found only unrelated MyTEAM/world/roster-file callers or lower-level ownership helpers, not this complete MyLEAGUE transaction; do not replace with a raw field write |
| TEAM_SET_STARTERS | D05 | NOT_FOUND_WITH_SEARCH_SCOPE | team_id, parameters | Bounded named-Setter searches found only unrelated MyTEAM/world/roster-file callers or lower-level ownership helpers, not this complete MyLEAGUE transaction; do not replace with a raw field write |
| TEAM_SET_MINUTES_ROTATION | D05 | NOT_FOUND_WITH_SEARCH_SCOPE | team_id, parameters | Bounded named-Setter searches found only unrelated MyTEAM/world/roster-file callers or lower-level ownership helpers, not this complete MyLEAGUE transaction; do not replace with a raw field write |
| TEAM_SET_PLAYER_ROLE_POSITION | D05 | NOT_FOUND_WITH_SEARCH_SCOPE | team_id, parameters | Bounded named-Setter searches found only unrelated MyTEAM/world/roster-file callers or lower-level ownership helpers, not this complete MyLEAGUE transaction; do not replace with a raw field write |
| TEAM_MANAGE_STAFF | D05 | PARTIAL_BINDING | team_id, parameters | Staff offer struct recovered; hire/fire lifecycle and full ABI incomplete |
| TEAM_OTHER_SUPPORTED_OPERATIONS | D05 | PARTIAL_BINDING | team_id, parameters | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| DRAFT_SELECT_PROSPECT | D06 | CALL_LOGIC_RECOVERED | team_id, player_id, pick_id | draft.select |
| DRAFT_PICK_RIGHTS_ACTION | D06 | PARTIAL_BINDING | team_id, parameters | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| DRAFT_STAGE_REQUIRED_CONTEXT | D06 | CALL_LOGIC_RECOVERED |  | draft.context |
| TRAIN_TEAM_SET_SCHEDULE | D07 | CALL_LOGIC_RECOVERED | team_id, date, training | training.team_date |
| TRAIN_TEAM_SET_INTENSITY | D07 | CALL_LOGIC_RECOVERED | team_id, date, value | training.intensity |
| TRAIN_PLAYER_SET_FOCUS | D07 | PARTIAL_BINDING | team_id, parameters | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| TRAIN_PLAYER_MENTOR_ASSIGNMENT | D07 | PARTIAL_BINDING | team_id, mentor_player_id, mentee_player_ids, badge_ids | Manager/list/UID mapping and complete arguments unresolved |
| READ_LEAGUE_SETTINGS_AND_CALENDAR | D08 | PARTIAL_BINDING | team_id, player_id, season_id, limit | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| READ_TEAM_ROSTER_ROTATION_FINANCE | D08 | PARTIAL_BINDING | team_id | read.team |
| READ_PLAYER_PROFILE_ATTRIBUTES_TENDENCIES_BADGES | D08 | PARTIAL_BINDING | player_id | read.player |
| READ_PLAYER_MATCH_SEASON_CAREER_STATS | D08 | PARTIAL_BINDING | team_id, player_id, season_id, limit | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| READ_COACH_STAFF_GAMEPLAN_TRAINING | D08 | PARTIAL_BINDING | team_id | read.coach |
| READ_GAMES_STANDINGS_AWARDS_HISTORY | D08 | PARTIAL_BINDING | team_id, player_id, season_id, limit | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| READ_DRAFT_CLASS_PICKS_AND_SCOUT_REPORTS | D08 | PARTIAL_BINDING | team_id, player_id, season_id, limit | No complete PC22 logical entity/parameter/commit binding for this exact action; see domain source leads |
| SCOUT_LIST_DRAFT_PROSPECTS | D09 | CALL_LOGIC_RECOVERED | limit | scout.list |
| SCOUT_READ_PROSPECT_INFO | D09 | PARTIAL_BINDING | player_id, team_id | scout.info |
| SCOUT_ASSIGN_TARGETS | D09 | CALL_LOGIC_RECOVERED | team_id, player_ids, priority_raw | scout.append_goal |
| SCOUT_READ_PROGRESS_REPORT | D09 | PARTIAL_BINDING | team_id, player_id | scout.progress |
| SCOUT_READ_STAFF_CAPACITY_SCHEDULE | D09 | PARTIAL_BINDING | team_id | scout.budget |
| COACH_ENSURE_OPPONENT_GAMEPLAN | D04 | CALL_LOGIC_RECOVERED | team_id, opponent_team_id | gameplan.ensure |
| READ_TEAM_ROSTER_BASIC | D08 | CALL_LOGIC_RECOVERED | team_id | read.team |
| READ_COACH_CURRENT | D08 | CALL_LOGIC_RECOVERED | team_id | read.coach |
| SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS | D09 | CALL_LOGIC_RECOVERED | limit | scout.list |
| SCOUT_READ_PROGRESS_RAW | D09 | CALL_LOGIC_RECOVERED | team_id, player_id | scout.progress |
| SCOUT_READ_TRIP_BUDGET | D09 | CALL_LOGIC_RECOVERED | team_id | scout.budget |
| SCOUT_EXECUTE_CURRENT_TRIP | D09 | CALL_LOGIC_RECOVERED | team_id | scout.execute_trip |
| TRADE_MULTI_PLAYER_PACKAGE | D01 | CALL_LOGIC_RECOVERED | team_a, team_b, players_a, players_b, picks_a, picks_b | trade.assets |
| COACH_SET_KNOWN_CURRENT_SETTINGS | D04 | CALL_LOGIC_RECOVERED | team_id, settings | coach.settings |
| SCOUT_SET_EXISTING_GOAL_TARGETS | D09 | CALL_LOGIC_RECOVERED | team_id, player_ids, goal_index | scout.existing_goal |
| READ_CURRENT_DRAFT_PICK | D08 | CALL_LOGIC_RECOVERED |  | draft.context |
| TEAM_SET_CHEMISTRY | D05 | PARTIAL_BINDING | team_id, value, reason_mode | Reason mode and delegate readiness unclosed; no default mode invented |
| TEAM_CONDITIONAL_COACHING_RULES | D05 | REFERENCE_ONLY | team_id, parameters | Nextgen official feature lead plus PC22 type/field names; actual PC22 mutation/commit binding unresolved |
| STAFF_ASSIGN_SPECIALIST_ROLE | D05 | REFERENCE_ONLY | team_id, parameters | Nextgen official feature lead plus PC22 type/field names; actual PC22 mutation/commit binding unresolved |
| TRAIN_PREP_HUB_RECOVERY_PLAN | D07 | REFERENCE_ONLY | team_id, parameters | Nextgen official feature lead plus PC22 type/field names; actual PC22 mutation/commit binding unresolved |

## Native绑定索引

RVA均来自固定PC22构建。UNKNOWN返回类型/参数或unknowns非空时不可执行；LAYOUT是只读布局，不冒充业务函数。完整对象、生命周期、指纹及参数编码在data/native_bindings.json和runtime源码。

| Binding | RVA | 返回 | 显式Win64参数 | 缺口 |
|---|---|---|---|---|
| coach.apply_gameplan | 0x146eaa0 | void | input_GAMEPLAN:pointer, target_COACHDATA:pointer |  |
| trade.add_player | 0x12dec20 | int | proposal:pointer, from_team:pointer, to_team:pointer, player:pointer |  |
| trade.validate | 0x12ec930 | int | proposal:pointer |  |
| trade.full_check | 0x12e1800 | int | proposal:pointer, current_team_in_trade:int, context:pointer, checks:int, zero:int, output:pointer |  |
| trade.commit_wrapper | 0x132b840 | int | proposal:pointer, output:pointer |  |
| trade.add_pick | 0x12de850 | int | proposal:pointer, from_team:pointer, to_team:pointer, pick:pointer |  |
| pick.by_id | 0xf3ca00 | pointer | pick_id:uint |  |
| pick.unique_id | 0x947330 | uint | pick:pointer |  |
| player.by_id | 0xf3f580 | pointer | player_uid:uint |  |
| training.set_team_on_date | 0x1325f10 | void | team:pointer, native_date_key:int, training_input:pointer |  |
| training.daily_by_date | 0x12f1390 | pointer | team:pointer, native_date_key:int |  |
| gameplan.ensure_opponent | 0x1244230 | pointer | manager:pointer, opponent_team:pointer |  |
| scout.focus_specific | 0x1322f30 | void | goal:pointer, count:int, prospect_pointer_array:pointer |  |
| scout.initialize_goal | 0x1257560 | void | goal:pointer |  |
| scout.append_goal | 0x1244580 | int | trip:pointer, goal:pointer, team:pointer |  |
| scout.execute_trip | 0x1261d40 | void | team:pointer |  |
| scout.goal_prospect_by_index | 0x12f2790 | pointer | goal:pointer, index:int |  |
| sign.offer_contract | 0x12bd4c0 | int | signing:pointer, context_or_null:pointer, origin_flag:int, mode_flag:int | Fresh proposal initialization/default enum values and flag meanings are not fully closed; Offer accepted/pending is not identical to completed signing |
| sign.default_type | 0x12b7d60 | int | player:pointer, team:pointer |  |
| sign.process | 0x12bde70 | UNKNOWN | signing:pointer, context:pointer, mode:int, source_tag:uint, source_line:int | Commit preconditions, exact return and offer-status flow require caller closure; do not bypass OfferContract |
| sign.process_options | 0x12bfec0 | UNKNOWN | player:pointer | This processes marked options; exact mark-setting entry and full ABI remain unresolved |
| staff.sign | 0x1327de0 | UNKNOWN | signing:pointer | Staff signing object44 bytes recovered; full ABI and proposal lifecycle unresolved |
| draft.current_selection | 0x92a6a0 | pointer | round_key:int, slot_key:int, table_kind:int |  |
| draft.expansion_selection | 0x92a700 | pointer | round_key:int, slot_key:int |  |
| draft.select | 0xec9610 | void | player:pointer, team:pointer |  |
| mentor.append | 0x124f0f0 | UNKNOWN | manager:pointer, UNKNOWN:pointer | Mentee identity/list slot arguments and target mentor placement need recovery |
| mentor.remove | 0x125ed70 | UNKNOWN | manager:pointer, UNKNOWN:int | Full index/UID contract and stable mentor manager resolver need recovery |
| mentor.set_current_team | 0x13232d0 | UNKNOWN | UNKNOWN:pointer | Current-team/global manager dependencies and pointer-array schema not closed |
| player.editor_save | 0x141f6e0 | void |  | UI/global created-player editor state; no individual attribute/tendency/badge setter qualified; Do not run editor Save for an arbitrary MyLEAGUE player |
| player.copy_parent_candidate | 0x8fbe60 | UNKNOWN | destination_player:pointer, source_player:pointer | Generic parent copy exceeds selected24KiB/32-fragment bound; remaining ABI/complete footprint not recovered; Child object schemas, source ownership, callback and mandatory refresh sequence unresolved; not a standalone field setter |
| team.set_chemistry | 0x12d2060 | void | team:pointer, value:float, reason_mode:int | Reason enum and delegate readiness require closure before exposing this extra action |
| team.waive | 0x12d4530 | void | team:pointer, player:pointer, mode:int, reason:int, validation_flag:int, extra_flag:int, source_tag:uint, source_line:int | Business modes/reason/validation flag semantics and correct public wrapper must be recovered; do not default a validation bypass |
| team.release_internal | 0x12d0b60 | void | team:pointer, player:pointer, mode:int, reason:int, extra1:int, extra2:int | Internal removal helper participates in trade/waive; it is not a complete standalone roster or waiver transaction |
| read.team_layout | LAYOUT | LAYOUT |  |  |
| read.coach_layout | LAYOUT | LAYOUT |  |  |
| read.scout_layout | LAYOUT | LAYOUT |  |  |
