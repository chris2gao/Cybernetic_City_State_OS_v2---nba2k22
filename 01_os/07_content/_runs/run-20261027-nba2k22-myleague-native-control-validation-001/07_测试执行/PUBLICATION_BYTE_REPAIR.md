# 发布阶段准备脚本字节修复

候选44efdf32的本机受控检查通过后，额外核对Git对象发现Batch03/04准备目录中的2个batch.json和16个JS在初次加入索引时被Git从CRLF规范化为LF。真实执行文件、raw Evidence、case和哈希仍完整；本机工作树保留原始CRLF，因此仅检查工作树未暴露Git blob差异。

后加`** -text`不会自动重新加入旧索引内容。修复措施是只对这两个准备目录执行`git add --renormalize`，使Git blob重新取原始工作树字节；没有改写真实raw或更改哈希来迁就换行，也没有重跑游戏。

`audit_live_observations.py --check`现增加对每批manifest和每个准备程序的`git show HEAD:path`字节SHA检查。最终候选重新执行Managed Run/Inspect，并核对远端blob。44efdf32的初次验证不作为修复后最终候选的验收收据。
