# Human capacity-work clarification — 2026-10-25

Human stated:

> 容量压力可以先不进行，原因是当前的数据只是一个月的，我们后面扩展到一个完整赛季，才能知道一个赛季的容量，并根据容量推算，我们的数据库最终保留多少年在数据库里，如果无法保留100年的数据。

Execution consequence: stop further capacity stress, capacity-driven A/B optimization or retention conclusions in the current one-month sample. First obtain representative complete-season facts, then measure one-season growth and estimate longer retention. Human may later select a horizon below100 years if the measured season evidence requires it. No concrete shorter horizon or history deletion has yet been chosen.

The already completed SQLite page measurement and simple fixed-population models are historical exploratory evidence only. They do not demonstrate actual100-season storage or determine retention. The completed fact backup/recovery verification remains valid and separate. No capacity job remains running; overall implementation stays active and other work continues.

Canonical working policy: `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/CAPACITY_AND_RETENTION_POLICY.md`.
