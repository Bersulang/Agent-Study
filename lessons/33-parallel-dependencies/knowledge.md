# 阶段33复习：并发、取消与依赖门控

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

Semaphore(2)限制同时活动查询数；gather等待知识和工单两个任务。wait_for超过0.1秒抛TimeoutError，bounded将它标为timeout。query用finally递减active，因此取消也会释放活动计数。只有两个值都不是timeout才生成summary。

先预测：ticket超时而knowledge已成功，结果怎样？状态partial、summary为None。正常返回空字符串和超时是不同状态，练习应分别表达。取消协程也不保证外部服务停止副作用；真实网络操作仍需幂等和超时策略。Java可类比CompletableFuture组合与信号量，但取消传播语义需要逐层核对。


## 进一步检查

`gather`按传入顺序返回两个结果，即使ticket查询实际晚于knowledge完成，变量仍对应原调用位置。Semaphore峰值记录并发上限，不代表总查询数。超时分支返回字符串timeout是教学约定，业务上应使用结构化状态，避免正常答案恰好等于这个字符串。

若查询一正常返回空值，依赖是否满足由业务契约决定；它不能自动等同timeout。取消会经wait_for向内部协程传播，finally会执行，但远端HTTP服务器可能已接到请求。Java CompletableFuture也需区分取消本地future与撤销服务端处理。