# 阶段 46：链路追踪、成本与脱敏

[课程首页](../../README.md) · [完整路线](../../docs/roadmap.md) · [本课知识](knowledge.md)

## 1. 业务场景

用户说助手很慢，需要知道耗时来自模型、检索还是工具。同时日志不能把密钥和邮件地址原样存下来。

## 2. 学习目标与前置知识

先完成前面的 Python、工具、状态和协作基础。本课重点是理解机制，能够修改并验证代码。遇到不理解的语法先查看本课语法说明，再回到基础阶段复习。

学习完成后，能独立完成下方新需求，说明失败条件，并用测试检验结果。材料准备完毕不表示已经通过能力验收。

## 3. 关键概念

### 1. Trace与Span

Trace是一条请求的整体链路，Span是其中一个步骤。父子Span建立调用关系，错误和耗时在步骤上记录。Java的链路追踪概念相同，但跨线程或协程要显式传播上下文。

### 2. 指标与成本

指标汇总数量、错误和延迟；日志保存离散事件；轨迹关联步骤。Token计费估算必须带模型和价格版本，示例每百万Token价格仅为假设值，不代表供应商实际价格。

### 3. 结构化脱敏

根据字段白名单和敏感键过滤，比随意输出对象安全。递归处理嵌套字典，正文默认不记录；文本替换只是补充，不能保证识别全部敏感信息。

## 4. 操作演示

默认案例使用 Python 标准库，固定本地数据，无需网络和模型密钥。以下命令从项目根目录运行：

```powershell
.\.venv\Scripts\python.exe .\lessons\46-observability\examples\demo.py
```

本机示例输出：

```text
轨迹： [{'request_id': 'request-001', 'span': 'lookup', 'status': 'ok', 'error_type': None}]
脱敏结果： {'count': 2, 'credentials': {'api_key': '[REDACTED]'}}
假设成本： 0.0014
```

先预测结果，再运行；不要只看最后一行，观察成功和失败请求是怎样分流的。

## 5. 代码执行过程与新语法

使用上下文管理器包围一个步骤；进入时记录单调时钟，退出时保存耗时和状态，即使发生异常也会记录；emit递归脱敏后输出结构化事件；Token价格按输入输出分别计算。

### 本课语法提示

`@contextmanager` 把包含yield的生成器变成with上下文；finally即使异常也执行；perf_counter提供单调计时，不能当作日历时间。

函数的参数表示需要提供的信息，返回值表示结果。异常表示当前调用不能继续，不能简单吞掉所有异常；需要将失败类别传给上层处理。注释与讲义共同解释关键决策。

## 6. 常见错误与排查

| 症状 | 原因 | 排查与修复 |
| --- | --- | --- |
| 密钥出现在嵌套字段 | 只过滤顶层 | 递归处理字典和列表，默认不记录正文 |
| 时间差为负 | 使用可被校时的墙上时钟 | 步骤耗时使用perf_counter |
| 成本没有价格依据 | 混用模型或价格单位 | 保存价格版本与每百万单位 |

排查时保留输入类别、状态与错误码；涉及身份、密钥和业务数据时，先脱敏再记录。一次运行成功只能证明当前案例，必须覆盖变化后的需求和失败路径。

## 7. 独立练习

1. 加入错误步骤，日志必须保留错误类型而不保留异常中的敏感正文。
2. 增加request_id关联，同一请求的工具和模型步骤使用同一ID。
3. 按输入和输出Token计算成本，拒绝负数。

编辑 [练习骨架](exercises/practice.py)。完成后运行自己的案例，再对照 [参考答案](solutions/solution.py)。答案只提供一种实现，你可以使用更清楚的结构，只要行为满足要求。

```powershell
.\.venv\Scripts\python.exe .\lessons\46-observability\exercises\practice.py
.\.venv\Scripts\python.exe .\lessons\46-observability\solutions\solution.py
```

## 8. 测试与能力验收

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s .\lessons\46-observability\tests -v
```

测试针对真实教学函数的成功和失败行为。练习尚未完成时，参考实现测试通过不能证明你的实现也正确，你需要为新增需求编写案例。

解释指标、日志、轨迹差别；演示嵌套密钥脱敏和失败Span；说明假设价格不是实际账单。

提交你的代码、操作结果、错误排查记录和设计解释。验收至少检查：能解释机制、能完成新需求、能定位故障、能给出验证依据。

## 9. 企业工程边界

默认案例是本地轨迹记录器，不是完整OpenTelemetry SDK。真实集成见integrations目录，实际OTLP后端与告警需另外部署；正文和凭证采取默认不记录原则。

生产接入需要按场景明确身份、数据保留、故障恢复、容量和发布策略。本课程案例的验证范围是本地确定性行为，未调用真实外部模型或声称在生产环境通过。

## 10. 知识回顾与参考资料

复习 [本课知识文档](knowledge.md)，将实际遇到的问题写到练习记录，经分析后再同步知识手册。

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/instrumentation/)。
- [Python上下文管理器](https://docs.python.org/3.12/library/contextlib.html)。

## 源码分段追踪与Java对照

### 输入和初始化

events由请求入口创建，span函数在同一个列表追加步骤结果。

request_id将model和tool两个步骤关联起来，不把用户Token当请求ID。

perf_counter适合计算经过时间，不用于审批日期或跨机器时间戳。

@contextmanager把包含yield的生成器变为上下文管理器。

进入with先记录start；执行到yield时把控制权交给调用方的代码块。

### 校验与状态推进

代码块抛Exception后，异常重新进入生成器的except分支。

except只保存type(error).__name__，不把str(error)放进日志。

raise不带新对象时重新抛出原异常，上层仍能处理超时。

finally在成功和失败都执行，所以失败步骤不会从轨迹消失。

error_type成功时是None，失败时例如TimeoutError。

duration_ms来自结束减开始；各次运行不同，测试不要断言固定时长。

日志脱敏先根据字段名遮盖token、content等敏感值。

嵌套字典与列表递归处理，不能只清理第一层api_key。

### 失败与验证证据

文本里的邮箱正则只是补充，不能保证消除所有个人信息。

正文默认不记录，比猜测正文里哪些词敏感更可靠。

estimate_cost分别计算输入与输出，再除以一百万。

1000输入、200输出、单价1与2得到0.0014，仅是假设货币单位。

用量或价格负数说明数据错误，不能返回负账单抵消成本。

指标汇总趋势，日志记录单条事件，轨迹关联一次请求的各步骤。

本地span没有跨进程传播功能，真实OTel接入见集成目录。

### Java Web迁移

contextmanager类似Java try-with-resources，但yield把with内部异常送回生成器；finally记录失败后仍重抛。OTel Span和MDC请求ID与此对应，指标和日志仍有不同职责。

完整练习覆盖说明见[参考答案说明](solutions/README.md)，请在完成练习后阅读。
