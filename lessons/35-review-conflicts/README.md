# 阶段 35：生成检查与证据冲突

## 使用场景

草稿声称退款期限99天，引用却不存在；另一份政策又与当前政策冲突。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能分别检查证据冲突、主张支持与引用归属；说明有限修订不能消除真实冲突，并按权威级别选择或转人工。

- 前置：阶段34的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：生成草稿与证据核验分开

`review`先取证据值集合。若值不唯一，返回conflicting_evidence；只有值一致时，才检查草稿的citation是否存在于证据ID集合、claim值是否被支持。也就是说引用有效和主张正确要同时成立。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
values = {item["value"] for item in evidence}
if len(values) != 1:
    return {"accepted": False, "reason": "conflicting_evidence"}
```

`revise`最多尝试max_rounds次修订：初稿故意错误，之后尝试从一条证据修正。先预测：有两条同级证据分别值7和14，修订会选一条并接受吗？不会，review在冲突判断处就拒绝；反复生成不能消除来源冲突。

练习以active和authority筛选证据；最高权威等级仍有不同值时应标冲突，不能按列表第一项挑选。真实系统还需生效时间、来源权威规则和人工升级，不能让生成模型自行决定哪个政策是真的。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/35-review-conflicts/examples/demo.py
python -m unittest discover -s lessons/35-review-conflicts/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'accepted', 'rounds': 1, 'citation': 'policy-v2'}
conflict {'status': 'human_review', 'rounds': 2, 'citation': None}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""生成与核验分离：检查引用支持主张，并识别同级证据冲突。"""
def review(draft, evidence):
    values = {item["value"] for item in evidence}
    if len(values) != 1:
        return {"accepted": False, "reason": "conflicting_evidence"}
    citations = {item["id"] for item in evidence}
    if draft["citation"] not in citations or draft["value"] not in values:
        return {"accepted": False, "reason": "unsupported_claim"}
    return {"accepted": True, "reason": None}

def revise(evidence, max_rounds=2):
    draft = {"value": 99, "citation": "missing"}
    for round_number in range(max_rounds + 1):
        verdict = review(draft, evidence)
        if verdict["accepted"]:
            return {"status": "accepted", "rounds": round_number, "citation": draft["citation"]}
        if round_number == max_rounds:
            break
        # 模拟修订只取一条证据。冲突不会因重复生成而自动消失。
        draft = {"value": evidence[0]["value"], "citation": evidence[0]["id"]}
    return {"status": "human_review", "rounds": max_rounds, "citation": None}

def run_case(case):
    evidence = [{"id": "policy-v2", "value": 7}]
    if case == "conflict":
        evidence.append({"id": "policy-v2-other", "value": 14})
    return revise(evidence)
```

按执行顺序追踪：

1. values集合去重，多个不同值表示证据争议。
2. citations集合保证草稿引用标识确实在资料中。
3. round_number=0检查原稿，不算修订次数。
4. 修订选择首条证据只是确定性模拟，不是模型推理。
5. 冲突持续到预算上限，返回人工复核而不是伪造共识。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java校验器返回字段错误并允许有限修复；模型检查者仍可能判断错，所以业务不变量应由确定性代码守护。

## 易错点与排查

- 让两个模型互相赞同当证明：共识可能共享同一错误来源。
- 只验证引用id存在：还要检查内容支持具体主张。
- 把最新抓取时间当政策生效时间：资料权威和有效期需单独管理。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`choose_evidence(evidence)`。

仅选择明确active且最高authority的证据；最高等级出现不同值时返回conflict；不按列表位置选政策。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/35-review-conflicts/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“生成与检查”与“证据支持”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`conflict`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

生产检查应记录具体引用片段、版本、有效时间与检查规则；人工决议也应形成可审计证据。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 35`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
