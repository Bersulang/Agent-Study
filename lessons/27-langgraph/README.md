# 阶段 27：LangGraph状态与中断

## 使用场景

把手写的审核流程迁移成图，审批暂停后必须使用同一任务状态恢复。

主线项目是企业知识与工单协作助手。本阶段只增加一个可解释的能力边界，先验证机制，再讨论规模化。
运行演示不需要模型密钥，也不会请求真实业务系统。

## 学习目标

- 能追踪draft、waiting、done/rejected四种状态的允许转移。
- 能说明无decision时为何保持waiting，以及拒绝如何成为终态。
- 能把任务ID与审批摘要绑定，阻止批准恢复到另一个任务。

## 前置知识

真正先修是阶段13—16的循环、状态与审批，以及阶段25的恢复概念；若只预习可先看本地step函数，真实checkpointer留待集成验收。

## 概念

`step`先复制输入状态，再按stage做单步转换：draft进入waiting；waiting遇到None仍保持等待；收到布尔decision才转done或rejected；终态再次进入时不变。非布尔审批值抛ValueError。

下面摘录或简化本课示例的关键步骤，需结合[完整源码](examples/demo.py)中的定义与上下文阅读；运行时使用下方演示命令。

```python
if state["stage"] == "waiting":
    if decision is None:
        return next_state
    if not isinstance(decision, bool):
        raise ValueError("审批决定必须为布尔值")
    next_state["stage"] = "done" if decision else "rejected"
```

先预测：`step(waiting_state, False)`得到什么？新的stage是rejected，approved=False；原状态仍是waiting。这里做浅复制，本例只改外层字段；若节点要改嵌套对象，必须重新设计状态所有权。

反例：恢复时只检查approved而不核对task和摘要，可能把T1批准用于T2。练习将审批绑定到同一task/digest，并拒绝过期或不匹配记录。真实LangGraph还需持久checkpointer和节点重跑幂等，单次调用这个纯函数不证明副作用只发生一次。

## 演示文件与执行命令

默认工作目录是项目根目录 `C:\Users\Mason\Desktop\agent-study`。
如已创建虚拟环境，可以把python替换成 `.\.venv\Scripts\python.exe`，无需激活或修改执行策略。

```powershell
python lessons/27-langgraph/examples/demo.py
python lessons/27-langgraph/solutions/solution.py
python -m unittest discover -s lessons/27-langgraph/tests -v
```

第一条运行演示；第二条仅在完成练习后阅读与运行；第三条执行本阶段行为检查。
`-m`表示让解释器把模块当入口，`discover`搜寻test_开头文件，`-s`指定测试目录，`-v`显示每个测试名字。
测试正常时结尾是 `OK`。故意运行未完成的练习函数出现NotImplementedError，代表你还需要实现，不代表环境坏了。

### 默认演示预期输出

```text
{'stage': 'waiting', 'task': 'T1'}
{'stage': 'rejected', 'task': 'T1', 'approved': False}
```

### 预期输出如何阅读

第一次step把输入draft复制并转成waiting；第二次给False后得到rejected和approved=False。打印的第一份waiting状态未被第二次调用改写，展示了单步状态转换与暂停点。

## 执行过程与状态变化

1. draft到waiting。
2. 未提供决定保持暂停。
3. 决定必须为bool，拒绝进入rejected。
4. 默认纯函数与integrations真实状态图对照。

默认输出先显示由draft派生的waiting副本，再显示收到False后得到的rejected副本；输入字典没有被直接改写。

## 对照源码的逐行解释

按examples/demo.py中的顺序阅读，下列关键表达式决定正常与失败路径。

| 表达式或位置 | 为什么这样写及状态变化 |
|---|---|
| `next_state = dict(state)` | 创建新状态以便测试原输入未变；嵌套数据仍需设计更新策略。 |
| `draft到waiting` | 准备完成后等待决定，不能在缺少审批时直接done。 |
| `decision is None` | 用None区分没有决定与明确拒绝False；if not decision会把两者混为一谈。 |
| `isinstance(decision, bool)` | 严格要求审批是布尔，字符串yes不能被真值规则误认为有效批准。 |
| `终态` | done或rejected再次执行保持不变；未知状态抛错，避免从损坏检查点任意继续。 |
| `框架迁移` | 真实图节点返回字段更新，条件边选择后继，检查点按thread_id保存；恢复Command不会自动提供业务授权。 |
| `子图与中断` | 子图封装局部流程；interrupt节点恢复可能重跑中断前代码，真实写入应放审批后且使用幂等键。 |

## Java Web对照

Java常用枚举与不可变状态对象限制转移；本课用字典演示状态更新，浅复制不会复制嵌套值，框架恢复还须绑定同一任务与审批摘要。

## 易错点与排错顺序

1. 文件路径错误：确认终端在项目根目录，先运行演示而不是练习骨架。
2. 把空结果当成功：查返回状态与来源，不能编造缺失字段或证据。
3. 在失败后继续修改：先验证再变更，给失败输入补行为测试。
4. 共享可变对象：调用前后打印输入，确认是否被无意修改。
5. 把模拟效果当生产质量：检查本页边界说明与真实接入目录。
6. 只看最终回答：保留查询、状态或执行轨迹，定位失败发生在哪一步。

## 独立练习

增加审批动作摘要，在恢复时检查task与摘要一致；过期审批不能恢复另一个任务。然后对照真实LangGraph集成说明节点重跑的副作用风险。

打开 [练习要求](exercises/README.md)，在 [practice.py](exercises/practice.py) 实现。
骨架有意留下待实现函数，示例和参考答案不能替代你自己的思考与测试。
自动校验保存状态转换与绑定拒绝；真实checkpointer和节点副作用仍须独立集成验收。

## 能力验收

- 能不看代码解释至少三个概念，并各举一个企业助手场景。
- 能预测演示执行前后的关键字段，再通过运行核对。
- 能独立修改一项业务规则并解释对结果的影响。
- 能让一个失败输入按预期被拒绝，且不产生越权或错误证据。
- 能说明本课测试证明了什么、没有证明什么。

材料制作、代码验证、学员掌握是三种状态；本课提供材料与验证方法，学员能力仍待验收。

## 工程延伸与边界

默认手写状态机不是LangGraph。真实SDK图、中断与InMemorySaver位于integrations；内存Saver不提供跨进程持久恢复。

从本课迁移到企业项目时，先写输入输出契约与独立评估案例，再决定存储、模型和框架。
保留可追溯来源和任务/身份信息，让问题能定位到具体数据与步骤。
添加性能优化前先检查正确性，尤其是失败时是否仍保护权限、预算和有效状态。
单元测试覆盖本地规则；真实网络、持久化、并发与供应商行为需要额外集成验证。

## 官方资料与复习

- [本课官方参考](https://docs.langchain.com/oss/python/langgraph/interrupts)：查API或协议边界，不要求一次读完。
- [Python 3.12教程](https://docs.python.org/zh-cn/3.12/tutorial/)：复习循环、函数、异常和模块。
- [本课知识卡](knowledge.md)：按定义、案例、误区整理。
- [验证记录](verification.md)：仅记录实际执行范围，不能据此声称生产部署通过。

## 真实集成入口

打开[集成说明](integrations/README.md)，按独立环境安装和验证；默认运行无需安装这些依赖。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 27`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
