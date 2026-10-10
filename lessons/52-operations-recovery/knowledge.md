# 阶段 52：备份恢复、事故与反馈闭环：复习问题

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

先根据[本课源码](examples/demo.py)预测行为，再展开核对。

## 1. 源文件不存在时为什么先拒绝，而不是直接connect？

<details>
<summary>核对思路</summary>

普通connect可能创建新空库，使路径错误变成看似成功的备份。源存在检查与只读连接能把这种失败保留下来。

</details>

## 2. integrity_check为什么不够？

<details>
<summary>核对思路</summary>

它检查数据库格式层面的完整性，不知道应用需要tasks表及哪些列。业务结构与实际状态必须另查。

</details>

## 3. 为什么反馈先标pending_review？

<details>
<summary>核对思路</summary>

重复去除只解决重复记录，不证明反馈正确。来源、脱敏和审核决定能否进入正式评估集。

</details>

## 把规则放回一次执行

默认演示的执行顺序如下：

1. 在临时source库建立tasks表，插入(t1, approved)，事务提交并关闭连接。
2. snapshot只读打开source，以backup接口写入新的backup库。
3. restore检查backup格式、表和列，复制到新的restored库。
4. 重新连接restored，实际查询得到(t1, approved)。它证明状态在本次本地恢复中保留，不仅仅是文件存在。
5. 退出临时目录，三个数据库被清理；随后两条相同反馈合并成一个pending_review候选。

[示例源码](examples/demo.py)中的`fetchone()[0]`先取一行，再取这一行的第一列；SQL的问号占位符绑定数据值，避免把输入拼进SQL。`tables`和`columns`用集合做成员检查，因此目标是所需结构是否存在，不是查询结果顺序是否固定。

练习的solve适配器检查离线恢复报告，不等于运行本节的数据库恢复过程。完整能力验收仍应实际恢复到隔离库并核对业务记录。

## 独立迁移

根据[练习要求](exercises/README.md)构造一个正常案例和一个边界案例，先说清楚预计改变的状态与必须保留的状态，再写代码。命令日志自动保存，完整服务能力另按[集成说明](../../docs/integrations.md)验收。

## 验证范围提醒

恢复完成后的核查应包含记录数量、状态分布和业务约束。只显示“数据库可打开”没有证明任务是否完整，也没有证明新应用版本能继续推进这些状态。
