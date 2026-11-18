---
name: os-model-routing
description: "City-State OS 的模型与产品面路由：为执行或独立审核选择 provider、surface、model 与参数档位，生成 receiver_setup。派单前确定执行者或审核者时使用。"
---

# 模型路由与接收者设置（L3_EXECUTION_GATED）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/model_routing/启动清单_v1.yml`（读取分层 `read_tiers`）。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

选择执行者或独立审核者之前；写任务包 executor_profile 时。

适用角色：初始化必载 = 任务规划；按触发加载 = 审核

## 启动必读（角色初始化时读完，约 1 KB）

- `01_os/03_mechanisms/model_routing/README.md`

## 按动作读取（做到这一步时再读）

- 选择执行者或独立审核者、写 receiver_setup 时：`01_os/03_mechanisms/model_routing/路由契约_v1.yml`、`01_os/03_mechanisms/model_routing/协作角色与接收者设置契约_v1.yml`、`01_os/02_boot/协作伙伴.md`、`01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml`、`01_os/03_mechanisms/model_routing/项目观察证据_v1.yml`
- 核对模型目录的来源时：`01_os/03_mechanisms/model_routing/来源索引_v1.yml`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/model_routing/启动清单_v1.yml`
- `01_os/05_registry/model_routing_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/03_mechanisms/model_routing/实现/verify_model_routing.py`
- `01_os/06_execution/boot/model_routing/route_receiver.py`

## 命令

- `python -B 01_os/03_mechanisms/model_routing/实现/verify_model_routing.py static .` → validation_passed，退出 0
- `python -B 01_os/06_execution/boot/model_routing/route_receiver.py --selection <selection> --catalog <catalog> --role-contract <role-contract>` → 输出 receiver_setup，authority 恒为 routing_only

## 边界与停止

- 已登记候选默认可用，只有 Human 能标记不可用或恢复；不按价格或额度路由
- 路由结果不授予文件、发布或受保护动作权限
