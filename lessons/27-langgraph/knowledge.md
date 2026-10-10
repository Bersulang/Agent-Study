# 阶段27复习：暂停状态与恢复绑定

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习契约](exercises/README.md)。

此demo用纯函数模拟状态图一步。draft进入waiting；waiting加上None仍waiting，表示还没有审核决定；只有布尔值才推进。False进入rejected，True进入done；完成态不会再次推进。

`dict(state)`创建外层副本，所以示例返回新字典而不改调用者传入的state。它是浅复制，嵌套列表仍可能共享。先预测：传入`decision="yes"`会默认批准吗？不会，抛ValueError。

练习的批准必须同时绑定task和digest。即使审批为True，来自T1的digest也不能恢复T2；过期或不匹配的记录拒绝继续。框架节点可能在恢复、重试时重跑，因此外部写入要有幂等保护；此纯函数没有真的调用LangGraph checkpoint。

Java可以用枚举表达stage、不可变状态对象表达节点输入输出，并用持久化checkpoint恢复。真实集成还要验证checkpoint存储、身份可信度和副作用发生次数。完成[练习](exercises/README.md)时列出每条状态转移的前提。
