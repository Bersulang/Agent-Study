# 阶段46：链路追踪、成本与脱敏：复习问题

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

先根据[演示源码](examples/demo.py)回答，再展开解释。复习的重点是能够预测一个新输入的执行过程。

## 1. 为什么记录异常类型而不是异常正文？

<details>
<summary>核对思路</summary>

类型能区分超时、校验等故障，正文却可能包含远端返回的敏感内容。需要更细诊断时应定义允许记录的结构化字段，而非默认全量收集。

</details>

## 2. finally与except各做什么？

<details>
<summary>核对思路</summary>

except只在匹配异常时处理并继续传播；finally在成功和失败路径都执行，用于保存计时记录。日志不能把失败改造成成功。

</details>

## 3. 脱敏递归为何必要？

<details>
<summary>核对思路</summary>

credentials这样的嵌套对象里可能有api_key。只处理顶层键会漏掉它；规则仍不能保证识别所有秘密，因此正文默认不收集。

</details>

## 用一个反例检查理解

打开[示例源码](examples/demo.py)，分别追踪span的正常路径和异常路径：

```text
进入span → 保存开始时间 → yield交给业务代码
正常返回 → finally记录status=ok与耗时
业务抛错 → except保存error_type并重新抛出 → finally记录status=error与耗时
```

默认演示只有正常lookup，因此error_type为None。不要把这一输出当成失败路径也已被演示；对应测试与独立练习应主动构造错误。

脱敏时，从result进入credentials，再遇到api_key，输出值替换为[REDACTED]。仅改变键的大小写也应受到保护，因为代码先对key执行lower。练习增加关联ID和错误信息时，检查字段是否保留，不要求最终报告句式与参考答案相同。

## 独立迁移

打开[练习要求](exercises/README.md)，先选一个正常输入和一个会触发边界的输入，写出预期业务状态，再实现。默认演示只证明本地机制；真实服务、负载或身份系统另按[集成说明](../../docs/integrations.md)验收。讲义末尾保留本课参考资料入口。

## 验证范围提醒

指标汇总一段时间的趋势，日志保存单个事件，轨迹关联同一次请求的多个步骤。本地span没有跨进程传播功能，真实OpenTelemetry接入按集成目录执行，不能把本地列表当成完整观测平台。
