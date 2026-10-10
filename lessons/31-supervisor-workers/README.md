# 阶段 31：主控与子Agent委派

## 使用场景

综合回答需要政策依据和工单状态，主控必须知道哪些结果尚未回来。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能追踪任务ID去重、worker调用次数和缺失结果；区分必需与可选任务，并说明深度上限如何在委派前阻止递归。

- 前置：阶段30的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：主控怎样知道任务真的完成

`supervise`按原始任务列表协调worker，但用`task["id"]`识别逻辑任务。列表里重复出现knowledge时，`seen`让它只派发一次，避免worker重复读取或写入。深度限制发生在派发前：当前depth已经等于max_depth时，calls为0。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
if key in seen:
    continue
seen.add(key)
worker = workers.get(task["role"])
if worker is not None:
    value = worker(task)
```

<details><summary>先预测：ticket worker返回None，knowledge成功，status是什么？</summary>

incomplete，因为missing按原始计划中已见任务和实际结果计算，而不是只看成功结果数量。练习把必需任务缺失作为阻断条件，可选任务缺失只放warnings。

</details>

反例：用`len(results) == len(tasks)`判断完成，重复id会造成数量不匹配；若先对tasks去重又忘了缺少worker的任务，也可能误报成功。这个同步函数不实现模型委派或并行worker，仅说明任务身份、深度和完成门槛。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/31-supervisor-workers/examples/demo.py
python -m unittest discover -s lessons/31-supervisor-workers/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'completed', 'calls': 2, 'missing': []}
missing {'status': 'incomplete', 'calls': 2, 'missing': ['ticket']}
depth {'status': 'depth_exceeded', 'calls': 0, 'missing': []}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""主控委派：子任务有稳定标识、深度限制和缺失结果检查。"""
def supervise(tasks, workers, depth=0, max_depth=2):
    if depth >= max_depth:
        return {"status": "depth_exceeded", "calls": 0, "missing": []}
    seen = set()
    results = {}
    calls = 0
    for task in tasks:
        key = task["id"]
        if key in seen:
            continue  # 相同逻辑任务只委派一次，避免重复副作用。
        seen.add(key)
        worker = workers.get(task["role"])
        if worker is not None:
            calls += 1
            value = worker(task)
            if value is not None:
                results[key] = value
    # 完成条件来自原始计划，不能把已有结果数量误当全部成功。
    missing = sorted(seen - results.keys())
    return {"status": "incomplete" if missing else "completed", "calls": calls, "missing": missing}

def run_case(case):
    tasks = [{"id": "knowledge", "role": "reader"}, {"id": "ticket", "role": "ticket"}]
    tasks.append(dict(tasks[0]))  # 人为制造重复委派请求。
    workers = {"reader": lambda task: "policy-v2", "ticket": lambda task: "T-7"}
    if case == "missing":
        workers["ticket"] = lambda task: None
    return supervise(tasks, workers, depth=2 if case == "depth" else 0)
```

按执行顺序追踪：

1. seen保存逻辑任务id，重复id直接continue。
2. workers字典把职责名映射到可调用函数，lambda是只有一个表达式的小函数。
3. 调用计数在执行前加一，空结果依然算一次真实调用。
4. results只保存有效值，None表示缺失，而非空字符串。
5. seen减results.keys得到missing，缺失会阻止成功状态。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java调度器调用多个Service并汇总Future；Python可调用对象直接存字典，但需要清楚规定返回None的意义。

## 易错点与排查

- 用返回结果的数量判断成功：重复结果可能掩盖缺失。
- 让子Agent自由委派而不传depth：深度限制失效。
- 去重缓存只看文本：不同租户的相同文本不能共用业务结果。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`summarize_required(tasks, results)`。

将必需和可选子任务区分；必需缺失阻止完成，可选缺失记录warning；重复task id定义为同一个逻辑任务。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/31-supervisor-workers/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“主控”与“子任务标识”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`depth`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

跨进程委派还需要任务持久化、身份传递和全局预算；主控内存中的seen无法跨重启去重。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 31`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
