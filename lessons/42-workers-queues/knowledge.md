# 阶段42知识：Worker队列与租约

## 关联

[课程讲义](README.md) · [运行示例](examples/demo.py) · [练习](exercises/README.md)

## 概念与业务落点

### API与Worker分离

入口持久接收请求，工作者独立执行耗时任务。

api与worker使用两个真实SQLite连接。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 至少一次投递

消息可能重复抵达，处理端必须识别逻辑重复。

jobs主键使两次enqueue同一T-7仍只有一条任务。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 租约

一段有限时间内任务归某个Worker处理，过期后可重新领取。

worker-a到110过期，worker-b在111接手。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### Fencing token

每次领取递增编号，业务提交只接受当前编号。

token1的旧worker提交失败，token2成功且effects为1。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

## 状态与失败路径

- isolation_level=None启用显式事务管理。
- BEGIN IMMEDIATE先获得写锁，把SELECT和UPDATE放在一个事务。
- claim对done或未过期leased返回None。
- 每次重新领取token加一，防止旧owner凭过期租约提交。
- complete条件同时验证owner、token、state和有效期。
- effects与done在同一事务写入；两个连接finally显式关闭。

## 易错解释

- 只写owner不写token：同名Worker重启可能冒充旧领取。
- 锁过期后旧Worker继续写外部系统：锁本身不能阻止旧执行者。
- SQLite队列叫生产消息代理：它没有分布式broker的调度与确认能力。

## Java对照

类似Java任务表轮询加乐观锁，但锁住数据库行不代表锁住远程业务系统；远端也需接收幂等键或fencing token。

## 独立迁移

只有当前owner/token且租约尚未过期才可续租；过期拒绝；新Worker接管后旧token不能续租。

## 工程限制

生产队列需要可见性超时、死信、指数退避、吞吐监控；租约时间必须来自一致的时间来源并考虑暂停和时钟偏差。

默认行为是教学机制，不等于模型质量证明或生产系统认证。验收必须由学员独立完成并提供证据。
