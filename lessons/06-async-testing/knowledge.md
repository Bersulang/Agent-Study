# 阶段06知识整理：异步、超时、取消与测试

关联课程：[讲义](README.md)；例子：[综合演示](examples/demo.py)、[同步测试](examples/01_sync_test.py)、[await](examples/02_await.py)、[并发限流](examples/03_concurrency.py)、[超时取消](examples/04_timeout_cancel.py)、[异步测试](examples/05_async_test.py)。

## async def、协程和事件循环分别是什么？

`async def query_ticket()`定义协程函数；`query_ticket()`返回尚未驱动的协程对象。`await`只在协程里等待另一个可等待对象，并在等待时让出控制权。`asyncio.run(...)`负责为顶层程序建立事件循环并最终收尾。若忘记await或调度，业务函数不会按预期返回状态，可能出现“协程从未等待”警告。`time.sleep`是同步阻塞调用，会停止整个循环推进。

## 并发为什么不等于并行？

在[并发示例](examples/03_concurrency.py)中，三项任务都已创建，但Semaphore容量为2，只让两项同时进入查询区。两项遇到`await sleep`时暂停，循环调度其他项；第三项等许可。单线程也能在等待时交错工作，因此这是并发而非CPU同时计算。`gather(*tasks)`把列表拆成多个实参，返回列表按传入顺序排列，不能拿输出次序推断完成次序。

## 超时为什么不能当作事务回滚？

`wait_for`到期后向被等待协程请求取消并抛`TimeoutError`；同步短示例中1秒睡眠被0.01秒期限打断，控制流进入捕获分支。但取消本地等待不撤销已提交的远端写入。若任务接近副作用边界，重试需要幂等键、查询结果或补偿机制。调用方主动取消产生的`CancelledError`通常要清理后向上传播，不能和业务超时混为一谈。

## 测试和Mock能证明什么？

同步`unittest`将预期业务结果写成断言；异步`IsolatedAsyncioTestCase`让测试方法await实际协程。断言若只检查“没有异常”，不能证明规则正确。Mock能精确重现超时或错误，让错误分支稳定测试；它只证明本地代码如何处理模拟结果，不证明真实网络、供应商或模型质量。每个测试都应有区分正确与错误实现的输入。

## 执行与失败路径

综合示例按T1/T2/T3顺序传入`gather`。T1与T2先取得许可并等待短时间，T3等待许可；前两项释放后，T3开始查询。每个timeout为0.1秒且覆盖等待许可的时间，所以第三项最终进入`TimeoutError`分支，返回timeout记录。gather结果仍按传入顺序排列。手工变更延迟或并发上限时，需区分“开始运行的时间”和“完成先后”。

## Java迁移

Java `CompletableFuture`与Python协程都支持异步组合，但执行调度和取消语义要读各自API；Python asyncio常在单线程事件循环交错推进协程。同步阻塞调用会卡循环，超时Future也不会自动撤销外部系统已完成的操作。

## 工程应用

企业服务要分别限制任务总量、排队时间与在途请求，Semaphore只处理同时进入的数量。后续引入pytest可改善参数化、fixture与插件；本课`unittest`避免额外依赖。Mock不等于真实模型质量评估。

## 复习与验证

先预测容量2时第三个请求处于“没创建”还是“等待许可”，再预测超时后`gather`返回项是否改序。随后完成[独立练习](exercises/README.md)：实现异步`solve(data)`、限制并发、处理单次超时，并编写外部取消仍能向外传播的测试。参考答案只在实现完成后对照。

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
