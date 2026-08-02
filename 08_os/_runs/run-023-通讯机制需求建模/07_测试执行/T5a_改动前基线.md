# T5a 改动前基线复现

- task: `os-v2-communication-requirement-model-scope-revision-001`
- exact base: `11b6bb2ba8064a1368067e6c9924b506249d8dcc`
- measured before v2 creation: `2026-08-02`
- replay command: `python 08_os/_runs/run-023-通讯机制需求建模/07_测试执行/validate_requirement_model.py`
- actual exit code: `0`
- actual stdout: `{"all_passed": true, "test_count": 15}`
- v1 SHA-256: `cfff1e32928db0c8aeb860260b8ed9c34e32994ab1b137e015dcafe5eac0f4a7`
- Human确认_v1 SHA-256: `43ad434934e3193bb74f4457856f394569c37aaca0ec36c99327b148e0bfd89e`

该基线只证明原 run-023 的 v1 schema/确认两态 validator 在开工前为 15/15；它不证明 Human
三项新裁定已经进入 A，也不证明 v2 或阶段三门已完成。
