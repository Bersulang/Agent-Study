# 阶段06知识整理：异步、超时、取消与测试

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 协程与事件循环

定义：async def创建协程函数；调用得到协程对象；await让出执行权等待结果。

使用：asyncio.run创建事件循环驱动main；sleep模拟可让出的等待，time.sleep会阻塞线程。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 并发与信号量

定义：并发是在等待期间交错推进；Semaphore限制同时进入临界段的任务数。

使用：容量2时第三个查询必须等前两个中至少一个离开；不是CPU多核并行。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 超时与取消

定义：wait_for在期限到达时请求取消被等待协程，并等取消完成；取消不是撤回已发生副作用。

使用：捕获TimeoutError得到可读失败；CancelledError应通常继续传播。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 隔离测试与Mock

定义：unittest将预期行为写成断言；Mock替换外部依赖，使失败可重复。

使用：IsolatedAsyncioTestCase每个异步测试隔离事件循环；不要依赖真实网络时延。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 执行与失败路径

asyncio.run启动循环；collect创建信号量与三个协程。

gather将协程调度为任务；前两条拿到信号量，第三条等待。

await sleep让出控制权，循环推进其他任务。

T1、T2短暂等待后完成；T3超过包含排队时间的0.1秒期限。

wait_for取消T3后safe_query返回timeout；结果列表保持输入顺序。

## Java迁移

可类比CompletableFuture的异步组合，但Python事件循环常在单线程调度，不能在协程里直接执行长时间阻塞I/O。async不是自动创建线程；CPU任务需另行处理。

## 工程应用

企业服务要同时限制任务总量、排队时间与在途请求。后续引入pytest可改善参数化、fixture与插件，但本课unittest避免增加依赖；Mock不是模拟真实质量评估。

## 复习与验证

先解释概念，再完成[独立练习](exercises/README.md)。

保留真实运行记录；参考答案能运行不代表你已掌握。

[官方来源](https://docs.python.org/zh-cn/3.12/library/asyncio-task.html)

## 测试语法与可选开发工具

`asyncio.gather`接收多个等待对象，结果次序对应输入；失败策略与取消传播需单独测试。
答案中的 `*(one(...) for ... in data)`把生成器产生的多个协程展开成位置参数。
`lambda: False`是无参数函数，调用时返回False；用于默认“尚未取消”的检查器。
测试的 `with self.assertRaises(...)`要求块内抛指定异常；未抛或抛错类型都会失败。
`patch.object`在with范围临时替换依赖，退出后恢复；`AsyncMock`模拟可await的依赖。
`nonlocal active`允许嵌套函数修改外层局部绑定；不声明时赋值会创建内层局部变量。
测试使用importlib按文件加载模块，因为课程目录不是合法Python包名；这是测试装载工具，不要求初学者手写。

[可选pytest/格式/类型检查接入](integrations/README.md)解释安装命令和版本；默认unittest无需第三方包。
本次没有安装或执行pytest、ruff、mypy；已有unittest回归已实际运行。
