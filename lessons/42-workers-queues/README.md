# 阶段 42：Worker队列与租约

## 使用场景

API先记录任务，Worker稍后领取；一个Worker暂停太久后另一个接手，旧Worker不得提交。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能处理重复投递、原子领取、过期接管，并用fencing token拒绝旧执行者。

- 前置：阶段41的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：租约过期后用token隔离旧Worker

`enqueue`以job id主键去重。`claim`用`BEGIN IMMEDIATE`把读取当前状态和写入lease放进一个写事务；未过期任务不能被第二个Worker拿走。租约过期可接管，token递增。`complete`同时检查owner、token、状态和expires，并把done与effects放在同一事务。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
updated = self.db.execute(
    "UPDATE jobs SET state='done' WHERE id=? AND owner=? AND token=? "
    "AND state='leased' AND expires>?",
    (job_id, owner, token, now))
```

<details><summary>先预测：worker-a持token1停顿，worker-b到期后领取token2；a再提交会怎样？</summary>

WHERE匹配不到，stale_accepted=False；b提交后effects只为1。未到期时第二次claim返回None。

</details>

反例：先SELECT、离开事务后再UPDATE会让两个Worker都以为自己拿到工作；只有租约没有fencing token，旧Worker恢复后仍可能覆盖新结果。Python取消/超时也不能撤回已发出的外部HTTP副作用，外部系统还需幂等键。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/42-workers-queues/examples/demo.py
python -m unittest discover -s lessons/42-workers-queues/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
duplicate {'jobs': 1, 'effects': 1, 'status': 'done'}
lease {'first_token': 1, 'second_token': 2, 'stale_accepted': False, 'effects': 1}
busy {'second_claim': None, 'status': 'leased'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""SQLite 本地租约队列：唯一投递键、原子领取、fencing token拒绝旧Worker。"""
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

class Queue:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, state TEXT, owner TEXT, expires REAL, token INTEGER);
            CREATE TABLE IF NOT EXISTS effects(job_id TEXT PRIMARY KEY);
        """)

    def enqueue(self, job_id):
        self.db.execute("INSERT OR IGNORE INTO jobs VALUES (?, 'pending', NULL, 0, 0)", (job_id,))

    def claim(self, job_id, owner, now, ttl=10):
        # 显式写事务串行化领取，不能先SELECT再在事务外UPDATE。
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT state,expires,token FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None or row[0] == "done" or (row[0] == "leased" and row[1] > now):
                self.db.execute("COMMIT")
                return None
            token = row[2] + 1
            self.db.execute("UPDATE jobs SET state='leased',owner=?,expires=?,token=? WHERE id=?",
                            (owner, now + ttl, token, job_id))
            self.db.execute("COMMIT")
            return token
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def complete(self, job_id, owner, token, now):
        self.db.execute("BEGIN IMMEDIATE")
```

按执行顺序追踪：

1. isolation_level=None启用显式事务管理。
2. BEGIN IMMEDIATE先获得写锁，把SELECT和UPDATE放在一个事务。
3. claim对done或未过期leased返回None。
4. 每次重新领取token加一，防止旧owner凭过期租约提交。
5. complete条件同时验证owner、token、state和有效期。
6. effects与done在同一事务写入；两个连接finally显式关闭。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java任务表轮询加乐观锁，但锁住数据库行不代表锁住远程业务系统；远端也需接收幂等键或fencing token。

## 易错点与排查

- 只写owner不写token：同名Worker重启可能冒充旧领取。
- 锁过期后旧Worker继续写外部系统：锁本身不能阻止旧执行者。
- SQLite队列叫生产消息代理：它没有分布式broker的调度与确认能力。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`renew(queue, job_id, owner, token, now, ttl)`。

只有当前owner/token且租约尚未过期才可续租；过期拒绝；新Worker接管后旧token不能续租。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/42-workers-queues/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“API与Worker分离”与“至少一次投递”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`busy`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

生产队列需要可见性超时、死信、指数退避、吞吐监控；租约时间必须来自一致的时间来源并考虑暂停和时钟偏差。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html)：连接、事务与参数化查询。
- [SQLite事务](https://www.sqlite.org/lang_transaction.html)：IMMEDIATE写事务与锁边界。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 42`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
