# 阶段36复习：预算、重试和副作用

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

cooperate跨任务共享budget。每次尝试前检查额度，随后attempts加1。TemporaryFailure声明本次未生效，可重试；denied立即永久失败；成功才增加effects并将key加入completed。已完成key再次出现会跳过。

先预测：预算2、连续temporary五次，attempts=2、effects=0，最终budget_exhausted。若错误响应可能已经写入，就不能归为可重试temporary。练习把预算平均分给任务并按顺序分配余数；生产还要分别监控模型用量、工具次数和真实副作用。


## 进一步检查

`for outcome in outcomes`耗尽而未成功时走else，返回budget_exhausted；永久denied则在遇到时立刻退出，即使后面列表还有ok。已经完成的key跳过，说明重投递去重按逻辑任务身份发生，而不是比较动作文本。effects只在成功处加一，用于区分尝试与副作用。

预算为0时第一次循环前直接返回，副作用为0。预算分配练习中余数按task_names原始顺序分配，因此排序输入会改变哪个任务多一份预算；重复任务名应拒绝，否则字典映射会覆盖预算。