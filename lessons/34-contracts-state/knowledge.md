# 阶段34复习：版本冲突与原子合并

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

merge先比较expected_version，再验证patch字段恰好为status且值属于ready/blocked。全部检查后才update并递增version；返回副本供外部读取。冲突或非法字段都在状态变更前失败。

先预测：patch含合法status和额外private_reason，status会先更新吗？不会，整份字典先验证。merge_many要先验证全部patch，再一次更新状态、版本只加1；中间失败时输入state保持原样。Java数据库可使用乐观锁version列和事务实现类似约束，本地字典不提供跨进程并发保护。


## 进一步检查

示例的patch只允许一个status键，因此使用`set(patch)`比较整个字段集合：多字段补丁会拒绝，而不是忽略未知字段后部分更新。返回`dict(state)`保护内部外层字典，但它仍是浅复制。expected_version失败不会增加version，避免两个调用者基于同一旧状态都成功覆盖。

批量合并应先复制候选状态并验证每一项，再一次写回原状态。注意不能每合一项就加version，否则第3项失败时前两项已泄漏出去。生产数据库要依赖事务与条件UPDATE，Python字典的单线程演示不提供并发原子性。