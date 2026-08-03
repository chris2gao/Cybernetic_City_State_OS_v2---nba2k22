# 旧入口 matched baseline

本目录保存三次同口径 `token_profile_run.v1`：

- task type：`communication_context_recovery`
- scale：backend executor 的 neutral-baseline full initialization，固定读取同一组旧入口文件，
  required ref 数量相同；
- acceptance：文件可读、STATE/INBOX 均为 neutral baseline、不可观测指标保持 `null`。

宿主未暴露每次 replay 的 provider token/cache/cost 指标，因此这些字段按
`.ai/TOKEN_USAGE_PROFILE.md` 保持 `null`，不得据此声称成本达标。记录只冻结旧入口测量方法、
匹配维度、实际文件字节和 wall time；阶段六用同一匹配维度收集新入口记录，阶段七才比较并判断
R8。三个 JSON 均由临时文件 + 原子 rename 首次创建，聚合器实测 `record_count=3`、
`skipped_malformed_files=0`。
