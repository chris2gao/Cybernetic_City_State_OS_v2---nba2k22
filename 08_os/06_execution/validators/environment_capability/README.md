# Environment capability receipt validator

`validate.py` 是 environment capability receipt v1 的 canonical validator。它把已登记的
`check-jsonschema` wrapper 与不复用 schema 正则的独立 checker 组合成一个入口：

```powershell
python "08_os/06_execution/validators/environment_capability/validate.py" "<receipt.json>"
```

默认 schema 与 wrapper 都从仓库内 canonical 路径解析；`--schema` 和 `--wrapper` 仅用于对
同合同副本做隔离测试。validator 按现有合同把 canonical `.yml` schema 逐字节复制为临时
`.json` 后调用 wrapper，临时副本随调用删除。历史原型保留在 run-020，仅作证据，不再是调用入口。

## 结果合同

- schema 与 checker 都放行：`classification: pass`，exit `0`；
- schema 与 checker 都拒绝：`classification: agreed_reject`，exit `0`；
- 仅 checker 拒绝：`classification: checker_only`，exit `0`，这是 schema 盲区信号；
- 仅 schema 拒绝：必须是非零退出，细分如下：
  - 若只把字符串型 `measured_at` 替换成合法 date-time，或只把 schema 中 `safeString`
    落点的空字符串替换成非空占位值，再经同一 wrapper 重验即可通过，则返回
    `schema_only_known_difference`，exit `1`；
  - 若已知差异修复后仍不能通过，则返回 `schema_only_unexplained_disagreement`，exit `1`。

已知差异白名单只有 `measured_at_format` 与 `safe_string_min_length`。判定不是按错误文本猜测：
validator 仅修改白名单对应字段并用同一 schema 重验；存在任何并行未知错误时重验仍会失败，
所以不能借白名单放行。wrapper policy/tool 故障返回 `schema_validator_failure`，exit `2`。

`checker_errors` 合同与 run-020 原型一致。checker 继续独立推导 drive-root、UNC、POSIX
用户/系统根、home 缩写和环境变量展开等路径形态；本次提升不扩张 schema 正则。
