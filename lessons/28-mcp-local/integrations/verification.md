# 实际集成验证

2026-10-06，Windows PowerShell + Python 3.12.10。

实际安装环境为系统临时目录下agent-study-sdk-17-29，未改全局Python。安装固定顶层依赖：pypdf6.19.0、langgraph1.2.13、mcp2.3.0。

## 可复现命令

安装命令见README.md；从项目根目录，用安装依赖后的虚拟环境解释器执行：

```powershell
.\.venv\Scripts\python.exe lessons\28-mcp-local\integrations\client.py
```

实际退出码：0

```text
tools ['get_ticket']
result {'found': True, 'ticket': {'status': 'open', 'title': '登录失败'}}
unknown_tool_is_error True
resource 付款前必须审批。
prompt 请先查询工单T1，再基于真实字段总结状态。
Tool 'missing' failed: 'Unknown tool: missing'
```

Unknown tool: missing日志是有意调用未知工具的负例。曾因裸dict返回注解没有structured_content而断言失败；改成Pydantic输出模型后真实stdio断言通过。

课程集成验证不等于学员能力已通过。完整独立环境依赖快照见同目录verified-environment.txt；教学安装仍以requirements.txt为准。
