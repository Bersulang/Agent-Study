# 阶段30—43材料验证记录

验证日期：2026-10-06。环境：Windows PowerShell、Python3.12.10。
本记录只描述材料制作和代码验证；所有阶段学员能力仍待独立验收。

## 标准库材料

逐阶段从项目根目录执行：

```powershell
python lessons/NN-topic/examples/demo.py
python lessons/NN-topic/solutions/solution.py
python lessons/NN-topic/exercises/practice.py
python -m unittest discover -s lessons/NN-topic/tests
```

NN-topic依次为30-routing-roles至43-approval-idempotency的实际目录。
14个默认演示、14个参考答案和14个练习骨架，共42个脚本全部退出码0。
练习骨架加载成功不代表练习完成；骨架保留NotImplementedError供学员实现。
40项标准库业务回归全部通过，包含成功、权限拒绝、歧义、深度/跳数上限、超时、版本冲突、证据冲突、预算耗尽、回滚、租约接管和审批失效/撤销/变更/恢复重放。

测试先行证据：在默认run_case尚返回空字典时，40项业务断言均观察到FAIL；实现后全部转为OK。没有用导入错误代替行为断言失败。

41—43真实写临时SQLite文件，新建连接验证恢复或不同Worker，所有连接显式close后清理临时目录；没有遗留数据库句柄。

## 真实集成

集成验证使用临时虚拟环境`$env:TEMP/agent-study-services-venv`，未写进课程目录。
锁定直接依赖见各课integrations/requirements.txt；学员可在根目录`.venv`按同样依赖复现。

```powershell
& "$env:TEMP/agent-study-services-venv/Scripts/python.exe" -m unittest discover -s lessons/37-a2a-remote/integrations -p test_protocol.py
& "$env:TEMP/agent-study-services-venv/Scripts/python.exe" lessons/37-a2a-remote/integrations/client.py --local
& "$env:TEMP/agent-study-services-venv/Scripts/python.exe" -m unittest discover -s lessons/39-fastapi-service/integrations -p test_app.py
python -m unittest discover -s lessons/40-java-integration/integrations -p test_client.py
```

- 37：官方a2a-sdk0.3.26协议3项通过。发现技能、完成Task/Artifact、tasks/get查证、input-required取消均调用真实SDK ASGI应用。官方ClientFactory客户端`--local`成功。
- 37：另实际启动server.py监听127.0.0.1:9999，用默认网络client.py完成发现、完成及查证，退出码0；finally终止服务并释放端口。
- 39：FastAPI0.115.12真实TestClient业务3项通过，验证422无副作用、201创建、续读SSE、会话隔离、取消/重复取消。
- 39：另1项真实页面响应JavaScript经Node24.21.0解析通过；此项Node缺失时明确skip。先复现字符串转义错误，再改原始字符串并转绿。
- 40：2项本机HTTP探针通过，验证Python实际发送身份/trace头及保留401错误体；探针不是Spring Boot。

本地协议3项、FastAPI4项、PythonHTTP2项，共9项集成检查全部通过，无skip。
FastAPI与A2A接口测试均先在无路由应用上确认业务状态码断言失败，再添加实现并转绿；客户端HTTP测试先确认空结果断言失败再实现。

## 静态和未验证范围

63个交付Python文件AST解析全部通过；pom.xml通过XML解析。14个主讲义159—181行，各阶段knowledge.md至少67行，所有配套要求均有对应材料。

PATH未发现java或mvn，因此没有执行Java构建、JUnit/MockMvc或Python→Spring Boot端到端；这些命令和3项Java测试已提供，但未声称通过。
没有执行真实模型、生产身份认证、TLS、跨供应商A2A互操作、浏览器视觉/点击验收、分布式队列或外部业务写入。本课默认模型逻辑及业务数据是确定性教学替代。
