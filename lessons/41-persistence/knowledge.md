# 阶段41复习：事务提交与新连接恢复

关联：[讲义](README.md)、[SQLite示例](examples/demo.py)、[练习](exercises/README.md)。

save使用expected_version做乐观更新。rowcount不为1时报version_conflict；成功更新和audit插入在同一连接事务内。模拟提交前崩溃会使两者一起回滚。关闭连接后用新Store读取，确认状态来自磁盘。

连接上下文负责commit/rollback，不负责关闭连接，需finally/close。CREATE TABLE IF NOT EXISTS不是迁移工具；生产还要迁移版本、保留策略、备份和并发验证。


## 进一步检查

冲突案例中第一次save将version 0改为1；第二次仍提交expected_version 0，因此更新行数为0并回滚，状态保留ready/version1。异常案例在audit插入前发生，状态更新也一起撤销。最终新连接读取避免误把Python对象缓存当磁盘恢复。

参数化SQL中的问号和tuple值分离代码与数据，避免把task_id拼接进查询。示例没有数据库迁移脚本、并发压测或备份恢复；CREATE TABLE IF NOT EXISTS仅初始化表结构，不保证已有生产表自动升级。