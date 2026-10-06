# 阶段 34：通信契约与共享状态

## 使用场景

两个协作角色都想更新同一工单，旧版本结果不能覆盖较新的检查结论。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能定义允许字段、校验补丁、拒绝陈旧版本并保持更新原子性。

- 前置：阶段33的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 任务契约

定义与用途：明确输入、输出、证据和错误格式，使接收者不解析自由文本猜状态。

具体例子：patch只允许status，非法private_reason被拒绝。

### 2. 共享与私有状态

定义与用途：共享事实经受控合并，角色内部草稿不直接进入公共状态。

具体例子：state只含version和status，私人理由不能写入。

### 3. 乐观并发

定义与用途：提交者携带读到的版本，只有版本仍一致才允许更新。

具体例子：第一次以version=1写入后，第二次仍用1触发version_conflict。

### 4. 原子校验

定义与用途：先验证整个请求，再做任何状态变化。

具体例子：包含合法status和非法字段的补丁失败后version仍1。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/34-contracts-state/examples/demo.py
python -m unittest discover -s lessons/34-contracts-state/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'version': 2, 'status': 'ready'}
conflict {'version': 2, 'status': 'ready', 'error': 'version_conflict'}
invalid {'version': 1, 'status': 'new', 'error': 'invalid_patch'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""显式结果契约与乐观并发版本，拒绝非法字段后不部分更新。"""
def merge(state, patch, expected_version):
    if expected_version != state["version"]:
        raise ValueError("version_conflict")
    # 必须校验整个补丁，避免前半部分已写入、后半部分才发现越权。
    if set(patch) != {"status"} or patch["status"] not in {"ready", "blocked"}:
        raise ValueError("invalid_patch")
    state.update(patch)
    state["version"] += 1
    return dict(state)  # 返回拷贝，避免外部修改内部共享字典。

def run_case(case):
    state = {"version": 1, "status": "new"}
    try:
        if case == "invalid":
            merge(state, {"status": "ready", "private_reason": "leak"}, 1)
        else:
            merge(state, {"status": "ready"}, 1)
            if case == "conflict":
                merge(state, {"status": "blocked"}, 1)
    except ValueError as exc:
        return {**state, "error": str(exc)}
    return state
```

按执行顺序追踪：

1. merge先比版本，发现陈旧请求立刻拒绝。
2. set(patch)提取所有key，必须与允许集合完全相等。
3. 值域检查保证status不能任意拼写。
4. 两个校验都通过之后才update并自增版本。
5. 返回dict(state)防止接收者拿到内部字典引用。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

对应Java乐观锁@Version和DTO字段校验；Python类型标注本身不做运行时验证，必须写检查或使用校验库。

## 易错点与排查

- 更新每个字段时才逐个验证：可能留下半写入状态。
- 仅对客户端显示版本却不在服务端比较：不是并发保护。
- 返回内部共享对象：调用者可以绕过merge直接修改。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`merge_many(state, patches, expected_version)`。

原子合并一批补丁：全部合法才写入、版本仅加一；任意补丁非法时状态完全不变。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/34-contracts-state/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“任务契约”与“共享与私有状态”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`invalid`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

内存字典仅说明机制；数据库需带version条件的UPDATE并检查rowcount，分布式状态还需租户隔离。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。
