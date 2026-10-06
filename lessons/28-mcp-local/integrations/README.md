# 官方MCP SDK：stdio服务器与客户端

本目录使用mcp==2.3.0；2026-10-06已核查SDK官方文档。v2使用MCPServer、Client和snake_case结果字段，与v1 FastMCP例子有差异。
默认examples/dispatch只是机制演示，不是协议实现；这里有真实初始化、发现、调用与子进程传输。

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/28-mcp-local/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/28-mcp-local/integrations/client.py
```

客户端会自行启动server.py，运行完成后关闭子进程，无需先手工启动服务。
应打印tools包含get_ticket；result中found为True；unknown_tool_is_error为True；之后打印policy资源与摘要提示。
仅直接运行server.py会等待stdio协议输入，不能把等待误认为卡死；Ctrl+C可结束手工启动的服务。

## 首次出现的SDK语法

- `@mcp.tool()`是装饰器：把下面的函数登记为工具，SDK从参数类型生成Schema。
- `ticket_id: str`是类型标注；SDK据此校验协议参数，Python普通直接调用不会自动做同等校验。
- `-> TicketResult`描述返回输出模型；BaseModel属于Pydantic，SDK依赖中已包含，字段声明生成结构化输出Schema。
- `ticket: dict | None`表示值可以是字典或None；`|`在这里是类型联合，不是集合运算。docstring作为对外工具描述，必须表达明确用途。
- `async def`声明协程，`await`等待I/O；它不是自动开线程。
- `async with Client(params)`管理整个连接生命周期；离开块自动关闭。
- `asyncio.timeout(20)`给整个演示20秒预算，防止故障时无限等待。
- `StdioServerParameters`声明子进程命令，sys.executable锁定当前解释器。

## 责任与失败边界

stdio是本机进程传输，不是HTTP端点；stdout属于协议，日志写stderr。默认SDK保护不能替代避免import时输出垃圾。
Tools有结构化参数与执行结果；Resources按URI读取数据；Prompts由用户选择并渲染消息模板。
资源或提示中的不可信内容不能提升成系统权限；客户端发现工具也不代表可以越权查询所有工单。
结果先检查is_error再信任structured_content；不存在工单返回found=False，未知工具返回协议错误结果，两者不同。
本例只用内存工单数据，没有认证系统、租户数据或真实写操作。生产需服务端授权、错误脱敏、输出限额与审计。
客户端生命周期完成即可回收子进程；真实集成验证在verification.md记录，不能把只通过默认dispatch当作SDK已验证。

- [官方客户端](https://py.sdk.modelcontextprotocol.io/client/)
- [官方运行与stdio说明](https://py.sdk.modelcontextprotocol.io/run/)
- [SDK v2迁移](https://py.sdk.modelcontextprotocol.io/migration/)
