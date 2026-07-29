# 上下文管理实现

- `文件布局契约_v1.yml`：机器可读文件类别、路径、跟踪、注册和生命周期。
- `verify_context_structure.py`：验证必需路径、boot、registry、final evidence、旧活动路径、
  D2 版本、边界措辞、双 run root 所有权与 runtime ignore、发布禁令、A v2/确认 v2
  与 `PART-01=failed`。

运行：

```powershell
python "08_os/03_mechanisms/context_management/实现/verify_context_structure.py"
```

任何 finding 都以稳定 ID 输出并返回非零。
