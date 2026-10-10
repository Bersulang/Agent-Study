# 阶段 46：链路追踪、成本与脱敏

[课程首页](../../README.md) · [完整路线](../../docs/roadmap.md) · [本课知识](knowledge.md)

## 1. 业务场景

用户说助手很慢，需要知道耗时来自模型、检索还是工具。同时日志不能把密钥和邮件地址原样存下来。

## 2. 学习目标与前置知识

能关联一次请求的步骤，记录成功与失败耗时，并解释哪些数据不进入日志以及成本如何计算。

真正先修是Python基础、工具契约和状态/失败边界（对应阶段03—16）。本课不要求先完成30—38多Agent；可使用阶段39之后的服务或本地固定数据练习治理机制。按[项目里程碑](../../docs/milestones.md)持续把案例、权限、轨迹和发布记录合入主项目。

本课先建立下方机制的执行模型，再完成独立练习；验收时需要能预测新输入如何改变结果，而不只是复述术语。

## 3. 从问题建立机制

### 一次请求失败了，怎样找到失败的那一步

“请求失败”只能描述现象。若一次请求包含检索、模型调用和工具执行，维护者需要知道耗时花在哪里、哪个步骤失败、这些记录是否属于同一次请求。request_id连接整个请求，span给其中一段操作命名。

本课的span是一个上下文管理器。进入with时记录起点，退出时追加事件；业务语句写在with块里。这样调用方不用在每个成功与失败分支重复写计时逻辑。

### yield在这里不是生成工单，而是划分进入和退出

阶段05见过生成器的yield。`@contextmanager`把包含一次yield的函数转换成可用于with的管理器：yield之前是进入逻辑，yield把控制权交给with块，离开with时再回来执行收尾。若块内抛异常，异常会在yield位置重新出现，进入except；保存错误类型后再raise，保证日志不会吞掉业务失败。

finally负责无论成功失败都保存耗时。`perf_counter`适合测两个时点之间的持续时间，它不用于记录日历日期。日志里舍去演示耗时是为了让固定输出稳定，不表示实际耗时恒定。

### 先决定不收集什么，再讨论脱敏

redact递归检查字典和列表，遇到api_key、token、content等敏感字段用占位文字替换。递归表示对子结构应用同一规则；只遮盖最外层会漏掉credentials里的密钥。邮件正则只是补充，不是能识别任意秘密的通用保证。

错误事件保存异常类名，不保存原始异常正文。Java日志常把异常堆栈直接输出，Agent工具错误却可能夹带文档或凭证；诊断方便与数据最小化需要一起设计。

### 成本是可复核计算，不是一个模型猜测值

本例输入1000 token、输出200 token，假设每百万分别为1与2，则费用为(1000×1+200×2)/1000000=0.0014。输入和输出可能有不同单价，不能把总token统一乘一个价格。本课用假设费率讲公式，不提供供应商实时报价。

<details><summary>先预测：工具在with块里抛出异常，轨迹会丢失吗？上层还会收到异常吗？</summary>

不会丢失，finally仍追加事件，并记status=error及异常类型。裸raise继续传播原异常，上层仍需处理业务失败。只记日志后返回正常结果会改变程序语义。
</details>

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

## 5. 跟踪一次完整执行

打开[示例源码](examples/demo.py)，分别追踪span的正常路径和异常路径：

```text
进入span → 保存开始时间 → yield交给业务代码
正常返回 → finally记录status=ok与耗时
业务抛错 → except保存error_type并重新抛出 → finally记录status=error与耗时
```

默认演示只有正常lookup，因此error_type为None。不要把这一输出当成失败路径也已被演示；对应测试与独立练习应主动构造错误。

脱敏时，从result进入credentials，再遇到api_key，输出值替换为[REDACTED]。仅改变键的大小写也应受到保护，因为代码先对key执行lower。练习增加关联ID和错误信息时，检查字段是否保留，不要求最终报告句式与参考答案相同。

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

先读[练习接口与要求](exercises/README.md)，再编辑 [练习骨架](exercises/practice.py)。完成后运行自己的案例，再对照 [参考答案](solutions/solution.py)。答案只提供一种实现，你可以使用更清楚的结构，只要行为满足要求。

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

练习结果由自动校验记录，设计解释可在学习对话中讨论。先独立实现，再查看参考答案；材料测试不替代作业验收。

## 9. 企业工程边界

指标汇总一段时间的趋势，日志保存单个事件，轨迹关联同一次请求的多个步骤。本地span没有跨进程传播功能，真实OpenTelemetry接入按集成目录执行，不能把本地列表当成完整观测平台。

默认案例是本地轨迹记录器，不是完整OpenTelemetry SDK。真实集成见integrations目录，实际OTLP后端与告警需另外部署；正文和凭证采取默认不记录原则。

生产接入需要按场景明确身份、数据保留、故障恢复、容量和发布策略。本课程案例的验证范围是本地确定性行为，未调用真实外部模型或声称在生产环境通过。

## 10. 知识回顾与参考资料

复习 [本课知识文档](knowledge.md)，将实际遇到的问题写到练习记录，经分析后再同步知识手册。

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/instrumentation/)。
- [Python上下文管理器](https://docs.python.org/3.12/library/contextlib.html)。

## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 46`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
