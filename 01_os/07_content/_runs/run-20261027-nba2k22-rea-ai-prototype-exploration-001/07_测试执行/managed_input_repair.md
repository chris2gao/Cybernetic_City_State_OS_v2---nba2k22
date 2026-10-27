# 精确候选验证输入格式修正

初始候选`e697dca576a8d12468af0e0fb4667c2f3be93809`的managed run在执行检查之前返回`candidate_outside_packet_allowlist`，随后同候选inspect亦返回相同输入错误；这不是测试PASS，也不是语义测试失败。

诊断：当前OS managed_verify.py的allowed函数仅支持精确文件或以`/**`结尾的目录规则，不支持任务包中的`REA_AI_MECHANISM_KNOWLEDGE_*`文件名通配。实际diff只新增`REA_AI_MECHANISM_KNOWLEDGE_V1.md`。将该规则收窄为这一精确文件，其他两个目录范围保持原样。没有扩大业务/权限范围，没有绕过runner，没有改OS实现。

修正后使用新提交及新attempt执行完整三检查，并以同候选inspect复核；实际结果另存，不覆盖此前拒绝事实。此为一次有新诊断依据的确定性修复，不形成失败预算耗尽记录。
