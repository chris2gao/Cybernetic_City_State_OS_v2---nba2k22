---
name: os-communication
description: "City-State OS 的 Human 中转通讯协议。要写正式交接消息、发 v2 中转指针、作为接收方从指针进入任务、纠正已发消息或归档通讯任务时使用。不轮询、不自动投递。"
---

# 正式通讯与 Human 中转交接（L3_EXECUTION_GATED）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/communication_system/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

发出或接收正式交接；建立通讯任务空间；归档通讯任务。

适用角色：初始化必载 = 任务规划；按触发加载 = 任务开发、审核、特色内容开发、特色内容教学或使用

## 必读（按顺序全部读完）

- `01_os/02_boot/communication_system/启动清单_v1.yml`
- `01_os/03_mechanisms/communication_system/通讯契约_v1.yml`
- `01_os/03_mechanisms/communication_system/端点卡契约_v1.yml`
- `01_os/03_mechanisms/communication_system/角色与权限边界_v1.yml`
- `01_os/03_mechanisms/communication_system/消息契约_v1.yml`
- `01_os/03_mechanisms/communication_system/发送方区与序号契约_v1.yml`
- `01_os/03_mechanisms/communication_system/文档与引用契约_v1.yml`
- `01_os/03_mechanisms/communication_system/载体与发布契约_v1.yml`
- `01_os/03_mechanisms/communication_system/Git收敛契约_v1.yml`
- `01_os/03_mechanisms/communication_system/导航与归档契约_v1.yml`
- `01_os/03_mechanisms/communication_system/纠正与跨端一致性_v1.yml`
- `01_os/03_mechanisms/communication_system/正式动作接入契约_v1.yml`
- `01_os/03_mechanisms/communication_system/Human中转指针契约_v2.yml`
- `01_os/05_registry/communication_system_v1.yml`
- `01_os/03_mechanisms/communication_system/README.md`
- `01_os/03_mechanisms/communication_system/接收方bootstrap_v1.md`

## 入口程序（调用即可，不必通读源码）

- `01_os/06_execution/boot/communication_system/validator/validate_communication_system.py`

## 命令

- `python -B 01_os/06_execution/boot/communication_system/validator/validate_communication_system.py static .` → validation_passed，退出 0
- `python -B 01_os/06_execution/boot/communication_system/publisher/publish_message.py --task-root <task-root> --message <message>` → 只在宪法路径通过后发布

## 边界与停止

- “已发送”只表示载体写入并读回成功，不表示对方已读、理解或接受
- 已发布消息不可改，纠正发 correction 并 supersedes
- 九字段 v1 指针只可显式历史读取，新发布必须用 v2 指针
