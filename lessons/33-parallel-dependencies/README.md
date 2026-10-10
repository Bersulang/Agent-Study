# 阶段 33：并行任务与依赖

## 使用场景

政策查询与工单查询相互独立，但最终回答必须同时依赖二者。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能追踪并发上限、等待超时和取消清理；解释汇总为何依赖两个结果，并区分timeout与正常空结果。

- 前置：阶段32的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：并发完成不等于依赖齐全

`execute`用Semaphore限制同时活动查询数，再用`asyncio.gather`并发等待知识和工单结果。每个query在进入信号量后递增active，在`finally`里递减；即使被取消，计数也会归还。`wait_for`为每个查询设置0.1秒截止时间，超时变成可识别的`timeout`结果。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
knowledge, ticket = await asyncio.gather(
    bounded("policy-v2", 0.01),
    bounded("T-7", 0.5 if slow_ticket else 0.02))
complete = "timeout" not in (knowledge, ticket)
```

<details><summary>先预测：工单耗时0.5秒时，是否会生成summary？</summary>

不会，工单结果为timeout，状态partial，summary=None；快路径两个结果齐备才汇总。timeout和正常返回空结果不同，练习要分别表示。

</details>

反例：只等第一个任务成功就摘要会漏掉另一个依赖；不在finally减active会使取消后的并发计数失真。超时取消协程不等于外部服务一定停止处理，真实请求还需幂等与超时语义。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/33-parallel-dependencies/examples/demo.py
python -m unittest discover -s lessons/33-parallel-dependencies/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'completed', 'knowledge': 'policy-v2', 'ticket': 'T-7', 'summary': 'policy-v2 / T-7', 'peak': 2}
timeout {'status': 'partial', 'knowledge': 'policy-v2', 'ticket': 'timeout', 'summary': None, 'peak': 2}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""独立查询并行，汇总依赖两个查询成功；超时后不生成假结论。"""
import asyncio

async def execute(slow_ticket=False):
    semaphore = asyncio.Semaphore(2)
    active = 0
    peak = 0

    async def query(value, delay):
        nonlocal active, peak  # 修改外层变量；不是创建局部同名变量。
        async with semaphore:
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(delay)  # 代表可取消的异步 I/O。
                return value
            finally:
                active -= 1  # 取消也必须释放活动计数。

    async def bounded(value, delay):
        try:
            return await asyncio.wait_for(query(value, delay), timeout=0.1)
        except TimeoutError:
            return "timeout"

    knowledge, ticket = await asyncio.gather(
        bounded("policy-v2", 0.01), bounded("T-7", 0.5 if slow_ticket else 0.02))
    complete = "timeout" not in (knowledge, ticket)
    return {"status": "completed" if complete else "partial", "knowledge": knowledge,
            "ticket": ticket, "summary": f"{knowledge} / {ticket}" if complete else None, "peak": peak}

def run_case(case):
    return asyncio.run(execute(slow_ticket=case == "timeout"))
```

按执行顺序追踪：

1. async def定义协程函数，调用它得到待执行对象。
2. async with获取并最终释放信号量。
3. nonlocal让内层query修改外层active与peak。
4. wait_for包住每个查询，各自拥有0.1秒期限。
5. gather返回值按传入顺序排列，并不按完成顺序排列。
6. 最后检查结果再生成summary；asyncio.run管理事件循环并在结束时关闭。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java CompletableFuture并发I/O加Semaphore；Python协程通常在单线程事件循环推进，CPU密集任务仍需线程/进程或外部服务。

## 易错点与排查

- 在async函数内用time.sleep：会阻塞整个事件循环。
- 认为wait_for能终止任意线程或远程写入：取消只对可协作取消对象有效。
- 一个查询超时却编造综合结论：应显式部分成功。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`dependency_summary(knowledge, ticket)`。

实现汇总门控：任一结果缺失时返回blocked及缺失名称；两者存在才生成summary；补充区别超时和正常空结果。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/33-parallel-dependencies/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“并发”与“依赖”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`timeout`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

生产需端到端deadline传播、连接池限制与取消协议；延迟应记录实际分布，避免只有平均值。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。
- [asyncio任务与超时](https://docs.python.org/3.12/library/asyncio-task.html)：gather、wait_for与取消语义。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 33`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
