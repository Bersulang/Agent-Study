# 阶段25复习：工作区边界与可验证恢复

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习契约](exercises/README.md)。

`safe_path(root, relative)`先resolve两端，再检查目标是否仍处于base之下，避免`../secret`和相邻前缀目录逃逸。它不能阻止检查后符号链接被并发替换，因此不等价OS沙箱。

`resume`只在checkpoint标记done且report文件存在时复用；缺少产物就重建。先写报告再写checkpoint，减少状态早于产物的问题，但两个write仍不是事务。练习进一步计算SHA256：报告存在还不够，内容也要与checkpoint摘要一致。

先预测：文件已被改动但checkpoint仍记done，能否返回reused？不能，应拒绝复用或进入明确恢复错误。坏JSON同样是损坏证据，不能默默当作新任务覆盖。Java任务恢复可使用事务或原子重命名配合哈希；多进程还需要锁。
