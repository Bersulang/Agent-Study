# 官方A2A SDK接入

本目录实际使用`a2a-sdk==0.3.26`，对应A2A协议0.3及JSON-RPC传输。它不是自定义REST模拟。课程有意固定0.3线复现接口；官方最新1.x提供新的API与迁移指南，升级时先重新运行协议测试。

默认`examples/demo.py`只是离线领域生命周期；本目录SDK应用才负责Agent Card、JSON-RPC、TaskStore和Artifact编码。

## 安装与本地验证

以下命令都从项目根目录执行。已有`.venv`时无需重复创建。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/37-a2a-remote/integrations/requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s lessons/37-a2a-remote/integrations -p test_protocol.py
.\.venv\Scripts\python.exe lessons/37-a2a-remote/integrations/client.py --local
```

`-r`让pip按requirements读取固定直接依赖。安装需要网络；安装后`--local`使用httpx的ASGITransport，在进程内调用真实SDK应用，不开常驻端口、不调用模型。

预期测试3项通过，客户端显示技能`ticket-status`、状态`completed`、查证产物`T-7: open`。任务id由SDK生成，不固定。

## 真实HTTP方式

终端A从项目根目录启动服务：

```powershell
.\.venv\Scripts\python.exe lessons/37-a2a-remote/integrations/server.py
```

终端B仍从项目根目录运行：

```powershell
.\.venv\Scripts\python.exe lessons/37-a2a-remote/integrations/client.py
```

终端A按Ctrl+C停止。服务只监听`127.0.0.1:9999`，避免把无生产认证的教学应用公开。

## 代码追踪

1. `AgentSkill`描述ticket-status能力，`AgentCard`公开能力及服务URL；能力声明不是认证凭据。
2. `DefaultRequestHandler`和`A2AStarletteApplication`是官方SDK对象；它们处理`message/send`、`tasks/get`和`tasks/cancel`等标准方法。
3. executor用`new_task`生成Task，并通过EventQueue交给SDK管理。
4. `TaskUpdater`发送working状态、正式artifact和completed终态。
5. 输入`wait`产生input-required状态，代表等待补充；协议测试随后请求取消，确认canceled且没有产物。
6. 客户端用`A2ACardResolver`发现卡片，`ClientFactory`选择官方传输，发送结构化Message并按task id查证。

`async def`返回协程；`await`等待异步事件队列或HTTP；注解中的RequestContext/EventQueue描述SDK对象类型。`Part(root=TextPart(...))`是Pydantic联合类型包装，不是普通字典嵌套。`message_id`等Python字段序列化时由SDK转成规范JSON别名。

## 错误、身份与生产边界

- 查询非T-7输入返回failed状态，没有正式工单产物。
- 未知task id由SDK生成协议错误；已经完成的任务不可再次取消。
- `InMemoryTaskStore`重启丢失任务，只适合本地教学；生产换为持久存储。
- 本地服务没有实现生产认证，也没有真实模型；跨服务认证应遵循官方安全规则并核查租户授权。
- 本地ASGI测试不证明真实网络、TLS、代理、负载均衡、断线恢复或跨供应商互操作全部通过。

官方依据：[协议0.3](https://a2a-protocol.org/v0.3.0/specification/)、[Executor](https://a2a-protocol.org/v0.3.0/tutorials/python/4-agent-executor/)、[启动服务](https://a2a-protocol.org/v0.3.0/tutorials/python/5-start-server/)、[官方SDK及迁移指南](https://github.com/a2aproject/a2a-python)。
