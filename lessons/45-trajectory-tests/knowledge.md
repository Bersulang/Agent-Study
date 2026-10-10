# 阶段45：执行过程与回归测试：复习问题

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

先根据[演示源码](examples/demo.py)回答，再展开解释。复习的重点是能够预测一个新输入的执行过程。

## 1. 为什么不能只检查事件列表含approved？

<details>
<summary>核对思路</summary>

列表包含不等于顺序正确。批准必须在写入之前，并且没有在写入前被撤销；需要逐项推进状态。

</details>

## 2. 为什么started、read还不能作为成功？

<details>
<summary>核对思路</summary>

轨迹尚未到达finished，可能因超时或崩溃中断。完整性与某些局部步骤成功是两件事。

</details>

## 3. 轨迹校验是否证明模型推理正确？

<details>
<summary>核对思路</summary>

不证明。它只检查程序记录的可观察动作及约定顺序；内容质量要用阶段44的证据与评估标准另验。

</details>

## 用一个反例检查理解

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

## 独立迁移

打开[练习要求](exercises/README.md)，先选一个正常输入和一个会触发边界的输入，写出预期业务状态，再实现。默认演示只证明本地机制；真实服务、负载或身份系统另按[集成说明](../../docs/integrations.md)验收。讲义末尾保留本课参考资料入口。

## 验证范围提醒

这个函数审计给定事件，不会回滚已经发生的远程副作用。真实轨迹还要绑定任务ID、稳定序号和可信事件来源，端到端业务测试则核对实际写入结果；两个层面的证据要一起看。
