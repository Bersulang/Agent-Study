# 阶段43复习：审批快照与幂等查证

关联：[讲义](README.md)、[SQLite Ledger](examples/demo.py)、[练习](exercises/README.md)。

审批摘要绑定具体close动作、ticket_id和期限；首次执行还要验证撤销和动作白名单。操作key已存在时，摘要相同就返回保存结果，摘要不同冲突。操作记录和effects同事务提交，因此重连后重复key不会再次关闭工单。

响应丢失后，先查结果再考虑是否执行。过期审批不影响已提交操作的查证；但首执行过期、撤销或动作被编辑均应拒绝且effects为0。这个保证只覆盖同一SQLite事务；跨服务写入仍需目标服务幂等和可查询结果。


## 进一步检查

`BEGIN IMMEDIATE`防止两个SQLite连接同时判断相同key不存在。成功路径插入effects和operations后一起commit；任何异常rollback。审批先绑定稳定摘要，比较时包含kind和ticket_id；将T-7改成T-8即变成approval_mismatch。撤销或now等于expires也在首执行前拒绝。

幂等重放查询已有operations后立即返回结果，不会重复消费审批或增加effects；同key但摘要不同应返回冲突，不能把旧结果交给新动作。真实跨服务业务需目标服务也支持幂等键/查证接口，因为本地SQLite事务无法回滚外部系统已发生的写操作。