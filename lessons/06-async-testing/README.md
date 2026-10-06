# 阶段 06：异步、超时、取消与测试

## 使用场景

助手同时查询多个部门，等待网络不能让其他查询停住。先用可控的asyncio.sleep模拟I/O，验证并发上限与超时。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 05 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 协程与事件循环

async def创建协程函数；调用得到协程对象；await让出执行权等待结果。

用途与例子：asyncio.run创建事件循环驱动main；sleep模拟可让出的等待，time.sleep会阻塞线程。

### 2. 并发与信号量

并发是在等待期间交错推进；Semaphore限制同时进入临界段的任务数。

用途与例子：容量2时第三个查询必须等前两个中至少一个离开；不是CPU多核并行。

### 3. 超时与取消

wait_for在期限到达时请求取消被等待协程，并等取消完成；取消不是撤回已发生副作用。

用途与例子：捕获TimeoutError得到可读失败；CancelledError应通常继续传播。

### 4. 隔离测试与Mock

unittest将预期行为写成断言；Mock替换外部依赖，使失败可重复。

用途与例子：IsolatedAsyncioTestCase每个异步测试隔离事件循环；不要依赖真实网络时延。

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

1. asyncio.run启动循环；collect创建信号量与三个协程。
2. gather将协程调度为任务；前两条拿到信号量，第三条等待。
3. await sleep让出控制权，循环推进其他任务。
4. T1、T2短暂等待后完成；T3超过包含排队时间的0.1秒期限。
5. wait_for取消T3后safe_query返回timeout；结果列表保持输入顺序。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比CompletableFuture的异步组合，但Python事件循环常在单线程调度，不能在协程里直接执行长时间阻塞I/O。async不是自动创建线程；CPU任务需另行处理。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

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
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

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
