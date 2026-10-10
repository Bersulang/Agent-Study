# 阶段32复习：交接时限制事实与路径

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

handoff先从facts提取ticket_id，丢弃private_note，再检查目标是否已在history中、是否超hop上限，最后验证目标角色及必需事实。成功才把owner切换到ticket；loop_blocked和hop_limit保持原owner。

先预测：接收者ticket在history里但事实完整，是否继续转交？不继续，避免循环。reader需要question、ticket需要ticket_id，缺少时应澄清；不得通过修改调用者facts补造字段。Java中可用不同角色的请求DTO限制传递数据；生产系统还需服务端授权。


## 进一步检查

history保存的是控制权已走过的角色路径，所以交接循环判断要早于改变owner。hop限制同样在转移前检查；失败返回当前owner，让上游知道任务没有交出去。事实白名单有意很小：ticket角色只需要ticket_id，不应收到HR备注或整段对话。

先试缺少ticket_id：本demo对不满足合同的接收请求抛ValueError；独立练习要求把缺少question/ticket_id转换为needs_clarification。这是接口契约变化，不应把异常直接复制进练习。Java可为reader和ticket分别定义请求record，从类型层减少多余字段。