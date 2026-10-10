# 阶段42复习：租约与fencing

关联：[讲义](README.md)、[SQLite队列](examples/demo.py)、[练习](exercises/README.md)。

同一job_id由主键去重。领取在BEGIN IMMEDIATE事务内完成查询和更新；有效租约阻止第二个Worker领取。租约过期后新Worker得到更高token。complete只有owner、token、state、expires都匹配才提交done和effects。

旧Worker持token1、接管者持token2时，旧提交被拒绝；fencing token防止过期执行者覆盖新结果。外部HTTP无法与SQLite同事务，所以仍须对端幂等。练习续租时要求当前token且租约尚未过期。


## 进一步检查

领取条件使用`expires > now`判定租约仍有效，因此now恰等于expires时可被新Worker领取；complete使用`expires > now`，边界相同时旧Worker不能提交。`BEGIN IMMEDIATE`把竞争领取串行化，异常时显式ROLLBACK。队列和effects表在本地同库，所以效果计数原子；远端HTTP做不到共享事务。

练习renew必须验证job仍leased、owner/token当前、租约未过期且ttl为正，再更新expires。过期租约不能由旧owner续活；新Worker拿到更高token后，fencing条件让旧写入无法覆盖。