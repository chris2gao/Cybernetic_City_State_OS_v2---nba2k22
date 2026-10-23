# 离线重放

在仓库根目录使用 Python3、Capstone。无需管理员权限或运行游戏；不允许把进程句柄作为image输入。`sources/gemini/audited_memory.py`等历史脚本仅供阅读，**不要执行历史live采集器**。

```powershell
python -B -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/research/native_access/NATIVE_INGREDIENTS_CODEX_R02 -p test_research.py -v
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/native_access/NATIVE_INGREDIENTS_CODEX_R02/build_evidence.py
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/native_access/NATIVE_INGREDIENTS_CODEX_R02/static_evidence.py --image '<authorized disk NBA2K22.exe>' --replay 08_Domain_Applications/Antigravity_GM_Engine/research/native_access/NATIVE_INGREDIENTS_CODEX_R02/static_capture.json
```

`build_evidence.py`重写派生fixture，内容应逐字节一致。文件哈希不同的游戏镜像直接拒绝。无镜像的审查者可以检查已存指令字节/分派表和fixture测试，但不能声称自己完成了磁盘镜像重放。`NBA2K22_R02_STATIC_IMAGE`仅供Managed第三项指定授权磁盘路径，不包含在发布材料中。

Managed计划在 `01_os/07_content/_runs/run-20261023-native-ingredients-codex-r02/verification_plan.json`，按其受检候选SHA在干净工作树执行标准 `managed_verify.py run` 和同参数 `inspect`，使用仓库外全新attempt目录。完成指针与receipt保存候选、命令、原始日志哈希；最终closure提交只添加run证据，业务目录与packet/plan相对于受检候选保持不变。

固定策略示例地址0x1000/0x2000等均为合成mock地址；PID101也是合成绑定。测试中的Ben/Stephen等名字是合成边界用例，不是已恢复的实机given name。生产PID/file绑定、敏感地图、Windows访问入口及当前UI/Save认证不在本轮实现中。
