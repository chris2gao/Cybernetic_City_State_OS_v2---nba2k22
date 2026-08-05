# 阶段协同推演闭环 · MAJOR-1 Windows 路径修复独立复审

```yaml
review_dispatch:
  task_id: os-v2-stage-collaborative-deliberation-activation-001
  repository: chris2gao/Cybernetic_City_State_OS_v2---core
  branch: dev/os-v2-stage-collaborative-deliberation-activation-001
  exact_master_base: 161163a4a762a33ad7c5b4382bccaa4023c7d0e5
  failed_review_head: 3b9243f608fdce13eeff5b446861bea51058d758
  repaired_content_head: 6f066794106c33be98de3cf4dba3cb4ad75cd245
  repaired_validator_blob: 8222b7b70f11a2e24902f76c4dcd5be0f26c26df
  repair_record_blob: 60a35e8ef3c976603c6c0e53b7cc4259db62b8c9
  reviewer: cc_opus_5
  branch_modification_allowed: false
  master_publication_authorized: false
```

审核开始前请直读远端分支当前 40 位 head，以包含本派单与最终 run 状态的远端 head 为复审基线。

本次只复审先前 FAIL 的 MAJOR-1 及其必要 blob 绑定与回归，不重新扩大 activation 语义范围。

## 原 finding

Windows 上：

```python
str(Path(ACTIVE_VALIDATOR_PATH).with_name(BASE_VALIDATOR_NAME))
```

生成反斜杠仓库路径，导致完整 checkout 的 v2 static 返回 13。

## 修复

```python
base_validator_path = ACTIVE_VALIDATOR_PATH.rsplit("/", 1)[0] + "/" + BASE_VALIDATOR_NAME
```

Validator：

`08_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py`

新 blob：

`8222b7b70f11a2e24902f76c4dcd5be0f26c26df`

Boot 新 blob：

`f513cc58473f19c0c0c2948676a14b7feff76159`

七个 workflow 引用均已绑定新 validator blob。Registry 的 validator 字段只存仓库路径、不存 blob，因此无需修改。

修复记录：

`08_os/_runs/run-20260804-阶段协同推演闭环激活-001/07_测试执行/MAJOR-1_Windows路径修复与复验_v1.yml`

blob：

`60a35e8ef3c976603c6c0e53b7cc4259db62b8c9`

请在 Windows 的完整字节精确 checkout 上独立核验：

1. failed review head 到修复 content head 是否恰为 9 个路径，每个路径仅一行替换；
2. validator 是否只改变 `base_validator_path` 的构造方式；
3. Windows 与 POSIX 下该逻辑是否都生成正斜杠仓库路径；
4. boot `load_order[validator]` 是否绑定新 blob；
5. 七个 workflow `validator_ref.blob_sha` 是否全部绑定新 blob；
6. registry 是否仍正确保存 validator 的正斜杠仓库路径，且无需 blob schema 变更；
7. 在完整 checkout 上运行 runtime guard，基线为 0，七种禁止 canonical live-state 目录均为 15，还原为 0；
8. 在完整 Windows checkout 上运行 v2 static，必须返回 0；
9. 原 35 个 fixture 必须 35/35，分布 12/18/2/3；
10. workflow 引用缺失、额外、重复、未知均返回 16；陈旧 exact blob 返回 13；无效授权返回 15；
11. active-dormant 语义、权限边界、核心 7/45/47/10/16/26/5 计量是否完全未变；
12. master 是否仍精确为 `161163a4a762a33ad7c5b4382bccaa4023c7d0e5` 且未激活；
13. MAJOR-1 是否关闭，是否仍有 blocker 或 major；
14. 激活任务是否允许完成，是否可请求 Human 普通 fast-forward。

不要修改分支，不要提交，不要推送。

最终结论只使用 PASS、PASS_WITH_NON_BLOCKING_NOTES 或 FAIL。
