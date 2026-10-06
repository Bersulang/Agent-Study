# 阶段 46 知识：链路追踪、成本与脱敏

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

### 1. Trace与Span

Trace是一条请求的整体链路，Span是其中一个步骤。父子Span建立调用关系，错误和耗时在步骤上记录。Java的链路追踪概念相同，但跨线程或协程要显式传播上下文。

### 2. 指标与成本

指标汇总数量、错误和延迟；日志保存离散事件；轨迹关联步骤。Token计费估算必须带模型和价格版本，示例每百万Token价格仅为假设值，不代表供应商实际价格。

### 3. 结构化脱敏

根据字段白名单和敏感键过滤，比随意输出对象安全。递归处理嵌套字典，正文默认不记录；文本替换只是补充，不能保证识别全部敏感信息。

## 执行过程

使用上下文管理器包围一个步骤；进入时记录单调时钟，退出时保存耗时和状态，即使发生异常也会记录；emit递归脱敏后输出结构化事件；Token价格按输入输出分别计算。

## 新语法

`@contextmanager` 把包含yield的生成器变成with上下文；finally即使异常也执行；perf_counter提供单调计时，不能当作日历时间。

## 判断与排错

| 密钥出现在嵌套字段 | 只过滤顶层 | 递归处理字典和列表，默认不记录正文 |
| 时间差为负 | 使用可被校时的墙上时钟 | 步骤耗时使用perf_counter |
| 成本没有价格依据 | 混用模型或价格单位 | 保存价格版本与每百万单位 |

## 工程边界

默认案例是本地轨迹记录器，不是完整OpenTelemetry SDK。真实集成见integrations目录，实际OTLP后端与告警需另外部署；正文和凭证采取默认不记录原则。

## 复习问题

解释指标、日志、轨迹差别；演示嵌套密钥脱敏和失败Span；说明假设价格不是实际账单。

## 资料

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/instrumentation/)。
- [Python上下文管理器](https://docs.python.org/3.12/library/contextlib.html)。

## 练习扩展与新验证边界

Span增加error_type，仅保存异常类名；原始异常正文不进入事件。contextmanager中yield前是进入逻辑，yield后/except/finally接收with块的完成或异常；重新raise保留上层失败处理。参考答案将model与tool关联同一个request_id。

对应实现与完整失败案例见[参考答案说明](solutions/README.md)，完成练习后再阅读。
