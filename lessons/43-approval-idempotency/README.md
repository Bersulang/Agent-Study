# 阶段 43：审批、幂等与查证

## 使用场景

人工同意关闭T-7；提交成功却HTTP响应丢失，恢复后必须查证结果而不是再关闭一次。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能绑定审批动作摘要、期限与撤销状态，事务保存幂等结果并安全重放。

- 前置：阶段42的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：先查幂等结果，再决定是否新执行

动作摘要由稳定JSON和SHA-256计算。Ledger.execute先取得写锁，查询key：已存在且摘要相同就返回旧结果并标replayed，不再次检查已消费审批或再写effects；同key不同摘要报冲突。只有没有已保存结果时才检查审批摘要、撤销、期限和动作白名单。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
saved = self.db.execute(
    "SELECT digest,result FROM operations WHERE key=?", (key,)).fetchone()
if saved:
    if saved[0] != action_digest:
        raise ValueError("idempotency_key_conflict")
    return saved[1], True
```

<details><summary>先预测：成功提交后响应丢失，审批随后过期，客户端用同key和同动作重试，会再执行吗？</summary>

不会，只查已提交结果；effects仍为1。若action改成T-8则摘要冲突。审批过期、撤销或内容不匹配时首执行不产生副作用。

</details>

反例：先做外部写入，再保存幂等记录，中途崩溃仍可能重复副作用。本演示将效果和操作记录放同一SQLite事务中；真实远程系统无法共享这个事务，需服务端幂等键、查证接口和恢复流程。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/43-approval-idempotency/examples/demo.py
python -m unittest discover -s lessons/43-approval-idempotency/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
replay {'effects': 1, 'result': 'closed:T-7', 'replayed': True}
expired {'effects': 0, 'error': 'approval_expired'}
changed {'effects': 0, 'error': 'approval_mismatch'}
revoked {'effects': 0, 'error': 'approval_revoked'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

打开[完整示例](examples/demo.py)，重点阅读`Ledger.execute`。这里需要把`try`内的查询、写入和提交，与末尾`except BaseException`里的回滚一起阅读；只看查询开头会遗漏事务最重要的失败路径。先跟踪同一个key第一次执行，再跟踪已提交后的重放。

按执行顺序追踪：

1. digest使用稳定JSON和SHA256绑定参数。
2. BEGIN IMMEDIATE串行化同一个key首次执行。
3. 先查operations：相同摘要直接返回保存结果，摘要不同报冲突。
4. 没有保存结果才校验审批摘要、撤销与期限。
5. effects和operations一起提交，异常统一rollback。
6. 关闭再新建Ledger模拟恢复后重试，没有新增业务效果。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java事务内业务表和幂等表同时提交；HTTP远程服务不参与SQLite事务，不能宣称跨服务exactly-once。

## 易错点与排查

- 审批只保存approved=True：改变参数后仍可能执行。
- 先写业务再单独保存幂等结果：中间崩溃会重复执行。
- 重放完成结果要求再次审批：会把已成功操作误判为失败，但结果查询仍需身份校验。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`query_operation(ledger, key, action)`。

只查询已保存操作；不存在返回unknown，不自动执行；摘要不同返回conflict；能用响应丢失案例证明查询不增加effects。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/43-approval-idempotency/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“审批绑定”与“失效与撤销”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`revoked`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

跨服务使用远端幂等键、outbox、对账及必要补偿；补偿不是事务回滚，撤销审批也不自动撤销已完成动作。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html)：连接、事务与参数化查询。
- [SQLite事务](https://www.sqlite.org/lang_transaction.html)：IMMEDIATE写事务与锁边界。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 43`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
