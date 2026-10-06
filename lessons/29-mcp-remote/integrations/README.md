# 官方SDK Streamable HTTP本地验证

mcp==2.3.0；2026-10-06核查官方HTTP传输与授权文档。本地验证仅监听127.0.0.1，不提供OAuth或生产认证。

从项目根目录安装与自动验证：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/29-mcp-remote/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/29-mcp-remote/integrations/local_verify.py
```

local_verify启动子进程，15秒内等待就绪，发现get_ticket并查询T1，finally停止进程，再确认断连失败。整个流程有限退出。
应输出真实HTTP MCP读取通过，以及服务停止后连接按预期失败；网络请求是回环，不访问外网。
手工操作时使用两个PowerShell终端，工作目录均是项目根目录：

```powershell
# 终端A：服务会常驻，验证后Ctrl+C停止。
.\.venv\Scripts\python.exe lessons/29-mcp-remote/integrations/server.py --port 8765
# 终端B：一次查询后正常退出。
.\.venv\Scripts\python.exe lessons/29-mcp-remote/integrations/client.py --url http://127.0.0.1:8765/mcp
```

## 真实传输做了什么

MCPServer.run的transport选择streamable-http，host限制监听地址，port指定本地端口。
Client(URL)进入时建立协议连接，发现工具，每次结果检查is_error；关闭时结束会话。
会话恢复和断连不是简单把HTTP 200当业务成功；需检查协议结果与工具Schema，并为长操作设计明确期限。
默认离线call_read只演示只读断连重试，真实client本例明确失败，没有声称实现完整自动重连。

## 认证与授权边界

本机无认证服务绝不能直接改为0.0.0.0后发布。公开服务需要TLS、可信认证、对象权限和速率限制。
认证回答“谁”，授权回答“能对哪些对象做什么”；有效token也不能绕过租户/工单权限。
MCP HTTP授权遵循协议的OAuth要求，需受保护资源元数据、授权服务器发现、令牌受众与scope核验，不能把任意Bearer字符串检查冒充完整OAuth。
如果使用企业网关或静态教学令牌，说明它与规范OAuth之间的差异；客户端凭证由安全存储提供，日志不打印Authorization。
SDK v2自定义头与超时放在httpx2.AsyncClient，再传给streamable_http_client(url, http_client=...)；不要照搬旧headers参数。
401/403应停止并修复身份或权限，不盲目重试；超时后的写操作可能已经提交，应查询状态或使用服务端幂等键。
重连后重新发现工具；名字相同但Schema变化也可能不兼容，固定契约并记录版本。
本次未配置OAuth授权服务器、生产TLS、跨公网部署或写工具；不能声称这些能力验证通过。

- [官方HTTP运行](https://py.sdk.modelcontextprotocol.io/run/)
- [官方客户端传输](https://py.sdk.modelcontextprotocol.io/client/transports/)
- [官方SDK授权](https://py.sdk.modelcontextprotocol.io/run/authorization/)
- [MCP授权规范](https://modelcontextprotocol.io/specification/latest/basic/authorization)
