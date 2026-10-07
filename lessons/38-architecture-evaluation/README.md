# 阶段 38：架构评估与选择

## 使用场景

有人建议把助手拆成五个Agent；团队要用相同任务集证明是否值得维护与调用成本。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能在同一评估集比较可用质量和预算，记录结果而非凭印象选架构。

- 学习前可预习本课的方案判断问题；正式对比需有阶段07/08评估案例以及阶段30职责划分的概念。阶段37 A2A不属于前置。若要比较多Agent实现，还需先完成相应的31—36机制。
- 建议在阶段39—43核心服务完成后，用同一评估集做正式架构结论；多Agent结果不是毕业交付必需项。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 统一评估集

定义与用途：所有实现面对同一输入和预先标注的期望结果。

具体例子：政策、工单、组合三条fixture统一用于single/workflow/multi。

### 2. 质量门槛

定义与用途：先满足业务质量，再比较成本或延迟。

具体例子：只有全部三题正确的架构进入eligible。

### 3. 成本与延迟

定义与用途：成本是资源消耗，延迟是用户等待，二者不可混为一谈。

具体例子：本课costs为手工逻辑单位，不是真实token或毫秒。

### 4. 维护取舍

定义与用途：在达到门槛的实现里选择复杂度与资源合理的方案。

具体例子：workflow正确率相同时成本2小于multi的4，优先workflow。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/38-architecture-evaluation/examples/demo.py
python -m unittest discover -s lessons/38-architecture-evaluation/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
comparison {'single_correct': 2, 'workflow_correct': 3, 'multi_correct': 3, 'selected': 'workflow'}
regression {'single_correct': 2, 'workflow_correct': 2, 'multi_correct': 3, 'selected': 'multi'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""同一数据集对比架构；预算使用逻辑单位，不伪称模型延迟基准。"""
FIXTURES = [("政策", "policy-v2"), ("工单", "T-7"), ("政策和工单", "policy-v2 / T-7")]

def single(question):
    # 单职责实现会遗漏组合问题，不代表所有单 Agent 都有此限制。
    return "policy-v2" if "政策" in question else "T-7"

def workflow(question, broken=False):
    if question == "政策和工单":
        return None if broken else "policy-v2 / T-7"
    return single(question)

def multi(question):
    parts = []
    if "政策" in question:
        parts.append("policy-v2")
    if "工单" in question:
        parts.append("T-7")
    return " / ".join(parts)

def evaluate(broken=False):
    implementations = {"single": single, "workflow": lambda q: workflow(q, broken), "multi": multi}
    # 手工成本表是教学预算，测真实成本应记录实际调用和 token。
    costs = {"single": 1, "workflow": 2, "multi": 4}
    scores = {}
    for name, implementation in implementations.items():
        scores[name] = sum(implementation(q) == expected for q, expected in FIXTURES)
    eligible = [name for name in scores if scores[name] == len(FIXTURES)]
    selected = min(eligible, key=lambda name: costs[name]) if eligible else "none"
    return {"single_correct": scores["single"], "workflow_correct": scores["workflow"],
            "multi_correct": scores["multi"], "selected": selected}

def run_case(case):
    return evaluate(broken=case == "regression")
```

按执行顺序追踪：

1. FIXTURES在实现运行前定义，不用模型自己生成期望答案。
2. single代表一个具体有限实现，不代表所有单Agent能力。
3. evaluate逐一调用三个实现并对照相同expected。
4. eligible先筛质量，min再按逻辑成本排序。
5. regression故意破坏workflow组合题，观察选择变化。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java比较同步Service、状态机和并发编排；语言或框架不是质量保证，必须控制数据集、环境和调用参数。

## 易错点与排查

- 不同架构使用不同测试题：结果不可比较。
- 把逻辑单位输出写成实测性能报告：教学预算不是基准。
- 只看最终答案：权限、工具轨迹与失败率也影响架构可用性。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`choose_architecture(reports, quality_floor)`。

输入真实报告中的quality、p95_ms、cost；先筛质量与延迟预算，再按成本选择，无可用方案返回none。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/38-architecture-evaluation/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“统一评估集”与“质量门槛”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`regression`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

生产用多次重复测量、置信区间和失败样本；架构评估应包括运维、可观测性、安全与团队熟悉程度。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。
