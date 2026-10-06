# 阶段 41：持久化、事务与恢复

## 使用场景

助手保存检查点后进程重启，必须恢复已提交状态；失败提交不能留下孤立审计。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能设计最小SQLite检查点，解释事务边界、版本冲突与重启读取。

- 前置：阶段40的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 检查点

定义与用途：恢复任务必需的状态快照，不等于保存所有聊天文本。

具体例子：tasks保存state和version，重建连接读取ready。

### 2. 事务

定义与用途：一组写入全部成功提交或全部失败回滚。

具体例子：状态更新和audit插入在同一个with self.db中。

### 3. 审计

定义与用途：记录谁在何时做了什么，业务事实变化应有关联事件。

具体例子：演示audit记录checkpoint_saved，生产还要actor与tenant。

### 4. 迁移与保留

定义与用途：数据库结构升级和过期数据清理需独立策略。

具体例子：CREATE IF NOT EXISTS只负责初始建表，不自动迁移已有列。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/41-persistence/examples/demo.py
python -m unittest discover -s lessons/41-persistence/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
restart {'state': 'ready', 'version': 1, 'audit': 1}
rollback {'state': 'new', 'version': 0, 'audit': 0}
conflict {'state': 'ready', 'version': 1, 'error': 'version_conflict'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""持久化检查点：业务状态和审计一起提交，冲突及异常均回滚。"""
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, state TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(task_id TEXT NOT NULL, event TEXT NOT NULL);
        """)

    def create(self, task_id):
        with self.db:
            self.db.execute("INSERT INTO tasks VALUES (?, 'new', 0)", (task_id,))

    def save(self, task_id, state, expected_version, crash=False):
        with self.db:
            updated = self.db.execute("UPDATE tasks SET state=?, version=version+1 WHERE id=? AND version=?",
                                      (state, task_id, expected_version))
            if updated.rowcount != 1:
                raise ValueError("version_conflict")
            if crash:
                raise RuntimeError("模拟提交前故障")
            self.db.execute("INSERT INTO audit VALUES (?, ?)", (task_id, "checkpoint_saved"))

    def load(self, task_id):
        state, version = self.db.execute("SELECT state,version FROM tasks WHERE id=?", (task_id,)).fetchone()
        audit = self.db.execute("SELECT COUNT(*) FROM audit WHERE task_id=?", (task_id,)).fetchone()[0]
        return {"state": state, "version": version, "audit": audit}

    def close(self):
        self.db.close()  # 连接上下文只负责事务，不自动关闭连接。

```

按执行顺序追踪：

1. Store初始化创建两张表，PRIMARY KEY拒绝重复task id。
2. save的UPDATE携带expected_version，只更新符合版本的一行。
3. rowcount不等1就抛冲突，事务自动回滚。
4. crash发生在审计前，with负责把状态更新一起回滚。
5. close关闭连接，重新Store连接同一路径证明真实磁盘恢复。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java JDBC事务或@Transactional；SQLite单文件适合本地验证，连接跨线程使用及并发写吞吐需单独考虑。

## 易错点与排查

- with connection自动关闭连接：它管理事务，close仍需要调用。
- 先提交状态再写审计：后一步失败会丢失关联。
- 把所有提示词和工具结果无限保留：需数据用途与期限。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`list_recoverable(store)`。

读取所有new与ready任务的id/state/version，排除completed；使用参数化SQL；关闭后重新连接应读取同样结果。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/41-persistence/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“检查点”与“事务”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`conflict`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

企业生产通常需要迁移脚本、备份恢复、租户索引、加密、保留策略；本课不声称SQLite教具可替代分布式数据库。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html)：连接、事务与参数化查询。
- [SQLite事务](https://www.sqlite.org/lang_transaction.html)：IMMEDIATE写事务与锁边界。
