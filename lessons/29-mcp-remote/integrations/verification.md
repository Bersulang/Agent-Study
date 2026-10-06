# 实际集成验证

2026-10-06，Windows PowerShell + Python 3.12.10。

实际安装环境为系统临时目录下agent-study-sdk-17-29，未改全局Python。安装固定顶层依赖：pypdf6.19.0、langgraph1.2.13、mcp2.3.0。

## 可复现命令

安装命令见README.md；从项目根目录，用安装依赖后的虚拟环境解释器执行：

```powershell
.\.venv\Scripts\python.exe lessons\29-mcp-remote\integrations\local_verify.py
```

实际退出码：0

```text
tools ['get_ticket']
result {'found': True, 'ticket_id': 'T1', 'status': 'open'}
真实HTTP MCP读取通过
服务停止后连接按预期失败；本例不盲目重试写操作
```

真实HTTP工具发现与读取、子进程关闭、关闭后断连失败通过；裸dict结构化结果问题由输出模型修正。OAuth、TLS、跨公网、写操作幂等和自动重连未验证。

课程集成验证不等于学员能力已通过。完整独立环境依赖快照见同目录verified-environment.txt；教学安装仍以requirements.txt为准。
