# 阶段 06：异步、超时、取消与测试

## 使用场景

助手同时查询多个部门，等待网络不能让其他查询停住。先用可控的asyncio.sleep模拟I/O，验证并发上限与超时。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 区分创建协程、await等待与事件循环调度，不把async等同于多线程。
- 追踪三个查询如何竞争两个许可，并保持返回顺序。
- 区分超时和外部取消，说明本地取消为何不保证远端回滚。
- 用确定的输入验证成功、超时和取消传播，而不只检查“没报错”。

## 前置知识与阅读顺序

先完成阶段 05 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 协程与事件循环

先运行一个只有一次等待的例子，暂时不加入并发与超时：

```python
import asyncio

# async def定义协程函数；await标出可以等待异步结果的位置。
async def query():
    print("开始查询")
    await asyncio.sleep(0)
    print("查询完成")
    return "open"

# 顶层普通代码由run启动事件循环，并接收协程的最终返回值。
status = asyncio.run(query())
print(status)
```

输出依次为“开始查询”“查询完成”“open”。先计算`query()`得到协程对象；`run`驱动它执行。遇到`await asyncio.sleep(0)`时，这个协程让出一次执行权；之后从暂停处恢复，直到return把open交回调用者。只有这一个查询时，看不出并发收益，但我们已经能区分“创建协程”和“让它运行”。


设想要查询三张工单，网络响应期间CPU没有需要执行的Python语句。普通同步函数会一直停在等待处；`async def query_ticket()`定义一个协程函数，调用`query_ticket()`只得到待运行的协程对象。`asyncio.run(query_ticket())`创建并驱动顶层事件循环；协程执行到`await asyncio.sleep(...)`时暂停并把控制权交给循环，结果准备好后再恢复。

`await`只能在async函数中使用，它不代表“开一个线程”，也不是所有同步函数前面加async就会变快。短示例返回`"T-1: open"`；真实HTTP客户端必须提供可await的I/O接口。若在协程里调用`time.sleep`，它会阻塞整个事件循环，别的协程也无法推进。

Java对照：可类比`CompletableFuture`或异步HTTP客户端的等待；调度策略不同，Python asyncio常在一个线程里交错运行协程，并不自动并行执行CPU密集任务。

<details><summary>先预测：只调用 query_ticket() 而不await、不交给asyncio.run，会打印工单状态吗？</summary>

不会，它只创建了协程对象。程序退出时还可能警告“coroutine was never awaited”。必须让事件循环驱动它，且在协程里等待其结果。
</details>

### 2. 并发与信号量

短示例`03_concurrency.py`中的`main`建立三个工单查询协程，再由`asyncio.gather`一起调度；综合演示则在`collect`中直接传入三个协程。查询开始后，容量为2的`Semaphore`允许前两个任务进入`async with limit`，第三个任务在获取许可的位置等待。前两个在`await sleep`期间让出执行权，完成后退出上下文并归还许可，第三个才开始查询。

`tasks`列表循环中创建三个协程；`gather(*tasks)`里的星号将列表元素展开成`gather(task1, task2, task3)`这些位置参数。`gather`返回结果按传入顺序排列，哪怕任务完成次序不同。信号量限制并发在途数量，不限制每秒总请求数，也不代表CPU同时执行。

Java对照：Semaphore都用许可数量限制并发访问；Python的`async with`在正常返回或异常/取消时会释放许可，前提是资源在上下文管理器里获取。

<details><summary>先预测：前两个任务拿到许可后，第三个协程是在列表中不存在，还是已经创建但等待许可？</summary>

它已经创建并交给`gather`调度，只是执行到`async with limit`时等许可。前两个释放许可后它可以继续，因此状态是“等待”，不是“未创建”。
</details>

### 3. 超时与取消

`asyncio.wait_for(slow_query(), timeout=0.01)`给整个等待设截止时间。期限到了，`wait_for`请求取消被等待协程，等待取消收尾后抛`TimeoutError`；上层可以将超时转换成业务错误结果。本例的`slow_query`只睡眠，所以取消后没有外部副作用。

如果请求已经把“创建工单”写入远程服务，取消本地协程不会撤销远端写入。重试可能重复提交，因此后续课程会用幂等键/审批等机制处理。被调用方因取消通常应清理资源后继续传播`CancelledError`，不能把取消伪装成成功值。并发示例里的期限包住`query`整体，所以获取信号量的排队时间也计入0.1秒。

Java对照：超时通常会取消Future或停止等待，但同样不保证外部副作用回滚；业务层仍要设计幂等和恢复。

<details><summary>先预测：wait_for超时时，sleep(1)会在后台继续完整睡眠一秒吗？</summary>

本例的取消会打断协程中的可取消等待，随后进入TimeoutError分支。若协程吞掉取消或正在不可取消的同步调用里，停止可能延迟；`wait_for`也要等取消处理完成后才返回。
</details>

### 4. 隔离测试与Mock

测试把预期写成可重复的断言。同步示例的`test_high_priority_is_urgent`调用纯函数并断言priority 4为紧急；若业务规则改成`>4`，测试应失败并指出契约变了。异步测试继承`IsolatedAsyncioTestCase`，测试方法仍声明`async def`，使用`await fetch_status()`得到实际返回值。

测试使用`asyncio.sleep(0)`让出一次控制权，不需要真实网络和固定外部时延。Mock可以替换模型或HTTP函数来模拟超时，但Mock断言的是我们的代码如何处理模拟响应，并不证明真实供应商接口行为或模型质量。每个用例应独立设置输入，避免上一次测试遗留状态影响下一次。

Java对照：`unittest`的assert与JUnit断言相近；`IsolatedAsyncioTestCase`负责为异步测试提供事件循环，类似测试框架管理异步测试上下文。

<details><summary>先预测：如果测试只断言“函数没抛异常”，priority=2也会被判为正确吗？</summary>

会。测试没有断言业务结果，就没有检查“只有priority至少4算紧急”这一规则。测试必须写出能区分正确实现和错误实现的结果断言。
</details>

## 分小节学习与预测题

先运行短示例，再读下方并发工单综合演示。命令从项目根目录运行；先预测结果或异常，再执行并解释等待期间的状态变化。

1. [同步测试](examples/01_sync_test.py)：运行 `python lessons/06-async-testing/examples/01_sync_test.py`。先预测`is_urgent(4)`是否为真，再看`assertTrue`如何把业务期望变成失败条件；把输入改为3会导致断言失败。
2. [协程与await](examples/02_await.py)：运行 `python lessons/06-async-testing/examples/02_await.py`，输出`T-1: open`。调用`query_ticket()`本身不运行完函数体；`asyncio.run`驱动顶层协程，内部`await sleep`让出事件循环后恢复。
3. [并发与限流](examples/03_concurrency.py)：运行 `python lessons/06-async-testing/examples/03_concurrency.py`，输出顺序为T-0、T-1、T-2。代码先用循环显式建立协程列表，再由`gather(*tasks)`调度；星号将列表展开成多个位置参数。容量2使第三个查询等待许可，不代表CPU并行。
4. [超时与取消](examples/04_timeout_cancel.py)：运行 `python lessons/06-async-testing/examples/04_timeout_cancel.py`，输出`查询超时`。先猜它会返回`"完成"`还是进入异常分支；0.01秒截止早于1秒睡眠，`wait_for`请求取消并抛`TimeoutError`。
5. [异步测试](examples/05_async_test.py)：运行 `python lessons/06-async-testing/examples/05_async_test.py`，看到测试通过。异步测试方法需`async def`，测试中`await fetch_status()`取得`"open"`，再由断言比较；删掉await将无法正确检查协程结果。

Java对照：Python协程由事件循环调度，不自动创建线程；等待方式可类比异步HTTP客户端/CompletableFuture。`Semaphore`与Java许可计数器用途相近，同步阻塞I/O会占住事件循环。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/06-async-testing/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
[{'id': 'T1', 'status': 'open'}, {'id': 'T2', 'status': 'open'}, {'id': 'T3', 'error': 'timeout'}]
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""本地模拟I/O；无网络，不宣称真实接口性能。"""
import asyncio

async def query(identity, delay, semaphore):
    # async with获取许可，异常与取消时也会释放。
    async with semaphore:
        await asyncio.sleep(delay)
        return {"id": identity, "status": "open"}

async def safe_query(identity, delay, semaphore, timeout=0.1):
    try:
        return await asyncio.wait_for(query(identity, delay, semaphore), timeout)
    except TimeoutError:
        return {"id": identity, "error": "timeout"}

async def collect():
    semaphore = asyncio.Semaphore(2)
    # gather结果按输入次序排列，不按完成先后；模拟一条超时。
    return await asyncio.gather(
        safe_query("T1", 0.001, semaphore),
        safe_query("T2", 0.002, semaphore),
        safe_query("T3", 0.2, semaphore),
    )

if __name__ == "__main__":
    print(asyncio.run(collect()))
```

## 代码执行过程与逐段解释

1. `asyncio.run(collect())`建立并运行事件循环。`collect`创建容量2的信号量，随后准备T1/T2/T3三个查询。
2. `gather`把三个协程纳入调度。T1、T2先进入信号量上下文，T3已经在等待许可；三个查询的等待都由同一个循环交错推进。
3. 每个`await asyncio.sleep(delay)`都暂停当前协程，循环可以执行其他已就绪的协程。短延迟的T1、T2先完成并释放许可。
4. T3接着取得许可并开始0.2秒等待；它的`wait_for(timeout=0.1)`从调用`query`时开始计时，已超过期限后取消等待。
5. `safe_query`只捕获TimeoutError并返回`{"id":"T3","error":"timeout"}`。`gather`按输入参数顺序收集，所以结果仍按T1、T2、T3排列，不代表完成顺序。

反例：若把超时捕获改成`except asyncio.CancelledError: return ...`，调用者主动取消整组任务也可能被伪装成普通超时结果。正常业务超时可映射错误，外部取消通常应继续传播。

## Java 对照

Python asyncio与Java `CompletableFuture`都能表达等待和组合，但Python协程通常由事件循环单线程交错调度；在协程里做长时间阻塞I/O会卡住同一循环。async不会自动创建线程，CPU密集任务需要其他执行策略。测试层面，JUnit与unittest都需要断言明确预期；异步测试框架还要替用例管理等待上下文。

## 易错点与排查

- coroutine was never awaited：创建协程但没有await或调度。
- 事件循环已运行：不要在async函数里再次asyncio.run，直接await。
- 吞掉CancelledError：上层任务可能无法正确停止；清理后重新raise。
- 超时包含排队：wait_for包裹整个query，获取信号量也计时。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现异步solve(data)：data是(id,delay)列表，最大并发2，单任务期限0.02秒，返回成功记录或timeout错误，输入顺序保持。另写测试覆盖成功、超时、外部取消传播；取消不能被转成成功。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/06-async-testing/exercises/practice.py
python lessons/06-async-testing/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

## 企业工程延伸

企业服务要同时限制任务总量、排队时间与在途请求。后续引入pytest可改善参数化、fixture与插件，但本课unittest避免增加依赖；Mock不是模拟真实质量评估。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/asyncio-task.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试命令：`python -m unittest discover -s lessons/06-async-testing/tests -v`。`-m`运行模块，discover按目录发现测试，`-v`显示案例名。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 06`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
