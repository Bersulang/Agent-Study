# 阶段 56：企业知识与工单协作助手：毕业交付：复习问题

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

先自己沿[演示源码](examples/demo.py)追踪，再展开核对。不要用最终输出文字代替对状态和权限的理解。

## 1. pending是否代表工单创建成功？

<details>
<summary>核对思路</summary>

不是。它只表示草稿已持久化、等待针对当前参数的批准；tickets写入发生在approve的成功事务中。

</details>

## 2. 标题修改为什么让旧批准失效？

<details>
<summary>核对思路</summary>

批准绑定动作内容的摘要。revise更新标题及摘要，旧digest不再等于当前记录，执行器在业务写入前拒绝。

</details>

## 3. 默认示例的重启验证覆盖什么？

<details>
<summary>核对思路</summary>

它重建Assistant并重新连接同一个本地数据库，证明持久记录可供重放。不等于实际进程崩溃、容器重启或跨服务副作用恢复。

</details>

## 4. 本地事务能保护Spring服务写入吗？

<details>
<summary>核对思路</summary>

不能。远程服务不参与这个SQLite事务，需要自己的幂等键、状态查询和结果不确定时的恢复协议。

</details>

## 用完整请求检查理解

先按默认演示核对状态，再阅读完整Assistant类：

| 调用 | 数据库变化 | 返回或拒绝 |
| --- | --- | --- |
| 查询政策 | 只读，工单数仍0 | answered，附教学来源 |
| 首次创建请求k1 | 新增A/k1的pending草稿 | pending，ticket=None |
| A批准当前digest | 同事务插入一张工单、草稿改done | done，保存ticket编号 |
| 新建Assistant连接同一库，再批准同摘要 | 不再新增工单 | 返回原done结果 |
| B批准A的k1 | 按B/k1查不到草稿，无写入 | PermissionError |

从[request](examples/demo.py)开始，只跟踪draft分支，先不要同时读所有函数；读懂后再转approve，找到唯一工单INSERT，向前核对身份、摘要、状态和时间。最后跟踪revise与cancel如何使旧路径失效。

`planner=fixture_plan`把函数作为默认依赖，调用`self.planner(question)`才能得到计划；这允许在集成中替换模型而不重写事务。`ThreadPoolExecutor.submit`返回Future，`.result()`取得该工作单元的结果或传播错误。它不是把模型的隐藏推理变成线程。

完整服务、身份和部署验证入口在[integrations](integrations/README.md)。自动练习中的solve只检查离线审批/幂等报告接口，不执行整个毕业项目，不能因该小检查通过就将本课能力标记完成。

## 迁移到自己的实现

根据[独立练习](exercises/README.md)增加一个没有在演示中直接出现的输入，预测会走哪条分支、改变哪些状态、保留哪些证据。先做自己的实现，再阅读参考答案；自动检查接口只覆盖题目明确列出的代码子集。

## 验证范围提醒

毕业验证要加入真实进程重启、失败重试和新需求回归，并披露尚未接通的外部服务。默认输出虽然使用“重启重放”标签，实际只重建对象并连接同一数据库；观察到的范围必须如实说明。
