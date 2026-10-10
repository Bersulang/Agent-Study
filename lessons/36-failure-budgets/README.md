# 阶段 36：协作失败与总预算

## 使用场景

主控和多个工作者各自重试，若只设局部上限可能把总调用次数成倍放大。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能区分总尝试预算、完成任务和副作用计数；区分可重试暂时失败与永久拒绝，并预测预算耗尽后的行为。

- 前置：阶段35的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：重试消耗共同预算，副作用要单独计数

`cooperate`逐个处理逻辑key；已经完成的key会跳过。每次尝试前检查总budget，随后attempts加一。TemporaryFailure表示本次确认未生效，允许下一次；denied是永久失败，立即返回；只有成功才增加effects并记入completed。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
if attempts >= budget:
    return {"status": "budget_exhausted", "attempts": attempts, "effects": effects}
attempts += 1
if outcome == "temporary":
    raise TemporaryFailure("本次尚未产生副作用")
```

<details><summary>先预测：budget=2且同一任务连续temporary五次，副作用effects是多少？</summary>

0；两次尝试后预算耗尽。若第1次永久denied，后面的ok不执行。两个任务共享同一总预算，而不是各自获得budget。

</details>

反例：把所有异常都当temporary会重试权限拒绝或已经提交的写请求；将attempts和effects混成同一指标，也看不出失败是否已产生副作用。生产预算还应覆盖模型、工具、并发和费用，不只计调用次数。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/36-failure-budgets/examples/demo.py
python -m unittest discover -s lessons/36-failure-budgets/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'completed', 'attempts': 2, 'effects': 1}
budget {'status': 'budget_exhausted', 'attempts': 2, 'effects': 0}
permanent {'status': 'permanent_failure', 'attempts': 1, 'effects': 0}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""协作总预算：重试消耗全局预算，永久错误停止，已完成任务去重。"""
class TemporaryFailure(Exception):
    """暂时失败且本次未生效，才允许自动重试。"""

def cooperate(actions, budget):
    completed = {}
    attempts = 0
    effects = 0
    for key, outcomes in actions:
        if key in completed:
            continue
        for outcome in outcomes:
            if attempts >= budget:
                return {"status": "budget_exhausted", "attempts": attempts, "effects": effects}
            attempts += 1
            try:
                if outcome == "temporary":
                    raise TemporaryFailure("本次尚未产生副作用")
                if outcome == "denied":
                    return {"status": "permanent_failure", "attempts": attempts, "effects": effects}
                effects += 1
                completed[key] = "done"
                break
            except TemporaryFailure:
                continue
        else:
            return {"status": "budget_exhausted", "attempts": attempts, "effects": effects}
    return {"status": "completed", "attempts": attempts, "effects": effects}

def run_case(case):
    if case == "budget":
        return cooperate([("close-T7", ["temporary"] * 5)], budget=2)
    if case == "permanent":
        return cooperate([("close-T7", ["denied", "ok"])], budget=2)
    return cooperate([("close-T7", ["temporary", "ok"]), ("close-T7", ["ok"])], budget=3)
```

按执行顺序追踪：

1. completed保存成功任务键，开始每个任务先查是否完成。
2. 预算检查在每次尝试之前，不能先调用再判断超支。
3. attempts记录真实尝试，effects仅记录成功副作用。
4. TemporaryFailure是自定义异常类，仅捕获可重试类别。
5. for的else在循环未break时执行，表示没有一次成功。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

Java通常用异常类型或错误码决定Retry；Python自定义异常继承Exception，不能把BaseException所有子类都当业务可重试错误。

## 易错点与排查

- 所有Exception都重试：权限拒绝不会因等待变成允许。
- 子任务各有三次重试却宣称全局三次：总次数会膨胀。
- 内存去重等于重启后幂等：进程退出缓存即丢失。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`allocate_budget(total, task_names)`。

把总整数预算均匀分给任务，余数按任务顺序分配；总和等于total，不能有负数；零任务配正预算时明确报错。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/36-failure-budgets/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“总预算”与“错误分类”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`permanent`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

还需区分单次超时、分支deadline与整个任务deadline；取消需要传播并限制已在执行的外部副作用。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 36`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
