# DEV15 — Potential遮蔽与Intangibles轮换偏置

2026-10-20，PR #5独立开发分支；引擎`DEV14_V1.2_H_DEV15`。这是工程与合成验证交付，不是main部署、正式游戏写入或GM V4启用。实现证据见[给M3的交接](development_reviews/DEV14_TO_M3_HANDOFF.md)。

## 自动后处理与事实语义

`auto_pipeline_ingest.run_automated_ingestion`仍只运行完整`full_verified_v1`：生命周期/三库身份验证 → 同一RO会话原生采集与初步数量检查 → **暂存league/pool中sanitize_player_potential** → 两库commit及三库带日志安装 → 净化后snapshot_digest/pool SHA/manifest → 原来源审计 → export/SQLite backup/M0 → 玩家明确要求时Publish。没有新增局部采集开关。

`src/player_potential_mask.py`将所有player_pool的potential/raw_potential、source_details_json.attributes.potential.raw/value设为1；player_source_details的JSON同样处理；PLAYER完整raw_struct及state_io_objects中PLAYER_TENDENCY/PLAYER_PLAYTYPE/PLAYER_ROTATION_OVR_BIAS的raw只改0x441。原始Intangibles 0x440、身份、合同、历史新秀类型0x70及其他字节不变，Staff不处理。新导出副本内已有历史球员行也净化；**既有不可变档案从不就地修改**。

每行标source_role=GM_SANITIZED、mask_version/potential_mask_version=potential_v1、player_raw_masked=true；潜力字段visibility=MASKED_BY_GM_WORLD_RULE、evidence=NOT_GAME_OBSERVED。`player_potential_masks`在两库记录相同策略/覆盖计数：pool_total、roster_total、masked_json_count、masked_blob_count、missed_rows=0及排除0x441后的球员字节SHA256。校验该指纹证明0x440、身份、合同等未被后处理改变，不保留真Potential指纹或原值。

未知Potential列/JSON别名、未知PLAYER原始镜像、错长度、漏行或策略不一致均POTENTIAL_SANITIZATION_FAILED。双库savepoint失败一起撤销；正式文件只安装完整暂存组；中断PREPARED拒绝继续。保留旧已发布指针，不能用只隐藏查询列代替净化。再次净化已完整校验的同批直接返回，不改库；新采集总会净化新暂存池。

仅校验既有静态副本的本地dry-run（在内存副本执行并回滚，不转换旧档）：

```powershell
python -B scripts/sanitize_player_potential.py --career <career> --batch <batch> --dry-run
```

## 原始审计与历史访问

真实球员内存的Potential始终不改。`audit_source_extensions`在比较时仅规范化live PLAYER的0x441和该字段JSON，继续核对其他完整字节与属性/合同；Staff仍原样逐字节比较。DEV14审计只比较注册字段和身份，其中不注册Potential；不会因它被遮蔽而取消其他核对。导出和M0新mask批次封存前执行verify_sanitized_pair；不是日常GitHub JSON哈希同步检查。

旧M02/旧Release/Git历史仍可能公开原始Potential；本工程没有删除或重写它们。GM/ANALYTICS/DEVELOPMENT消费CLI必须调用require_gm_sanitized；新DEV14 stage源装载也执行该检查。旧包无mask标记不能重发，后续若需转换必须另行授权、建立新版本。CodeX仍可只读审计旧M0，不将其重新标为GM可用；source_binding.production_gm_eligible也据新遮蔽政策收紧。**M3另一分支接入时必须显式调用该方法**，不能假定它已更新。文件/公共GitHub级访问控制并未隔离所有同OS模型；规则不等于旧公开历史无法被读取。

## 历史新秀来源分开

GM历史新秀查询保留0x70筛选/身份元数据，但返回GM_SANITIZED标记。`query_historical_draft_class(..., for_native_injection=True)`拒绝脱敏池；`preflight_native_rookie_source`也拒绝含mask标记的行或来源，错误SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE。

独立预检DTO只接受FRESH_NATIVE_CALIBRATED或NATIVE_INJECTION_PRIVATE、native_binding、每人native_identity及完整原生raw，预检保留原始Potential，不授予写入权。当前**没有实际私有来源采集器、权限隔离主档或原生注入执行器**；不得通过改JSON标签把GM池变成原生源。未来适配器必须复用此拒绝规则。未读取/建立私有球员真潜力档。

## 唯一新增球员能力例外

`rotation.intangibles`注册target_kind=PLAYER_ROTATION_OVR_BIAS，复用memory_field_profile.fields.PLAYER.intangibles：0x440、1byte、conversion=rating。输入整数25–99，通过config.rating_to_raw编码（99→222），读回config.raw_to_rating；不是直接写入数字99。保持0x441及所有未选字节。

沿用PLAYER_TENDENCY/PLAYER_PLAYTYPE的同队唯一身份定位、source/process/save/instance/generation、完整批准tuple、CAS、durable preimages、回读和条件恢复。Journal含rotation_bias_changes的intangible_before/after和来源；OVR未观测仍UNKNOWN，分钟反馈等下次正常生产批次，不强迫模拟比赛或锁分钟。

```json
{"decision_id":"ROT_EXAMPLE","version":1,"reason":"轮换优先级假设，非批准","changes":[{"action_id":"A1","object_key":"同批rotation查询返回的键","field_key":"rotation.intangibles","target_value":65,"reason":"给该球员更高轮换优先级"}]}
```

```powershell
python -B scripts/gm_data_query.py rotation team --career <career> --batch <batch> --team CHA --role WEB_GM
python -B scripts/gm_state_io.py stage --career <career> --source-batch <batch> --proposal <intent.json>
python -B scripts/gm_state_io.py validate --career <career> --change-set <id>
```

正式写入按玩家2026-10-20决定，使用真实聊天批准引用、完整tuple和显式开关，review可选，不再做权限/防伪专项。TEAM_BOOK_REBIND、Personal防守和其他原生字段见DEV14手册。M3决定角色/分钟目标带与30队策略；底层不做经营决策。Potential=1不能筛球员；Intangibles偏置不是投篮/速度/传球增强，不承诺固定分钟收益或实机持久化。
