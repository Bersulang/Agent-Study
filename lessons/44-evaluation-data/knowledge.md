# 阶段44：评估数据与质量标准：复习问题

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

先根据[演示源码](examples/demo.py)回答，再展开解释。复习的重点是能够预测一个新输入的执行过程。

## 1. 为什么用Counter比较ID，而不是只比较集合？

<details>
<summary>核对思路</summary>

集合能发现缺失或多余ID，却会抹掉重复次数。一题返回两次仍是数据错误；先拒绝再计分，不能让重复答案影响分母。

</details>

## 2. release_allowed等于最终可发布吗？

<details>
<summary>核对思路</summary>

不等于。evaluate中的标记只检查安全违规，release_decision还看总体和类别门槛。把两个函数合起来阅读才能知道实际发布条件。

</details>

## 3. 模型评分与人工不一致时怎样处理？

<details>
<summary>核对思路</summary>

先记录分歧ID，再依据证据与评分标准复核。评分模型的自信程度不能替代事实来源。

</details>

## 用一个反例检查理解

沿着三个固定案例追踪evaluate，而不是只看输出小数：

| 执行点 | 输入/当前状态 | 产生的变化 |
| --- | --- | --- |
| 检查ID | 3个案例与3个对应预测 | 允许进入计分 |
| normal-1 | answer对answer | normal累计1次通过 |
| missing-1 | unavailable对unavailable | no_evidence累计1次通过 |
| unsafe-1 | answer对deny | security不加通过数，记录违规ID |
| 生成报告 | 总计2次通过、3道题 | success_rate为2/3，安全发布标记为False |

先在循环内观察correct，再观察passes和violations，就能解释为什么“总体还不错”与“必须拒绝发布”可以同时成立。练习增加clarify类别时，重点是它是否进入总分母和类别分母，而不是报告多打印了一个词。

`by_id = {row["id"]: row["action"] for row in predictions}`是字典推导式：逐个读取row，以id为键保存action。它必须放在重复ID校验之后，否则重复键会被后来的值覆盖，使数据问题消失。

## 独立迁移

打开[练习要求](exercises/README.md)，先选一个正常输入和一个会触发边界的输入，写出预期业务状态，再实现。默认演示只证明本地机制；真实服务、负载或身份系统另按[集成说明](../../docs/integrations.md)验收。讲义末尾保留本课参考资料入口。

## 验证范围提醒

空评估集与重复案例ID在计分前拒绝；release_decision还要显式检查类别集合非空，因为all在空集合上会返回True。三个固定案例只用于核查计分机制，不是用户流量样本，不能由此推断真实模型准确率。
