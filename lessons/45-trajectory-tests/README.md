# 阶段 45：执行过程与回归测试

[课程首页](../../README.md) · [完整路线](../../docs/roadmap.md) · [本课知识](knowledge.md)

## 1. 业务场景

工单助手最后回答“已创建”，不代表创建动作合规。它可能跳过审批，或者调用两次。需要把实际执行事件作为测试对象。

## 2. 学习目标与前置知识

能逐事件推进审批、写入次数和终态，指出一段不合规轨迹最先在哪一步失败。

真正先修是Python基础、工具契约和状态/失败边界（对应阶段03—16）。本课不要求先完成30—38多Agent；可使用阶段39之后的服务或本地固定数据练习治理机制。按[项目里程碑](../../docs/milestones.md)持续把案例、权限、轨迹和发布记录合入主项目。

本课先建立下方机制的执行模型，再完成独立练习；验收时需要能预测新输入如何改变结果，而不只是复述术语。

## 3. 从问题建立机制

### 最后答对，不表示过程合规

假设助手最后告诉用户“工单已创建”。它可能在没有批准时就写入，也可能创建了两次，只展示最后一个结果。单看回答文字无法发现这些问题，所以本课记录实际执行事件，并检查它们发生的顺序。

这里的轨迹不是模型隐藏思维，而是程序能观察到的动作：started、read、approved、write、finished。每个事件都对应执行边界。日志只有确实在相应步骤记录，才能作为证据；不能让模型自己编造一串看起来合理的事件。

### 把规则写成状态变化

validate_trace从三个状态开始：approved=False、writes=0、finished=False。遇到approved只改变批准状态，不会立即写入；遇到revoked把批准恢复为False；遇到write才同时检查调用身份是否authorized，以及当前是否approved。

这说明“曾经批准过”不是足够条件，写入发生时必须仍有有效批准。写入计数超过1会失败，用来保护本教学任务“一次业务写入”的约定。现实中允许多个写动作的任务要定义自己的动作键和次数规则，不能照搬这个数字。

### 结束状态为什么必须检查两次

循环每次先看finished：一旦结束，后续任何事件都不应出现。循环结束后再检查是否曾到达finished，否则一段中途截断的轨迹不能声称完整成功。前者拒绝“结束后又动手”，后者拒绝“还没结束就验收”。

Java中可以把这看作一个状态机校验器。异常类型也表达责任：缺少权限/审批用PermissionError，未知事件、重复写入或不完整轨迹用ValueError；它们不是统一替换为False的无差别失败。

<details><summary>先预测：started → approved → revoked → write → finished会通过吗？</summary>

不会。处理revoked后approved变回False。读到write时立即抛PermissionError，写入计数不会增加，也不会继续处理finished。
</details>

## 4. 操作演示

默认案例使用 Python 标准库，固定本地数据，无需网络和模型密钥。以下命令从项目根目录运行：

```powershell
.\.venv\Scripts\python.exe .\lessons\45-trajectory-tests\examples\demo.py
```

本机示例输出：

```text
合规轨迹： {'valid': True, 'writes': 1}
违规轨迹： 写入前缺少权限或有效审批
```

先预测结果，再运行；不要只看最后一行，观察成功和失败请求是怎样分流的。

## 5. 跟踪一次完整执行

在源码[validate_trace](examples/demo.py)中跟踪成功轨迹：

| 读到的事件 | approved | writes | finished |
| --- | --- | --- | --- |
| started后初始化 | False | 0 | False |
| read | False | 0 | False |
| approved | True | 0 | False |
| write | True | 1 | False |
| finished | True | 1 | True |

合法轨迹返回valid=True、writes=1。反例started→write在进入write分支时就被拒绝。即使之后列表里写着approved，也不会“补救”已经不合规的顺序。

阅读代码中的`elif`时，每个事件只匹配其中一个分支。`event not in {"read", "planned"}`是在排除允许但不改变这些状态的事件；漏写它会让拼错的事件名称静默通过。独立练习再加入撤销与终态案例，用轨迹证明规则，而不是在最终回答中搜索“已审批”。

## 6. 常见错误与排查

| 症状 | 原因 | 排查与修复 |
| --- | --- | --- |
| 答案正确但未审批 | 只评分最终文本 | 读取实际工具事件并检查时序 |
| 测试绑死每个模型步骤 | 断言不稳定的精确轨迹 | 检查业务不变量和允许的动作集合 |
| 重复写入没发现 | 只检查是否曾经成功 | 累计实际写入次数 |

排查时保留输入类别、状态与错误码；涉及身份、密钥和业务数据时，先脱敏再记录。一次运行成功只能证明当前案例，必须覆盖变化后的需求和失败路径。

## 7. 独立练习

1. 扩展撤销事件 revoked，批准后撤销的轨迹不能写入。
2. 允许没有写入的只读任务正常结束，但禁止finished之后动作。
3. 构造批准前写入、重复写入、撤销后写入三条违规轨迹。

先读[练习接口与要求](exercises/README.md)，再编辑 [练习骨架](exercises/practice.py)。完成后运行自己的案例，再对照 [参考答案](solutions/solution.py)。答案只提供一种实现，你可以使用更清楚的结构，只要行为满足要求。

```powershell
.\.venv\Scripts\python.exe .\lessons\45-trajectory-tests\exercises\practice.py
.\.venv\Scripts\python.exe .\lessons\45-trajectory-tests\solutions\solution.py
```

## 8. 测试与能力验收

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s .\lessons\45-trajectory-tests\tests -v
```

测试针对真实教学函数的成功和失败行为。练习尚未完成时，参考实现测试通过不能证明你的实现也正确，你需要为新增需求编写案例。

用一条“最终答案相同、轨迹不同”的案例证明检查有效；解释何时做契约测试，何时做端到端测试。

练习结果由自动校验记录，设计解释可在学习对话中讨论。先独立实现，再查看参考答案；材料测试不替代作业验收。

## 9. 企业工程边界

这个函数审计给定事件，不会回滚已经发生的远程副作用。真实轨迹还要绑定任务ID、稳定序号和可信事件来源，端到端业务测试则核对实际写入结果；两个层面的证据要一起看。

示例检查离线结构化事件。生产事件需由执行器或业务服务生成，不能信任模型自述“我批准了”；审批身份与参数绑定见阶段43。

生产接入需要按场景明确身份、数据保留、故障恢复、容量和发布策略。本课程案例的验证范围是本地确定性行为，未调用真实外部模型或声称在生产环境通过。

## 10. 知识回顾与参考资料

复习 [本课知识文档](knowledge.md)，将实际遇到的问题写到练习记录，经分析后再同步知识手册。

- [Python unittest](https://docs.python.org/3.12/library/unittest.html)。

## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 45`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
