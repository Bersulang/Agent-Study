# 阶段 30：职责划分与路由

## 使用场景

客服收到政策咨询与工单请求，需要选择具有最小权限的处理者。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能区分Agent、工具与固定节点，写出可解释且不扩大权限的路由。

- 真正先修：阶段11工具契约、12权限/幂等和13停止控制；并需能使用03函数、04异常与05容器。阶段29远程MCP是可选背景，不是本课硬前置。
- 本课是多Agent深化入口。可先完成阶段39—43核心服务，再回到本课学习协作模式。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 职责边界

定义与用途：定义一个角色可以决定哪些事情。工具执行已选定动作，Agent还会选择下一步，节点只是流程位置。

具体例子：knowledge角色回答政策，ticket角色读取工单；本课角色实现是确定性函数，不是真实模型Agent。

### 2. 规则路由

定义与用途：由可审计的条件决定目标，用于输入明确的分类任务。

具体例子：只含政策走knowledge，同时含政策和工单走human澄清。

### 3. 模型候选

定义与用途：模型建议某个职责，必须经程序验证允许集合与权限。

具体例子：model_choice='ticket'遇到allowed_roles只有knowledge时仍转人工。

### 4. 兜底

定义与用途：无法确定、目标未知或权限不足时进入安全的非写入路径。

具体例子：human返回permission=none，不自动赋予人工角色业务写权限。

<details><summary>先预测：`route("查询工单", {"knowledge"}, model_choice="ticket")`返回什么？</summary>

先按文本得到ticket候选；随后模型候选ticket属于已知角色，所以当前候选仍是ticket。但调用者的`allowed_roles`只有knowledge，最后权限过滤将角色改成human，返回`{"role": "human", "permission": "none"}`。如果跳过最后一步，模型就能替调用者扩大权限。
</details>

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/30-routing-roles/examples/demo.py
python -m unittest discover -s lessons/30-routing-roles/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
knowledge {'role': 'knowledge', 'permission': 'read'}
ambiguous {'role': 'human', 'permission': 'none'}
denied {'role': 'human', 'permission': 'none'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""职责路由：规则模拟意图判断，权限始终由程序验证。"""
def route(text, allowed_roles, model_choice=None):
    # 同时命中两种职责时不猜测，进入人工澄清。
    matches = []
    if "政策" in text:
        matches.append("knowledge")
    if "工单" in text:
        matches.append("ticket")
    role = matches[0] if len(matches) == 1 else "human"
    # 模型输出只是候选；即使候选合法，也不能扩大调用者权限。
    if model_choice is not None:
        role = model_choice if model_choice in {"knowledge", "ticket"} else "human"
    if role not in allowed_roles:
        role = "human"
    return {"role": role, "permission": "read" if role != "human" else "none"}

def run_case(case):
    if case == "knowledge":
        return route("查询退款政策", {"knowledge"})
    if case == "ambiguous":
        return route("政策和工单都要查", {"knowledge", "ticket"})
    if case == "denied":
        return route("查询工单", {"knowledge"}, model_choice="ticket")
    raise ValueError("未知案例")
```

按执行顺序追踪：

1. route先建立命中列表，列表长度是歧义判断依据。
2. 只有唯一命中时取matches[0]，避免空列表越界。
3. 模型候选必须属于已知角色集合，未知名字不能变成函数调用。
4. allowed_roles做最后一道权限过滤，判断与授权分离。
5. run_case分别展示成功、歧义和候选越权。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

Java可用枚举和Strategy选择处理器；Python字符串需要显式允许集合，动态字典不会自动提供枚举约束。

## 易错点与排查

- 把模型推荐当授权：必须在程序和下游业务服务再次检查。
- 多个关键词仅取第一个：组合任务可能需要拆解或澄清。
- 每个函数都叫Agent：固定查询函数不具备自主选择能力。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`batch_route(requests, allowed_roles)`。

实现批量路由，空白请求返回human；统计每个角色数量；输入列表不得被修改。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/30-routing-roles/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“职责边界”与“规则路由”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`denied`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

生产中记录路由理由与分类版本，并用独立评估集衡量错误分流；业务写入仍需要审批。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 30`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
