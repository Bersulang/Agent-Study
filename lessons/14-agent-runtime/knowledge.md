# 阶段14复习：事件如何解释Runtime执行

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习契约](exercises/README.md)。

## 三种记录各回答什么问题？

在`execute(["lookup", "lookup"], budget=1)`中，`messages`保存第一次工具结果，适合交给Agent继续决策；`state`保存当前`used=1`、预算和最终reason；`events`按发生顺序记下started、tool_started、tool_completed、stopped。事件日志不是对话消息，消息也不能说明一次工具是否被取消或失败。

## 为什么`before_tool`放在调用之前？

这个函数先问取消，再问预算。返回字符串表示拦截原因，返回`None`表示放行。若预算为1，第一次调用后used从0变1；第二次在产生tool_started前被拦截。因此副作用和计数顺序明确。未知工具也不会被记为已执行。

先预测：提前取消时事件列表中是否出现tool_started？不会，因为检查先于事件记录和函数调用。若工具已经开始后抛异常，则有tool_started和tool_failed，但没有tool_completed，调用次数仍计入预算。

## 哪些边界容易被误解？

这里的取消仅在调用边界检查，不能中断已经运行的同步阻塞函数。`budget`限制工具调用次数，不代表模型token或真实费用预算。示例捕获异常类型并停止，生产Runtime还需要定义哪些业务错误可重试、哪些错误应终止，并持久化事件序号。

## Java迁移

`before_tool`类似Java拦截器，`state`类似执行上下文，`events`类似应用事件。Python字典方便演示但字段可随意改；Java DTO能在编译期约束字段，却仍需处理运行时取消与副作用顺序。完成[练习](exercises/README.md)时，重点核对取消或预算终止是否留下了不该出现的tool_started。
