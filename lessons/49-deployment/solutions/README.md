# 阶段49参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py实际探测可写目录并确认探测文件删除，拒绝不存在目录、文件路径与非法端口；断言依赖故障存活200/就绪503。OS拒写由test_extensions.py在实际创建文件边界模拟，Windows只读属性不是ACL。下面提供实际容器步骤，本机未运行Docker。

从项目根目录执行：

```powershell
python lessons/49-deployment/solutions/solution.py
python -m unittest discover -s lessons/49-deployment/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。

## Docker重启与数据验证（需要Docker）

以下命令从项目根目录执行；不加down -v，保留命名卷。容器内数据库写入是临时教学数据，记录第一次与重启后两次SELECT结果；预期均为[("persisted",)]。本次没有运行Docker，不能据此声称容器验证通过。

```powershell
docker compose -f lessons/49-deployment/integrations/compose.yaml up --build -d
docker compose -f lessons/49-deployment/integrations/compose.yaml exec health python -c "import sqlite3; c=sqlite3.connect('/app/data/service.db'); c.execute('CREATE TABLE IF NOT EXISTS probe(value TEXT UNIQUE)'); c.execute('INSERT OR IGNORE INTO probe VALUES (?)', ('persisted',)); c.commit(); print(c.execute('SELECT value FROM probe').fetchall()); c.close()"
docker compose -f lessons/49-deployment/integrations/compose.yaml restart health
docker compose -f lessons/49-deployment/integrations/compose.yaml exec health python -c "import sqlite3; c=sqlite3.connect('/app/data/service.db'); print(c.execute('SELECT value FROM probe').fetchall()); c.close()"
docker compose -f lessons/49-deployment/integrations/compose.yaml down
```

exec在运行容器内执行命令；restart保留卷但重启进程。若权限错误，修复卷归属和初始化流程；不要启用特权模式。生产禁止用这些探测写入真实业务表。
