# 阶段22复习：按子问题查证据并及时停止

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习契约](exercises/README.md)。

这节的topics已经由调用者分解。`research`每次对一个主题查内存表，trace记录查询尝试，evidence只记录命中，missing列出未覆盖主题。证据数量与查询数量可能不同。

预算在访问知识前检查；同一命中主题会复用已有证据。演示以budget=2处理发票、审批、期限，前两项成功后停止，期限缺失，因此status是partial而不是complete。不能因部分命中就编造剩余条件。

先预测：topics中连续两次出现“期限”且第一次未命中，演示会为第二次再查一次吗？会，因为现有实现只复用命中项。练习要求先按首次出现顺序去重，让重复的未命中主题也不重复消耗预算。budget=0则在第一次查询前停止。

Java中可用`LinkedHashSet`保序去重，使用额度对象记录查询数。固定知识表和人工传入主题只验证编排控制，不证明自动分解、外部检索或答案质量。完成[练习](exercises/README.md)时分别核对complete、knowledge_missing和budget_exhausted。
