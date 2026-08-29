# 接收方 bootstrap

接收方只依据 Human 转交的精确 pointer 进入当前任务空间，并按以下顺序读取：

1. `manifest.yml`；
2. 自己的 endpoint card；
3. endpoint card 指定的 role context entry；
4. pointer 指向的 exact message；
5. 消息列出的每个 direct `required_refs`。

普通消息不要求 `authorization_ref` 或 `recipient_delegation_ref`。当消息显式带有
`confirmation_ref`、legacy `authorization_ref` 或 legacy `recipient_delegation_ref` 时，该 ref 必须
已经在 `required_refs` 中并按其契约校验。默认目录扫描、递归展开引用、默认读取
全部 sender index 或历史任务均禁止。任何必读文件缺失、越出任务根或是目录时，接收方
停止并通过 Human 中转新的 `blocked` / `request` 消息说明精确缺项；不得自行扩大读取面。

