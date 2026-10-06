# 阶段 32：Handoff控制权交接

## 使用场景

接待者确认用户要查工单，将后续对话交给工单角色，同时避免传出私人备注。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能解释交接与工具调用的区别，保留必要事实并阻止循环转交。

- 前置：阶段31的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 控制权

定义与用途：谁负责下一轮用户交互和后续行动选择。

具体例子：owner从reception变ticket；普通函数调用返回后owner通常不变。

### 2. 交接上下文

定义与用途：接收者完成职责所需的最小事实集合。

具体例子：保留ticket_id，过滤private_note。

### 3. 交接条件

定义与用途：接收者能力和必需事实满足时才能改变owner。

具体例子：缺失ticket_id抛ValueError，不产生半完成交接。

### 4. 防环与跳数

定义与用途：历史角色检测重复目标，同时限制最长转交链。

具体例子：ticket已经出现在history时返回loop_blocked；跳数到上限返回hop_limit。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/32-handoff/examples/demo.py
python -m unittest discover -s lessons/32-handoff/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'owner': 'ticket', 'facts': {'ticket_id': 'T-7'}, 'status': 'transferred'}
loop {'owner': 'reception', 'facts': {'ticket_id': 'T-7'}, 'status': 'loop_blocked'}
limit {'owner': 'reception', 'facts': {'ticket_id': 'T-7'}, 'status': 'hop_limit'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""交接转移对话控制权，事实通过白名单缩减。"""
def handoff(owner, target, facts, history, max_hops=3):
    selected = {key: facts[key] for key in ("ticket_id",) if key in facts}
    # history 是已拥有控制权的角色路径；先检查再改变 owner。
    if target in history:
        return {"owner": owner, "facts": selected, "status": "loop_blocked"}
    if len(history) - 1 >= max_hops:
        return {"owner": owner, "facts": selected, "status": "hop_limit"}
    if target != "ticket" or "ticket_id" not in selected:
        raise ValueError("接收者或必要事实不符合交接契约")
    return {"owner": target, "facts": selected, "status": "transferred"}

def run_case(case):
    facts = {"ticket_id": "T-7", "private_note": "不应传给另一角色"}
    history = ["reception"]
    if case == "loop":
        history = ["reception", "ticket", "reception"]
    if case == "limit":
        history = ["reader", "reviewer", "helper", "reception"]
    return handoff("reception", "ticket", facts, history)
```

按执行顺序追踪：

1. selected通过字典推导式构造新字典，不直接传递facts引用。
2. 循环检测发生在改变owner前，拒绝结果保持原owner。
3. len(history)-1是已经完成的交接次数。
4. 目标和必要字段校验通过后，才返回transferred。
5. run_case证明三种路径都不会带出private_note。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

Java工作流中修改assignee类似转移负责人；方法调用不等于assignee变化。Python字典浅拷贝也不能隔离嵌套可变对象。

## 易错点与排查

- 把所有聊天历史传给所有角色：会泄露不必要的私人信息。
- 只限制跳数不查环：短环也会耗尽预算和用户耐心。
- 用owner名字授予权限：身份与授权仍应由服务验证。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`safe_handoff(owner, target, facts, history)`。

扩展为reader与ticket两类接收者，分别校验question和ticket_id；缺失字段返回needs_clarification；不能改变输入事实。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/32-handoff/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“控制权”与“交接上下文”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`limit`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

持久化交接事件与接收确认；并发会话需版本控制，防止两个角色同时认为自己是owner。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。
